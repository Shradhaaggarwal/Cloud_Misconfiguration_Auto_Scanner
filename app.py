import streamlit as st
import json
import concurrent.futures
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder

# project modules
from scanner.inventory import list_storage_accounts
from scanner.checks_azure import check_storage_public_blob_access
from scanner.check_storage_encryption import check_storage_encryption
from scanner.check_vms import list_vms_with_public_ip
from scanner.check_nsg import check_open_nsg_rules
from db import dao

# ------------- SCAN ENGINE (parallel) -------------
def run_all_checks():
    findings = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(list_storage_accounts): "storage",
            executor.submit(list_vms_with_public_ip): "vms",
            executor.submit(check_open_nsg_rules): "nsgs",
        }
        for future in concurrent.futures.as_completed(futures):
            service = futures[future]
            try:
                result = future.result()
                if service == "storage":
                    findings += check_storage_public_blob_access(result)
                    findings += check_storage_encryption(result)
                else:
                    findings += result
            except Exception as e:
                findings.append({
                    "rule_id": "ERROR",
                    "service": service,
                    "title": f"Error scanning {service}",
                    "severity": "Low",
                    "resource_id": "-",
                    "evidence": str(e),
                    "remediation": []
                })
    return findings

# ------------- UI PAGES -----------------
def landing_page():
    st.title("☁️ Azure Misconfiguration Auto Scanner")
    st.markdown("""
    ## 🔐 Welcome!
    A **next-gen CSPM-lite tool** to automatically detect misconfigurations in your Azure cloud.
    
    ### 🚀 Features:
    - Fast **parallel scans** across Azure resources
    - Smart **SQLite persistence** (trend history)
    - Intuitive **Findings Explorer** with filters & search
    - Beautiful **charts** & KPIs for risk posture
    - 📂 **Database browser** for raw evidence
    - 📝 **Exportable Reports** (HTML/PDF, coming soon)
    - 🤖 **GenAI Assistant** (explain findings in plain English, coming soon)

    ---
    """)
    if st.button("🔥 Run Quick Scan Now"):
        run_id = dao.start_run()
        with st.spinner("Running parallel scan..."):
            findings = run_all_checks()
            dao.save_findings(run_id, findings)
            dao.finish_run(run_id)
        st.success(f"✅ Scan finished with {len(findings)} findings.")
        st.json(findings)

def dashboard_page():
    import pandas as pd
    import plotly.express as px

    st.header("📊 Security Dashboard")
    findings = dao.get_all_findings()
    if not findings:
        st.warning("No findings yet. Run a scan first.")
        return

    # KPI metrics
    total = len(findings)
    highs = sum(1 for f in findings if f["severity"] == "High")
    meds = sum(1 for f in findings if f["severity"] == "Medium")
    lows = sum(1 for f in findings if f["severity"] == "Low")

    # Highlight storage encryption findings
    encryption_findings = [f for f in findings if f["rule_id"] == "AZ-Storage-Encryption-001"]
    if encryption_findings:
        st.info(f"🔒 {len(encryption_findings)} Storage Accounts missing encryption!")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Findings", total)
    col2.metric("High", highs, delta=f"{int((highs/total)*100)}%")
    col3.metric("Medium", meds, delta=f"{int((meds/total)*100)}%")
    col4.metric("Low", lows, delta=f"{int((lows/total)*100)}%")

    # Pie chart
    fig = px.pie(
        names=["High", "Medium", "Low"],
        values=[highs, meds, lows],
        title="Findings by Severity",
        color=["High", "Medium", "Low"],
        color_discrete_map={"High":"red","Medium":"orange","Low":"green"}
    )
    st.plotly_chart(fig)

    # Trendline chart (new)
    st.subheader("📈 Findings Trend over Runs")
    trend = dao.get_findings_trend()
    if trend:
        df_trend = pd.DataFrame(trend)
        df_trend["started_at"] = pd.to_datetime(df_trend["started_at"])

        line = px.line(
            df_trend,
            x="started_at",
            y="findings",
            text="findings",
            markers=True,
            title="Findings per Run Over Time"
        )
        st.plotly_chart(line)
    else:
        st.info("No runs recorded yet.")


def findings_page():
    import pandas as pd
    st.header("📑 Findings Explorer")
    findings = dao.get_all_findings()
    if not findings:
        st.info("No findings yet. Run a scan first.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(findings)

    # Apply color styles for severity (using Streamlit dataframe styling, not AgGrid)
    def color_severity(val):
        if val == "High":
            return "background-color: red; color: white"
        elif val == "Medium":
            return "background-color: orange; color: white"
        elif val == "Low":
            return "background-color: green; color: white"
        return ""

    st.write("### Filter Findings")
    severity = st.multiselect("Filter by Severity", ["High", "Medium", "Low"])
    service = st.multiselect("Filter by Service", list(df["service"].unique()))
    rule = st.multiselect("Filter by Rule ID", list(df["rule_id"].unique()))

    filtered = df
    if severity:
        filtered = filtered[filtered["severity"].isin(severity)]
    if service:
        filtered = filtered[filtered["service"].isin(service)]
    if rule:
        filtered = filtered[filtered["rule_id"].isin(rule)]

    st.write(f"Showing {len(filtered)} findings")

    # Show evidence details for encryption findings
    if not filtered.empty:
        st.write("### Evidence Preview for Encryption Findings")
        enc_findings = filtered[filtered["rule_id"] == "AZ-Storage-Encryption-001"]
        for _, row in enc_findings.iterrows():
            st.info(f"Resource: {row['resource_name']} | Evidence: {row['evidence']}")

    # Show a full-width table with wrapped evidence and remediation
    if not filtered.empty:
        import html
        def format_evidence(ev):
            if isinstance(ev, dict):
                return html.escape(json.dumps(ev, indent=2, ensure_ascii=False))
            return html.escape(str(ev))

        def format_remediation(rem):
            if isinstance(rem, list):
                return "<ul>" + "".join(f"<li>{html.escape(str(r))}</li>" for r in rem) + "</ul>"
            return html.escape(str(rem))

        # Build HTML table
        table_html = "<table style='width:100%;table-layout:fixed;word-break:break-word;'>"
        table_html += "<tr>" + "".join(f"<th>{col}</th>" for col in ["Rule ID", "Service", "Title", "Severity", "Resource", "Evidence", "Remediation"]) + "</tr>"
        for _, row in filtered.iterrows():
            table_html += "<tr>"
            table_html += f"<td>{html.escape(str(row['rule_id']))}</td>"
            table_html += f"<td>{html.escape(str(row['service']))}</td>"
            table_html += f"<td>{html.escape(str(row['title']))}</td>"
            table_html += f"<td>{html.escape(str(row['severity']))}</td>"
            table_html += f"<td>{html.escape(str(row.get('resource_name', row.get('resource_id'))))}</td>"
            table_html += f"<td><pre style='white-space:pre-wrap;'>{format_evidence(row['evidence'])}</pre></td>"
            table_html += f"<td>{format_remediation(row['remediation'])}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No findings to display.")


def database_page():
    st.header("🗄 Database Browser")
    findings = dao.get_all_findings()
    st.write("Raw DB contents:")
    st.json(findings)

from reports.generate_report import generate_report
import os

def reports_page():
    st.header("📝 Reports")

    # List available runs
    runs = dao.get_all_runs()  # we’ll add this helper
    run_ids = [r["id"] for r in runs]

    st.write("Select which run to generate a report for:")
    run_choice = st.selectbox("Run ID", ["All Runs"] + run_ids)

    if st.button("Generate Report PDF"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"azure_report_{timestamp}.pdf"

        if run_choice == "All Runs":
            pdf_path = generate_report(filename)
        else:
            pdf_path = generate_report(filename, run_id=run_choice)

        st.success(f"Report generated: {pdf_path}")
        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Download Report", f, file_name=filename)


# ------------- NAVIGATION ----------------
def main():
    with st.sidebar:
        selected = option_menu(
            "Navigation",
            ["Landing Page", "Dashboard", "Findings Explorer", "Database Browser", "Reports"],
            icons=["house", "bar-chart", "search", "database", "file-earmark-text"],
            menu_icon="cast",
            default_index=0,
        )
    if selected == "Landing Page":
        landing_page()
    elif selected == "Dashboard":
        dashboard_page()
    elif selected == "Findings Explorer":
        findings_page()
    elif selected == "Database Browser":
        database_page()
    elif selected == "Reports":
        reports_page()

if __name__ == "__main__":
    main()
