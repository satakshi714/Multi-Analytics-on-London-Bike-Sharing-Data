import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Bike Dashboard", layout="wide")

# -----------------------------
# PREMIUM CSS
# -----------------------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0f172a, #020617);
}

/* Card */
.card {
    background: rgba(255, 255, 255, 0.05);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 15px;
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 15px 40px rgba(99,102,241,0.2);
}

/* Section spacing */
.section {
    margin-top: 25px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #020617;
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("london_merged.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.day
    df['weekday'] = df['timestamp'].dt.day_name()
    return df

df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("# 🚲 Bike Dashboard")
st.sidebar.markdown("### Premium Analytics")

page = st.sidebar.radio("", ["📊 Dashboard", "📁 Data", "ℹ️ About"])

st.sidebar.markdown("---")

# FILTER
st.sidebar.subheader("Filters")

min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()

date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

filtered_df = df[
    (df['timestamp'].dt.date >= date_range[0]) &
    (df['timestamp'].dt.date <= date_range[1])
]

weather_map = {
    1: "Clear",
    2: "Cloudy",
    3: "Light Rain",
    4: "Heavy Rain",
    7: "Snow"
}

filtered_df['weather'] = filtered_df['weather_code'].map(weather_map)

# -----------------------------
# CARD FUNCTION
# -----------------------------
def kpi_card(title, value):
    return f"""
    <div class="card">
        <p style="color:#9CA3AF; font-size:13px;">{title}</p>
        <h2>{value}</h2>
    </div>
    """

def chart_card(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "📊 Dashboard":

    st.markdown("# 🚲 London Bike Dashboard")
    st.markdown("### Clean, interactive analytics")

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(kpi_card("🚴 Total Rides", int(filtered_df['cnt'].sum())), unsafe_allow_html=True)
    col2.markdown(kpi_card("📈 Avg Rides", int(filtered_df['cnt'].mean())), unsafe_allow_html=True)
    col3.markdown(kpi_card("🌡️ Temperature", round(filtered_df['t1'].mean(), 2)), unsafe_allow_html=True)
    col4.markdown(kpi_card("💧 Humidity", round(filtered_df['hum'].mean(), 2)), unsafe_allow_html=True)

    st.markdown("<div class='section'></div>", unsafe_allow_html=True)

    # TREND SECTION
    st.subheader("📈 Ride Trends")

    fig1 = px.line(filtered_df, x="timestamp", y="cnt", color_discrete_sequence=["#6366F1"])
    chart_card(fig1)

    filtered_df = filtered_df.sort_values("timestamp")
    filtered_df['moving_avg'] = filtered_df['cnt'].rolling(24).mean()

    fig2 = px.line(filtered_df, x="timestamp", y=["cnt", "moving_avg"])
    chart_card(fig2)

    st.markdown("<div class='section'></div>", unsafe_allow_html=True)

    # IMPACT
    st.subheader("🌦️ Impact Factors")

    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.bar(filtered_df, x="weather", y="cnt", color="weather")
        chart_card(fig3)

    with col2:
        fig4 = px.scatter(filtered_df, x="t1", y="cnt", color="weather")
        chart_card(fig4)

    st.markdown("<div class='section'></div>", unsafe_allow_html=True)

    # PATTERNS
    st.subheader("⏰ Usage Patterns")

    hour_df = filtered_df.groupby("hour")["cnt"].mean().reset_index()
    fig5 = px.line(hour_df, x="hour", y="cnt", markers=True)
    chart_card(fig5)

    weekday_df = filtered_df.groupby("weekday")["cnt"].mean().reset_index()
    fig6 = px.bar(weekday_df, x="weekday", y="cnt", color="weekday")
    chart_card(fig6)

# -----------------------------
# DATA PAGE
# -----------------------------
elif page == "📁 Data":
    st.title("📁 Dataset")
    st.dataframe(filtered_df)

# -----------------------------
# ABOUT PAGE
# -----------------------------
else:
    st.title("ℹ️ About")

    st.write("""
    This dashboard provides insights into London bike sharing usage.

    Built with:
    - Streamlit
    - Plotly
    - Pandas
    """)