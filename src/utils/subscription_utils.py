from datetime import datetime, date, timedelta
from ..models.subscription import Subscription

def calculate_next_billing_date(subscription):
    """Calculate the next billing date based on the current one"""
    current_date = subscription.next_billing_date
    
    if subscription.billing_cycle == "Monthly":
        # Move to next month
        month = current_date.month + 1
        year = current_date.year
        
        if month > 12:
            month = 1
            year += 1
        
        # Make sure we don't exceed the day count for the month
        day = min(current_date.day, days_in_month(year, month))
        next_date = date(year, month, day)
        
    elif subscription.billing_cycle == "Quarterly":
        # Move ahead 3 months
        month = current_date.month + 3
        year = current_date.year
        
        while month > 12:
            month -= 12
            year += 1
        
        # Make sure we don't exceed the day count for the month
        day = min(current_date.day, days_in_month(year, month))
        next_date = date(year, month, day)
        
    elif subscription.billing_cycle == "Yearly":
        # Move ahead 1 year
        year = current_date.year + 1
        
        # Make sure we don't exceed the day count for the month
        day = min(current_date.day, days_in_month(year, current_date.month))
        next_date = date(year, current_date.month, day)
    
    else:
        # Default: move ahead 1 month
        month = current_date.month + 1
        year = current_date.year
        
        if month > 12:
            month = 1
            year += 1
        
        day = min(current_date.day, days_in_month(year, month))
        next_date = date(year, month, day)
    
    return next_date

def days_in_month(year, month):
    """Get the number of days in a month"""
    if month == 2:  # February
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):  # Leap year
            return 29
        return 28
    elif month in [4, 6, 9, 11]:  # 30-day months
        return 30
    else:  # 31-day months
        return 31

def mark_subscription_as_paid(session, subscription_id):
    """Mark a subscription as paid and update its next billing date"""
    subscription = session.query(Subscription).get(subscription_id)
    if subscription:
        # Calculate next billing date
        next_date = calculate_next_billing_date(subscription)
        
        # Update the subscription
        subscription.next_billing_date = next_date
        
        # Commit the changes
        session.commit()
        
        return True
    return False