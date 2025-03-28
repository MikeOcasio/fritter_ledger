from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QScrollArea, QFrame,
                           QLineEdit, QTextEdit, QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import io
from datetime import datetime
import os
import fitz  # PyMuPDF for PDF handling
from .components.modern_table import ModernTable
from ..models.receipt import Receipt
from ..database.db_manager import DatabaseManager
from ..utils.reference_manager import ReferenceManager  # Import our new reference manager

class ReceiptManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.reference_manager = ReferenceManager()  # Add reference manager
        self.editing_id = None
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
        
        # Reference ID field (readonly, will be auto-generated)
        reference_layout = QHBoxLayout()
        reference_label = QLabel("Reference ID:")
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Auto-generated")
        self.reference_input.setReadOnly(True)  # Make it read-only
        self.reference_input.setStyleSheet("background-color: #333333;")  # Darker background to indicate readonly
        reference_layout.addWidget(reference_label)
        reference_layout.addWidget(self.reference_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setMaximumHeight(100)
        
        # Upload button
        self.upload_button = QPushButton("Upload Receipt")
        self.upload_button.clicked.connect(self.upload_receipt)
        
        upload_layout.addWidget(QLabel("Add New Receipt"))
        upload_layout.addWidget(self.name_input)
        upload_layout.addLayout(reference_layout)  # Add reference ID field
        upload_layout.addWidget(self.notes_input)
        upload_layout.addWidget(self.upload_button)
        
        # Receipt display section
        headers = ["Name", "Reference ID", "Date", "Notes"]
        self.receipt_table = ModernTable(headers, with_actions=True)
        self.receipt_table.view_clicked.connect(self.view_receipt)
        self.receipt_table.download_clicked.connect(self.download_receipt)
        self.receipt_table.edit_clicked.connect(self.edit_receipt)
        self.receipt_table.delete_clicked.connect(self.delete_receipt)
        
        layout.addWidget(upload_section)
        layout.addWidget(QLabel("Stored Receipts"))
        layout.addWidget(self.receipt_table)
        
        # Set initial auto-generated reference ID
        self.update_reference_id()

    def update_reference_id(self):
        """Update the reference ID field with a new auto-generated ID"""
        if not self.editing_id:  # Only generate new ID when not editing
            new_reference = self.reference_manager.get_next_receipt_reference()
            self.reference_input.setText(new_reference)

    def load_receipts(self):
        # Clear existing table
        self.receipt_table.clear_table()
        
        session = self.db_manager.get_session()
        try:
            receipts = session.query(Receipt).all()
            for receipt in receipts:
                receipt_data = {
                    'Name': receipt.name,
                    'Reference ID': receipt.reference_id or '-',
                    'Date': receipt.date.strftime("%Y-%m-%d %H:%M"),
                    'Notes': receipt.notes or '-',
                    'ID': receipt.id
                }
                self.receipt_table.add_row(receipt_data, receipt.id)
        finally:
            session.close()

    def upload_receipt(self):
        # If we're editing, just update the name, reference ID, and notes
        if self.editing_id:
            session = self.db_manager.get_session()
            try:
                receipt = session.query(Receipt).get(self.editing_id)
                if receipt:
                    receipt.name = self.name_input.text() or receipt.name
                    # Don't update reference_id when editing, keep the original
                    receipt.notes = self.notes_input.toPlainText()
                    
                    session.commit()
                    
                    # Reset form and refresh data
                    self.clear_form()
                    self.load_receipts()  # This will clear and reload all cards
                else:
                    QMessageBox.warning(self, "Error", "Receipt not found")
            finally:
                session.close()
            return
        
        # Otherwise handle a new upload
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Receipt",
            "",
            "All Supported Files (*.png *.jpg *.jpeg *.pdf);;Images (*.png *.jpg *.jpeg);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_name:
            try:
                image_data = None
                
                # Handle file based on extension
                _, ext = os.path.splitext(file_name)
                if ext.lower() == '.pdf':
                    # Convert PDF to image
                    image_data = self.convert_pdf_to_image(file_name)
                else:
                    # Handle as image
                    with Image.open(file_name) as img:
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format=img.format)
                        image_data = img_byte_arr.getvalue()
                
                if image_data:
                    # Create a new session
                    session = self.db_manager.get_session()
                    try:
                        # Get the auto-generated reference ID
                        reference_id = self.reference_input.text()
                        
                        receipt = Receipt(
                            name=self.name_input.text() or os.path.basename(file_name),
                            reference_id=reference_id,  # Use the auto-generated ID
                            notes=self.notes_input.toPlainText(),
                            image=image_data
                        )
                        
                        session.add(receipt)
                        session.commit()
                        
                        # Get receipt data for display
                        receipt_data = {
                            'Name': receipt.name,
                            'Reference ID': receipt.reference_id,
                            'Date': receipt.date.strftime("%Y-%m-%d %H:%M"),
                            'Notes': receipt.notes or '-',
                            'ID': receipt.id
                        }
                        
                        self.clear_form()  
                        # Add to table after clearing form to prevent duplicate UI updates
                        self.receipt_table.add_row(receipt_data, receipt.id)
                        
                    finally:
                        session.close()
                else:
                    QMessageBox.warning(self, "Error", "Could not process the file.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error uploading receipt: {str(e)}")
                print(f"Error uploading receipt: {str(e)}")

    def clear_form(self):
        self.name_input.clear()
        self.notes_input.clear()
        self.editing_id = None
        self.upload_button.setText("Upload Receipt")
        
        # Generate a new reference ID
        self.update_reference_id()

    def add_receipt_card(self, receipt_data):
        display_data = {
            'Name': receipt_data['Name'],
            'Reference ID': receipt_data['Reference ID'],
            'Date': receipt_data['Date'],
            'Notes': receipt_data['Notes'],
            'ID': receipt_data['ID']  # Keep ID for reference
        }
        self.receipt_table.add_row(display_data, receipt_data['ID'])

    def convert_pdf_to_image(self, pdf_path):
        """Convert first page of PDF to image"""
        try:
            # Open the PDF
            pdf_document = fitz.open(pdf_path)
            
            # Get the first page
            page = pdf_document[0]
            
            # Render page to an image with higher resolution
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # Convert to PNG image
            img_data = pix.tobytes("png")
            
            # Close the PDF
            pdf_document.close()
            
            return img_data
            
        except Exception as e:
            print(f"Error converting PDF: {str(e)}")
            return None

    def view_receipt(self, receipt_id):
        session = self.db_manager.get_session()
        try:
            receipt = session.query(Receipt).get(receipt_id)
            if receipt and receipt.image:
                image_dialog = ImageViewerDialog(receipt.name, receipt.image, self)
                image_dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Receipt image not found")
        finally:
            session.close()

    def download_receipt(self, receipt_id):
        session = self.db_manager.get_session()
        try:
            receipt = session.query(Receipt).get(receipt_id)
            if receipt and receipt.image:
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Receipt Image",
                    os.path.join(os.path.expanduser("~"), f"{receipt.name}.png"),
                    "Images (*.png *.jpg);;All Files (*)"
                )
                
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(receipt.image)
                    QMessageBox.information(self, "Success", "Receipt downloaded successfully")
            else:
                QMessageBox.warning(self, "Error", "Receipt image not found")
        finally:
            session.close()

    def edit_receipt(self, receipt_id):
        session = self.db_manager.get_session()
        try:
            receipt = session.query(Receipt).get(receipt_id)
            if receipt:
                # Set form fields
                self.name_input.setText(receipt.name)
                self.reference_input.setText(receipt.reference_id or "")  # Set reference ID
                self.notes_input.setText(receipt.notes or "")
                
                # Set editing state
                self.editing_id = receipt_id
                self.upload_button.setText("Update Receipt")
            else:
                QMessageBox.warning(self, "Error", "Receipt not found")
        finally:
            session.close()

    def delete_receipt(self, receipt_id):
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this receipt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            session = self.db_manager.get_session()
            try:
                receipt = session.query(Receipt).get(receipt_id)
                if receipt:
                    session.delete(receipt)
                    session.commit()
                    
                    # Refresh the table
                    self.load_receipts()
                    
                    # If we were editing this record, clear the form
                    if self.editing_id == receipt_id:
                        self.clear_form()
            finally:
                session.close()

    def highlight_record(self, record_id):
        """Highlight a specific record by ID when coming from search"""
        # Find the row with this ID
        row_index = None
        for row in range(self.receipt_table.rowCount()):
            item_id = self.receipt_table.item_id_for_row(row)
            if item_id == record_id:
                row_index = row
                break
        
        if row_index is not None:
            # Scroll to the row
            self.receipt_table.scrollToItem(self.receipt_table.item(row_index, 0))
            
            # Select the row
            self.receipt_table.selectRow(row_index)
            
            # Flash highlight animation (implemented in ModernTable)
            self.receipt_table.flash_highlight_row(row_index)
            
            # Load the record in edit form
            self.edit_receipt(record_id)
            
            # Also view the receipt
            self.view_receipt(record_id)


class ImageViewerDialog(QDialog):
    def __init__(self, title, image_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Receipt: {title}")
        self.setMinimumSize(800, 600)
        self.image_data = image_data
        self.title = title
        self.zoom_level = 1.0
        self.current_page = 0
        self.pages = []
        
        # Try to detect if it's a PDF
        self.is_pdf = False
        if image_data[:4] == b'%PDF':
            self.is_pdf = True
            self.load_pdf_pages()
        
        self.init_ui()
    
    def load_pdf_pages(self):
        try:
            # Load PDF from binary data
            pdf_stream = io.BytesIO(self.image_data)
            pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
            
            # Extract each page as an image
            for i in range(len(pdf_document)):
                page = pdf_document[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                self.pages.append(img_data)
            
            pdf_document.close()
        except Exception as e:
            print(f"Error loading PDF pages: {str(e)}")
            # Fallback to treating as single image
            self.is_pdf = False
            self.pages = [self.image_data]
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add scroll area for large images
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.image_label)
        self.scroll.setWidgetResizable(True)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(40)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.zoom_label = QLabel("100%")  # Create this BEFORE showing images
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(40)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)
        
        # Page navigation (only show if PDF with multiple pages)
        self.page_layout = QHBoxLayout()
        if self.is_pdf and len(self.pages) > 1:
            prev_btn = QPushButton("Previous")
            prev_btn.clicked.connect(self.previous_page)
            
            self.page_label = QLabel(f"Page {self.current_page + 1} of {len(self.pages)}")
            
            next_btn = QPushButton("Next")
            next_btn.clicked.connect(self.next_page)
            
            self.page_layout.addWidget(prev_btn)
            self.page_layout.addWidget(self.page_label)
            self.page_layout.addWidget(next_btn)
        
        # Action buttons
        action_layout = QHBoxLayout()
        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.download_receipt)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        
        action_layout.addWidget(download_btn)
        action_layout.addWidget(close_btn)
        
        # Add all control elements
        controls_layout.addLayout(zoom_layout)
        controls_layout.addStretch()
        if self.is_pdf and len(self.pages) > 1:
            controls_layout.addLayout(self.page_layout)
        controls_layout.addStretch()
        controls_layout.addLayout(action_layout)
        
        main_layout.addWidget(self.scroll)
        main_layout.addLayout(controls_layout)
        
        # Now load the image after all UI elements are created
        if self.is_pdf and self.pages:
            self.show_current_page()
        else:
            self.show_image(self.image_data)
    
    def show_image(self, image_data, apply_zoom=True):
        # Convert image data to QPixmap
        image = QImage.fromData(image_data)
        self.pixmap = QPixmap.fromImage(image)
        
        if apply_zoom:
            self.apply_zoom()
        else:
            self.image_label.setPixmap(self.pixmap)
    
    def show_current_page(self):
        if 0 <= self.current_page < len(self.pages):
            self.show_image(self.pages[self.current_page])
            if hasattr(self, 'page_label'):
                self.page_label.setText(f"Page {self.current_page + 1} of {len(self.pages)}")
    
    def apply_zoom(self):
        if hasattr(self, 'pixmap'):
            # Get original size
            original_size = self.pixmap.size()
            
            # Calculate zoomed size
            zoomed_width = int(original_size.width() * self.zoom_level)
            zoomed_height = int(original_size.height() * self.zoom_level)
            
            # Create scaled pixmap
            scaled_pixmap = self.pixmap.scaled(
                zoomed_width, 
                zoomed_height,
                Qt.AspectRatioMode.KeepAspectRatio
            )
            
            # Update image and zoom label
            self.image_label.setPixmap(scaled_pixmap)
            self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
    
    def zoom_in(self):
        self.zoom_level = min(5.0, self.zoom_level + 0.25)  # Max 500%
        self.apply_zoom()
    
    def zoom_out(self):
        self.zoom_level = max(0.25, self.zoom_level - 0.25)  # Min 25%
        self.apply_zoom()
    
    def next_page(self):
        if self.is_pdf and self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.show_current_page()
    
    def previous_page(self):
        if self.is_pdf and self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()
    
    def download_receipt(self):
        if self.is_pdf:
            # Download as PDF
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Receipt",
                os.path.join(os.path.expanduser("~"), f"{self.title}.pdf"),
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(self.image_data)
                QMessageBox.information(self, "Success", "Receipt downloaded successfully")
        else:
            # Download as image
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Receipt Image",
                os.path.join(os.path.expanduser("~"), f"{self.title}.png"),
                "Images (*.png *.jpg);;All Files (*)"
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(self.image_data)
                QMessageBox.information(self, "Success", "Receipt downloaded successfully")