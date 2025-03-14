import sqlite3

class LeaveAgent:
    def process_leave(self, student_id, days):
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()

        # Get assigned mentor
        cursor.execute("SELECT mentor_id FROM mentor_students WHERE student_id=?", (student_id,))
        mentor = cursor.fetchone()

        if not mentor:
            return "No assigned mentor."

        mentor_id = mentor[0]

        # Auto-approve if days ≤ 5
        status = "approved" if days <= 5 else "pending"
        
        cursor.execute("""
            INSERT INTO leave_requests (student_id, mentor_id, days, status) VALUES (?, ?, ?, ?)
        """, (student_id, mentor_id, days, status))

        conn.commit()
        conn.close()

        return status
