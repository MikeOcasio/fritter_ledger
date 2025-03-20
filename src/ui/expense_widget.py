from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QDateEdit,
                           QComboBox, QFrame)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from .components.card_table import CardTable
from ..models.expense import Expense
from ..database.db_manager import DatabaseManager

class ExpenseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
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
        
        # Receipt reference
        receipt_layout = QHBoxLayout()
        self.receipt_label = QLabel("Receipt Reference:")
        self.receipt_input = QLineEdit()
        self.receipt_input.setPlaceholderText("Enter receipt ID from Receipts tab")
        receipt_layout.addWidget(self.receipt_label)
        receipt_layout.addWidget(self.receipt_input)
        
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
        
        # Add card table
        self.expense_table = CardTable()
        table_label = QLabel("Recent Expenses")
        table_label.setProperty("class", "section-title")
        main_layout.addWidget(table_label)
        main_layout.addWidget(self.expense_table)
        
        self.setLayout(main_layout)

    def load_expenses(self):
        session = self.db_manager.get_session()
        try:
            expenses = session.query(Expense).all()
            for expense in expenses:
                self.add_expense_card(expense)
        finally:
            session.close()

    def add_expense(self):
        try:
            # Create new session
            session = self.db_manager.get_session()
            
            expense = Expense(
                amount=float(self.amount_input.text()),
                description=self.desc_input.text(),
                category=self.cat_input.currentText(),
                date=self.date_input.date().toPyDate()
            )
            
            try:
                session.add(expense)
                session.commit()
                # Get the data before closing session
                expense_data = {
                    'Amount': f"${expense.amount:.2f}",
                    'Description': expense.description,
                    'Category': expense.category,
                    'Date': expense.date.strftime("%Y-%m-%d")
                }
                self.expense_table.add_card(expense_data)
                self.clear_form()
            except Exception as e:
                session.rollback()
                print(f"Error adding expense: {str(e)}")
            finally:
                session.close()
                
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")
            return

    def add_expense_card(self, expense):
        # Create new session for loading expense
        session = self.db_manager.get_session()
        try:
            # Merge the expense with the new session
            expense = session.merge(expense)
            self.expense_table.add_card({
                'Amount': f"${expense.amount:.2f}",
                'Description': expense.description,
                'Category': expense.category,
                'Date': expense.date.strftime("%Y-%m-%d")
            })
        finally:
            session.close()

    def clear_form(self):
        self.amount_input.clear()
        self.desc_input.clear()
        self.cat_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.receipt_input.clear()
        self.amount_input.setStyleSheet("")