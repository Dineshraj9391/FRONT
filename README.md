# SpendWise — Smart Expense Tracker

A Flask-based expense tracking and budget management web app for students and families.

## Features
- Registration, login, logout and password hashing
- Dashboard with income, expenses, balance and budget progress
- Add/edit/delete expenses and income
- Categories, search and month filtering
- Monthly budgets with progress warnings
- Savings goals and contributions
- Needs vs wants analytics
- Expense analytics with Chart.js
- Recurring expense tracking
- Family member management
- Notifications and monthly reports
- Responsive Bootstrap UI
- SQLite by default for easy setup; database layer is isolated for future MySQL migration

## Run locally
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

Demo account is not pre-created; register a new account.
