from datetime import date, datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spendwise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    mode = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    icon = db.Column(db.String(20), default='wallet')
    kind = db.Column(db.String(20), default='expense')

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(255), default='')
    need_want = db.Column(db.String(10), default='need')
    spent_on = db.Column(db.Date, default=date.today)
    category = db.relationship('Category')

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    received_on = db.Column(db.Date, default=date.today)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    month = db.Column(db.String(7), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.relationship('Category')

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target = db.Column(db.Float, nullable=False)
    saved = db.Column(db.Float, default=0)
    deadline = db.Column(db.Date, nullable=True)

class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relation = db.Column(db.String(50), default='Member')
    monthly_limit = db.Column(db.Float, default=0)

class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), default='monthly')
    next_date = db.Column(db.Date, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def seed_categories():
    if Category.query.count(): return
    defaults = [('Food','fork','expense'),('Transport','car','expense'),('Shopping','bag','expense'),('Bills','receipt','expense'),('Education','book','expense'),('Health','heart','expense'),('Entertainment','play','expense'),('Other','wallet','expense')]
    db.session.add_all([Category(name=n, icon=i, kind=k) for n,i,k in defaults])
    db.session.commit()

def month_key(value=None):
    return (value or date.today()).strftime('%Y-%m')

def expense_total(uid, month=None):
    q = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == uid)
    if month: q = q.filter(func.strftime('%Y-%m', Expense.spent_on) == month)
    return float(q.scalar() or 0)

def income_total(uid, month=None):
    q = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(Income.user_id == uid)
    if month: q = q.filter(func.strftime('%Y-%m', Income.received_on) == month)
    return float(q.scalar() or 0)

@app.context_processor
def globals_processor():
    return {'today': date.today(), 'month_key': month_key()}

@app.route('/')
def index():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name, email = request.form.get('name','').strip(), request.form.get('email','').strip().lower()
        password, mode = request.form.get('password',''), request.form.get('mode','student')
        if not name or not email or len(password) < 6:
            flash('Enter your name/email and a password of at least 6 characters.', 'danger')
        elif User.query.filter_by(email=email).first(): flash('Email is already registered.', 'warning')
        else:
            user = User(name=name, email=email, password=generate_password_hash(password), mode=mode)
            db.session.add(user); db.session.commit(); login_user(user)
            flash('Welcome to SpendWise!', 'success'); return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if user and check_password_hash(user.password, request.form.get('password','')):
            login_user(user, remember=True); return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    m = month_key(); expenses = expense_total(current_user.id, m); income = income_total(current_user.id, m)
    budgets = Budget.query.filter_by(user_id=current_user.id, month=m).all()
    budget_total = sum(b.amount for b in budgets)
    recent = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.spent_on.desc(), Expense.id.desc()).limit(6).all()
    cats = db.session.query(Category.name, func.sum(Expense.amount)).join(Expense, Expense.category_id == Category.id).filter(Expense.user_id == current_user.id, func.strftime('%Y-%m', Expense.spent_on) == m).group_by(Category.name).all()
    return render_template('dashboard.html', income=income, expenses=expenses, balance=income-expenses, budget=budget_total, budget_used=expenses, recent=recent, cat_labels=[x[0] for x in cats], cat_values=[float(x[1]) for x in cats])

@app.route('/expenses')
@login_required
def expenses():
    q = Expense.query.filter_by(user_id=current_user.id)
    search = request.args.get('search','').strip(); month = request.args.get('month', month_key())
    if search: q = q.join(Category).filter((Expense.note.ilike(f'%{search}%')) | (Category.name.ilike(f'%{search}%')))
    if month: q = q.filter(func.strftime('%Y-%m', Expense.spent_on) == month)
    return render_template('expenses.html', expenses=q.order_by(Expense.spent_on.desc(), Expense.id.desc()).all(), categories=Category.query.all(), selected_month=month, search=search)

@app.route('/expenses/add', methods=['GET','POST'])
@login_required
def add_expense():
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            e = Expense(user_id=current_user.id, category_id=int(request.form['category_id']), amount=float(request.form['amount']), note=request.form.get('note','').strip(), need_want=request.form.get('need_want','need'), spent_on=datetime.strptime(request.form['spent_on'],'%Y-%m-%d').date())
            db.session.add(e); db.session.commit(); flash('Expense added.', 'success'); return redirect(url_for('expenses'))
        except (ValueError, KeyError): flash('Please enter valid expense details.', 'danger')
    return render_template('add_expense.html', categories=categories, expense=None)

@app.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    e = db.session.get(Expense, expense_id)
    if not e or e.user_id != current_user.id: return jsonify({'error':'Not found'}), 404
    db.session.delete(e); db.session.commit(); flash('Expense deleted.', 'success'); return redirect(url_for('expenses'))

@app.route('/income', methods=['GET','POST'])
@login_required
def income():
    if request.method == 'POST':
        try:
            i = Income(user_id=current_user.id, source=request.form['source'].strip(), amount=float(request.form['amount']), received_on=datetime.strptime(request.form['received_on'],'%Y-%m-%d').date())
            db.session.add(i); db.session.commit(); flash('Income added.', 'success'); return redirect(url_for('income'))
        except (ValueError, KeyError): flash('Please enter valid income details.', 'danger')
    rows = Income.query.filter_by(user_id=current_user.id).order_by(Income.received_on.desc()).all()
    return render_template('income.html', incomes=rows)

@app.route('/income/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    i = db.session.get(Income, income_id)
    if not i or i.user_id != current_user.id: return jsonify({'error':'Not found'}), 404
    db.session.delete(i); db.session.commit(); flash('Income deleted.', 'success'); return redirect(url_for('income'))

@app.route('/budget', methods=['GET','POST'])
@login_required
def budget():
    if request.method == 'POST':
        try:
            b = Budget.query.filter_by(user_id=current_user.id, category_id=int(request.form['category_id']), month=request.form['month']).first()
            if b: b.amount = float(request.form['amount'])
            else: db.session.add(Budget(user_id=current_user.id, category_id=int(request.form['category_id']), month=request.form['month'], amount=float(request.form['amount'])))
            db.session.commit(); flash('Budget saved.', 'success'); return redirect(url_for('budget'))
        except (ValueError, KeyError): flash('Invalid budget details.', 'danger')
    rows = Budget.query.filter_by(user_id=current_user.id, month=month_key()).all()
    data=[]
    for b in rows:
        spent = float(db.session.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.user_id==current_user.id, Expense.category_id==b.category_id, func.strftime('%Y-%m',Expense.spent_on)==b.month).scalar() or 0)
        data.append((b, spent))
    return render_template('budget.html', budgets=data, categories=Category.query.all())

@app.route('/savings', methods=['GET','POST'])
@login_required
def savings():
    if request.method == 'POST':
        try:
            g = SavingsGoal(user_id=current_user.id, name=request.form['name'].strip(), target=float(request.form['target']), saved=float(request.form.get('saved',0)), deadline=datetime.strptime(request.form['deadline'],'%Y-%m-%d').date() if request.form.get('deadline') else None)
            db.session.add(g); db.session.commit(); flash('Savings goal created.', 'success'); return redirect(url_for('savings'))
        except (ValueError, KeyError): flash('Invalid savings goal.', 'danger')
    return render_template('savings.html', goals=SavingsGoal.query.filter_by(user_id=current_user.id).all())

@app.route('/analytics')
@login_required
def analytics():
    m=month_key(); cats=db.session.query(Category.name,func.sum(Expense.amount)).join(Expense,Expense.category_id==Category.id).filter(Expense.user_id==current_user.id,func.strftime('%Y-%m',Expense.spent_on)==m).group_by(Category.name).all()
    needs=float(db.session.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.user_id==current_user.id,Expense.need_want=='need',func.strftime('%Y-%m',Expense.spent_on)==m).scalar() or 0)
    wants=float(db.session.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.user_id==current_user.id,Expense.need_want=='want',func.strftime('%Y-%m',Expense.spent_on)==m).scalar() or 0)
    return render_template('analytics.html', labels=[x[0] for x in cats], values=[float(x[1]) for x in cats], needs=needs, wants=wants, income=income_total(current_user.id,m), expenses=expense_total(current_user.id,m))

@app.route('/family', methods=['GET','POST'])
@login_required
def family():
    if request.method == 'POST':
        try:
            db.session.add(FamilyMember(user_id=current_user.id,name=request.form['name'].strip(),relation=request.form.get('relation','Member'),monthly_limit=float(request.form.get('monthly_limit',0))))
            db.session.commit(); flash('Family member added.', 'success')
        except ValueError: flash('Invalid monthly limit.', 'danger')
    return render_template('family.html', members=FamilyMember.query.filter_by(user_id=current_user.id).all())

@app.route('/recurring', methods=['GET','POST'])
@login_required
def recurring():
    if request.method == 'POST':
        try:
            db.session.add(RecurringExpense(user_id=current_user.id,name=request.form['name'].strip(),amount=float(request.form['amount']),frequency=request.form.get('frequency','monthly'),next_date=datetime.strptime(request.form['next_date'],'%Y-%m-%d').date()))
            db.session.commit(); flash('Recurring expense saved.', 'success')
        except (ValueError, KeyError): flash('Invalid recurring expense.', 'danger')
    return render_template('recurring.html', items=RecurringExpense.query.filter_by(user_id=current_user.id).order_by(RecurringExpense.next_date).all())

@app.route('/reports')
@login_required
def reports():
    m=month_key(); return render_template('reports.html', month=m, income=income_total(current_user.id,m), expenses=expense_total(current_user.id,m), balance=income_total(current_user.id,m)-expense_total(current_user.id,m))

@app.route('/api/summary')
@login_required
def api_summary():
    m=month_key(); return jsonify({'income':income_total(current_user.id,m),'expenses':expense_total(current_user.id,m),'balance':income_total(current_user.id,m)-expense_total(current_user.id,m)})

@app.cli.command('init-db')
def init_db_command():
    db.create_all(); seed_categories(); print('Database initialized.')

with app.app_context():
    db.create_all(); seed_categories()

if __name__ == '__main__':
    app.run(debug=True)
