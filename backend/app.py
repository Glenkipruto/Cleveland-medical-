from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
import os

_base = os.path.dirname(os.path.abspath(__file__))

def eat_now():
    from datetime import datetime as dt, timedelta
    return dt.utcnow() + timedelta(hours=3)


app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cleveland-secret-key-2024')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///cleveland.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.context_processor
def inject_unread():
    if session.get('username'):
        unread = Message.query.filter_by(
            receiver_id=session.get('username'),
            is_read=False
        ).count()
        return {'unread_messages': unread}
    return {'unread_messages': 0}


# ═══════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════

class Staff(db.Model):
    __tablename__ = 'staff'
    id             = db.Column(db.Integer,     primary_key=True)
    staff_id       = db.Column(db.String(50),  unique=True)
    email          = db.Column(db.String(100), unique=True)
    password       = db.Column(db.String(200))
    role           = db.Column(db.String(50))
    full_name      = db.Column(db.String(200), nullable=True)
    department     = db.Column(db.String(100), nullable=True)
    job_title      = db.Column(db.String(100), nullable=True)
    phone          = db.Column(db.String(20),  nullable=True)
    specialization = db.Column(db.String(200), nullable=True)
    courses_taught = db.Column(db.Text,        nullable=True)

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

class Course(db.Model):
    __tablename__ = 'courses'
    id          = db.Column(db.Integer,     primary_key=True)
    code        = db.Column(db.String(50),  nullable=False, unique=True)
    name        = db.Column(db.String(200), nullable=False)
    department  = db.Column(db.String(100), nullable=False)
    duration    = db.Column(db.String(20),  nullable=False)
    tuition_fee = db.Column(db.Float,       default=0)
    capacity    = db.Column(db.Integer,     default=50)
    intake_year = db.Column(db.Integer,     default=2026)
    description = db.Column(db.Text,        nullable=True)
    status      = db.Column(db.String(20),  default='Active')

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id        = db.Column(db.Integer,     primary_key=True)
    title     = db.Column(db.String(200), nullable=False)
    message   = db.Column(db.Text,        nullable=False)
    audience  = db.Column(db.String(20),  default='All')
    priority  = db.Column(db.String(20),  default='Normal')
    date      = db.Column(db.String(20),  nullable=False)
    posted_by = db.Column(db.String(100), nullable=False)

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id         = db.Column(db.Integer,     primary_key=True)
    program    = db.Column(db.String(100), nullable=False)
    subject    = db.Column(db.String(100), nullable=False)
    lecturer   = db.Column(db.String(100), nullable=False)
    day        = db.Column(db.String(20),  nullable=False)
    start_time = db.Column(db.String(10),  nullable=False)
    end_time   = db.Column(db.String(10),  nullable=False)
    room       = db.Column(db.String(50),  nullable=False)
    year       = db.Column(db.String(20),  default='Year 1')
    semester   = db.Column(db.String(20),  default='Semester 1')

class Examination(db.Model):
    __tablename__ = 'examinations'
    id          = db.Column(db.Integer,     primary_key=True)
    program     = db.Column(db.String(100), nullable=False)
    subject     = db.Column(db.String(100), nullable=False)
    exam_type   = db.Column(db.String(20),  nullable=False)
    exam_date   = db.Column(db.String(20),  nullable=False)
    start_time  = db.Column(db.String(10),  nullable=False)
    end_time    = db.Column(db.String(10),  nullable=False)
    venue       = db.Column(db.String(100), nullable=False)
    year        = db.Column(db.String(20),  default='Year 1')
    invigilator = db.Column(db.String(100), nullable=True)
    total_marks = db.Column(db.Integer,     default=100)
    semester    = db.Column(db.String(20),  default='Semester 1')
    status      = db.Column(db.String(20),  default='Scheduled')

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id           = db.Column(db.Integer,     primary_key=True)
    student_id   = db.Column(db.String(50),  nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    amount       = db.Column(db.Float,       nullable=False)
    method       = db.Column(db.String(30),  nullable=False)
    status       = db.Column(db.String(20),  default='Paid')
    date         = db.Column(db.DateTime,    default=eat_now)

class FinanceExpense(db.Model):
    __tablename__ = 'finance_expenses'
    id          = db.Column(db.Integer,     primary_key=True)
    department  = db.Column(db.String(50),  nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    amount      = db.Column(db.Float,       nullable=False)
    description = db.Column(db.String(200), nullable=True)
    status      = db.Column(db.String(20),  default='Approved')
    date        = db.Column(db.DateTime,    default=eat_now)

class Receivable(db.Model):
    __tablename__ = 'receivables'
    id           = db.Column(db.Integer,     primary_key=True)
    debtor_name  = db.Column(db.String(100), nullable=False)
    reference    = db.Column(db.String(50),  nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    amount       = db.Column(db.Float,       nullable=False)
    due_date     = db.Column(db.Date,        nullable=False)
    status       = db.Column(db.String(20),  default='Outstanding')
    date_created = db.Column(db.DateTime,    default=eat_now)

class Payable(db.Model):
    __tablename__ = 'payables'
    id           = db.Column(db.Integer,     primary_key=True)
    vendor_name  = db.Column(db.String(100), nullable=False)
    reference    = db.Column(db.String(50),  nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    amount       = db.Column(db.Float,       nullable=False)
    due_date     = db.Column(db.Date,        nullable=False)
    notes        = db.Column(db.String(200), nullable=True)
    status       = db.Column(db.String(20),  default='Pending')
    date_created = db.Column(db.DateTime,    default=eat_now)

class CashBank(db.Model):
    __tablename__ = 'cash_bank'
    id               = db.Column(db.Integer,     primary_key=True)
    transaction_type = db.Column(db.String(20),  nullable=False)
    account          = db.Column(db.String(50),  nullable=False)
    description      = db.Column(db.String(200), nullable=False)
    amount           = db.Column(db.Float,       nullable=False)
    reference        = db.Column(db.String(50),  nullable=True)
    date             = db.Column(db.Date,        nullable=False)
    date_created     = db.Column(db.DateTime,    default=eat_now)

class GrantDonation(db.Model):
    __tablename__ = 'grants_donations'
    id            = db.Column(db.Integer,     primary_key=True)
    donor_name    = db.Column(db.String(100), nullable=False)
    type          = db.Column(db.String(50),  nullable=False)
    purpose       = db.Column(db.String(200), nullable=False)
    amount        = db.Column(db.Float,       nullable=False)
    date_received = db.Column(db.Date,        nullable=False)
    notes         = db.Column(db.String(200), nullable=True)
    status        = db.Column(db.String(20),  default='Received')
    date_created  = db.Column(db.DateTime,    default=eat_now)

class FinancePayroll(db.Model):
    __tablename__ = 'finance_payroll'
    id           = db.Column(db.Integer,     primary_key=True)
    staff_id     = db.Column(db.String(30),  nullable=False)
    name         = db.Column(db.String(100), nullable=False)
    department   = db.Column(db.String(50),  nullable=False)
    role         = db.Column(db.String(50),  nullable=False)
    basic_salary = db.Column(db.Float,       nullable=False)
    allowances   = db.Column(db.Float,       default=0)
    status       = db.Column(db.String(20),  default='Pending')
    date_created = db.Column(db.DateTime,    default=eat_now)

class FinanceInventory(db.Model):
    __tablename__ = 'finance_inventory'
    id           = db.Column(db.Integer,     primary_key=True)
    item_name    = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    department   = db.Column(db.String(50),  nullable=False)
    quantity     = db.Column(db.Integer,     nullable=False)
    unit_price   = db.Column(db.Float,       nullable=False)
    min_stock    = db.Column(db.Integer,     default=5)
    condition    = db.Column(db.String(20),  default='Good')
    date_created = db.Column(db.DateTime,    default=eat_now)

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

class AdminPayroll(db.Model):
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

class AdminInventory(db.Model):
    __tablename__ = 'admin_inventory'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100))
    category      = db.Column(db.String(50), default='Other')
    unit          = db.Column(db.String(20), default='pcs')
    quantity      = db.Column(db.Integer, default=0)
    unit_price    = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Integer, default=10)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.String(20))
    description = db.Column(db.String(200))
    type        = db.Column(db.String(50))
    amount      = db.Column(db.Float, default=0)
    status      = db.Column(db.String(20))

class StaffNotice(db.Model):
    __tablename__ = 'staff_notices'
    id          = db.Column(db.Integer,     primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    message     = db.Column(db.Text,        nullable=False)
    notice_type = db.Column(db.String(50),  nullable=False)
    course      = db.Column(db.String(100), nullable=True)
    posted_by   = db.Column(db.String(100), nullable=False)
    date        = db.Column(db.String(20),  nullable=False)
    audience    = db.Column(db.String(20),  default='Students')

class Message(db.Model):
    __tablename__ = 'messages'
    id          = db.Column(db.Integer,     primary_key=True)
    sender_id   = db.Column(db.String(100), nullable=False)
    sender_name = db.Column(db.String(200), nullable=False)
    receiver_id = db.Column(db.String(100), nullable=False)
    subject     = db.Column(db.String(200), nullable=False)
    body        = db.Column(db.Text,        nullable=False)
    is_read     = db.Column(db.Boolean,     default=False)
    date_sent   = db.Column(db.DateTime,    default=eat_now)
    reply_to    = db.Column(db.Integer,     db.ForeignKey('messages.id'), nullable=True)

# ── RECEPTIONIST MODELS ──
class VisitorLog(db.Model):
    __tablename__ = 'visitor_log'
    id           = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(100), nullable=False)
    phone        = db.Column(db.String(20), nullable=True)
    purpose      = db.Column(db.String(200), nullable=False)
    host         = db.Column(db.String(100), nullable=False)
    id_number    = db.Column(db.String(50), nullable=True)
    time_in      = db.Column(db.String(20), nullable=False)
    time_out     = db.Column(db.String(20), nullable=True)
    date         = db.Column(db.String(20), nullable=False)
    recorded_by  = db.Column(db.String(100), nullable=False)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    attendee   = db.Column(db.String(100), nullable=False)
    appt_date  = db.Column(db.String(20), nullable=False)
    appt_time  = db.Column(db.String(10), nullable=False)
    location   = db.Column(db.String(100), nullable=True)
    notes      = db.Column(db.Text, nullable=True)
    status     = db.Column(db.String(20), default='Confirmed')
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=eat_now)

class DocumentRequest(db.Model):
    __tablename__ = 'document_requests'
    id             = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    doc_type       = db.Column(db.String(100), nullable=False)
    student_id     = db.Column(db.String(50), nullable=True)
    notes          = db.Column(db.Text, nullable=True)
    status         = db.Column(db.String(20), default='Pending')
    date_requested = db.Column(db.String(20), nullable=False)
    processed_by   = db.Column(db.String(100), nullable=True)
    created_at     = db.Column(db.DateTime, default=eat_now)

class MailPackage(db.Model):
    __tablename__ = 'mail_packages'
    id            = db.Column(db.Integer, primary_key=True)
    mail_type     = db.Column(db.String(20), nullable=False)
    party_name    = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.String(200), nullable=False)
    notes         = db.Column(db.Text, nullable=True)
    status        = db.Column(db.String(20), default='Pending')
    date_recorded = db.Column(db.String(20), nullable=False)
    recorded_by   = db.Column(db.String(100), nullable=False)
    created_at    = db.Column(db.DateTime, default=eat_now)

class OfficeSupply(db.Model):
    __tablename__ = 'office_supplies'
    id         = db.Column(db.Integer, primary_key=True)
    item_name  = db.Column(db.String(100), nullable=False)
    category   = db.Column(db.String(50), default='Stationery')
    quantity   = db.Column(db.Integer, default=0)
    unit       = db.Column(db.String(20), default='pcs')
    min_stock  = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=eat_now)


# ═══════════════════════════════════════════
# CREATE TABLES + SETUP
# ═══════════════════════════════════════════

with app.app_context():
    db.create_all()

    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        with db.engine.connect() as conn:
            for col, coltype in [
                ('full_name',      'VARCHAR(200)'),
                ('department',     'VARCHAR(100)'),
                ('job_title',      'VARCHAR(100)'),
                ('phone',          'VARCHAR(20)'),
                ('specialization', 'VARCHAR(200)'),
                ('courses_taught', 'TEXT'),
            ]:
                try:
                    conn.execute(db.text(f'ALTER TABLE staff ADD COLUMN {col} {coltype}'))
                    conn.commit()
                    print(f'✅ Added column: {col}')
                except:
                    print(f'⏭️ Skipped {col}: already exists')

    try:
        existing_admin = Staff.query.filter_by(staff_id='CMC-ADMIN-01').first()
        if not existing_admin:
            db.session.add(Staff(
                staff_id='CMC-ADMIN-01',
                email='admin@cmc.edu',
                password='password123',
                role='admin'
            ))
            db.session.commit()
            print('✅ Default admin created: CMC-ADMIN-01 / password123')
    except:
        pass


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
            session['role']       = staff.role
            session['username']   = staff.staff_id
            session['email']      = staff.email
            session['full_name']  = staff.full_name  or staff.staff_id
            session['job_title']  = staff.job_title  or 'Staff'
            session['department'] = staff.department or 'CMC'
            if staff.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif staff.role == 'finance':
                return redirect(url_for('finance_dashboard'))
            elif staff.role == 'front_office':
                return redirect(url_for('front_office_dashboard'))
            elif staff.role == 'receptionist':
                return redirect(url_for('receptionist_dashboard'))
        else:
            flash('Invalid credentials or role mismatch. Please try again.')
    return render_template("staff_login.html")


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
    return render_template('admin_dashboard.html',
        total_students      = Student.query.count(),
        staff_count         = Staff.query.count(),
        students_owing      = Student.query.filter(Student.balance > 0).count(),
        total_courses       = Course.query.count(),
        total_announcements = Announcement.query.count(),
        upcoming_exams      = Examination.query.filter_by(status='Scheduled').count(),
        recent_students     = Student.query.order_by(Student.id.desc()).limit(5).all(),
        latest_announcements= Announcement.query.order_by(Announcement.id.desc()).limit(3).all())


# ═══════════════════════════════════════════
# STAFF MANAGEMENT
# ═══════════════════════════════════════════

@app.route('/manage-staff')
def manage_staff():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('manage_staff.html',
        staff_list  = Staff.query.order_by(Staff.id).all(),
        all_courses = Course.query.filter_by(status='Active').order_by(Course.name).all())

@app.route('/manage-staff/add', methods=['POST'])
def add_staff():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    staff_id = request.form.get('staff_id')
    email    = request.form.get('email')
    if Staff.query.filter((Staff.staff_id == staff_id) | (Staff.email == email)).first():
        flash('A staff member with that ID or email already exists.', 'error')
        return redirect(url_for('manage_staff'))
    db.session.add(Staff(
        staff_id       = staff_id, email=email,
        password       = request.form.get('password'),
        role           = request.form.get('role'),
        full_name      = request.form.get('full_name', ''),
        department     = request.form.get('department', ''),
        job_title      = request.form.get('job_title', ''),
        phone          = request.form.get('phone', ''),
        courses_taught = ', '.join(request.form.getlist('courses_taught'))
    ))
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
    if session.get('role') not in ['admin', 'front_office', 'receptionist']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('students.html', students=Student.query.order_by(Student.id.desc()).all())

@app.route('/students/add', methods=['POST'])
def add_student():
    if session.get('role') not in ['admin', 'front_office']:
        flash('Access denied.')
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
    if session.get('role') not in ['admin', 'front_office', 'receptionist']:
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
# ANNOUNCEMENTS
# ═══════════════════════════════════════════

@app.route('/announcements')
def announcements():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('announcements.html',
        announcements=Announcement.query.order_by(Announcement.id.desc()).all())

@app.route('/announcements/add', methods=['POST'])
def add_announcement():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    db.session.add(Announcement(
        title=request.form['title'], message=request.form['message'],
        audience=request.form['audience'], priority=request.form['priority'],
        date=request.form['date'], posted_by=request.form['posted_by']
    ))
    db.session.commit()
    flash('Announcement posted successfully!', 'success')
    return redirect(url_for('announcements'))

@app.route('/announcements/delete/<int:ann_id>', methods=['POST'])
def delete_announcement(ann_id):
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('announcements'))


# ═══════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════

@app.route('/courses')
def courses():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('courses.html', courses=Course.query.order_by(Course.id.desc()).all())

@app.route('/courses/add', methods=['POST'])
def add_course():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    db.session.add(Course(
        code=request.form['code'], name=request.form['name'],
        department=request.form['department'], duration=request.form['duration'],
        tuition_fee=float(request.form['tuition_fee']),
        capacity=int(request.form['capacity']),
        intake_year=int(request.form['intake_year']),
        description=request.form.get('description', ''),
        status=request.form['status']
    ))
    db.session.commit()
    flash('Course added successfully!', 'success')
    return redirect(url_for('courses'))

@app.route('/courses/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('courses'))


# ═══════════════════════════════════════════
# TIMETABLE
# ═══════════════════════════════════════════

@app.route('/timetable')
def timetable():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('timetable.html',
        timetable=Timetable.query.order_by(Timetable.day, Timetable.start_time).all(),
        courses=Course.query.filter_by(status='Active').all())

@app.route('/timetable/add', methods=['POST'])
def add_timetable():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    db.session.add(Timetable(
        program=request.form['program'], subject=request.form['subject'],
        lecturer=request.form['lecturer'], day=request.form['day'],
        start_time=request.form['start_time'], end_time=request.form['end_time'],
        room=request.form['room'], year=request.form['year'],
        semester=request.form['semester']
    ))
    db.session.commit()
    flash('Schedule added successfully!', 'success')
    return redirect(url_for('timetable'))

@app.route('/timetable/delete/<int:tt_id>', methods=['POST'])
def delete_timetable(tt_id):
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    tt = Timetable.query.get_or_404(tt_id)
    db.session.delete(tt)
    db.session.commit()
    flash('Schedule deleted.', 'success')
    return redirect(url_for('timetable'))


# ═══════════════════════════════════════════
# EXAMINATIONS
# ═══════════════════════════════════════════

@app.route('/examinations')
def examinations():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('examinations.html',
        exams=Examination.query.order_by(Examination.exam_date).all(),
        courses=Course.query.filter_by(status='Active').all(),
        total_exams=Examination.query.count(),
        scheduled=Examination.query.filter_by(status='Scheduled').count(),
        completed=Examination.query.filter_by(status='Completed').count(),
        postponed=Examination.query.filter_by(status='Postponed').count())

@app.route('/examinations/add', methods=['POST'])
def add_examination():
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    db.session.add(Examination(
        program=request.form['program'], subject=request.form['subject'],
        exam_type=request.form['exam_type'], exam_date=request.form['exam_date'],
        start_time=request.form['start_time'], end_time=request.form['end_time'],
        venue=request.form['venue'], year=request.form['year'],
        invigilator=request.form.get('invigilator', ''),
        total_marks=int(request.form.get('total_marks', 100)),
        semester=request.form['semester'], status=request.form['status']
    ))
    db.session.commit()
    flash('Exam scheduled successfully!', 'success')
    return redirect(url_for('examinations'))

@app.route('/examinations/delete/<int:exam_id>', methods=['POST'])
def delete_examination(exam_id):
    if session.get('role') != 'admin':
        return redirect(url_for('staff_login'))
    exam = Examination.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted.', 'success')
    return redirect(url_for('examinations'))


# ═══════════════════════════════════════════
# FINANCE OVERVIEW (Admin)
# ═══════════════════════════════════════════

@app.route('/finance-overview')
def finance_overview():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    from sqlalchemy import func
    tuition_collected   = db.session.query(func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    tuition_pending     = db.session.query(func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    grants_total        = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    donations_total     = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    payroll_list        = FinancePayroll.query.all()
    payroll_total       = sum(p.basic_salary + p.allowances for p in payroll_list)
    payroll_paid        = sum(p.basic_salary + p.allowances for p in payroll_list if p.status == 'Paid')
    payroll_pending     = sum(p.basic_salary + p.allowances for p in payroll_list if p.status == 'Pending')
    cash_deposits       = db.session.query(func.sum(CashBank.amount)).filter_by(transaction_type='Deposit').scalar() or 0
    cash_withdrawals    = db.session.query(func.sum(CashBank.amount)).filter_by(transaction_type='Withdrawal').scalar() or 0
    payable_paid        = db.session.query(func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    payable_pending     = db.session.query(func.sum(Payable.amount)).filter_by(status='Pending').scalar() or 0
    inventory_list      = FinanceInventory.query.all()
    inventory_value     = sum(i.quantity * i.unit_price for i in inventory_list)
    inventory_low_stock = sum(1 for i in inventory_list if i.quantity <= i.min_stock)
    total_income        = tuition_collected + grants_total + donations_total
    total_expenses      = payable_paid + payroll_total
    return render_template('finance_overview.html',
        total_income=total_income, total_expenses=total_expenses,
        net_balance=total_income - total_expenses, outstanding_fees=tuition_pending,
        tuition_collected=tuition_collected, tuition_pending=tuition_pending,
        tuition_overdue=0, tuition_records=FeePayment.query.count(),
        grants_total=grants_total, donations_total=donations_total,
        payroll_staff=FinancePayroll.query.count(), payroll_total=payroll_total,
        payroll_paid=payroll_paid, payroll_pending=payroll_pending,
        cash_deposits=cash_deposits, cash_withdrawals=cash_withdrawals,
        payable_paid=payable_paid, payable_pending=payable_pending,
        payable_overdue=0, payable_records=Payable.query.count(),
        inventory_items=FinanceInventory.query.count(),
        inventory_value=inventory_value, inventory_low_stock=inventory_low_stock)


# ═══════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════

@app.route('/reports')
def reports():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    from sqlalchemy import func
    tuition_collected  = db.session.query(func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    grants_total       = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    donations_total    = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    total_income       = tuition_collected + grants_total + donations_total
    total_expenses     = db.session.query(func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    return render_template('reports.html',
        total_students=Student.query.count(),
        active_students=Student.query.filter_by(status='Active').count(),
        deferred_students=Student.query.filter_by(status='Deferred').count(),
        graduated_students=Student.query.filter_by(status='Graduated').count(),
        suspended_students=Student.query.filter_by(status='Suspended').count(),
        programs=db.session.query(Student.program, func.count(Student.id)).group_by(Student.program).all(),
        total_staff=Staff.query.count(),
        admin_count=Staff.query.filter_by(role='admin').count(),
        finance_count=Staff.query.filter_by(role='finance').count(),
        frontoffice_count=Staff.query.filter_by(role='front_office').count(),
        total_courses=Course.query.count(),
        active_courses=Course.query.filter_by(status='Active').count(),
        total_exams=Examination.query.count(),
        scheduled_exams=Examination.query.filter_by(status='Scheduled').count(),
        completed_exams=Examination.query.filter_by(status='Completed').count(),
        postponed_exams=Examination.query.filter_by(status='Postponed').count(),
        total_announcements=Announcement.query.count(),
        tuition_collected=tuition_collected,
        total_outstanding=db.session.query(func.sum(Student.balance)).filter(Student.balance > 0).scalar() or 0,
        total_income=total_income, total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
        recent_students=Student.query.order_by(Student.id.desc()).limit(10).all())


# ═══════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════

@app.route('/settings')
def settings():
    if session.get('role') not in ['admin', 'finance', 'front_office']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('settings.html',
        staff_count=Staff.query.count(), student_count=Student.query.count())

@app.route('/settings/update-profile', methods=['POST'])
def update_profile():
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    staff = Staff.query.filter_by(staff_id=session.get('username')).first()
    if staff:
        new_email = request.form.get('email')
        if Staff.query.filter(Staff.email == new_email, Staff.id != staff.id).first():
            flash('That email is already in use.', 'error')
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
    staff   = Staff.query.filter_by(staff_id=session.get('username')).first()
    current = request.form.get('current_password')
    new_pw  = request.form.get('new_password')
    confirm = request.form.get('confirm_password')
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
    # Redirect to correct settings page based on role
    if session.get('role') == 'receptionist':
        return redirect(url_for('receptionist_settings'))
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
# FINANCE DASHBOARD + ROUTES
# ═══════════════════════════════════════════

@app.route('/finance')
def finance_dashboard():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    total_income   = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    total_expenses = db.session.query(db.func.sum(FinanceExpense.amount)).scalar() or 0
    pending_fees   = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    recent_fees    = FeePayment.query.order_by(FeePayment.date.desc()).limit(5).all()
    return render_template('finance/dashboard.html',
        total_income=total_income, total_expenses=total_expenses,
        pending_fees=pending_fees, net_balance=total_income - total_expenses,
        recent_fees=recent_fees)

@app.route('/api/chart-data')
def chart_data():
    from sqlalchemy import extract
    import calendar
    months_data, income_data, expense_data = [], [], []
    for m in range(1, 7):
        months_data.append(calendar.month_abbr[m])
        tuition = db.session.query(db.func.sum(FeePayment.amount)).filter(
            FeePayment.status=='Paid', extract('month', FeePayment.date)==m,
            extract('year', FeePayment.date)==2026).scalar() or 0
        grants = db.session.query(db.func.sum(GrantDonation.amount)).filter(
            GrantDonation.status=='Received',
            extract('month', GrantDonation.date_received)==m,
            extract('year', GrantDonation.date_received)==2026).scalar() or 0
        income_data.append(tuition + grants)
        expenses = db.session.query(db.func.sum(Payable.amount)).filter(
            Payable.status=='Paid', extract('month', Payable.date_created)==m,
            extract('year', Payable.date_created)==2026).scalar() or 0
        expense_data.append(expenses)
    return jsonify({'months': months_data, 'income': income_data, 'expenses': expense_data})

@app.route('/finance/tuition')
def tuition():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payments        = FeePayment.query.order_by(FeePayment.date.desc()).all()
    total_collected = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    total_pending   = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    total_overdue   = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Overdue').scalar() or 0
    return render_template('finance/tuition.html',
        payments=payments, total_collected=total_collected,
        total_pending=total_pending, total_overdue=total_overdue,
        total_records=FeePayment.query.count())

@app.route('/finance/tuition/add', methods=['POST'])
def add_tuition():
    if session.get('role') not in ['finance', 'admin', 'front_office']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(FeePayment(
        student_id   = request.form['student_id'],
        student_name = request.form['student_name'],
        category     = request.form['category'],
        amount       = float(request.form['amount']),
        method       = request.form['method'],
        status       = request.form.get('status', 'Paid')
    ))
    db.session.commit()
    flash('Payment recorded successfully!', 'success')
    referrer = request.referrer or ''
    if 'students' in referrer:
        return redirect(referrer)
    return redirect(url_for('tuition'))

@app.route('/finance/tuition/delete/<int:fee_id>', methods=['POST'])
def delete_tuition(fee_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    fee = FeePayment.query.get_or_404(fee_id)
    db.session.delete(fee)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('tuition'))

@app.route('/finance/accounts-receivable')
def accounts_receivable():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    receivables = Receivable.query.order_by(Receivable.date_created.desc()).all()
    return render_template('finance/accounts_receivable.html',
        receivables=receivables,
        total_received=db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Received').scalar() or 0,
        total_outstanding=db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Outstanding').scalar() or 0,
        total_overdue=db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Overdue').scalar() or 0,
        total_records=Receivable.query.count())

@app.route('/finance/accounts-receivable/add', methods=['POST'])
def add_receivable():
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    db.session.add(Receivable(
        debtor_name=request.form['debtor_name'], reference=request.form['reference'],
        category=request.form['category'], amount=float(request.form['amount']),
        due_date=date.fromisoformat(request.form['due_date']), status=request.form['status']
    ))
    db.session.commit()
    flash('Invoice added successfully!', 'success')
    return redirect(url_for('accounts_receivable'))

@app.route('/finance/accounts-receivable/delete/<int:item_id>', methods=['POST'])
def delete_receivable(item_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    item = Receivable.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('accounts_receivable'))

@app.route('/finance/accounts-payable')
def accounts_payable():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payables = Payable.query.order_by(Payable.date_created.desc()).all()
    return render_template('finance/accounts_payable.html',
        payables=payables,
        total_paid=db.session.query(db.func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0,
        total_pending=db.session.query(db.func.sum(Payable.amount)).filter_by(status='Pending').scalar() or 0,
        total_overdue=db.session.query(db.func.sum(Payable.amount)).filter_by(status='Overdue').scalar() or 0,
        total_records=Payable.query.count())

@app.route('/finance/accounts-payable/add', methods=['POST'])
def add_payable():
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    db.session.add(Payable(
        vendor_name=request.form['vendor_name'], reference=request.form['reference'],
        category=request.form['category'], amount=float(request.form['amount']),
        due_date=date.fromisoformat(request.form['due_date']),
        notes=request.form.get('notes', ''), status=request.form['status']
    ))
    db.session.commit()
    flash('Bill added successfully!', 'success')
    return redirect(url_for('accounts_payable'))

@app.route('/finance/accounts-payable/delete/<int:item_id>', methods=['POST'])
def delete_payable(item_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    item = Payable.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Bill deleted.', 'success')
    return redirect(url_for('accounts_payable'))

@app.route('/finance/cash-bank')
def cash_bank():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    transactions   = CashBank.query.order_by(CashBank.date.desc()).all()
    total_deposits = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Deposit').scalar() or 0
    total_wds      = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Withdrawal').scalar() or 0
    cash_on_hand   = db.session.query(db.func.sum(CashBank.amount)).filter_by(account='Cash', transaction_type='Deposit').scalar() or 0
    return render_template('finance/cash_bank.html',
        transactions=transactions, total_deposits=total_deposits,
        total_withdrawals=total_wds, cash_on_hand=cash_on_hand,
        bank_balance=total_deposits - total_wds)

@app.route('/finance/cash-bank/add', methods=['POST'])
def add_cash_bank():
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    db.session.add(CashBank(
        transaction_type=request.form['transaction_type'],
        account=request.form['account'], description=request.form['description'],
        amount=float(request.form['amount']),
        reference=request.form.get('reference', ''),
        date=date.fromisoformat(request.form['date'])
    ))
    db.session.commit()
    flash('Transaction recorded successfully!', 'success')
    return redirect(url_for('cash_bank'))

@app.route('/finance/cash-bank/delete/<int:item_id>', methods=['POST'])
def delete_cash_bank(item_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    item = CashBank.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Transaction deleted.', 'success')
    return redirect(url_for('cash_bank'))

@app.route('/finance/grants-donations')
def grants_donations():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    records = GrantDonation.query.order_by(GrantDonation.date_created.desc()).all()
    return render_template('finance/grants_donations.html',
        records=records,
        total_grants=db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0,
        total_donations=db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0,
        total_pending=db.session.query(db.func.sum(GrantDonation.amount)).filter_by(status='Pending').scalar() or 0,
        total_records=GrantDonation.query.count())

@app.route('/finance/grants-donations/add', methods=['POST'])
def add_grant_donation():
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    db.session.add(GrantDonation(
        donor_name=request.form['donor_name'], type=request.form['type'],
        purpose=request.form['purpose'], amount=float(request.form['amount']),
        date_received=date.fromisoformat(request.form['date_received']),
        notes=request.form.get('notes', ''), status=request.form['status']
    ))
    db.session.commit()
    flash('Record added successfully!', 'success')
    return redirect(url_for('grants_donations'))

@app.route('/finance/grants-donations/delete/<int:item_id>', methods=['POST'])
def delete_grant_donation(item_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    item = GrantDonation.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('grants_donations'))

@app.route('/finance/payroll')
def payroll():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payroll_list = FinancePayroll.query.order_by(FinancePayroll.date_created.desc()).all()
    return render_template('finance/payroll.html',
        payroll=payroll_list,
        total_net_pay=sum(s.basic_salary + s.allowances for s in payroll_list),
        total_paid=sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Paid'),
        total_pending=sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Pending'),
        total_staff=FinancePayroll.query.count())

@app.route('/finance/payroll/add', methods=['POST'])
def add_payroll():
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    db.session.add(FinancePayroll(
        staff_id=request.form['staff_id'], name=request.form['name'],
        department=request.form['department'], role=request.form['role'],
        basic_salary=float(request.form['basic_salary']),
        allowances=float(request.form.get('allowances', 0)),
        status=request.form['status']
    ))
    db.session.commit()
    flash('Staff added to payroll successfully!', 'success')
    return redirect(url_for('payroll'))

@app.route('/finance/payroll/delete/<int:staff_id>', methods=['POST'])
def delete_payroll(staff_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    staff = FinancePayroll.query.get_or_404(staff_id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff removed from payroll.', 'success')
    return redirect(url_for('payroll'))

@app.route('/finance/inventory')
def inventory():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    items = FinanceInventory.query.order_by(FinanceInventory.date_created.desc()).all()
    return render_template('finance/inventory.html',
        items=items, total_items=FinanceInventory.query.count(),
        total_value=sum(i.quantity * i.unit_price for i in items),
        low_stock=sum(1 for i in items if i.quantity <= i.min_stock),
        total_categories=db.session.query(FinanceInventory.category).distinct().count())

@app.route('/finance/inventory/add', methods=['POST'])
def add_inventory():
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    db.session.add(FinanceInventory(
        item_name=request.form['item_name'], category=request.form['category'],
        department=request.form['department'], quantity=int(request.form['quantity']),
        unit_price=float(request.form['unit_price']),
        min_stock=int(request.form.get('min_stock', 5)),
        condition=request.form['condition']
    ))
    db.session.commit()
    flash('Item added successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/finance/inventory/delete/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    if session.get('role') != 'finance':
        return redirect(url_for('staff_login'))
    item = FinanceInventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'success')
    return redirect(url_for('inventory'))

@app.route('/finance/reports')
def finance_reports():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    tuition_collected      = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    tuition_pending        = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    tuition_overdue        = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Overdue').scalar() or 0
    receivable_received    = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Received').scalar() or 0
    receivable_outstanding = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Outstanding').scalar() or 0
    receivable_overdue     = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Overdue').scalar() or 0
    payable_paid           = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    payable_pending        = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Pending').scalar() or 0
    payable_overdue        = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Overdue').scalar() or 0
    cash_deposits          = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Deposit').scalar() or 0
    cash_withdrawals       = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Withdrawal').scalar() or 0
    grants_total           = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    donations_total        = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    payroll_list           = FinancePayroll.query.all()
    payroll_total          = sum(s.basic_salary + s.allowances for s in payroll_list)
    payroll_paid           = sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Paid')
    payroll_pending        = sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Pending')
    inventory_list         = FinanceInventory.query.all()
    inventory_value        = sum(i.quantity * i.unit_price for i in inventory_list)
    total_income           = tuition_collected + grants_total + donations_total + receivable_received
    total_expenses         = payable_paid + payroll_total
    return render_template('finance/reports.html',
        total_income=total_income, total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
        total_outstanding=receivable_outstanding + tuition_pending,
        tuition_collected=tuition_collected, tuition_pending=tuition_pending,
        tuition_overdue=tuition_overdue, tuition_records=FeePayment.query.count(),
        receivable_received=receivable_received,
        receivable_outstanding=receivable_outstanding,
        receivable_overdue=receivable_overdue, receivable_records=Receivable.query.count(),
        payable_paid=payable_paid, payable_pending=payable_pending,
        payable_overdue=payable_overdue, payable_records=Payable.query.count(),
        cash_deposits=cash_deposits, cash_withdrawals=cash_withdrawals,
        grants_total=grants_total, donations_total=donations_total,
        payroll_staff=FinancePayroll.query.count(), payroll_total=payroll_total,
        payroll_paid=payroll_paid, payroll_pending=payroll_pending,
        inventory_items=FinanceInventory.query.count(),
        inventory_value=inventory_value,
        inventory_low_stock=sum(1 for i in inventory_list if i.quantity <= i.min_stock))


# ═══════════════════════════════════════════
# LECTURER (front_office) DASHBOARD
# ═══════════════════════════════════════════

import calendar as cal

def get_staff():
    return Staff.query.filter_by(staff_id=session.get('username')).first()

@app.route('/front-office-dashboard')
def front_office_dashboard():
    if session.get('role') != 'front_office':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    staff        = get_staff()
    course_names = [c.strip() for c in (staff.courses_taught or '').split(',') if c.strip()]
    my_courses   = Course.query.filter(Course.name.in_(course_names)).all() if course_names else []
    today_name   = cal.day_name[date.today().weekday()]
    today_classes = Timetable.query.filter_by(
        lecturer=staff.full_name or staff.staff_id, day=today_name).all()
    my_exams = Examination.query.filter_by(
        invigilator=staff.full_name or staff.staff_id, status='Scheduled').all()
    announcements = Announcement.query.filter(
        Announcement.audience.in_(['All', 'Staff'])
    ).order_by(Announcement.id.desc()).limit(5).all()
    return render_template('staff/dashboard.html',
        staff=staff, my_courses=my_courses,
        today_classes=today_classes, my_exams=my_exams,
        announcements=announcements)

@app.route('/staff/my-courses')
def staff_my_courses():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    staff        = get_staff()
    course_names = [c.strip() for c in (staff.courses_taught or '').split(',') if c.strip()]
    return render_template('staff/courses.html',
        my_courses=Course.query.filter(Course.name.in_(course_names)).all() if course_names else [],
        staff=staff)

@app.route('/staff/timetable')
def staff_timetable():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    staff = get_staff()
    return render_template('staff/timetable.html',
        timetable=Timetable.query.filter_by(
            lecturer=staff.full_name or staff.staff_id
        ).order_by(Timetable.day, Timetable.start_time).all(),
        staff=staff)

@app.route('/staff/exams')
def staff_exams():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    staff = get_staff()
    return render_template('staff/exams.html',
        my_exams=Examination.query.filter_by(
            invigilator=staff.full_name or staff.staff_id
        ).order_by(Examination.exam_date).all(),
        staff=staff)

@app.route('/staff/announcements')
def staff_announcements():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    return render_template('staff/announcements.html',
        announcements=Announcement.query.filter(
            Announcement.audience.in_(['All', 'Staff'])
        ).order_by(Announcement.id.desc()).all())

@app.route('/staff/notices')
def staff_notices():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    staff = get_staff()
    return render_template('staff/notices.html',
        notices=StaffNotice.query.filter_by(posted_by=staff.staff_id).order_by(StaffNotice.id.desc()).all(),
        staff=staff)

@app.route('/staff/notices/add', methods=['POST'])
def add_staff_notice():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    staff = get_staff()
    db.session.add(StaffNotice(
        title=request.form['title'], message=request.form['message'],
        notice_type=request.form['notice_type'],
        course=request.form.get('course', ''),
        posted_by=staff.staff_id, date=request.form['date'],
        audience=request.form.get('audience', 'Students')
    ))
    db.session.commit()
    flash('Notice posted successfully!', 'success')
    return redirect(url_for('staff_notices'))

@app.route('/staff/notices/delete/<int:notice_id>', methods=['POST'])
def delete_staff_notice(notice_id):
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    notice = StaffNotice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted.', 'success')
    return redirect(url_for('staff_notices'))

@app.route('/staff/profile')
def staff_profile():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    return render_template('staff/profile.html', staff=get_staff())

@app.route('/staff/profile/update', methods=['POST'])
def update_staff_profile():
    if session.get('role') != 'front_office':
        return redirect(url_for('staff_login'))
    staff = get_staff()
    if staff:
        staff.full_name = request.form.get('full_name', '')
        staff.phone     = request.form.get('phone', '')
        new_email       = request.form.get('email', '')
        if Staff.query.filter(Staff.email == new_email, Staff.id != staff.id).first():
            flash('That email is already in use.', 'error')
        else:
            staff.email = new_email
            session['full_name'] = staff.full_name or staff.staff_id
            db.session.commit()
            flash('Profile updated successfully!', 'success')
    return redirect(url_for('staff_profile'))


# ═══════════════════════════════════════════
# RECEPTIONIST DASHBOARD + ROUTES
# ═══════════════════════════════════════════

@app.route('/receptionist-dashboard')
def receptionist_dashboard():
    if session.get('role') != 'receptionist':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    staff = get_staff()
    today_str = date.today().strftime('%Y-%m-%d')
    announcements = Announcement.query.filter(
        Announcement.audience.in_(['All', 'Staff'])
    ).order_by(Announcement.id.desc()).limit(5).all()
    return render_template('receptionist/dashboard.html',
        staff=staff,
        total_students=Student.query.count(),
        active_students=Student.query.filter_by(status='Active').count(),
        total_announcements=Announcement.query.count(),
        announcements=announcements,
        recent_students=Student.query.order_by(Student.id.desc()).limit(5).all(),
        today_visitors=VisitorLog.query.filter_by(date=today_str).count(),
        pending_documents=DocumentRequest.query.filter_by(status='Pending').count(),
        today_appointments=Appointment.query.filter_by(appt_date=today_str).count(),
        pending_mail=MailPackage.query.filter_by(status='Pending', mail_type='Incoming').count())

@app.route('/receptionist/students')
def receptionist_students():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    return render_template('receptionist/students.html',
        students=Student.query.order_by(Student.id.desc()).all())

@app.route('/receptionist/students/<int:student_id>')
def receptionist_student_profile(student_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    return render_template('receptionist/student_profile.html',
        student=Student.query.get_or_404(student_id))

@app.route('/receptionist/student-assistance')
def receptionist_student_assistance():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    return render_template('receptionist/student_assistance.html',
        courses=Course.query.filter_by(status='Active').order_by(Course.name).all())

@app.route('/receptionist/announcements')
def receptionist_announcements():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    return render_template('receptionist/announcements.html',
        announcements=Announcement.query.filter(
            Announcement.audience.in_(['All', 'Staff'])
        ).order_by(Announcement.id.desc()).all())

@app.route('/receptionist/settings')
def receptionist_settings():
    if session.get('role') != 'receptionist':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('receptionist/settings.html')

@app.route('/receptionist/profile')
def receptionist_profile():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    return render_template('receptionist/profile.html', staff=get_staff())

@app.route('/receptionist/profile/update', methods=['POST'])
def update_receptionist_profile():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    staff = get_staff()
    if staff:
        staff.full_name = request.form.get('full_name', '')
        staff.phone     = request.form.get('phone', '')
        new_email       = request.form.get('email', '')
        if Staff.query.filter(Staff.email == new_email, Staff.id != staff.id).first():
            flash('That email is already in use.', 'error')
        else:
            staff.email = new_email
            session['full_name'] = staff.full_name or staff.staff_id
            db.session.commit()
            flash('Profile updated successfully!', 'success')
    return redirect(url_for('receptionist_profile'))

# ── VISITOR LOG ──
@app.route('/receptionist/visitor-log')
def receptionist_visitor_log():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    today_str = date.today().strftime('%Y-%m-%d')
    visitors = VisitorLog.query.order_by(VisitorLog.id.desc()).all()
    return render_template('receptionist/visitor_log.html',
        visitors=visitors,
        today_count=VisitorLog.query.filter_by(date=today_str).count(),
        inside_count=VisitorLog.query.filter_by(date=today_str, time_out=None).count(),
        total_count=VisitorLog.query.count())

@app.route('/receptionist/visitor-log/add', methods=['POST'])
def receptionist_add_visitor():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    now = eat_now()
    db.session.add(VisitorLog(
        visitor_name=request.form['visitor_name'],
        phone=request.form.get('phone', ''),
        purpose=request.form['purpose'],
        host=request.form['host'],
        id_number=request.form.get('id_number', ''),
        time_in=now.strftime('%H:%M'),
        date=now.strftime('%Y-%m-%d'),
        recorded_by=session.get('username')
    ))
    db.session.commit()
    flash('Visitor signed in successfully!', 'success')
    return redirect(url_for('receptionist_visitor_log'))

@app.route('/receptionist/visitor-log/<int:visitor_id>/signout', methods=['POST'])
def receptionist_visitor_signout(visitor_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    visitor = VisitorLog.query.get_or_404(visitor_id)
    visitor.time_out = eat_now().strftime('%H:%M')
    db.session.commit()
    flash(f'{visitor.visitor_name} signed out.', 'success')
    return redirect(url_for('receptionist_visitor_log'))

# ── APPOINTMENTS ──
@app.route('/receptionist/appointments')
def receptionist_appointments():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    today_str = date.today().strftime('%Y-%m-%d')
    appointments = Appointment.query.order_by(Appointment.appt_date, Appointment.appt_time).all()
    return render_template('receptionist/appointments.html',
        appointments=appointments,
        today_count=Appointment.query.filter_by(appt_date=today_str).count(),
        upcoming_count=Appointment.query.filter(Appointment.appt_date >= today_str).count(),
        total_count=Appointment.query.count())

@app.route('/receptionist/appointments/add', methods=['POST'])
def receptionist_add_appointment():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    db.session.add(Appointment(
        title=request.form['title'],
        attendee=request.form['attendee'],
        appt_date=request.form['appt_date'],
        appt_time=request.form['appt_time'],
        location=request.form.get('location', ''),
        notes=request.form.get('notes', ''),
        status=request.form.get('status', 'Confirmed'),
        created_by=session.get('username')
    ))
    db.session.commit()
    flash('Appointment scheduled successfully!', 'success')
    return redirect(url_for('receptionist_appointments'))

@app.route('/receptionist/appointments/<int:appt_id>/delete', methods=['POST'])
def receptionist_delete_appointment(appt_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    appt = Appointment.query.get_or_404(appt_id)
    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted.', 'success')
    return redirect(url_for('receptionist_appointments'))

# ── DOCUMENT REQUESTS ──
@app.route('/receptionist/documents')
def receptionist_document_requests():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    requests = DocumentRequest.query.order_by(DocumentRequest.created_at.desc()).all()
    return render_template('receptionist/document_requests.html',
        requests=requests,
        pending_count=DocumentRequest.query.filter_by(status='Pending').count(),
        completed_count=DocumentRequest.query.filter_by(status='Completed').count(),
        total_count=DocumentRequest.query.count())

@app.route('/receptionist/documents/add', methods=['POST'])
def receptionist_add_document():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    db.session.add(DocumentRequest(
        requester_name=request.form['requester_name'],
        doc_type=request.form['doc_type'],
        student_id=request.form.get('student_id', ''),
        notes=request.form.get('notes', ''),
        date_requested=eat_now().strftime('%Y-%m-%d'),
        processed_by=session.get('username')
    ))
    db.session.commit()
    flash('Document request recorded!', 'success')
    return redirect(url_for('receptionist_document_requests'))

@app.route('/receptionist/documents/<int:doc_id>/complete', methods=['POST'])
def receptionist_complete_document(doc_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    doc = DocumentRequest.query.get_or_404(doc_id)
    doc.status = 'Completed'
    db.session.commit()
    flash('Document request marked as completed.', 'success')
    return redirect(url_for('receptionist_document_requests'))

@app.route('/receptionist/documents/<int:doc_id>/delete', methods=['POST'])
def receptionist_delete_document(doc_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    doc = DocumentRequest.query.get_or_404(doc_id)
    db.session.delete(doc)
    db.session.commit()
    flash('Request deleted.', 'success')
    return redirect(url_for('receptionist_document_requests'))

# ── MAIL & PACKAGES ──
@app.route('/receptionist/mail')
def receptionist_mail():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    mail_list = MailPackage.query.order_by(MailPackage.created_at.desc()).all()
    return render_template('receptionist/mail.html',
        mail_list=mail_list,
        incoming_count=MailPackage.query.filter_by(mail_type='Incoming').count(),
        outgoing_count=MailPackage.query.filter_by(mail_type='Outgoing').count(),
        pending_count=MailPackage.query.filter_by(status='Pending').count())

@app.route('/receptionist/mail/add', methods=['POST'])
def receptionist_add_mail():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    db.session.add(MailPackage(
        mail_type=request.form['mail_type'],
        party_name=request.form['party_name'],
        description=request.form['description'],
        notes=request.form.get('notes', ''),
        date_recorded=eat_now().strftime('%Y-%m-%d'),
        recorded_by=session.get('username')
    ))
    db.session.commit()
    flash('Mail recorded successfully!', 'success')
    return redirect(url_for('receptionist_mail'))

@app.route('/receptionist/mail/<int:mail_id>/collect', methods=['POST'])
def receptionist_collect_mail(mail_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    mail = MailPackage.query.get_or_404(mail_id)
    mail.status = 'Collected'
    db.session.commit()
    flash('Mail marked as collected.', 'success')
    return redirect(url_for('receptionist_mail'))

# ── OFFICE SUPPLIES ──
@app.route('/receptionist/supplies')
def receptionist_supplies():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    supplies = OfficeSupply.query.order_by(OfficeSupply.item_name).all()
    return render_template('receptionist/supplies.html',
        supplies=supplies,
        total_items=OfficeSupply.query.count(),
        low_stock=sum(1 for s in supplies if s.quantity <= s.min_stock))

@app.route('/receptionist/supplies/add', methods=['POST'])
def receptionist_add_supply():
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    db.session.add(OfficeSupply(
        item_name=request.form['item_name'],
        category=request.form.get('category', 'Stationery'),
        quantity=int(request.form.get('quantity', 0)),
        unit=request.form.get('unit', 'pcs'),
        min_stock=int(request.form.get('min_stock', 5))
    ))
    db.session.commit()
    flash('Supply item added!', 'success')
    return redirect(url_for('receptionist_supplies'))

@app.route('/receptionist/supplies/<int:supply_id>/restock', methods=['POST'])
def receptionist_restock_supply(supply_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    supply = OfficeSupply.query.get_or_404(supply_id)
    supply.quantity += int(request.form.get('quantity', 0))
    db.session.commit()
    flash(f'{supply.item_name} restocked successfully!', 'success')
    return redirect(url_for('receptionist_supplies'))

@app.route('/receptionist/supplies/<int:supply_id>/delete', methods=['POST'])
def receptionist_delete_supply(supply_id):
    if session.get('role') != 'receptionist':
        return redirect(url_for('staff_login'))
    supply = OfficeSupply.query.get_or_404(supply_id)
    db.session.delete(supply)
    db.session.commit()
    flash('Item deleted.', 'success')
    return redirect(url_for('receptionist_supplies'))


# ═══════════════════════════════════════════
# MESSAGES
# ═══════════════════════════════════════════

@app.route('/messages')
def messages():
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    username = session.get('username')
    role     = session.get('role')
    inbox    = Message.query.filter_by(receiver_id=username).order_by(Message.date_sent.desc()).all()
    sent     = Message.query.filter_by(sender_id=username).order_by(Message.date_sent.desc()).all()
    unread   = Message.query.filter_by(receiver_id=username, is_read=False).count()
    auto_to  = request.args.get('to', '')
    if role == 'admin':
        contacts = Staff.query.filter(
            Staff.role.in_(['finance', 'front_office', 'receptionist']),
            Staff.staff_id != username).all()
    elif role in ['finance', 'front_office', 'receptionist']:
        contacts = Staff.query.filter_by(role='admin').all()
    else:
        contacts = []
    auto_contact = None
    if auto_to == 'finance':
        auto_contact = Staff.query.filter_by(role='finance').first()
    return render_template('messages.html',
        inbox=inbox, sent=sent, unread=unread,
        contacts=contacts, auto_contact=auto_contact)

@app.route('/messages/send', methods=['POST'])
def send_message():
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    db.session.add(Message(
        sender_id   = session.get('username'),
        sender_name = session.get('full_name') or session.get('username'),
        receiver_id = request.form.get('receiver_id'),
        subject     = request.form.get('subject'),
        body        = request.form.get('body'),
        reply_to    = request.form.get('reply_to') or None
    ))
    db.session.commit()
    flash('Message sent successfully!', 'success')
    return redirect(url_for('messages'))

@app.route('/messages/read/<int:msg_id>')
def read_message(msg_id):
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    msg = Message.query.get_or_404(msg_id)
    if msg.receiver_id == session.get('username'):
        msg.is_read = True
        db.session.commit()
    return redirect(url_for('messages'))

@app.route('/messages/delete/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    msg = Message.query.get_or_404(msg_id)
    if msg.sender_id == session.get('username') or msg.receiver_id == session.get('username'):
        db.session.delete(msg)
        db.session.commit()
        flash('Message deleted.', 'success')
    return redirect(url_for('messages'))


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


# ═══════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))