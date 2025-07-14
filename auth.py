
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "katanomi2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Κωδικός Πρόσβασης:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Κωδικός Πρόσβασης:", type="password", on_change=password_entered, key="password")
        st.error("🚫 Λάθος κωδικός.")
        return False
    else:
        return True
