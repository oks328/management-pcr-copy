# Management-PCR
This is a capstone that is for Philippines' Strategic Performance Management System (SPMS) forms. Primarily for academic environments.

## Setup Instructions

### 1. Prerequisites
- Python 3.1x installed
- XAMPP (or any local MySQL database server)

### 2. Database Setup
1. Open XAMPP Control Panel and start **MySQL**.
2. Open your database manager (e.g., phpMyAdmin at `http://localhost/phpmyadmin`).
3. Create a new database named `ipcr_db`.
4. Import your SQL schema to create the necessary tables. (You can refer to `temp_schema.txt` for table structure details).
5. **Important - Initial Admin Account:** By default, all newly registered users are assigned the `Faculty` role with a `PENDING` verification status. To access the admin dashboard, you must manually insert an initial Admin account into your database:
   - `tbl_employee_profiles` (Add personal details)
   - `tbl_auth_credentials` (Add email, hashed password, set `verification_status` to `'APPROVED'`)
   - `tbl_system_access` (Set `system_role` to `'Admin'`)

### 3. Application Setup
1. Clone this repository and navigate to the project folder in your terminal.
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```
5. Open your web browser and navigate to `http://localhost:5000`.

---

## Sample Walkthrough: Admin Portal & System Updates

The latest updates focus on the **Admin Verification Workflow** and **Accrual Admin Portal**. Here is how to test the new features:

### 1. User Lifecycle Management (Verification Workflow)
1. **Simulate a Sign Up:** On the login page, click **Register** and fill out the faculty details. Upon submission, the account enters a `PENDING` state.
2. **Admin Login:** Log in using your manually seeded Admin credentials. You will automatically be routed to the **Admin Dashboard**.
3. **Review Pending Users:** Locate the "Pending Verification" section in the dashboard to see the newly registered user.
4. **Detailed Review:** Click the **Review** button next to the pending user. A modal will appear displaying all the submitted profile information.
5. **Take Action:** Thoroughly verify the details within the modal, then choose to either **Approve** (grants system access) or **Reject** (removes the application).

### 2. System Governance
From the Admin Dashboard, you can also explore other newly implemented operational modules:
- **Academic Term Configuration:** Open new IPCR academic terms by specifying the Year, Semester, and submission Deadline Date.
- **Master Performance Indicators:** Manage system-wide indicators by defining categories, descriptions, and efficiency types tied to the active academic term.
- **Database Maintenance:** Use the backup feature to securely generate snapshots of the `ipcr_db` database directly to your `/backups` folder.
