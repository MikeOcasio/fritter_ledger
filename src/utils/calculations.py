from datetime import datetime, timedelta
from sqlalchemy import func

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