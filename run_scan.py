# run_scan.py
from scanner.inventory import list_storage_accounts
from scanner.checks_azure import check_storage_public_blob_access
from scanner.check_storage_encryption import check_storage_encryption
from scanner.check_vms import list_vms_with_public_ip  # keep the original working import
from scanner.check_nsg import check_open_nsg_rules
from scanner.check_function_apps import check_unrestricted_function_apps
from scanner.check_resource_tags import check_resource_tags

import json

# NEW: try to import optional inventory helpers; fall back to safe stubs if missing
try:
    from scanner.check_vms import list_nics, list_vms
except Exception:
    try:
        from scanner.inventory import list_nics, list_vms
    except Exception:
        def list_nics():
            return []
        def list_vms():
            return []

# NEW IMPORTS
try:
    from scanner.inventory_extensions import list_key_vaults, list_app_services
except Exception:
    def list_key_vaults():
        return []
    def list_app_services():
        return []

try:
    from scanner.check_key_vaults import check_key_vaults
except Exception:
    def check_key_vaults(x): return []

try:
    from scanner.check_storage_network_rules import check_storage_network_rules
except Exception:
    def check_storage_network_rules(x): return []

try:
    from scanner.check_app_service_secrets import check_app_service_secrets
except Exception:
    def check_app_service_secrets(x): return []

try:
    from scanner.check_vm_ip_forwarding import check_vm_ip_forwarding
except Exception:
    def check_vm_ip_forwarding(x): return []

try:
    from scanner.check_vm_multiple_public_ips import check_vm_multiple_public_ips
except Exception:
    def check_vm_multiple_public_ips(x): return []

try:
    from scanner.check_vm_boot_diagnostics import check_vm_boot_diagnostics
except Exception:
    def check_vm_boot_diagnostics(x): return []


def run():
    findings = []

    print("Scanning storage accounts...")
    accounts = list_storage_accounts()
    findings += check_storage_public_blob_access(accounts)

    print("Checking storage account encryption...")
    findings += check_storage_encryption(accounts)

    print("Checking storage network rules...")
    findings += check_storage_network_rules(accounts)

    print("Scanning virtual machines for public IPs...")
    vm_pub_findings_or_vms = list_vms_with_public_ip()

    if vm_pub_findings_or_vms and isinstance(vm_pub_findings_or_vms[0], dict) and vm_pub_findings_or_vms[0].get("rule_id"):
        findings += vm_pub_findings_or_vms
        try:
            vms_for_checks = list_vms()
        except Exception:
            vms_for_checks = []
    else:
        vms_for_checks = vm_pub_findings_or_vms or []

    try:
        nics = list_nics()
    except Exception:
        nics = []

    print("Scanning NSGs for open rules...")
    findings += check_open_nsg_rules()

    # gather resource lists for tag checking — combine available inventories (best-effort)
    resources_for_tag_check = []
    try:
        if accounts:
            resources_for_tag_check.extend(accounts)
    except:
        pass

    try:
        if vms_for_checks:
            resources_for_tag_check.extend(vms_for_checks)
    except:
        pass

    try:
        if nics:
            resources_for_tag_check.extend(nics)
    except:
        pass

    # app services must be defined BEFORE usage
    app_services = list_app_services()

    try:
        if app_services:
            resources_for_tag_check.extend(app_services)
    except:
        pass

    try:
        key_vaults = list_key_vaults()
        if key_vaults:
            resources_for_tag_check.extend(key_vaults)
    except:
        pass

    print("Checking resources for missing tags (low severity)...")
    findings += check_resource_tags(resources_for_tag_check)

    print("Scanning Function Apps for anonymous access...")
    findings += check_unrestricted_function_apps()

    print("Scanning App Services for plaintext secrets...")
    findings += check_app_service_secrets(app_services)

    print("Checking NICs for IP forwarding enabled...")
    findings += check_vm_ip_forwarding(nics)

    print("Checking for multiple public IPs on NICs/VMs...")
    findings += check_vm_multiple_public_ips(nics or vms_for_checks)

    print("Checking VM boot diagnostics settings...")
    findings += check_vm_boot_diagnostics(vms_for_checks)

    print("Scanning Key Vault configurations...")
    findings += check_key_vaults(key_vaults)

    print(f"\nTotal findings: {len(findings)}")
    if findings:
        for f in findings:
            print("\n------------------------------")
            print(f"Rule ID: {f.get('rule_id')}")
            print(f"Service: {f.get('service')}")
            print(f"Title: {f.get('title')}")
            print(f"Severity: {f.get('severity')}")
            print(f"Resource: {f.get('resource_name', f.get('resource_id'))}")
            print("Evidence:")
            print(json.dumps(f.get('evidence'), indent=2, ensure_ascii=False))
            print("Remediation:")
            if isinstance(f.get('remediation'), list):
                for r in f.get('remediation'):
                    print(f"- {r}")
            else:
                print(f.get('remediation'))
        print("\n------------------------------")
    else:
        print("No findings detected.")

    return findings


if __name__ == "__main__":
    run()
