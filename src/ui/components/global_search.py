from PyQt6.QtWidgets import (QWidget, QLineEdit, QVBoxLayout, QLabel, QFrame, QHBoxLayout, 
                           QPushButton, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont

from ...database.db_manager import DatabaseManager
from ...models.expense import Expense
from ...models.income import Income
from ...models.subscription import Subscription
from ...models.receipt import Receipt
from ...models.client import Client
from sqlalchemy import or_, func


class SearchResult:
    """Class to hold search result data"""
    def __init__(self, text, source_type, source_id, breadcrumb):
        self.text = text 
        self.source_type = source_type  # "expense", "income", "subscription", "receipt", "client"
        self.source_id = source_id
        self.breadcrumb = breadcrumb
        
    def __str__(self):
        return f"{self.text} -> {self.breadcrumb}"


class SearchResultItem(QFrame):
    """Custom widget for displaying search results with breadcrumbs"""
    clicked = pyqtSignal(SearchResult)
    
    def __init__(self, search_result, parent=None):
        super().__init__(parent)
        self.search_result = search_result
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Set hover effects
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        
        # Main text
        main_text = QLabel(search_result.text)
        main_text.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        main_text.setStyleSheet("color: white;")
        
        # Breadcrumb text
        breadcrumb = QLabel(search_result.breadcrumb)
        breadcrumb.setFont(QFont("Arial", 9))
        breadcrumb.setStyleSheet("color: #AAAAAA;")
        
        layout.addWidget(main_text)
        layout.addWidget(breadcrumb)
        
        # Set colors - dark background for all result types
        self.base_color = "#2a2a2a"
        self.hover_color = "#3a3a3a"
        
        # Apply color as background
        self.setStyleSheet(f"""
            SearchResultItem {{
                background-color: {self.base_color};
                border-radius: 4px;
                color: white;
                border-left: 4px solid {self._get_accent_color(search_result.source_type)};
            }}
        """)
    
    def _get_accent_color(self, source_type):
        """Get accent color for left border based on result type"""
        color_map = {
            "expense": "#F44336",    # Red
            "income": "#4CAF50",     # Green
            "subscription": "#2196F3", # Blue
            "receipt": "#FF9800",    # Orange
            "client": "#9C27B0"      # Purple
        }
        return color_map.get(source_type.lower(), "#757575")
    
    def lighten_color(self, hex_color, factor=0.2):
        """Lighten a hex color by a factor"""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        self.setStyleSheet(f"""
            SearchResultItem {{
                background-color: {self.hover_color};
                border-radius: 4px;
                color: white;
                border-left: 4px solid {self._get_accent_color(self.search_result.source_type)};
            }}
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self.setStyleSheet(f"""
            SearchResultItem {{
                background-color: {self.base_color};
                border-radius: 4px;
                color: white;
                border-left: 4px solid {self._get_accent_color(self.search_result.source_type)};
            }}
        """)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.search_result)
        super().mousePressEvent(event)


class GlobalSearch(QWidget):
    """Global search widget that searches across all data tables"""
    result_selected = pyqtSignal(str, int)  # Emits (tab_name, record_id)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search input container
        search_container = QFrame()
        search_container.setObjectName("search-container")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search icon or label
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Arial", 14))
        search_icon.setStyleSheet("color: white;")
        search_layout.addWidget(search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search across all records...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setMinimumHeight(30)
        search_layout.addWidget(self.search_input)
        
        # Clear button (optional, since QLineEdit has built-in clear button)
        clear_btn = QPushButton("✕")
        clear_btn.setFixedSize(30, 30)
        clear_btn.setToolTip("Clear search")
        clear_btn.setObjectName("search-clear-btn")
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        layout.addWidget(search_container)
        
        # Create results popup container (not in main layout)
        self.results_container = QFrame(self.window())  # Create as child of main window
        self.results_container.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.results_container.setObjectName("search-results-container")
        self.results_container.setMaximumHeight(400)  # Limit height
        
        # Results layout
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(0)
        
        # Create scroll area for results
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget for scroll area
        scroll_content = QWidget()
        self.results_list = QVBoxLayout(scroll_content)
        self.results_list.setContentsMargins(10, 10, 10, 10)
        self.results_list.setSpacing(8)
        self.results_list.addStretch()
        
        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area)
        
        # Initially hide results
        self.results_container.hide()
        
        # Set styling
        self.setStyleSheet("""
            #search-container {
                background-color: #3a3a3a;
                border-radius: 20px;
                border: 1px solid #1a237e;
            }
            
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 14px;
                selection-background-color: #1a237e;
            }
            
            #search-clear-btn {
                background-color: transparent;
                color: #aaaaaa;
                border: none;
                font-size: 14px;
                padding: 0;
            }
            
            #search-clear-btn:hover {
                color: white;
            }
        """)
        
        # Style the results container separately
        self.results_container.setStyleSheet("""
            #search-results-container {
                background-color: #2a2a2a;
                border: 1px solid #1a237e;
                border-radius: 8px;
            }
            
            QScrollArea {
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #3a3a3a;
                width: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #1a237e;
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
    
    def on_search_text_changed(self, text):
        """Handle search text changes with debounce"""
        # Clear the previous timer
        self.search_timer.stop()
        
        if text:
            # Start a new timer
            self.search_timer.start(300)  # 300ms debounce
        else:
            # If text is empty, hide results immediately
            self.clear_results()
            self.results_container.hide()
    
    def showEvent(self, event):
        """Override showEvent to ensure we hide results when parent is shown"""
        super().showEvent(event)
        self.clear_search()
    
    def hideEvent(self, event):
        """Override hideEvent to ensure popup is hidden too"""
        self.results_container.hide()
        super().hideEvent(event)
    
    def resizeEvent(self, event):
        """Override resizeEvent to reposition popup if needed"""
        super().resizeEvent(event)
        if self.results_container.isVisible():
            self.position_results_container()
    
    def position_results_container(self):
        """Position the results container below the search input"""
        # Position under the search widget
        global_pos = self.mapToGlobal(QPoint(0, self.height()))
        self.results_container.move(global_pos)
        self.results_container.setFixedWidth(self.width())
    
    def perform_search(self):
        """Execute the search query"""
        query = self.search_input.text().strip()
        
        if not query or len(query) < 2:
            self.clear_results()
            self.results_container.hide()
            return
            
        # Get results from database
        results = self.search_database(query)
        
        # Display results
        self.display_results(results)
        
        # Position and show results
        self.position_results_container()
        self.results_container.show()
        self.results_container.raise_()
    
    def search_database(self, query):
        """Search across all database tables for matching records"""
        results = []
        session = self.db_manager.get_session()
        
        try:
            # Case-insensitive search
            like_term = f"%{query}%"
            
            # Search expenses
            expenses = session.query(Expense).filter(
                or_(
                    Expense.description.ilike(like_term),
                    Expense.category.ilike(like_term),
                    Expense.receipt_reference.ilike(like_term)
                )
            ).all()
            
            for expense in expenses:
                # Create result with breadcrumb
                if query.lower() in expense.description.lower():
                    results.append(SearchResult(
                        expense.description, 
                        "expense", 
                        expense.id, 
                        f"Expenses: {expense.category} - ${expense.amount:.2f}"
                    ))
                elif expense.receipt_reference and query.lower() in expense.receipt_reference.lower():
                    results.append(SearchResult(
                        expense.receipt_reference, 
                        "expense", 
                        expense.id, 
                        f"Expenses: Receipt Reference - {expense.description}"
                    ))
                else:
                    results.append(SearchResult(
                        expense.category, 
                        "expense", 
                        expense.id, 
                        f"Expenses: {expense.description} - ${expense.amount:.2f}"
                    ))
            
            # Search income
            incomes = session.query(Income).filter(
                or_(
                    Income.source.ilike(like_term),
                    Income.client.ilike(like_term),
                    Income.invoice_id.ilike(like_term),
                    Income.contract_id.ilike(like_term),
                    Income.status.ilike(like_term)
                )
            ).all()
            
            for income in incomes:
                # Figure out which field matched
                if income.source and query.lower() in income.source.lower():
                    results.append(SearchResult(
                        income.source, 
                        "income", 
                        income.id, 
                        f"Income: ${income.amount:.2f} - {income.client or 'No client'}"
                    ))
                elif income.client and query.lower() in income.client.lower():
                    results.append(SearchResult(
                        income.client, 
                        "income", 
                        income.id, 
                        f"Income: Client - {income.source}"
                    ))
                elif income.invoice_id and query.lower() in income.invoice_id.lower():
                    results.append(SearchResult(
                        income.invoice_id, 
                        "income", 
                        income.id, 
                        f"Income: Invoice ID - {income.source}"
                    ))
                elif income.contract_id and query.lower() in income.contract_id.lower():
                    results.append(SearchResult(
                        income.contract_id, 
                        "income", 
                        income.id, 
                        f"Income: Contract ID - {income.source}"
                    ))
                elif income.status and query.lower() in income.status.lower():
                    results.append(SearchResult(
                        income.status, 
                        "income", 
                        income.id, 
                        f"Income: Status - {income.source}"
                    ))
            
            # Search subscriptions
            subscriptions = session.query(Subscription).filter(
                or_(
                    Subscription.name.ilike(like_term),
                    Subscription.billing_cycle.ilike(like_term)
                )
            ).all()
            
            for subscription in subscriptions:
                if query.lower() in subscription.name.lower():
                    results.append(SearchResult(
                        subscription.name, 
                        "subscription", 
                        subscription.id, 
                        f"Subscriptions: ${subscription.amount:.2f} - {subscription.billing_cycle}"
                    ))
                else:
                    results.append(SearchResult(
                        subscription.billing_cycle, 
                        "subscription", 
                        subscription.id, 
                        f"Subscriptions: {subscription.name} - ${subscription.amount:.2f}"
                    ))
            
            # Search receipts
            receipts = session.query(Receipt).filter(
                or_(
                    Receipt.name.ilike(like_term),
                    Receipt.reference_id.ilike(like_term),
                    Receipt.notes.ilike(like_term)
                )
            ).all()
            
            for receipt in receipts:
                if receipt.reference_id and query.lower() in receipt.reference_id.lower():
                    results.append(SearchResult(
                        receipt.reference_id, 
                        "receipt", 
                        receipt.id, 
                        f"Receipts: Reference ID - {receipt.name}"
                    ))
                elif query.lower() in receipt.name.lower():
                    results.append(SearchResult(
                        receipt.name, 
                        "receipt", 
                        receipt.id, 
                        f"Receipts: {receipt.date.strftime('%Y-%m-%d')}"
                    ))
                elif receipt.notes and query.lower() in receipt.notes.lower():
                    results.append(SearchResult(
                        receipt.notes[:30] + ("..." if len(receipt.notes) > 30 else ""), 
                        "receipt", 
                        receipt.id, 
                        f"Receipts: Notes - {receipt.name}"
                    ))
            
            # Search clients
            clients = session.query(Client).filter(
                or_(
                    Client.business_name.ilike(like_term),
                    Client.poc.ilike(like_term),
                    Client.email.ilike(like_term),
                    Client.phone.ilike(like_term),
                    Client.address.ilike(like_term)
                )
            ).all()
            
            for client in clients:
                if query.lower() in client.business_name.lower():
                    results.append(SearchResult(
                        client.business_name, 
                        "client", 
                        client.id, 
                        f"Clients: {client.email}"
                    ))
                elif client.poc and query.lower() in client.poc.lower():
                    results.append(SearchResult(
                        client.poc, 
                        "client", 
                        client.id, 
                        f"Clients: Contact Person - {client.business_name}"
                    ))
                elif query.lower() in client.email.lower():
                    results.append(SearchResult(
                        client.email, 
                        "client", 
                        client.id, 
                        f"Clients: Email - {client.business_name}"
                    ))
                elif client.phone and query.lower() in client.phone.lower():
                    results.append(SearchResult(
                        client.phone, 
                        "client", 
                        client.id, 
                        f"Clients: Phone - {client.business_name}"
                    ))
                elif client.address and query.lower() in client.address.lower():
                    results.append(SearchResult(
                        client.address[:30] + ("..." if len(client.address) > 30 else ""), 
                        "client", 
                        client.id, 
                        f"Clients: Address - {client.business_name}"
                    ))
            
            # Limit to maximum results
            return results[:20]  # Limit to 20 results
            
        finally:
            session.close()
    
    def display_results(self, results):
        """Display the search results"""
        self.clear_results()
        
        if not results:
            # Show "No results found" message
            no_results = QLabel("No matching records found")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results.setStyleSheet("color: #AAAAAA; padding: 20px;")
            self.results_list.insertWidget(0, no_results)
        else:
            # Add each result
            for result in results:
                result_item = SearchResultItem(result)
                result_item.clicked.connect(self.on_result_clicked)
                self.results_list.insertWidget(0, result_item)
    
    def clear_results(self):
        """Clear all search results"""
        # Remove all widgets except the last stretch item
        while self.results_list.count() > 1:
            item = self.results_list.itemAt(0)
            if item and item.widget():
                item.widget().deleteLater()
            self.results_list.removeItem(item)
    
    def clear_search(self):
        """Clear search input and results"""
        self.search_input.clear()
        self.clear_results()
        self.results_container.hide()
    
    def on_result_clicked(self, result):
        """Handle click on a search result"""
        # Map source_type to tab name
        tab_map = {
            "expense": "Expenses",
            "income": "Income",
            "subscription": "Subscriptions",
            "receipt": "Receipts",
            "client": "Clients"
        }
        
        tab_name = tab_map.get(result.source_type.lower())
        if tab_name:
            self.result_selected.emit(tab_name, result.source_id)
            self.clear_search()