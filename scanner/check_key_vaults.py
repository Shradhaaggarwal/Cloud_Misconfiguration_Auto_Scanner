# FILE: scanner/check_key_vaults.py
from typing import List, Dict


def check_key_vaults(vaults: List[Dict]) -> List[Dict]:
    """Check Key Vaults for soft-delete / purge protection and overly-broad access policies.

    Returns a list of findings with the same shape your other checks use:
    {
        "rule_id": str,
        "title": str,
        "service": str,
        "resource_id": str,
        "severity": str,
        "evidence": dict,
        "remediation": str
    }
    """
    findings = []

    for v in vaults:
        props = v.get("properties", {})
        rv_id = v.get("id") or v.get("resourceId") or v.get("name")

        # Soft delete
        soft_delete = props.get("enableSoftDelete") if props else None
        if not soft_delete:
            findings.append({
                "rule_id": "AZKV001",
                "title": "Key Vault soft-delete not enabled",
                "service": "KeyVault",
                "resource_id": rv_id,
                "severity": "High",
                "evidence": {"enableSoftDelete": soft_delete},
                "remediation": (
                    "Enable soft-delete and purge protection for the Key Vault. "
                    "Example: az keyvault update --name <name> --enable-soft-delete true --enable-purge-protection true"
                ),
            })

        # Purge protection
        purge_protection = props.get("enablePurgeProtection") if props else None
        if not purge_protection:
            findings.append({
                "rule_id": "AZKV002",
                "title": "Key Vault purge protection not enabled",
                "service": "KeyVault",
                "resource_id": rv_id,
                "severity": "High",
                "evidence": {"enablePurgeProtection": purge_protection},
                "remediation": (
                    "Enable purge protection to prevent permanent deletion. "
                    "Example: az keyvault update --name <name> --enable-purge-protection true"
                ),
            })

        # Access policies - overly broad principals
        access_policies = v.get("properties", {}).get("accessPolicies") if v.get("properties") else []
        for ap in access_policies or []:
            principal_id = ap.get("tenantId") or ap.get("objectId") or ap.get("principalId")
            # Heuristic: if displayName or principalId contains 'all' or 'everyone' flag it
            display_name = ap.get("displayName") or ap.get("principalName") or ""
            if display_name and any(x in display_name.lower() for x in ["all", "everyone", "allusers"]):
                findings.append({
                    "rule_id": "AZKV003",
                    "title": "Key Vault access policy granted to overly-broad principal",
                    "service": "KeyVault",
                    "resource_id": rv_id,
                    "severity": "High",
                    "evidence": {"access_policy_display": display_name, "principal_id": principal_id},
                    "remediation": (
                        "Restrict Key Vault access policies to specific service principals or users, or use RBAC. "
                        "Review access policies and remove overly-broad principals."
                    ),
                })

    return findings


