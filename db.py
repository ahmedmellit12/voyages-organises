import streamlit as st
from pymongo import MongoClient
import pandas as pd

# MongoDB Connection
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

# Fetch and cache data
@st.cache_data
def fetch_data():
    """Fetch data from MongoDB and return as a Pandas DataFrame."""
    data = list(collection.find({}, {"_id": 0}))
    return pd.DataFrame(data) if data else pd.DataFrame()

# Utility functions
def delete_record(ad_id: str, price: str) -> bool:
    """Delete a record based on Ad ID and Price."""
    result = collection.delete_one({"Ad ID": ad_id, "Prix": price})
    return result.deleted_count > 0

def update_record(ad_id: str, price: str, column: str, new_value: str) -> bool:
    """Update a record with a new value for a specific column."""
    if new_value.strip():
        result = collection.update_one(
            {"Ad ID": ad_id, "Prix": price},
            {"$set": {column: new_value}}
        )
        return result.modified_count > 0
    return False

# Streamlit App
st.title("Outil d'administration")

try:
    # Fetch data
    data = fetch_data()

    if not data.empty:
        # Display data
        st.write("### Aperçu des Données")
        st.dataframe(data)

        # Combine Ad ID and Price for selection
        if "Ad ID" in data.columns and "Prix" in data.columns:
            combined_options = [f"{row['Ad ID']} - {row['Prix']}" for _, row in data.iterrows()]

            # Delete Record
            st.write("### Supprimer un Enregistrement")
            selected_option_delete = st.selectbox(
                "Sélectionnez l'ID et le Prix de l'annonce à supprimer", 
                options=combined_options, 
                key="delete"
            )

            if st.button("Supprimer l'enregistrement sélectionné"):
                ad_id, price = selected_option_delete.split(" - ")
                if delete_record(ad_id, price):
                    st.success(f"Enregistrement avec l'ID '{ad_id}' et le Prix '{price}' supprimé avec succès!")
                    # Refresh data
                    data = fetch_data()
                    st.dataframe(data)
                else:
                    st.error(f"Échec de la suppression de l'enregistrement avec l'ID '{ad_id}' et le Prix '{price}'.")

            # Update Record
            st.write("### Modifier un Enregistrement")
            selected_option_edit = st.selectbox(
                "Sélectionnez l'ID et le Prix de l'annonce à modifier", 
                options=combined_options, 
                key="edit"
            )

            ad_id, price = selected_option_edit.split(" - ")
            record_to_edit = collection.find_one({"Ad ID": ad_id, "Prix": price}, {"_id": 0})
            st.write("Enregistrement Sélectionné :")
            st.json(record_to_edit)

            column_to_edit = st.selectbox("Sélectionnez une colonne à modifier", options=data.columns)
            new_value = st.text_input(f"Entrez la nouvelle valeur pour {column_to_edit}")

            if st.button("Mettre à jour l'enregistrement"):
                if update_record(ad_id, price, column_to_edit, new_value):
                    st.success(f"Enregistrement avec l'ID '{ad_id}' et le Prix '{price}' mis à jour avec succès!")
                    # Refresh data
                    data = fetch_data()
                    st.dataframe(data)
                else:
                    st.error(f"Aucun changement n'a été apporté à l'enregistrement avec l'ID '{ad_id}' et le Prix '{price}'.")
        else:
            st.error("Les colonnes requises 'Ad ID' et 'Prix' sont manquantes dans les données.")
    else:
        st.warning("Aucune donnée trouvée dans la collection MongoDB.")
except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")
