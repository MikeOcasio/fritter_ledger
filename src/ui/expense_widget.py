from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QDateEdit,
                           QComboBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from .components.card_table import CardTable
from ..models.expense import Expense
from ..models.receipt import Receipt
from ..database.db_manager import DatabaseManager
from .components.modern_table import ModernTable

class ExpenseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.editing_id = None  # Track which record we're editing
        self.init_ui()
        self.load_expenses()
        self.receipt_reference = None

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
        
        # Description input
        desc_layout = QHBoxLayout()
        self.desc_label = QLabel("Description:")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Enter expense description")
        desc_layout.addWidget(self.desc_label)
        desc_layout.addWidget(self.desc_input)
        
        # Category dropdown
        cat_layout = QHBoxLayout()
        self.cat_label = QLabel("Category:")
        self.cat_input = QComboBox()
        self.cat_input.addItems([
            "Software",
            "Transportation",
            "Utilities",
            "Services",
            "Food",
            "Other"
        ])
        cat_layout.addWidget(self.cat_label)
        cat_layout.addWidget(self.cat_input)
        
        # Date picker
        date_layout = QHBoxLayout()
        self.date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_input)
        
        # Receipt reference dropdown
        receipt_layout = QHBoxLayout()
        self.receipt_label = QLabel("Receipt Reference:")
        self.receipt_input = QComboBox()  # Changed to combobox for dropdown
        self.receipt_input.setEditable(True)  # Allow typing for search
        self.receipt_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't add new items
        self.receipt_input.setPlaceholderText("Select a receipt reference")
        receipt_layout.addWidget(self.receipt_label)
        receipt_layout.addWidget(self.receipt_input)
        
        # Refresh button for receipt references
        self.refresh_receipts_btn = QPushButton("↻")
        self.refresh_receipts_btn.setToolTip("Refresh receipt list")
        self.refresh_receipts_btn.setFixedWidth(30)
        self.refresh_receipts_btn.clicked.connect(self.populate_receipt_references)
        receipt_layout.addWidget(self.refresh_receipts_btn)
        
        # Add expense button
        self.submit_button = QPushButton("Add Expense")
        self.submit_button.setProperty("class", "success")
        self.submit_button.clicked.connect(self.add_expense)
        
        # Add layouts to form
        layouts = [amount_layout, desc_layout, cat_layout, 
                  date_layout, receipt_layout]
        for layout in layouts:
            form_layout.addLayout(layout)
        
        form_layout.addWidget(self.submit_button)
        
        # Add form frame to main layout
        main_layout.addWidget(form_frame)
        
        # Add table
        headers = ["Amount", "Description", "Category", "Receipt Ref", "Date"]
        self.expense_table = ModernTable(headers, with_actions=True)
        self.expense_table.edit_clicked.connect(self.edit_expense)
        self.expense_table.delete_clicked.connect(self.delete_expense)
        table_label = QLabel("Recent Expenses")
        table_label.setProperty("class", "section-title")
        main_layout.addWidget(table_label)
        main_layout.addWidget(self.expense_table)
        
        self.setLayout(main_layout)
        
        # Populate receipt references
        self.populate_receipt_references()

    def populate_receipt_references(self):
        """Load all receipt references into the dropdown"""
        # Save current text if any
        current_text = self.receipt_input.currentText()
        
        # Clear existing items
        self.receipt_input.clear()
        
        # Add empty option first
        self.receipt_input.addItem("", None)
        
        session = self.db_manager.get_session()
        try:
            # Get all receipts ordered by most recent first
            receipts = session.query(Receipt).order_by(Receipt.date.desc()).all()
            
            for receipt in receipts:
                if receipt.reference_id:
                    display_text = f"{receipt.reference_id} - {receipt.name}"
                    self.receipt_input.addItem(display_text, receipt.reference_id)
            
            # Try to restore previous selection
            if current_text:
                index = self.receipt_input.findText(current_text, Qt.MatchFlag.MatchContains)
                if index >= 0:
                    self.receipt_input.setCurrentIndex(index)
                
        finally:
            session.close()

    def load_expenses(self):
        session = self.db_manager.get_session()
        try:
            # Clear existing table
            self.expense_table.clear_table()
            
            # Load all expenses
            expenses = session.query(Expense).all()
            for expense in expenses:
                expense_data = {
                    'Amount': f"${expense.amount:.2f}",
                    'Description': expense.description,
                    'Category': expense.category,
                    'Receipt Ref': expense.receipt_reference or '-',  # Display receipt reference
                    'Date': expense.date.strftime("%Y-%m-%d"),
                    'ID': expense.id
                }
                self.expense_table.add_row(expense_data, expense.id)
        finally:
            session.close()

    def add_expense(self):
        try:
            amount = float(self.amount_input.text())
            description = self.desc_input.text()
            category = self.cat_input.currentText()
            date = self.date_input.date().toPyDate()
            
            # Get receipt reference from dropdown
            receipt_ref = None
            if self.receipt_input.currentIndex() > 0:  # If not the empty selection
                receipt_ref = self.receipt_input.currentData()
                if not receipt_ref:  # If data isn't set but text is entered, try to parse
                    text = self.receipt_input.currentText()
                    if " - " in text:
                        receipt_ref = text.split(" - ")[0].strip()
            
            session = self.db_manager.get_session()
            
            try:
                if self.editing_id:  # Update existing record
                    expense = session.query(Expense).get(self.editing_id)
                    if expense:
                        expense.amount = amount
                        expense.description = description
                        expense.category = category
                        expense.date = date
                        expense.receipt_reference = receipt_ref  # Update receipt reference
                        
                        # Update display
                        session.commit()
                        
                        # Refresh the table
                        self.load_expenses()
                        
                        # Reset editing state
                        self.clear_form()
                else:  # Create new record
                    expense = Expense(
                        amount=amount,
                        description=description,
                        category=category,
                        date=date,
                        receipt_reference=receipt_ref  # Set receipt reference
                    )
                    
                    session.add(expense)
                    session.commit()
                    
                    # Add to display
                    expense_data = {
                        'Amount': f"${expense.amount:.2f}",
                        'Description': expense.description,
                        'Category': expense.category,
                        'Receipt Ref': expense.receipt_reference or '-',
                        'Date': expense.date.strftime("%Y-%m-%d"),
                        'ID': expense.id
                    }
                    self.expense_table.add_row(expense_data, expense.id)
                    
                    self.clear_form()
            finally:
                session.close()
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")

    def edit_expense(self, expense_id):
        session = self.db_manager.get_session()
        try:
            expense = session.query(Expense).get(expense_id)
            if expense:
                # Populate form with expense data
                self.amount_input.setText(str(expense.amount))
                self.desc_input.setText(expense.description)
                
                # Set category dropdown
                index = self.cat_input.findText(expense.category)
                if index >= 0:
                    self.cat_input.setCurrentIndex(index)
                
                # Set receipt reference dropdown
                if expense.receipt_reference:
                    ref_index = -1
                    for i in range(self.receipt_input.count()):
                        if self.receipt_input.itemData(i) == expense.receipt_reference:
                            ref_index = i
                            break
                    
                    if ref_index >= 0:
                        self.receipt_input.setCurrentIndex(ref_index)
                    else:
                        # If not found, add it to the dropdown
                        self.receipt_input.addItem(expense.receipt_reference, expense.receipt_reference)
                        self.receipt_input.setCurrentIndex(self.receipt_input.count() - 1)
                else:
                    self.receipt_input.setCurrentIndex(0)  # Empty selection
                
                # Set date
                date = QDate(expense.date.year, expense.date.month, expense.date.day)
                self.date_input.setDate(date)
                
                # Set editing state
                self.editing_id = expense_id
                self.submit_button.setText("Update Expense")
        finally:
            session.close()

    def delete_expense(self, expense_id):
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this expense?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            session = self.db_manager.get_session()
            try:
                expense = session.query(Expense).get(expense_id)
                if expense:
                    session.delete(expense)
                    session.commit()
                    
                    # Refresh the table
                    self.load_expenses()
                    
                    # If we were editing this record, clear the form
                    if self.editing_id == expense_id:
                        self.clear_form()
                        self.editing_id = None
                        self.submit_button.setText("Add Expense")
            finally:
                session.close()

    def clear_form(self):
        self.amount_input.clear()
        self.desc_input.clear()
        self.cat_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.receipt_input.setCurrentIndex(0)  # Reset to empty selection
        self.amount_input.setStyleSheet("")
        self.editing_id = None
        self.submit_button.setText("Add Expense")