from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QStackedWidget, QLabel, QSizePolicy,
                           QToolButton, QFrame, QApplication)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont
import os
from .expense_widget import ExpenseWidget
from .income_widget import IncomeWidget
from .subscription_widget import SubscriptionWidget
from .receipt_manager import ReceiptManager
from .client_widget import ClientWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fritter Ledger")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create and add sidebar
        self.sidebar = CollapsibleSidebar()
        self.sidebar.button_clicked.connect(self.change_page)
        self.main_layout.addWidget(self.sidebar)
        
        # Create and add content area
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with hamburger menu
        header_layout = QHBoxLayout()
        
        # Hamburger menu button
        self.menu_button = QToolButton()
        self.menu_button.setText("☰")
        self.menu_button.setFont(QFont("Arial", 16))
        self.menu_button.setToolTip("Toggle Menu")
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_button.setStyleSheet("""
            QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                padding: 8px;
                font-size: 24px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        self.menu_button.clicked.connect(self.toggle_sidebar)
        
        # Page title
        self.page_title = QLabel("Expenses")
        self.page_title.setProperty("class", "page-title")
        
        header_layout.addWidget(self.menu_button)
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        
        # Create stacked widget for page content
        self.pages = QStackedWidget()
        
        # Create pages and add to stacked widget
        self.expense_page = ExpenseWidget()
        self.income_page = IncomeWidget()
        self.subscription_page = SubscriptionWidget()
        self.receipt_page = ReceiptManager()
        self.client_page = ClientWidget()
        
        self.pages.addWidget(self.expense_page)
        self.pages.addWidget(self.income_page)
        self.pages.addWidget(self.subscription_page)
        self.pages.addWidget(self.receipt_page)
        self.pages.addWidget(self.client_page)
        
        # Add pages to content layout
        content_layout.addWidget(self.pages)
        
        # Add content container to main layout
        self.main_layout.addWidget(self.content_container)
        
        # Initially collapse sidebar
        QApplication.processEvents()  # Process events to ensure UI is built
        self.sidebar.collapse()
        
        # Load stylesheet
        style_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())
    
    def change_page(self, page_index, page_name):
        """Change the current page in the stacked widget"""
        self.pages.setCurrentIndex(page_index)
        self.page_title.setText(page_name)
        # Auto-collapse sidebar on mobile/small screens
        if self.width() < 1000:
            self.sidebar.collapse()
    
    def toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed state"""
        if self.sidebar.is_expanded:
            self.sidebar.collapse()
        else:
            self.sidebar.expand()
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Auto-collapse sidebar on mobile/small screens
        if event.size().width() < 800 and self.sidebar.is_expanded:
            self.sidebar.collapse()


class CollapsibleSidebar(QFrame):
    """Custom sidebar widget with navigation buttons that can collapse"""
    button_clicked = pyqtSignal(int, str)  # Signal emitted when a button is clicked (index, name)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.is_expanded = True
        self.expanded_width = 200
        self.collapsed_width = 0
        
        # Configure frame
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # App title
        self.app_title = QLabel("Fritter Ledger")
        self.app_title.setObjectName("sidebar-title")
        self.app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_title.setMinimumHeight(60)
        self.layout.addWidget(self.app_title)
        
        # Add navigation buttons
        self.add_button("Expenses", 0)
        self.add_button("Income", 1)
        self.add_button("Subscriptions", 2)
        self.add_button("Receipts", 3)
        self.add_button("Clients", 4)
        
        # Add spacer to push buttons to the top
        self.layout.addStretch()
        
    def add_button(self, text, index):
        """Add a navigation button to the sidebar"""
        button = QPushButton(text)
        button.setObjectName("sidebar-button")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(50)
        button.clicked.connect(lambda: self.button_clicked.emit(index, text))
        self.layout.addWidget(button)
    
    def expand(self):
        """Expand the sidebar with animation"""
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.collapsed_width)
        self.animation.setEndValue(self.expanded_width)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
        # Also animate minimum width for smooth animation
        self.animation_min = QPropertyAnimation(self, b"minimumWidth")
        self.animation_min.setDuration(300)
        self.animation_min.setStartValue(self.collapsed_width)
        self.animation_min.setEndValue(self.expanded_width)
        self.animation_min.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation_min.start()
        
        self.is_expanded = True
    
    def collapse(self):
        """Collapse the sidebar with animation"""
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.expanded_width)
        self.animation.setEndValue(self.collapsed_width)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
        # Also animate minimum width for smooth animation
        self.animation_min = QPropertyAnimation(self, b"minimumWidth")
        self.animation_min.setDuration(300)
        self.animation_min.setStartValue(self.expanded_width)
        self.animation_min.setEndValue(self.collapsed_width)
        self.animation_min.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation_min.start()
        
        self.is_expanded = False