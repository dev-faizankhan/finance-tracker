"""Budget Management Feature

Handles budget setting, tracking, analysis, and recommendations.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from calendar import monthrange
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

# Import transaction functions
import sys
sys.path.append(str(Path(__file__).parent.parent))
from transactions.transactions import (
    read_transactions,
    format_amount,
    EXPENSE_CATEGORIES,
    filter_by_type,
    filter_by_category
)

console = Console()

# Constants
DATABASE_DIR = Path("database")
BUDGETS_FILE = DATABASE_DIR / "budgets.txt"
BUDGET_PERIODS = ["monthly", "weekly"]


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensure_budgets_file_exists() -> None:
    """Create budgets file if it doesn't exist."""
    DATABASE_DIR.mkdir(exist_ok=True)
    if not BUDGETS_FILE.exists():
        BUDGETS_FILE.touch()


def read_budgets() -> List[Dict]:
    """Read all budgets from file.

    Returns:
        List of budget dictionaries with keys: category, limit_paisa, period
    """
    ensure_budgets_file_exists()
    budgets = []

    if not BUDGETS_FILE.exists() or BUDGETS_FILE.stat().st_size == 0:
        return budgets

    try:
        with open(BUDGETS_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    parts = line.split('|')
                    if len(parts) != 3:
                        console.print(f"[yellow]Warning: Skipping malformed line {line_num}[/yellow]")
                        continue

                    category, limit_paisa, period = parts

                    # Validate data
                    if period not in BUDGET_PERIODS:
                        console.print(f"[yellow]Warning: Invalid period on line {line_num}[/yellow]")
                        continue

                    budgets.append({
                        "category": category,
                        "limit_paisa": int(limit_paisa),
                        "period": period
                    })
                except (ValueError, IndexError) as e:
                    console.print(f"[yellow]Warning: Error parsing line {line_num}: {e}[/yellow]")
                    continue
    except Exception as e:
        console.print(f"[red]Error reading budgets file: {e}[/red]")

    return budgets


def write_budget(category: str, limit_paisa: int, period: str) -> bool:
    """Append a new budget to file.

    Args:
        category: Budget category
        limit_paisa: Budget limit in paisa
        period: "monthly" or "weekly"

    Returns:
        True if successful, False otherwise
    """
    ensure_budgets_file_exists()

    try:
        with open(BUDGETS_FILE, 'a', encoding='utf-8') as f:
            line = f"{category}|{limit_paisa}|{period}\n"
            f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error writing budget: {e}[/red]")
        return False


def update_budget(category: str, new_limit_paisa: int) -> bool:
    """Update an existing budget.

    Args:
        category: Category to update
        new_limit_paisa: New budget limit in paisa

    Returns:
        True if successful, False otherwise
    """
    budgets = read_budgets()
    updated = False

    for budget in budgets:
        if budget['category'] == category:
            budget['limit_paisa'] = new_limit_paisa
            updated = True
            break

    if not updated:
        console.print(f"[red]Budget for {category} not found[/red]")
        return False

    try:
        with open(BUDGETS_FILE, 'w', encoding='utf-8') as f:
            for budget in budgets:
                line = f"{budget['category']}|{budget['limit_paisa']}|{budget['period']}\n"
                f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error updating budget: {e}[/red]")
        return False


def delete_budget(category: str) -> bool:
    """Delete a budget.

    Args:
        category: Category to delete

    Returns:
        True if successful, False otherwise
    """
    budgets = read_budgets()
    original_count = len(budgets)
    budgets = [b for b in budgets if b['category'] != category]

    if len(budgets) == original_count:
        console.print(f"[red]Budget for {category} not found[/red]")
        return False

    try:
        with open(BUDGETS_FILE, 'w', encoding='utf-8') as f:
            for budget in budgets:
                line = f"{budget['category']}|{budget['limit_paisa']}|{budget['period']}\n"
                f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error deleting budget: {e}[/red]")
        return False


def budget_exists(category: str) -> bool:
    """Check if budget exists for category.

    Args:
        category: Category to check

    Returns:
        True if budget exists, False otherwise
    """
    budgets = read_budgets()
    return any(b['category'] == category for b in budgets)


# ============================================================================
# TIME FUNCTIONS
# ============================================================================

def get_current_month() -> str:
    """Get current month in YYYY-MM format.

    Returns:
        Current month string
    """
    return datetime.now().strftime("%Y-%m")


def get_month_from_date(date_str: str) -> str:
    """Extract month from date string.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Month in YYYY-MM format
    """
    return date_str[:7]


def is_same_month(date1: str, date2: str) -> bool:
    """Check if two dates are in the same month.

    Args:
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format

    Returns:
        True if same month, False otherwise
    """
    return get_month_from_date(date1) == get_month_from_date(date2)


def filter_current_month_transactions(transactions: List[Dict]) -> List[Dict]:
    """Filter transactions for current month only.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Filtered list of current month transactions
    """
    current_month = get_current_month()
    return [t for t in transactions if get_month_from_date(t['date']) == current_month]


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def get_budget_for_category(category: str) -> Optional[int]:
    """Get budget limit for a category.

    Args:
        category: Category name

    Returns:
        Budget limit in paisa or None if not set
    """
    budgets = read_budgets()
    for budget in budgets:
        if budget['category'] == category:
            return budget['limit_paisa']
    return None


def get_current_month_spending(category: str) -> int:
    """Get total spending for category in current month.

    Args:
        category: Category name

    Returns:
        Total spent in paisa
    """
    transactions = read_transactions()
    expenses = filter_by_type(transactions, "expense")
    current_month_expenses = filter_current_month_transactions(expenses)
    category_expenses = filter_by_category(current_month_expenses, category)

    return sum(t['amount_paisa'] for t in category_expenses)


def calculate_remaining(budget: int, spent: int) -> int:
    """Calculate remaining budget.

    Args:
        budget: Budget amount in paisa
        spent: Spent amount in paisa

    Returns:
        Remaining amount in paisa (can be negative)
    """
    return budget - spent


def calculate_utilization(spent: int, budget: int) -> float:
    """Calculate budget utilization percentage.

    Args:
        spent: Spent amount in paisa
        budget: Budget amount in paisa

    Returns:
        Utilization percentage (can exceed 100)
    """
    if budget == 0:
        return 0.0
    return (spent / budget) * 100


def get_budget_status(utilization: float) -> tuple[str, str]:
    """Get budget status based on utilization.

    Args:
        utilization: Utilization percentage

    Returns:
        Tuple of (status_text, color)
    """
    if utilization >= 100:
        return ("Over Budget", "red")
    elif utilization >= 70:
        return ("Warning", "yellow")
    else:
        return ("OK", "green")


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def get_budget_data() -> List[Dict]:
    """Get comprehensive budget data with spending information.

    Returns:
        List of dictionaries with budget and spending data
    """
    budgets = read_budgets()
    budget_data = []

    for budget in budgets:
        category = budget['category']
        limit = budget['limit_paisa']
        spent = get_current_month_spending(category)
        remaining = calculate_remaining(limit, spent)
        utilization = calculate_utilization(spent, limit)
        status_text, status_color = get_budget_status(utilization)

        budget_data.append({
            'category': category,
            'limit_paisa': limit,
            'spent_paisa': spent,
            'remaining_paisa': remaining,
            'utilization': utilization,
            'status_text': status_text,
            'status_color': status_color,
            'period': budget['period']
        })

    return budget_data


def get_overbudget_categories() -> List[str]:
    """Get list of categories that exceeded budget.

    Returns:
        List of category names
    """
    budget_data = get_budget_data()
    return [b['category'] for b in budget_data if b['utilization'] >= 100]


def get_warning_categories() -> List[str]:
    """Get list of categories at warning level (70-100%).

    Returns:
        List of category names
    """
    budget_data = get_budget_data()
    return [b['category'] for b in budget_data if 70 <= b['utilization'] < 100]


def get_healthy_categories() -> List[str]:
    """Get list of categories under 70% utilization.

    Returns:
        List of category names
    """
    budget_data = get_budget_data()
    return [b['category'] for b in budget_data if b['utilization'] < 70]


def calculate_total_budget() -> int:
    """Calculate total of all budgets.

    Returns:
        Total budget in paisa
    """
    budgets = read_budgets()
    return sum(b['limit_paisa'] for b in budgets)


def calculate_total_spent() -> int:
    """Calculate total spent across all budgeted categories in current month.

    Returns:
        Total spent in paisa
    """
    budget_data = get_budget_data()
    return sum(b['spent_paisa'] for b in budget_data)


def calculate_overall_utilization() -> float:
    """Calculate overall budget utilization.

    Returns:
        Overall utilization percentage
    """
    total_budget = calculate_total_budget()
    total_spent = calculate_total_spent()

    if total_budget == 0:
        return 0.0

    return (total_spent / total_budget) * 100


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_budgets_table() -> None:
    """Display all budgets in a rich table with progress bars."""
    budget_data = get_budget_data()

    if not budget_data:
        console.print("[yellow]No budgets set yet[/yellow]")
        return

    # Sort by utilization (highest first)
    budget_data.sort(key=lambda x: x['utilization'], reverse=True)

    table = Table(
        title=f"Budget Status - {get_current_month()}",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED
    )

    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Budget", justify="right")
    table.add_column("Spent", justify="right")
    table.add_column("Remaining", justify="right")
    table.add_column("Used", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Progress", width=20)

    for data in budget_data:
        # Format amounts
        budget_str = format_amount(data['limit_paisa'])
        spent_str = format_amount(data['spent_paisa'])
        remaining_str = format_amount(data['remaining_paisa'])

        # Color code remaining amount
        if data['remaining_paisa'] < 0:
            remaining_str = f"[red]{remaining_str}[/red]"
        else:
            remaining_str = f"[green]{remaining_str}[/green]"

        # Utilization percentage
        util_str = f"{data['utilization']:.1f}%"

        # Status with emoji
        status_emoji = {
            "OK": "",
            "Warning": "�",
            "Over Budget": "L"
        }
        status_display = f"{status_emoji[data['status_text']]} {data['status_text']}"

        # Progress bar
        progress_bar = create_progress_bar(data['utilization'], data['status_color'])

        table.add_row(
            data['category'],
            budget_str,
            f"[{data['status_color']}]{spent_str}[/{data['status_color']}]",
            remaining_str,
            f"[{data['status_color']}]{util_str}[/{data['status_color']}]",
            f"[{data['status_color']}]{status_display}[/{data['status_color']}]",
            progress_bar
        )

    console.print(table)


def create_progress_bar(utilization: float, color: str) -> str:
    """Create a text-based progress bar.

    Args:
        utilization: Utilization percentage
        color: Color for the bar

    Returns:
        Formatted progress bar string
    """
    # Cap at 100% for display
    display_util = min(utilization, 100)
    filled = int(display_util / 5)  # 20 chars max
    empty = 20 - filled

    bar = f"[{color}]{'�' * filled}{'�' * empty}[/{color}]"
    return bar


def display_budget_summary() -> None:
    """Display comprehensive budget summary."""
    budget_data = get_budget_data()

    if not budget_data:
        console.print("[yellow]No budgets set yet[/yellow]")
        return

    total_budget = calculate_total_budget()
    total_spent = calculate_total_spent()
    total_remaining = total_budget - total_spent
    overall_util = calculate_overall_utilization()

    overbudget = len(get_overbudget_categories())
    warning = len(get_warning_categories())
    healthy = len(get_healthy_categories())

    # Calculate average utilization
    avg_util = sum(b['utilization'] for b in budget_data) / len(budget_data) if budget_data else 0

    # Color code based on overall status
    overall_color = "green"
    if overall_util >= 100:
        overall_color = "red"
    elif overall_util >= 70:
        overall_color = "yellow"

    summary = f"""[bold]Total Budget:[/bold]     {format_amount(total_budget)}
[bold]Total Spent:[/bold]      {format_amount(total_spent)}
[bold]Total Remaining:[/bold]  [{overall_color}]{format_amount(total_remaining)}[/{overall_color}]
[bold]Overall Usage:[/bold]    [{overall_color}]{overall_util:.1f}%[/{overall_color}]
[bold]Average Usage:[/bold]    {avg_util:.1f}%

[red]L Over Budget:[/red]    {overbudget} categories
[yellow]�  Warning:[/yellow]       {warning} categories
[green] Healthy:[/green]       {healthy} categories"""

    panel = Panel(
        summary,
        title=f"Budget Summary - {datetime.now().strftime('%B %Y')}",
        border_style="blue",
        box=box.DOUBLE
    )
    console.print(panel)


def display_budget_analysis() -> None:
    """Display detailed budget analysis."""
    console.print(f"\n[bold cyan]Budget Analysis - {datetime.now().strftime('%B %Y')}[/bold cyan]\n")

    budget_data = get_budget_data()

    if not budget_data:
        console.print("[yellow]No budgets set yet[/yellow]")
        return

    overbudget = [(b['category'], b['utilization']) for b in budget_data if b['utilization'] >= 100]
    warning = [(b['category'], b['utilization']) for b in budget_data if 70 <= b['utilization'] < 100]
    healthy = [(b['category'], b['utilization']) for b in budget_data if b['utilization'] < 70]

    # Sort each by utilization
    overbudget.sort(key=lambda x: x[1], reverse=True)
    warning.sort(key=lambda x: x[1], reverse=True)
    healthy.sort(key=lambda x: x[1])

    if overbudget:
        console.print("[bold red]L Categories Over Budget:[/bold red]")
        for cat, util in overbudget:
            console.print(f"  [red]• {cat}: {util:.1f}% (Over by {util - 100:.1f}%)[/red]")
        console.print()

    if warning:
        console.print("[bold yellow]�  Categories at Warning Level:[/bold yellow]")
        for cat, util in warning:
            console.print(f"  [yellow]• {cat}: {util:.1f}%[/yellow]")
        console.print()

    if healthy:
        console.print("[bold green] Healthy Categories (Most Room):[/bold green]")
        for cat, util in healthy:
            budget_limit = next(b['limit_paisa'] for b in budget_data if b['category'] == cat)
            remaining = next(b['remaining_paisa'] for b in budget_data if b['category'] == cat)
            console.print(f"  [green]• {cat}: {util:.1f}% ({format_amount(remaining)} remaining)[/green]")
        console.print()

    # Recommendations
    console.print("[bold cyan]Recommendations:[/bold cyan]")
    if overbudget:
        console.print(f"  • Consider reducing spending in: {', '.join([c for c, _ in overbudget])}")
    if warning:
        console.print(f"  • Monitor closely: {', '.join([c for c, _ in warning])}")
    if len(budget_data) < len(EXPENSE_CATEGORIES):
        console.print(f"  • Set budgets for remaining categories to track all expenses")
    if not overbudget and not warning:
        console.print("  • Great job! All budgets are in healthy range")


def display_budget_alerts() -> None:
    """Display budget alerts for categories needing attention."""
    console.print(f"\n[bold red]�  Budget Alerts - {datetime.now().strftime('%B %Y')}[/bold red]\n")

    budget_data = get_budget_data()

    if not budget_data:
        console.print("[yellow]No budgets set yet[/yellow]")
        return

    has_alerts = False

    # Critical: Over budget
    overbudget = [b for b in budget_data if b['utilization'] >= 100]
    if overbudget:
        has_alerts = True
        console.print("[bold red]=� CRITICAL - Budget Exceeded:[/bold red]")
        for b in overbudget:
            overage = b['spent_paisa'] - b['limit_paisa']
            console.print(f"  • {b['category']}: {format_amount(b['spent_paisa'])} spent of {format_amount(b['limit_paisa'])} budget")
            console.print(f"    Over by: [red]{format_amount(overage)}[/red]")
        console.print()

    # High: 90%+ utilization
    high_util = [b for b in budget_data if 90 <= b['utilization'] < 100]
    if high_util:
        has_alerts = True
        console.print("[bold yellow]�  HIGH ALERT - 90%+ Used:[/bold yellow]")
        for b in high_util:
            console.print(f"  • {b['category']}: {b['utilization']:.1f}% used ({format_amount(b['remaining_paisa'])} left)")
        console.print()

    # Medium: 80%+ utilization
    medium_util = [b for b in budget_data if 80 <= b['utilization'] < 90]
    if medium_util:
        has_alerts = True
        console.print("[bold yellow]�  MEDIUM ALERT - 80%+ Used:[/bold yellow]")
        for b in medium_util:
            console.print(f"  • {b['category']}: {b['utilization']:.1f}% used ({format_amount(b['remaining_paisa'])} left)")
        console.print()

    if not has_alerts:
        console.print("[green] No budget alerts! All categories are in good standing.[/green]\n")
    else:
        console.print("[bold cyan]=� Suggestions:[/bold cyan]")
        if overbudget:
            console.print("  • Stop or significantly reduce spending in over-budget categories")
        if high_util or medium_util:
            console.print("  • Carefully monitor spending for the rest of the month")
            console.print("  • Consider postponing non-essential purchases")


def show_success(message: str) -> None:
    """Display success message.

    Args:
        message: Success message
    """
    console.print(f"[green] {message}[/green]")


def show_error(message: str) -> None:
    """Display error message.

    Args:
        message: Error message
    """
    console.print(f"[red] {message}[/red]")


# ============================================================================
# INPUT FUNCTIONS
# ============================================================================

def get_budget_amount() -> Optional[int]:
    """Get budget amount from user and convert to paisa.

    Returns:
        Amount in paisa (int) or None if cancelled
    """
    while True:
        amount_str = questionary.text(
            "Enter monthly budget amount (in Rs):",
            validate=lambda text: len(text) > 0 or "Amount cannot be empty"
        ).ask()

        if amount_str is None:  # User cancelled
            return None

        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[red]Budget amount must be positive[/red]")
                continue

            # Convert to paisa (multiply by 100)
            amount_paisa = int(amount_float * 100)
            return amount_paisa
        except ValueError:
            console.print("[red]Invalid amount. Please enter a valid number[/red]")


def get_budget_category() -> Optional[str]:
    """Get category for budget.

    Returns:
        Selected category or None if cancelled
    """
    category = questionary.select(
        "Select category for budget:",
        choices=EXPENSE_CATEGORIES
    ).ask()

    return category


# ============================================================================
# FEATURE IMPLEMENTATIONS
# ============================================================================

def set_budget() -> None:
    """Set a new budget for a category."""
    console.print("\n[bold cyan]Set Budget[/bold cyan]\n")

    category = get_budget_category()
    if category is None:
        return

    # Check if budget already exists
    if budget_exists(category):
        update_existing = questionary.confirm(
            f"Budget for {category} already exists. Do you want to update it?",
            default=True
        ).ask()

        if not update_existing:
            return

        # Get new amount and update
        amount_paisa = get_budget_amount()
        if amount_paisa is None:
            return

        if update_budget(category, amount_paisa):
            show_success(f"Budget for {category} updated to {format_amount(amount_paisa)}")
        else:
            show_error("Failed to update budget")
    else:
        # Create new budget
        amount_paisa = get_budget_amount()
        if amount_paisa is None:
            return

        # For now, always use monthly period
        period = "monthly"

        if write_budget(category, amount_paisa, period):
            show_success(f"Budget for {category} set to {format_amount(amount_paisa)}/month")
        else:
            show_error("Failed to set budget")


def view_budgets() -> None:
    """View all budgets with spending information."""
    console.print()
    display_budgets_table()
    console.print()
    display_budget_summary()


def budget_summary() -> None:
    """Display budget summary."""
    console.print()
    display_budget_summary()


def budget_analysis() -> None:
    """Display budget analysis."""
    display_budget_analysis()


def budget_alerts() -> None:
    """Display budget alerts."""
    display_budget_alerts()


def edit_budget() -> None:
    """Edit an existing budget."""
    budgets = read_budgets()

    if not budgets:
        console.print("[yellow]No budgets set yet[/yellow]")
        return

    console.print("\n[bold cyan]Edit Budget[/bold cyan]\n")

    # Create choices
    choices = [f"{b['category']} - {format_amount(b['limit_paisa'])}/month" for b in budgets]

    selected = questionary.select(
        "Select budget to edit:",
        choices=choices
    ).ask()

    if selected is None:
        return

    # Extract category
    category = selected.split(' - ')[0]

    # Get current budget
    current_budget = get_budget_for_category(category)
    console.print(f"\n[bold]Current budget for {category}:[/bold] {format_amount(current_budget)}")

    # Get new amount
    new_amount = get_budget_amount()
    if new_amount is None:
        return

    if update_budget(category, new_amount):
        show_success(f"Budget for {category} updated to {format_amount(new_amount)}")
    else:
        show_error("Failed to update budget")


def delete_budget_ui() -> None:
    """Delete a budget."""
    budgets = read_budgets()

    if not budgets:
        console.print("[yellow]No budgets set yet[/yellow]")
        return

    console.print("\n[bold cyan]Delete Budget[/bold cyan]\n")

    # Create choices
    choices = [f"{b['category']} - {format_amount(b['limit_paisa'])}/month" for b in budgets]

    selected = questionary.select(
        "Select budget to delete:",
        choices=choices
    ).ask()

    if selected is None:
        return

    # Extract category
    category = selected.split(' - ')[0]

    # Confirm deletion
    confirm = questionary.confirm(
        f"Are you sure you want to delete the budget for {category}?",
        default=False
    ).ask()

    if confirm:
        if delete_budget(category):
            show_success(f"Budget for {category} deleted")
        else:
            show_error("Failed to delete budget")


def budget_recommendations() -> None:
    """Provide budget recommendations based on spending patterns."""
    console.print(f"\n[bold cyan]=� Budget Recommendations - {datetime.now().strftime('%B %Y')}[/bold cyan]\n")

    budget_data = get_budget_data()
    all_transactions = read_transactions()
    current_month_expenses = filter_current_month_transactions(filter_by_type(all_transactions, "expense"))

    if not budget_data and not current_month_expenses:
        console.print("[yellow]Not enough data for recommendations. Add some transactions and budgets first.[/yellow]")
        return

    has_recommendations = False

    # Recommendation 1: Budget increases for overspent categories
    overbudget = [b for b in budget_data if b['utilization'] >= 100]
    if overbudget:
        has_recommendations = True
        console.print("[bold yellow]=� Consider Increasing Budgets:[/bold yellow]")
        for b in overbudget:
            # Suggest 20% increase
            suggested = int(b['limit_paisa'] * 1.2)
            console.print(f"  • {b['category']}: {format_amount(b['limit_paisa'])} � {format_amount(suggested)} (+20%)")
        console.print()

    # Recommendation 2: Budget decreases for under-utilized categories
    underutilized = [b for b in budget_data if b['utilization'] < 50 and b['spent_paisa'] > 0]
    if underutilized:
        has_recommendations = True
        console.print("[bold green]=� Consider Reducing Budgets:[/bold green]")
        for b in underutilized:
            # Suggest amount based on actual spending + 30% buffer
            suggested = int(b['spent_paisa'] * 1.3)
            savings = b['limit_paisa'] - suggested
            console.print(f"  • {b['category']}: {format_amount(b['limit_paisa'])} � {format_amount(suggested)} (save {format_amount(savings)})")
        console.print()

    # Recommendation 3: Categories without budgets
    budgeted_categories = [b['category'] for b in budget_data]
    categories_with_spending = set(t['category'] for t in current_month_expenses)
    unbudgeted = categories_with_spending - set(budgeted_categories)

    if unbudgeted:
        has_recommendations = True
        console.print("[bold cyan]=� Set Budgets For:[/bold cyan]")
        for cat in unbudgeted:
            spent = get_current_month_spending(cat)
            # Suggest current spending + 20% as budget
            suggested = int(spent * 1.2)
            console.print(f"  • {cat}: Current spending {format_amount(spent)}, suggested budget: {format_amount(suggested)}")
        console.print()

    # Recommendation 4: Savings opportunities
    total_budget = calculate_total_budget()
    total_spent = calculate_total_spent()
    if total_budget > 0 and total_spent < total_budget:
        has_recommendations = True
        potential_savings = total_budget - total_spent
        console.print("[bold green]=� Savings Opportunity:[/bold green]")
        console.print(f"  • You're on track to save {format_amount(potential_savings)} this month!")
        console.print(f"  • That's {((potential_savings / total_budget) * 100):.1f}% of your total budget")
        console.print()

    # Recommendation 5: Balanced budget suggestion
    if budget_data:
        has_recommendations = True
        console.print("[bold cyan]�  Budget Allocation Suggestion:[/bold cyan]")
        console.print("  Based on common financial advice:")
        console.print("  • Food: 25-30% of budget")
        console.print("  • Transport: 10-15% of budget")
        console.print("  • Bills: 20-25% of budget")
        console.print("  • Entertainment: 5-10% of budget")
        console.print("  • Savings: 20-30% of income")
        console.print()

    if not has_recommendations:
        console.print("[green] Your budgets look well-balanced! Keep up the good work.[/green]\n")


# ============================================================================
# BUDGET MENU
# ============================================================================

def budget_menu() -> None:
    """Display and handle budget management menu."""
    while True:
        console.print()
        choice = questionary.select(
            "Budget Management",
            choices=[
                "Set New Budget",
                "View All Budgets",
                "Budget Summary",
                "Budget Analysis",
                "Budget Alerts",
                "Edit Budget",
                "Delete Budget",
                "Budget Recommendations",
                "Back to Main Menu"
            ]
        ).ask()

        if choice is None or choice == "Back to Main Menu":
            break

        if choice == "Set New Budget":
            set_budget()
        elif choice == "View All Budgets":
            view_budgets()
        elif choice == "Budget Summary":
            budget_summary()
        elif choice == "Budget Analysis":
            budget_analysis()
        elif choice == "Budget Alerts":
            budget_alerts()
        elif choice == "Edit Budget":
            edit_budget()
        elif choice == "Delete Budget":
            delete_budget_ui()
        elif choice == "Budget Recommendations":
            budget_recommendations()
