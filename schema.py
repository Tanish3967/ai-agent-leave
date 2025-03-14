import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("leave_management.db")
cursor = conn.cursor()

# Drop existing tables (for fresh setup, remove if not needed)
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS leave_requests")
cursor.execute("DROP TABLE IF EXISTS mentors")

# Create Users Table
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'mentor', 'student')) NOT NULL
)
""")

# Create Mentors Table (to allow multiple students under one mentor)
cursor.execute("""
CREATE TABLE mentors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    FOREIGN KEY (mentor_id) REFERENCES users(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE (mentor_id, student_id) -- Ensure no duplicate mentor-student assignments
)
""")

# Create Leave Requests Table
cursor.execute("""
CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    mentor_id INTEGER NOT NULL,
    days INTEGER NOT NULL CHECK(days > 0 AND days <= 10), -- Max leave days limit
    status TEXT CHECK(status IN ('approved', 'pending', 'rejected')) NOT NULL DEFAULT 'pending',
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (mentor_id) REFERENCES users(id)
)
""")

# Insert Synthetic Users
users_data = [
    ("admin1", "admin123", "admin"),
    ("mentor1", "mentor123", "mentor"),
    ("mentor2", "mentor123", "mentor"),
    ("student1", "student123", "student"),
    ("student2", "student123", "student"),
]

cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users_data)

# Assign Students to Mentors
mentors_data = [
    (2, 4),  # Mentor 1 -> Student 1
    (2, 5),  # Mentor 1 -> Student 2
    (3, 5),  # Mentor 2 -> Student 2
]

cursor.executemany("INSERT INTO mentors (mentor_id, student_id) VALUES (?, ?)", mentors_data)

# Commit and Close Connection
conn.commit()
conn.close()

print("Database schema created and synthetic data inserted successfully.")
