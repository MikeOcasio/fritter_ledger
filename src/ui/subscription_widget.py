from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QComboBox, QDateEdit,
                           QFrame)
from PyQt6.QtCore import Qt, QDate
from ..models.subscription import Subscription
from .components.card_table import CardTable
from datetime import datetime

class SubscriptionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Form section
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)

        # Name input
        name_layout = QHBoxLayout()
        self.name_label = QLabel("Service Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Service name")
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_input)

        # Amount input
        amount_layout = QHBoxLayout()
        self.amount_label = QLabel("Amount ($):")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_layout.addWidget(self.amount_label)
        amount_layout.addWidget(self.amount_input)

        # Billing cycle
        cycle_layout = QHBoxLayout()
        self.cycle_label = QLabel("Billing Cycle:")
        self.cycle_input = QComboBox()
        self.cycle_input.addItems(["Monthly", "Yearly", "Quarterly"])
        cycle_layout.addWidget(self.cycle_label)
        cycle_layout.addWidget(self.cycle_input)

        # Next billing date
        date_layout = QHBoxLayout()
        self.date_label = QLabel("Next Billing:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_input)

        # Add button
        self.add_button = QPushButton("Add Subscription")
        self.add_button.setProperty("class", "success")
        self.add_button.clicked.connect(self.add_subscription)

        # Add layouts to form
        layouts = [name_layout, amount_layout, cycle_layout, date_layout]
        for layout in layouts:
            form_layout.addLayout(layout)
        form_layout.addWidget(self.add_button)

        # Add form frame to main layout
        main_layout.addWidget(form_frame)

        # Add card table
        self.subscription_table = CardTable()
        main_layout.addWidget(QLabel("Active Subscriptions"))
        main_layout.addWidget(self.subscription_table)

        self.setLayout(main_layout)

    def add_subscription(self):
        try:
            subscription_data = {
                'name': self.name_input.text(),
                'amount': float(self.amount_input.text()),
                'billing_cycle': self.cycle_input.currentText(),
                'next_billing': self.date_input.date().toPyDate()
            }
            
            # Add to card table
            self.subscription_table.add_card(subscription_data)
            
            # Clear form
            self.clear_form()
            
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")
            return

    def clear_form(self):
        self.name_input.clear()
        self.amount_input.clear()
        self.cycle_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.amount_input.setStyleSheet("")