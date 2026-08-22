import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="RUAS Executive Placement Intelligence Platform",
    page_icon="📊",
    layout="wide"
)

st.title("RUAS Executive Placement Intelligence Platform")

# ==================================================
# FILE UPLOAD
# ==================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload Placement Workbook",
    type=["xlsx", "xls"]
)

if uploaded_file is None:
    st.info("Upload your placement workbook to begin.")
    st.stop()

# ==================================================
# LOAD EXCEL
# ==================================================

xls = pd.ExcelFile(uploaded_file)

sheet = st.sidebar.selectbox(
    "Select Sheet",
    xls.sheet_names
)

df = pd.read_excel(uploaded_file, sheet_name=sheet)

# ==================================================
# COLUMN STANDARDIZATION
# ==================================================

df.columns = [str(c).strip() for c in df.columns]

# ==================================================
# FILTERS
# ==================================================

st.sidebar.header("Executive Filters")

filtered = df.copy()

# Faculty Filter
faculty_col = None
for c in df.columns:
    if "faculty" in c.lower():
        faculty_col = c
        break

if faculty_col:

    faculty = st.sidebar.selectbox(
        "Faculty",
        ["All"] + sorted(df[faculty_col].dropna().astype(str).unique())
    )

    if faculty != "All":
        filtered = filtered[
            filtered[faculty_col].astype(str) == faculty
        ]

# Year Filter
year_col = None
for c in df.columns:
    if "year" in c.lower():
        year_col = c
        break

if year_col:

    year = st.sidebar.selectbox(
        "Year",
        ["All"] +
        sorted(filtered[year_col].dropna().astype(str).unique())
    )

    if year != "All":
        filtered = filtered[
            filtered[year_col].astype(str) == year
        ]

# Program Filter
program_col = None

for c in df.columns:

    if (
        "program" in c.lower()
        or
        "branch" in c.lower()
        or
        "department" in c.lower()
    ):
        program_col = c
        break

if program_col:

    program = st.sidebar.selectbox(
        "Program",
        ["All"] +
        sorted(filtered[program_col]
        .dropna()
        .astype(str)
        .unique())
    )

    if program != "All":
        filtered = filtered[
            filtered[program_col].astype(str) == program
        ]

# ==================================================
# DETECT PACKAGE COLUMN
# ==================================================

package_col = None

for c in filtered.columns:

    name = c.lower()

    if (
        "package" in name
        or
        "salary" in name
        or
        "ctc" in name
    ):
        package_col = c
        break

# ==================================================
# EXECUTIVE KPI SECTION
# ==================================================

st.subheader("Executive Dashboard")

total_records = len(filtered)

avg_package = 0
highest_package = 0
median_package = 0

if package_col:

    pkg = pd.to_numeric(
        filtered[package_col],
        errors="coerce"
    )

    avg_package = round(pkg.mean(), 2)
    highest_package = round(pkg.max(), 2)
    median_package = round(pkg.median(), 2)

placement_quality_index = round(
    (
        min(avg_package, 20) * 3
        +
        min(total_records / 10, 40)
    ),
    2
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Student Records",
    f"{total_records:,}"
)

c2.metric(
    "Average Package",
    avg_package
)

c3.metric(
    "Median Package",
    median_package
)

c4.metric(
    "Highest Package",
    highest_package
)

c5.metric(
    "Placement Quality Index",
    placement_quality_index
)

# ==================================================
# AI INSIGHTS
# ==================================================

st.subheader("AI Insights")

insights = []

if package_col:

    insights.append(
        f"Average package is {avg_package}"
    )

    insights.append(
        f"Highest package is {highest_package}"
    )

    insights.append(
        f"Median package is {median_package}"
    )

if total_records > 0:

    insights.append(
        f"{total_records} student records available."
    )

for i in insights:
    st.success(i)

# ==================================================
# PACKAGE DISTRIBUTION
# ==================================================

if package_col:

    st.subheader("Package Distribution")

    fig = px.histogram(
        filtered,
        x=package_col,
        nbins=20,
        title="Package Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# PROGRAM ANALYTICS
# ==================================================

if program_col:

    st.subheader("Program Analytics")

    prog = (
        filtered.groupby(program_col)
        .size()
        .reset_index(name="Students")
    )

    fig2 = px.bar(
        prog,
        x=program_col,
        y="Students",
        color=program_col,
        title="Program-wise Student Distribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ==================================================
# RECRUITER INTELLIGENCE
# ==================================================

company_col = None

for c in filtered.columns:

    if (
        "company" in c.lower()
        or
        "employer" in c.lower()
        or
        "recruiter" in c.lower()
    ):
        company_col = c
        break

if company_col:

    st.subheader("Recruiter Intelligence")

    recruiter = (
        filtered.groupby(company_col)
        .size()
        .reset_index(name="Hires")
        .sort_values(
            "Hires",
            ascending=False
        )
        .head(20)
    )

    fig3 = px.bar(
        recruiter,
        x=company_col,
        y="Hires",
        color="Hires",
        title="Top Recruiters"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# ==================================================
# DATA TABLE
# ==================================================

st.subheader("Filtered Dataset")

st.dataframe(
    filtered,
    use_container_width=True
)

# ==================================================
# DOWNLOAD
# ==================================================

csv = filtered.to_csv(index=False)

st.download_button(
    "Download Filtered Data",
    csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)