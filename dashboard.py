import streamlit as st
import pandas as pd
import altair as alt

# Kinova Dashboard
st.title("Kinova Dashboard")

# load csv files with caching
@st.cache_data
def load_data_from_url(path):
    return pd.read_csv(path)

@st.cache_data
def load_data_from_file(file):
    return pd.read_csv(file)

# default csv file with github raw url
csv_file_path = 'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/0_KinovaLog.csv'
df = load_data_from_url(csv_file_path)

# Option to load local csv file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = load_data_from_file(uploaded_file)

# display csv file
st.write("Contents of the CSV file:")
st.dataframe(df)

# extract stats from csv
st.write("Stats:")
st.write(df.describe())

# Dropdown for joint selection
joint_options = [f"Joint_{i}" for i in range(7)]  # Joint_0 bis Joint_6
selected_joint = st.selectbox("Select a specific Joint:", joint_options)

# get joint number
joint_number = selected_joint.split("_")[1]

# define column for joint
pos_col = f"Pos_{joint_number}"
temp_col = f"Temp_{joint_number}"
torque_col = f"Torque_{joint_number}"
current_col = f"Current_{joint_number}"
velocity_col = f"Velocity_{joint_number}"
time_col = df.columns[0]  # time first column

# time span filter, change color with .toml
time_min, time_max = st.slider(
    "Select Time Range",
    min_value=float(df[time_col].min()),
    max_value=float(df[time_col].max()),
    value=(float(df[time_col].min()), float(df[time_col].max()))
)

# filter function
df_filtered = df[(df[time_col] >= time_min) & (df[time_col] <= time_max)]

# Layout for diagrams (2 columns)
st.write(f"Diagrams for {selected_joint}:")
col1, col2 = st.columns(2)

# Function to plot 
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

# show 2 colunns
with col1:
    st.altair_chart(plot_chart(df_filtered, time_col, pos_col, "Time [s]", "Position [deg]"))
    st.altair_chart(plot_chart(df_filtered, time_col, torque_col, "Time [s]", "Torque [Nm]"))

with col2:
    st.altair_chart(plot_chart(df_filtered, time_col, temp_col, "Time [s]", "Temperature [°C]"))
    st.altair_chart(plot_chart(df_filtered, time_col, current_col, "Time [s]", "Current [A]"))

# last diagram wide (does not work currently!)
st.altair_chart(plot_chart(df_filtered, time_col, velocity_col, "Time [s]", "Velocity [deg/s]"))

# advaanced stats
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

# single out joint diagram
st.write(f"Detailed View: {selected_y_label}")
st.altair_chart(plot_chart(df_filtered, time_col, selected_y_col, "Time [s]", selected_y_label))




