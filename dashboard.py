"""Personal Finance Tracker - Streamlit Dashboard

Web-based dashboard for visualizing financial data with interactive charts and metrics.

Usage:
    streamlit run dashboard.py
"""

import sys
from pathlib import Path
import streamlit as st

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import dashboard modules
from features.dashboard.metrics import (
    calculate_balance_metrics,
    get_budget_metrics,
    get_recent_transactions,
    get_spending_breakdown,
    get_income_breakdown,
    get_trend_data,
    get_financial_health_metrics,
    get_top_spending_transactions,
    get_savings_metrics,
    get_dashboard_summary,
    filter_transactions_by_date,
    filter_transactions_by_category,
    filter_transactions_by_type
)
from features.dashboard.charts import (
    create_spending_pie_chart,
    create_income_pie_chart,
    create_trend_chart,
    create_budget_bar_chart,
    create_savings_gauge,
    create_category_bar_chart
)
from features.dashboard.components import (
    format_currency,
    display_metric_card,
    display_budget_progress,
    display_transactions_table,
    display_top_transactions,
    display_health_score,
    display_savings_summary,
    display_empty_state,
    create_filter_sidebar,
    display_quick_stats,
    apply_custom_css
)
from features.transactions.transactions import read_transactions


# Page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Main dashboard application."""

    # Apply custom CSS
    apply_custom_css()

    # Header
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1>💰 Personal Finance Dashboard</h1>
        <p style='font-size: 18px; color: #666;'>
            Track • Budget • Analyze • Save
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Get dashboard summary
    try:
        summary = get_dashboard_summary()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    # Quick statistics row
    st.subheader("Quick Overview")
    display_quick_stats(summary)

    st.divider()

    # =================================================================
    # SECTION 1: Balance Metrics
    # =================================================================
    st.header("💵 Financial Overview")

    try:
        balance_metrics = calculate_balance_metrics()

        col1, col2, col3 = st.columns(3)

        with col1:
            delta_color = "normal" if balance_metrics['income_change'] >= 0 else "inverse"
            st.metric(
                label="Total Income",
                value=format_currency(balance_metrics['income']),
                delta=f"{balance_metrics['income_change']:+.1f}% vs last month",
                delta_color=delta_color
            )

        with col2:
            delta_color = "normal" if balance_metrics['balance_change'] >= 0 else "inverse"
            st.metric(
                label="Current Balance",
                value=format_currency(balance_metrics['balance']),
                delta=f"{balance_metrics['balance_change']:+.1f}% vs last month",
                delta_color=delta_color
            )

        with col3:
            delta_color = "inverse" if balance_metrics['expense_change'] >= 0 else "normal"
            st.metric(
                label="Total Expenses",
                value=format_currency(balance_metrics['expenses']),
                delta=f"{balance_metrics['expense_change']:+.1f}% vs last month",
                delta_color=delta_color
            )

    except Exception as e:
        st.error(f"Error calculating balance metrics: {e}")

    st.divider()

    # =================================================================
    # SECTION 2: Budget Status & Savings
    # =================================================================
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Budget Overview")

        try:
            budget_data = get_budget_metrics()

            if budget_data:
                for budget in budget_data:
                    display_budget_progress(budget)
                    st.write("")  # Add spacing
            else:
                display_empty_state("No budgets set. Set budgets to track your spending!")

        except Exception as e:
            st.error(f"Error loading budget data: {e}")

    with col_right:
        st.subheader("💰 Savings Summary")

        try:
            savings_data = get_savings_metrics()
            display_savings_summary(savings_data)

            # Add savings gauge
            st.write("")
            st.plotly_chart(
                create_savings_gauge(savings_data['savings_rate']),
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error loading savings data: {e}")

    st.divider()

    # =================================================================
    # SECTION 3: Charts Row 1 - Spending & Income Breakdown
    # =================================================================
    st.header("📈 Spending & Income Analysis")

    col1, col2 = st.columns(2)

    with col1:
        try:
            spending_data = get_spending_breakdown()
            if spending_data:
                fig = create_spending_pie_chart(spending_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                display_empty_state("No expense data for this month")
        except Exception as e:
            st.error(f"Error creating spending chart: {e}")

    with col2:
        try:
            income_data = get_income_breakdown()
            if income_data:
                fig = create_income_pie_chart(income_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                display_empty_state("No income data for this month")
        except Exception as e:
            st.error(f"Error creating income chart: {e}")

    st.divider()

    # =================================================================
    # SECTION 4: Trend Chart & Financial Health
    # =================================================================
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📉 Income vs Expenses Trend")

        try:
            trend_data = get_trend_data(months=6)
            if trend_data:
                fig = create_trend_chart(trend_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                display_empty_state("Not enough data to show trends")
        except Exception as e:
            st.error(f"Error creating trend chart: {e}")

    with col2:
        st.subheader("🎯 Financial Health")

        try:
            health_metrics = get_financial_health_metrics()
            display_health_score(health_metrics['score'], health_metrics['rating'])

            # Add health breakdown
            st.write("")
            st.caption("**Score Components:**")
            st.caption("• Savings Rate (30 pts)")
            st.caption("• Budget Adherence (25 pts)")
            st.caption("• Balance Status (25 pts)")
            st.caption("• Financial Consistency (20 pts)")

        except Exception as e:
            st.error(f"Error calculating health score: {e}")

    st.divider()

    # =================================================================
    # SECTION 5: Top Spending Transactions
    # =================================================================
    st.header("💸 Top Spending This Month")

    try:
        top_transactions = get_top_spending_transactions(limit=5)
        if top_transactions:
            display_top_transactions(top_transactions)
        else:
            display_empty_state("No expense transactions this month")
    except Exception as e:
        st.error(f"Error loading top transactions: {e}")

    st.divider()

    # =================================================================
    # SECTION 6: Recent Transactions
    # =================================================================
    st.header("📝 Recent Transactions")

    # Add filter controls
    col1, col2, col3 = st.columns(3)

    with col1:
        trans_type_filter = st.selectbox(
            "Filter by type",
            options=["All", "Income", "Expense"],
            index=0,
            key="trans_filter"
        )

    with col2:
        limit = st.slider(
            "Number of transactions",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            key="limit_slider"
        )

    with col3:
        if st.button("🔄 Refresh Data", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()

    try:
        transactions = get_recent_transactions(limit=limit)

        # Apply type filter
        if trans_type_filter != "All":
            transactions = filter_transactions_by_type(transactions, trans_type_filter.lower())

        if transactions:
            display_transactions_table(transactions)
            st.caption(f"Showing {len(transactions)} transactions")
        else:
            display_empty_state("No transactions found")

    except Exception as e:
        st.error(f"Error loading transactions: {e}")

    # =================================================================
    # Footer
    # =================================================================
    st.divider()
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666;'>
        <p>Personal Finance Tracker Dashboard v1.0</p>
        <p style='font-size: 12px;'>Built with Streamlit • Data updates in real-time</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
