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
st.title("MongoDB Data Viewer, Editor, and Deletion Tool")

try:
    # Fetch data from MongoDB
    data = list(collection.find({}, {"_id": 0}))  # Exclude the "_id" field

    if data:
        # Convert the data to a DataFrame
        df = pd.DataFrame(data)

        # Show the dataframe
        st.write("### Data Preview")
        st.dataframe(df)

        # Allow the user to delete a record
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

        # Allow the user to modify a specific record
        st.write("### Modify a Record")
        if "Ad ID" in df.columns:
            selected_ad_id = st.selectbox("Select Ad ID to modify", options=ad_ids, key="modify")

            # Display the selected record
            record_to_edit = collection.find_one({"Ad ID": selected_ad_id}, {"_id": 0})
            st.write("Selected Record:")
            st.json(record_to_edit)

            # Choose a column to modify
            column_to_edit = st.selectbox("Select Column to Modify", options=df.columns)

            # Input the new value
            new_value = st.text_input(f"Enter new value for {column_to_edit}")

            # Button to confirm modification
            if st.button("Update Record"):
                if new_value.strip():
                    # Update the record in MongoDB
                    update_result = collection.update_one(
                        {"Ad ID": selected_ad_id},
                        {"$set": {column_to_edit: new_value}}
                    )
                    if update_result.modified_count > 0:
                        st.success(f"Record with Ad ID '{selected_ad_id}' successfully updated!")
                    else:
                        st.error(f"No changes were made to the record with Ad ID '{selected_ad_id}'.")

                    # Refresh the data display
                    data = list(collection.find({}, {"_id": 0}))  # Fetch updated data
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.warning("No data left in the collection.")
                else:
                    st.error("New value cannot be empty!")
    else:
        st.warning("No data found in the MongoDB collection.")
except Exception as e:
    st.error(f"An error occurred: {e}")
