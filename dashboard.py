import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Kinova Dashboard
st.title("Kinova Dashboard")

# path to CSV file
csv_file_path = 'https://raw.githubusercontent.com/TKL01/Kinova-Dashboard/refs/heads/main/0_KinovaLog.csv'  # raw github repo path for streamlit cloud  

# Read CSV
df = pd.read_csv(csv_file_path)

# Show first row of the CSV
st.write("Contents of the CSV file:")
st.dataframe(df)

# Stats
st.write("Stats:")
st.write(df.describe())

# Dropdown for selecting the joint
joint_options = [f"Joint_{i}" for i in range(7)]  # Joint_0 to Joint_6
selected_joint = st.selectbox("Select a specific Joint:", joint_options)

# Extracting the joint number from the selected option
joint_number = selected_joint.split("_")[1]

# line charts for the selected joint
st.write(f"Diagram for {selected_joint}:")

# Define the columns for the selected joint
pos_col = f"Pos_{joint_number}"
temp_col = f"Temp_{joint_number}"
torque_col = f"Torque_{joint_number}"
current_col = f"Current_{joint_number}"
velocity_col = f"Velocity_{joint_number}"
time_col = df.columns[0]  # first column is the time column

# create a line chart with labels
def plot_chart(x, y, xlabel, ylabel):
    plt.figure(figsize=(10, 4))
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    st.pyplot(plt)

# xy labels
plot_chart(df[time_col].values, df[pos_col].values, "Time [s]", "Position [deg]")
plot_chart(df[time_col].values, df[temp_col].values, "Time [s]", "Temperature [°C]")
plot_chart(df[time_col].values, df[torque_col].values, "Time [s]", "Torque [Nm]")
plot_chart(df[time_col].values, df[current_col].values, "Time [s]", "Current [A]")
plot_chart(df[time_col].values, df[velocity_col].values, "Time [s]", "Velocity [m/s]")
