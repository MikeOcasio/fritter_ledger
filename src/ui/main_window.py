from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
import os
from .expense_widget import ExpenseWidget
from .income_widget import IncomeWidget
from .subscription_widget import SubscriptionWidget
from .receipt_manager import ReceiptManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fritter Ledger")
        self.setMinimumSize(1000, 700)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.addTab(ExpenseWidget(), "Expenses")
        tabs.addTab(IncomeWidget(), "Income")
        tabs.addTab(SubscriptionWidget(), "Subscriptions")
        tabs.addTab(ReceiptManager(), "Receipts")
        
        layout.addWidget(tabs)
        
        # Load stylesheet
        style_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())