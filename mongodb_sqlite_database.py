import sqlite3
import re
import json
import os
import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient


class ContactManager:
    def __init__(self, master):
        self.master = master
        self.master.title("My Contacts")
        self.master.geometry("1080x500")  # Set initial size of the window

        # Allow the window to be resizable
        self.master.resizable(True, True)  # Set both width and height to be resizable

        # Connect to the SQLite database
        self.conn = sqlite3.connect("contacts.db")
        self.create_table()

        # Connect to MongoDB
        self.mongo_client = MongoClient(
            "mongodb+srv://Chris:13Guyver13@mongodbnetninja.pso3x.mongodb.net/?retryWrites=true&w=majority&appName=mongodbNetNinja"
        )
        self.mongo_db = self.mongo_client["test"]
        self.mongo_collection = self.mongo_db["Contacts"]

        # Create UI elements
        self.create_widgets()

        # Set default colors
        self.set_widget_colors("#000000", "#ff0000")  # Change colors here

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                date_of_birth TEXT,
                street_address TEXT,
                postal_code TEXT,
                state_or_province TEXT,
                country TEXT,
                email TEXT UNIQUE,
                phone_number TEXT,
                notes TEXT
            )
        """
        )
        self.conn.commit()

    def create_widgets(self):
        # Input fields
        labels = [
            "First Name:",
            "Last Name:",
            "Date of Birth (YYYY-MM-DD):",
            "Street Address:",
            "Postal Code:",
            "State/Province:",
            "Country:",
            "Email:",
            "Phone Number (---)--- ----:",
            "Notes:",
        ]
        self.entries = []

        # Create entry fields
        for i, label in enumerate(labels):
            row = i // 3  # Determine the row number
            column = i % 3  # Determine the column number

            if label == "Notes:":
                tk.Label(self.master, text=label).grid(
                    row=row,
                    column=column * 2,
                    padx=(20, 0),
                    pady=5,
                    sticky="e",  # Changed padx to 20
                )
                entry = tk.Text(self.master, height=5, width=125)  # Adjusted width
                entry.grid(
                    row=row, column=column * 2 + 1, padx=(0, 10), pady=5, columnspan=6
                )
            else:
                tk.Label(self.master, text=label).grid(
                    row=row,
                    column=column * 2,
                    padx=(20, 0),
                    pady=5,
                    sticky="e",  # Changed padx to 20
                )
                entry = tk.Entry(self.master, width=50)  # Adjusted width
                entry.grid(row=row, column=column * 2 + 1, padx=(0, 10), pady=5)
            self.entries.append(entry)

        # Buttons
        button_labels = [
            ("Add New Contact", self.add_new_entry),
            ("Export Contacts to JSON", self.export_to_json),
            ("Import Contacts from JSON", self.import_from_json),
            ("View All Contacts", self.view_contacts),
            ("Delete Contact", self.delete_contact),  # New delete button
            ("Clear Fields", self.clear_fields),  # New clear button
        ]

        # Calculate the maximum button width based on text length
        button_width = (
            max(len(text) for text, _ in button_labels) + 16
        )  # 8px padding on each side

        for i, (text, command) in enumerate(button_labels):
            button = tk.Button(
                self.master, text=text, command=command, width=button_width
            )
            button.grid(
                row=len(labels) // 2 + 1,
                column=i,
                padx=(10, 5),
                pady=10,
                sticky="ew",
            )

        # Configure grid weights for even spacing
        for i in range(len(button_labels)):
            self.master.grid_columnconfigure(i, weight=1)

        # Text widget for displaying contacts
        self.contact_display = tk.Text(
            self.master, height=15, width=150
        )  # Increased width
        self.contact_display.grid(
            row=len(labels) // 3 + 2,
            column=0,
            columnspan=6,
            padx=10,
            pady=10,
        )
        self.contact_display.config(state=tk.DISABLED)  # Make it read-only initially

    def set_widget_colors(self, bg_color, fg_color):
        """Set background and foreground colors for all widgets."""
        self.master.config(bg=bg_color)
        for entry in self.entries:
            entry.config(bg=bg_color, fg=fg_color)
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(bg=bg_color, fg=fg_color)
        # Set colors for the contact display
        self.contact_display.config(bg=bg_color, fg=fg_color)

    def add_new_entry(self):
        first_name = self.entries[0].get()
        last_name = self.entries[1].get()
        dob = self.entries[2].get()
        street_address = self.entries[3].get()
        postal_code = self.entries[4].get()
        state_or_province = self.entries[5].get()
        country = self.entries[6].get()
        email = self.entries[7].get()
        phone_number = self.entries[8].get()
        notes = self.entries[9].get("1.0", tk.END).strip()  # Get text from Text widget

        # Validate phone number format
        if not re.match(r"^\(\d{3}\)\d{3} \d{4}$", phone_number):
            messagebox.showerror(
                "Error",
                "Invalid format. Please enter the phone number in (---)--- ---- format.",
            )
            return

        new_contact = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "street_address": street_address,
            "postal_code": postal_code,
            "state_or_province": state_or_province,
            "country": country,
            "email": email,
            "phone_number": phone_number,
            "notes": notes,
        }

        # Insert into SQLite
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO Contacts (first_name, last_name, date_of_birth, street_address, postal_code, 
                state_or_province, country, email, phone_number, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    first_name,
                    last_name,
                    dob,
                    street_address,
                    postal_code,
                    state_or_province,
                    country,
                    email,
                    phone_number,
                    notes,
                ),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "A contact with this email already exists.")
            return

        # Insert into MongoDB
        self.mongo_collection.insert_one(new_contact)

        messagebox.showinfo("Success", f"Added new contact: {new_contact}")
        self.clear_fields()

    def clear_fields(self):
        for entry in self.entries:
            if isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)  # Clear Text widget
            else:
                entry.delete(0, tk.END)

    def export_to_json(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Contacts")
        contacts = cursor.fetchall()
        contact_list = []
        for contact in contacts:
            contact_dict = {
                "id": contact[0],
                "first_name": contact[1],
                "last_name": contact[2],
                "date_of_birth": contact[3],
                "street_address": contact[4],
                "postal_code": contact[5],
                "state_or_province": contact[6],
                "country": contact[7],
                "email": contact[8],
                "phone_number": contact[9],
                "notes": contact[10],
            }
            contact_list.append(contact_dict)

        filename = "contacts.json"
        with open(filename, "w") as json_file:
            json.dump(contact_list, json_file, indent=4)
        messagebox.showinfo("Success", f"Exported contacts to {filename}")

    def import_from_json(self):
        filename = "contacts.json"
        if os.path.exists(filename):
            with open(filename, "r") as json_file:
                contacts = json.load(json_file)
                for contact in contacts:
                    new_contact = {
                        "first_name": contact["first_name"],
                        "last_name": contact["last_name"],
                        "date_of_birth": contact["date_of_birth"],
                        "street_address": contact["street_address"],
                        "postal_code": contact["postal_code"],
                        "state_or_province": contact["state_or_province"],
                        "country": contact["country"],
                        "email": contact["email"],
                        "phone_number": contact["phone_number"],
                        "notes": contact["notes"],
                    }
                    try:
                        cursor = self.conn.cursor()
                        cursor.execute(
                            """
                            INSERT INTO Contacts (first_name, last_name, date_of_birth, street_address, postal_code, 
                            state_or_province, country, email, phone_number, notes) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                new_contact["first_name"],
                                new_contact["last_name"],
                                new_contact["date_of_birth"],
                                new_contact["street_address"],
                                new_contact["postal_code"],
                                new_contact["state_or_province"],
                                new_contact["country"],
                                new_contact["email"],
                                new_contact["phone_number"],
                                new_contact["notes"],
                            ),
                        )
                        self.mongo_collection.insert_one(
                            new_contact
                        )  # Insert into MongoDB
                    except sqlite3.IntegrityError:
                        continue  # Skip duplicates
                self.conn.commit()
            messagebox.showinfo("Success", f"Imported contacts from {filename}")
        else:
            messagebox.showerror("Error", f"{filename} does not exist.")

    def delete_contact(self):
        email = self.entries[7].get()  # Assuming email is used as the unique identifier
        if not email:
            messagebox.showerror("Error", "Please enter an email to delete a contact.")
            return

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Contacts WHERE email = ?", (email,))
        if cursor.rowcount > 0:
            self.conn.commit()
            self.mongo_collection.delete_one({"email": email})  # Delete from MongoDB
            messagebox.showinfo("Success", f"Deleted contact with email: {email}")
            self.clear_fields()  # Clear fields after deletion
        else:
            messagebox.showerror("Error", f"No contact found with email: {email}")

    def view_contacts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Contacts")
        contacts = cursor.fetchall()
        self.contact_display.config(state=tk.NORMAL)  # Enable editing
        self.contact_display.delete("1.0", tk.END)  # Clear previous content
        if contacts:
            contact_list = "\n".join(
                [
                    f"Name: {contact[1]} {contact[2]}\n"
                    f"Email: {contact[8]}\n"
                    f"Phone: {contact[9]}\n"
                    f"Address: {contact[4]}, {contact[5]}, {contact[6]}, {contact[7]}\n"
                    f"DOB: {contact[3]}\n"
                    f"Notes: {contact[10]}\n"
                    for contact in contacts
                ]
            )
            self.contact_display.insert(tk.END, contact_list)
        else:
            self.contact_display.insert(tk.END, "No contacts found.")
        self.contact_display.config(state=tk.DISABLED)  # Make it read-only again

    def close(self):
        self.conn.close()
        self.mongo_client.close()  # Close MongoDB connection
        self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactManager(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
