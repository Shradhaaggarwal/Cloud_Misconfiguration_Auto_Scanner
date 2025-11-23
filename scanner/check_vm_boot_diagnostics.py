# scanner/check_vm_boot_diagnostics.py
from typing import List, Dict

def check_vm_boot_diagnostics(vms: List[Dict]) -> List[Dict]:
    """
    Detect VMs that have boot diagnostics disabled.
    Expects vms: list of VM dicts (az vm show .as_dict() shape)
    The property path often is: properties.diagnosticsProfile.bootDiagnostics.enabled
    """
    findings = []
    for vm in vms or []:
        props = vm.get("properties", {}) or {}
        diag = props.get("diagnosticsProfile") or props.get("diagnosticsProfile", {})
        # Some SDK outputs place bootDiagnostics under properties.bootDiagnostics (older shapes)
        boot = None
        if isinstance(diag, dict) and "bootDiagnostics" in diag:
            boot = diag.get("bootDiagnostics")
        else:
            # fallback to properties.bootDiagnostics
            boot = props.get("bootDiagnostics")

        enabled = None
        if isinstance(boot, dict):
            enabled = boot.get("enabled")
        # If property not found, assume disabled (safer to flag)
        if enabled is False or enabled is None:
            resource_id = vm.get("id") or vm.get("resourceId") or vm.get("name")
            vm_name = vm.get("name") or (resource_id.split("/")[-1] if resource_id else None)
            findings.append({
                "rule_id": "AZ-VM-BOOTDIAG-001",
                "title": "Boot diagnostics disabled on VM",
                "service": "VirtualMachine",
                "resource_id": resource_id,
                "resource_name": vm_name,
                "severity": "Medium",
                "evidence": {"bootDiagnostics_enabled": enabled},
                "remediation": [
                    "Enable Boot Diagnostics to capture console logs and screenshots for troubleshooting and forensics.",
                    "Azure CLI example: az vm boot-diagnostics enable --resource-group <rg> --name <vm> --storage <storage-account-url>"
                ]
            })
    return findings
