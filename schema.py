import sqlite3

def update_schema():
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()

    # Drop old tables if they exist
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS leave_requests")

    # Create updated users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'mentor', 'student')) NOT NULL
        )
    """)

    # Create updated leave_requests table
    cursor.execute("""
        CREATE TABLE leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            mentor_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER NOT NULL,
            status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) NOT NULL DEFAULT 'pending',
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (mentor_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def insert_synthetic_data():
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()

    # Insert synthetic users
    users = [
        ("admin_user", "admin_pass", "admin"),
        ("mentor1", "mentor1_pass", "mentor"),
        ("mentor2", "mentor2_pass", "mentor"),
        ("student1", "student1_pass", "student"),
        ("student2", "student2_pass", "student"),
    ]
    cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_schema()
    insert_synthetic_data()
    print("Database schema updated & synthetic data inserted successfully.")
