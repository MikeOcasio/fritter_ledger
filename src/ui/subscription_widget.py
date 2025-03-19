from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QComboBox, QDateEdit)
from ..models.subscription import Subscription
from datetime import datetime

class SubscriptionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Name input
        self.name_label = QLabel("Service Name:")
        self.name_input = QLineEdit()
        
        # Amount input
        self.amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()
        
        # Billing cycle selection
        self.cycle_label = QLabel("Billing Cycle:")
        self.cycle_input = QComboBox()
        self.cycle_input.addItems(["Monthly", "Yearly", "Quarterly"])
        
        # Next billing date
        self.date_label = QLabel("Next Billing Date:")
        self.date_input = QDateEdit()
        self.date_input.setDate(datetime.now().date())
        
        # Add button
        self.add_button = QPushButton("Add Subscription")
        self.add_button.clicked.connect(self.add_subscription)
        
        # Add widgets to layout
        widgets = [self.name_label, self.name_input,
                  self.amount_label, self.amount_input,
                  self.cycle_label, self.cycle_input,
                  self.date_label, self.date_input,
                  self.add_button]
                  
        for widget in widgets:
            self.layout.addWidget(widget)
            
        self.setLayout(self.layout)

    def add_subscription(self):
        new_subscription = Subscription(
            name=self.name_input.text(),
            amount=float(self.amount_input.text()),
            billing_cycle=self.cycle_input.currentText(),
            next_billing_date=self.date_input.date().toPyDate()
        )
        # Here you would typically save the subscription to the database
        print(f"Added subscription: {new_subscription}")