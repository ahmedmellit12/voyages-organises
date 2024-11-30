import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Connexion à MongoDB
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Base de données et collection
db = client["voyagesorganises"]  # Nom de la base de données
collection = db["voyages"]       # Nom de la collection

# Titre de l'application
st.title("Visualiseur, Éditeur et Outil de Suppression de Données MongoDB")

try:
    # Récupérer les données de MongoDB
    data = list(collection.find({}, {"_id": 0}))  # Exclure le champ "_id"

    if data:
        # Convertir les données en DataFrame
        df = pd.DataFrame(data)

        # Afficher les données
        st.write("### Aperçu des Données")
        st.dataframe(df)

        # Combiner l'ID d'annonce et le prix pour la sélection
        if "Ad ID" in df.columns and "Prix" in df.columns:
            combined_options = [f"{row['Ad ID']} - {row['Prix']}" for _, row in df.iterrows()]
            
            # Permettre à l'utilisateur de supprimer un enregistrement
            st.write("### Supprimer un Enregistrement")
            selected_option_delete = st.selectbox("Sélectionnez l'ID et le Prix de l'annonce à supprimer", options=combined_options, key="delete")

            # Bouton pour confirmer la suppression
            # if st.button("Supprimer l'enregistrement sélectionné"):
            #     ad_id, price = selected_option_delete.split(" - ")
            #     result = collection.delete_one({"Ad ID": ad_id, "Prix": price})
            #     if result.deleted_count > 0:
            #         st.success(f"Enregistrement avec l'ID '{ad_id}' et le Prix '{price}' supprimé avec succès!")
            #     else:
            #         st.error(f"Échec de la suppression de l'enregistrement avec l'ID '{ad_id}' et le Prix '{price}'.")

                # Rafraîchir l'affichage des données
                # data = list(collection.find({}, {"_id": 0}))  # Récupérer les données mises à jour
                # if data:
                #     df = pd.DataFrame(data)
                #     st.dataframe(df)
                # else:
                #     st.warning("Aucune donnée restante dans la collection.")

            # Permettre à l'utilisateur de modifier un enregistrement
            st.write("### Modifier un Enregistrement")
            selected_option_edit = st.selectbox("Sélectionnez l'ID et le Prix de l'annonce à modifier", options=combined_options, key="edit")

            # Afficher l'enregistrement sélectionné
            ad_id, price = selected_option_edit.split(" - ")
            record_to_edit = collection.find_one({"Ad ID": ad_id, "Prix": price}, {"_id": 0})
            st.write("Enregistrement Sélectionné :")
            st.json(record_to_edit)

            # Choisir une colonne à modifier
            column_to_edit = st.selectbox("Sélectionnez une colonne à modifier", options=df.columns)

            # Saisir la nouvelle valeur
            new_value = st.text_input(f"Entrez la nouvelle valeur pour {column_to_edit}")

            # Bouton pour confirmer la modification
            if st.button("Mettre à jour l'enregistrement"):
                if new_value.strip():
                    # Mettre à jour l'enregistrement dans MongoDB
                    update_result = collection.update_one(
                        {"Ad ID": ad_id, "Prix": price},
                        {"$set": {column_to_edit: new_value}}
                    )
                    if update_result.modified_count > 0:
                        st.success(f"Enregistrement avec l'ID '{ad_id}' et le Prix '{price}' mis à jour avec succès!")
                    else:
                        st.error(f"Aucun changement n'a été apporté à l'enregistrement avec l'ID '{ad_id}' et le Prix '{price}'.")

                    # Rafraîchir l'affichage des données
                    data = list(collection.find({}, {"_id": 0}))  # Récupérer les données mises à jour
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.warning("Aucune donnée restante dans la collection.")
                else:
                    st.error("La nouvelle valeur ne peut pas être vide!")
        else:
            st.error("Les colonnes requises 'Ad ID' et 'Prix' sont manquantes dans les données.")
    else:
        st.warning("Aucune donnée trouvée dans la collection MongoDB.")
except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")
