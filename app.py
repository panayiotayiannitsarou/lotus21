import pandas as pd
import math
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)", layout="wide")
st.title("📘 Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)")

uploaded_file = st.file_uploader("📥 Μεταφόρτωση Excel με Μαθητές Πυρήνα", type=[".xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = None
    class_names = ["Α1", "Α2"]

    # ΒΗΜΑ 1 – ΠΑΙΔΙΑ ΕΚΠΑΙΔΕΥΤΙΚΩΝ
    teacher_kids = df[df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν']
    if len(teacher_kids) <= 2:
        for i, (_, row) in enumerate(teacher_kids.iterrows()):
            df.loc[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = class_names[i]
    else:
        assigned = {c: [] for c in class_names}
        for _, row in teacher_kids.iterrows():
            conflict = row['ΣΥΓΚΡΟΥΣΗ']
            gender = row['ΦΥΛΟ']
            counts = {c: len(assigned[c]) for c in class_names}
            sorted_classes = sorted(class_names, key=lambda x: counts[x])
            for cls in sorted_classes:
                if conflict not in assigned[cls]:
                    df.loc[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = cls
                    assigned[cls].append(row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'])
                    break

    # ΒΗΜΑ 2 – ΖΩΗΡΟΙ
    lively_kids = df[df['ΖΩΗΡΟΣ'] == 'Ν']
    assigned_lively = {c: df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == c) & (df['ΖΩΗΡΟΣ'] == 'Ν')].shape[0] for c in class_names}
    for _, row in lively_kids.iterrows():
        if pd.notna(df.loc[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']): continue
        conflict = row['ΣΥΓΚΡΟΥΣΗ']
        gender = row['ΦΥΛΟ']
        sorted_classes = sorted(class_names, key=lambda x: assigned_lively[x])
        for cls in sorted_classes:
            class_df = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == cls]
            if conflict not in class_df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values:
                df.loc[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = cls
                assigned_lively[cls] += 1
                break

    # ΒΗΜΑ 3 – ΙΔΙΑΙΤΕΡΟΤΗΤΕΣ
    special_kids = df[df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν']
    assigned_special = {c: df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == c) & (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')].shape[0] for c in class_names}
    lively_counts = {c: df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == c) & (df['ΖΩΗΡΟΣ'] == 'Ν')].shape[0] for c in class_names}
    for _, row in special_kids.iterrows():
        if pd.notna(df.loc[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']): continue
        conflict = row['ΣΥΓΚΡΟΥΣΗ']
        gender = row['ΦΥΛΟ']
        sorted_classes = sorted(class_names, key=lambda c: (lively_counts[c], assigned_special[c]))
        for cls in sorted_classes:
            class_df = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == cls]
            if conflict not in class_df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values:
                df.loc[row.name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = cls
                assigned_special[cls] += 1
                break

    st.subheader("📋 Προεπισκόπηση Κατανομής Πυρήνα")
    st.dataframe(df[['ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']])

    # 📊 Στατιστικά
    stats = df.groupby('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ').agg(
        Αριθμός_Μαθητών=('ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'count'),
        Αγόρια=('ΦΥΛΟ', lambda x: (x == 'Α').sum()),
        Κορίτσια=('ΦΥΛΟ', lambda x: (x == 'Κ').sum()),
        Παιδιά_Εκπαιδευτικών=('ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', lambda x: (x == 'Ν').sum()),
        Ζωηροί=('ΖΩΗΡΟΣ', lambda x: (x == 'Ν').sum()),
        Ιδιαιτερότητες=('ΙΔΙΑΙΤΕΡΟΤΗΤΑ', lambda x: (x == 'Ν').sum())
    ).reset_index()
    st.subheader("📊 Στατιστικά Κατανομής")
    st.dataframe(stats)

    # 📥 Λήψη Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Κατανομή Πυρήνα')
    st.download_button("📤 Λήψη Αρχείου Excel", data=output.getvalue(), file_name="katanomi_pyrina_v1.xlsx")
