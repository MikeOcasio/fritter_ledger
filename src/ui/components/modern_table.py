from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QAbstractItemView,
                           QPushButton, QHBoxLayout, QWidget, QDialog, 
                           QVBoxLayout, QTextEdit, QLabel, QHeaderView, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

class ModernTable(QTableWidget):
    view_clicked = pyqtSignal(int)
    download_clicked = pyqtSignal(int)
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    paid_clicked = pyqtSignal(int)  # New signal for marking as paid
    
    def __init__(self, headers, with_actions=False, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.with_actions = with_actions
        self.row_id_map = {}  # Map row index to data ID
        self.init_ui()
        self.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
    def init_ui(self):
        # Set column count based on headers plus actions column if needed
        column_count = len(self.headers)
        if self.with_actions:
            column_count += 1
        self.setColumnCount(column_count)
        
        # Set headers
        header_labels = self.headers.copy()
        if self.with_actions:
            header_labels.append("Actions")
        self.setHorizontalHeaderLabels(header_labels)
        
        # Set table properties
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)  # Show grid lines for better visibility
        self.verticalHeader().setVisible(False)
        
        # Make all columns stretch to fill available space
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # But set the actions column to fixed size if present
        if self.with_actions:
            last_column = self.columnCount() - 1
            self.horizontalHeader().setSectionResizeMode(last_column, QHeaderView.ResizeMode.Fixed)
            
        self.horizontalHeader().setHighlightSections(False)
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Set stylesheet for modern look
        self.setStyleSheet("""
            QTableWidget {
                background-color: #3a3a3a;
                color: #ffffff;
                border: none;
                gridline-color: #545454;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #545454;
            }
            QTableWidget::item:selected {
                background-color: #1a237e;
                color: white;
            }
            QHeaderView::section {
                background-color: #1a237e;
                color: #ffffff;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #333333;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        
        # Set minimum column widths and row height
        self.horizontalHeader().setMinimumSectionSize(120)
        self.verticalHeader().setDefaultSectionSize(50)  # Increased row height
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show context menu for the selected row"""
        row = self.rowAt(position.y())
        if row >= 0:
            item_id = self.row_id_map.get(row)
            if item_id is not None:
                from PyQt6.QtWidgets import QMenu
                
                context_menu = QMenu(self)
                
                # Check if this is a receipt
                is_receipt = False
                for col, header in enumerate(self.headers):
                    if header.lower() in ['notes']:
                        is_receipt = True
                        break
                
                if is_receipt:
                    view_action = context_menu.addAction("View Receipt")
                    view_action.triggered.connect(lambda: self.view_clicked.emit(item_id))
                    
                    download_action = context_menu.addAction("Download Receipt")
                    download_action.triggered.connect(lambda: self.download_clicked.emit(item_id))
                    
                    context_menu.addSeparator()
                
                # For any row with long text
                for col, header in enumerate(self.headers):
                    if header.lower() in ['description', 'notes', 'name', 'service', 'source']:
                        item = self.item(row, col)
                        if item and item.toolTip():
                            view_text_action = context_menu.addAction(f"View Full {header}")
                            view_text_action.triggered.connect(
                                lambda checked=False, h=header, t=item.text(), ft=item.toolTip(): 
                                self.show_text_dialog(h, t, ft)
                            )
                
                context_menu.addSeparator()
                
                edit_action = context_menu.addAction("Edit")
                edit_action.triggered.connect(lambda: self.edit_clicked.emit(item_id))
                
                delete_action = context_menu.addAction("Delete")
                delete_action.triggered.connect(lambda: self.delete_clicked.emit(item_id))
                
                context_menu.exec(self.mapToGlobal(position))
    
    def create_icon_button(self, tooltip, icon_text, on_click, is_delete=False):
        """Create a tool button with icon-like text character"""
        btn = QToolButton()
        btn.setText(icon_text)
        btn.setToolTip(tooltip)
        btn.clicked.connect(on_click)
        btn.setIconSize(QSize(24, 24))
        btn.setFixedSize(36, 36)
        
        if is_delete:
            btn.setStyleSheet("""
                QToolButton {
                    color: #f44336;
                    font-size: 18px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: rgba(244, 67, 54, 0.1);
                    border-radius: 4px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QToolButton {
                    color: #ffffff;
                    font-size: 18px;
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                }
            """)
        
        return btn
        
    def add_row(self, data, item_id):
        # Add a new row
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        # Store ID mapping
        self.row_id_map[row_position] = item_id
        
        # Add data to cells
        for col, header in enumerate(self.headers):
            # Get value from data (case insensitive matching)
            value = None
            for key in data.keys():
                if key.lower() == header.lower():
                    value = data[key]
                    break
            
            if value is not None:
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                # Truncate text for various field types
                if header.lower() in ['description', 'notes'] and len(str(value)) > 40:
                    item.setText(str(value)[:40] + "...")
                    item.setToolTip(str(value))  # Show full text on hover
                elif header.lower() in ['name', 'service', 'source'] and len(str(value)) > 25:
                    item.setText(str(value)[:25] + "...")
                    item.setToolTip(str(value))  # Show full text on hover
                    
                self.setItem(row_position, col, item)
        
        # Add action buttons if needed
        if self.with_actions:
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(8)  # Spacing between icons
            
            # Check if this is a receipt (has view/download)
            is_receipt = 'Date' in data and 'Notes' in data
            
            # Check if this is a subscription (has "Billing Cycle")
            is_subscription = 'Billing Cycle' in data
            
            if is_receipt:
                # Eye icon for view
                view_btn = self.create_icon_button(
                    "View Receipt", 
                    "👁️", 
                    lambda _, r=row_position: self.on_view_clicked(r)
                )
                
                # Download icon 
                download_btn = self.create_icon_button(
                    "Download Receipt", 
                    "⬇️", 
                    lambda _, r=row_position: self.on_download_clicked(r)
                )
                
                action_layout.addWidget(view_btn)
                action_layout.addWidget(download_btn)
            
            # If this is a subscription, add a "Mark as Paid" button
            if is_subscription:
                paid_btn = self.create_icon_button(
                    "Mark as Paid", 
                    "✓", 
                    lambda _, r=row_position: self.on_paid_clicked(r)
                )
                action_layout.addWidget(paid_btn)
            
            # Pencil icon for edit
            edit_btn = self.create_icon_button(
                "Edit", 
                "✏️", 
                lambda _, r=row_position: self.on_edit_clicked(r)
            )
            
            # X icon for delete
            delete_btn = self.create_icon_button(
                "Delete", 
                "✖", 
                lambda _, r=row_position: self.on_delete_clicked(r),
                is_delete=True
            )
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch(1)  # Add stretch to align buttons to the left
            
            # Set a fixed minimum width for the actions cell and add the widget
            self.setCellWidget(row_position, len(self.headers), action_widget)
            
            # Set fixed width for actions column - smaller with icons
            action_width = 250 if (is_receipt or is_subscription) else 120
            self.setColumnWidth(len(self.headers), action_width)
        
        # Adjust row height to accommodate buttons
        self.setRowHeight(row_position, 50)  # Increased row height
        
    def resizeEvent(self, event):
        """Override resize event to adjust column widths when table is resized"""
        super().resizeEvent(event)
        
        # Set actions column width (if present)
        if self.with_actions:
            last_column = self.columnCount() - 1
            action_width = min(250, max(150, self.width() // 6))  # Scale with table width, but with limits
            self.setColumnWidth(last_column, action_width)
    
    def clear_table(self):
        # Clear all rows
        self.setRowCount(0)
        self.row_id_map = {}
        
    def on_view_clicked(self, row):
        item_id = self.row_id_map.get(row)
        if item_id is not None:
            self.view_clicked.emit(item_id)
            
    def on_download_clicked(self, row):
        item_id = self.row_id_map.get(row)
        if item_id is not None:
            self.download_clicked.emit(item_id)
            
    def on_edit_clicked(self, row):
        item_id = self.row_id_map.get(row)
        if item_id is not None:
            self.edit_clicked.emit(item_id)
            
    def on_delete_clicked(self, row):
        item_id = self.row_id_map.get(row)
        if item_id is not None:
            self.delete_clicked.emit(item_id)
            
    def on_paid_clicked(self, row):
        """Handle click on the "Mark as Paid" button"""
        item_id = self.row_id_map.get(row)
        if item_id is not None:
            self.paid_clicked.emit(item_id)
            
    def on_cell_double_clicked(self, row, column):
        """Handle double-click on a cell to show full description/notes"""
        header = self.horizontalHeaderItem(column).text()
        if header.lower() in ['description', 'notes', 'name', 'service', 'source']:
            item = self.item(row, column)
            if item and (item.toolTip() or item.text()):
                self.show_text_dialog(header, item.text(), item.toolTip())
    
    def show_text_dialog(self, header, text, full_text=None):
        """Show a dialog with the full text content"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Full {header}")
        dialog.setMinimumSize(600, 400)  # Increased size
        
        layout = QVBoxLayout(dialog)
        
        # Use the full text from tooltip if provided (for truncated text)
        content = full_text if full_text else text
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(content)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #545454;
                padding: 10px;
                font-size: 14px;
            }
        """)
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(35)  # Increased button height
        close_btn.clicked.connect(dialog.close)
        
        layout.addWidget(QLabel(f"{header}:"))
        layout.addWidget(text_edit)
        layout.addWidget(close_btn)
        
        dialog.exec()