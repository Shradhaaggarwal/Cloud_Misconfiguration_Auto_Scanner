# scanner/check_vm_ip_forwarding.py
from typing import List, Dict

def check_vm_ip_forwarding(nics: List[Dict]) -> List[Dict]:
    """
    Detect NICs that have IP forwarding enabled.
    Expects inventory function that returns NIC dicts (az SDK as_dict() shape or similar).
    """
    findings = []
    for nic in nics or []:
        # try multiple keys so it works with different inventory shapes
        enabled = nic.get("enableIPForwarding")
        # older SDK shapes might use "enable_ip_forwarding"
        if enabled is None:
            enabled = nic.get("properties", {}).get("enableIpForwarding") or nic.get("properties", {}).get("enableIPForwarding")

        if enabled is True:
            resource_id = nic.get("id") or nic.get("resourceId") or nic.get("name")
            nic_name = nic.get("name") or (resource_id.split("/")[-1] if resource_id else None)
            findings.append({
                "rule_id": "AZ-VM-IPFWD-001",
                "title": "IP forwarding enabled on NIC",
                "service": "NetworkInterface",
                "resource_id": resource_id,
                "resource_name": nic_name,
                "severity": "High",
                "evidence": {"nic_name": nic_name, "ip_forwarding": True},
                "remediation": [
                    "Disable IP forwarding on the NIC unless it is required for routers or appliance scenarios.",
                    "Azure CLI example: az network nic update --resource-group <rg> --name <nic> --ip-forwarding false"
                ]
            })
    return findings
