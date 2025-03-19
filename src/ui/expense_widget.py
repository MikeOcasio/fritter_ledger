from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFileDialog, QDateEdit,
                           QComboBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
import os
from PIL import Image
import io

class ExpenseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.receipt_data = None

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Input form section
        form_layout = QVBoxLayout()
        
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
            "Food & Dining",
            "Transportation",
            "Utilities",
            "Entertainment",
            "Shopping",
            "Healthcare",
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
        
        # Receipt upload
        receipt_layout = QHBoxLayout()
        self.receipt_label = QLabel("Receipt:")
        self.receipt_button = QPushButton("Upload Receipt")
        self.receipt_button.clicked.connect(self.upload_receipt)
        self.receipt_status = QLabel("No receipt uploaded")
        receipt_layout.addWidget(self.receipt_label)
        receipt_layout.addWidget(self.receipt_button)
        receipt_layout.addWidget(self.receipt_status)
        
        # Add expense button
        self.submit_button = QPushButton("Add Expense")
        self.submit_button.clicked.connect(self.add_expense)
        self.submit_button.setStyleSheet("background-color: #4CAF50; color: white;")
        
        # Add all layouts to form
        layouts = [amount_layout, desc_layout, cat_layout, 
                  date_layout, receipt_layout]
        for layout in layouts:
            form_layout.addLayout(layout)
        
        form_layout.addWidget(self.submit_button)
        
        # Create a frame for the form
        form_frame = QFrame()
        form_frame.setLayout(form_layout)
        form_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        main_layout.addWidget(form_frame)
        self.setLayout(main_layout)

    def upload_receipt(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Receipt",
            "",
            "Images (*.png *.jpg *.jpeg);;All Files (*)"
        )
        
        if file_name:
            try:
                with Image.open(file_name) as img:
                    # Convert to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format=img.format)
                    self.receipt_data = img_byte_arr.getvalue()
                    
                self.receipt_status.setText(
                    f"Receipt uploaded: {os.path.basename(file_name)}"
                )
            except Exception as e:
                self.receipt_status.setText(f"Error uploading receipt: {str(e)}")
                self.receipt_data = None

    def add_expense(self):
        try:
            amount = float(self.amount_input.text())
            description = self.desc_input.text()
            category = self.cat_input.currentText()
            date = self.date_input.date().toPyDate()
            
            # Create expense object (you'll need to implement database integration)
            expense_data = {
                'amount': amount,
                'description': description,
                'category': category,
                'date': date,
                'receipt': self.receipt_data
            }
            
            # Clear form after successful addition
            self.clear_form()
            
            print(f"Added expense: {expense_data}")  # Replace with DB integration
            
        except ValueError:
            self.amount_input.setStyleSheet("border: 1px solid red;")
            return

    def clear_form(self):
        self.amount_input.clear()
        self.desc_input.clear()
        self.cat_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.receipt_data = None
        self.receipt_status.setText("No receipt uploaded")
        self.amount_input.setStyleSheet("")