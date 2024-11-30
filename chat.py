import streamlit as st
from pymongo import MongoClient
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Configure OpenAI API key
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# MongoDB connection
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Database and collection
db = client["voyagesorganises"]  # Database name
collection = db["voyages"]       # Collection name

# Streamlit app title
st.title("Conseiller IA pour Voyages Organisés")

@st.cache_data
def fetch_data():
    """Fetch data from MongoDB and return as a Pandas DataFrame."""
    data = list(collection.find({}, {"_id": 0}))  # Exclude "_id" field
    return pd.DataFrame(data) if data else pd.DataFrame()

# Fetch data from MongoDB
df = fetch_data()

if not df.empty:
    # Initialize the LLM
    llm = OpenAI(temperature=0)

    # Define a custom prompt
    prompt_template = """
        Vous êtes un expert en voyages avec une connaissance approfondie du marché marocain. Vous avez accès aux données suivantes collectées à partir de la bibliothèque de publicités Meta :
        {data}

        Veuillez analyser les données et fournir une réponse détaillée à la question de l'utilisateur. Assurez-vous de mettre en évidence les tendances, les modèles de prix, les destinations populaires, les activités et d'autres informations importantes qui peuvent aider Ahmed à mieux organiser ses voyages au Maroc.

        Question de l'utilisateur : {question}
    """
    prompt = PromptTemplate(input_variables=["data", "question"], template=prompt_template)

    # Define the LLMChain
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input box for user message
    if user_input := st.chat_input("Posez une question sur les données :"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate a response using LLMChain
        try:
            response = llm_chain.run({"data": df.to_string(index=False), "question": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_message = f"Une erreur s'est produite : {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})

    # Show data overview
    st.write("### Aperçu des données")
    st.dataframe(df)
else:
    st.warning("Aucune donnée trouvée dans la collection MongoDB.")
