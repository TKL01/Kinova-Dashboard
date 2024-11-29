import streamlit as st
import pandas as pd

# Kinova Dashboard
st.title("Kinova Dashboard")

# path to CSV file
csv_file_path = '/home/student/Kinova Temperature/DataLogger/0_KinovaLog.csv'  

# Read CSV
df = pd.read_csv(csv_file_path)

# Show first row of the CSV
st.write("Contents of the CSV file:")
st.dataframe(df)

# Stats
st.write("Stats:")
st.write(df.describe())

# Line chart
if st.checkbox("Diagram:"):
    st.line_chart(df)

