"""Dashboard UI Components

Provides reusable Streamlit UI components for the dashboard.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict


def format_currency(amount_paisa: int) -> str:
    """Format amount in paisa to rupees string.

    Args:
        amount_paisa: Amount in paisa

    Returns:
        Formatted currency string
    """
    rupees = amount_paisa / 100
    return f"Rs {rupees:,.2f}"


def display_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Display a metric card.

    Args:
        label: Metric label
        value: Metric value
        delta: Change value
        delta_color: Color for delta (normal, inverse, off)
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def display_budget_progress(budget: Dict):
    """Display budget progress bar.

    Args:
        budget: Budget dict with category, spent, limit, utilization
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        # Determine color
        if budget['utilization'] < 70:
            color = "green"
        elif budget['utilization'] < 100:
            color = "orange"
        else:
            color = "red"

        # Display progress bar
        progress_value = min(budget['utilization'] / 100, 1.0)
        st.progress(progress_value)

        # Display amounts
        spent_str = format_currency(budget['spent_paisa'])
        limit_str = format_currency(budget['limit_paisa'])
        st.caption(f"{budget['category']}: {spent_str} / {limit_str}")

    with col2:
        # Display utilization percentage
        st.metric("", f"{budget['utilization']:.1f}%")


def display_transactions_table(transactions: List[Dict]):
    """Display transactions as a table.

    Args:
        transactions: List of transaction dicts
    """
    if not transactions:
        st.info("No transactions found")
        return

    # Convert to DataFrame
    df_data = []
    for trans in transactions:
        df_data.append({
            'Date': trans['date'],
            'Type': trans['type'].capitalize(),
            'Category': trans['category'],
            'Description': trans['description'],
            'Amount': trans['amount_paisa'] / 100
        })

    df = pd.DataFrame(df_data)

    # Display with custom formatting
    st.dataframe(
        df,
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="YYYY-MM-DD"
            ),
            "Type": st.column_config.TextColumn(
                "Type",
                width="small"
            ),
            "Category": st.column_config.TextColumn(
                "Category",
                width="medium"
            ),
            "Description": st.column_config.TextColumn(
                "Description",
                width="large"
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount (Rs)",
                format="Rs %.2f"
            )
        },
        hide_index=True,
        use_container_width=True
    )


def display_top_transactions(transactions: List[Dict]):
    """Display top transactions with percentages.

    Args:
        transactions: List of transaction dicts with percentage
    """
    if not transactions:
        st.info("No transactions found")
        return

    for i, trans in enumerate(transactions, 1):
        col1, col2, col3 = st.columns([0.5, 3, 1])

        with col1:
            st.write(f"**#{i}**")

        with col2:
            st.write(f"**{trans['description']}**")
            st.caption(f"{trans['date']} • {trans['category']}")

        with col3:
            amount_str = format_currency(trans['amount_paisa'])
            st.write(f"**{amount_str}**")
            st.caption(f"{trans['percentage']:.1f}%")

        if i < len(transactions):
            st.divider()


def display_health_score(score: int, rating: str):
    """Display financial health score.

    Args:
        score: Health score (0-100)
        rating: Rating text (Excellent/Good/Fair/Poor)
    """
    # Determine color
    if score >= 80:
        color = "green"
        emoji = "🌟"
    elif score >= 60:
        color = "blue"
        emoji = "⭐"
    elif score >= 40:
        color = "orange"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "❗"

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Financial Health", f"{score}/100")

    with col2:
        st.progress(score / 100)
        st.caption(f"{emoji} {rating}")


def display_savings_summary(savings_data: Dict):
    """Display savings summary.

    Args:
        savings_data: Dict with savings metrics
    """
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Monthly Savings",
            format_currency(savings_data['monthly_savings'])
        )

    with col2:
        st.metric(
            "Savings Rate",
            f"{savings_data['savings_rate']:.1f}%"
        )

    st.caption(f"Projected Annual Savings: {format_currency(savings_data['projected_annual'])}")

    if savings_data['active_goals'] > 0:
        st.caption(f"Active Savings Goals: {savings_data['active_goals']}")


def display_empty_state(message: str):
    """Display empty state message.

    Args:
        message: Message to display
    """
    st.info(f"📊 {message}")


def create_filter_sidebar():
    """Create sidebar with filters.

    Returns:
        Dict with filter values
    """
    st.sidebar.header("Filters")

    # Date range filter
    st.sidebar.subheader("Date Range")
    use_date_filter = st.sidebar.checkbox("Enable date filter", value=False)

    start_date = None
    end_date = None
    if use_date_filter:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("From", key="start_date")
        with col2:
            end_date = st.date_input("To", key="end_date")

    # Transaction type filter
    st.sidebar.subheader("Transaction Type")
    trans_type = st.sidebar.selectbox(
        "Type",
        options=["All", "Income", "Expense"],
        index=0
    )

    # Category filter
    st.sidebar.subheader("Categories")
    use_category_filter = st.sidebar.checkbox("Filter by category", value=False)

    categories = []
    if use_category_filter:
        from features.transactions.transactions import EXPENSE_CATEGORIES, INCOME_CATEGORIES
        all_categories = list(EXPENSE_CATEGORIES) + list(INCOME_CATEGORIES)
        categories = st.sidebar.multiselect(
            "Select categories",
            options=all_categories
        )

    return {
        'use_date_filter': use_date_filter,
        'start_date': str(start_date) if start_date else None,
        'end_date': str(end_date) if end_date else None,
        'trans_type': trans_type.lower(),
        'use_category_filter': use_category_filter,
        'categories': categories
    }


def display_quick_stats(summary: Dict):
    """Display quick statistics.

    Args:
        summary: Dict with summary statistics
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Transactions", summary['total_transactions'])

    with col2:
        st.metric("Budgets", summary['total_budgets'])

    with col3:
        st.metric("Goals", summary['total_goals'])

    with col4:
        st.metric("Health Score", f"{summary['health_score']}/100")


def apply_custom_css():
    """Apply custom CSS styling."""
    st.markdown("""
    <style>
        /* Main container */
        .main {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Metric cards */
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Progress bars */
        .stProgress > div > div {
            height: 20px;
            border-radius: 10px;
        }

        /* Headers */
        h1 {
            color: #1f77b4;
            font-weight: 700;
        }

        h2 {
            color: #2c3e50;
            font-weight: 600;
            margin-top: 20px;
        }

        h3 {
            color: #34495e;
            font-weight: 500;
        }

        /* Cards */
        .element-container {
            margin-bottom: 10px;
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: #f8f9fa;
        }

        /* Buttons */
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            font-weight: 500;
        }

        /* Dataframe */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }
    </style>
    """, unsafe_allow_html=True)
