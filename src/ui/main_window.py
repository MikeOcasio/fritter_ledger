from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from .expense_widget import ExpenseWidget
from .income_widget import IncomeWidget
from .subscription_widget import SubscriptionWidget
from .receipt_manager import ReceiptManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fritter Ledger")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(ExpenseWidget(), "Expenses")
        tabs.addTab(IncomeWidget(), "Income")
        tabs.addTab(SubscriptionWidget(), "Subscriptions")
        tabs.addTab(ReceiptManager(), "Receipts")
        
        layout.addWidget(tabs)
        
        # Load stylesheet
        with open('src/ui/styles.qss', 'r') as f:
            self.setStyleSheet(f.read())