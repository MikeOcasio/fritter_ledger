from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QComboBox, QDateEdit,
                           QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from ..models.subscription import Subscription
from ..database.db_manager import DatabaseManager
from .components.modern_table import ModernTable
from datetime import datetime

class SubscriptionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.editing_id = None  # Track which record we're editing
        self.init_ui()
        self.load_subscriptions()

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

        # Add table
        headers = ["Service", "Amount", "Billing Cycle", "Next Billing"]
        self.subscription_table = ModernTable(headers, with_actions=True)
        self.subscription_table.edit_clicked.connect(self.edit_subscription)
        self.subscription_table.delete_clicked.connect(self.delete_subscription)
        main_layout.addWidget(QLabel("Active Subscriptions"))
        main_layout.addWidget(self.subscription_table)

        self.setLayout(main_layout)

    def load_subscriptions(self):
        session = self.db_manager.get_session()
        try:
            # Clear existing table
            self.subscription_table.clear_table()
            
            # Load all subscriptions
            subscriptions = session.query(Subscription).all()
            for subscription in subscriptions:
                subscription_data = {
                    'Service': subscription.name,
                    'Amount': f"${subscription.amount:.2f}",
                    'Billing Cycle': subscription.billing_cycle,
                    'Next Billing': subscription.next_billing_date.strftime("%Y-%m-%d"),
                    'ID': subscription.id
                }
                self.subscription_table.add_row(subscription_data, subscription.id)
        finally:
            session.close()

    def add_subscription(self):
        try:
            name = self.name_input.text()
            amount = float(self.amount_input.text())
            billing_cycle = self.cycle_input.currentText()
            next_billing_date = self.date_input.date().toPyDate()
            
            session = self.db_manager.get_session()
            
            try:
                if self.editing_id:  # Update existing record
                    subscription = session.query(Subscription).get(self.editing_id)
                    if subscription:
                        subscription.name = name
                        subscription.amount = amount
                        subscription.billing_cycle = billing_cycle
                        subscription.next_billing_date = next_billing_date
                        
                        # Update display
                        session.commit()
                        
                        # Reset editing state
                        self.clear_form()
                        
                        # Refresh the table
                        self.load_subscriptions()
                else:  # Create new record
                    subscription = Subscription(
                        name=name,
                        amount=amount,
                        billing_cycle=billing_cycle,
                        next_billing_date=next_billing_date
                    )
                    
                    session.add(subscription)
                    session.commit()
                    
                    # Get the ID assigned by the database
                    subscription_data = {
                        'Service': subscription.name,
                        'Amount': f"${subscription.amount:.2f}",
                        'Billing Cycle': subscription.billing_cycle,
                        'Next Billing': subscription.next_billing_date.strftime("%Y-%m-%d"),
                        'ID': subscription.id
                    }
                    
                    # Add to display
                    self.subscription_table.add_row(subscription_data, subscription.id)
                    self.clear_form()
            finally:
                session.close()
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")
            return

    def edit_subscription(self, subscription_id):
        """Edit an existing subscription"""
        session = self.db_manager.get_session()
        try:
            subscription = session.query(Subscription).get(subscription_id)
            if subscription:
                # Populate form with subscription data
                self.name_input.setText(subscription.name)
                self.amount_input.setText(str(subscription.amount))
                
                # Set cycle dropdown
                index = self.cycle_input.findText(subscription.billing_cycle)
                if index >= 0:
                    self.cycle_input.setCurrentIndex(index)
                
                # Set date
                date = QDate(
                    subscription.next_billing_date.year,
                    subscription.next_billing_date.month,
                    subscription.next_billing_date.day
                )
                self.date_input.setDate(date)
                
                # Set editing state
                self.editing_id = subscription_id
                self.add_button.setText("Update Subscription")
        finally:
            session.close()

    def delete_subscription(self, subscription_id):
        """Delete a subscription"""
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this subscription?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            session = self.db_manager.get_session()
            try:
                subscription = session.query(Subscription).get(subscription_id)
                if subscription:
                    session.delete(subscription)
                    session.commit()
                    
                    # Refresh the table
                    self.load_subscriptions()
                    
                    # If we were editing this record, clear the form
                    if self.editing_id == subscription_id:
                        self.clear_form()
            finally:
                session.close()

    def clear_form(self):
        """Clear form fields and reset editing state"""
        self.name_input.clear()
        self.amount_input.clear()
        self.cycle_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.amount_input.setStyleSheet("")
        self.editing_id = None
        self.add_button.setText("Add Subscription")