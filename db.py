import streamlit as st
import pandas as pd

# Title of the app
st.title("Excel Data Viewer")

# Specify the Excel file name
file_name = "voyages_organisés.xlsx"

try:
    # Read the Excel file
    df = pd.read_excel(file_name)

    # Show the dataframe
    st.write("### Data Preview")
    st.dataframe(df)

    # Show basic statistics
    st.write("### Summary Statistics")
    st.write(df.describe())

except FileNotFoundError:
    st.error(f"The file '{file_name}' was not found in the directory.")
except Exception as e:
    st.error(f"An error occurred: {e}")
