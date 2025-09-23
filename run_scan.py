# run_scan.py
from scanner.inventory import list_storage_accounts
from scanner.checks_azure import check_storage_public_blob_access
from scanner.check_vms import list_vms_with_public_ip
from scanner.check_nsg import check_open_nsg_rules
import json

def run():
    findings = []

    print("Scanning storage accounts...")
    accounts = list_storage_accounts()
    findings += check_storage_public_blob_access(accounts)

    print("Scanning virtual machines for public IPs...")
    findings += list_vms_with_public_ip()

    print("Scanning NSGs for open rules...")
    findings += check_open_nsg_rules()

    print(f"\nTotal findings: {len(findings)}")
    if findings:
        print(json.dumps(findings, indent=2))
    else:
        print("No findings detected.")

if __name__ == "__main__":
    run()
