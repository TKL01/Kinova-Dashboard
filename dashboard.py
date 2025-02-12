###
# This streamlit app visualizes the data collected by OPCUA_LogClient_time.py at https://irolabkinova.streamlit.app/
# created by TKL
###

import streamlit as st
import pandas as pd
import altair as alt
import os

# Github repo raw links OLD without data folder:
# csv_file_options = {
#     "Kinova Log 0":'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/0_KinovaLog_joint_1.csv',
#     "Kinova Log 1": 'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/0_KinovaLog_joint_3.csv',
#     #'inova Log 2": 'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/2_KinovaLog.csv',
# }

# Github repo relative paths
# csv_file_options = {
#     "Kinova Log 0": "data/0_KinovaLog.csv",
#     "Kinova Log 1": "data/0_KinovaLog_joint_1.csv",
    
# }
# load csv files from data folder in github repo
###
# This streamlit app visualizes the data collected by OPCUA_LogClient_time.py at https://irolabkinova.streamlit.app/
# created by TKL
###

import streamlit as st
import pandas as pd
import altair as alt
import os

st.title("Robot Dashboard")

# define data folders for each robot
kinova_data_folder = "data/Kinova"
xarm_data_folder = "data/UFactory"

# Dropdown for robot selection
robot_options = {
    "Kinova": kinova_data_folder,
    "xArm6": xarm_data_folder
}
selected_robot = st.selectbox("Select a Robot:", list(robot_options.keys()))

# load CSV files from the selected robot's data folder
@st.cache_data
def list_csv_files(folder):
    return [f for f in os.listdir(folder) if f.endswith(".csv")]

# check files
# @st.cache_data
# def list_csv_files(folder):
#     files = os.listdir(folder)
#     st.write("Files in folder:", files)
#     csv_files = [f for f in files if f.endswith(".csv")]
#     st.write("CSV files:", csv_files)
#     return csv_files

# generate file paths for dropdown based on selected robot
data_folder = robot_options[selected_robot]
csv_files = list_csv_files(data_folder)
csv_file_options = {file_name: os.path.join(data_folder, file_name) for file_name in csv_files}

# Dropdown for file selection
selected_file = st.selectbox("Select a CSV file:", list(csv_file_options.keys()))

# get relative path for selected file
csv_file_path = csv_file_options[selected_file]

# load CSVs
@st.cache_data
def load_data_from_file(file_path):
    return pd.read_csv(file_path)

df = load_data_from_file(csv_file_path)

# display the selected file name
st.write(f"Selected file: {selected_file}")

# Option to upload a local CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = load_data_from_file(uploaded_file)

# display data
st.write("Contents of the CSV file:")
st.dataframe(df)

# extract stats, minmax, mean, std
st.write("Statistics Overview:")
st.write(df.describe())

# Dropdown for joint selection
joint_options = [f"Joint_{i}" for i in range(7)]  # Joint_0 to Joint_6
selected_joint = st.selectbox("Select a specific Joint:", joint_options)

# get joint number
joint_number = selected_joint.split("_")[1]

# define columns 
pos_col = f"Pos_{joint_number}"
temp_col = f"Temp_{joint_number}"
torque_col = f"Torque_{joint_number}"
current_col = f"Current_{joint_number}"
velocity_col = f"Velocity_{joint_number}"
time_col = df.columns[0]  # time is the first column

# time span filter
time_min, time_max = st.slider(
    "Select Time Range",
    min_value=float(df[time_col].min()),
    max_value=float(df[time_col].max()),
    value=(float(df[time_col].min()), float(df[time_col].max()))
)

# filter and display data based on slider
df_filtered = df[(df[time_col] >= time_min) & (df[time_col] <= time_max)]

# layout for diagrams
st.write(f"Diagrams for {selected_joint}:")
col1, col2 = st.columns(2)

# Function to plot charts
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

# show diagrams in two columns
with col1:
    st.altair_chart(plot_chart(df_filtered, time_col, pos_col, "Time [s]", "Position [deg]"))
    st.altair_chart(plot_chart(df_filtered, time_col, torque_col, "Time [s]", "Torque [Nm]"))

with col2:
    st.altair_chart(plot_chart(df_filtered, time_col, temp_col, "Time [s]", "Temperature [°C]"))
    st.altair_chart(plot_chart(df_filtered, time_col, current_col, "Time [s]", "Current [A]"))

# show full-width diagram for velocity
st.altair_chart(plot_chart(df_filtered, time_col, velocity_col, "Time [s]", "Velocity [deg/s]"))

# Stats for joint selected
st.write(f"Statistics for {selected_joint}:")
stats = df_filtered[[time_col, pos_col, temp_col, torque_col, current_col, velocity_col]].describe()
st.dataframe(stats)


#axis labels
ylabel_map = {
    pos_col: "Position [deg]",
    temp_col: "Temperature [°C]",
    torque_col: "Torque [Nm]",
    current_col: "Current [A]",
    velocity_col: "Velocity [deg/s]",
}

##view selected joint in single diagram

# selected_y_col = st.selectbox("Select Parameter for detailed View:", list(ylabel_map.keys()))
# selected_y_label = ylabel_map[selected_y_col]

# Single detailed diagram
# st.write(f"Detailed View: {selected_y_label}")
# st.altair_chart(plot_chart(df_filtered, time_col, selected_y_col, "Time [s]", selected_y_label))





