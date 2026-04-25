import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.set_page_config(page_title="Bird Species Analysis", layout="wide")

@st.cache_data
def load_data():
    forest = pd.read_csv("Forestbirds.csv")
    grassland = pd.read_csv("grasslandbirds.csv")

    forest["Habitat"] = "Forest"
    grassland["Habitat"] = "Grassland"

    df = pd.concat([forest, grassland], ignore_index=True)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.strftime("%b")
    df["Sex"].fillna("Undetermined", inplace=True)
    df["Site_Name"].fillna("Unknown", inplace=True)
    df["Wind"] = df["Wind"].str.split("(").str[0].str.strip()

    df.drop_duplicates(inplace=True)
    return df

df = load_data()

conn = sqlite3.connect(":memory:", check_same_thread=False)
df.to_sql("observations", conn, if_exists="replace", index=False)

st.sidebar.header("Filters")

habitat_filter = st.sidebar.multiselect("Habitat", ["Forest", "Grassland"], default=["Forest", "Grassland"])
admin_filter = st.sidebar.multiselect("Admin Unit", sorted(df["Admin_Unit_Code"].unique()), default=sorted(df["Admin_Unit_Code"].unique()))
month_filter = st.sidebar.multiselect("Month", ["May", "Jun", "Jul"], default=["May", "Jun", "Jul"])

fdf = df[
    df["Habitat"].isin(habitat_filter) &
    df["Admin_Unit_Code"].isin(admin_filter) &
    df["Month"].isin(month_filter)
]

st.title("Bird Species Observation Analysis")
st.caption("Forest and Grassland Ecosystems - 2018")
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Observations", len(fdf))
col2.metric("Unique Species", fdf["Common_Name"].nunique())
col3.metric("Forest Species", fdf[fdf["Habitat"] == "Forest"]["Common_Name"].nunique())
col4.metric("Grassland Species", fdf[fdf["Habitat"] == "Grassland"]["Common_Name"].nunique())

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Overview", "Temporal", "Spatial", "Species",
    "Environment", "Distance and Behaviour", "Observers", "Conservation", "SQL"
])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Observations by Habitat")
        hab = fdf.groupby("Habitat").size().reset_index(name="Count")
        st.plotly_chart(px.pie(hab, names="Habitat", values="Count", hole=0.4), use_container_width=True)

    with c2:
        st.subheader("Species Richness by Habitat")
        sr = fdf.groupby("Habitat")["Common_Name"].nunique().reset_index(name="Species")
        st.plotly_chart(px.bar(sr, x="Habitat", y="Species", color="Habitat", text="Species"), use_container_width=True)

    st.subheader("Observations by Admin Unit")
    au = fdf.groupby(["Admin_Unit_Code", "Habitat"]).size().reset_index(name="Count")
    st.plotly_chart(px.bar(au, x="Admin_Unit_Code", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    st.subheader("Top 10 Most Observed Species")
    top10 = fdf["Common_Name"].value_counts().head(10).reset_index()
    top10.columns = ["Species", "Count"]
    st.plotly_chart(px.bar(top10.sort_values("Count"), x="Count", y="Species", orientation="h"), use_container_width=True)


with tab2:
    st.subheader("Daily Observations Over Time")
    daily = fdf.groupby(["Date", "Habitat"]).size().reset_index(name="Count")
    st.plotly_chart(px.line(daily, x="Date", y="Count", color="Habitat", markers=True), use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Monthly Observations")
        month_order = ["May", "Jun", "Jul"]
        mo = fdf.groupby(["Month", "Habitat"]).size().reset_index(name="Count")
        mo["Month"] = pd.Categorical(mo["Month"], categories=month_order, ordered=True)
        mo.sort_values("Month", inplace=True)
        st.plotly_chart(px.bar(mo, x="Month", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    with c2:
        st.subheader("Species Richness by Month")
        mo_sp = fdf.groupby(["Month", "Habitat"])["Common_Name"].nunique().reset_index(name="Species")
        mo_sp["Month"] = pd.Categorical(mo_sp["Month"], categories=month_order, ordered=True)
        mo_sp.sort_values("Month", inplace=True)
        st.plotly_chart(px.line(mo_sp, x="Month", y="Species", color="Habitat", markers=True), use_container_width=True)

    st.subheader("Visit Distribution")
    vis = fdf.groupby(["Visit", "Habitat"]).size().reset_index(name="Count")
    st.plotly_chart(px.bar(vis, x="Visit", y="Count", color="Habitat", barmode="group"), use_container_width=True)


with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Species Richness by Admin Unit")
        sr_au = fdf.groupby(["Admin_Unit_Code", "Habitat"])["Common_Name"].nunique().reset_index(name="Species")
        st.plotly_chart(px.bar(sr_au, x="Admin_Unit_Code", y="Species", color="Habitat", barmode="group"), use_container_width=True)

    with c2:
        st.subheader("Total Observations by Admin Unit")
        obs_au = fdf.groupby("Admin_Unit_Code").size().reset_index(name="Count").sort_values("Count")
        st.plotly_chart(px.bar(obs_au, x="Count", y="Admin_Unit_Code", orientation="h"), use_container_width=True)

    st.subheader("Admin Unit and Month Heatmap")
    hm = fdf.groupby(["Admin_Unit_Code", "Month"]).size().unstack(fill_value=0)
    hm = hm[[c for c in ["May", "Jun", "Jul"] if c in hm.columns]]
    st.plotly_chart(px.imshow(hm, color_continuous_scale="Greens", labels=dict(color="Observations")), use_container_width=True)

    st.subheader("Top 20 Active Plots")
    top_plots = fdf.groupby("Plot_Name").size().reset_index(name="Count").nlargest(20, "Count")
    st.plotly_chart(px.bar(top_plots, x="Plot_Name", y="Count"), use_container_width=True)


with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top 15 Species - Forest vs Grassland")
        top15 = fdf["Common_Name"].value_counts().head(15).index
        sp_hab = fdf[fdf["Common_Name"].isin(top15)].groupby(["Common_Name", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(sp_hab, x="Common_Name", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    with c2:
        st.subheader("ID Method Distribution")
        idm = fdf.groupby(["ID_Method", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(idm, x="ID_Method", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Sex Ratio")
        sex = fdf.groupby(["Sex", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(sex, x="Sex", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    with c4:
        st.subheader("Species Exclusive to Each Habitat")
        forest_sp = set(fdf[fdf["Habitat"] == "Forest"]["Common_Name"].unique())
        grass_sp = set(fdf[fdf["Habitat"] == "Grassland"]["Common_Name"].unique())
        venn = pd.DataFrame({
            "Category": ["Forest Only", "Both", "Grassland Only"],
            "Count": [len(forest_sp - grass_sp), len(forest_sp & grass_sp), len(grass_sp - forest_sp)]
        })
        st.plotly_chart(px.bar(venn, x="Category", y="Count", text="Count"), use_container_width=True)


with tab5:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Temperature Distribution")
        st.plotly_chart(px.histogram(fdf, x="Temperature", color="Habitat", barmode="overlay", nbins=30), use_container_width=True)

    with c2:
        st.subheader("Humidity Distribution")
        st.plotly_chart(px.histogram(fdf, x="Humidity", color="Habitat", barmode="overlay", nbins=30), use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Sky Conditions")
        sky = fdf.groupby(["Sky", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(sky, x="Sky", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    with c4:
        st.subheader("Wind Conditions")
        wind = fdf.groupby(["Wind", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(wind, x="Wind", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    st.subheader("Temperature vs Humidity")
    sample = fdf.sample(min(3000, len(fdf)), random_state=42)
    st.plotly_chart(px.scatter(sample, x="Temperature", y="Humidity", color="Habitat", opacity=0.5), use_container_width=True)

    st.subheader("Disturbance Effect")
    dist = fdf.groupby(["Disturbance", "Habitat"]).size().reset_index(name="Count")
    st.plotly_chart(px.bar(dist, x="Disturbance", y="Count", color="Habitat", barmode="group"), use_container_width=True)


with tab6:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Observation Distance by Habitat")
        dist_hab = fdf.groupby(["Distance", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(dist_hab, x="Distance", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    with c2:
        st.subheader("Flyover Observed")
        fly = fdf.copy()
        fly["Flyover"] = fly["Flyover_Observed"].map({True: "Yes", False: "No"})
        fly_grp = fly.groupby(["Flyover", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(fly_grp, x="Flyover", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    st.subheader("Top 15 Species Seen Within 50 Meters")
    close = fdf[fdf["Distance"] == "<= 50 Meters"]["Common_Name"].value_counts().head(15).reset_index()
    close.columns = ["Species", "Count"]
    st.plotly_chart(px.bar(close.sort_values("Count"), x="Count", y="Species", orientation="h"), use_container_width=True)


with tab7:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Observations per Observer")
        obs_cnt = fdf.groupby(["Observer", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(obs_cnt, x="Observer", y="Count", color="Habitat", barmode="group"), use_container_width=True)

    with c2:
        st.subheader("Unique Species per Observer")
        obs_sp = fdf.groupby(["Observer", "Habitat"])["Common_Name"].nunique().reset_index(name="Species")
        st.plotly_chart(px.bar(obs_sp, x="Observer", y="Species", color="Habitat", barmode="group"), use_container_width=True)

    st.subheader("Observer Activity Over Time")
    obs_time = fdf.groupby(["Date", "Observer"]).size().reset_index(name="Count")
    st.plotly_chart(px.line(obs_time, x="Date", y="Count", color="Observer", markers=True), use_container_width=True)

    st.subheader("Observer and Admin Unit Heatmap")
    obs_hm = fdf.groupby(["Observer", "Admin_Unit_Code"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(obs_hm, color_continuous_scale="Blues", labels=dict(color="Observations")), use_container_width=True)


with tab8:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Watchlist Status by Habitat")
        pif = fdf.copy()
        pif["Status"] = pif["PIF_Watchlist_Status"].map({True: "At-Risk", False: "Not At-Risk"})
        pif_grp = pif.groupby(["Status", "Habitat"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(pif_grp, x="Habitat", y="Count", color="Status", barmode="group"), use_container_width=True)

    with c2:
        st.subheader("Regional Stewardship by Admin Unit")
        rs = fdf[fdf["Regional_Stewardship_Status"] == True].groupby("Admin_Unit_Code").size().reset_index(name="Count").sort_values("Count")
        st.plotly_chart(px.bar(rs, x="Count", y="Admin_Unit_Code", orientation="h"), use_container_width=True)

    st.subheader("Most Observed At-Risk Species")
    atrisk = fdf[fdf["PIF_Watchlist_Status"] == True]["Common_Name"].value_counts().head(15).reset_index()
    atrisk.columns = ["Species", "Count"]
    st.plotly_chart(px.bar(atrisk.sort_values("Count"), x="Count", y="Species", orientation="h"), use_container_width=True)

    st.subheader("At-Risk Species Table")
    con_tbl = fdf[fdf["PIF_Watchlist_Status"] == True].groupby(
        ["Common_Name", "Scientific_Name", "Habitat"]
    ).agg(
        Observations=("Common_Name", "count"),
        Admin_Units=("Admin_Unit_Code", "nunique")
    ).reset_index().sort_values("Observations", ascending=False)
    st.dataframe(con_tbl, use_container_width=True)


with tab9:
    st.subheader("SQL Query Explorer")
    st.info("Table name: observations")

    presets = {
        "Top 10 species": "SELECT Common_Name, COUNT(*) AS Count FROM observations GROUP BY Common_Name ORDER BY Count DESC LIMIT 10;",
        "Species per habitat": "SELECT Habitat, COUNT(DISTINCT Common_Name) AS Species FROM observations GROUP BY Habitat;",
        "Observations by admin unit": "SELECT Admin_Unit_Code, COUNT(*) AS Count FROM observations GROUP BY Admin_Unit_Code ORDER BY Count DESC;",
        "At-risk species": "SELECT DISTINCT Common_Name, Scientific_Name FROM observations WHERE PIF_Watchlist_Status = 1;",
        "Observer stats": "SELECT Observer, COUNT(*) AS Observations, COUNT(DISTINCT Common_Name) AS Species FROM observations GROUP BY Observer;",
        "Sky vs observations": "SELECT Sky, COUNT(*) AS Count FROM observations GROUP BY Sky ORDER BY Count DESC;"
    }

    choice = st.selectbox("Pick a query or write your own", ["Custom"] + list(presets.keys()))
    default = presets.get(choice, "SELECT * FROM observations LIMIT 20;")
    query = st.text_area("SQL", value=default, height=100)

    if st.button("Run"):
        try:
            result = pd.read_sql_query(query, conn)
            st.write(f"{len(result)} rows returned")
            st.dataframe(result, use_container_width=True)
            num_cols = result.select_dtypes("number").columns.tolist()
            cat_cols = result.select_dtypes("object").columns.tolist()
            if cat_cols and num_cols:
                st.plotly_chart(px.bar(result, x=cat_cols[0], y=num_cols[0]), use_container_width=True)
        except Exception as e:
            st.error(str(e))

    with st.expander("Available columns"):
        st.write(list(df.columns))
