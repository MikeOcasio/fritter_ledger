from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QComboBox, 
                           QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from ...utils.calculations import (calculate_total_expenses, calculate_total_income,
                                 calculate_monthly_subscriptions, calculate_subscription_total)
from ...database.db_manager import DatabaseManager
from datetime import datetime, timedelta

class SummaryFooter(QFrame):
    period_changed = pyqtSignal(str, datetime, datetime)  # Signal emitted when period changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.setObjectName("summary-footer")
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Set up time periods
        self.periods = {
            "This Month": self._get_month_range(0),
            "Last Month": self._get_month_range(-1),
            "This Quarter": self._get_quarter_range(0),
            "Last Quarter": self._get_quarter_range(-1),
            "This Year": self._get_year_range(0),
            "Last Year": self._get_year_range(-1),
            "Last 6 Months": self._get_custom_range(months=6),
            "All Time": (datetime(2000, 1, 1), datetime.now())
        }
        
        self.current_period = "This Month"
        self.init_ui()
        self.update_totals()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(20)
        
        # Period selection dropdown
        self.period_label = QLabel("Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItems(list(self.periods.keys()))
        self.period_combo.setCurrentText("This Month")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        
        # Total labels with bold font
        bold_font = QFont()
        bold_font.setBold(True)
        
        # Income total
        income_layout = QHBoxLayout()
        income_label = QLabel("Income:")
        income_label.setFont(bold_font)
        self.income_total = QLabel("$0.00")
        self.income_total.setFont(bold_font)
        self.income_total.setStyleSheet("color: #4CAF50;")  # Green for income
        income_layout.addWidget(income_label)
        income_layout.addWidget(self.income_total)
        
        # Expenses total
        expenses_layout = QHBoxLayout()
        expenses_label = QLabel("Expenses:")
        expenses_label.setFont(bold_font)
        self.expenses_total = QLabel("$0.00")
        self.expenses_total.setFont(bold_font)
        self.expenses_total.setStyleSheet("color: #F44336;")  # Red for expenses
        expenses_layout.addWidget(expenses_label)
        expenses_layout.addWidget(self.expenses_total)
        
        # Subscriptions total
        subs_layout = QHBoxLayout()
        subs_label = QLabel("Subscriptions:")
        subs_label.setFont(bold_font)
        self.subs_total = QLabel("$0.00")
        self.subs_total.setFont(bold_font)
        self.subs_total.setStyleSheet("color: #2196F3;")  # Blue for subscriptions
        subs_layout.addWidget(subs_label)
        subs_layout.addWidget(self.subs_total)
        
        # Net total (Income - Expenses - Subscriptions)
        net_layout = QHBoxLayout()
        net_label = QLabel("Net:")
        net_label.setFont(bold_font)
        self.net_total = QLabel("$0.00")
        self.net_total.setFont(bold_font)
        net_layout.addWidget(net_label)
        net_layout.addWidget(self.net_total)
        
        # Refresh button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("Refresh totals")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.clicked.connect(self.update_totals)
        
        # Add all elements to layout
        layout.addWidget(self.period_label)
        layout.addWidget(self.period_combo)
        layout.addStretch(1)
        layout.addLayout(income_layout)
        layout.addLayout(expenses_layout)
        layout.addLayout(subs_layout)
        layout.addLayout(net_layout)
        layout.addWidget(self.refresh_btn)
        
    def on_period_changed(self, period_text):
        self.current_period = period_text
        start_date, end_date = self.periods[period_text]
        
        # Update the totals for the new period
        self.update_totals()
        
        # Emit signal with new period
        self.period_changed.emit(period_text, start_date, end_date)
        
    def update_totals(self):
        """Update all total values based on selected time period"""
        start_date, end_date = self.periods[self.current_period]
        
        # Get session for database queries
        session = self.db_manager.get_session()
        try:
            # Calculate totals
            income_total = calculate_total_income(session, start_date, end_date)
            expense_total = calculate_total_expenses(session, start_date, end_date)
            sub_total = calculate_subscription_total(session, self.current_period)
            
            # Format and display totals
            self.income_total.setText(f"${income_total:.2f}")
            self.expenses_total.setText(f"${expense_total:.2f}")
            self.subs_total.setText(f"${sub_total:.2f}")
            
            # Calculate and format net total
            net = income_total - expense_total - sub_total
            self.net_total.setText(f"${net:.2f}")
            
            # Color code net total based on value
            if net > 0:
                self.net_total.setStyleSheet("color: #4CAF50;")  # Green for positive
            elif net < 0:
                self.net_total.setStyleSheet("color: #F44336;")  # Red for negative
            else:
                self.net_total.setStyleSheet("color: #FFFFFF;")  # White for zero
                
        finally:
            session.close()
            
    def _get_month_range(self, offset=0):
        """Get date range for current month +/- offset"""
        today = datetime.now()
        # Calculate target month with offset
        year = today.year
        month = today.month + offset
        
        # Adjust year if month is out of range
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1
            
        # First day of target month
        start = datetime(year, month, 1)
        
        # First day of next month
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
            
        # Adjust end to be the last day of target month
        end = end - timedelta(seconds=1)
        
        return (start, end)
    
    def _get_quarter_range(self, offset=0):
        """Get date range for current quarter +/- offset"""
        today = datetime.now()
        
        # Calculate current quarter
        current_quarter = (today.month - 1) // 3 + 1
        year = today.year
        
        # Apply offset
        quarter = current_quarter + offset
        while quarter > 4:
            quarter -= 4
            year += 1
        while quarter < 1:
            quarter += 4
            year -= 1
            
        # Calculate start month for quarter (1, 4, 7, 10)
        start_month = (quarter - 1) * 3 + 1
        
        # First day of quarter
        start = datetime(year, start_month, 1)
        
        # First day of next quarter
        if quarter == 4:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, start_month + 3, 1)
            
        # Adjust end to be the last day of current quarter
        end = end - timedelta(seconds=1)
        
        return (start, end)
    
    def _get_year_range(self, offset=0):
        """Get date range for current year +/- offset"""
        today = datetime.now()
        year = today.year + offset
        
        # First day of year
        start = datetime(year, 1, 1)
        
        # First day of next year
        end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        
        return (start, end)
    
    def _get_custom_range(self, months=6):
        """Get custom date range going back X months from today"""
        end = datetime.now()
        
        # Calculate start date by subtracting months
        year = end.year
        month = end.month - months
        
        # Adjust year if month is out of range
        while month < 1:
            month += 12
            year -= 1
            
        # First day of start month
        start = datetime(year, month, 1)
        
        return (start, end)