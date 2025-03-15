import streamlit as st
import requests

# Flask backend URL
BACKEND_URL = "http://localhost:5000"  # Change to deployed URL if needed

st.title("AI-Powered Academic System")

# Academic Query Section
st.subheader("Ask an Academic Question")
student_id = st.text_input("Enter Your Student ID")
query = st.text_area("Enter your question:")
if st.button("Ask AI"):
    response = requests.post(f"{BACKEND_URL}/academic", json={"student_id": student_id, "query": query})
    st.success(response.json()["response"])

# Leave Request Section
st.subheader("Request Leave")
leave_days = st.number_input("Number of Leave Days", min_value=1, max_value=30, step=1)
if st.button("Submit Leave Request"):
    response = requests.post(f"{BACKEND_URL}/leave", json={"student_id": student_id, "days": leave_days})
    st.success(response.json()["response"])

# Certificate Generation Section
st.subheader("Generate Certificate")
if st.button("Generate Certificate"):
    response = requests.post(f"{BACKEND_URL}/certificate", json={"student_id": student_id})
    st.success(response.json()["response"])
