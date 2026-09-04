# SpendWise — Smart Expense Tracker

SpendWise is a beginner-friendly **full-stack expense tracking and budget management system** built with Flask, SQLAlchemy, Bootstrap and Chart.js.

## Full-stack features
- User registration, login, logout and secure password hashing
- Personal dashboard with income, expenses, balance and budget progress
- Add and delete expenses and income
- Expense categories, search and month filtering
- Monthly category budgets
- Savings goals
- Needs vs wants analytics
- Chart.js analytics dashboard
- Recurring expenses
- Family member management
- Monthly reports
- Responsive Bootstrap UI
- SQLite for local development
- PostgreSQL support for persistent production deployment on Vercel

## Tech stack
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript, Chart.js
- **Backend:** Python, Flask, Flask-Login
- **Database:** SQLAlchemy + SQLite/PostgreSQL
- **Deployment:** Vercel

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

Open `http://127.0.0.1:5000` and register a new account.

## Vercel deployment
The project uses `api/index.py` as the Vercel Python entry point and `vercel.json` to route requests to Flask.

For a quick demo, the app can use a temporary SQLite database on Vercel. **For real persistent user data, configure a managed PostgreSQL database and set these Vercel environment variables:**

```text
DATABASE_URL=your-postgresql-connection-string
SECRET_KEY=your-long-random-secret
```

After environment variables are added, redeploy the project.

## Main routes
- `/` — landing page
- `/register` — create account
- `/login` — sign in
- `/dashboard` — overview
- `/expenses` — expense management
- `/income` — income management
- `/budget` — budgets
- `/analytics` — charts and spending analysis
- `/savings` — savings goals
- `/family` — family members
- `/recurring` — recurring expenses
- `/reports` — monthly report

## Project structure
```text
FRONT/
├── api/index.py
├── app.py
├── requirements.txt
├── vercel.json
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── expenses.html
│   ├── add_expense.html
│   ├── income.html
│   ├── budget.html
│   ├── analytics.html
│   ├── savings.html
│   ├── family.html
│   ├── recurring.html
│   └── reports.html
└── static/
    └── css/style.css
```
