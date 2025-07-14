
import pandas as pd

def extract_conflicts(row):
    # Υποστηρίζει και τις δύο εκδοχές: ΣΥΓΚΡΟΥΣΗ ή ΣΥΓΚΡΟΥΣΕΙΣ
    conflicts = row.get('ΣΥΓΚΡΟΥΣΗ') or row.get('ΣΥΓΚΡΟΥΣΕΙΣ')
    return conflicts.split(',') if pd.notna(conflicts) else []

def run_step_1(df, num_sections):
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = None
    teacher_kids = df[df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν'].copy()
    section_counts = {f"Τμήμα {i+1}": 0 for i in range(num_sections)}

    for _, row in teacher_kids.iterrows():
        conflicts = extract_conflicts(row)
        placed = False
        for section in section_counts:
            section_kids = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == section]
            if row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] in section_kids.get('ΣΥΓΚΡΟΥΣΗ', '').values or                row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] in section_kids.get('ΣΥΓΚΡΟΥΣΕΙΣ', '').values:
                continue
            df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'], 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = section
            section_counts[section] += 1
            placed = True
            break
        if not placed:
            df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'], 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = min(section_counts, key=section_counts.get)
            section_counts[min(section_counts, key=section_counts.get)] += 1
    return df

def run_step_2(df, num_sections):
    # Placeholder – εδώ θα υλοποιηθεί η λογική ζωηρών
    return df

def run_step_3(df, num_sections):
    # Placeholder – εδώ θα υλοποιηθεί η λογική ιδιαιτεροτήτων
    return df

def calculate_stats(df, num_sections):
    stats = []
    for i in range(num_sections):
        section = f"Τμήμα {i+1}"
        group = df[df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == section]
        stats.append({
            "Τμήμα": section,
            "Πλήθος": len(group),
            "Αγόρια": (group['ΦΥΛΟ'] == 'Α').sum(),
            "Κορίτσια": (group['ΦΥΛΟ'] == 'Κ').sum(),
            "Παιδιά Εκπαιδευτικών": (group['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν').sum(),
            "Ζωηροί": (group['ΖΩΗΡΟΣ'] == 'Ν').sum(),
            "Ιδιαιτερότητες": (group['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν').sum()
        })
    return pd.DataFrame(stats)
