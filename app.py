import streamlit as st
import sqlite3
import hashlib
import os

st.set_page_config(page_title="Student Performance", page_icon="🎓")

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    ).hex()


def register_user(username, password):
    salt = os.urandom(16)
    hashed = hash_password(password, salt)
    stored_password = salt.hex() + ":" + hashed

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, stored_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(username, password):
    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()

    if result:
        stored = result[0]
        salt_hex, saved_hash = stored.split(":")
        salt = bytes.fromhex(salt_hex)

        return hash_password(password, salt) == saved_hash

    return False


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


st.title("🎓 Student Performance Prediction")

if not st.session_state.logged_in:

    choice = st.sidebar.selectbox(
        "Select Option",
        ["Login", "Signup"]
    )

    if choice == "Signup":

        st.subheader("Create New Account")

        username = st.text_input("Enter Username")
        password = st.text_input("Enter Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Signup"):

            if username.strip() == "" or password == "":
                st.warning("Please fill all fields")

            elif password != confirm:
                st.error("Passwords do not match")

            else:
                if register_user(username, password):
                    st.success("Account created successfully! Now login.")
                else:
                    st.error("Username already exists")

    else:

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()

            else:
                st.error("Invalid username or password")


else:

    st.sidebar.success(
        "Logged in as " + st.session_state.username
    )

    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    if page == "Dashboard":

        st.header("Student Dashboard")

        st.write(
            "Welcome to Student Performance Prediction Dashboard."
        )

        st.info(
            "This dashboard helps students understand "
            "their expected academic performance."
        )

        st.metric("Project", "Student Performance")
        st.metric("Model Type", "Classification")

    elif page == "Prediction":

        st.header("Student Performance Prediction")

        study_hours = st.number_input(
            "Study Hours per Day",
            min_value=0.0,
            max_value=24.0,
            value=2.0
        )

        attendance = st.slider(
            "Attendance Percentage",
            0, 100, 75
        )

        marks = st.slider(
            "Previous Marks",
            0, 100, 50
        )

        if st.button("Predict Performance"):

            score = (study_hours * 5) + (attendance * 0.3) + (marks * 0.5)

            if score >= 70:
                result = "High Performance"

            elif score >= 45:
                result = "Average Performance"

            else:
                result = "Low Performance"

            st.subheader("Prediction Result")
            st.success(result)

            st.write("Study Hours:", study_hours)
            st.write("Attendance:", attendance, "%")
            st.write("Previous Marks:", marks)

            st.caption(
                "This is a sample rule-based prediction, "
                "not a trained machine learning model."
            )

conn.close()