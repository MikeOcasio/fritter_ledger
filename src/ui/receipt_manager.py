from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QScrollArea, QFrame,
                           QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt
from PIL import Image
import io
from datetime import datetime
from .components.card_table import CardTable

class ReceiptManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Upload section
        upload_section = QFrame()
        upload_layout = QVBoxLayout(upload_section)
        
        # Fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Receipt Name")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setMaximumHeight(100)
        
        # Upload button
        self.upload_button = QPushButton("Upload Receipt")
        self.upload_button.clicked.connect(self.upload_receipt)
        
        upload_layout.addWidget(QLabel("Add New Receipt"))
        upload_layout.addWidget(self.name_input)
        upload_layout.addWidget(self.notes_input)
        upload_layout.addWidget(self.upload_button)
        
        # Receipt display section
        self.receipt_table = CardTable()
        
        layout.addWidget(upload_section)
        layout.addWidget(QLabel("Stored Receipts"))
        layout.addWidget(self.receipt_table)

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
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format=img.format)
                    receipt_data = {
                        'name': self.name_input.text() or 'Untitled',
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'notes': self.notes_input.toPlainText(),
                        'image': img_byte_arr.getvalue()
                    }
                    # Here you would save to database
                    self.add_receipt_card(receipt_data)
                    
            except Exception as e:
                print(f"Error uploading receipt: {str(e)}")

    def add_receipt_card(self, receipt_data):
        display_data = {
            'Name': receipt_data['name'],
            'Date': receipt_data['date'],
            'Notes': receipt_data['notes']
        }
        self.receipt_table.add_card(display_data)