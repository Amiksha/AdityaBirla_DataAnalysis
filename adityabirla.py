import pandas as pd
import streamlit as st

st.title("📊 Weekly Performance Dashboard")

# ================== FILE UPLOAD ==================
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ----- Date Handling -----
    df["Submitted date"] = pd.to_datetime(df["Submitted date"], errors="coerce")
    df["Start date"] = pd.to_datetime(df["Start date"], errors="coerce")

    # ----- Flags -----
    df["completed_flag"] = df["Submitted"].str.upper().eq("YES")
    df["completed_within_week"] = df["completed_flag"] & (
        (df["Submitted date"] - df["Start date"]).dt.days <= 7
    )

    # ----- Weekly Buckets -----
    df['week_start'] = df['Submitted date'] - pd.to_timedelta(df['Submitted date'].dt.weekday, unit='D')
    df['week_end'] = df['week_start'] + pd.Timedelta(days=6)

    # ================== DATE SELECTOR ==================
    start_date = st.date_input("📅 Select Start Date",
                               min_value=df["Submitted date"].min().date(),
                               max_value=df["Submitted date"].max().date())
    
    end_date = start_date + pd.Timedelta(days=6)
    st.success(f"📆 Reporting Window: {start_date} → {end_date}")

    # ================== Manager Filter Dropdown ==================
    manager_list = ["ALL Managers"] + sorted(df["L1 name"].dropna().unique().tolist())
    selected_manager = st.selectbox("👤 Select Manager (optional)", manager_list)

    # ================== FILTER DATA ==================
    filtered = df[(df["Submitted date"].dt.date >= start_date) &
                  (df["Submitted date"].dt.date <= end_date)]

    if selected_manager != "ALL Managers":
        filtered = filtered[filtered["L1 name"] == selected_manager]

    if filtered.empty:
        st.warning("⚠ No records found for this time window.")
        st.stop()

    # ================== AGENT WEEKLY SUMMARY ==================
    summary = filtered.groupby(["L1 name","User name"]).agg(
        modules_assigned=("Assessment id","nunique"),
        completed=("completed_flag","sum"),
        completed_within_week=("completed_within_week","sum"),
        avg_score=("Overall score","mean"),
        attempts=("No of attempts","sum")
    ).reset_index()

    st.subheader("📍 Weekly Summary (Agent-wise)")
    st.dataframe(summary, use_container_width=True)

else:
    st.info("⬆ Upload Excel file to begin analysis.")
