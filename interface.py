import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_tags import st_tags

# Define the columns
columns = [
    "Nom de l'agent", "Ad ID", "Nom de l'agence", "Site Web", "Contact", "Titre du circuit", "Durée",
    "Prix", "Localisation de l'agence", "Destinations", "Activités", "Hébergement"
]

# File path for the Excel file
output_file = "voyages_organisés.xlsx"

# Load or initialize the DataFrame
if Path(output_file).exists():
    df = pd.read_excel(output_file)
else:
    df = pd.DataFrame(columns=columns)

# Define required fields
required_fields = [
    "Nom de l'agent", "Ad ID", "Nom de l'agence", "Contact", "Titre du circuit", "Durée", "Prix", "Localisation de l'agence"
]

# Predefined options for "Nom de l'agent"
agent_options = ["Sélectionner l'agent", "Achraf", "Abdelali", "Ahmed"]

# Streamlit interface
st.title("Analyse du marché des voyages organisés - Saisie de données")

# Add "Nom de l'agent" as the first field
entry = {}
entry["Nom de l'agent"] = st.selectbox("Nom de l'agent", options=agent_options)

# Create a grid of two columns
col1, col2 = st.columns(2)

tag_list = ["Contact", "Hébergement", "Destinations", "Activités"]

# Add other fields
for i, column in enumerate(columns[1:]):  # Skip "Nom de l'agent" as it's already handled
    if column in tag_list:
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
    # Validate required fields
    missing_fields = [
        field
        for field in required_fields
        if (isinstance(entry[field], list) and not entry[field])  # Check for empty lists
        or (isinstance(entry[field], str) and not entry[field].strip())  # Check for empty strings
    ]
    # Check if the agent is not selected
    if entry["Nom de l'agent"] == "Sélectionner l'agent":
        missing_fields.append("Nom de l'agent")
    
    if missing_fields:
        st.error(f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}")
    else:
        # Convert list fields to strings for saving to Excel
        for field in tag_list:
            entry[field] = ", ".join(entry[field])

        # Check if the combination of Ad ID and Prix already exists
        ad_id = entry["Ad ID"]
        price = entry["Prix"]
        if not df.empty and ((df["Ad ID"] == ad_id) & (df["Prix"] == price)).any():
            st.error(
                f"La combinaison de l'Ad ID {ad_id} et du Prix {price} existe déjà dans la base de données. Veuillez vérifier vos données."
            )
        else:
            # Append the new entry to the DataFrame
            new_data = pd.DataFrame([entry])
            df = pd.concat([df, new_data], ignore_index=True)
            
            # Save the updated DataFrame to Excel
            df.to_excel(output_file, index=False)
            
            st.success("Données ajoutées avec succès !")
            st.write("Données mises à jour")
            st.dataframe(df)
