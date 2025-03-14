import sqlite3

def create_database():
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()

    # Users Table (Students, Mentors, Admins)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'mentor', 'student')) NOT NULL
    )""")

    # Leave Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        mentor_id INTEGER NOT NULL,
        days INTEGER NOT NULL,
        status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
        FOREIGN KEY (student_id) REFERENCES users(id),
        FOREIGN KEY (mentor_id) REFERENCES users(id)
    )""")

    # Mentor-Student Mapping
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mentor_students (
        mentor_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        FOREIGN KEY (mentor_id) REFERENCES users(id),
        FOREIGN KEY (student_id) REFERENCES users(id)
    )""")

    # Backlog Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backlog_records (
        student_id INTEGER NOT NULL,
        has_backlog BOOLEAN NOT NULL CHECK(has_backlog IN (0,1)),
        FOREIGN KEY (student_id) REFERENCES users(id)
    )""")

    # Academic Calendar (Uploaded PDF File Path)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL
    )""")

    # Certificates Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        certificate_path TEXT NOT NULL,
        email_sent BOOLEAN DEFAULT 0,
        FOREIGN KEY (student_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
