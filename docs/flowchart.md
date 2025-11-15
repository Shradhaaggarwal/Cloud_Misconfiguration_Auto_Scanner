# Project Flowchart

This diagram shows the high-level architecture and data flow for the Cloud_Misconfiguration_Auto_Scanner project.

- Streamlit UI (`app.py`) and CLI (`run_scan.py`) trigger scans.
- `scanner/inventory.py` queries Azure and returns resources to scanner modules.
- Scanner modules (`scanner/*.py`) produce findings which are saved by `db/dao.py`.
- `reports/generate_report.py` renders `reports/template.html` and optionally converts to PDF using wkhtmltopdf + pdfkit.

View the flowchart image below (open in VS Code or a browser):

![Architecture flowchart](./architecture_flowchart.svg)

Notes
- The SVG is an editable, plain-text file — you can tweak positions, labels, or colors directly.
- If you want a PNG export, open the SVG in a browser and export or use a command-line tool like `rsvg-convert` or `inkscape`.
