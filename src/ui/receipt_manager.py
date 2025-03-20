from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QScrollArea, QFrame,
                           QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt
from PIL import Image
import io
from datetime import datetime
from .components.card_table import CardTable
from ..models.receipt import Receipt
from ..database.db_manager import DatabaseManager

class ReceiptManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.load_receipts()

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

    def load_receipts(self):
        session = self.db_manager.get_session()
        try:
            receipts = session.query(Receipt).all()
            for receipt in receipts:
                self.add_receipt_card({
                    'Name': receipt.name,
                    'Date': receipt.date.strftime("%Y-%m-%d %H:%M"),
                    'Notes': receipt.notes,
                    'ID': receipt.id
                })
        finally:
            session.close()

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
                    
                    receipt = Receipt(
                        name=self.name_input.text() or 'Untitled',
                        notes=self.notes_input.toPlainText(),
                        image=img_byte_arr.getvalue()
                    )
                    
                    if self.db_manager.add_record(receipt):
                        self.add_receipt_card({
                            'Name': receipt.name,
                            'Date': receipt.date.strftime("%Y-%m-%d %H:%M"),
                            'Notes': receipt.notes,
                            'ID': receipt.id
                        })
                        self.clear_form()
                    
            except Exception as e:
                print(f"Error uploading receipt: {str(e)}")

    def clear_form(self):
        self.name_input.clear()
        self.notes_input.clear()

    def add_receipt_card(self, receipt_data):
        display_data = {
            'Name': receipt_data['Name'],
            'Date': receipt_data['Date'],
            'Notes': receipt_data['Notes']
        }
        self.receipt_table.add_card(display_data)