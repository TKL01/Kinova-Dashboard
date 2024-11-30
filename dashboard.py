import streamlit as st
import pandas as pd
import altair as alt

# Kinova Dashboard
st.title("Kinova Dashboard")

# Path to CSV file
csv_file_path = 'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/0_KinovaLog.csv'

# load data with caching
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data(csv_file_path)

# show CSV
st.write("Contents of the CSV file:")
st.dataframe(df)

# show stats/summary
st.write("Stats:")
st.write(df.describe())

# Dropdown Joints
joint_options = [f"Joint_{i}" for i in range(7)]  # Joint_0 to Joint_6
selected_joint = st.selectbox("Select a specific Joint:", joint_options)

# extract Joint number
joint_number = selected_joint.split("_")[1]

#  get columns for selected Joint
pos_col = f"Pos_{joint_number}"
temp_col = f"Temp_{joint_number}"
torque_col = f"Torque_{joint_number}"
current_col = f"Current_{joint_number}"
velocity_col = f"Velocity_{joint_number}"
time_col = df.columns[0]  # Time column is first

# Time span filter slider orange (#FFA500) add .streamlit/config.toml config file to change
time_min, time_max = st.slider(
    "Select Time Range",
    min_value=float(df[time_col].min()),
    max_value=float(df[time_col].max()),
    value=(float(df[time_col].min()), float(df[time_col].max()))
)

# filter data for specific time span
df_filtered = df[(df[time_col] >= time_min) & (df[time_col] <= time_max)]

# Layout plots
st.write(f"Diagrams for {selected_joint}:")
col1, col2 = st.columns(2)

# plot with altair/streamlit
def plot_chart(data, x, y, xlabel, ylabel):
    chart = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X(x, title=xlabel),
            y=alt.Y(y, title=ylabel),
            tooltip=[x, y]
        )
        .properties(width=350, height=300)
    )
    return chart

# create plots in columns next to each other
with col1:
    st.altair_chart(plot_chart(df_filtered, time_col, pos_col, "Time [s]", "Position [deg]"))
    st.altair_chart(plot_chart(df_filtered, time_col, torque_col, "Time [s]", "Torque [Nm]"))

with col2:
    st.altair_chart(plot_chart(df_filtered, time_col, temp_col, "Time [s]", "Temperature [°C]"))
    st.altair_chart(plot_chart(df_filtered, time_col, current_col, "Time [s]", "Current [A]"))

# last plot make full size since 5 are displayed
st.altair_chart(plot_chart(df_filtered, time_col, velocity_col, "Time [s]", "Velocity [deg/s]"))

# add advanced stats for selected joint
st.write(f"Advanced Statistics for {selected_joint}:")
stats = df_filtered[[time_col, pos_col, temp_col, torque_col, current_col, velocity_col]].describe()
st.dataframe(stats)

# dynamic xy labels
ylabel_map = {
    pos_col: "Position [deg]",
    temp_col: "Temperature [°C]",
    torque_col: "Torque [Nm]",
    current_col: "Current [A]",
    velocity_col: "Velocity [deg/s]",
}
selected_y_col = st.selectbox("Select Parameter for detailed View:", list(ylabel_map.keys()))
selected_y_label = ylabel_map[selected_y_col]

# Detailliertes Diagramm für ausgewählten Parameter
st.write(f"Detailed View: {selected_y_label}")
st.altair_chart(plot_chart(df_filtered, time_col, selected_y_col, "Time [s]", selected_y_label))



