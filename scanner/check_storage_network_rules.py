# scanner/check_storage_network_rules.py
from typing import List, Dict, Any

def _to_dict_if_sdk(obj: Any) -> Dict:
    """
    Convert Azure SDK objects to plain dicts if possible.
    If obj already a dict, return it unchanged.
    """
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    # Azure SDK objects often have `as_dict()` method
    try:
        if hasattr(obj, "as_dict"):
            return obj.as_dict() or {}
    except Exception:
        pass
    # fallback: try __dict__
    try:
        return dict(obj.__dict__)
    except Exception:
        # last resort, return empty dict
        return {}

def check_storage_network_rules(storage_accounts: List[Any]) -> List[Dict]:
    """
    Check storage accounts for public network access and allowBlobPublicAccess flag.
    Accepts list of dicts or Azure SDK StorageAccount objects.
    Returns list of findings (same shape as your other checks).
    """
    findings = []

    for s in storage_accounts or []:
        sdict = _to_dict_if_sdk(s)

        # properties might be nested in various shapes; normalize
        props = sdict.get("properties") or {}
        # try alternate keys sometimes returned by SDK or custom inventory
        if not props and isinstance(s, dict):
            # try lower-cased / alternate keys
            for k in ("Properties", "props"):
                if k in s:
                    props = s[k] or {}

        # Resource id / name resolution
        resource_id = sdict.get("id") or sdict.get("resourceId") or sdict.get("name") or None
        resource_type = sdict.get("type") or sdict.get("kind") or "StorageAccount"
        resource_name = sdict.get("name") or (resource_id.split("/")[-1] if isinstance(resource_id, str) else None)

        # allowBlobPublicAccess can be at top-level properties or nested
        allow_blob_public = None
        try:
            if isinstance(props, dict) and "allowBlobPublicAccess" in props:
                allow_blob_public = props.get("allowBlobPublicAccess")
            else:
                allow_blob_public = sdict.get("allowBlobPublicAccess", None)
        except Exception:
            allow_blob_public = None

        if allow_blob_public is True:
            findings.append({
                "rule_id": "AZST001",
                "title": "Storage account allows blob public access",
                "service": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "severity": "High",
                "evidence": {"allowBlobPublicAccess": allow_blob_public},
                "remediation": (
                    "Disable blob public access on the storage account. "
                    "Example: az storage account update -n <name> -g <rg> --allow-blob-public-access false"
                ),
            })

        # networkAcls often appears under properties.networkAcls
        network_acls = {}
        try:
            if isinstance(props, dict):
                network_acls = props.get("networkAcls") or props.get("network_acls") or {}
            else:
                network_acls = sdict.get("networkAcls") or {}
        except Exception:
            network_acls = {}

        default_action = None
        bypass = None
        try:
            if isinstance(network_acls, dict):
                default_action = network_acls.get("defaultAction") or network_acls.get("default_action")
                bypass = network_acls.get("bypass")
        except Exception:
            default_action = None
            bypass = None

        if default_action and isinstance(default_action, str) and default_action.lower() == "allow":
            findings.append({
                "rule_id": "AZST002",
                "title": "Storage account default network ACL allows public access",
                "service": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "severity": "High",
                "evidence": {"networkAcls.defaultAction": default_action, "bypass": bypass},
                "remediation": (
                    "Restrict network access to selected virtual networks/IP ranges or enable private endpoints. "
                    "Example: az storage account update -n <name> -g <rg> --default-action Deny"
                ),
            })

    return findings
