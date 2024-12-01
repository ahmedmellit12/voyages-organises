import streamlit as st
from pymongo import MongoClient
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Configure OpenAI API Key securely
@st.cache_resource
def get_openai_api_key():
    return st.secrets["openai"]["api_key"]

os.environ["OPENAI_API_KEY"] = get_openai_api_key()

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
    """Fetch data from MongoDB and return it as a Pandas DataFrame."""
    data = list(collection.find({}, {"_id": 0}))
    return pd.DataFrame(data) if data else pd.DataFrame()

# Initialize Streamlit App
# st.title("Consultant IA pour l'Analyse du Marché des Voyages Organisés")

# Fetch data
df = fetch_data()

if not df.empty:
    # Initialize LLM with LangChain
    llm = OpenAI(temperature=0)
    prompt_template = """
        Vous êtes un expert en intelligence concurrentielle et stratégique, avec une spécialisation dans le marché des voyages organisés au Maroc.  

        Les données suivantes ont été collectées par nos agents, Abdelali, Ahmed et Achraf de *Honorable Voyages*, via la bibliothèque de publicités Meta :  
        {data}  

        En combinant ces informations avec votre expertise approfondie du marché :  
        1. Identifiez les **tendances actuelles** dans le secteur.  
        2. Analysez les **modèles tarifaires** observés.  
        3. Mettez en lumière les **destinations et activités populaires**.  
        4. Proposez d'autres **insights stratégiques pertinents** pour optimiser l'offre et la stratégie de *Honorable Voyages*.  

        Votre analyse doit être concise (30 à 100 mots), directement exploitable par Ahmed, responsable des voyages organisés chez *Honorable Voyages*.  

        Question de l'utilisateur : {question}
    """
    prompt = PromptTemplate(input_variables=["data", "question"], template=prompt_template)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour, je suis un agent IA spécialisé en intelligence concurrentielle et stratégique dans le domaine du tourisme. Comment puis-je vous aider ?"}]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_query := st.chat_input("Posez votre question"):
        # Add user query to chat history
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate response using LangChain
        try:
            assistant_response = llm_chain.run({"data": df.to_string(index=False), "question": user_query})
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        except Exception as e:
            error_message = f"Une erreur s'est produite : {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            with st.chat_message("assistant"):
                st.error(error_message)
else:
    st.warning("Aucune donnée trouvée dans la collection MongoDB.")
