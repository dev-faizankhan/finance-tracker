"""Financial Analytics Feature

Provides comprehensive financial analysis including spending patterns,
income trends, savings analysis, and financial health scoring.
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from calendar import monthrange
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Import from other features
import sys
sys.path.append(str(Path(__file__).parent.parent))
from transactions.transactions import (
    read_transactions,
    format_amount,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    filter_by_type,
    filter_by_category,
    calculate_total_income as trans_total_income,
    calculate_total_expenses as trans_total_expenses
)
from budgets.budgets import (
    read_budgets,
    get_budget_data
)

console = Console()


# ============================================================================
# TIME PERIOD & DATA AGGREGATION FUNCTIONS
# ============================================================================

def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")


def get_last_month() -> str:
    """Get previous month in YYYY-MM format."""
    today = datetime.now()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    return last_month.strftime("%Y-%m")


def get_month_name(month_str: str) -> str:
    """Convert YYYY-MM to month name.

    Args:
        month_str: Month in YYYY-MM format

    Returns:
        Month name like 'November 2024'
    """
    try:
        date_obj = datetime.strptime(month_str + "-01", "%Y-%m-%d")
        return date_obj.strftime("%B %Y")
    except:
        return month_str


def filter_transactions_by_month(transactions: List[Dict], month: str) -> List[Dict]:
    """Filter transactions for a specific month.

    Args:
        transactions: List of transaction dictionaries
        month: Month in YYYY-MM format

    Returns:
        Filtered transactions
    """
    return [t for t in transactions if t['date'].startswith(month)]


def get_current_month_data() -> Dict:
    """Get all transaction data for current month."""
    transactions = read_transactions()
    current_month = get_current_month()
    return filter_transactions_by_month(transactions, current_month)


def get_last_month_data() -> Dict:
    """Get all transaction data for previous month."""
    transactions = read_transactions()
    last_month = get_last_month()
    return filter_transactions_by_month(transactions, last_month)


def get_last_n_months_data(n: int) -> Dict[str, List[Dict]]:
    """Get data for last N months grouped by month.

    Args:
        n: Number of months to retrieve

    Returns:
        Dictionary mapping month strings to transaction lists
    """
    transactions = read_transactions()
    result = {}

    today = datetime.now()
    for i in range(n):
        if i == 0:
            month_date = today
        else:
            # Go back i months
            month_date = today.replace(day=1) - timedelta(days=1)
            for _ in range(i - 1):
                month_date = month_date.replace(day=1) - timedelta(days=1)

        month_str = month_date.strftime("%Y-%m")
        result[month_str] = filter_transactions_by_month(transactions, month_str)

    return result


def get_days_in_month(month: str) -> int:
    """Get number of days in a month.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Number of days in the month
    """
    try:
        year, mon = map(int, month.split('-'))
        return monthrange(year, mon)[1]
    except:
        return 30  # Default fallback


# ============================================================================
# SPENDING CALCULATION FUNCTIONS
# ============================================================================

def calculate_total_spending(month: str) -> int:
    """Calculate total expenses for a month in paisa.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Total spending in paisa
    """
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    expenses = filter_by_type(month_transactions, "expense")
    return sum(t['amount_paisa'] for t in expenses)


def calculate_category_spending(category: str, month: str) -> int:
    """Calculate spending for a specific category in a month.

    Args:
        category: Category name
        month: Month in YYYY-MM format

    Returns:
        Total spending in paisa
    """
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    expenses = filter_by_type(month_transactions, "expense")
    category_expenses = filter_by_category(expenses, category)
    return sum(t['amount_paisa'] for t in category_expenses)


def calculate_category_percentage(category_amount: int, total: int) -> float:
    """Calculate category spending as percentage of total.

    Args:
        category_amount: Category spending amount
        total: Total spending amount

    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (category_amount / total) * 100


def calculate_average_daily_spending(month: str) -> int:
    """Calculate average daily spending (burn rate) for a month.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Average daily spending in paisa
    """
    total = calculate_total_spending(month)
    days = get_days_in_month(month)
    return total // days if days > 0 else 0


def calculate_burn_rate() -> int:
    """Calculate current burn rate (average daily spending).

    Returns:
        Average daily spending in paisa
    """
    current_month = get_current_month()
    return calculate_average_daily_spending(current_month)


def get_top_spending_categories(n: int = 3, month: Optional[str] = None) -> List[Tuple[str, int]]:
    """Get top N spending categories.

    Args:
        n: Number of top categories to return
        month: Month in YYYY-MM format (None for current month)

    Returns:
        List of tuples (category, amount_paisa) sorted by amount
    """
    if month is None:
        month = get_current_month()

    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    expenses = filter_by_type(month_transactions, "expense")

    # Calculate spending per category
    category_spending = {}
    for expense in expenses:
        cat = expense['category']
        category_spending[cat] = category_spending.get(cat, 0) + expense['amount_paisa']

    # Sort and return top N
    sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
    return sorted_categories[:n]


def get_spending_by_category(month: Optional[str] = None) -> Dict[str, int]:
    """Get spending amount for all categories.

    Args:
        month: Month in YYYY-MM format (None for current month)

    Returns:
        Dictionary mapping category to amount in paisa
    """
    if month is None:
        month = get_current_month()

    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    expenses = filter_by_type(month_transactions, "expense")

    category_spending = {}
    for expense in expenses:
        cat = expense['category']
        category_spending[cat] = category_spending.get(cat, 0) + expense['amount_paisa']

    return category_spending


# ============================================================================
# INCOME CALCULATION FUNCTIONS
# ============================================================================

def calculate_total_income_month(month: str) -> int:
    """Calculate total income for a month in paisa.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Total income in paisa
    """
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    income = filter_by_type(month_transactions, "income")
    return sum(t['amount_paisa'] for t in income)


def calculate_income_by_source(source: str, month: str) -> int:
    """Calculate income from a specific source in a month.

    Args:
        source: Income source/category
        month: Month in YYYY-MM format

    Returns:
        Income amount in paisa
    """
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    income = filter_by_type(month_transactions, "income")
    source_income = filter_by_category(income, source)
    return sum(t['amount_paisa'] for t in source_income)


def get_income_by_source(month: Optional[str] = None) -> Dict[str, int]:
    """Get income amounts for all sources.

    Args:
        month: Month in YYYY-MM format (None for current month)

    Returns:
        Dictionary mapping source to amount in paisa
    """
    if month is None:
        month = get_current_month()

    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, month)
    income = filter_by_type(month_transactions, "income")

    source_income = {}
    for inc in income:
        src = inc['category']
        source_income[src] = source_income.get(src, 0) + inc['amount_paisa']

    return source_income


def calculate_average_income(months: int = 3) -> int:
    """Calculate average monthly income over N months.

    Args:
        months: Number of months to average

    Returns:
        Average monthly income in paisa
    """
    month_data = get_last_n_months_data(months)
    total_income = 0

    for month_transactions in month_data.values():
        income = filter_by_type(month_transactions, "income")
        total_income += sum(t['amount_paisa'] for t in income)

    return total_income // months if months > 0 else 0


def calculate_income_stability() -> float:
    """Calculate income stability score (0-100).

    Higher score means more stable income.
    Based on variance in monthly income over last 3 months.

    Returns:
        Stability score (0-100)
    """
    month_data = get_last_n_months_data(3)

    if len(month_data) < 2:
        return 100.0  # Not enough data, assume stable

    incomes = []
    for month_transactions in month_data.values():
        income = filter_by_type(month_transactions, "income")
        month_income = sum(t['amount_paisa'] for t in income)
        incomes.append(month_income)

    if not incomes or max(incomes) == 0:
        return 100.0

    # Calculate coefficient of variation
    avg = sum(incomes) / len(incomes)
    if avg == 0:
        return 100.0

    variance = sum((x - avg) ** 2 for x in incomes) / len(incomes)
    std_dev = variance ** 0.5
    cv = std_dev / avg

    # Convert to score (lower CV = higher stability)
    # CV of 0 = 100%, CV of 0.5 = 50%, CV of 1+ = 0%
    stability = max(0, 100 - (cv * 100))
    return min(100, stability)


# ============================================================================
# SAVINGS CALCULATION FUNCTIONS
# ============================================================================

def calculate_monthly_savings(month: str) -> int:
    """Calculate savings for a month (income - expenses).

    Args:
        month: Month in YYYY-MM format

    Returns:
        Savings in paisa (can be negative)
    """
    income = calculate_total_income_month(month)
    expenses = calculate_total_spending(month)
    return income - expenses


def calculate_savings_rate(month: str) -> float:
    """Calculate savings rate as percentage of income.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Savings rate percentage
    """
    income = calculate_total_income_month(month)
    if income == 0:
        return 0.0

    savings = calculate_monthly_savings(month)
    return (savings / income) * 100


def calculate_average_savings(months: int = 3) -> int:
    """Calculate average monthly savings over N months.

    Args:
        months: Number of months to average

    Returns:
        Average savings in paisa
    """
    month_data = get_last_n_months_data(months)
    total_savings = 0

    for month_str in month_data.keys():
        total_savings += calculate_monthly_savings(month_str)

    return total_savings // months if months > 0 else 0


def calculate_projected_annual_savings() -> int:
    """Calculate projected annual savings based on current rate.

    Returns:
        Projected annual savings in paisa
    """
    current_month = get_current_month()
    monthly_savings = calculate_monthly_savings(current_month)
    return monthly_savings * 12


# ============================================================================
# TREND CALCULATION FUNCTIONS
# ============================================================================

def calculate_month_over_month_change(category: Optional[str] = None) -> float:
    """Calculate percentage change from last month.

    Args:
        category: Specific category or None for total spending

    Returns:
        Percentage change (positive = increase, negative = decrease)
    """
    current_month = get_current_month()
    last_month = get_last_month()

    if category:
        current = calculate_category_spending(category, current_month)
        previous = calculate_category_spending(category, last_month)
    else:
        current = calculate_total_spending(current_month)
        previous = calculate_total_spending(last_month)

    if previous == 0:
        return 0.0 if current == 0 else 100.0

    return ((current - previous) / previous) * 100


def get_spending_trend(category: str, months: int = 3) -> str:
    """Determine spending trend for a category.

    Args:
        category: Category name
        months: Number of months to analyze

    Returns:
        "increasing", "decreasing", or "stable"
    """
    month_data = get_last_n_months_data(months)

    if len(month_data) < 2:
        return "stable"

    spending_list = []
    for month_str in sorted(month_data.keys()):
        amount = calculate_category_spending(category, month_str)
        spending_list.append(amount)

    # Check trend
    if len(spending_list) < 2:
        return "stable"

    # Calculate simple trend
    increases = 0
    decreases = 0

    for i in range(1, len(spending_list)):
        if spending_list[i] > spending_list[i-1]:
            increases += 1
        elif spending_list[i] < spending_list[i-1]:
            decreases += 1

    if increases > decreases:
        return "increasing"
    elif decreases > increases:
        return "decreasing"
    else:
        return "stable"


def compare_with_last_month() -> Dict:
    """Get comprehensive comparison with last month.

    Returns:
        Dictionary with comparison data
    """
    current_month = get_current_month()
    last_month = get_last_month()

    current_income = calculate_total_income_month(current_month)
    last_income = calculate_total_income_month(last_month)

    current_expenses = calculate_total_spending(current_month)
    last_expenses = calculate_total_spending(last_month)

    current_savings = calculate_monthly_savings(current_month)
    last_savings = calculate_monthly_savings(last_month)

    income_change = 0.0
    if last_income > 0:
        income_change = ((current_income - last_income) / last_income) * 100

    expense_change = 0.0
    if last_expenses > 0:
        expense_change = ((current_expenses - last_expenses) / last_expenses) * 100

    savings_change = 0.0
    if last_savings > 0:
        savings_change = ((current_savings - last_savings) / last_savings) * 100

    return {
        'current_income': current_income,
        'last_income': last_income,
        'income_change': income_change,
        'current_expenses': current_expenses,
        'last_expenses': last_expenses,
        'expense_change': expense_change,
        'current_savings': current_savings,
        'last_savings': last_savings,
        'savings_change': savings_change
    }


def detect_spending_spikes() -> List[Dict]:
    """Detect unusual high-value transactions.

    Returns:
        List of transaction dictionaries that are unusually high
    """
    current_month = get_current_month()
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, current_month)
    expenses = filter_by_type(month_transactions, "expense")

    if not expenses:
        return []

    # Calculate average and threshold
    amounts = [t['amount_paisa'] for t in expenses]
    avg = sum(amounts) / len(amounts)
    threshold = avg * 2  # Spike is 2x average

    # Find spikes
    spikes = [t for t in expenses if t['amount_paisa'] > threshold]
    return sorted(spikes, key=lambda x: x['amount_paisa'], reverse=True)


# ============================================================================
# FINANCIAL HEALTH SCORE CALCULATIONS
# ============================================================================

def calculate_savings_score() -> int:
    """Calculate savings score (max 30 points).

    Based on savings rate:
    - >= 20%: 30 points
    - 15-20%: 22 points
    - 10-15%: 15 points
    - 5-10%: 8 points
    - < 5%: 0 points

    Returns:
        Score (0-30)
    """
    current_month = get_current_month()
    rate = calculate_savings_rate(current_month)

    if rate >= 20:
        return 30
    elif rate >= 15:
        return 22
    elif rate >= 10:
        return 15
    elif rate >= 5:
        return 8
    else:
        return 0


def calculate_budget_adherence_score() -> int:
    """Calculate budget adherence score (max 25 points).

    Based on percentage of budgets maintained:
    - All budgets OK: 25 points
    - 75%+ OK: 18 points
    - 50%+ OK: 12 points
    - 25%+ OK: 6 points
    - < 25% OK: 0 points

    Returns:
        Score (0-25)
    """
    budgets = read_budgets()

    if not budgets:
        return 15  # No budgets set, give partial credit

    budget_data = get_budget_data()
    if not budget_data:
        return 15

    ok_count = sum(1 for b in budget_data if b['utilization'] < 100)
    total_count = len(budget_data)

    if total_count == 0:
        return 15

    ok_percentage = (ok_count / total_count) * 100

    if ok_percentage == 100:
        return 25
    elif ok_percentage >= 75:
        return 18
    elif ok_percentage >= 50:
        return 12
    elif ok_percentage >= 25:
        return 6
    else:
        return 0


def calculate_balance_score() -> int:
    """Calculate balance score (max 25 points).

    Based on income vs expenses:
    - Positive balance: 25 points
    - Break-even: 15 points
    - Negative balance: 0 points

    Returns:
        Score (0-25)
    """
    current_month = get_current_month()
    savings = calculate_monthly_savings(current_month)

    if savings > 0:
        return 25
    elif savings == 0:
        return 15
    else:
        return 0


def calculate_consistency_score() -> int:
    """Calculate spending consistency score (max 20 points).

    Based on staying within category spending patterns:
    - No major overspending: 20 points
    - 1 spike: 15 points
    - 2 spikes: 10 points
    - 3+ spikes: 5 points

    Returns:
        Score (0-20)
    """
    spikes = detect_spending_spikes()
    spike_count = len(spikes)

    if spike_count == 0:
        return 20
    elif spike_count == 1:
        return 15
    elif spike_count == 2:
        return 10
    else:
        return 5


def calculate_overall_health_score() -> int:
    """Calculate overall financial health score (0-100).

    Returns:
        Total score (0-100)
    """
    savings_score = calculate_savings_score()
    budget_score = calculate_budget_adherence_score()
    balance_score = calculate_balance_score()
    consistency_score = calculate_consistency_score()

    return savings_score + budget_score + balance_score + consistency_score


def get_health_interpretation(score: int) -> Tuple[str, str]:
    """Get interpretation of health score.

    Args:
        score: Health score (0-100)

    Returns:
        Tuple of (interpretation, color)
    """
    if score >= 80:
        return ("Excellent", "green")
    elif score >= 60:
        return ("Good", "yellow")
    elif score >= 40:
        return ("Fair", "orange")
    else:
        return ("Poor", "red")


# ============================================================================
# ASCII VISUALIZATION FUNCTIONS
# ============================================================================

def display_category_bar_chart(month: Optional[str] = None) -> None:
    """Display ASCII bar chart of spending by category.

    Args:
        month: Month in YYYY-MM format (None for current month)
    """
    if month is None:
        month = get_current_month()

    category_spending = get_spending_by_category(month)

    if not category_spending:
        console.print("[yellow]No spending data available[/yellow]")
        return

    total = sum(category_spending.values())

    console.print(f"\n[bold cyan]Spending by Category - {get_month_name(month)}[/bold cyan]\n")

    # Sort by amount
    sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)

    for category, amount in sorted_categories:
        percentage = calculate_category_percentage(amount, total)
        bar_length = int(percentage / 2)  # Scale to ~50 chars max
        bar = "�" * bar_length

        console.print(
            f"{category:15} [cyan]{bar:50}[/cyan] {percentage:5.1f}% ({format_amount(amount)})"
        )

    console.print()


def display_trend_indicator(change: float) -> str:
    """Get trend indicator with arrow and color.

    Args:
        change: Percentage change

    Returns:
        Formatted string with arrow and percentage
    """
    if change > 0:
        return f"[red]� +{change:.1f}%[/red]"
    elif change < 0:
        return f"[green]� {change:.1f}%[/green]"
    else:
        return "[yellow]� 0.0%[/yellow]"


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_spending_analysis() -> None:
    """Display comprehensive spending analysis."""
    console.print(f"\n[bold cyan]=� Spending Analysis - {get_month_name(get_current_month())}[/bold cyan]\n")

    current_month = get_current_month()
    total_spending = calculate_total_spending(current_month)

    if total_spending == 0:
        console.print("[yellow]No spending data available for current month[/yellow]")
        return

    # Create summary table
    table = Table(title="Spending Summary", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Amount", justify="right")
    table.add_column("Change", justify="right")

    # Total spending
    mom_change = calculate_month_over_month_change(None)
    table.add_row(
        "Total Spending",
        format_amount(total_spending),
        display_trend_indicator(mom_change)
    )

    # Burn rate
    burn_rate = calculate_burn_rate()
    table.add_row(
        "Daily Average (Burn Rate)",
        format_amount(burn_rate),
        ""
    )

    # Top 3 categories
    top_categories = get_top_spending_categories(3, current_month)
    if top_categories:
        table.add_row("", "", "")
        table.add_row("[bold]Top Spending Categories[/bold]", "", "")
        for i, (cat, amount) in enumerate(top_categories, 1):
            percentage = calculate_category_percentage(amount, total_spending)
            table.add_row(
                f"{i}. {cat}",
                format_amount(amount),
                f"{percentage:.1f}%"
            )

    console.print(table)

    # Display bar chart
    console.print()
    display_category_bar_chart(current_month)


def display_income_analysis() -> None:
    """Display comprehensive income analysis."""
    console.print(f"\n[bold cyan]=� Income Analysis - {get_month_name(get_current_month())}[/bold cyan]\n")

    current_month = get_current_month()
    total_income = calculate_total_income_month(current_month)

    if total_income == 0:
        console.print("[yellow]No income data available for current month[/yellow]")
        return

    income_sources = get_income_by_source(current_month)
    last_month_income = calculate_total_income_month(get_last_month())

    income_change = 0.0
    if last_month_income > 0:
        income_change = ((total_income - last_month_income) / last_month_income) * 100

    # Summary table
    table = Table(title="Income Summary", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Source", style="cyan")
    table.add_column("Amount", justify="right")
    table.add_column("Percentage", justify="right")

    for source, amount in sorted(income_sources.items(), key=lambda x: x[1], reverse=True):
        percentage = calculate_category_percentage(amount, total_income)
        table.add_row(source, format_amount(amount), f"{percentage:.1f}%")

    table.add_row("", "", "")
    table.add_row(
        "[bold]Total Income[/bold]",
        f"[bold]{format_amount(total_income)}[/bold]",
        display_trend_indicator(income_change)
    )

    console.print(table)

    # Income stability
    stability = calculate_income_stability()
    avg_income = calculate_average_income(3)

    info = f"""[bold]3-Month Average:[/bold] {format_amount(avg_income)}
[bold]Income Stability:[/bold] {stability:.1f}% ({"Stable" if stability >= 70 else "Variable"})
[bold]Last Month:[/bold] {format_amount(last_month_income)} {display_trend_indicator(income_change)}"""

    panel = Panel(info, title="Income Trends", border_style="blue")
    console.print()
    console.print(panel)


def display_savings_analysis() -> None:
    """Display comprehensive savings analysis."""
    console.print(f"\n[bold cyan]=� Savings Analysis - {get_month_name(get_current_month())}[/bold cyan]\n")

    current_month = get_current_month()
    savings = calculate_monthly_savings(current_month)
    savings_rate = calculate_savings_rate(current_month)
    avg_savings = calculate_average_savings(3)
    projected_annual = calculate_projected_annual_savings()

    # Determine status
    if savings >= 0:
        status_color = "green" if savings_rate >= 20 else "yellow"
        status_text = "On Track" if savings_rate >= 20 else "Below Target"
    else:
        status_color = "red"
        status_text = "Deficit"

    # Create table
    table = Table(title="Savings Summary", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Amount", justify="right")

    table.add_row("Monthly Savings", f"[{status_color}]{format_amount(savings)}[/{status_color}]")
    table.add_row("Savings Rate", f"[{status_color}]{savings_rate:.1f}%[/{status_color}]")
    table.add_row("3-Month Average", format_amount(avg_savings))
    table.add_row("Projected Annual", format_amount(projected_annual))
    table.add_row("Status", f"[{status_color}]{status_text}[/{status_color}]")

    console.print(table)

    # Recommendations
    console.print()
    if savings_rate >= 20:
        console.print("[green] Excellent! You're saving above the recommended 20% rate.[/green]")
    elif savings_rate >= 10:
        console.print(f"[yellow]�  You're saving {savings_rate:.1f}%. Aim for 20% for optimal financial health.[/yellow]")
    elif savings_rate >= 0:
        console.print(f"[yellow]�  Low savings rate ({savings_rate:.1f}%). Consider reducing expenses.[/yellow]")
    else:
        console.print("[red]L Warning: You're spending more than earning this month.[/red]")


def display_financial_health_score() -> None:
    """Display financial health score with breakdown."""
    console.print(f"\n[bold cyan]<� Financial Health Score - {get_month_name(get_current_month())}[/bold cyan]\n")

    # Calculate scores
    savings_score = calculate_savings_score()
    budget_score = calculate_budget_adherence_score()
    balance_score = calculate_balance_score()
    consistency_score = calculate_consistency_score()
    total_score = calculate_overall_health_score()

    interpretation, color = get_health_interpretation(total_score)

    # Score breakdown table
    table = Table(title="Score Breakdown", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("Status", justify="center")

    def get_status_bar(score: int, max_score: int) -> str:
        percentage = (score / max_score * 100) if max_score > 0 else 0
        if percentage >= 80:
            return "[green]��������[/green]"
        elif percentage >= 60:
            return "[yellow]��������[/yellow]"
        elif percentage >= 40:
            return "[yellow]��������[/yellow]"
        else:
            return "[red]��������[/red]"

    table.add_row("Savings Rate", str(savings_score), "30", get_status_bar(savings_score, 30))
    table.add_row("Budget Adherence", str(budget_score), "25", get_status_bar(budget_score, 25))
    table.add_row("Income vs Expenses", str(balance_score), "25", get_status_bar(balance_score, 25))
    table.add_row("Spending Consistency", str(consistency_score), "20", get_status_bar(consistency_score, 20))
    table.add_row("", "", "", "")
    table.add_row(
        "[bold]Overall Score[/bold]",
        f"[bold {color}]{total_score}[/bold {color}]",
        "[bold]100[/bold]",
        f"[{color}]{interpretation}[/{color}]"
    )

    console.print(table)

    # Recommendations
    console.print()
    console.print("[bold cyan]=� Recommendations to Improve Score:[/bold cyan]")

    if savings_score < 20:
        console.print("  • Increase savings rate to at least 20% of income")
    if budget_score < 15:
        console.print("  • Work on staying within your budgets")
    if balance_score < 20:
        console.print("  • Reduce expenses to create positive monthly balance")
    if consistency_score < 15:
        console.print("  • Avoid unusual high-value purchases")

    if total_score >= 80:
        console.print("  [green]• Keep up the excellent work![/green]")


def display_category_trends() -> None:
    """Display spending trends for categories."""
    console.print(f"\n[bold cyan]=� Category Spending Trends[/bold cyan]\n")

    current_month = get_current_month()
    last_month = get_last_month()

    # Get spending for both months
    current_spending = get_spending_by_category(current_month)
    last_spending = get_spending_by_category(last_month)

    if not current_spending and not last_spending:
        console.print("[yellow]Not enough data to show trends[/yellow]")
        return

    # Combine all categories
    all_categories = set(current_spending.keys()) | set(last_spending.keys())

    # Create comparison table
    table = Table(title="Month-over-Month Comparison", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Last Month", justify="right")
    table.add_column("This Month", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("Trend", justify="center")

    for category in sorted(all_categories):
        current = current_spending.get(category, 0)
        last = last_spending.get(category, 0)

        if last > 0:
            change = ((current - last) / last) * 100
        else:
            change = 0.0 if current == 0 else 100.0

        trend = get_spending_trend(category, 3)
        trend_symbol = "�" if trend == "increasing" else "�" if trend == "decreasing" else "�"

        table.add_row(
            category,
            format_amount(last),
            format_amount(current),
            display_trend_indicator(change),
            trend_symbol
        )

    console.print(table)


def display_monthly_report() -> None:
    """Generate and display comprehensive monthly report."""
    current_month = get_current_month()
    month_name = get_month_name(current_month)

    # Gather all data
    total_income = calculate_total_income_month(current_month)
    total_expenses = calculate_total_spending(current_month)
    savings = calculate_monthly_savings(current_month)
    savings_rate = calculate_savings_rate(current_month)
    burn_rate = calculate_burn_rate()

    income_sources = get_income_by_source(current_month)
    top_categories = get_top_spending_categories(5, current_month)

    budget_data = get_budget_data()
    budgets_on_track = sum(1 for b in budget_data if b['utilization'] < 100) if budget_data else 0
    total_budgets = len(budget_data) if budget_data else 0

    health_score = calculate_overall_health_score()
    interpretation, _ = get_health_interpretation(health_score)

    comparison = compare_with_last_month()

    # Build report
    report = f"""[bold cyan]PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP[/bold cyan]
[bold cyan]        Monthly Financial Report - {month_name}[/bold cyan]
[bold cyan]PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP[/bold cyan]

[bold yellow]INCOME SUMMARY[/bold yellow]
Total Income:        {format_amount(total_income)} {display_trend_indicator(comparison['income_change'])}"""

    for source, amount in sorted(income_sources.items(), key=lambda x: x[1], reverse=True):
        report += f"\n  {source:20} {format_amount(amount)}"

    report += f"""

[bold yellow]EXPENSE SUMMARY[/bold yellow]
Total Expenses:      {format_amount(total_expenses)} {display_trend_indicator(comparison['expense_change'])}
Average Daily:       {format_amount(burn_rate)}

[bold yellow]TOP SPENDING CATEGORIES[/bold yellow]"""

    for i, (cat, amount) in enumerate(top_categories, 1):
        percentage = calculate_category_percentage(amount, total_expenses) if total_expenses > 0 else 0
        report += f"\n{i}. {cat:20} {format_amount(amount):15} ({percentage:.1f}%)"

    savings_color = "green" if savings >= 0 else "red"
    savings_status = "Above Target " if savings_rate >= 20 else "Below Target �" if savings_rate >= 0 else "Deficit L"

    report += f"""

[bold yellow]SAVINGS[/bold yellow]
Amount Saved:        [{savings_color}]{format_amount(savings)}[/{savings_color}]
Savings Rate:        [{savings_color}]{savings_rate:.1f}%[/{savings_color}]
Status:              {savings_status}"""

    if total_budgets > 0:
        report += f"""

[bold yellow]BUDGET PERFORMANCE[/bold yellow]
Categories On Track: {budgets_on_track}/{total_budgets}
Over Budget:         {total_budgets - budgets_on_track} categories"""

    health_color = "green" if health_score >= 80 else "yellow" if health_score >= 60 else "red"
    stars = "P" * (health_score // 20)

    report += f"""

[bold yellow]FINANCIAL HEALTH SCORE[/bold yellow]
Score:               [{health_color}]{health_score}/100[/{health_color}]
Rating:              [{health_color}]{interpretation} {stars}[/{health_color}]

[bold yellow]KEY INSIGHTS[/bold yellow]"""

    # Generate insights
    if comparison['expense_change'] > 10:
        report += f"\n• Spending increased by {comparison['expense_change']:.1f}% vs last month"
    elif comparison['expense_change'] < -10:
        report += f"\n• Spending decreased by {abs(comparison['expense_change']):.1f}% vs last month"

    if comparison['income_change'] > 5:
        report += f"\n• Income increased by {comparison['income_change']:.1f}% vs last month"
    elif comparison['income_change'] < -5:
        report += f"\n• Income decreased by {abs(comparison['income_change']):.1f}% vs last month"

    # Check for high spending categories
    if top_categories:
        top_cat, top_amount = top_categories[0]
        mom_change = calculate_month_over_month_change(top_cat)
        if abs(mom_change) > 15:
            report += f"\n• {top_cat} spending {'up' if mom_change > 0 else 'down'} {abs(mom_change):.1f}%"

    report += f"""

[bold yellow]RECOMMENDATIONS[/bold yellow]"""

    if savings_rate >= 20:
        report += "\n• Maintain current savings rate - excellent work!"
    else:
        target_reduction = int((total_income * 0.20 - savings) / 100) * 100
        report += f"\n• Reduce expenses by {format_amount(target_reduction)} to reach 20% savings"

    if top_categories and len(top_categories) > 0:
        top_cat, top_amount = top_categories[0]
        mom_change = calculate_month_over_month_change(top_cat)
        if mom_change > 15:
            report += f"\n• Consider reducing {top_cat} expenses"

    if total_budgets > 0 and budgets_on_track < total_budgets:
        report += f"\n• Review and adjust budgets for over-budget categories"

    report += f"""

[bold cyan]PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP[/bold cyan]"""

    console.print(report)


def display_insights() -> None:
    """Display key insights and recommendations."""
    console.print(f"\n[bold cyan]=� Financial Insights - {get_month_name(get_current_month())}[/bold cyan]\n")

    current_month = get_current_month()

    # Gather data
    savings_rate = calculate_savings_rate(current_month)
    comparison = compare_with_last_month()
    spikes = detect_spending_spikes()
    budget_data = get_budget_data()

    insights = []
    recommendations = []

    # Savings insights
    if savings_rate >= 20:
        insights.append("[green] Excellent savings rate! You're saving above the recommended 20%.[/green]")
    elif savings_rate >= 10:
        insights.append(f"[yellow]�  Savings rate is {savings_rate:.1f}%. Aim for 20% for better financial health.[/yellow]")
        recommendations.append(f"Try to save an additional {20 - savings_rate:.1f}% of your income")
    elif savings_rate >= 0:
        insights.append(f"[red]L Low savings rate ({savings_rate:.1f}%). Consider reducing expenses.[/red]")
        recommendations.append("Review your spending and identify areas to cut back")
    else:
        insights.append("[red]L Warning: Spending exceeds income this month.[/red]")
        recommendations.append("Urgently reduce expenses or increase income")

    # Income insights
    if abs(comparison['income_change']) > 10:
        direction = "increased" if comparison['income_change'] > 0 else "decreased"
        insights.append(f"=� Income {direction} by {abs(comparison['income_change']):.1f}% compared to last month")

    # Expense insights
    if abs(comparison['expense_change']) > 10:
        direction = "increased" if comparison['expense_change'] > 0 else "decreased"
        color = "red" if comparison['expense_change'] > 0 else "green"
        insights.append(f"[{color}]=� Spending {direction} by {abs(comparison['expense_change']):.1f}% compared to last month[/{color}]")

        if comparison['expense_change'] > 0:
            recommendations.append("Identify why spending increased and take corrective action")

    # Budget insights
    if budget_data:
        on_track = sum(1 for b in budget_data if b['utilization'] < 100)
        total = len(budget_data)
        over_budget = total - on_track

        if over_budget == 0:
            insights.append(f"[green] Great job! All {total} budgets are on track.[/green]")
        elif on_track > over_budget:
            insights.append(f"[yellow]�  {on_track}/{total} budgets on track. {over_budget} over budget.[/yellow]")
            recommendations.append(f"Focus on reducing spending in over-budget categories")
        else:
            insights.append(f"[red]L Only {on_track}/{total} budgets on track. Review your spending.[/red]")
            recommendations.append("Consider adjusting budgets or significantly reducing expenses")

    # Spending spike insights
    if spikes:
        insights.append(f"[yellow]�  Detected {len(spikes)} unusually high transaction(s) this month.[/yellow]")
        recommendations.append("Review large purchases and consider if they could be reduced")

    # Category insights
    top_categories = get_top_spending_categories(3, current_month)
    if top_categories:
        top_cat, _ = top_categories[0]
        mom_change = calculate_month_over_month_change(top_cat)
        if abs(mom_change) > 20:
            direction = "increased" if mom_change > 0 else "decreased"
            insights.append(f"=� {top_cat} spending {direction} by {abs(mom_change):.1f}% this month")
            if mom_change > 20:
                recommendations.append(f"Reduce {top_cat} expenses - consider cost-saving alternatives")

    # Display insights
    if insights:
        console.print("[bold yellow]Key Insights:[/bold yellow]")
        for insight in insights:
            console.print(f"  {insight}")

    console.print()

    # Display recommendations
    if recommendations:
        console.print("[bold cyan]Recommendations:[/bold cyan]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")
    else:
        console.print("[green] No major concerns. Keep up the good work![/green]")

    console.print()


# ============================================================================
# FEATURE IMPLEMENTATIONS
# ============================================================================

def spending_analysis() -> None:
    """Show spending analysis."""
    display_spending_analysis()


def income_analysis() -> None:
    """Show income analysis."""
    display_income_analysis()


def savings_analysis() -> None:
    """Show savings analysis."""
    display_savings_analysis()


def financial_health_score() -> None:
    """Show financial health score."""
    display_financial_health_score()


def category_trends() -> None:
    """Show category trends."""
    display_category_trends()


def monthly_report() -> None:
    """Show comprehensive monthly report."""
    display_monthly_report()


def compare_months() -> None:
    """Compare current month with previous month."""
    console.print(f"\n[bold cyan]=� Month Comparison[/bold cyan]\n")

    current_month = get_current_month()
    last_month = get_last_month()

    current_name = get_month_name(current_month)
    last_name = get_month_name(last_month)

    comparison = compare_with_last_month()

    table = Table(title=f"{last_name} vs {current_name}", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column(last_name, justify="right")
    table.add_column(current_name, justify="right")
    table.add_column("Change", justify="right")

    table.add_row(
        "Income",
        format_amount(comparison['last_income']),
        format_amount(comparison['current_income']),
        display_trend_indicator(comparison['income_change'])
    )

    table.add_row(
        "Expenses",
        format_amount(comparison['last_expenses']),
        format_amount(comparison['current_expenses']),
        display_trend_indicator(comparison['expense_change'])
    )

    table.add_row(
        "Savings",
        format_amount(comparison['last_savings']),
        format_amount(comparison['current_savings']),
        display_trend_indicator(comparison['savings_change']) if comparison['last_savings'] > 0 else ""
    )

    console.print(table)
    console.print()


def view_insights() -> None:
    """Show key insights and recommendations."""
    display_insights()


# ============================================================================
# ANALYTICS MENU
# ============================================================================

def analytics_menu() -> None:
    """Display and handle analytics menu."""
    while True:
        console.print()
        choice = questionary.select(
            "Financial Analytics",
            choices=[
                "Spending Analysis",
                "Income Analysis",
                "Savings Analysis",
                "Financial Health Score",
                "Category Trends",
                "Monthly Report",
                "Compare Months",
                "View Insights",
                "Back to Main Menu"
            ]
        ).ask()

        if choice is None or choice == "Back to Main Menu":
            break

        if choice == "Spending Analysis":
            spending_analysis()
        elif choice == "Income Analysis":
            income_analysis()
        elif choice == "Savings Analysis":
            savings_analysis()
        elif choice == "Financial Health Score":
            financial_health_score()
        elif choice == "Category Trends":
            category_trends()
        elif choice == "Monthly Report":
            monthly_report()
        elif choice == "Compare Months":
            compare_months()
        elif choice == "View Insights":
            view_insights()
