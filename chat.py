import streamlit as st
from pymongo import MongoClient
import pandas as pd
from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI

# Set your OpenAI API key
import os
os.environ["OPENAI_API_KEY"] = "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"

# MongoDB connection
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Database and collection
db = client["voyagesorganises"]  # Database name
collection = db["voyages"]       # Collection name

# Streamlit app
st.title("MongoDB Chatbot with LangChain")

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

    # Initialize the LangChain agent
    st.write("### Chat with your Data")
    llm = OpenAI(temperature=0)  # LLM setup
    agent = create_pandas_dataframe_agent(llm, df, verbose=True)

    # Chat interface
    user_input = st.text_input("Ask a question about the data:", "")

    if user_input:
        try:
            # Get response from the LangChain agent
            response = agent.run(user_input)
            st.write("### Response:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("No data found in the MongoDB collection.")