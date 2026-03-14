from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.config['SECRET_KEY'] = 'cleveland-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cleveland.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ═══════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════

class Staff(db.Model):
    __tablename__ = 'staff'
    id       = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(50), unique=True)
    email    = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role     = db.Column(db.String(50))

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.String(20))
    description = db.Column(db.String(200))
    type        = db.Column(db.String(50))
    amount      = db.Column(db.Float, default=0)
    status      = db.Column(db.String(20))

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100))
    category      = db.Column(db.String(50), default='Other')
    unit          = db.Column(db.String(20), default='pcs')
    quantity      = db.Column(db.Integer, default=0)
    unit_price    = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Integer, default=10)

class Student(db.Model):
    __tablename__ = 'students'
    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.String(50), unique=True)
    first_name  = db.Column(db.String(100))
    last_name   = db.Column(db.String(100))
    full_name   = db.Column(db.String(200))
    dob         = db.Column(db.String(20))
    national_id = db.Column(db.String(50))
    phone       = db.Column(db.String(20))
    email       = db.Column(db.String(100))
    program     = db.Column(db.String(100))
    year        = db.Column(db.Integer)
    intake_year = db.Column(db.Integer)
    tuition_fee = db.Column(db.Float, default=0)
    amount_paid = db.Column(db.Float, default=0)
    balance     = db.Column(db.Float, default=0)
    status      = db.Column(db.String(30), default='Active')
    payments    = db.relationship('Payment', backref='student', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    id          = db.Column(db.Integer, primary_key=True)
    receipt_no  = db.Column(db.String(50), unique=True)
    date        = db.Column(db.String(20))
    student_id  = db.Column(db.Integer, db.ForeignKey('students.id'))
    amount      = db.Column(db.Float, default=0)
    method      = db.Column(db.String(50))
    notes       = db.Column(db.String(200))
    recorded_by = db.Column(db.String(100))

class Expense(db.Model):
    __tablename__ = 'expenses'
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.String(20))
    vendor      = db.Column(db.String(100))
    category    = db.Column(db.String(50))
    description = db.Column(db.String(200))
    amount      = db.Column(db.Float, default=0)
    due_date    = db.Column(db.String(20))
    status      = db.Column(db.String(20), default='pending')
    recorded_by = db.Column(db.String(100))

class CashTransaction(db.Model):
    __tablename__ = 'cash_transactions'
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.String(20))
    description = db.Column(db.String(200))
    cb_type     = db.Column(db.String(20))
    account     = db.Column(db.String(50))
    amount      = db.Column(db.Float, default=0)
    reference   = db.Column(db.String(100))
    recorded_by = db.Column(db.String(100))

class Grant(db.Model):
    __tablename__ = 'grants'
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.String(20))
    source      = db.Column(db.String(100))
    type        = db.Column(db.String(50))
    description = db.Column(db.String(200))
    amount      = db.Column(db.Float, default=0)
    reference   = db.Column(db.String(100))
    recorded_by = db.Column(db.String(100))

class Payroll(db.Model):
    __tablename__ = 'payroll'
    id           = db.Column(db.Integer, primary_key=True)
    staff_id     = db.Column(db.String(50))
    staff_name   = db.Column(db.String(100))
    role         = db.Column(db.String(50))
    period       = db.Column(db.String(50))
    gross_salary = db.Column(db.Float, default=0)
    paye         = db.Column(db.Float, default=0)
    nhif         = db.Column(db.Float, default=0)
    nssf         = db.Column(db.Float, default=0)
    net_pay      = db.Column(db.Float, default=0)
    status       = db.Column(db.String(20), default='pending')
    pay_date     = db.Column(db.String(20))
    recorded_by  = db.Column(db.String(100))


# ═══════════════════════════════════════════
# CREATE TABLES
# ═══════════════════════════════════════════

with app.app_context():
    db.create_all()


# ═══════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════

@app.route('/')
def home():
    return render_template("index.html")


# ═══════════════════════════════════════════
# STAFF LOGIN
# ═══════════════════════════════════════════

@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        identifier = request.form.get('username')
        password   = request.form.get('password')
        role       = request.form.get('role')
        staff = Staff.query.filter(
            (Staff.staff_id == identifier) | (Staff.email == identifier)
        ).first()
        if staff and staff.password == password and staff.role == role:
            session['role']     = staff.role
            session['username'] = staff.staff_id
            session['email']    = staff.email
            if staff.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif staff.role == 'finance':
                return redirect(url_for('finance_dashboard'))
            elif staff.role == 'front_office':
                return redirect(url_for('front_office_dashboard'))
        else:
            flash('Invalid credentials or role mismatch. Please try again.')
    return render_template("staff_login.html")


# ═══════════════════════════════════════════
# STUDENT LOGIN
# ═══════════════════════════════════════════

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    return render_template("student_login.html")


# ═══════════════════════════════════════════
# ADMIN DASHBOARD
# ═══════════════════════════════════════════

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))

    total_students      = Student.query.count()
    staff_count         = Staff.query.count()
    students_owing      = Student.query.filter(Student.balance > 0).count()
    total_courses       = 0
    total_announcements = 0
    upcoming_exams      = 0
    recent_students     = Student.query.order_by(Student.id.desc()).limit(5).all()
    latest_announcements = []

    return render_template('admin_dashboard.html',
                           total_students=total_students,
                           staff_count=staff_count,
                           students_owing=students_owing,
                           total_courses=total_courses,
                           total_announcements=total_announcements,
                           upcoming_exams=upcoming_exams,
                           recent_students=recent_students,
                           latest_announcements=latest_announcements)

# ═══════════════════════════════════════════
# STAFF MANAGEMENT
# ═══════════════════════════════════════════

@app.route('/manage-staff')
def manage_staff():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('manage_staff.html', staff_list=Staff.query.order_by(Staff.id).all())

@app.route('/manage-staff/add', methods=['POST'])
def add_staff():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    staff_id = request.form.get('staff_id')
    email    = request.form.get('email')
    existing = Staff.query.filter((Staff.staff_id == staff_id) | (Staff.email == email)).first()
    if existing:
        flash('A staff member with that ID or email already exists.', 'error')
        return redirect(url_for('manage_staff'))
    db.session.add(Staff(staff_id=staff_id, email=email,
        password=request.form.get('password'), role=request.form.get('role')))
    db.session.commit()
    flash(f'Staff member {staff_id} added successfully.', 'success')
    return redirect(url_for('manage_staff'))

@app.route('/manage-staff/<int:staff_id>/delete', methods=['POST'])
def delete_staff(staff_id):
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    staff = Staff.query.get_or_404(staff_id)
    if staff.staff_id == session.get('username'):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('manage_staff'))
    db.session.delete(staff)
    db.session.commit()
    flash(f'{staff.staff_id} has been removed.', 'success')
    return redirect(url_for('manage_staff'))


# ═══════════════════════════════════════════
# STUDENTS
# ═══════════════════════════════════════════

@app.route('/students')
def students():
    if session.get('role') not in ['admin', 'front_office']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('students.html', students=Student.query.order_by(Student.id.desc()).all())

@app.route('/students/add', methods=['POST'])
def add_student():
    if session.get('role') not in ['admin', 'front_office']:
        return redirect(url_for('staff_login'))
    first_name  = request.form.get('first_name')
    last_name   = request.form.get('last_name')
    tuition_fee = float(request.form.get('tuition_fee') or 0)
    amount_paid = float(request.form.get('amount_paid') or 0)
    db.session.add(Student(
        student_id=request.form.get('student_id'),
        first_name=first_name, last_name=last_name,
        full_name=f"{first_name} {last_name}",
        dob=request.form.get('dob'), national_id=request.form.get('national_id'),
        phone=request.form.get('phone'), email=request.form.get('email'),
        program=request.form.get('program'), year=int(request.form.get('year') or 1),
        intake_year=request.form.get('intake_year'),
        tuition_fee=tuition_fee, amount_paid=amount_paid,
        balance=tuition_fee - amount_paid, status=request.form.get('status', 'Active'),
    ))
    db.session.commit()
    flash('Student added successfully.', 'success')
    return redirect(url_for('students'))

@app.route('/students/<int:student_id>')
def student_profile(student_id):
    if session.get('role') not in ['admin', 'front_office']:
        return redirect(url_for('staff_login'))
    return render_template('student_profile.html',
        student=Student.query.get_or_404(student_id),
        today=date.today().isoformat())

@app.route('/students/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    if session.get('role') != 'admin':
        flash('Only administrators can delete students.')
        return redirect(url_for('students'))
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'{student.full_name} has been deleted.', 'success')
    return redirect(url_for('students'))


# ═══════════════════════════════════════════
# TUITION & PAYMENTS
# ═══════════════════════════════════════════

@app.route('/tuition-payments')
def tuition_payments():
    if session.get('role') not in ['admin', 'front_office', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    all_students      = Student.query.order_by(Student.full_name).all()
    payments          = Payment.query.order_by(Payment.id.desc()).all()
    total_collected   = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    total_outstanding = db.session.query(db.func.sum(Student.balance)).scalar() or 0
    fully_paid        = Student.query.filter(Student.balance == 0).count()
    with_balance      = Student.query.filter(Student.balance > 0).count()
    return render_template('tuition_payments.html',
        students=all_students, payments=payments,
        total_collected=total_collected, total_outstanding=total_outstanding,
        fully_paid=fully_paid, with_balance=with_balance,
        today=date.today().isoformat(),
    )

@app.route('/tuition-payments/record', methods=['POST'])
def record_payment():
    if session.get('role') not in ['admin', 'front_office', 'finance']:
        return redirect(url_for('staff_login'))
    student    = Student.query.get_or_404(request.form.get('student_id'))
    amount     = float(request.form.get('amount') or 0)
    pay_date   = request.form.get('date')
    receipt_no = request.form.get('receipt_no')
    method     = request.form.get('method')
    db.session.add(Payment(
        receipt_no=receipt_no, date=pay_date, student_id=student.id,
        amount=amount, method=method,
        notes=request.form.get('notes'), recorded_by=session.get('username'),
    ))
    student.amount_paid += amount
    student.balance      = max(0, student.tuition_fee - student.amount_paid)
    db.session.add(Transaction(
        date=pay_date,
        description=f"Tuition payment — {student.full_name} ({receipt_no})",
        type='income', amount=amount, status='paid',
    ))
    account_map = {'Cash':'Cash','M-Pesa':'M-Pesa','Bank Transfer':'Bank','Cheque':'Bank','Card':'Bank'}
    db.session.add(CashTransaction(
        date=pay_date,
        description=f"Tuition — {student.full_name} ({receipt_no})",
        cb_type='deposit', account=account_map.get(method, 'Cash'),
        amount=amount, recorded_by=session.get('username'),
    ))
    db.session.commit()
    flash(f'Payment of KSh {amount:,.2f} recorded for {student.full_name}. Receipt: {receipt_no}', 'success')
    return redirect(url_for('tuition_payments'))


# ═══════════════════════════════════════════
# ACCOUNTS RECEIVABLE
# ═══════════════════════════════════════════

@app.route('/accounts-receivable')
def accounts_receivable():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    all_students     = Student.query.order_by(Student.full_name).all()
    payments         = Payment.query.order_by(Payment.id.desc()).all()
    total_receivable = db.session.query(db.func.sum(Student.balance)).scalar() or 0
    total_collected  = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    current_count    = Student.query.filter(Student.balance > 0).count()
    overdue_count    = Student.query.filter(Student.balance > 0, Student.intake_year < 2026).count()
    return render_template('accounts_receivable.html',
        students=all_students, payments=payments,
        total_receivable=total_receivable, total_collected=total_collected,
        current_count=current_count, overdue_count=overdue_count,
    )


# ═══════════════════════════════════════════
# ACCOUNTS PAYABLE
# ═══════════════════════════════════════════

@app.route('/accounts-payable')
def accounts_payable():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    expenses      = Expense.query.order_by(Expense.id.desc()).all()
    total_payable = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_pending = db.session.query(db.func.sum(Expense.amount)).filter_by(status='pending').scalar() or 0
    total_paid    = db.session.query(db.func.sum(Expense.amount)).filter_by(status='paid').scalar() or 0
    overdue_count = Expense.query.filter(
        Expense.status == 'pending',
        Expense.due_date < date.today().isoformat()
    ).count()
    return render_template('accounts_payable.html',
        expenses=expenses, total_payable=total_payable,
        total_pending=total_pending, total_paid=total_paid,
        overdue_count=overdue_count, today=date.today().isoformat(),
    )

@app.route('/accounts-payable/add', methods=['POST'])
def add_expense():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    amount   = float(request.form.get('amount') or 0)
    exp_date = request.form.get('date')
    status   = request.form.get('status', 'pending')
    db.session.add(Expense(
        date=exp_date, vendor=request.form.get('vendor'),
        category=request.form.get('category'),
        description=request.form.get('description'),
        amount=amount, due_date=request.form.get('due_date'),
        status=status, recorded_by=session.get('username'),
    ))
    db.session.add(Transaction(
        date=exp_date,
        description=f"{request.form.get('category')} — {request.form.get('vendor')}",
        type='expense', amount=amount, status=status,
    ))
    db.session.commit()
    flash(f'Expense of KSh {amount:,.2f} added successfully.', 'success')
    return redirect(url_for('accounts_payable'))

@app.route('/accounts-payable/<int:expense_id>/pay', methods=['POST'])
def mark_expense_paid(expense_id):
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    expense = Expense.query.get_or_404(expense_id)
    expense.status = 'paid'
    db.session.add(CashTransaction(
        date=date.today().isoformat(),
        description=f"Payment — {expense.vendor}: {expense.description}",
        cb_type='withdrawal', account='Bank',
        amount=expense.amount, recorded_by=session.get('username'),
    ))
    db.session.commit()
    flash('Expense marked as paid.', 'success')
    return redirect(url_for('accounts_payable'))

@app.route('/accounts-payable/<int:expense_id>/delete', methods=['POST'])
def delete_expense(expense_id):
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('accounts_payable'))


# ═══════════════════════════════════════════
# CASH & BANK
# ═══════════════════════════════════════════

@app.route('/cash-and-bank')
def cash_and_bank():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    cb_transactions = CashTransaction.query.order_by(CashTransaction.id.desc()).all()
    def bal(account):
        deps = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(account=account, cb_type='deposit').scalar() or 0
        wds  = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(account=account, cb_type='withdrawal').scalar() or 0
        return deps - wds
    cash_balance      = bal('Cash')
    bank_balance      = bal('Bank')
    mpesa_balance     = bal('M-Pesa')
    total_deposits    = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(cb_type='deposit').scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(cb_type='withdrawal').scalar() or 0
    transaction_count = CashTransaction.query.count()
    return render_template('cash_and_bank.html',
        cb_transactions=cb_transactions,
        cash_balance=cash_balance, bank_balance=bank_balance, mpesa_balance=mpesa_balance,
        total_deposits=total_deposits, total_withdrawals=total_withdrawals,
        transaction_count=transaction_count, today=date.today().isoformat(),
    )

@app.route('/cash-and-bank/add', methods=['POST'])
def add_cash_transaction():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    amount = float(request.form.get('amount') or 0)
    db.session.add(CashTransaction(
        date=request.form.get('date'),
        description=request.form.get('description'),
        cb_type=request.form.get('cb_type'),
        account=request.form.get('account'),
        amount=amount,
        reference=request.form.get('reference'),
        recorded_by=session.get('username'),
    ))
    db.session.commit()
    flash(f'Transaction of KSh {amount:,.2f} recorded successfully.', 'success')
    return redirect(url_for('cash_and_bank'))


# ═══════════════════════════════════════════
# GRANTS & DONATIONS
# ═══════════════════════════════════════════

@app.route('/grants-donations')
def grants_donations():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    grants          = Grant.query.order_by(Grant.id.desc()).all()
    total_received  = db.session.query(db.func.sum(Grant.amount)).scalar() or 0
    total_grants    = db.session.query(db.func.sum(Grant.amount)).filter_by(type='Grant').scalar() or 0
    total_donations = db.session.query(db.func.sum(Grant.amount)).filter_by(type='Donation').scalar() or 0
    total_count     = Grant.query.count()
    return render_template('grants_donations.html',
        grants=grants, total_received=total_received,
        total_grants=total_grants, total_donations=total_donations,
        total_count=total_count, today=date.today().isoformat(),
    )

@app.route('/grants-donations/add', methods=['POST'])
def add_grant():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    amount = float(request.form.get('amount') or 0)
    gdate  = request.form.get('date')
    gtype  = request.form.get('type')
    db.session.add(Grant(
        date=gdate, source=request.form.get('source'),
        type=gtype, description=request.form.get('description'),
        amount=amount, reference=request.form.get('reference'),
        recorded_by=session.get('username'),
    ))
    db.session.add(Transaction(
        date=gdate,
        description=f"{gtype} — {request.form.get('source')}",
        type=gtype.lower(), amount=amount, status='paid',
    ))
    db.session.add(CashTransaction(
        date=gdate,
        description=f"{gtype} — {request.form.get('source')}",
        cb_type='deposit', account='Bank',
        amount=amount, recorded_by=session.get('username'),
    ))
    db.session.commit()
    flash(f'{gtype} of KSh {amount:,.2f} recorded successfully.', 'success')
    return redirect(url_for('grants_donations'))

@app.route('/grants-donations/<int:grant_id>/delete', methods=['POST'])
def delete_grant(grant_id):
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    grant = Grant.query.get_or_404(grant_id)
    db.session.delete(grant)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('grants_donations'))



# ═══════════════════════════════════════════
# PAYROLL
# ═══════════════════════════════════════════

@app.route('/payroll')
def payroll():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payroll_records  = Payroll.query.order_by(Payroll.id.desc()).all()
    total_gross      = db.session.query(db.func.sum(Payroll.gross_salary)).scalar() or 0
    total_deductions = db.session.query(db.func.sum(Payroll.paye + Payroll.nhif + Payroll.nssf)).scalar() or 0
    total_net        = db.session.query(db.func.sum(Payroll.net_pay)).scalar() or 0
    staff_count      = db.session.query(Payroll.staff_id).distinct().count()
    return render_template('payroll.html',
        payroll_records=payroll_records,
        total_gross=total_gross, total_deductions=total_deductions,
        total_net=total_net, staff_count=staff_count,
        today=date.today().isoformat(),
    )

@app.route('/payroll/add', methods=['POST'])
def add_payroll():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    gross  = float(request.form.get('gross_salary') or 0)
    net    = float(request.form.get('net_pay') or 0)
    status = request.form.get('status', 'pending')
    pdate  = request.form.get('pay_date')
    period = request.form.get('period')
    sname  = request.form.get('staff_name')
    db.session.add(Payroll(
        staff_id=request.form.get('staff_id'),
        staff_name=sname, role=request.form.get('role'),
        period=period, gross_salary=gross,
        paye=float(request.form.get('paye') or 0),
        nhif=float(request.form.get('nhif') or 0),
        nssf=float(request.form.get('nssf') or 0),
        net_pay=net, status=status,
        pay_date=pdate, recorded_by=session.get('username'),
    ))
    db.session.add(Transaction(
        date=pdate or date.today().isoformat(),
        description=f"Salary — {sname} ({period})",
        type='payroll', amount=gross, status=status,
    ))
    if status == 'paid':
        db.session.add(CashTransaction(
            date=pdate or date.today().isoformat(),
            description=f"Salary payment — {sname} ({period})",
            cb_type='withdrawal', account='Bank',
            amount=net, recorded_by=session.get('username'),
        ))
    db.session.commit()
    flash(f'Payroll record for {sname} added. Net pay: KSh {net:,.2f}', 'success')
    return redirect(url_for('payroll'))

@app.route('/payroll/<int:payroll_id>/pay', methods=['POST'])
def mark_payroll_paid(payroll_id):
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    p = Payroll.query.get_or_404(payroll_id)
    p.status = 'paid'
    db.session.add(CashTransaction(
        date=date.today().isoformat(),
        description=f"Salary payment — {p.staff_name} ({p.period})",
        cb_type='withdrawal', account='Bank',
        amount=p.net_pay, recorded_by=session.get('username'),
    ))
    db.session.commit()
    flash(f'Payroll for {p.staff_name} marked as paid.', 'success')
    return redirect(url_for('payroll'))

@app.route('/payroll/<int:payroll_id>/delete', methods=['POST'])
def delete_payroll(payroll_id):
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    p = Payroll.query.get_or_404(payroll_id)
    db.session.delete(p)
    db.session.commit()
    flash('Payroll record deleted.', 'success')
    return redirect(url_for('payroll'))


# ═══════════════════════════════════════════
# INVENTORY
# ═══════════════════════════════════════════

@app.route('/inventory')
def inventory():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    items          = Inventory.query.order_by(Inventory.name).all()
    total_items    = Inventory.query.count()
    total_value    = sum(i.quantity * i.unit_price for i in items)
    low_stock_count= Inventory.query.filter(Inventory.quantity <= Inventory.reorder_level, Inventory.quantity > 0).count()
    out_of_stock   = Inventory.query.filter(Inventory.quantity == 0).count()
    return render_template('inventory.html',
        items=items, total_items=total_items, total_value=total_value,
        low_stock_count=low_stock_count, out_of_stock=out_of_stock,
    )

@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    db.session.add(Inventory(
        name=request.form.get('name'),
        category=request.form.get('category', 'Other'),
        unit=request.form.get('unit', 'pcs'),
        quantity=int(request.form.get('quantity') or 0),
        unit_price=float(request.form.get('unit_price') or 0),
        reorder_level=int(request.form.get('reorder_level') or 10),
    ))
    db.session.commit()
    flash(f'{request.form.get("name")} added to inventory.', 'success')
    return redirect(url_for('inventory'))

@app.route('/inventory/restock', methods=['POST'])
def restock_inventory():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    item = Inventory.query.get_or_404(request.form.get('item_id'))
    add_qty = int(request.form.get('add_quantity') or 0)
    item.quantity += add_qty
    db.session.commit()
    flash(f'{item.name} restocked by {add_qty}. New quantity: {item.quantity}.', 'success')
    return redirect(url_for('inventory'))

@app.route('/inventory/edit', methods=['POST'])
def edit_inventory():
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    item = Inventory.query.get_or_404(request.form.get('item_id'))
    item.name          = request.form.get('name')
    item.category      = request.form.get('category', 'Other')
    item.unit          = request.form.get('unit', 'pcs')
    item.quantity      = int(request.form.get('quantity') or 0)
    item.unit_price    = float(request.form.get('unit_price') or 0)
    item.reorder_level = int(request.form.get('reorder_level') or 10)
    db.session.commit()
    flash(f'{item.name} updated successfully.', 'success')
    return redirect(url_for('inventory'))

@app.route('/inventory/<int:item_id>/delete', methods=['POST'])
def delete_inventory(item_id):
    if session.get('role') not in ['admin', 'finance']:
        return redirect(url_for('staff_login'))
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'{item.name} deleted from inventory.', 'success')
    return redirect(url_for('inventory'))


# ═══════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════

@app.route('/reports')
def reports():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))

    from sqlalchemy import func

    # Income
    tuition_collected = db.session.query(func.sum(Payment.amount)).scalar() or 0
    grants_total      = db.session.query(func.sum(Grant.amount)).filter_by(type='Grant').scalar() or 0
    donations_total   = db.session.query(func.sum(Grant.amount)).filter_by(type='Donation').scalar() or 0
    other_income      = db.session.query(func.sum(Grant.amount)).filter(
                            Grant.type.notin_(['Grant','Donation'])).scalar() or 0
    total_income      = tuition_collected + grants_total + donations_total + other_income

    # Expenses
    utilities_total   = db.session.query(func.sum(Expense.amount)).filter_by(category='Utility').scalar() or 0
    suppliers_total   = db.session.query(func.sum(Expense.amount)).filter_by(category='Supplier').scalar() or 0
    rent_total        = db.session.query(func.sum(Expense.amount)).filter_by(category='Rent').scalar() or 0
    other_expenses    = db.session.query(func.sum(Expense.amount)).filter_by(category='Other').scalar() or 0
    expenses_only     = db.session.query(func.sum(Expense.amount)).scalar() or 0
    payroll_total     = db.session.query(func.sum(Payroll.gross_salary)).scalar() or 0
    total_expenses    = expenses_only + payroll_total
    pending_expenses  = db.session.query(func.sum(Expense.amount)).filter_by(status='pending').scalar() or 0
    paid_expenses     = db.session.query(func.sum(Expense.amount)).filter_by(status='paid').scalar() or 0
    payroll_count     = Payroll.query.count()
    pending_payroll   = Payroll.query.filter_by(status='pending').count()
    pending_payroll_amount = db.session.query(func.sum(Payroll.net_pay)).filter_by(status='pending').scalar() or 0

    # Net
    net_surplus = total_income - total_expenses

    # AR
    total_ar     = db.session.query(func.sum(Student.balance)).scalar() or 0
    fully_paid   = Student.query.filter(Student.balance == 0).count()
    with_balance = Student.query.filter(Student.balance > 0).count()
    total_students = Student.query.count()

    # Cash & Bank balances
    def bal(account):
        deps = db.session.query(func.sum(CashTransaction.amount)).filter_by(account=account, cb_type='deposit').scalar() or 0
        wds  = db.session.query(func.sum(CashTransaction.amount)).filter_by(account=account, cb_type='withdrawal').scalar() or 0
        return deps - wds

    cash_balance  = bal('Cash')
    bank_balance  = bal('Bank')
    mpesa_balance = bal('M-Pesa')

    # Inventory value
    inventory_items = Inventory.query.all()
    inventory_value = sum(i.quantity * i.unit_price for i in inventory_items)

    # Tables
    income_transactions = Transaction.query.filter(
        Transaction.type.in_(['income','grant','donation'])
    ).order_by(Transaction.id.desc()).limit(20).all()
    expense_list = Expense.query.order_by(Expense.id.desc()).all()
    all_students = Student.query.order_by(Student.full_name).all()

    return render_template('reports.html',
        total_income=total_income, total_expenses=total_expenses,
        net_surplus=net_surplus, total_ar=total_ar,
        tuition_collected=tuition_collected, grants_total=grants_total,
        donations_total=donations_total, other_income=other_income,
        utilities_total=utilities_total, suppliers_total=suppliers_total,
        rent_total=rent_total, other_expenses=other_expenses,
        expenses_only=expenses_only, payroll_total=payroll_total,
        pending_expenses=pending_expenses, paid_expenses=paid_expenses,
        payroll_count=payroll_count, pending_payroll=pending_payroll,
        pending_payroll_amount=pending_payroll_amount,
        fully_paid=fully_paid, with_balance=with_balance,
        total_students=total_students,
        cash_balance=cash_balance, bank_balance=bank_balance,
        mpesa_balance=mpesa_balance, inventory_value=inventory_value,
        income_transactions=income_transactions,
        expense_list=expense_list, all_students=all_students,
    )


# ═══════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════

@app.route('/settings')
def settings():
    if session.get('role') not in ['admin', 'finance', 'front_office']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    staff_count   = Staff.query.count()
    student_count = Student.query.count()
    return render_template('settings.html',
        staff_count=staff_count, student_count=student_count)

@app.route('/settings/update-profile', methods=['POST'])
def update_profile():
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    staff = Staff.query.filter_by(staff_id=session.get('username')).first()
    if staff:
        new_email = request.form.get('email')
        existing  = Staff.query.filter(Staff.email == new_email, Staff.id != staff.id).first()
        if existing:
            flash('That email is already in use by another account.', 'error')
        else:
            staff.email = new_email
            session['email'] = new_email
            db.session.commit()
            flash('Profile updated successfully.', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/change-password', methods=['POST'])
def change_password():
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    staff = Staff.query.filter_by(staff_id=session.get('username')).first()
    current  = request.form.get('current_password')
    new_pw   = request.form.get('new_password')
    confirm  = request.form.get('confirm_password')
    if not staff or staff.password != current:
        flash('Current password is incorrect.', 'error')
    elif new_pw != confirm:
        flash('New passwords do not match.', 'error')
    elif len(new_pw) < 6:
        flash('Password must be at least 6 characters.', 'error')
    else:
        staff.password = new_pw
        db.session.commit()
        flash('Password changed successfully.', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/clear-transactions', methods=['POST'])
def clear_transactions():
    if session.get('role') != 'admin':
        flash('Only administrators can perform this action.', 'error')
        return redirect(url_for('settings'))
    Transaction.query.delete()
    db.session.commit()
    flash('All transaction records cleared.', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/clear-payments', methods=['POST'])
def clear_payments():
    if session.get('role') != 'admin':
        flash('Only administrators can perform this action.', 'error')
        return redirect(url_for('settings'))
    Payment.query.delete()
    db.session.commit()
    flash('All payment records cleared.', 'success')
    return redirect(url_for('settings'))

# ═══════════════════════════════════════════
# FINANCE DASHBOARD
# ═══════════════════════════════════════════

@app.route('/finance-dashboard')
def finance_dashboard():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('finance_dashboard.html')


# ═══════════════════════════════════════════
# FRONT OFFICE DASHBOARD
# ═══════════════════════════════════════════

@app.route('/front-office-dashboard')
def front_office_dashboard():
    if session.get('role') != 'front_office':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('staff_dashboard.html')


# ═══════════════════════════════════════════
# STUDENT DASHBOARD
# ═══════════════════════════════════════════

@app.route('/student-dashboard')
def student_dashboard():
    return render_template("student_dashboard.html")


# ═══════════════════════════════════════════
# LOGOUT
# ═══════════════════════════════════════════

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)