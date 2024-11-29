import streamlit as st
from pymongo import MongoClient
import pandas as pd

# MongoDB connection
connection_string = "mongodb+srv://honorablesvoyages:OJ5m95MyLHGqwOAN@voyagesorganises.x7xz0.mongodb.net/?retryWrites=true&w=majority&appName=voyagesorganises"
client = MongoClient(connection_string)

# Database and collection
db = client["voyagesorganises"]  # Database name
collection = db["voyages"]       # Collection name

# Title of the app
st.title("MongoDB Data Viewer")

try:
    # Fetch data from MongoDB
    data = list(collection.find({}, {"_id": 0}))  # Exclude the "_id" field

    if data:
        # Convert the data to a DataFrame
        df = pd.DataFrame(data)

        # Show the dataframe
        st.write("### Data Preview")
        st.dataframe(df)

        # Allow the user to select a row to delete
        st.write("### Delete a Record")
        if "Ad ID" in df.columns:
            ad_ids = df["Ad ID"].tolist()
            selected_ad_id = st.selectbox("Select Ad ID to delete", options=ad_ids)

            # Button to confirm deletion
            if st.button("Delete Selected Record"):
                # Delete the record from MongoDB
                result = collection.delete_one({"Ad ID": selected_ad_id})
                if result.deleted_count > 0:
                    st.success(f"Record with Ad ID '{selected_ad_id}' deleted successfully!")
                else:
                    st.error(f"Failed to delete the record with Ad ID '{selected_ad_id}'.")

                # Refresh the data display
                data = list(collection.find({}, {"_id": 0}))  # Fetch updated data
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.warning("No data left in the collection.")
        else:
            st.error("No 'Ad ID' column found in the data. Cannot delete records.")
    else:
        st.warning("No data found in the MongoDB collection.")
except Exception as e:
    st.error(f"An error occurred: {e}")
