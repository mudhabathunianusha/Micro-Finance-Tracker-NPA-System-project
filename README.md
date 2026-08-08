# Micro-Finance Tracker & NPA Dashboard

This project is a mini-project for tracking micro-finance loans, outstanding amounts, and Non-Performing Assets (NPA) using Python, SQLite, HTML, CSS, and Power BI.

## Project Features
- Loan entry for borrowers
- Outstanding amount tracking
- Recovery tracking
- NPA detection and summary
- Light dashboard with HTML/CSS interface
- Power BI-ready CSV export for analytics

## Project Structure
- app.py : Flask web application
- microfinance.db : SQLite database generated on the first run
- database.sql : SQL schema and sample data
- templates/index.html : dashboard page
- static/style.css : frontend styling
- powerbi_sample_data.csv : CSV dataset for Power BI

## How to Run
1. Open a terminal in the project folder.
2. Install dependencies:
   pip install -r requirements.txt
3. Start the application:
   python app.py
4. Open Chrome and visit:
   http://127.0.0.1:5000

## SQL Database Details
The database is stored in SQLite and includes the following tables:
- borrowers
- loans
- repayments

## Power BI Integration
1. Open Microsoft Power BI Desktop.
2. Click Get Data -> Text/CSV.
3. Select powerbi_sample_data.csv
4. Load the file and create visuals like:
   - Card for Total Portfolio
   - Card for Outstanding Amount
   - Donut chart for NPA vs Active
   - Bar chart for Branch-wise loan book
5. Add slicers for Loan Status and Village.

## Project Demo Link
Use this browser URL while running locally:
http://127.0.0.1:5000

## Guide Notes
This is a simple academic mini-project that demonstrates:
- Python for backend logic
- SQL for database design
- HTML/CSS for web UI
- Power BI for reporting and analysis
