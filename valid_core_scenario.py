
import pandas as pd
import random
import math

def get_fully_mutual_friendships(df):
    friends_map = {
        row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']: set(str(row['ΦΙΛΙΑ']).split(',')) if pd.notna(row['ΦΙΛΙΑ']) else set()
        for _, row in df.iterrows()
    }
    fully_mutual = set()
    for student, friends in friends_map.items():
        for friend in friends:
            friend = friend.strip()
            if friend in friends_map and student in friends_map[friend]:
                pair = tuple(sorted([student, friend]))
                fully_mutual.add(pair)
    return fully_mutual

def violates_conflict(df, student_name, target_class):
    conflict_name = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == student_name, 'ΣΥΓΚΡΟΥΣΗ'].values[0]
    if pd.isna(conflict_name):
        return False
    assigned_class = df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == conflict_name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].values
    return assigned_class.size > 0 and assigned_class[0] == target_class

def generate_random_scenario(df, class_names, seed):
    random.seed(seed)
    temp_df = df.copy()
    temp_df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = ''

    # Παιδιά Εκπαιδευτικών
    teacher_df = temp_df[temp_df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν'].sample(frac=1, random_state=seed)
    for i, (index, _) in enumerate(teacher_df.iterrows()):
        temp_df.loc[index, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = class_names[i % len(class_names)]

    # Ζωηροί
    lively_df = temp_df[(temp_df['ΖΩΗΡΟΣ'] == 'Ν') & (temp_df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == '')].sample(frac=1, random_state=seed)
    lively_counts = temp_df[(temp_df['ΖΩΗΡΟΣ'] == 'Ν') & (temp_df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν')].groupby("ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ").size().reindex(class_names, fill_value=0).to_dict()

    for _, row in lively_df.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        target_class = min(lively_counts, key=lively_counts.get)
        temp_df.loc[temp_df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = target_class
        lively_counts[target_class] += 1

    # Ιδιαιτερότητες
    special_df = temp_df[(temp_df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (temp_df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == '')].sample(frac=1, random_state=seed)
    special_counts = temp_df[temp_df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν'].groupby("ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ").size().reindex(class_names, fill_value=0).to_dict()

    for _, row in special_df.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        target_class = min(special_counts, key=special_counts.get)
        temp_df.loc[temp_df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = target_class
        special_counts[target_class] += 1

    return temp_df

def find_valid_core_scenario(df, class_names, max_trials=100):
    mutual_friend_pairs = get_fully_mutual_friendships(df)

    for seed in range(1000, 1000 + max_trials):
        temp_df = generate_random_scenario(df, class_names, seed)

        # Έλεγχος στοχευμένης κατανομής
        teacher_count = temp_df[temp_df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν'].groupby("ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ").size().reindex(class_names, fill_value=0).tolist()
        lively_count = temp_df[temp_df['ΖΩΗΡΟΣ'] == 'Ν'].groupby("ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ").size().reindex(class_names, fill_value=0).tolist()
        special_count = temp_df[temp_df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν'].groupby("ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ").size().reindex(class_names, fill_value=0).tolist()

        targeted = (
            teacher_count in [[1, 2], [2, 1]] and
            lively_count in [[1, 2], [2, 1]] and
            special_count == [1, 1]
        )
        if not targeted:
            continue

        # Έλεγχος συγκρούσεων
        has_conflict = False
        for _, row in temp_df.iterrows():
            if violates_conflict(temp_df, row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'], row['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']):
                has_conflict = True
                break
        if has_conflict:
            continue

        # Έλεγχος αμοιβαίων φιλιών
        all_friends_ok = True
        for s1, s2 in mutual_friend_pairs:
            t1 = temp_df.loc[temp_df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s1, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].values[0]
            t2 = temp_df.loc[temp_df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == s2, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].values[0]
            if t1 != t2:
                all_friends_ok = False
                break

        if all_friends_ok:
            return temp_df, seed

    return None, None
