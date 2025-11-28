import pandas as pd
import streamlit as st

st.title("📊 Weekly Performance Dashboard")

# ------------------ FILE UPLOAD ------------------
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx","xls"])

if uploaded_file:

    # Read xls/xlsx correctly
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext == "xls":
        df = pd.read_excel(uploaded_file, engine="xlrd")
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    # ------------------ CLEAN DATES ------------------
    # Convert invalid submission dates (0000-00-00) to NaT
    df["Submitted date"] = df["Submitted date"].replace("0000-00-00 00:00:00", pd.NaT)
    df["Submitted date"] = pd.to_datetime(df["Submitted date"], errors="coerce")
    df["Start date"] = pd.to_datetime(df["Start date"], errors="coerce")

    # Completion status flag
    df["completion_status"] = df["Submitted"].apply(lambda x: "Completed" if str(x).upper()=="YES" else "Not Completed")

    # ------------------ WEEK INPUT ------------------
    start_date = st.date_input("📅 Select Week Start Date")
    end_date = start_date + pd.Timedelta(days=6)

    st.success(f"📆 Week Selected: **{start_date} → {end_date}**")

    # ------------------ MANAGER FILTER ------------------
    manager_option = ["All Managers"] + sorted(df["L1 name"].dropna().unique().tolist())
    selected_manager = st.selectbox("👤 Filter by Manager (Optional)", manager_option)

    # ------------------ WEEK FILTER CORE LOGIC ------------------
    weekly_data = df[
           # Completed users (within week)
           ((df["Submitted date"].dt.date >= start_date) & (df["Submitted date"].dt.date <= end_date))
        |
           # Not completed but assigned within the same week
           ((df["Submitted date"].isna()) & (df["Start date"].dt.date.between(start_date, end_date)))
    ]

    # Manager selection filter
    if selected_manager != "All Managers":
        weekly_data = weekly_data[weekly_data["L1 name"] == selected_manager]

    if weekly_data.empty:
        st.warning("⚠ No records available for this week/manager selection.")
        st.stop()

    # ------------------ SUMMARY OUTPUT ------------------
    summary = weekly_data.groupby(["L1 name","User name"]).agg(
        modules_assigned  = ("Assessment id","nunique"),
        completed         = ("completion_status", lambda x: (x=="Completed").sum()),
        not_completed     = ("completion_status", lambda x: (x=="Not Completed").sum()),
        avg_score         = ("Overall score","mean"),
        attempts          = ("No of attempts","sum")
    ).reset_index()

    st.subheader("📌 Weekly Summary (Completed + Pending Users)")
    st.dataframe(summary, use_container_width=True)

else:
    st.info("⬆ Upload Excel to generate weekly performance insights.")
