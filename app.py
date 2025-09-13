# app.py
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

# ------------------------------
# Load CSV
# ------------------------------
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

# ------------------------------
# Mapping short names to full names
# ------------------------------
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
    "SHG":"Shiab Hossen Gaddafee",
}
df['Teacher'] = df['Teacher'].map(lambda x: full_name_mapping.get(x, x))

# ------------------------------
# Department-wise faculty
# ------------------------------
department_faculty = {
    "CSE": [
        "Ashikur Rahman", "Syed Nahin Hossain", "Ahmmed Bin Ashfaque",
        "Md. Masrafi Bin Seraj Sakib", "Md. Mehedi Rahman Rana", "Md. Mahamudul Hasan Khalid"
    ],
    "DBA": [
        "Dr. Md. Jahangir Alam","Shiab Hossen Gaddafee"
    ],
    "ME": [
        "Utpol Kumar","Ponkaj Mondol","Asif Hassan",
        "MHKB Brigadier General Md Humayun Kabir Bhuiyan, psc",
        "Dr. Khandkar Aftab Hossain","Mehedi Hasan"
    ],
    "CE": [
        "Md. Sayeed Hasan","Dr. Nadim Reza Khandaker"
    ],
    "EEE": [
        "Zahin Tazwar"
    ]
}

# ------------------------------
# Faculty metadata (designation etc.)
# ------------------------------
faculty_metadata = {
    "Ashikur Rahman": {"Dept": "CSE", "Designation": "Lecturer"},
    "Syed Nahin Hossain": {"Dept": "CSE", "Designation": "Lecturer"},
    "Ahmmed Bin Ashfaque": {"Dept": "CSE", "Designation": "Lecturer"},
    "Md. Masrafi Bin Seraj Sakib": {"Dept": "CSE", "Designation": "Lecturer"},
    "Md. Mehedi Rahman Rana": {"Dept": "CSE", "Designation": "Assistant Professor"},
    "Md. Mahamudul Hasan Khalid": {"Dept": "CSE", "Designation": "Lecturer"},
    "Dr. Md. Jahangir Alam": {"Dept": "DBA", "Designation": "Professor"},
    "Shiab Hossen Gaddafee": {"Dept": "DBA", "Designation": "Lecturer"},
    # Add other teachers with designation...
}

# ------------------------------
# PDF Generator
# ------------------------------
time_slots = [
    "8:30-9:20", "9:25-10:15", "10:20-11:10", "11:10-11:40",
    "11:40-12:30", "12:35-1:25", "1:25-1:40", "1:40-2:30"
]
days_order = ["Sun", "Mon", "Tue", "Wed", "Thu"]

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def generate_pdf(teacher_name, dept, filtered_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()

    center_style = ParagraphStyle(
        name="Center",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        spaceAfter=6,
    )
    title_style = ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=12,
    )

    story = []

    # Title / faculty info
    story.append(Paragraph("<b>BAUST Khulna | July 2025</b>", title_style))
    story.append(Paragraph("Routine", title_style))
    story.append(Spacer(1, 12))
    designation = faculty_metadata.get(teacher_name, {}).get("Designation", "N/A")
    story.append(Paragraph(f"<b>Faculty Member:</b> {teacher_name}", center_style))
    story.append(Paragraph(f"<b>Department:</b> {dept}", center_style))
    story.append(Paragraph(f"<b>Designation:</b> {designation}", center_style))
    story.append(Spacer(1, 12))

    # Build table_data: header + one row per day
    table_data = [["Day"] + time_slots]
    for day in days_order:
        row = [day]
        for slot in time_slots:
            if slot in ["11:10-11:40", "1:25-1:40"]:
                row.append("BREAK")
            else:
                match = filtered_df[(filtered_df["Day"] == day) & (filtered_df["Time"] == slot)]
                if not match.empty:
                    row.append("\n".join(match["Course"].tolist()))
                else:
                    row.append("")
        table_data.append(row)

    table = Table(table_data, repeatRows=1)

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ])

    # Apply styling only to cells that actually contain "BREAK"
    for r_idx, row in enumerate(table_data):
        # skip header row (r_idx == 0) if you don't want header treated
        for c_idx, cell in enumerate(row):
            if isinstance(cell, str) and cell.strip().upper() == "BREAK":
                style.add("BACKGROUND", (c_idx, r_idx), (c_idx, r_idx), colors.lightgrey)
                style.add("FONTNAME", (c_idx, r_idx), (c_idx, r_idx), "Helvetica-Bold")
                style.add("TEXTCOLOR", (c_idx, r_idx), (c_idx, r_idx), colors.darkblue)
                style.add("VALIGN", (c_idx, r_idx), (c_idx, r_idx), "MIDDLE")

    table.setStyle(style)
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------------------
# Streamlit Interface
# ------------------------------
st.title("BAUST Routine Management System")

tab1, tab2 = st.tabs(["Check Teacher Availability", "View Routine Table"])

# ------------------------------
# Tab 1: Check Teacher Availability
# ------------------------------
# ------------------------------
# Tab 1: Check Teacher Availability
# ------------------------------
with tab1:
    st.header("Check Teacher Availability (Busy / Free)")

    # Add "Select..." as the first option
    days = ["Select Day"] + sorted(df['Day'].dropna().unique())
    selected_day = st.selectbox("Select Day", days, key="day_avail")

    if selected_day != "Select Day":
        times = ["Select Time"] + sorted(df.loc[df['Day'] == selected_day, 'Time'].dropna().unique())
        selected_time = st.selectbox("Select Time slot", times, key="time_avail")
    else:
        selected_time = "Select Time"

    dept_choices = ["Select Dept."] + sorted(df['Dept'].dropna().unique())
    selected_dept = st.selectbox("Filter by Dept. (optional)", dept_choices, key="dept_avail")

    # Only apply mask if valid selections made
    if selected_day != "Select Day" and selected_time != "Select Time":
        mask = (df['Day'] == selected_day) & (df['Time'] == selected_time)
        if selected_dept != "Select Dept.":
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
    else:
        st.info("Please select Day and Time to check teacher availability.")

# ------------------------------
# Tab 2: View Routine Table
# ------------------------------
with tab2:
    st.header("View Routine by Department or Teacher")

    dept_choices = ["(All)"] + sorted(df['Dept'].dropna().unique())
    selected_dept = st.selectbox("Select Department", dept_choices, key="dept_routine_tab")

    teacher_disabled = selected_dept == "(All)"

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

    mask = pd.Series([True]*len(df))
    if not teacher_disabled and selected_teacher != "(All)":
        mask &= (df['Teacher'] == selected_teacher)
    elif selected_dept != "(All)":
        mask &= (df['Dept'] == selected_dept)

    filtered_df = df[mask]

    if not filtered_df.empty:
        st.markdown(f"**BAUST Khulna | July 2025**")
        if not teacher_disabled and selected_teacher != "(All)":
            st.markdown(f"**Faculty Member:** {selected_teacher}")
            dept_set = filtered_df['Dept'].unique()
            st.markdown(f"**Department:** {', '.join(dept_set)}")
        elif selected_dept != "(All)":
            st.markdown(f"**Department:** {selected_dept}")

        time_slots_display = sorted(filtered_df['Time'].unique())
        days_order_display = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
        routine_table = pd.DataFrame(index=days_order_display, columns=time_slots_display)

        for _, row in filtered_df.iterrows():
            routine_table.at[row['Day'], row['Time']] = row['Course']

        st.dataframe(routine_table.fillna(""))

        # --- PDF download button ---
        if not teacher_disabled and selected_teacher != "(All)":
            pdf_buffer = generate_pdf(selected_teacher, selected_dept, filtered_df)
            st.download_button(
                label="📥 Download Routine as PDF",
                data=pdf_buffer,
                file_name=f"{selected_teacher}_routine.pdf",
                mime="application/pdf"
            )
    else:
        st.write("No routine found for the selected department/teacher.")










