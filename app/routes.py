from flask import render_template, request, redirect, session, url_for, flash
from app import app
from .auth import hash_pass, verify_pass
from .models import get_db_connection, get_user_by_email, register_user, get_pending_users, update_user_status, open_new_term, get_all_terms, add_master_indicator, get_master_indicators, reset_user_password
import mysql.connector, time
from functools import wraps
import os, subprocess, datetime


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash("Unauthorized access. Admin privileges required.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form.get('email', '').lower().strip()
    password = request.form.get('password', '')
    
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('login'))
        
    cursor = conn.cursor()
    result = get_user_by_email(cursor, email)
    conn.close()
    
    if not result:
        time.sleep(0.5) # prevent timing attacks
        flash("Invalid Credentials.", "danger")
        return redirect(url_for('login'))
    
    row = result[0]
    emp_id, stored_hash, system_role, verification_status, first_name, last_name = row
    
    if verify_pass(password, stored_hash):
        if verification_status == 'PENDING':
            flash("Account awaiting Admin approval.", "warning")
            return redirect(url_for('login'))
        elif verification_status == 'REJECTED':
            flash("Account has been rejected.", "danger")
            return redirect(url_for('login'))
            
        session['emp_id'] = emp_id
        session['role'] = system_role
        session['name'] = first_name
        
        if system_role == 'Admin': return redirect(url_for('admin_dashboard'))
        elif system_role == 'Dean': return redirect(url_for('dean_dashboard'))
        elif system_role == 'Manager': return redirect(url_for('manager_dashboard'))
        elif system_role == 'Faculty': return redirect(url_for('faculty_dashboard'))
        elif system_role == 'Designated': return redirect(url_for('designated_dashboard'))
        
        return redirect(url_for('login'))
    else:
        time.sleep(0.5)
        flash("Invalid Credentials.", "danger")
        return redirect(url_for('login'))
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        emp_id = request.form.get('emp_id', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        college = request.form.get('college', '').strip()
        academic_rank = request.form.get('academic_rank', '').strip()
        employment_status = request.form.get('employment_status', '').strip()
        assigned_program = request.form.get('assigned_program', '').strip()
        designation = request.form.get('designation', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        if not designation:
            designation = 'None'
            
        if not all([emp_id, first_name, last_name, college, academic_rank, employment_status, assigned_program, email, password]):
            flash("All fields required.", "danger")
            return redirect(url_for('register'))
        
        hashed_pw = hash_pass(password)
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for('register'))
            
        try:
            cursor = conn.cursor()
            register_user(conn, cursor, emp_id, first_name, last_name, college, academic_rank, employment_status, assigned_program, designation, email, hashed_pw)
            cursor.close()
            conn.close()
            flash("Registration successful. Awaiting Admin approval.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            if conn.is_connected():
                conn.rollback()
                conn.close()
            flash("Registration failed. Employee ID or Email may already exist.", "danger")
            return redirect(url_for('register'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return render_template('admin_dashboard.html')
        
    cursor = conn.cursor()
    
    pending_users = get_pending_users(cursor)
    terms = get_all_terms(cursor)
    indicators = get_master_indicators(cursor)
    
    # Calculate stats
    cursor.execute("SELECT COUNT(*) FROM tbl_auth_credentials WHERE verification_status = 'APPROVED'")
    active_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tbl_evidence_repo")
    evidence_count = cursor.fetchone()[0]
    
    # Find active term details
    cursor.execute("SELECT term_id, academic_year, semester, deadline_date FROM tbl_academic_terms WHERE is_active = TRUE")
    active_term = cursor.fetchone()
    days_remaining = 0
    if active_term and active_term[3]:
        delta = active_term[3] - datetime.date.today()
        days_remaining = delta.days if delta.days > 0 else 0
        
    stats = {
        'active_users': active_users,
        'evidence_count': evidence_count,
        'days_remaining': days_remaining
    }
    
    conn.close()
    return render_template('admin_dashboard.html', pending_users=pending_users, terms=terms, indicators=indicators, stats=stats, active_term=active_term)

@app.route('/admin/verify_user', methods=['POST'])
@admin_required
def admin_verify_user():
    emp_id = request.form.get('emp_id')
    action = request.form.get('action') # 'approve' or 'reject'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        update_user_status(conn, cursor, emp_id, action)
        flash(f"User {action.upper()}D successfully.", "success")
    except Exception as e:
        flash(f"Error processing action: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/open_term', methods=['POST'])
@admin_required
def admin_open_term():
    academic_year = request.form.get('academic_year')
    semester = request.form.get('semester')
    deadline_date = request.form.get('deadline_date')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        open_new_term(conn, cursor, academic_year, semester, deadline_date)
        flash("New Academic Term opened successfully.", "success")
    except Exception as e:
        flash(f"Error opening term: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_indicator', methods=['POST'])
@admin_required
def admin_add_indicator():
    term_id = request.form.get('term_id')
    category_name = request.form.get('category_name')
    description = request.form.get('description')
    efficiency_type = request.form.get('efficiency_type')
    
    if not term_id:
        flash("Action denied. No active Academic Term found.", "danger")
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        add_master_indicator(conn, cursor, category_name, description, efficiency_type, term_id)
        flash("Master Indicator added successfully.", "success")
    except Exception as e:
        flash(f"Error adding indicator: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reset_password', methods=['POST'])
@admin_required
def admin_reset_password():
    emp_id = request.form.get('emp_id')
    new_password = request.form.get('new_password')
    
    if not new_password:
        flash("Password cannot be empty.", "danger")
        return redirect(url_for('admin_dashboard'))
        
    hashed_pw = hash_pass(new_password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        reset_user_password(conn, cursor, emp_id, hashed_pw)
        flash("Password reset successfully.", "success")
    except Exception as e:
        flash(f"Error resetting password: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/backup_db')
@admin_required
def admin_backup_db():
    backup_dir = os.path.join(app.root_path, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ipcr_db_backup_{timestamp}.sql"
    filepath = os.path.join(backup_dir, filename)
    
    try:
        cmd = ['mysqldump', '-u', 'root', 'ipcr_db']
        with open(filepath, 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        flash(f"Database backed up successfully to: /backups/{filename}", "success")
    except FileNotFoundError:
        try:
            xampp_cmd = [r'C:\xampp\mysql\bin\mysqldump.exe', '-u', 'root', 'ipcr_db']
            with open(filepath, 'w') as f:
                subprocess.run(xampp_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
            flash(f"Database backed up successfully to: /backups/{filename}", "success")
        except Exception as fallback_e:
            flash(f"Backup failed. Could not find mysqldump: {fallback_e}", "danger")
    except Exception as e:
        flash(f"Backup failed: {e}", "danger")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/faculty')
def faculty_dashboard(): return render_template('faculty_dashboard.html')

@app.route('/dean')
def dean_dashboard(): return render_template('dean_dashboard.html')

@app.route('/manager')
def manager_dashboard(): return render_template('manager_dashboard.html')

@app.route('/designated')
def designated_dashboard(): return render_template('designated_dashboard.html')