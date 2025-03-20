from datetime import datetime, timedelta
from sqlalchemy import func
from ..models.subscription import Subscription

def calculate_total_expenses(session, start_date=None, end_date=None):
    from ..models.expense import Expense
    query = session.query(func.sum(Expense.amount))
    
    if start_date and end_date:
        query = query.filter(Expense.date.between(start_date, end_date))
    
    return query.scalar() or 0.0

def calculate_total_income(session, start_date=None, end_date=None):
    from ..models.income import Income
    query = session.query(func.sum(Income.amount))
    
    if start_date and end_date:
        query = query.filter(Income.date.between(start_date, end_date))
    
    return query.scalar() or 0.0

def calculate_monthly_subscriptions(session):
    from ..models.subscription import Subscription
    query = session.query(func.sum(Subscription.amount))\
        .filter(Subscription.billing_cycle == 'Monthly')
    return query.scalar() or 0.0

def calculate_subscription_total(session, period):
    """Calculate total subscription costs for the given period"""
    from ..models.subscription import Subscription
    
    # Get all subscriptions
    subscriptions = session.query(Subscription).all()
    
    # Calculate total subscription cost for the period
    total = 0.0
    
    for sub in subscriptions:
        # Calculate cost based on billing cycle and period
        amount = sub.amount
        
        if sub.billing_cycle == "Monthly":
            # Monthly subscriptions
            if period in ["This Month", "Last Month"]:
                total += amount
            elif period in ["This Quarter", "Last Quarter"]:
                total += amount * 3  # 3 months in a quarter
            elif period in ["This Year", "Last Year"]:
                total += amount * 12  # 12 months in a year
            elif period == "Last 6 Months":
                total += amount * 6
            elif period == "All Time":
                # Calculate months since creation
                # For simplicity, just use 24 months as an estimate
                total += amount * 24
                
        elif sub.billing_cycle == "Quarterly":
            # Quarterly subscriptions
            if period in ["This Month", "Last Month"]:
                total += amount / 3  # Prorated for one month
            elif period in ["This Quarter", "Last Quarter"]:
                total += amount
            elif period in ["This Year", "Last Year"]:
                total += amount * 4  # 4 quarters in a year
            elif period == "Last 6 Months":
                total += amount * 2  # 2 quarters in 6 months
            elif period == "All Time":
                # Calculate quarters since creation (estimate)
                total += amount * 8  # 8 quarters = 2 years
                
        elif sub.billing_cycle == "Yearly":
            # Yearly subscriptions
            if period in ["This Month", "Last Month"]:
                total += amount / 12  # Prorated for one month
            elif period in ["This Quarter", "Last Quarter"]:
                total += amount / 4  # Prorated for one quarter
            elif period in ["This Year", "Last Year"]:
                total += amount
            elif period == "Last 6 Months":
                total += amount / 2  # Prorated for 6 months
            elif period == "All Time":
                # Calculate years since creation (estimate)
                total += amount * 2  # 2 years
    
    return total