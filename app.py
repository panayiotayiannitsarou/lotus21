# app.py — Γραμμική Εκτέλεση Βημάτων 1–3 Χωρίς Χρήση Σεναρίων

import streamlit as st
import pandas as pd
from io import BytesIO
from valid_core_steps import run_step_1, run_step_2, run_step_3, calculate_stats

st.set_page_config(page_title="Κατανομή Πυρήνα Μαθητών", layout="wide")
st.title("📘 Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)")

# --- Κωδικός Πρόσβασης ---
with st.sidebar:
    st.markdown("## 🔒 Κωδικός Πρόσβασης")
    password = st.text_input("Εισάγετε τον κωδικό:", type="password")
    if password != "katanomi2025":
        st.warning("🔐 Εισάγετε σωστό κωδικό για πρόσβαση στην εφαρμογή.")
        st.stop()
    enabled = st.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
    if not enabled:
        st.info("Η εφαρμογή είναι απενεργοποιημένη.")
        st.stop()

# --- Μεταφόρτωση Excel ---
st.markdown("### 📥 Μεταφόρτωση Excel με Μαθητές")
uploaded_file = st.file_uploader("Drag and drop file here", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")

    # --- Υπολογισμός αριθμού τμημάτων ---
    num_students = len(df)
    num_sections = -(-num_students // 25)  # Στρογγυλοποίηση προς τα πάνω
    st.success(f"✅ Υπολογίστηκαν {num_sections} τμήματα.")

    # --- Εμφάνιση Πυρήνα ---
    df_core = df[(df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν') | (df['ΖΩΗΡΟΣ'] == 'Ν') | (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')].copy()
    df_core.reset_index(drop=True, inplace=True)
    st.markdown("### 🎯 Πυρήνας Μαθητών (Εντοπισμένος)")
    st.dataframe(df_core)

    # --- Βήμα 1 ---
    df_step1 = run_step_1(df_core.copy(), num_sections)
    # --- Βήμα 2 ---
    df_step2 = run_step_2(df_step1.copy(), num_sections)
    # --- Βήμα 3 ---
    df_step3 = run_step_3(df_step2.copy(), num_sections)

    st.markdown("### ✅ ΠΡΟΤΕΙΝΟΜΕΝΗ ΚΑΤΑΝΟΜΗ ΠΥΡΗΝΑ")
    st.dataframe(df_step3)

    # --- Στατιστικά ---
    stats = calculate_stats(df_step3, num_sections)
    st.markdown("### 📊 Στατιστικά Κατανομής")
    st.dataframe(stats)

    # --- Λήψη αποτελέσματος ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_step3.to_excel(writer, index=False, sheet_name='Κατανομή Πυρήνα')
        stats.to_excel(writer, index=False, sheet_name='Στατιστικά')
    st.download_button("📥 Λήψη Κατανομής σε Excel", data=output.getvalue(), file_name="Πυρήνας_Κατανομής.xlsx")
