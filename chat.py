import streamlit as st
from pymongo import MongoClient
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Configure OpenAI API Key
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# MongoDB Connection
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Database and collection
db = client["voyagesorganises"]
collection = db["voyages"]

# Streamlit App Title
st.title("Conseiller IA pour Voyages Organisés")

@st.cache_data
def fetch_data():
    """Fetch data from MongoDB and convert it into a Pandas DataFrame."""
    data = list(collection.find({}, {"_id": 0}))  # Exclude "_id"
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data

# Fetch data from MongoDB
df = fetch_data()

if not df.empty:
    # Initialize LLM with LangChain
    llm = OpenAI(temperature=0)

    # Define a prompt template for interacting with the data
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

    # Define the LLMChain
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_query := st.chat_input("Posez une question sur les données :"):
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
