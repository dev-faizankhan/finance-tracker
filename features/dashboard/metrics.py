"""Dashboard Metrics Calculations

Provides all metric calculations for the Streamlit dashboard.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from features.transactions.transactions import read_transactions, format_amount
from features.budgets.budgets import read_budgets, get_budget_data
from features.smart_assistant.smart_assistant import read_goals
from features.analytics.analytics import (
    calculate_total_income_month,
    calculate_total_spending,
    calculate_monthly_savings,
    calculate_savings_rate,
    calculate_overall_health_score,
    get_current_month,
    get_spending_by_category,
    get_income_by_source,
)


def get_previous_month() -> str:
    """Get previous month in YYYY-MM format.

    Returns:
        Previous month string
    """
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_previous_month = first_day_this_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m")


def calculate_balance_metrics() -> Dict:
    """Calculate balance section metrics.

    Returns:
        Dict with income, expenses, balance, and changes
    """
    current_month = get_current_month()
    previous_month = get_previous_month()

    # Current month
    current_income = calculate_total_income_month(current_month)
    current_expenses = calculate_total_spending(current_month)
    current_balance = current_income - current_expenses

    # Previous month
    previous_income = calculate_total_income_month(previous_month)
    previous_expenses = calculate_total_spending(previous_month)
    previous_balance = previous_income - previous_expenses

    # Calculate percentage changes
    income_change = ((current_income - previous_income) / previous_income * 100) if previous_income > 0 else 0
    expense_change = ((current_expenses - previous_expenses) / previous_expenses * 100) if previous_expenses > 0 else 0
    balance_change = ((current_balance - previous_balance) / abs(previous_balance) * 100) if previous_balance != 0 else 0

    return {
        'income': current_income,
        'expenses': current_expenses,
        'balance': current_balance,
        'income_change': income_change,
        'expense_change': expense_change,
        'balance_change': balance_change
    }


def get_budget_metrics() -> List[Dict]:
    """Get budget status metrics.

    Returns:
        List of budget status dicts
    """
    return get_budget_data()


def get_recent_transactions(limit: int = 20) -> List[Dict]:
    """Get recent transactions.

    Args:
        limit: Number of transactions to return

    Returns:
        List of recent transactions
    """
    transactions = read_transactions()
    # Sort by date descending
    transactions.sort(key=lambda x: x['date'], reverse=True)
    return transactions[:limit]


def get_spending_breakdown() -> Dict[str, int]:
    """Get spending breakdown by category for current month.

    Returns:
        Dict mapping category to amount in paisa
    """
    current_month = get_current_month()
    return get_spending_by_category(current_month)


def get_income_breakdown() -> Dict[str, int]:
    """Get income breakdown by source for current month.

    Returns:
        Dict mapping source to amount in paisa
    """
    current_month = get_current_month()
    return get_income_by_source(current_month)


def get_trend_data(months: int = 6) -> List[Dict]:
    """Get income vs expenses trend data.

    Args:
        months: Number of months to include

    Returns:
        List of dicts with month, income, expenses
    """
    transactions = read_transactions()

    # Get last N months
    today = datetime.now()
    months_data = []

    for i in range(months - 1, -1, -1):
        # Calculate month
        month_date = today - timedelta(days=i * 30)
        month_str = month_date.strftime("%Y-%m")

        # Calculate income and expenses for this month
        month_transactions = [t for t in transactions if t['date'].startswith(month_str)]
        income = sum(t['amount_paisa'] for t in month_transactions if t['type'] == 'income')
        expenses = sum(t['amount_paisa'] for t in month_transactions if t['type'] == 'expense')

        months_data.append({
            'month': month_date.strftime("%b %Y"),
            'month_key': month_str,
            'income': income,
            'expenses': expenses
        })

    return months_data


def get_financial_health_metrics() -> Dict:
    """Get financial health metrics.

    Returns:
        Dict with score and rating
    """
    score = calculate_overall_health_score()

    if score >= 80:
        rating = "Excellent"
        color = "green"
    elif score >= 60:
        rating = "Good"
        color = "blue"
    elif score >= 40:
        rating = "Fair"
        color = "orange"
    else:
        rating = "Poor"
        color = "red"

    return {
        'score': score,
        'rating': rating,
        'color': color
    }


def get_top_spending_transactions(limit: int = 5) -> List[Dict]:
    """Get top spending transactions for current month.

    Args:
        limit: Number of transactions to return

    Returns:
        List of top transactions
    """
    current_month = get_current_month()
    transactions = read_transactions()

    # Filter to current month expenses
    month_expenses = [
        t for t in transactions
        if t['date'].startswith(current_month) and t['type'] == 'expense'
    ]

    # Sort by amount descending
    month_expenses.sort(key=lambda x: x['amount_paisa'], reverse=True)

    # Calculate percentage of total
    total_expenses = sum(t['amount_paisa'] for t in month_expenses)

    result = []
    for trans in month_expenses[:limit]:
        percentage = (trans['amount_paisa'] / total_expenses * 100) if total_expenses > 0 else 0
        result.append({
            **trans,
            'percentage': percentage
        })

    return result


def get_savings_metrics() -> Dict:
    """Get savings metrics for current month.

    Returns:
        Dict with savings information
    """
    current_month = get_current_month()

    savings = calculate_monthly_savings(current_month)
    savings_rate = calculate_savings_rate(current_month)

    # Calculate projected annual savings
    projected_annual = savings * 12

    # Get savings goals
    goals = read_goals()
    savings_goals = [g for g in goals if g['goal_type'] == 'savings']

    return {
        'monthly_savings': savings,
        'savings_rate': savings_rate,
        'projected_annual': projected_annual,
        'active_goals': len(savings_goals)
    }


def get_dashboard_summary() -> Dict:
    """Get complete dashboard summary.

    Returns:
        Dict with all dashboard data
    """
    transactions = read_transactions()
    budgets = read_budgets()
    goals = read_goals()

    balance_metrics = calculate_balance_metrics()
    health_metrics = get_financial_health_metrics()

    return {
        'total_transactions': len(transactions),
        'total_budgets': len(budgets),
        'total_goals': len(goals),
        'balance': balance_metrics['balance'],
        'health_score': health_metrics['score'],
        'health_rating': health_metrics['rating']
    }


def filter_transactions_by_date(
    transactions: List[Dict],
    start_date: str,
    end_date: str
) -> List[Dict]:
    """Filter transactions by date range.

    Args:
        transactions: List of transactions
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Filtered transactions
    """
    return [
        t for t in transactions
        if start_date <= t['date'] <= end_date
    ]


def filter_transactions_by_category(
    transactions: List[Dict],
    categories: List[str]
) -> List[Dict]:
    """Filter transactions by categories.

    Args:
        transactions: List of transactions
        categories: List of categories to include

    Returns:
        Filtered transactions
    """
    if not categories:
        return transactions
    return [t for t in transactions if t['category'] in categories]


def filter_transactions_by_type(
    transactions: List[Dict],
    trans_type: str
) -> List[Dict]:
    """Filter transactions by type.

    Args:
        transactions: List of transactions
        trans_type: Transaction type ('income', 'expense', or 'all')

    Returns:
        Filtered transactions
    """
    if trans_type == 'all':
        return transactions
    return [t for t in transactions if t['type'] == trans_type]
