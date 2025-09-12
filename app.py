# app.py
import pandas as pd
import streamlit as st

# Load CSV
CSV_PATH = "routine_clean_v3.csv"

@st.cache_data
def load_data(path=CSV_PATH):
    df = pd.read_csv(path)
    df['Teacher'] = df['Teacher'].astype(str).str.strip()
    df['Dept'] = df['Dept'].astype(str).str.strip()
    df['Day'] = df['Day'].astype(str).str.strip()
    df['Time'] = df['Time'].astype(str).str.strip()
    df = df.dropna(subset=['Teacher','Day','Time'], how='any')
    return df

df = load_data()

# Mapping short names to full names
full_name_mapping = {
    "MHKB": "MHKB Brigadier General Md Humayun Kabir Bhuiyan, psc",
    "MMHK": "Md. Mahamudul Hasan Khalid",
    "MOF": "Brigadier General Md. Omar Faruque",
    "MSH":"Md. Sayeed Hasan",
    "NRK":"Dr. Nadim Reza Khandaker",
    "TH":"Tajmul Hasan",
    "KAH":"Dr. Khandkar Aftab Hossain",
    "JAA":"Jannatul Ambia Akhi",
    "BCG":"Dr. Basudeb Chandra Ghosh",
    "AAN":"Dr. Abdullah-Al Nahid",
    "MRR":"Md. Mehedi Rahman Rana",
    "MWU":"Dr. Md. Wali Ullah",
    "MA":"Dr. Mahbub Alam",
    "SSI":"Sheikh Shareeful Islam",
    "JA":"Dr. Md. Jahangir Alam",
    "MMBS":"Md. Masrafi Bin Seraj Sakib",
    "AH":"Asif Hassan",
    "MAR":"Md. Ashiqur Rahman",
    "AUK":"Md. Ayaj Uddin Khan",
    "NR":"Neha Rahman",
    "ABA":"Ahmmed Bin Ashfaque",
    "SMA":"Mst. Sabrina Muktar Arju",
    "ZT":"Zahin Tazwar",
    "SNH":"Syed Nahin Hossain",
    "PK":"Pulak Kundu",
    "MM":"Mehedi Hasan",
    "MAH":"Md. Abdul Hannan",
    "PM":"Ponkaj Mondol",
    "AR":"Ashikur Rahman",
    "UK":"Utpol Kumar",
}

df['Teacher'] = df['Teacher'].map(lambda x: full_name_mapping.get(x, x))

# Pre-define department-wise faculty (example: CSE)
department_faculty = {
    "CSE": ["Ashikur Rahman", "Syed Nahin Hossain", "Ahmmed Bin Ashfaque",
            "Md. Masrafi Bin Seraj Sakib", "Md. Mehedi Rahman Rana", "Md. Mahamudul Hasan Khalid"]
    # Add other departments if needed
}

# --- Streamlit Interface ---
st.title("BAUST Routine Management System")

# Use Streamlit tabs
tab1, tab2 = st.tabs(["Check Teacher Availability", "View Routine Table"])

# ------------------------------
# Tab 1: Check Teacher Availability
# ------------------------------
with tab1:
    st.header("Check Teacher Availability (Busy / Free)")

    # Day selector
    days = sorted(df['Day'].dropna().unique())
    selected_day = st.selectbox("Select Day", days, key="day_avail")

    # Time slot selector
    times = sorted(df.loc[df['Day'] == selected_day, 'Time'].dropna().unique())
    selected_time = st.selectbox("Select Time slot", times, key="time_avail")

    # Optional department filter
    dept_choices = ["(All)"] + sorted(df['Dept'].dropna().unique())
    selected_dept = st.selectbox("Filter by Dept. (optional)", dept_choices, key="dept_avail")

    # Compute busy/free
    mask = (df['Day'] == selected_day) & (df['Time'] == selected_time)
    if selected_dept != "(All)":
        mask &= (df['Dept'] == selected_dept)

    busy = sorted(df.loc[mask, 'Teacher'].dropna().unique())
    all_teachers = sorted(df['Teacher'].dropna().unique())
    free = [t for t in all_teachers if t not in busy]

    st.subheader("Busy Teachers")
    if busy:
        st.write(busy)
        st.table(df.loc[mask, ['Dept','Section','Time','Teacher','Course','Room']].drop_duplicates())
    else:
        st.write("No teachers scheduled (busy) for this slot.")

    st.subheader("Free Teachers")
    if free:
        st.write(free)
    else:
        st.write("No teachers are free (all are scheduled).")

# ------------------------------
# Tab 2: View Routine Table
# ------------------------------
with tab2:
    st.header("View Routine by Department or Teacher")

    # Department selection
    dept_choices = ["(All)"] + sorted(df['Dept'].dropna().unique())
    selected_dept = st.selectbox("Select Department", dept_choices, key="dept_routine_tab")

    # Teacher dropdown disabled if "(All)" selected
    teacher_disabled = selected_dept == "(All)"

    # Teacher selection filtered by department
    if not teacher_disabled:
        if selected_dept in department_faculty:
            teachers_filtered = department_faculty[selected_dept]
        else:
            teachers_filtered = sorted(df[df['Dept'] == selected_dept]['Teacher'].unique())
        teacher_choices = ["(All)"] + teachers_filtered
    else:
        teacher_choices = ["(All)"]

    selected_teacher = st.selectbox(
        "Select Teacher",
        teacher_choices,
        key="teacher_routine_tab",
        disabled=teacher_disabled
    )

    # Filter DataFrame
    mask = pd.Series([True]*len(df))
    if not teacher_disabled and selected_teacher != "(All)":
        mask &= (df['Teacher'] == selected_teacher)
    elif selected_dept != "(All)":
        mask &= (df['Dept'] == selected_dept)

    filtered_df = df[mask]

    if not filtered_df.empty:
        # Metadata
        st.markdown(f"**BAUST Khulna | July 2025**")
        if not teacher_disabled and selected_teacher != "(All)":
            st.markdown(f"**Faculty Member:** {selected_teacher}")
            dept_set = filtered_df['Dept'].unique()
            st.markdown(f"**Department:** {', '.join(dept_set)}")
        elif selected_dept != "(All)":
            st.markdown(f"**Department:** {selected_dept}")

        # Create timetable: days vs time slots
        time_slots = sorted(filtered_df['Time'].unique())
        days_order = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
        routine_table = pd.DataFrame(index=days_order, columns=time_slots)

        for _, row in filtered_df.iterrows():
            routine_table.at[row['Day'], row['Time']] = row['Course']

        st.dataframe(routine_table.fillna(""))

    else:
        st.write("No routine found for the selected department/teacher.")
