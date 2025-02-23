from pymongo import MongoClient
import re
import json
import os


def main():
    # Connect to the MongoDB server
    client = MongoClient("mongodb://localhost:27017/")

    # Create or connect to a database
    db = client["Contacts"]

    # Create or connect to a collection
    collection = db["contacts_collection"]

    # Function to add new entries
    def add_new_entry():
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")

        # Ensure dob is in YYYY-MM-DD format
        while True:
            dob = input("Enter date of birth (YYYY-MM-DD): ")
            if re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
                break
            else:
                print("Invalid format. Please enter the date in YYYY-MM-DD format.")

        street_address = input("Enter street address: ")
        postal_code = input("Enter postal code: ")
        state_or_province = input("Enter state or province: ")
        country = input("Enter country: ")
        email = input("Enter email: ")

        # Ensure phone number is in (---)--- ---- format
        while True:
            phone_number = input("Enter phone number: ")
            if re.match(r"^\(\d{3}\)\d{3} \d{4}$", phone_number):
                break
            else:
                print(
                    "Invalid format. Please enter the phone number in (---)--- ---- format."
                )

        notes = input("Enter any notes: ")  # New field for notes

        new_document = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "street_address": street_address,
            "postal_code": postal_code,
            "state_or_province": state_or_province,
            "country": country,
            "email": email,
            "phone_number": phone_number,
            "notes": notes,  # Add notes to the document
        }

        collection.insert_one(new_document)
        print(f"Added new document: {new_document}")

    # Function to export contacts to a JSON file
    def export_to_json(filename="contacts.json"):
        contacts = list(collection.find())
        for contact in contacts:
            contact["_id"] = str(
                contact["_id"]
            )  # Convert ObjectId to string for JSON serialization
        with open(filename, "w") as json_file:
            json.dump(contacts, json_file, indent=4)
        print(f"Exported contacts to {filename}")

    # Function to import contacts from a JSON file
    def import_from_json(filename="contacts.json"):
        if os.path.exists(filename):
            with open(filename, "r") as json_file:
                contacts = json.load(json_file)
                for contact in contacts:
                    contact["_id"] = None  # Remove _id to avoid duplicate key error
                    collection.insert_one(contact)
            print(f"Imported contacts from {filename}")
        else:
            print(f"{filename} does not exist.")

    # Add new entries
    while True:
        add_new_entry()
        cont = input("Do you want to add another entry? (yes/no): ")
        if cont.lower() != "yes":
            break

    # Export contacts to JSON
    export_to_json()

    # Import contacts from JSON
    import_choice = input("Do you want to import contacts from JSON? (yes/no): ")
    if import_choice.lower() == "yes":
        import_from_json()

    # Query the collection
    print("All documents in the collection:")
    for doc in collection.find():
        print(doc)

    # Close the connection
    client.close()


if __name__ == "__main__":
    main()
