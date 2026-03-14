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
    id             = db.Column(db.Integer,     primary_key=True)
    staff_id       = db.Column(db.String(50),  unique=True)
    email          = db.Column(db.String(100), unique=True)
    password       = db.Column(db.String(200))
    role           = db.Column(db.String(50))
    full_name      = db.Column(db.String(200), nullable=True)
    department     = db.Column(db.String(100), nullable=True)
    job_title      = db.Column(db.String(100), nullable=True)
    phone          = db.Column(db.String(20),  nullable=True)
    
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

class Inventory(db.Model):
    __tablename__ = 'inventory'
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

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id         = db.Column(db.Integer,    primary_key=True)
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
    id           = db.Column(db.Integer,    primary_key=True)
    program      = db.Column(db.String(100), nullable=False)
    subject      = db.Column(db.String(100), nullable=False)
    exam_type    = db.Column(db.String(20),  nullable=False)
    exam_date    = db.Column(db.String(20),  nullable=False)
    start_time   = db.Column(db.String(10),  nullable=False)
    end_time     = db.Column(db.String(10),  nullable=False)
    venue        = db.Column(db.String(100), nullable=False)
    year         = db.Column(db.String(20),  default='Year 1')
    invigilator  = db.Column(db.String(100), nullable=True)
    total_marks  = db.Column(db.Integer,     default=100)
    semester     = db.Column(db.String(20),  default='Semester 1')
    status       = db.Column(db.String(20),  default='Scheduled')


# ═══════════════════════════════════════════
# CREATE TABLES
# ═══════════════════════════════════════════

with app.app_context():
    db.create_all()
    
    # ADD NEW COLUMNS TO EXISTING STAFF TABLE
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
            except Exception as e:
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


#ANNOUNCEMENT ROUTES
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
    new_ann = Announcement(
        title     = request.form['title'],
        message   = request.form['message'],
        audience  = request.form['audience'],
        priority  = request.form['priority'],
        date      = request.form['date'],
        posted_by = request.form['posted_by']
    )
    db.session.add(new_ann)
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

#courses routes

@app.route('/courses')
def courses():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    all_courses = Course.query.order_by(Course.id.desc()).all()
    return render_template('courses.html', courses=all_courses)

@app.route('/courses/add', methods=['POST'])
def add_course():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    new_course = Course(
        code        = request.form['code'],
        name        = request.form['name'],
        department  = request.form['department'],
        duration    = request.form['duration'],
        tuition_fee = float(request.form['tuition_fee']),
        capacity    = int(request.form['capacity']),
        intake_year = int(request.form['intake_year']),
        description = request.form.get('description', ''),
        status      = request.form['status']
    )
    db.session.add(new_course)
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
#TIMETABLE ROUTES

@app.route('/timetable')
def timetable():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    all_schedules = Timetable.query.order_by(Timetable.day, Timetable.start_time).all()
    all_courses   = Course.query.filter_by(status='Active').all()
    return render_template('timetable.html',
                           timetable=all_schedules,
                           courses=all_courses)

@app.route('/timetable/add', methods=['POST'])
def add_timetable():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    new_tt = Timetable(
        program    = request.form['program'],
        subject    = request.form['subject'],
        lecturer   = request.form['lecturer'],
        day        = request.form['day'],
        start_time = request.form['start_time'],
        end_time   = request.form['end_time'],
        room       = request.form['room'],
        year       = request.form['year'],
        semester   = request.form['semester']
    )
    db.session.add(new_tt)
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

#EXAMINATIONS

@app.route('/examinations')
def examinations():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    all_exams   = Examination.query.order_by(Examination.exam_date).all()
    all_courses = Course.query.filter_by(status='Active').all()
    total_exams = Examination.query.count()
    scheduled   = Examination.query.filter_by(status='Scheduled').count()
    completed   = Examination.query.filter_by(status='Completed').count()
    postponed   = Examination.query.filter_by(status='Postponed').count()
    return render_template('examinations.html',
                           exams=all_exams,
                           courses=all_courses,
                           total_exams=total_exams,
                           scheduled=scheduled,
                           completed=completed,
                           postponed=postponed)

@app.route('/examinations/add', methods=['POST'])
def add_examination():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))
    new_exam = Examination(
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
    )
    db.session.add(new_exam)
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

#FINANCE OVERVIEW ROUTES
@app.route('/finance-overview')
def finance_overview():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('staff_login'))

    # Tuition — from finance system
    from sqlalchemy import func
    tuition_collected = db.session.query(func.sum(Payment.amount)).scalar() or 0
    tuition_pending   = db.session.query(func.sum(Student.balance)).filter(Student.balance > 0).scalar() or 0
    tuition_overdue   = 0
    tuition_records   = Payment.query.count()

    # Grants & Donations
    grants_total    = db.session.query(func.sum(Grant.amount)).filter_by(type='Grant').scalar() or 0
    donations_total = db.session.query(func.sum(Grant.amount)).filter_by(type='Donation').scalar() or 0

    # Payroll
    payroll_list    = Payroll.query.all()
    payroll_staff   = Payroll.query.count()
    payroll_total   = sum(p.gross_salary for p in payroll_list)
    payroll_paid    = sum(p.net_pay for p in payroll_list if p.status == 'paid')
    payroll_pending = sum(p.net_pay for p in payroll_list if p.status == 'pending')

    # Cash & Bank
    cash_deposits    = db.session.query(func.sum(CashTransaction.amount)).filter_by(cb_type='deposit').scalar() or 0
    cash_withdrawals = db.session.query(func.sum(CashTransaction.amount)).filter_by(cb_type='withdrawal').scalar() or 0

    # Payables
    payable_paid    = db.session.query(func.sum(Expense.amount)).filter_by(status='paid').scalar() or 0
    payable_pending = db.session.query(func.sum(Expense.amount)).filter_by(status='pending').scalar() or 0
    payable_overdue = 0
    payable_records = Expense.query.count()

    # Inventory
    inventory_list      = Inventory.query.all()
    inventory_items     = Inventory.query.count()
    inventory_value     = sum(i.quantity * i.unit_price for i in inventory_list)
    inventory_low_stock = sum(1 for i in inventory_list if i.quantity <= i.reorder_level)

    # Totals
    total_income      = tuition_collected + grants_total + donations_total
    total_expenses    = payable_paid + payroll_total
    net_balance       = total_income - total_expenses
    outstanding_fees  = tuition_pending

    return render_template('finance_overview.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           net_balance=net_balance,
                           outstanding_fees=outstanding_fees,
                           tuition_collected=tuition_collected,
                           tuition_pending=tuition_pending,
                           tuition_overdue=tuition_overdue,
                           tuition_records=tuition_records,
                           grants_total=grants_total,
                           donations_total=donations_total,
                           payroll_staff=payroll_staff,
                           payroll_total=payroll_total,
                           payroll_paid=payroll_paid,
                           payroll_pending=payroll_pending,
                           cash_deposits=cash_deposits,
                           cash_withdrawals=cash_withdrawals,
                           payable_paid=payable_paid,
                           payable_pending=payable_pending,
                           payable_overdue=payable_overdue,
                           payable_records=payable_records,
                           inventory_items=inventory_items,
                           inventory_value=inventory_value,
                           inventory_low_stock=inventory_low_stock)


#reports

@app.route('/reports')
def reports():
    if session.get('role') not in ['admin', 'finance']:
        flash('Access denied.')
        return redirect(url_for('staff_login'))

    from sqlalchemy import func

    # STUDENTS
    total_students    = Student.query.count()
    active_students   = Student.query.filter_by(status='Active').count()
    deferred_students = Student.query.filter_by(status='Deferred').count()
    graduated_students= Student.query.filter_by(status='Graduated').count()
    suspended_students= Student.query.filter_by(status='Suspended').count()

    # STUDENTS BY PROGRAM
    programs = db.session.query(
        Student.program,
        func.count(Student.id)
    ).group_by(Student.program).all()

    # STAFF
    total_staff    = Staff.query.count()
    admin_count    = Staff.query.filter_by(role='admin').count()
    finance_count  = Staff.query.filter_by(role='finance').count()
    frontoffice_count = Staff.query.filter_by(role='front_office').count()

    # COURSES
    total_courses  = Course.query.count()
    active_courses = Course.query.filter_by(status='Active').count()

    # EXAMS
    total_exams    = Examination.query.count()
    scheduled_exams= Examination.query.filter_by(status='Scheduled').count()
    completed_exams= Examination.query.filter_by(status='Completed').count()
    postponed_exams= Examination.query.filter_by(status='Postponed').count()

    # ANNOUNCEMENTS
    total_announcements = Announcement.query.count()

    # FINANCE OVERVIEW (simple)
    tuition_collected = db.session.query(func.sum(Payment.amount)).scalar() or 0
    total_outstanding = db.session.query(func.sum(Student.balance)).filter(Student.balance > 0).scalar() or 0
    grants_total      = db.session.query(func.sum(Grant.amount)).filter_by(type='Grant').scalar() or 0
    donations_total   = db.session.query(func.sum(Grant.amount)).filter_by(type='Donation').scalar() or 0
    total_income      = tuition_collected + grants_total + donations_total
    total_expenses    = db.session.query(func.sum(Expense.amount)).scalar() or 0
    net_balance       = total_income - total_expenses

    # RECENT STUDENTS
    recent_students = Student.query.order_by(Student.id.desc()).limit(10).all()

    return render_template('reports.html',
        total_students=total_students,
        active_students=active_students,
        deferred_students=deferred_students,
        graduated_students=graduated_students,
        suspended_students=suspended_students,
        programs=programs,
        total_staff=total_staff,
        admin_count=admin_count,
        finance_count=finance_count,
        frontoffice_count=frontoffice_count,
        total_courses=total_courses,
        active_courses=active_courses,
        total_exams=total_exams,
        scheduled_exams=scheduled_exams,
        completed_exams=completed_exams,
        postponed_exams=postponed_exams,
        total_announcements=total_announcements,
        tuition_collected=tuition_collected,
        total_outstanding=total_outstanding,
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        recent_students=recent_students)






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