import streamlit as st
from pymongo import MongoClient
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# MongoDB connection
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Database and collection
db = client["voyagesorganises"]  # Database name
collection = db["voyages"]       # Collection name

# Load OpenAI API key from secrets
import os
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

st.title("Chat with Your MongoDB Data")

@st.cache_data
def fetch_data():
    """Fetch data from MongoDB and convert it to a Pandas DataFrame."""
    data = list(collection.find({}, {"_id": 0}))  # Exclude the "_id" field
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data

# Load data from MongoDB
df = fetch_data()

if not df.empty:
    st.write("### Data Preview")
    st.dataframe(df)

    # Initialize LLM
    st.write("### Chat with your Data")
    llm = OpenAI(temperature=0)

    # Define a custom prompt template
    prompt_template = """
    You are an AI assistant with access to the following data:
    {data}

    Please answer the user's question:
    {question}
    """
    prompt = PromptTemplate(input_variables=["data", "question"], template=prompt_template)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # User input for questions
    user_input = st.text_input("Ask a question about the data:", "")

    if user_input:
        try:
            # Generate a response using LLMChain
            response = llm_chain.run({"data": df.to_string(), "question": user_input})
            st.write("### Response:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("No data found in the MongoDB collection.")
