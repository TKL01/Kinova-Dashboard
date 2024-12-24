import streamlit as st
import pandas as pd
import altair as alt


st.title("Kinova Dashboard")

# Github repo raw links
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

data_folder = "data/"
@st.cache_data
def list_csv_files(folder):
    return [f for f in os.listdir(folder) if f.endswith(".csv")]

# Generate file paths for dropdown
csv_files = list_csv_files(data_folder)
csv_file_options = {file_name: os.path.join(data_folder, file_name) for file_name in csv_files}

# Dropdown for file selection
selected_file = st.selectbox("Select a CSV file:", list(csv_file_options.keys()))

# Get the relative path for the selected file
csv_file_path = csv_file_options[selected_file]

# Load data
@st.cache_data
def load_data_from_file(file_path):
    return pd.read_csv(file_path)

df = load_data_from_file(csv_file_path)

# Display the selected file name
st.write(f"Selected file: {selected_file}")

# Option to upload a local csv file
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

# get joint no.#
joint_number = selected_joint.split("_")[1]

# define columns 
pos_col = f"Pos_{joint_number}"
temp_col = f"Temp_{joint_number}"
torque_col = f"Torque_{joint_number}"
current_col = f"Current_{joint_number}"
velocity_col = f"Velocity_{joint_number}"
time_col = df.columns[0]  # Time is the first column

# time span filter
time_min, time_max = st.slider(
    "Select Time Range",
    min_value=float(df[time_col].min()),
    max_value=float(df[time_col].max()),
    value=(float(df[time_col].min()), float(df[time_col].max()))
)

# filter and display data
df_filtered = df[(df[time_col] >= time_min) & (df[time_col] <= time_max)]

# Layout for diagrams
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

# Show diagrams in two columns
with col1:
    st.altair_chart(plot_chart(df_filtered, time_col, pos_col, "Time [s]", "Position [deg]"))
    st.altair_chart(plot_chart(df_filtered, time_col, torque_col, "Time [s]", "Torque [Nm]"))

with col2:
    st.altair_chart(plot_chart(df_filtered, time_col, temp_col, "Time [s]", "Temperature [°C]"))
    st.altair_chart(plot_chart(df_filtered, time_col, current_col, "Time [s]", "Current [A]"))

# Show full-width diagram, DOES NOT WORK YET
st.altair_chart(plot_chart(df_filtered, time_col, velocity_col, "Time [s]", "Velocity [deg/s]"))

# stats for joint selected
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


# selected_y_col = st.selectbox("Select Parameter for detailed View:", list(ylabel_map.keys()))
# selected_y_label = ylabel_map[selected_y_col]

# Single detailed diagram
# st.write(f"Detailed View: {selected_y_label}")
# st.altair_chart(plot_chart(df_filtered, time_col, selected_y_col, "Time [s]", selected_y_label))





