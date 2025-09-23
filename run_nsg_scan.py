# run_nsg_scan.py
from scanner.check_nsg import check_open_nsg_rules
import json

if __name__ == "__main__":
    findings = check_open_nsg_rules()
    print(f"Found {len(findings)} NSG rule(s) open to the world on sensitive ports.")
    if findings:
        print(json.dumps(findings, indent=2))
    else:
        print("No risky NSG rules found.")
