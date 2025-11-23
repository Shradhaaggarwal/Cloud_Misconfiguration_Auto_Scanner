# server.py
import json
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import db.dao as dao  # Imports your existing DAO functions
import os
from flask import send_from_directory, send_file
from reports.generate_report import generate_report
import run_scan



import run_scan

app = Flask(__name__)
CORS(app)  # Enables the React frontend to communicate with this server

# Helper to safely parse the JSON strings stored in your DB
def parse_json_field(field_value, default_value):
    if not field_value:
        return default_value
    if isinstance(field_value, str):
        try:
            return json.loads(field_value)
        except:
            return default_value
    return field_value

# Serve generated report files for download
@app.route("/reports/exports/<path:filename>", methods=["GET"])
def serve_report_file(filename):
    export_dir = os.path.join(os.getcwd(), "reports", "exports")
    # Safety: ensure path traversal can't escape folder
    safe_path = os.path.normpath(os.path.join(export_dir, filename))
    if not safe_path.startswith(os.path.normpath(export_dir)):
        return jsonify({"error": "Invalid filename"}), 400
    if not os.path.exists(safe_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(safe_path, as_attachment=True)

# API endpoint the frontend expects: generate (or return) a report for a run_id
@app.route("/api/report", methods=["GET"])
def api_generate_report():
    run_id = request.args.get("run_id")
    # Build a safe unique filename
    fname = f"azure_report_run_{run_id or 'all'}_{int(time.time())}.pdf"
    try:
        # generate_report(output_name, run_id=None) -> returns absolute or relative path
        pdf_path = generate_report(fname, run_id=run_id)
    except Exception as e:
        # Return a 500 with the error so frontend can show it
        return jsonify({"error": str(e)}), 500

    # pdf_path might be e.g. "reports/exports/azure_report_run_18_1700000000.pdf"
    pdf_name = os.path.basename(pdf_path)
    # Return the *URL* the frontend can use to download the file
    download_url = f"/reports/exports/{pdf_name}"
    return jsonify({"url": download_url})


@app.route('/api/findings', methods=['GET'])
def get_findings():
    run_id = request.args.get('run_id')
    
    # Use your existing DAO functions
    if run_id:
        findings_list = dao.get_findings_by_run(run_id)
    else:
        findings_list = dao.get_all_findings()
        
    # Map the DAO dictionaries to the Frontend API contract
    mapped_results = []
    for f in findings_list:
        # Parse 'evidence' and 'remediation' from JSON strings to objects/lists
        evidence = parse_json_field(f.get('evidence'), {})
        remediation = parse_json_field(f.get('remediation'), [])
        
        # If remediation is a list, join it into a string for the frontend table
        remediation_text = remediation
        if isinstance(remediation, list):
            remediation_text = "\n".join(remediation)
            
        mapped_results.append({
            "id": str(f.get('id')),
            "run_id": f.get('run_id'),
            "rule_id": f.get('rule_id'),
            "severity": f.get('severity'), # Must be 'High', 'Medium', 'Low', or 'Informational'
            "service": f.get('service'),
            "description": f.get('title'), # Frontend expects 'description', DB has 'title'
            "remediation_steps": remediation_text, 
            "resource_id": f.get('resource_id'),
            "evidence": evidence
        })
        
    return jsonify(mapped_results)

@app.route('/api/runs', methods=['GET'])
def get_runs():
    runs = dao.get_all_runs()

    mapped = []
    for r in runs:
        run_id = r.get("id")
        total = len(dao.get_findings_by_run(run_id))

        mapped.append({
            "run_id": str(run_id),
            "timestamp": (
                r.get("started_at").isoformat()
                if r.get("started_at") else None
            ),
            "status": r.get("status"),
            "total_findings": total
        })

    return jsonify(mapped)


# server.py - replace /api/trend with this implementation
from datetime import datetime
from collections import defaultdict

@app.route('/api/trend', methods=['GET'])
def get_trend():
    runs = dao.get_all_runs()  # returns runs from DAO
    # Use a map keyed by date string (YYYY-MM-DD) to aggregate multiple runs same day
    by_date = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0, "count_runs": 0})

    for r in runs:
        run_id = r.get("id")
        # Get findings for the run (list of dicts)
        findings = dao.get_findings_by_run(run_id)

        # Normalize started_at -> date_key (YYYY-MM-DD) for safe sorting and grouping
        started = r.get("started_at")
        date_key = None
        if started:
            if isinstance(started, str):
                # try to parse ISO string
                try:
                    dt = datetime.fromisoformat(started)
                except Exception:
                    try:
                        dt = datetime.strptime(started, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt = None
            else:
                dt = started  # datetime already
            if dt:
                date_key = dt.strftime("%Y-%m-%d")
        if date_key is None:
            # fallback to run id as unique key
            date_key = f"run-{run_id}"

        # count severities robustly (normalize text)
        for f in findings:
            sev = f.get("severity", "")
            if sev is None:
                continue
            s = str(sev).strip().lower()
            if s == "high":
                by_date[date_key]["high"] += 1
            elif s == "medium":
                by_date[date_key]["medium"] += 1
            elif s == "low":
                by_date[date_key]["low"] += 1
            else:
                # ignore or extend for informational
                pass

        by_date[date_key]["count_runs"] += 1

    # convert to list sorted by date (attempt to sort YYYY-MM-DD correctly)
    results = []
    for date_key, vals in by_date.items():
        # format the date for frontend expected style (MM/DD) while keeping stable ordering
        try:
            if date_key.startswith("run-"):
                label = date_key
                sort_key = date_key
            else:
                dt = datetime.strptime(date_key, "%Y-%m-%d")
                label = dt.strftime("%m/%d")
                sort_key = date_key
        except Exception:
            label = date_key
            sort_key = date_key

        results.append({
            "date": label,
            "high": vals["high"],
            "medium": vals["medium"],
            "low": vals["low"],
            "sort_key": sort_key
        })

    results = sorted(results, key=lambda x: x["sort_key"])
    # drop sort_key before returning
    for r in results:
        r.pop("sort_key", None)

    return jsonify(results)

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    # Trigger your existing scan logic
    try:
        # Example flow matching your 'app.py' logic:
        run_id = dao.start_run()
        
        # NOTE: In a real deployment, run this in a background thread!
        # For now, we run it synchronously to keep it simple.
        findings = run_scan.run()   # <-- adjusted to call run() from your run_scan.py
        if findings is None:
             findings = [] # Safety check
        dao.save_findings(run_id, findings)
        dao.finish_run(run_id)
        
        return jsonify({"message": "Scan completed", "runId": str(run_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Sentinel Scout API Bridge on port 5000...")
    app.run(debug=True, port=5000)
