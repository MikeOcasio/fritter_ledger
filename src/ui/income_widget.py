from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QDateEdit, QFrame, QMessageBox,
                           QComboBox)
from PyQt6.QtCore import Qt, QDate
from ..models.income import Income
from ..models.client import Client
from ..database.db_manager import DatabaseManager
from .components.modern_table import ModernTable
from datetime import datetime

class IncomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.editing_id = None  # Track which record we're editing
        self.init_ui()
        self.load_income()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Form section
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)

        # Amount input
        amount_layout = QHBoxLayout()
        self.amount_label = QLabel("Amount ($):")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_layout.addWidget(self.amount_label)
        amount_layout.addWidget(self.amount_input)

        # Source input
        source_layout = QHBoxLayout()
        self.source_label = QLabel("Source:")
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Income source")
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_input)
        
        # Client dropdown (instead of text input)
        client_layout = QHBoxLayout()
        self.client_label = QLabel("Client:")
        self.client_input = QComboBox()
        self.client_input.setEditable(True)  # Allow manual entry
        self.client_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # But don't add new items to dropdown
        self.populate_client_dropdown()
        client_layout.addWidget(self.client_label)
        client_layout.addWidget(self.client_input)
        
        # Refresh client button
        self.refresh_client_btn = QPushButton("↻")
        self.refresh_client_btn.setToolTip("Refresh client list")
        self.refresh_client_btn.setFixedWidth(30)
        self.refresh_client_btn.clicked.connect(self.populate_client_dropdown)
        client_layout.addWidget(self.refresh_client_btn)
        
        # Invoice ID input
        invoice_layout = QHBoxLayout()
        self.invoice_label = QLabel("Invoice ID:")
        self.invoice_input = QLineEdit()
        self.invoice_input.setPlaceholderText("Invoice ID (optional)")
        invoice_layout.addWidget(self.invoice_label)
        invoice_layout.addWidget(self.invoice_input)
        
        # Contract ID input
        contract_layout = QHBoxLayout()
        self.contract_label = QLabel("Contract ID:")
        self.contract_input = QLineEdit()
        self.contract_input.setPlaceholderText("Contract ID (optional)")
        contract_layout.addWidget(self.contract_label)
        contract_layout.addWidget(self.contract_input)
        
        # Status dropdown
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status:")
        self.status_input = QComboBox()
        self.status_input.addItems([
            "Received", 
            "Invoiced", 
            "Past Due", 
            "Delinquent", 
            "Pending"
        ])
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_input)

        # Date picker
        date_layout = QHBoxLayout()
        self.date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_input)

        # Add button
        self.add_button = QPushButton("Add Income")
        self.add_button.setProperty("class", "success")
        self.add_button.clicked.connect(self.add_income)

        # Add layouts to form
        layouts = [amount_layout, source_layout, client_layout, 
                  invoice_layout, contract_layout, status_layout, date_layout]
        for layout in layouts:
            form_layout.addLayout(layout)
        form_layout.addWidget(self.add_button)

        # Add form frame to main layout
        main_layout.addWidget(form_frame)

        # Add table with status column
        headers = ["Amount", "Source", "Client", "Invoice ID", "Contract ID", "Status", "Date"]
        self.income_table = ModernTable(headers, with_actions=True)
        self.income_table.edit_clicked.connect(self.edit_income)
        self.income_table.delete_clicked.connect(self.delete_income)
        main_layout.addWidget(QLabel("Income History"))
        main_layout.addWidget(self.income_table)
        
        self.setLayout(main_layout)
        
    def populate_client_dropdown(self):
        """Populate the client dropdown with all clients from the database"""
        # Save current text if any
        current_text = self.client_input.currentText()
        
        self.client_input.clear()
        
        # Add a blank option first
        self.client_input.addItem("", None)  # Empty item with None as user data
        
        # Get clients from database
        session = self.db_manager.get_session()
        try:
            clients = session.query(Client).order_by(Client.business_name).all()
            for client in clients:
                self.client_input.addItem(client.business_name, client.id)
                
            # Try to restore previous selection
            if current_text:
                index = self.client_input.findText(current_text)
                if index >= 0:
                    self.client_input.setCurrentIndex(index)
        finally:
            session.close()

    def load_income(self):
        session = self.db_manager.get_session()
        try:
            # Clear existing table
            self.income_table.clear_table()
            
            # Load all income records
            incomes = session.query(Income).all()
            for income in incomes:
                income_data = {
                    'Amount': f"${income.amount:.2f}",
                    'Source': income.source,
                    'Client': income.client or '-',
                    'Invoice ID': income.invoice_id or '-',
                    'Contract ID': income.contract_id or '-',
                    'Status': income.status or 'Pending',
                    'Date': income.date.strftime("%Y-%m-%d"),
                    'ID': income.id
                }
                self.income_table.add_row(income_data, income.id)
        finally:
            session.close()

    def add_income(self):
        try:
            amount = float(self.amount_input.text())
            source = self.source_input.text()
            
            # Get client from the dropdown or text input
            client = self.client_input.currentText()
            
            invoice_id = self.invoice_input.text()
            contract_id = self.contract_input.text()
            status = self.status_input.currentText()
            date = self.date_input.date().toPyDate()
            
            session = self.db_manager.get_session()
            
            try:
                if self.editing_id:  # Update existing record
                    income = session.query(Income).get(self.editing_id)
                    if income:
                        income.amount = amount
                        income.source = source
                        income.client = client
                        income.invoice_id = invoice_id
                        income.contract_id = contract_id
                        income.status = status
                        income.date = date
                        
                        # Update display
                        session.commit()
                        
                        # Reset editing state
                        self.clear_form()
                        
                        # Refresh the table
                        self.load_income()
                else:  # Create new record
                    income = Income(
                        amount=amount,
                        source=source,
                        client=client,
                        invoice_id=invoice_id,
                        contract_id=contract_id,
                        status=status,
                        date=date
                    )
                    
                    session.add(income)
                    session.commit()
                    
                    # Get the ID assigned by the database
                    income_data = {
                        'Amount': f"${income.amount:.2f}",
                        'Source': income.source,
                        'Client': income.client or '-',
                        'Invoice ID': income.invoice_id or '-',
                        'Contract ID': income.contract_id or '-',
                        'Status': income.status,
                        'Date': income.date.strftime("%Y-%m-%d"),
                        'ID': income.id
                    }
                    
                    # Add to display
                    self.income_table.add_row(income_data, income.id)
                    self.clear_form()
            finally:
                session.close()
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")
            return

    def edit_income(self, income_id):
        """Edit an existing income record"""
        session = self.db_manager.get_session()
        try:
            income = session.query(Income).get(income_id)
            if income:
                # Populate form with income data
                self.amount_input.setText(str(income.amount))
                self.source_input.setText(income.source)
                
                # Set client dropdown
                if income.client:
                    index = self.client_input.findText(income.client)
                    if index >= 0:
                        self.client_input.setCurrentIndex(index)
                    else:
                        # If not in dropdown, set it as text
                        self.client_input.setCurrentText(income.client)
                else:
                    self.client_input.setCurrentIndex(0)  # Empty option
                
                self.invoice_input.setText(income.invoice_id or "")
                self.contract_input.setText(income.contract_id or "")
                
                # Set status dropdown
                if income.status:
                    index = self.status_input.findText(income.status)
                    if index >= 0:
                        self.status_input.setCurrentIndex(index)
                else:
                    # Default to "Pending" if no status
                    index = self.status_input.findText("Pending")
                    if index >= 0:
                        self.status_input.setCurrentIndex(index)
                
                # Set date
                date = QDate(income.date.year, income.date.month, income.date.day)
                self.date_input.setDate(date)
                
                # Set editing state
                self.editing_id = income_id
                self.add_button.setText("Update Income")
        finally:
            session.close()

    def delete_income(self, income_id):
        """Delete an income record"""
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this income record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            session = self.db_manager.get_session()
            try:
                income = session.query(Income).get(income_id)
                if income:
                    session.delete(income)
                    session.commit()
                    
                    # Refresh the table
                    self.load_income()
                    
                    # If we were editing this record, clear the form
                    if self.editing_id == income_id:
                        self.clear_form()
            finally:
                session.close()

    def clear_form(self):
        """Clear form fields and reset editing state"""
        self.amount_input.clear()
        self.source_input.clear()
        self.client_input.setCurrentIndex(0)  # Set to empty
        self.invoice_input.clear()
        self.contract_input.clear()
        self.status_input.setCurrentIndex(0)  # Reset to first status
        self.date_input.setDate(QDate.currentDate())
        self.amount_input.setStyleSheet("")
        self.editing_id = None
        self.add_button.setText("Add Income")

    def highlight_record(self, record_id):
        """Highlight a specific record by ID when coming from search"""
        # Find the row with this ID
        row_index = None
        for row in range(self.income_table.rowCount()):
            item_id = self.income_table.item_id_for_row(row)
            if item_id == record_id:
                row_index = row
                break
        
        if row_index is not None:
            # Scroll to the row
            self.income_table.scrollToItem(self.income_table.item(row_index, 0))
            
            # Select the row
            self.income_table.selectRow(row_index)
            
            # Flash highlight animation (implemented in ModernTable)
            self.income_table.flash_highlight_row(row_index)
            
            # Load the record in edit form
            self.edit_income(record_id)