
# FILE: scanner/check_app_service_secrets.py
from typing import List, Dict
import re


SECRET_KEYWORDS = [
    r"password",
    r"passwd",
    r"secret",
    r"connectionstring",
    r"conn_str",
    r"api[_-]?key",
    r"client[_-]?secret",
    r"access[_-]?key",
]

# a simple heuristic for long base64-like blobs (common for keys)
BASE64_REGEX = re.compile(r"^[A-Za-z0-9+/]{32,}={0,2}$")


def _looks_like_secret(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    # check if contains any secret keyword in key name (skip if value is short)
    value_lower = value.lower()
    if len(value) >= 32 and BASE64_REGEX.match(value.strip()):
        return True
    # if value contains whitespace or is a JSON structure, skip heuristics
    # For other cases, rely on presence of characters typical of secrets
    if any(k in value_lower for k in ["pw=", "password=", "pwd=", "clientsecret", "apikey", "accesskey"]):
        return True
    return False


def check_app_service_secrets(apps: List[Dict]) -> List[Dict]:
    """Detect likely secrets in App Service / Function App settings.

    For each app, iterate app settings and connection strings and run heuristics.
    """
    findings = []

    for app in apps:
        rv_id = app.get("id") or app.get("resourceId") or app.get("name")
        settings = app.get("properties", {}).get("siteConfig", {}).get("appSettings")
        # Some inventory functions return settings as a dict under `appSettings` key
        if isinstance(settings, dict):
            items = settings.items()
        else:
            # If Stream or API returns list of dicts [{'name':..., 'value':...}]
            items = []
            for s in settings or []:
                if isinstance(s, dict):
                    items.append((s.get("name"), s.get("value")))

        for k, v in items:
            if not k:
                continue
            key_lower = k.lower()
            # Name-based heuristics
            if any(re.search(pattern, key_lower) for pattern in SECRET_KEYWORDS):
                findings.append({
                    "rule_id": "AZAS001",
                    "title": "App setting key name looks like it contains a secret",
                    "service": "AppService",
                    "resource_id": rv_id,
                    "severity": "High",
                    "evidence": {"setting": k, "value_preview": (v[:64] + "...") if v and isinstance(v, str) else v},
                    "remediation": (
                        "Move secrets to Key Vault and reference them via Key Vault references or managed identities. "
                        "Avoid storing secrets in plain app settings."
                    ),
                })
                continue

            # Value-based heuristics
            if _looks_like_secret(v):
                findings.append({
                    "rule_id": "AZAS002",
                    "title": "App setting value looks like a secret",
                    "service": "AppService",
                    "resource_id": rv_id,
                    "severity": "High",
                    "evidence": {"setting": k, "value_preview": (v[:64] + "...") if v else v},
                    "remediation": (
                        "Move secrets to Key Vault and reference them via Key Vault references or managed identities. "
                        "Rotate any suspected secrets."
                    ),
                })

    return findings

