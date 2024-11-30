import streamlit as st
from pymongo import MongoClient
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Définissez votre clé API OpenAI à l'aide des secrets de Streamlit pour une meilleure sécurité
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# Connexion à MongoDB
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Base de données et collection
db = client["voyagesorganises"]  # Nom de la base de données
collection = db["voyages"]       # Nom de la collection

# Application Streamlit
st.title("Conseiller IA pour Voyages Organisés")

@st.cache_data
def fetch_data():
    """Récupère les données de MongoDB et les convertit en DataFrame Pandas."""
    data = list(collection.find({}, {"_id": 0}))  # Exclure le champ "_id"
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()  # Retourner un DataFrame vide si aucune donnée

# Récupération des données de la base MongoDB
df = fetch_data()

if not df.empty:
    # Initialiser le LLM de LangChain
    llm = OpenAI(temperature=0)

    # Définir un modèle d'invite personnalisé pour interagir avec les données
    prompt_template = """
            Vous êtes un expert en intelligence concurrentielle et stratégique, spécialisé dans le marché des voyages organisés au Maroc.  

            Les données suivantes ont été collectées par nos agents Abdelali et Achraf de *Honorable Voyages* via la bibliothèque de publicités Meta :  
            {data}  

            Analysez ces informations en combinant votre expertise et votre connaissance approfondie du marché. Fournissez une réponse claire et exploitable à la question de l'utilisateur.  
            Mettez en avant :  
            - Les tendances actuelles  
            - Les modèles tarifaires  
            - Les destinations et activités populaires  
            - Tout autre élément pertinent pour aider Ahmed, responsable des voyages organisés chez *Honorable Voyages*, à optimiser l'offre et la stratégie de l'entreprise.  

            Votre réponse doit être :  
            - **Concise** (entre 30 et 150 mots)  
            - **Clair, précis et structuré**  
            - **Basé sur les données fournies et votre expertise**  

            Question de l'utilisateur : {question}

    """

    prompt = PromptTemplate(input_variables=["data", "question"], template=prompt_template)

    # Définir le LLMChain
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Interface utilisateur pour poser une question
    user_input = st.text_input("Posez une question sur les données :", "")

    if user_input:
        try:
            # Exécuter LLMChain avec la question de l'utilisateur et les données
            response = llm_chain.run({"data": df.to_string(index=False), "question": user_input})
            st.write("### Réponse :")
            st.write(response)
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
    st.write("### Aperçu des données")
    st.dataframe(df)
else:
    st.warning("Aucune donnée trouvée dans la collection MongoDB.")
