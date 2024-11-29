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

        # Combine Ad ID and Price for selection
        if "Ad ID" in df.columns and "Prix" in df.columns:
            combined_options = [f"{row['Ad ID']} - {row['Prix']}" for _, row in df.iterrows()]
            
            # Allow the user to delete a record
            st.write("### Delete a Record")
            selected_option_delete = st.selectbox("Select Ad ID and Price to delete", options=combined_options, key="delete")

            # Button to confirm deletion
            if st.button("Delete Selected Record"):
                ad_id, price = selected_option_delete.split(" - ")
                result = collection.delete_one({"Ad ID": ad_id, "Prix": price})
                if result.deleted_count > 0:
                    st.success(f"Record with Ad ID '{ad_id}' and Price '{price}' deleted successfully!")
                else:
                    st.error(f"Failed to delete the record with Ad ID '{ad_id}' and Price '{price}'.")

                # Refresh the data display
                data = list(collection.find({}, {"_id": 0}))  # Fetch updated data
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.warning("No data left in the collection.")

            # Allow the user to modify a record
            st.write("### Modify a Record")
            selected_option_edit = st.selectbox("Select Ad ID and Price to modify", options=combined_options, key="edit")

            # Display the selected record
            ad_id, price = selected_option_edit.split(" - ")
            record_to_edit = collection.find_one({"Ad ID": ad_id, "Prix": price}, {"_id": 0})
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
                        {"Ad ID": ad_id, "Prix": price},
                        {"$set": {column_to_edit: new_value}}
                    )
                    if update_result.modified_count > 0:
                        st.success(f"Record with Ad ID '{ad_id}' and Price '{price}' successfully updated!")
                    else:
                        st.error(f"No changes were made to the record with Ad ID '{ad_id}' and Price '{price}'.")

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
            st.error("Required columns 'Ad ID' and 'Prix' are missing in the data.")
    else:
        st.warning("No data found in the MongoDB collection.")
except Exception as e:
    st.error(f"An error occurred: {e}")
