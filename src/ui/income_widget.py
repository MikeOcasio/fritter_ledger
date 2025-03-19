from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QDateEdit, QFrame)
from PyQt6.QtCore import Qt, QDate
from ..models.income import Income
from .components.card_table import CardTable
from datetime import datetime

class IncomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

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
        layouts = [amount_layout, source_layout, date_layout]
        for layout in layouts:
            form_layout.addLayout(layout)
        form_layout.addWidget(self.add_button)

        # Add form frame to main layout
        main_layout.addWidget(form_frame)

        # Add card table
        self.income_table = CardTable()
        main_layout.addWidget(QLabel("Income History"))
        main_layout.addWidget(self.income_table)

        self.setLayout(main_layout)

    def add_income(self):
        try:
            income_data = {
                'amount': float(self.amount_input.text()),
                'source': self.source_input.text(),
                'date': self.date_input.date().toPyDate()
            }
            
            # Add to card table
            self.income_table.add_card(income_data)
            
            # Clear form
            self.clear_form()
            
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")
            return

    def clear_form(self):
        self.amount_input.clear()
        self.source_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.amount_input.setStyleSheet("")