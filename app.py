import pandas as pd
import math
import streamlit as st
from io import BytesIO
from auth import check_password
from valid_core_scenario import find_valid_core_scenario

if not check_password():
    st.stop()

st.set_page_config(page_title="Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)", layout="wide")
st.title("📘 Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)")

uploaded_file = st.file_uploader("📥 Μεταφόρτωση Excel με Μαθητές", type=[".xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    num_classes = math.ceil(len(df) / 25)
    class_names = [f"Α{i+1}" for i in range(num_classes)]
    st.success(f"✅ Υπολογίστηκαν {num_classes} τμήματα.")

    # ➕ Ενιαίος Πυρήνας Μαθητών (ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ ή ΖΩΗΡΟΣ ή ΙΔΙΑΙΤΕΡΟΤΗΤΑ == 'Ν')
    core_students = df[
        (df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν') |
        (df['ΖΩΗΡΟΣ'] == 'Ν') |
        (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')
    ].copy()

    st.subheader("🎯 Πυρήνας Μαθητών (Ενοποιημένος)")
    st.dataframe(core_students[['ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ']])

    # ✅ Αυτόματη επιλογή πλήρως έγκυρου σεναρίου πυρήνα
    valid_df, used_seed = find_valid_core_scenario(core_students, class_names)

    if valid_df is not None:
        df = valid_df.copy()
        st.success(f"🎯 Βρέθηκε πλήρως έγκυρο σενάριο πυρήνα (seed = {used_seed}) που τηρεί όλα τα κριτήρια.")
    else:
        st.error("❌ Δεν βρέθηκε πλήρως έγκυρο σενάριο πυρήνα στους δοκιμασμένους συνδυασμούς.")
        st.stop()

    # Προεπισκόπηση και λήψη αποτελέσματος
    st.subheader("📋 Προεπισκόπηση Κατανομής Πυρήνα")
    st.dataframe(df[['ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Κατανομή Πυρήνα')
    st.download_button("📤 Λήψη Κατανομής Πυρήνα", data=output.getvalue(), file_name="katanomi_pyrina.xlsx")
