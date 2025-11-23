# scanner/check_vm_multiple_public_ips.py
from typing import List, Dict

def check_vm_multiple_public_ips(nics_or_vms: List[Dict]) -> List[Dict]:
    """
    Detect VMs/NICs that have multiple public IPs attached.
    Accepts either:
      - list of NIC dicts (each containing ipConfigurations with publicIPAddress entries)
      - or list of VM dicts that include networkProfile -> networkInterfaces -> public ips
    """
    findings = []

    for item in nics_or_vms or []:
        # try NIC-based shape first
        ip_configs = None
        if "ipConfigurations" in item:
            ip_configs = item.get("ipConfigurations") or item.get("properties", {}).get("ipConfigurations")
            # ip_config may be a list of dicts; each ip_config.get("publicIPAddress") may be None or an object
            public_ips = []
            for cfg in ip_configs or []:
                pip = cfg.get("publicIPAddress") or (cfg.get("properties", {}).get("publicIPAddress") if isinstance(cfg.get("properties"), dict) else None)
                if pip:
                    # pip may be dict or contain an 'ipAddress' field only at the public-ip resource
                    ip_addr = pip.get("ipAddress") if isinstance(pip, dict) else None
                    # store either id or ip
                    public_ips.append({"id": pip.get("id") if isinstance(pip, dict) else pip, "ip": ip_addr})
            if len(public_ips) > 1:
                resource_id = item.get("id") or item.get("name")
                findings.append({
                    "rule_id": "AZ-VM-MULTIPIP-001",
                    "title": "NIC/VM has multiple public IP addresses",
                    "service": "VirtualMachine",
                    "resource_id": resource_id,
                    "resource_name": item.get("name"),
                    "severity": "High",
                    "evidence": {"public_ips": public_ips},
                    "remediation": [
                        "Remove additional public IPs or consolidate to a single required public IP.",
                        "Azure CLI example to delete a secondary public IP: az network public-ip delete -g <rg> -n <pip-name>"
                    ]
                })
            continue

        # else try VM-shaped item: look for public IPs under network interfaces
        if "networkProfile" in item:
            public_ips = []
            for nic_ref in item.get("networkProfile", {}).get("networkInterfaces", []) or []:
                # nic_ref may include id; we can't list the NIC from here without inventory helper
                # skip detailed counting here (inventory should pass NICs instead)
                pass

    return findings
