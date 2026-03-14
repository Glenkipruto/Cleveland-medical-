from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

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

# ── FINANCE MODELS ──

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id           = db.Column(db.Integer,     primary_key=True)
    student_id   = db.Column(db.String(50),  nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    amount       = db.Column(db.Float,       nullable=False)
    method       = db.Column(db.String(30),  nullable=False)
    status       = db.Column(db.String(20),  default='Paid')
    date         = db.Column(db.DateTime,    default=datetime.utcnow)

class FinanceExpense(db.Model):
    __tablename__ = 'finance_expenses'
    id          = db.Column(db.Integer,     primary_key=True)
    department  = db.Column(db.String(50),  nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    amount      = db.Column(db.Float,       nullable=False)
    description = db.Column(db.String(200), nullable=True)
    status      = db.Column(db.String(20),  default='Approved')
    date        = db.Column(db.DateTime,    default=datetime.utcnow)

class Receivable(db.Model):
    __tablename__ = 'receivables'
    id           = db.Column(db.Integer,     primary_key=True)
    debtor_name  = db.Column(db.String(100), nullable=False)
    reference    = db.Column(db.String(50),  nullable=False)
    category     = db.Column(db.String(50),  nullable=False)
    amount       = db.Column(db.Float,       nullable=False)
    due_date     = db.Column(db.Date,        nullable=False)
    status       = db.Column(db.String(20),  default='Outstanding')
    date_created = db.Column(db.DateTime,    default=datetime.utcnow)

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
    date_created = db.Column(db.DateTime,    default=datetime.utcnow)

class CashBank(db.Model):
    __tablename__ = 'cash_bank'
    id               = db.Column(db.Integer,     primary_key=True)
    transaction_type = db.Column(db.String(20),  nullable=False)
    account          = db.Column(db.String(50),  nullable=False)
    description      = db.Column(db.String(200), nullable=False)
    amount           = db.Column(db.Float,       nullable=False)
    reference        = db.Column(db.String(50),  nullable=True)
    date             = db.Column(db.Date,        nullable=False)
    date_created     = db.Column(db.DateTime,    default=datetime.utcnow)

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
    date_created  = db.Column(db.DateTime,    default=datetime.utcnow)

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
    date_created = db.Column(db.DateTime,    default=datetime.utcnow)

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
    date_created = db.Column(db.DateTime,    default=datetime.utcnow)

# ── MODELS KEPT FOR REPORTS COMPATIBILITY ──

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


# ═══════════════════════════════════════════
# CREATE TABLES + MIGRATE
# ═══════════════════════════════════════════

with app.app_context():
    db.create_all()
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
            session['role']      = staff.role
            session['username']  = staff.staff_id
            session['email']     = staff.email
            session['full_name'] = staff.full_name or staff.staff_id
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
    total_students       = Student.query.count()
    staff_count          = Staff.query.count()
    students_owing       = Student.query.filter(Student.balance > 0).count()
    total_courses        = Course.query.count()
    total_announcements  = Announcement.query.count()
    upcoming_exams       = Examination.query.filter_by(status='Scheduled').count()
    recent_students      = Student.query.order_by(Student.id.desc()).limit(5).all()
    latest_announcements = Announcement.query.order_by(Announcement.id.desc()).limit(3).all()
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
    db.session.add(Staff(
        staff_id       = staff_id,
        email          = email,
        password       = request.form.get('password'),
        role           = request.form.get('role'),
        full_name      = request.form.get('full_name', ''),
        department     = request.form.get('department', ''),
        job_title      = request.form.get('job_title', ''),
        phone          = request.form.get('phone', ''),
        specialization = request.form.get('specialization', ''),
        courses_taught = request.form.get('courses_taught', '')
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
        student_id  = request.form.get('student_id'),
        first_name  = first_name,
        last_name   = last_name,
        full_name   = f"{first_name} {last_name}",
        dob         = request.form.get('dob'),
        national_id = request.form.get('national_id'),
        phone       = request.form.get('phone'),
        email       = request.form.get('email'),
        program     = request.form.get('program'),
        year        = int(request.form.get('year') or 1),
        intake_year = request.form.get('intake_year'),
        tuition_fee = tuition_fee,
        amount_paid = amount_paid,
        balance     = tuition_fee - amount_paid,
        status      = request.form.get('status', 'Active'),
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
# ANNOUNCEMENTS
# ═══════════════════════════════════════════

@app.route('/announcements')
def announcements():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    all_announcements = Announcement.query.order_by(Announcement.id.desc()).all()
    return render_template('announcements.html', announcements=all_announcements)

@app.route('/announcements/add', methods=['POST'])
def add_announcement():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(Announcement(
        title     = request.form['title'],
        message   = request.form['message'],
        audience  = request.form['audience'],
        priority  = request.form['priority'],
        date      = request.form['date'],
        posted_by = request.form['posted_by']
    ))
    db.session.commit()
    flash('Announcement posted successfully!', 'success')
    return redirect(url_for('announcements'))

@app.route('/announcements/delete/<int:ann_id>', methods=['POST'])
def delete_announcement(ann_id):
    if session.get('role') != 'admin':
        flash('Access denied.')
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
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(Course(
        code        = request.form['code'],
        name        = request.form['name'],
        department  = request.form['department'],
        duration    = request.form['duration'],
        tuition_fee = float(request.form['tuition_fee']),
        capacity    = int(request.form['capacity']),
        intake_year = int(request.form['intake_year']),
        description = request.form.get('description', ''),
        status      = request.form['status']
    ))
    db.session.commit()
    flash('Course added successfully!', 'success')
    return redirect(url_for('courses'))

@app.route('/courses/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    if session.get('role') != 'admin':
        flash('Access denied.')
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
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(Timetable(
        program    = request.form['program'],
        subject    = request.form['subject'],
        lecturer   = request.form['lecturer'],
        day        = request.form['day'],
        start_time = request.form['start_time'],
        end_time   = request.form['end_time'],
        room       = request.form['room'],
        year       = request.form['year'],
        semester   = request.form['semester']
    ))
    db.session.commit()
    flash('Schedule added successfully!', 'success')
    return redirect(url_for('timetable'))

@app.route('/timetable/delete/<int:tt_id>', methods=['POST'])
def delete_timetable(tt_id):
    if session.get('role') != 'admin':
        flash('Access denied.')
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
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(Examination(
        program     = request.form['program'],
        subject     = request.form['subject'],
        exam_type   = request.form['exam_type'],
        exam_date   = request.form['exam_date'],
        start_time  = request.form['start_time'],
        end_time    = request.form['end_time'],
        venue       = request.form['venue'],
        year        = request.form['year'],
        invigilator = request.form.get('invigilator', ''),
        total_marks = int(request.form.get('total_marks', 100)),
        semester    = request.form['semester'],
        status      = request.form['status']
    ))
    db.session.commit()
    flash('Exam scheduled successfully!', 'success')
    return redirect(url_for('examinations'))

@app.route('/examinations/delete/<int:exam_id>', methods=['POST'])
def delete_examination(exam_id):
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    exam = Examination.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted.', 'success')
    return redirect(url_for('examinations'))


# ═══════════════════════════════════════════
# FINANCE OVERVIEW (Admin read-only)
# ═══════════════════════════════════════════

@app.route('/finance-overview')
def finance_overview():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    from sqlalchemy import func
    tuition_collected = db.session.query(func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    tuition_pending   = db.session.query(func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    tuition_overdue   = 0
    tuition_records   = FeePayment.query.count()
    grants_total      = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    donations_total   = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    payroll_list      = FinancePayroll.query.all()
    payroll_staff     = FinancePayroll.query.count()
    payroll_total     = sum(p.basic_salary + p.allowances for p in payroll_list)
    payroll_paid      = sum(p.basic_salary + p.allowances for p in payroll_list if p.status == 'Paid')
    payroll_pending   = sum(p.basic_salary + p.allowances for p in payroll_list if p.status == 'Pending')
    cash_deposits     = db.session.query(func.sum(CashBank.amount)).filter_by(transaction_type='Deposit').scalar() or 0
    cash_withdrawals  = db.session.query(func.sum(CashBank.amount)).filter_by(transaction_type='Withdrawal').scalar() or 0
    payable_paid      = db.session.query(func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    payable_pending   = db.session.query(func.sum(Payable.amount)).filter_by(status='Pending').scalar() or 0
    payable_overdue   = 0
    payable_records   = Payable.query.count()
    inventory_list      = FinanceInventory.query.all()
    inventory_items     = FinanceInventory.query.count()
    inventory_value     = sum(i.quantity * i.unit_price for i in inventory_list)
    inventory_low_stock = sum(1 for i in inventory_list if i.quantity <= i.min_stock)
    total_income      = tuition_collected + grants_total + donations_total
    total_expenses    = payable_paid + payroll_total
    net_balance       = total_income - total_expenses
    outstanding_fees  = tuition_pending
    return render_template('finance_overview.html',
                           total_income=total_income, total_expenses=total_expenses,
                           net_balance=net_balance, outstanding_fees=outstanding_fees,
                           tuition_collected=tuition_collected, tuition_pending=tuition_pending,
                           tuition_overdue=tuition_overdue, tuition_records=tuition_records,
                           grants_total=grants_total, donations_total=donations_total,
                           payroll_staff=payroll_staff, payroll_total=payroll_total,
                           payroll_paid=payroll_paid, payroll_pending=payroll_pending,
                           cash_deposits=cash_deposits, cash_withdrawals=cash_withdrawals,
                           payable_paid=payable_paid, payable_pending=payable_pending,
                           payable_overdue=payable_overdue, payable_records=payable_records,
                           inventory_items=inventory_items, inventory_value=inventory_value,
                           inventory_low_stock=inventory_low_stock)


# ═══════════════════════════════════════════
# ADMIN REPORTS
# ═══════════════════════════════════════════

@app.route('/reports')
def reports():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    from sqlalchemy import func
    total_students     = Student.query.count()
    active_students    = Student.query.filter_by(status='Active').count()
    deferred_students  = Student.query.filter_by(status='Deferred').count()
    graduated_students = Student.query.filter_by(status='Graduated').count()
    suspended_students = Student.query.filter_by(status='Suspended').count()
    programs           = db.session.query(Student.program, func.count(Student.id)).group_by(Student.program).all()
    total_staff        = Staff.query.count()
    admin_count        = Staff.query.filter_by(role='admin').count()
    finance_count      = Staff.query.filter_by(role='finance').count()
    frontoffice_count  = Staff.query.filter_by(role='front_office').count()
    total_courses      = Course.query.count()
    active_courses     = Course.query.filter_by(status='Active').count()
    total_exams        = Examination.query.count()
    scheduled_exams    = Examination.query.filter_by(status='Scheduled').count()
    completed_exams    = Examination.query.filter_by(status='Completed').count()
    postponed_exams    = Examination.query.filter_by(status='Postponed').count()
    total_announcements= Announcement.query.count()
    tuition_collected  = db.session.query(func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    total_outstanding  = db.session.query(func.sum(Student.balance)).filter(Student.balance > 0).scalar() or 0
    grants_total       = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    donations_total    = db.session.query(func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    total_income       = tuition_collected + grants_total + donations_total
    total_expenses     = db.session.query(func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    net_balance        = total_income - total_expenses
    recent_students    = Student.query.order_by(Student.id.desc()).limit(10).all()
    return render_template('reports.html',
        total_students=total_students, active_students=active_students,
        deferred_students=deferred_students, graduated_students=graduated_students,
        suspended_students=suspended_students, programs=programs,
        total_staff=total_staff, admin_count=admin_count,
        finance_count=finance_count, frontoffice_count=frontoffice_count,
        total_courses=total_courses, active_courses=active_courses,
        total_exams=total_exams, scheduled_exams=scheduled_exams,
        completed_exams=completed_exams, postponed_exams=postponed_exams,
        total_announcements=total_announcements,
        tuition_collected=tuition_collected, total_outstanding=total_outstanding,
        total_income=total_income, total_expenses=total_expenses,
        net_balance=net_balance, recent_students=recent_students)


# ═══════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════

@app.route('/settings')
def settings():
    if session.get('role') not in ['admin', 'finance', 'front_office']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    return render_template('settings.html',
        staff_count=Staff.query.count(),
        student_count=Student.query.count())

@app.route('/settings/update-profile', methods=['POST'])
def update_profile():
    if not session.get('username'):
        return redirect(url_for('staff_login'))
    staff = Staff.query.filter_by(staff_id=session.get('username')).first()
    if staff:
        new_email = request.form.get('email')
        existing  = Staff.query.filter(Staff.email == new_email, Staff.id != staff.id).first()
        if existing:
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
    net_balance    = total_income - total_expenses
    recent_fees    = FeePayment.query.order_by(FeePayment.date.desc()).limit(5).all()
    return render_template('finance/dashboard.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           pending_fees=pending_fees,
                           net_balance=net_balance,
                           recent_fees=recent_fees)

@app.route('/api/chart-data')
def chart_data():
    from sqlalchemy import extract
    import calendar
    months_data  = []
    income_data  = []
    expense_data = []
    for month_num in range(1, 7):
        months_data.append(calendar.month_abbr[month_num])
        tuition = db.session.query(db.func.sum(FeePayment.amount)).filter(
            FeePayment.status == 'Paid',
            extract('month', FeePayment.date) == month_num,
            extract('year',  FeePayment.date) == 2026
        ).scalar() or 0
        grants = db.session.query(db.func.sum(GrantDonation.amount)).filter(
            GrantDonation.status == 'Received',
            extract('month', GrantDonation.date_received) == month_num,
            extract('year',  GrantDonation.date_received) == 2026
        ).scalar() or 0
        income_data.append(tuition + grants)
        expenses = db.session.query(db.func.sum(Payable.amount)).filter(
            Payable.status == 'Paid',
            extract('month', Payable.date_created) == month_num,
            extract('year',  Payable.date_created) == 2026
        ).scalar() or 0
        expense_data.append(expenses)
    return jsonify({'months': months_data, 'income': income_data, 'expenses': expense_data})

# Tuition
@app.route('/finance/tuition')
def tuition():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payments        = FeePayment.query.order_by(FeePayment.date.desc()).all()
    total_collected = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    total_pending   = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    total_overdue   = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Overdue').scalar() or 0
    total_records   = FeePayment.query.count()
    return render_template('finance/tuition.html',
                           payments=payments, total_collected=total_collected,
                           total_pending=total_pending, total_overdue=total_overdue,
                           total_records=total_records)

@app.route('/finance/tuition/add', methods=['POST'])
def add_tuition():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(FeePayment(
        student_id   = request.form['student_id'],
        student_name = request.form['student_name'],
        category     = request.form['category'],
        amount       = float(request.form['amount']),
        method       = request.form['method'],
        status       = request.form['status']
    ))
    db.session.commit()
    flash('Payment recorded successfully!', 'success')
    return redirect(url_for('tuition'))

@app.route('/finance/tuition/delete/<int:fee_id>', methods=['POST'])
def delete_tuition(fee_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    fee = FeePayment.query.get_or_404(fee_id)
    db.session.delete(fee)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('tuition'))

# Accounts Receivable
@app.route('/finance/accounts-receivable')
def accounts_receivable():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    receivables       = Receivable.query.order_by(Receivable.date_created.desc()).all()
    total_received    = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Received').scalar() or 0
    total_outstanding = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Outstanding').scalar() or 0
    total_overdue     = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Overdue').scalar() or 0
    total_records     = Receivable.query.count()
    return render_template('finance/accounts_receivable.html',
                           receivables=receivables, total_received=total_received,
                           total_outstanding=total_outstanding, total_overdue=total_overdue,
                           total_records=total_records)

@app.route('/finance/accounts-receivable/add', methods=['POST'])
def add_receivable():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(Receivable(
        debtor_name = request.form['debtor_name'],
        reference   = request.form['reference'],
        category    = request.form['category'],
        amount      = float(request.form['amount']),
        due_date    = date.fromisoformat(request.form['due_date']),
        status      = request.form['status']
    ))
    db.session.commit()
    flash('Invoice added successfully!', 'success')
    return redirect(url_for('accounts_receivable'))

@app.route('/finance/accounts-receivable/delete/<int:item_id>', methods=['POST'])
def delete_receivable(item_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    item = Receivable.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('accounts_receivable'))

# Accounts Payable
@app.route('/finance/accounts-payable')
def accounts_payable():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payables      = Payable.query.order_by(Payable.date_created.desc()).all()
    total_paid    = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    total_pending = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Pending').scalar() or 0
    total_overdue = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Overdue').scalar() or 0
    total_records = Payable.query.count()
    return render_template('finance/accounts_payable.html',
                           payables=payables, total_paid=total_paid,
                           total_pending=total_pending, total_overdue=total_overdue,
                           total_records=total_records)

@app.route('/finance/accounts-payable/add', methods=['POST'])
def add_payable():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(Payable(
        vendor_name = request.form['vendor_name'],
        reference   = request.form['reference'],
        category    = request.form['category'],
        amount      = float(request.form['amount']),
        due_date    = date.fromisoformat(request.form['due_date']),
        notes       = request.form.get('notes', ''),
        status      = request.form['status']
    ))
    db.session.commit()
    flash('Bill added successfully!', 'success')
    return redirect(url_for('accounts_payable'))

@app.route('/finance/accounts-payable/delete/<int:item_id>', methods=['POST'])
def delete_payable(item_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    item = Payable.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Bill deleted.', 'success')
    return redirect(url_for('accounts_payable'))

# Cash & Bank
@app.route('/finance/cash-bank')
def cash_bank():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    transactions      = CashBank.query.order_by(CashBank.date.desc()).all()
    total_deposits    = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Deposit').scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Withdrawal').scalar() or 0
    cash_on_hand      = db.session.query(db.func.sum(CashBank.amount)).filter_by(account='Cash', transaction_type='Deposit').scalar() or 0
    bank_balance      = total_deposits - total_withdrawals
    return render_template('finance/cash_bank.html',
                           transactions=transactions, total_deposits=total_deposits,
                           total_withdrawals=total_withdrawals, cash_on_hand=cash_on_hand,
                           bank_balance=bank_balance)

@app.route('/finance/cash-bank/add', methods=['POST'])
def add_cash_bank():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(CashBank(
        transaction_type = request.form['transaction_type'],
        account          = request.form['account'],
        description      = request.form['description'],
        amount           = float(request.form['amount']),
        reference        = request.form.get('reference', ''),
        date             = date.fromisoformat(request.form['date'])
    ))
    db.session.commit()
    flash('Transaction recorded successfully!', 'success')
    return redirect(url_for('cash_bank'))

@app.route('/finance/cash-bank/delete/<int:item_id>', methods=['POST'])
def delete_cash_bank(item_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    item = CashBank.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Transaction deleted.', 'success')
    return redirect(url_for('cash_bank'))

# Grants & Donations
@app.route('/finance/grants-donations')
def grants_donations():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    records         = GrantDonation.query.order_by(GrantDonation.date_created.desc()).all()
    total_grants    = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    total_donations = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    total_pending   = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(status='Pending').scalar() or 0
    total_records   = GrantDonation.query.count()
    return render_template('finance/grants_donations.html',
                           records=records, total_grants=total_grants,
                           total_donations=total_donations, total_pending=total_pending,
                           total_records=total_records)

@app.route('/finance/grants-donations/add', methods=['POST'])
def add_grant_donation():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(GrantDonation(
        donor_name    = request.form['donor_name'],
        type          = request.form['type'],
        purpose       = request.form['purpose'],
        amount        = float(request.form['amount']),
        date_received = date.fromisoformat(request.form['date_received']),
        notes         = request.form.get('notes', ''),
        status        = request.form['status']
    ))
    db.session.commit()
    flash('Record added successfully!', 'success')
    return redirect(url_for('grants_donations'))

@app.route('/finance/grants-donations/delete/<int:item_id>', methods=['POST'])
def delete_grant_donation(item_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    item = GrantDonation.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Record deleted.', 'success')
    return redirect(url_for('grants_donations'))

# Payroll
@app.route('/finance/payroll')
def payroll():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    payroll_list  = FinancePayroll.query.order_by(FinancePayroll.date_created.desc()).all()
    total_net_pay = sum(s.basic_salary + s.allowances for s in payroll_list)
    total_paid    = sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Paid')
    total_pending = sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Pending')
    total_staff   = FinancePayroll.query.count()
    return render_template('finance/payroll.html',
                           payroll=payroll_list, total_net_pay=total_net_pay,
                           total_paid=total_paid, total_pending=total_pending,
                           total_staff=total_staff)

@app.route('/finance/payroll/add', methods=['POST'])
def add_payroll():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(FinancePayroll(
        staff_id     = request.form['staff_id'],
        name         = request.form['name'],
        department   = request.form['department'],
        role         = request.form['role'],
        basic_salary = float(request.form['basic_salary']),
        allowances   = float(request.form.get('allowances', 0)),
        status       = request.form['status']
    ))
    db.session.commit()
    flash('Staff added to payroll successfully!', 'success')
    return redirect(url_for('payroll'))

@app.route('/finance/payroll/delete/<int:staff_id>', methods=['POST'])
def delete_payroll(staff_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    staff = FinancePayroll.query.get_or_404(staff_id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff removed from payroll.', 'success')
    return redirect(url_for('payroll'))

# Inventory
@app.route('/finance/inventory')
def inventory():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    items            = FinanceInventory.query.order_by(FinanceInventory.date_created.desc()).all()
    total_items      = FinanceInventory.query.count()
    total_value      = sum(i.quantity * i.unit_price for i in items)
    low_stock        = sum(1 for i in items if i.quantity <= i.min_stock)
    total_categories = db.session.query(FinanceInventory.category).distinct().count()
    return render_template('finance/inventory.html',
                           items=items, total_items=total_items,
                           total_value=total_value, low_stock=low_stock,
                           total_categories=total_categories)

@app.route('/finance/inventory/add', methods=['POST'])
def add_inventory():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    db.session.add(FinanceInventory(
        item_name  = request.form['item_name'],
        category   = request.form['category'],
        department = request.form['department'],
        quantity   = int(request.form['quantity']),
        unit_price = float(request.form['unit_price']),
        min_stock  = int(request.form.get('min_stock', 5)),
        condition  = request.form['condition']
    ))
    db.session.commit()
    flash('Item added successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/finance/inventory/delete/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    item = FinanceInventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'success')
    return redirect(url_for('inventory'))

# Finance Reports
@app.route('/finance/reports')
def finance_reports():
    if session.get('role') != 'finance':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    tuition_collected      = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Paid').scalar() or 0
    tuition_pending        = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Pending').scalar() or 0
    tuition_overdue        = db.session.query(db.func.sum(FeePayment.amount)).filter_by(status='Overdue').scalar() or 0
    tuition_records        = FeePayment.query.count()
    receivable_received    = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Received').scalar() or 0
    receivable_outstanding = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Outstanding').scalar() or 0
    receivable_overdue     = db.session.query(db.func.sum(Receivable.amount)).filter_by(status='Overdue').scalar() or 0
    receivable_records     = Receivable.query.count()
    payable_paid           = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Paid').scalar() or 0
    payable_pending        = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Pending').scalar() or 0
    payable_overdue        = db.session.query(db.func.sum(Payable.amount)).filter_by(status='Overdue').scalar() or 0
    payable_records        = Payable.query.count()
    cash_deposits          = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Deposit').scalar() or 0
    cash_withdrawals       = db.session.query(db.func.sum(CashBank.amount)).filter_by(transaction_type='Withdrawal').scalar() or 0
    grants_total           = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Grant').scalar() or 0
    donations_total        = db.session.query(db.func.sum(GrantDonation.amount)).filter_by(type='Donation').scalar() or 0
    payroll_list           = FinancePayroll.query.all()
    payroll_staff          = FinancePayroll.query.count()
    payroll_total          = sum(s.basic_salary + s.allowances for s in payroll_list)
    payroll_paid           = sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Paid')
    payroll_pending        = sum(s.basic_salary + s.allowances for s in payroll_list if s.status == 'Pending')
    inventory_list         = FinanceInventory.query.all()
    inventory_items        = FinanceInventory.query.count()
    inventory_value        = sum(i.quantity * i.unit_price for i in inventory_list)
    inventory_low_stock    = sum(1 for i in inventory_list if i.quantity <= i.min_stock)
    total_income           = tuition_collected + grants_total + donations_total + receivable_received
    total_expenses         = payable_paid + payroll_total
    net_balance            = total_income - total_expenses
    total_outstanding      = receivable_outstanding + tuition_pending
    return render_template('finance/reports.html',
                           total_income=total_income, total_expenses=total_expenses,
                           net_balance=net_balance, total_outstanding=total_outstanding,
                           tuition_collected=tuition_collected, tuition_pending=tuition_pending,
                           tuition_overdue=tuition_overdue, tuition_records=tuition_records,
                           receivable_received=receivable_received,
                           receivable_outstanding=receivable_outstanding,
                           receivable_overdue=receivable_overdue,
                           receivable_records=receivable_records,
                           payable_paid=payable_paid, payable_pending=payable_pending,
                           payable_overdue=payable_overdue, payable_records=payable_records,
                           cash_deposits=cash_deposits, cash_withdrawals=cash_withdrawals,
                           grants_total=grants_total, donations_total=donations_total,
                           payroll_staff=payroll_staff, payroll_total=payroll_total,
                           payroll_paid=payroll_paid, payroll_pending=payroll_pending,
                           inventory_items=inventory_items, inventory_value=inventory_value,
                           inventory_low_stock=inventory_low_stock)


# ═══════════════════════════════════════════
# FRONT OFFICE / STAFF DASHBOARD
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