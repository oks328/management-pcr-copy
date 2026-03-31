import mysql.connector
from mysql.connector import Error


def get_db_connection():
    try:
        connection = mysql.connector.connect(
           host='localhost',       # Changed from '144.21.57.156'
           port=3306,              # Standard XAMPP MySQL port (was 6767)
           database='ipcr_db',     # Keep the database name
           user='root',            # Default XAMPP user
           password='',            # Default XAMPP password is empty
           connection_timeout=5
        )
        if connection.is_connected():
            print("Connection established to Localhost")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    
    
def get_user_by_email(cursor, email):
    query = """
        SELECT 
            c.emp_id, 
            c.password_hash, 
            s.system_role, 
            c.verification_status, 
            p.first_name, 
            p.last_name
        FROM tbl_auth_credentials c
        JOIN tbl_employee_profiles p ON c.emp_id = p.emp_id
        JOIN tbl_system_access s ON c.emp_id = s.emp_id
        WHERE c.corporate_email = %s
    """
    cursor.execute(query, (email,))
    return cursor.fetchall()

def register_user(conn, cursor, emp_id, first_name, last_name, college, academic_rank, employment_status, assigned_program, designation, email, password_hash):
    try:
        # Step 1: Insert into employee profiles
        query_profile = """
            INSERT INTO tbl_employee_profiles 
            (emp_id, first_name, last_name, college, academic_rank, employment_status, assigned_program, designation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_profile, (emp_id, first_name, last_name, college, academic_rank, employment_status, assigned_program, designation))
        
        # Step 2: Insert into auth credentials
        query_auth = """
            INSERT INTO tbl_auth_credentials (emp_id, corporate_email, password_hash, verification_status)
            VALUES (%s, %s, %s, 'PENDING')
        """
        cursor.execute(query_auth, (emp_id, email, password_hash))

        # Step 3: Insert into system access
        query_access = """
            INSERT INTO tbl_system_access (emp_id, system_role, account_status)
            VALUES (%s, 'Faculty', 'Active')
        """
        cursor.execute(query_access, (emp_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def get_pending_users(cursor):
    query = """
        SELECT 
            p.emp_id, 
            p.first_name, 
            p.last_name, 
            c.corporate_email, 
            s.system_role,
            p.college,
            p.academic_rank,
            p.employment_status,
            p.assigned_program,
            p.designation
        FROM tbl_employee_profiles p
        JOIN tbl_auth_credentials c ON p.emp_id = c.emp_id
        JOIN tbl_system_access s ON p.emp_id = s.emp_id
        WHERE c.verification_status = 'PENDING'
    """
    cursor.execute(query)
    return cursor.fetchall()

def update_user_status(conn, cursor, emp_id, action):
    try:
        if action == 'approve':
            query = "UPDATE tbl_auth_credentials SET verification_status = 'APPROVED' WHERE emp_id = %s"
            cursor.execute(query, (emp_id,))
        elif action == 'reject':
            # Scenario A Schema Delete cascades to auth and system access
            query = "DELETE FROM tbl_employee_profiles WHERE emp_id = %s"
            cursor.execute(query, (emp_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def open_new_term(conn, cursor, academic_year, semester, deadline_date):
    try:
        query_close = "UPDATE tbl_academic_terms SET is_active = FALSE"
        cursor.execute(query_close)
        
        query_open = """
            INSERT INTO tbl_academic_terms (academic_year, semester, deadline_date, is_active)
            VALUES (%s, %s, %s, TRUE)
        """
        cursor.execute(query_open, (academic_year, semester, deadline_date))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def get_all_terms(cursor):
    query = "SELECT term_id, academic_year, semester, deadline_date, is_active FROM tbl_academic_terms ORDER BY term_id DESC"
    cursor.execute(query)
    return cursor.fetchall()

def add_master_indicator(conn, cursor, category_name, description, efficiency_type, term_id):
    try:
        # Check if category exists or insert it
        cursor.execute("SELECT category_id FROM tbl_target_categories WHERE category_name = %s", (category_name,))
        cat_result = cursor.fetchone()
        
        if not cat_result:
            cursor.execute("INSERT INTO tbl_target_categories (category_name) VALUES (%s)", (category_name,))
            category_id = cursor.lastrowid
        else:
            category_id = cat_result[0]
            
        query = """
            INSERT INTO tbl_master_indicators (category_id, indicator_description, efficiency_type, term_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (category_id, description, efficiency_type, term_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def get_master_indicators(cursor, term_id):
    query = """
        SELECT m.indicator_id, c.category_name, m.indicator_description, m.efficiency_type,
               EXISTS(SELECT 1 FROM tbl_cascaded_quotas q WHERE q.indicator_id = m.indicator_id) AS is_locked
        FROM tbl_master_indicators m
        JOIN tbl_target_categories c ON m.category_id = c.category_id
        WHERE m.term_id = %s
        ORDER BY c.category_name, m.indicator_id
    """
    cursor.execute(query, (term_id,))
    return cursor.fetchall()

def import_previous_term_indicators(conn, cursor, active_term_id):
    try:
        cursor.execute("SELECT term_id FROM tbl_academic_terms WHERE is_active = FALSE ORDER BY term_id DESC LIMIT 1")
        prev_term = cursor.fetchone()
        if not prev_term:
            return False, "No previous term found to import from."
        
        cursor.execute("SELECT category_id, indicator_description, efficiency_type FROM tbl_master_indicators WHERE term_id = %s", (prev_term[0],))
        prev_indicators = cursor.fetchall()
        
        if not prev_indicators:
            return False, "Previous term has no indicators to import."
            
        for ind in prev_indicators:
            cursor.execute("""
                INSERT INTO tbl_master_indicators (category_id, indicator_description, efficiency_type, term_id)
                VALUES (%s, %s, %s, %s)
            """, (ind[0], ind[1], ind[2], active_term_id))
            
        conn.commit()
        return True, "Previous semester targets successfully imported!"
    except Exception as e:
        conn.rollback()
        raise e

def edit_master_indicator(conn, cursor, indicator_id, category_name, description, efficiency_type):
    try:
        cursor.execute("SELECT category_id FROM tbl_target_categories WHERE category_name = %s", (category_name,))
        cat_result = cursor.fetchone()
        if not cat_result:
            cursor.execute("INSERT INTO tbl_target_categories (category_name) VALUES (%s)", (category_name,))
            category_id = cursor.lastrowid
        else:
            category_id = cat_result[0]
            
        query = """
            UPDATE tbl_master_indicators 
            SET category_id = %s, indicator_description = %s, efficiency_type = %s
            WHERE indicator_id = %s
        """
        cursor.execute(query, (category_id, description, efficiency_type, indicator_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def delete_master_indicator(conn, cursor, indicator_id):
    try:
        cursor.execute("DELETE FROM tbl_master_indicators WHERE indicator_id = %s", (indicator_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def reset_user_password(conn, cursor, emp_id, password_hash):
    try:
        query = "UPDATE tbl_auth_credentials SET password_hash = %s WHERE emp_id = %s"
        cursor.execute(query, (password_hash, emp_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e