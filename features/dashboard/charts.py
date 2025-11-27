"""Dashboard Chart Generation

Provides chart generation functions using Plotly for the dashboard.
"""

from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go


def create_spending_pie_chart(spending_data: Dict[str, int]) -> go.Figure:
    """Create pie chart for spending by category.

    Args:
        spending_data: Dict mapping category to amount in paisa

    Returns:
        Plotly figure
    """
    if not spending_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No spending data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    categories = list(spending_data.keys())
    amounts = [amount / 100 for amount in spending_data.values()]  # Convert to rupees

    fig = px.pie(
        values=amounts,
        names=categories,
        title="Spending by Category",
        hole=0.3,  # Donut chart
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Rs %{value:.2f}<br>%{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        height=400
    )

    return fig


def create_income_pie_chart(income_data: Dict[str, int]) -> go.Figure:
    """Create pie chart for income by source.

    Args:
        income_data: Dict mapping source to amount in paisa

    Returns:
        Plotly figure
    """
    if not income_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No income data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    sources = list(income_data.keys())
    amounts = [amount / 100 for amount in income_data.values()]  # Convert to rupees

    fig = px.pie(
        values=amounts,
        names=sources,
        title="Income by Source",
        hole=0.3,  # Donut chart
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Rs %{value:.2f}<br>%{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        height=400
    )

    return fig


def create_trend_chart(trend_data: List[Dict]) -> go.Figure:
    """Create line chart for income vs expenses trend.

    Args:
        trend_data: List of dicts with month, income, expenses

    Returns:
        Plotly figure
    """
    if not trend_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No trend data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    months = [item['month'] for item in trend_data]
    income = [item['income'] / 100 for item in trend_data]  # Convert to rupees
    expenses = [item['expenses'] / 100 for item in trend_data]  # Convert to rupees

    fig = go.Figure()

    # Add income line
    fig.add_trace(go.Scatter(
        x=months,
        y=income,
        mode='lines+markers',
        name='Income',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8),
        hovertemplate='<b>Income</b><br>%{x}<br>Rs %{y:.2f}<extra></extra>'
    ))

    # Add expenses line
    fig.add_trace(go.Scatter(
        x=months,
        y=expenses,
        mode='lines+markers',
        name='Expenses',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8),
        hovertemplate='<b>Expenses</b><br>%{x}<br>Rs %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Income vs Expenses Trend",
        xaxis_title="Month",
        yaxis_title="Amount (Rs)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Add grid
    fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig


def create_budget_bar_chart(budget_data: List[Dict]) -> go.Figure:
    """Create bar chart for budget utilization.

    Args:
        budget_data: List of budget status dicts

    Returns:
        Plotly figure
    """
    if not budget_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No budget data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    categories = [b['category'] for b in budget_data]
    utilization = [b['utilization'] for b in budget_data]

    # Color code by utilization
    colors = []
    for util in utilization:
        if util < 70:
            colors.append('#2ecc71')  # Green
        elif util < 100:
            colors.append('#f39c12')  # Yellow/Orange
        else:
            colors.append('#e74c3c')  # Red

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=utilization,
            marker_color=colors,
            text=[f"{u:.1f}%" for u in utilization],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Utilization: %{y:.1f}%<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Budget Utilization",
        xaxis_title="Category",
        yaxis_title="Utilization (%)",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Add reference line at 100%
    fig.add_hline(y=100, line_dash="dash", line_color="red", opacity=0.5)

    # Add grid
    fig.update_xaxis(showgrid=False)
    fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig


def create_savings_gauge(savings_rate: float) -> go.Figure:
    """Create gauge chart for savings rate.

    Args:
        savings_rate: Savings rate percentage

    Returns:
        Plotly figure
    """
    # Determine color based on savings rate
    if savings_rate >= 30:
        color = "#2ecc71"  # Green
    elif savings_rate >= 20:
        color = "#3498db"  # Blue
    elif savings_rate >= 10:
        color = "#f39c12"  # Orange
    else:
        color = "#e74c3c"  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=savings_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Savings Rate", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 10], 'color': '#ffcccc'},
                {'range': [10, 20], 'color': '#ffe6cc'},
                {'range': [20, 30], 'color': '#cce6ff'},
                {'range': [30, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 20
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


def create_category_bar_chart(spending_data: Dict[str, int]) -> go.Figure:
    """Create horizontal bar chart for spending by category.

    Args:
        spending_data: Dict mapping category to amount in paisa

    Returns:
        Plotly figure
    """
    if not spending_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No spending data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    # Sort by amount descending
    sorted_items = sorted(spending_data.items(), key=lambda x: x[1], reverse=True)
    categories = [item[0] for item in sorted_items]
    amounts = [item[1] / 100 for item in sorted_items]  # Convert to rupees

    fig = go.Figure(data=[
        go.Bar(
            y=categories,
            x=amounts,
            orientation='h',
            marker_color='#3498db',
            text=[f"Rs {a:.2f}" for a in amounts],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Rs %{x:.2f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Spending by Category",
        xaxis_title="Amount (Rs)",
        yaxis_title="Category",
        height=max(300, len(categories) * 40),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Add grid
    fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxis(showgrid=False)

    return fig
