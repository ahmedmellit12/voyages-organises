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

        # Create a unique selection field combining "Ad ID" and "Price"
        if "Ad ID" in df.columns and "Prix" in df.columns:
            # Generate selection options as "Ad ID - Price"
            selection_options = df.apply(lambda row: f"{row['Ad ID']} - {row['Prix']}", axis=1).tolist()
            selected_record = st.selectbox("Select a record (Ad ID - Price)", options=selection_options)

            # Parse the selected value into Ad ID and Price
            if selected_record:
                selected_ad_id, selected_price = selected_record.split(" - ")

                # Display the selected record
                record_to_edit = collection.find_one({"Ad ID": selected_ad_id, "Prix": selected_price}, {"_id": 0})
                st.write("Selected Record:")
                st.json(record_to_edit)

                # Modify functionality
                st.write("### Modify the Record")
                column_to_edit = st.selectbox("Select Column to Modify", options=df.columns)
                new_value = st.text_input(f"Enter new value for {column_to_edit}")

                if st.button("Update Record"):
                    if new_value.strip():
                        # Update the record in MongoDB
                        update_result = collection.update_one(
                            {"Ad ID": selected_ad_id, "Prix": selected_price},
                            {"$set": {column_to_edit: new_value}}
                        )
                        if update_result.modified_count > 0:
                            st.success(f"Record with Ad ID '{selected_ad_id}' and Price '{selected_price}' successfully updated!")
                        else:
                            st.error(f"No changes were made to the record.")

                        # Refresh the data display
                        data = list(collection.find({}, {"_id": 0}))  # Fetch updated data
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.error("New value cannot be empty!")

                # Delete functionality
                st.write("### Delete the Record")
                if st.button("Delete Selected Record"):
                    delete_result = collection.delete_one({"Ad ID": selected_ad_id, "Prix": selected_price})
                    if delete_result.deleted_count > 0:
                        st.success(f"Record with Ad ID '{selected_ad_id}' and Price '{selected_price}' deleted successfully!")
                    else:
                        st.error(f"Failed to delete the record.")

                    # Refresh the data display
                    data = list(collection.find({}, {"_id": 0}))  # Fetch updated data
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.warning("No data left in the collection.")
        else:
            st.error("The required columns ('Ad ID', 'Prix') are missing in the database.")
    else:
        st.warning("No data found in the MongoDB collection.")
except Exception as e:
    st.error(f"An error occurred: {e}")
