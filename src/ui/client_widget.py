from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFrame, QMessageBox,
                           QTextEdit)
from PyQt6.QtCore import Qt
from ..models.client import Client
from ..database.db_manager import DatabaseManager
from .components.modern_table import ModernTable

class ClientWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.editing_id = None  # Track which record we're editing
        self.init_ui()
        self.load_clients()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Form section
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)

        # Business Name input (required)
        business_layout = QHBoxLayout()
        self.business_label = QLabel("Business Name*:")
        self.business_input = QLineEdit()
        self.business_input.setPlaceholderText("Business name (required)")
        business_layout.addWidget(self.business_label)
        business_layout.addWidget(self.business_input)
        
        # POC (Point of Contact) input
        poc_layout = QHBoxLayout()
        self.poc_label = QLabel("Point of Contact:")
        self.poc_input = QLineEdit()
        self.poc_input.setPlaceholderText("Contact person (optional)")
        poc_layout.addWidget(self.poc_label)
        poc_layout.addWidget(self.poc_input)
        
        # Email input (required)
        email_layout = QHBoxLayout()
        self.email_label = QLabel("Email*:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address (required)")
        email_layout.addWidget(self.email_label)
        email_layout.addWidget(self.email_input)
        
        # Phone input
        phone_layout = QHBoxLayout()
        self.phone_label = QLabel("Phone Number:")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone number (optional)")
        phone_layout.addWidget(self.phone_label)
        phone_layout.addWidget(self.phone_input)
        
        # Address input
        address_layout = QVBoxLayout()
        self.address_label = QLabel("Address:")
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Physical address (optional)")
        self.address_input.setMaximumHeight(80)
        address_layout.addWidget(self.address_label)
        address_layout.addWidget(self.address_input)

        # Add button
        self.add_button = QPushButton("Add Client")
        self.add_button.setProperty("class", "success")
        self.add_button.clicked.connect(self.add_client)

        # Add layouts to form
        layouts = [business_layout, poc_layout, email_layout, phone_layout]
        for layout in layouts:
            form_layout.addLayout(layout)
        form_layout.addLayout(address_layout)
        form_layout.addWidget(self.add_button)

        # Add form frame to main layout
        main_layout.addWidget(form_frame)

        # Add table
        headers = ["Business Name", "Contact Person", "Email", "Phone", "Address"]
        self.client_table = ModernTable(headers, with_actions=True)
        self.client_table.edit_clicked.connect(self.edit_client)
        self.client_table.delete_clicked.connect(self.delete_client)
        main_layout.addWidget(QLabel("Client Directory"))
        main_layout.addWidget(self.client_table)
        
        self.setLayout(main_layout)

    def load_clients(self):
        session = self.db_manager.get_session()
        try:
            # Clear existing table
            self.client_table.clear_table()
            
            # Load all client records
            clients = session.query(Client).all()
            for client in clients:
                client_data = {
                    'Business Name': client.business_name,
                    'Contact Person': client.poc or '-',
                    'Email': client.email,
                    'Phone': client.phone or '-',
                    'Address': client.address or '-',
                    'ID': client.id
                }
                self.client_table.add_row(client_data, client.id)
        finally:
            session.close()

    def add_client(self):
        # Validate required fields
        business_name = self.business_input.text().strip()
        email = self.email_input.text().strip()
        
        if not business_name:
            self.business_input.setStyleSheet("border: 1px solid red;")
            QMessageBox.warning(self, "Validation Error", "Business Name is required")
            return
            
        if not email:
            self.email_input.setStyleSheet("border: 1px solid red;")
            QMessageBox.warning(self, "Validation Error", "Email is required")
            return
            
        # Get optional fields
        poc = self.poc_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.toPlainText().strip()
        
        session = self.db_manager.get_session()
        
        try:
            if self.editing_id:  # Update existing record
                client = session.query(Client).get(self.editing_id)
                if client:
                    client.business_name = business_name
                    client.poc = poc
                    client.email = email
                    client.phone = phone
                    client.address = address
                    
                    # Update display
                    session.commit()
                    
                    # Reset editing state
                    self.clear_form()
                    
                    # Refresh the table
                    self.load_clients()
            else:  # Create new record
                client = Client(
                    business_name=business_name,
                    poc=poc,
                    email=email,
                    phone=phone,
                    address=address
                )
                
                session.add(client)
                session.commit()
                
                # Get the ID assigned by the database
                client_data = {
                    'Business Name': client.business_name,
                    'Contact Person': client.poc or '-',
                    'Email': client.email,
                    'Phone': client.phone or '-',
                    'Address': client.address or '-',
                    'ID': client.id
                }
                
                # Add to display
                self.client_table.add_row(client_data, client.id)
                self.clear_form()
        finally:
            session.close()

    def edit_client(self, client_id):
        """Edit an existing client record"""
        session = self.db_manager.get_session()
        try:
            client = session.query(Client).get(client_id)
            if client:
                # Populate form with client data
                self.business_input.setText(client.business_name)
                self.poc_input.setText(client.poc or "")
                self.email_input.setText(client.email)
                self.phone_input.setText(client.phone or "")
                self.address_input.setText(client.address or "")
                
                # Set editing state
                self.editing_id = client_id
                self.add_button.setText("Update Client")
        finally:
            session.close()

    def delete_client(self, client_id):
        """Delete a client record"""
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this client?\nThis may affect income records associated with this client.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            session = self.db_manager.get_session()
            try:
                client = session.query(Client).get(client_id)
                if client:
                    session.delete(client)
                    session.commit()
                    
                    # Refresh the table
                    self.load_clients()
                    
                    # If we were editing this record, clear the form
                    if self.editing_id == client_id:
                        self.clear_form()
            finally:
                session.close()

    def clear_form(self):
        """Clear form fields and reset editing state"""
        self.business_input.clear()
        self.poc_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.business_input.setStyleSheet("")
        self.email_input.setStyleSheet("")
        self.editing_id = None
        self.add_button.setText("Add Client")
        
    def get_clients_for_dropdown(self):
        """Get all clients for use in dropdowns"""
        session = self.db_manager.get_session()
        try:
            clients = session.query(Client).all()
            return [(client.id, client.business_name) for client in clients]
        finally:
            session.close()