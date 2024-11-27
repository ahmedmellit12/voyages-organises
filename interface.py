import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_tags import st_tags

# Define the columns
columns = [
    "Nom de l'agence", "Site Web", "Contact", 
    "Titre du circuit", "Durée", "Prix par personne", 
    "Localisation de l'agence", "Destinations", "Activités", 
    "Hébergement",
]

# File path for the Excel file
output_file = "voyages_organisés.xlsx"

# Load or initialize the DataFrame
if Path(output_file).exists():
    df = pd.read_excel(output_file)
else:
    df = pd.DataFrame(columns=columns)

# Streamlit interface
st.title("Analyse du marché des voyages organisés - Saisie de données")

# Create a grid of two columns
col1, col2 = st.columns(2)

# Create input fields for each column, distributing them evenly
entry = {}
for i, column in enumerate(columns):
    if column in ["Hébergement", "Destinations", "Activités"]:
        with (col1 if i % 2 == 0 else col2):
            entry[column] = st_tags(
                label=column,
                value=[],
                suggestions=[],
                key=column
            )
    else:
        with (col1 if i % 2 == 0 else col2):
            entry[column] = st.text_input(column)

# Submit button
if st.button("Envoyer"):
    # Convert list fields to strings for saving to Excel
    for field in ["Hébergement", "Destinations", "Activités"]:
        entry[field] = ", ".join(entry[field])
    
    # Append the new entry to the DataFrame
    new_data = pd.DataFrame([entry])
    df = pd.concat([df, new_data], ignore_index=True)
    
    # Save the updated DataFrame to Excel
    df.to_excel(output_file, index=False)
    
    st.success("Données ajoutées avec succès !")
    st.write("Données mises à jour")
    st.dataframe(df)