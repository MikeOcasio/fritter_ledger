from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QCalendarWidget, QTableWidget, QTableWidgetItem,
                           QFrame, QHeaderView, QSplitter, QAbstractItemView,
                           QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QDate, QSize, QRect
from PyQt6.QtGui import QColor, QBrush, QIcon, QFont, QPainter, QPen, QTextOption
from ...models.subscription import Subscription
from ...database.db_manager import DatabaseManager
from datetime import datetime, timedelta, date

class SubscriptionCalendar(QCalendarWidget):
    """Custom calendar widget with dots to mark subscription dates"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subscription_dates = {}  # Maps dates to number of subscriptions
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        
    def set_subscription_dates(self, dates_dict):
        """Set the dictionary of dates with subscriptions"""
        self.subscription_dates = dates_dict
        self.updateCells()
        
    def paintCell(self, painter, rect, date):
        """Override paint cell to add indicators for subscription dates"""
        # First, let the parent class paint the cell normally
        super().paintCell(painter, rect, date)
        
        # Then add our indicators if there are subscriptions for this date
        py_date = date.toPyDate()
        if py_date in self.subscription_dates:
            # Draw a small colored dot in bottom center of the cell
            painter.save()
            
            # Get number of subscriptions for this date
            subs = self.subscription_dates[py_date]
            count = len(subs)
            
            # Determine dot color based on subscription types
            has_monthly = any(sub['cycle'] == 'Monthly' for sub in subs)
            has_quarterly = any(sub['cycle'] == 'Quarterly' for sub in subs)
            has_yearly = any(sub['cycle'] == 'Yearly' for sub in subs)
            
            if has_monthly:
                dot_color = QColor("#2196F3")  # Blue
            elif has_quarterly:
                dot_color = QColor("#4CAF50")  # Green
            elif has_yearly:
                dot_color = QColor("#F44336")  # Red
            else:
                dot_color = QColor("#757575")  # Gray
            
            # Draw dot indicator
            dot_radius = 4
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(dot_color))
            
            if count > 1:
                # Draw badge with count
                badge_rect = QRect(rect.right() - 18, rect.top() + 2, 16, 16)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(dot_color))
                painter.drawEllipse(badge_rect)
                
                # Draw count text
                painter.setPen(QPen(QColor("white")))
                painter.setFont(QFont("Arial", 8))
                text_rect = QRect(badge_rect.left(), badge_rect.top(), badge_rect.width(), badge_rect.height())
                text_option = QTextOption()
                text_option.setAlignment(Qt.AlignmentFlag.AlignCenter)
                painter.drawText(text_rect, str(count), text_option)
                
                # Draw dot at bottom
                dot_x = rect.center().x()
                dot_y = rect.bottom() - dot_radius - 2
                painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius, 
                                  dot_radius * 2, dot_radius * 2)
            else:
                # Just draw a dot
                dot_x = rect.center().x()
                dot_y = rect.bottom() - dot_radius - 2
                painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius, 
                                  dot_radius * 2, dot_radius * 2)
            
            painter.restore()


class SubscriptionCalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.subscription_dates = {}  # Map dates to subscription IDs and details
        self.current_month_total = 0.0
        self.yearly_total = 0.0
        self.show_yearly_total = False  # Default to monthly total
        
        self.setWindowTitle("Subscription Calendar")
        self.setMinimumSize(1000, 700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        self.init_ui()
        self.load_subscriptions()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Title and totals selector
        title_layout = QHBoxLayout()
        title = QLabel("Subscription Calendar")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        # Radio buttons for total selection
        self.total_selector_group = QButtonGroup(self)
        
        self.monthly_total_radio = QRadioButton("Monthly Total")
        self.monthly_total_radio.setChecked(True)  # Default to monthly
        self.monthly_total_radio.toggled.connect(self.on_total_type_changed)
        
        self.yearly_total_radio = QRadioButton("Yearly Total")
        self.yearly_total_radio.toggled.connect(self.on_total_type_changed)
        
        self.total_selector_group.addButton(self.monthly_total_radio)
        self.total_selector_group.addButton(self.yearly_total_radio)
        
        # Total amount label
        self.total_label = QLabel()
        self.total_label.setFont(QFont("Arial", 14))
        self.total_label.setStyleSheet("color: #4CAF50;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.monthly_total_radio)
        title_layout.addWidget(self.yearly_total_radio)
        title_layout.addWidget(self.total_label)
        
        main_layout.addLayout(title_layout)
        
        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Calendar widget
        calendar_frame = QFrame()
        calendar_layout = QVBoxLayout(calendar_frame)
        
        # Use our custom calendar widget
        self.calendar = SubscriptionCalendar()
        self.calendar.clicked.connect(self.on_date_clicked)
        
        # Style the calendar to match the app
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #3a3a3a;
                color: white;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #1a237e;
                border: none;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }
            QCalendarWidget QMenu {
                background-color: #3a3a3a;
                color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: #3a3a3a;
                color: white;
                selection-background-color: #1a237e;
            }
            QCalendarWidget QTableView {
                alternate-background-color: #333333;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                selection-background-color: #1a237e;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1a237e;
            }
        """)
        
        calendar_layout.addWidget(self.calendar)
        
        # Legend
        legend_layout = QHBoxLayout()
        
        # Monthly subscriptions
        monthly_indicator = QFrame()
        monthly_indicator.setFixedSize(20, 20)
        monthly_indicator.setStyleSheet("background-color: #2196F3; border-radius: 10px;")
        legend_layout.addWidget(monthly_indicator)
        legend_layout.addWidget(QLabel("Monthly"))
        
        # Quarterly subscriptions
        quarterly_indicator = QFrame()
        quarterly_indicator.setFixedSize(20, 20)
        quarterly_indicator.setStyleSheet("background-color: #4CAF50; border-radius: 10px;")
        legend_layout.addWidget(quarterly_indicator)
        legend_layout.addWidget(QLabel("Quarterly"))
        
        # Yearly subscriptions
        yearly_indicator = QFrame()
        yearly_indicator.setFixedSize(20, 20)
        yearly_indicator.setStyleSheet("background-color: #F44336; border-radius: 10px;")
        legend_layout.addWidget(yearly_indicator)
        legend_layout.addWidget(QLabel("Yearly"))
        
        legend_layout.addStretch()
        
        calendar_layout.addLayout(legend_layout)
        
        # Right side: Subscriptions for selected date
        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        
        # Selected date label
        self.date_label = QLabel("Subscriptions due today")
        self.date_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        details_layout.addWidget(self.date_label)
        
        # Table for subscriptions on selected date
        self.sub_table = QTableWidget()
        self.sub_table.setColumnCount(4)
        self.sub_table.setHorizontalHeaderLabels(["Service", "Amount", "Billing Cycle", "Next Due"])
        self.sub_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sub_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sub_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sub_table.setAlternatingRowColors(True)
        details_layout.addWidget(self.sub_table)
        
        # Upcoming subscriptions
        self.upcoming_label = QLabel("Upcoming this month")
        self.upcoming_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        details_layout.addWidget(self.upcoming_label)
        
        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(4)
        self.upcoming_table.setHorizontalHeaderLabels(["Service", "Amount", "Billing Cycle", "Due Date"])
        self.upcoming_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.upcoming_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.upcoming_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.upcoming_table.setAlternatingRowColors(True)
        details_layout.addWidget(self.upcoming_table)
        
        # Add frames to splitter
        splitter.addWidget(calendar_frame)
        splitter.addWidget(details_frame)
        
        # Set initial sizes (40% calendar, 60% details)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        
        # Refresh button and close button
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_subscriptions()
        
        # Updates will be handled in load_subscriptions which will:
        # 1. Mark calendar dates with dots
        # 2. Select current date
        # 3. Load upcoming subscriptions
    
    def on_total_type_changed(self):
        """Handle change between monthly and yearly total display"""
        self.show_yearly_total = self.yearly_total_radio.isChecked()
        self.update_total_display()
    
    def update_total_display(self):
        """Update the total label based on selected total type"""
        selected_date = self.calendar.selectedDate().toPyDate()
        month_name = selected_date.strftime("%B %Y")
        
        if self.show_yearly_total:
            self.total_label.setText(f"Annual Total: ${self.yearly_total:.2f}")
        else:
            self.total_label.setText(f"{month_name} Total: ${self.current_month_total:.2f}")
    
    def load_subscriptions(self):
        """Load all subscriptions and mark their dates on the calendar"""
        session = self.db_manager.get_session()
        try:
            # Get current month and year for monthly total calculation
            current_date = QDate.currentDate().toPyDate()
            
            # Clear existing data
            self.subscription_dates = {}
            self.yearly_total = 0.0
            
            # Get all subscriptions
            subscriptions = session.query(Subscription).all()
            
            # Process each subscription
            for sub in subscriptions:
                next_billing = sub.next_billing_date
                
                # Calculate dates for the next 12 months
                all_dates = self.calculate_future_billing_dates(sub, 12)
                
                # Add each date to our tracking dict
                for billing_date in all_dates:
                    py_date = billing_date
                    if py_date not in self.subscription_dates:
                        self.subscription_dates[py_date] = []
                    
                    self.subscription_dates[py_date].append({
                        'id': sub.id,
                        'name': sub.name,
                        'amount': sub.amount,
                        'cycle': sub.billing_cycle
                    })
                
                # Calculate yearly total
                if sub.billing_cycle == "Monthly":
                    self.yearly_total += sub.amount * 12
                elif sub.billing_cycle == "Quarterly":
                    self.yearly_total += sub.amount * 4
                elif sub.billing_cycle == "Yearly":
                    self.yearly_total += sub.amount
            
            # Set the subscription dates for our custom calendar
            self.calendar.set_subscription_dates(self.subscription_dates)
            
            # Calculate the monthly total based on current month
            self.recalculate_monthly_total(current_date)
            
            # Update the total display
            self.update_total_display()
            
            # Set the current date
            today = QDate.currentDate()
            self.calendar.setSelectedDate(today)
            
            # Load the selected date's details
            self.on_date_clicked(today)
            
            # Load upcoming subscriptions for the current month automatically
            self.load_upcoming_subscriptions()
            
        finally:
            session.close()
    
    def calculate_future_billing_dates(self, subscription, months_ahead):
        """Calculate future billing dates based on billing cycle"""
        dates = []
        next_date = subscription.next_billing_date
        
        # Always include the next billing date
        dates.append(next_date)
        
        if subscription.billing_cycle == "Monthly":
            # Add monthly dates
            current_date = next_date
            for _ in range(months_ahead):
                # Move to next month
                month = current_date.month + 1
                year = current_date.year
                
                if month > 12:
                    month = 1
                    year += 1
                
                # Make sure we don't exceed the day count for the month
                day = min(current_date.day, self.days_in_month(year, month))
                current_date = date(year, month, day)
                dates.append(current_date)
                
        elif subscription.billing_cycle == "Quarterly":
            # Add quarterly dates
            current_date = next_date
            for _ in range(months_ahead // 3):
                # Move ahead 3 months
                month = current_date.month + 3
                year = current_date.year
                
                while month > 12:
                    month -= 12
                    year += 1
                
                # Make sure we don't exceed the day count for the month
                day = min(current_date.day, self.days_in_month(year, month))
                current_date = date(year, month, day)
                dates.append(current_date)
                
        elif subscription.billing_cycle == "Yearly":
            # Add yearly date if within the range
            year = next_date.year + 1
            if (year - datetime.now().year) <= (months_ahead // 12):
                # Make sure we don't exceed the day count for the month
                day = min(next_date.day, self.days_in_month(year, next_date.month))
                dates.append(date(year, next_date.month, day))
        
        return dates
    
    def days_in_month(self, year, month):
        """Get the number of days in a month"""
        if month == 2:  # February
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):  # Leap year
                return 29
            return 28
        elif month in [4, 6, 9, 11]:  # 30-day months
            return 30
        else:  # 31-day months
            return 31
    
    def on_date_clicked(self, qt_date):
        """Handle click on a calendar date"""
        py_date = qt_date.toPyDate()
        self.date_label.setText(f"Subscriptions due on {py_date.strftime('%B %d, %Y')}")
        
        # Recalculate monthly total for the new month if needed
        if py_date.month != self.calendar.selectedDate().toPyDate().month or py_date.year != self.calendar.selectedDate().toPyDate().year:
            self.recalculate_monthly_total(py_date)
            self.load_upcoming_subscriptions()  # Also reload upcoming for the new month
            
            # Update the upcoming label for the new month
            self.upcoming_label.setText(f"Upcoming in {py_date.strftime('%B %Y')}")
        
        # Clear the table
        self.sub_table.setRowCount(0)
        
        # If we have subscriptions for this date, show them
        if py_date in self.subscription_dates:
            subs = self.subscription_dates[py_date]
            
            # Set up the table with the subscriptions
            self.sub_table.setRowCount(len(subs))
            
            for row, sub in enumerate(subs):
                self.sub_table.setItem(row, 0, QTableWidgetItem(sub['name']))
                
                # Format amount with currency symbol
                amount_item = QTableWidgetItem(f"${sub['amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.sub_table.setItem(row, 1, amount_item)
                
                self.sub_table.setItem(row, 2, QTableWidgetItem(sub['cycle']))
                self.sub_table.setItem(row, 3, QTableWidgetItem(py_date.strftime("%Y-%m-%d")))
                
                # Color-code based on billing cycle
                if sub['cycle'] == 'Monthly':
                    color = QColor("#2196F3")  # Blue
                elif sub['cycle'] == 'Quarterly':
                    color = QColor("#4CAF50")  # Green
                elif sub['cycle'] == 'Yearly':
                    color = QColor("#F44336")  # Red
                else:
                    color = QColor("#757575")  # Gray
                
                # Apply light background color to the row
                for col in range(4):
                    item = self.sub_table.item(row, col)
                    color_with_alpha = QColor(color.red(), color.green(), color.blue(), 40)
                    item.setBackground(QBrush(color_with_alpha))
    
    def recalculate_monthly_total(self, current_date):
        """Recalculate total for a specific month"""
        month = current_date.month
        year = current_date.year
        self.current_month_total = 0.0
        
        # Sum all subscriptions for this month
        for py_date, subs in self.subscription_dates.items():
            if py_date.month == month and py_date.year == year:
                for sub in subs:
                    self.current_month_total += sub['amount']
        
        # Update the display if showing monthly totals
        if not self.show_yearly_total:
            self.update_total_display()
    
    def load_upcoming_subscriptions(self):
        """Load upcoming subscriptions for the current month"""
        selected_date = self.calendar.selectedDate().toPyDate()
        year = selected_date.year
        month = selected_date.month
        
        # Update the upcoming label for clarity
        self.upcoming_label.setText(f"Upcoming in {selected_date.strftime('%B %Y')}")
        
        upcoming_subs = []
        
        # Collect all subscriptions for this month
        for py_date, subs in self.subscription_dates.items():
            if py_date.year == year and py_date.month == month:
                for sub in subs:
                    upcoming_subs.append({
                        **sub, 
                        'due_date': py_date
                    })
        
        # Sort by date
        upcoming_subs.sort(key=lambda x: x['due_date'])
        
        # Update the table
        self.upcoming_table.setRowCount(len(upcoming_subs))
        
        for row, sub in enumerate(upcoming_subs):
            self.upcoming_table.setItem(row, 0, QTableWidgetItem(sub['name']))
            
            # Format amount with currency symbol
            amount_item = QTableWidgetItem(f"${sub['amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.upcoming_table.setItem(row, 1, amount_item)
            
            self.upcoming_table.setItem(row, 2, QTableWidgetItem(sub['cycle']))
            self.upcoming_table.setItem(row, 3, QTableWidgetItem(sub['due_date'].strftime("%Y-%m-%d")))
            
            # If this is the selected date, highlight the row
            if sub['due_date'] == selected_date:
                for col in range(4):
                    item = self.upcoming_table.item(row, col)
                    item.setBackground(QBrush(QColor(26, 35, 126, 80)))  # Primary color with alpha
            # Otherwise, color based on billing cycle
            else:
                if sub['cycle'] == 'Monthly':
                    color = QColor("#2196F3")  # Blue
                elif sub['cycle'] == 'Quarterly':
                    color = QColor("#4CAF50")  # Green
                elif sub['cycle'] == 'Yearly':
                    color = QColor("#F44336")  # Red
                else:
                    color = QColor("#757575")  # Gray
                
                # Apply light background color to the row
                for col in range(4):
                    item = self.upcoming_table.item(row, col)
                    color_with_alpha = QColor(color.red(), color.green(), color.blue(), 40)
                    item.setBackground(QBrush(color_with_alpha))
    
    def showEvent(self, event):
        """Handle dialog show event"""
        super().showEvent(event)
        # Select today's date by default
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.on_date_clicked(today)
        
        # Ensure upcoming is properly loaded
        self.load_upcoming_subscriptions()