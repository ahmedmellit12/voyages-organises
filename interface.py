import streamlit as st
from pymongo import MongoClient
from streamlit_tags import st_tags
from typing import List, Any

# MongoDB connection setup
@st.cache_resource
def get_mongo_client():
    connection_string = (
        "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/"
        "?retryWrites=true&w=majority&appName=voyagesorganises"
    )
    return MongoClient(connection_string)

client = get_mongo_client()
db = client["voyagesorganises"]
collection = db["voyages"]

# Define fields and options
columns = [
    "Nom de l'agent", "Ad ID", "Nom de l'agence", "Site Web", "Contact",
    "Titre du circuit", "Durée", "Prix", "Localisation de l'agence", 
    "Destinations", "Activités", "Hébergement"
]
required_fields = [
    "Nom de l'agent", "Ad ID", "Nom de l'agence", "Contact",
    "Titre du circuit", "Durée", "Prix", "Localisation de l'agence"
]
agent_options = ["Sélectionner l'agent", "Achraf", "Abdelali", "Ahmed"]
tag_fields = ["Contact", "Hébergement", "Destinations", "Activités"]

# Helper functions
def validate_required_fields(entry: dict, required: List[str]) -> List[str]:
    """Validate required fields."""
    missing = [
        field for field in required
        if not entry.get(field) or (
            isinstance(entry[field], list) and not entry[field]
        ) or (
            isinstance(entry[field], str) and not entry[field].strip()
        )
    ]
    return missing

def format_list_fields(entry: dict, fields: List[str]) -> dict:
    """Convert list fields to comma-separated strings for storage."""
    for field in fields:
        if isinstance(entry.get(field), list):
            entry[field] = ", ".join(entry[field])
    return entry

# Streamlit app interface
st.title("Analyse du marché des voyages organisés - Saisie de données")

entry = {}

# Input fields
entry["Nom de l'agent"] = st.selectbox("Nom de l'agent", options=agent_options)

col1, col2 = st.columns(2)

for i, column in enumerate(columns[1:]):
    with (col1 if i % 2 == 0 else col2):
        if column in tag_fields:
            entry[column] = st_tags(label=column, value=[], suggestions=[], key=column)
        else:
            entry[column] = st.text_input(column)

# Submission
if st.button("Envoyer"):
    missing_fields = validate_required_fields(entry, required_fields)
    if entry["Nom de l'agent"] == "Sélectionner l'agent":
        missing_fields.append("Nom de l'agent")

    if missing_fields:
        st.error(f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}")
    else:
        entry = format_list_fields(entry, tag_fields)

        if collection.find_one({"Ad ID": entry["Ad ID"], "Prix": entry["Prix"]}):
            st.error(
                f"La combinaison de l'Ad ID {entry['Ad ID']} et du Prix {entry['Prix']} existe déjà."
            )
        else:
            collection.insert_one(entry)
            st.success("Données ajoutées avec succès !")

            all_data = list(collection.find({}, {"_id": 0}))
            st.write("Données mises à jour")
            st.dataframe(all_data)
