import sqlite3

def generate_data():
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()

    # Insert Dummy Users
    users = [
        ("admin", "adminpass", "admin"),
        ("mentor1", "mentorpass", "mentor"),
        ("mentor2", "mentorpass", "mentor"),
        ("student1", "studentpass", "student"),
        ("student2", "studentpass", "student")
    ]
    cursor.executemany("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", users)

    # Mentor-Student Relationships
    mappings = [(2, 4), (3, 5)]  # (mentor_id, student_id)
    cursor.executemany("INSERT OR IGNORE INTO mentor_students (mentor_id, student_id) VALUES (?, ?)", mappings)

    # Backlog Data
    backlog_data = [(4, 1), (5, 0)]  # (student_id, has_backlog)
    cursor.executemany("INSERT OR IGNORE INTO backlog_records (student_id, has_backlog) VALUES (?, ?)", backlog_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    generate_data()
