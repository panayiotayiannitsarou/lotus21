# valid_core_steps.py – Εκτελεί τα Βήματα 1–3

import pandas as pd
from collections import defaultdict

# ----------------------------------
def run_step_1(df, num_sections):
    df = df.copy()
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = None
    teachers_kids = df[df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν']
    placed = set()
    section_counts = defaultdict(int)

    for i, (_, row) in enumerate(teachers_kids.iterrows()):
        conflicts = row['ΣΥΓΚΡΟΥΣΕΙΣ'].split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΕΙΣ']) else []
        gender = row['ΦΥΛΟ']
        friends = row['ΦΙΛΟΙ'].split(',') if pd.notna(row['ΦΙΛΟΙ']) else []

        # Προτεραιότητα: αποφυγή σύγκρουσης, φιλία, κατανομή φύλου
        best_section = None
        min_count = float('inf')

        for sec in range(1, num_sections+1):
            sec_label = f"Α{sec}"
            group = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label]
            if any(c.strip() in group['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values for c in conflicts):
                continue
            if best_section is None or section_counts[sec_label] < min_count:
                best_section = sec_label
                min_count = section_counts[sec_label]

        if best_section:
            idx = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']].index[0]
            df.at[idx, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = best_section
            section_counts[best_section] += 1
            placed.add(row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'])

    return df

# ----------------------------------
def run_step_2(df, num_sections):
    df = df.copy()
    lively = df[(df['ΖΩΗΡΟΣ'] == 'Ν') & (df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].isna())]
    section_lively = defaultdict(int)
    for sec in range(1, num_sections+1):
        sec_label = f"Α{sec}"
        section_lively[sec_label] = len(df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label) & (df['ΖΩΗΡΟΣ'] == 'Ν')])

    for _, row in lively.iterrows():
        conflicts = row['ΣΥΓΚΡΟΥΣΕΙΣ'].split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΕΙΣ']) else []
        friends = row['ΦΙΛΟΙ'].split(',') if pd.notna(row['ΦΙΛΟΙ']) else []

        best_section = None
        min_lively = float('inf')
        for sec in range(1, num_sections+1):
            sec_label = f"Α{sec}"
            group = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label]
            if any(c.strip() in group['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values for c in conflicts):
                continue
            if section_lively[sec_label] < min_lively:
                best_section = sec_label
                min_lively = section_lively[sec_label]

        if best_section:
            idx = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']].index[0]
            df.at[idx, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = best_section
            section_lively[best_section] += 1

    return df

# ----------------------------------
def run_step_3(df, num_sections):
    df = df.copy()
    special = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].isna())]
    section_special = defaultdict(int)
    section_lively = defaultdict(int)
    for sec in range(1, num_sections+1):
        sec_label = f"Α{sec}"
        section_special[sec_label] = len(df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label) & (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')])
        section_lively[sec_label] = len(df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label) & (df['ΖΩΗΡΟΣ'] == 'Ν')])

    for _, row in special.iterrows():
        conflicts = row['ΣΥΓΚΡΟΥΣΕΙΣ'].split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΕΙΣ']) else []
        friends = row['ΦΙΛΟΙ'].split(',') if pd.notna(row['ΦΙΛΟΙ']) else []

        best_section = None
        min_special = float('inf')
        for sec in sorted(range(1, num_sections+1), key=lambda x: section_lively[f"Α{x}"]):
            sec_label = f"Α{sec}"
            group = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label]
            if any(c.strip() in group['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values for c in conflicts):
                continue
            if section_special[sec_label] < min_special:
                best_section = sec_label
                min_special = section_special[sec_label]

        if best_section:
            idx = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']].index[0]
            df.at[idx, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = best_section
            section_special[best_section] += 1

    return df

# ----------------------------------
def calculate_stats(df, num_sections):
    df = df.copy()
    stats = []
    for sec in range(1, num_sections+1):
        sec_label = f"Α{sec}"
        group = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == sec_label]
        boys = len(group[group['ΦΥΛΟ'] == 'Α'])
        girls = len(group[group['ΦΥΛΟ'] == 'Κ'])
        lively = len(group[group['ΖΩΗΡΟΣ'] == 'Ν'])
        special = len(group[group['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν'])
        teachers = len(group[group['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν'])
        stats.append({
            'Τμήμα': sec_label,
            'Σύνολο': len(group),
            'Αγόρια': boys,
            'Κορίτσια': girls,
            'Ζωηροί': lively,
            'Ιδιαιτερότητες': special,
            'Παιδιά Εκπαιδευτικών': teachers
        })
    return pd.DataFrame(stats)
