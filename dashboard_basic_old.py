import streamlit as st
import pandas as pd
import altair as alt

# Kinova Dashboard
st.title("Kinova Dashboard")

# Path to CSV file
csv_file_path = 'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/0_KinovaLog.csv'

# Read CSV
df = pd.read_csv(csv_file_path)

# Show CSV
st.write("Contents of the CSV file:")
st.dataframe(df)

# Summary of stats
st.write("Stats:")
st.write(df.describe())

# Dropdown for selecting the joint
joint_options = [f"Joint_{i}" for i in range(7)]  # Joint_0 to Joint_6
selected_joint = st.selectbox("Select a specific Joint:", joint_options)

#extracting the joint number from the selected option
joint_number = selected_joint.split("_")[1]

#olumns for the selected joint
pos_col = f"Pos_{joint_number}"
temp_col = f"Temp_{joint_number}"
torque_col = f"Torque_{joint_number}"
current_col = f"Current_{joint_number}"
velocity_col = f"Velocity_{joint_number}"
time_col = df.columns[0]  # time column first

# altair/streamlit line charts
def plot_chart(data, x, y, xlabel, ylabel):
    chart = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X(x, title=xlabel),
            y=alt.Y(y, title=ylabel),
        )
        .properties(width=700, height=400)
    )
    st.altair_chart(chart)

# time column is numeric
df[time_col] = pd.to_numeric(df[time_col], errors='coerce')

# display plots
plot_chart(df, time_col, pos_col, "Time [s]", "Position [deg]")
plot_chart(df, time_col, temp_col, "Time [s]", "Temperature [°C]")
plot_chart(df, time_col, torque_col, "Time [s]", "Torque [Nm]")
plot_chart(df, time_col, current_col, "Time [s]", "Current [A]")
plot_chart(df, time_col, velocity_col, "Time [s]", "Velocity [deg/s]")