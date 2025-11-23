# scanner/check_resource_tags.py
from typing import List, Dict, Any

def _to_dict(obj: Any) -> Dict:
    """
    Convert many Python/Azure SDK objects to a plain dict.
    - If it's already a dict -> return it
    - If object has as_dict() -> call it
    - If object has __dict__ -> use that
    - As last resort, inspect public attributes via getattr
    """
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj

    # Try as_dict() (common in Azure SDK)
    try:
        if hasattr(obj, "as_dict"):
            ad = obj.as_dict()
            if isinstance(ad, dict):
                return ad
    except Exception:
        pass

    # Try __dict__
    try:
        if hasattr(obj, "__dict__"):
            return dict(obj.__dict__) or {}
    except Exception:
        pass

    # Last resort: inspect public attributes (best-effort)
    result = {}
    try:
        for attr in dir(obj):
            if attr.startswith("_"):
                continue
            try:
                val = getattr(obj, attr)
                # skip methods
                if callable(val):
                    continue
                result[attr] = val
            except Exception:
                # ignore any attr we can't access
                continue
    except Exception:
        pass

    return result

def check_resource_tags(resources: List[Any]) -> List[Dict]:
    """
    Emit Low severity finding for resources missing tags.
    Works with Azure SDK objects and plain dicts.
    """
    findings = []

    for r in resources or []:
        rd = _to_dict(r)

        # Try multiple common locations for tags
        tags = None
        try:
            tags = rd.get("tags")
        except Exception:
            tags = None

        if not tags:
            # nested properties tags path
            try:
                props = rd.get("properties", {}) if isinstance(rd, dict) else {}
            except Exception:
                props = {}
            if isinstance(props, dict):
                tags = props.get("tags") or props.get("Tags") or props.get("additionalProperties", {}).get("tags")

        # also accept Graph-like shapes where tags may be JSON string; treat non-empty as present
        if isinstance(tags, str):
            try:
                # quick heuristic: if string looks like '{}' or 'null' treat as empty
                if tags.strip() in ("", "null", "None", "{}"):
                    tags = None
                else:
                    tags = tags
            except Exception:
                tags = None

        if not tags:
            resource_id = rd.get("id") if isinstance(rd, dict) else None
            if not resource_id:
                resource_id = rd.get("resourceId") if isinstance(rd, dict) else None
            if not resource_id:
                # try to synthesize from name
                resource_id = rd.get("name") if isinstance(rd, dict) else None

            resource_name = rd.get("name") if isinstance(rd, dict) else None
            if not resource_name and isinstance(resource_id, str):
                resource_name = resource_id.split("/")[-1]

            resource_type = rd.get("type") if isinstance(rd, dict) else None
            if not resource_type:
                resource_type = rd.get("kind") if isinstance(rd, dict) else "Resource"

            findings.append({
                "rule_id": "AZ-RES-TAGS-001",
                "title": "Resource missing tags (recommend tagging for inventory & cost)",
                "service": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "severity": "Low",
                "evidence": {"has_tags": False},
                "remediation": [
                    "Apply meaningful tags (owner, environment, cost-center).",
                    "CLI: az resource tag --ids <resource-id> --tags owner=teamA environment=test"
                ]
            })

    return findings
