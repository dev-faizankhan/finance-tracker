"""Smart Financial Assistant Feature

Provides intelligent recommendations, proactive alerts, savings opportunities,
and financial goal tracking.
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from calendar import monthrange
import random
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
    filter_by_type,
    filter_by_category
)
from budgets.budgets import (
    read_budgets,
    get_budget_data,
    get_current_month_spending
)
from analytics.analytics import (
    calculate_total_spending,
    calculate_total_income_month,
    calculate_monthly_savings,
    calculate_savings_rate,
    calculate_overall_health_score,
    get_current_month,
    filter_transactions_by_month,
    get_month_name
)

console = Console()

# Constants
DATABASE_DIR = Path("database")
GOALS_FILE = DATABASE_DIR / "goals.txt"

GOAL_TYPES = [
    "Emergency Fund",
    "Vacation Savings",
    "Debt Payoff",
    "House Down Payment",
    "Education Fund",
    "General Savings",
    "Custom Goal"
]

FINANCIAL_TIPS = [
    "Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings",
    "Build an emergency fund covering 3-6 months of expenses",
    "Track every expense to understand your spending patterns",
    "Review and adjust your budget monthly based on actual spending",
    "Automate your savings by setting up automatic transfers",
    "Pay yourself first - save before spending on non-essentials",
    "Avoid impulse purchases by waiting 24 hours before buying",
    "Use cash for discretionary spending to limit overspending",
    "Compare prices and look for deals before major purchases",
    "Reduce subscription services you don't actively use",
    "Cook at home more often to save on food expenses",
    "Set specific, measurable financial goals with deadlines",
    "Review your financial health score monthly",
    "Celebrate small wins to stay motivated on your financial journey",
    "Consider the opportunity cost of every purchase",
    "Invest in yourself through education and skill development",
    "Don't let lifestyle inflation eat your income increases",
    "Build multiple income streams for financial security",
    "Start investing early to benefit from compound interest",
    "Keep debt under control - pay off high-interest debt first"
]


# ============================================================================
# GOALS FILE OPERATIONS
# ============================================================================

def ensure_goals_file_exists() -> None:
    """Create goals file if it doesn't exist."""
    DATABASE_DIR.mkdir(exist_ok=True)
    if not GOALS_FILE.exists():
        GOALS_FILE.touch()


def read_goals() -> List[Dict]:
    """Read all financial goals from file.

    Returns:
        List of goal dictionaries
    """
    ensure_goals_file_exists()
    goals = []

    if not GOALS_FILE.exists() or GOALS_FILE.stat().st_size == 0:
        return goals

    try:
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    parts = line.split('|')
                    if len(parts) != 6:
                        console.print(f"[yellow]Warning: Skipping malformed line {line_num}[/yellow]")
                        continue

                    name, target_paisa, current_paisa, deadline, created, goal_type = parts

                    goals.append({
                        "name": name,
                        "target_paisa": int(target_paisa),
                        "current_paisa": int(current_paisa),
                        "deadline": deadline,
                        "created_date": created,
                        "goal_type": goal_type
                    })
                except (ValueError, IndexError) as e:
                    console.print(f"[yellow]Warning: Error parsing line {line_num}: {e}[/yellow]")
                    continue
    except Exception as e:
        console.print(f"[red]Error reading goals file: {e}[/red]")

    return goals


def write_goal(name: str, target_paisa: int, deadline: str, goal_type: str, current_paisa: int = 0) -> bool:
    """Create a new financial goal.

    Args:
        name: Goal name
        target_paisa: Target amount in paisa
        deadline: Deadline in YYYY-MM-DD format
        goal_type: Type of goal
        current_paisa: Current amount saved (default 0)

    Returns:
        True if successful, False otherwise
    """
    ensure_goals_file_exists()

    # Check if goal already exists
    existing_goals = read_goals()
    if any(g['name'].lower() == name.lower() for g in existing_goals):
        console.print(f"[red]Goal with name '{name}' already exists[/red]")
        return False

    created_date = datetime.now().strftime("%Y-%m-%d")

    try:
        with open(GOALS_FILE, 'a', encoding='utf-8') as f:
            line = f"{name}|{target_paisa}|{current_paisa}|{deadline}|{created_date}|{goal_type}\n"
            f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error writing goal: {e}[/red]")
        return False


def update_goal_progress(goal_name: str, additional_amount: int) -> bool:
    """Add amount to goal progress.

    Args:
        goal_name: Name of the goal
        additional_amount: Amount to add in paisa

    Returns:
        True if successful, False otherwise
    """
    goals = read_goals()
    updated = False

    for goal in goals:
        if goal['name'].lower() == goal_name.lower():
            goal['current_paisa'] += additional_amount
            # Cap at target
            if goal['current_paisa'] > goal['target_paisa']:
                goal['current_paisa'] = goal['target_paisa']
            updated = True
            break

    if not updated:
        console.print(f"[red]Goal '{goal_name}' not found[/red]")
        return False

    try:
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            for goal in goals:
                line = f"{goal['name']}|{goal['target_paisa']}|{goal['current_paisa']}|{goal['deadline']}|{goal['created_date']}|{goal['goal_type']}\n"
                f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error updating goal: {e}[/red]")
        return False


def delete_goal(goal_name: str) -> bool:
    """Delete a financial goal.

    Args:
        goal_name: Name of the goal to delete

    Returns:
        True if successful, False otherwise
    """
    goals = read_goals()
    original_count = len(goals)
    goals = [g for g in goals if g['name'].lower() != goal_name.lower()]

    if len(goals) == original_count:
        console.print(f"[red]Goal '{goal_name}' not found[/red]")
        return False

    try:
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            for goal in goals:
                line = f"{goal['name']}|{goal['target_paisa']}|{goal['current_paisa']}|{goal['deadline']}|{goal['created_date']}|{goal['goal_type']}\n"
                f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error deleting goal: {e}[/red]")
        return False


def get_goal_by_name(name: str) -> Optional[Dict]:
    """Retrieve a specific goal by name.

    Args:
        name: Goal name

    Returns:
        Goal dictionary or None if not found
    """
    goals = read_goals()
    for goal in goals:
        if goal['name'].lower() == name.lower():
            return goal
    return None


# ============================================================================
# DAILY CALCULATION FUNCTIONS
# ============================================================================

def calculate_daily_budget() -> int:
    """Calculate daily budget based on monthly budget.

    Returns:
        Daily budget in paisa
    """
    current_month = get_current_month()
    budgets = read_budgets()

    if not budgets:
        return 0

    total_monthly_budget = sum(b['limit_paisa'] for b in budgets)
    days_in_month = monthrange(int(current_month[:4]), int(current_month[5:7]))[1]

    return total_monthly_budget // days_in_month if days_in_month > 0 else 0


def calculate_today_spending() -> int:
    """Calculate spending for today.

    Returns:
        Today's spending in paisa
    """
    today = datetime.now().strftime("%Y-%m-%d")
    transactions = read_transactions()
    expenses = filter_by_type(transactions, "expense")
    today_expenses = [t for t in expenses if t['date'] == today]

    return sum(t['amount_paisa'] for t in today_expenses)


def calculate_daily_remaining() -> int:
    """Calculate remaining daily budget.

    Returns:
        Remaining amount in paisa
    """
    daily_budget = calculate_daily_budget()
    today_spending = calculate_today_spending()
    return daily_budget - today_spending


def is_on_daily_track() -> bool:
    """Check if spending is within daily budget.

    Returns:
        True if on track, False otherwise
    """
    return calculate_daily_remaining() >= 0


# ============================================================================
# ALERT DETECTION FUNCTIONS
# ============================================================================

def check_budget_alerts() -> List[Dict]:
    """Check for budget-related alerts.

    Returns:
        List of alert dictionaries
    """
    alerts = []
    budget_data = get_budget_data()

    for budget in budget_data:
        utilization = budget['utilization']
        category = budget['category']

        if utilization > 100:
            alerts.append({
                'type': 'critical',
                'category': 'budget',
                'message': f"{category} budget exceeded ({utilization:.0f}% used)",
                'priority': 1
            })
        elif utilization >= 90:
            alerts.append({
                'type': 'critical',
                'category': 'budget',
                'message': f"{category} at {utilization:.0f}% of budget - Critical!",
                'priority': 1
            })
        elif utilization >= 80:
            alerts.append({
                'type': 'warning',
                'category': 'budget',
                'message': f"{category} at {utilization:.0f}% of budget - Watch closely",
                'priority': 2
            })

    return alerts


def check_large_transactions() -> List[Dict]:
    """Detect unusually large transactions.

    Returns:
        List of alert dictionaries
    """
    alerts = []
    current_month = get_current_month()
    monthly_income = calculate_total_income_month(current_month)

    if monthly_income == 0:
        return alerts

    threshold = monthly_income * 0.20  # 20% of income
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, current_month)
    expenses = filter_by_type(month_transactions, "expense")

    for expense in expenses:
        if expense['amount_paisa'] > threshold:
            alerts.append({
                'type': 'warning',
                'category': 'transaction',
                'message': f"Large transaction detected: {expense['description']} ({format_amount(expense['amount_paisa'])})",
                'priority': 2
            })

    return alerts


def check_spending_spikes() -> List[Dict]:
    """Detect spending sprees (multiple transactions in same category).

    Returns:
        List of alert dictionaries
    """
    alerts = []
    today = datetime.now().strftime("%Y-%m-%d")
    transactions = read_transactions()
    today_transactions = [t for t in transactions if t['date'] == today and t['type'] == 'expense']

    # Count transactions per category
    category_counts = {}
    for trans in today_transactions:
        cat = trans['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Alert if 3+ transactions in same category
    for category, count in category_counts.items():
        if count >= 3:
            alerts.append({
                'type': 'warning',
                'category': 'spending_spree',
                'message': f"{count} {category} transactions today - Spending spree detected!",
                'priority': 2
            })

    return alerts


def check_savings_alerts() -> List[Dict]:
    """Check for savings-related alerts.

    Returns:
        List of alert dictionaries
    """
    alerts = []
    current_month = get_current_month()
    savings = calculate_monthly_savings(current_month)
    savings_rate = calculate_savings_rate(current_month)

    if savings < 0:
        alerts.append({
            'type': 'critical',
            'category': 'savings',
            'message': f"Negative savings this month: {format_amount(abs(savings))} deficit",
            'priority': 1
        })
    elif savings_rate < 5:
        alerts.append({
            'type': 'warning',
            'category': 'savings',
            'message': f"Low savings rate: {savings_rate:.1f}% (Target: 20%)",
            'priority': 2
        })

    return alerts


def check_goal_alerts() -> List[Dict]:
    """Check for goal-related alerts.

    Returns:
        List of alert dictionaries
    """
    alerts = []
    goals = read_goals()

    for goal in goals:
        progress = calculate_goal_progress(goal)
        days_left = calculate_days_until_deadline(goal['deadline'])

        # Goal completed
        if progress >= 100:
            alerts.append({
                'type': 'success',
                'category': 'goal',
                'message': f"Goal '{goal['name']}' completed! Congratulations!",
                'priority': 4
            })
            continue

        # Deadline passed
        if days_left < 0:
            alerts.append({
                'type': 'warning',
                'category': 'goal',
                'message': f"Goal '{goal['name']}' deadline passed - {abs(days_left)} days overdue",
                'priority': 2
            })
            continue

        # Deadline approaching (within 30 days)
        if days_left <= 30 and days_left > 0:
            alerts.append({
                'type': 'info',
                'category': 'goal',
                'message': f"Goal '{goal['name']}' deadline in {days_left} days",
                'priority': 3
            })

        # Behind schedule
        if not is_goal_on_track(goal) and days_left > 0:
            alerts.append({
                'type': 'warning',
                'category': 'goal',
                'message': f"Goal '{goal['name']}' behind schedule ({progress:.0f}% complete)",
                'priority': 2
            })

    return alerts


def get_active_alerts() -> List[Dict]:
    """Get all active alerts sorted by priority.

    Returns:
        List of all alerts sorted by priority
    """
    all_alerts = []

    all_alerts.extend(check_budget_alerts())
    all_alerts.extend(check_large_transactions())
    all_alerts.extend(check_spending_spikes())
    all_alerts.extend(check_savings_alerts())
    all_alerts.extend(check_goal_alerts())

    # Sort by priority (lower number = higher priority)
    all_alerts.sort(key=lambda x: x['priority'])

    return all_alerts


# ============================================================================
# RECOMMENDATION GENERATION FUNCTIONS
# ============================================================================

def generate_spending_recommendations() -> List[str]:
    """Generate recommendations based on spending patterns.

    Returns:
        List of recommendation strings
    """
    recommendations = []
    budget_data = get_budget_data()

    for budget in budget_data:
        if budget['utilization'] > 100:
            overage = budget['spent_paisa'] - budget['limit_paisa']
            recommendations.append(
                f"Reduce {budget['category']} spending by {format_amount(overage)} to meet budget"
            )
        elif budget['utilization'] >= 80:
            recommendations.append(
                f"Watch {budget['category']} spending - {budget['utilization']:.0f}% of budget used"
            )

    return recommendations


def generate_savings_recommendations() -> List[str]:
    """Generate recommendations based on savings rate.

    Returns:
        List of recommendation strings
    """
    recommendations = []
    current_month = get_current_month()
    savings_rate = calculate_savings_rate(current_month)

    if savings_rate < 0:
        recommendations.append("Urgently reduce expenses - you're spending more than earning")
    elif savings_rate < 10:
        recommendations.append("Try to save at least 10% of income (currently {:.1f}%)".format(savings_rate))
    elif savings_rate < 20:
        recommendations.append("Good progress! Aim for 20% savings rate (currently {:.1f}%)".format(savings_rate))
    elif savings_rate >= 20:
        recommendations.append("Excellent savings rate! Consider investing surplus for long-term growth")

    return recommendations


def generate_budget_recommendations() -> List[str]:
    """Generate budget-related recommendations.

    Returns:
        List of recommendation strings
    """
    recommendations = []
    budgets = read_budgets()

    if not budgets:
        recommendations.append("Set budgets for better financial control and tracking")
    else:
        budget_data = get_budget_data()
        over_budget = sum(1 for b in budget_data if b['utilization'] >= 100)

        if over_budget > len(budget_data) / 2:
            recommendations.append("Review budget allocations - more than half are exceeded")

    return recommendations


def generate_health_recommendations() -> List[str]:
    """Generate recommendations based on financial health score.

    Returns:
        List of recommendation strings
    """
    recommendations = []
    health_score = calculate_overall_health_score()

    if health_score < 40:
        recommendations.append("Focus on reducing expenses and increasing savings to improve financial health")
    elif health_score < 60:
        recommendations.append("Good progress! Work on budget adherence to improve your score")
    elif health_score < 80:
        recommendations.append("Excellent! Maintain current habits and look for optimization opportunities")
    else:
        recommendations.append("Outstanding financial health! Consider increasing investment contributions")

    return recommendations


def generate_all_recommendations() -> List[str]:
    """Generate all recommendations.

    Returns:
        Combined list of all recommendations
    """
    all_recs = []

    all_recs.extend(generate_spending_recommendations())
    all_recs.extend(generate_savings_recommendations())
    all_recs.extend(generate_budget_recommendations())
    all_recs.extend(generate_health_recommendations())

    return all_recs


# ============================================================================
# SAVINGS OPPORTUNITY ANALYSIS
# ============================================================================

def find_savings_opportunities() -> List[Dict]:
    """Find categories where spending can be reduced.

    Returns:
        List of opportunity dictionaries
    """
    opportunities = []
    current_month = get_current_month()
    total_spending = calculate_total_spending(current_month)

    if total_spending == 0:
        return opportunities

    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, current_month)
    expenses = filter_by_type(month_transactions, "expense")

    # Calculate spending per category
    category_spending = {}
    for expense in expenses:
        cat = expense['category']
        category_spending[cat] = category_spending.get(cat, 0) + expense['amount_paisa']

    # Find categories with >25% of total spending
    for category, amount in category_spending.items():
        percentage = (amount / total_spending) * 100

        if percentage > 25:
            # Suggest 15% reduction
            potential_savings = int(amount * 0.15)
            opportunities.append({
                'category': category,
                'current_spending': amount,
                'percentage_of_total': percentage,
                'suggested_reduction': 15,
                'potential_monthly_savings': potential_savings,
                'potential_annual_savings': potential_savings * 12
            })

    return opportunities


def calculate_potential_savings(category: str, reduction_percent: float) -> int:
    """Calculate potential savings from reducing category spending.

    Args:
        category: Category name
        reduction_percent: Percentage to reduce (0-100)

    Returns:
        Potential monthly savings in paisa
    """
    current_month = get_current_month()
    transactions = read_transactions()
    month_transactions = filter_transactions_by_month(transactions, current_month)
    expenses = filter_by_type(month_transactions, "expense")
    category_expenses = filter_by_category(expenses, category)

    current_spending = sum(t['amount_paisa'] for t in category_expenses)
    return int(current_spending * (reduction_percent / 100))


# ============================================================================
# GOAL CALCULATION FUNCTIONS
# ============================================================================

def calculate_goal_progress(goal: Dict) -> float:
    """Calculate goal completion percentage.

    Args:
        goal: Goal dictionary

    Returns:
        Progress percentage (0-100)
    """
    if goal['target_paisa'] == 0:
        return 100.0

    progress = (goal['current_paisa'] / goal['target_paisa']) * 100
    return min(100.0, progress)


def calculate_required_monthly_savings(goal: Dict) -> int:
    """Calculate required monthly savings to meet goal deadline.

    Args:
        goal: Goal dictionary

    Returns:
        Required monthly savings in paisa
    """
    remaining = goal['target_paisa'] - goal['current_paisa']
    if remaining <= 0:
        return 0

    months_left = calculate_months_until_deadline(goal['deadline'])
    if months_left <= 0:
        return remaining  # Need it all now

    return remaining // months_left


def calculate_expected_completion_date(goal: Dict) -> str:
    """Calculate expected completion date based on current savings rate.

    Args:
        goal: Goal dictionary

    Returns:
        Expected completion date or "Unknown"
    """
    current_month = get_current_month()
    monthly_savings = calculate_monthly_savings(current_month)

    if monthly_savings <= 0:
        return "Unknown (no current savings)"

    remaining = goal['target_paisa'] - goal['current_paisa']
    if remaining <= 0:
        return "Completed"

    months_needed = remaining // monthly_savings
    expected_date = datetime.now() + timedelta(days=months_needed * 30)

    return expected_date.strftime("%B %Y")


def is_goal_on_track(goal: Dict) -> bool:
    """Check if goal is on track to meet deadline.

    Args:
        goal: Goal dictionary

    Returns:
        True if on track, False otherwise
    """
    progress = calculate_goal_progress(goal)
    months_passed = calculate_months_since_creation(goal['created_date'])
    months_total = calculate_months_between(goal['created_date'], goal['deadline'])

    if months_total == 0:
        return progress >= 100

    expected_progress = (months_passed / months_total) * 100
    return progress >= expected_progress


def calculate_days_until_deadline(deadline: str) -> int:
    """Calculate days until deadline.

    Args:
        deadline: Deadline in YYYY-MM-DD format

    Returns:
        Days until deadline (negative if passed)
    """
    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        today = datetime.now()
        delta = deadline_date - today
        return delta.days
    except:
        return 0


def calculate_months_until_deadline(deadline: str) -> int:
    """Calculate months until deadline.

    Args:
        deadline: Deadline in YYYY-MM-DD format

    Returns:
        Months until deadline
    """
    days = calculate_days_until_deadline(deadline)
    return max(1, days // 30)


def calculate_months_since_creation(created_date: str) -> int:
    """Calculate months since goal creation.

    Args:
        created_date: Creation date in YYYY-MM-DD format

    Returns:
        Months since creation
    """
    try:
        created = datetime.strptime(created_date, "%Y-%m-%d")
        today = datetime.now()
        delta = today - created
        return max(0, delta.days // 30)
    except:
        return 0


def calculate_months_between(start_date: str, end_date: str) -> int:
    """Calculate months between two dates.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Months between dates
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        delta = end - start
        return max(1, delta.days // 30)
    except:
        return 1


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_daily_financial_check() -> None:
    """Display daily financial check with today's status."""
    today = datetime.now().strftime("%B %d, %Y")

    # Calculate metrics
    today_spending = calculate_today_spending()
    daily_budget = calculate_daily_budget()
    remaining = calculate_daily_remaining()
    on_track = is_on_daily_track()

    # Get alerts
    alerts = get_active_alerts()
    critical_alerts = [a for a in alerts if a['type'] == 'critical'][:2]

    # Get random tip
    tip = random.choice(FINANCIAL_TIPS)

    # Build check display
    status_emoji = "OK" if on_track else "!!"
    status_color = "green" if on_track else "yellow"

    check_content = f"""[bold cyan]{today}[/bold cyan]

[bold yellow]Today's Spending:[/bold yellow]     {format_amount(today_spending)}
[bold yellow]Daily Budget:[/bold yellow]        {format_amount(daily_budget)} [{status_color}]{status_emoji}[/{status_color}]
[bold yellow]Remaining:[/bold yellow]           [{status_color}]{format_amount(remaining)}[/{status_color}]
"""

    if alerts:
        check_content += f"\n[bold red]!! Active Alerts: {len(alerts)}[/bold red]\n"
        for alert in critical_alerts:
            check_content += f"[red]• {alert['message']}[/red]\n"

    check_content += f"""
[bold cyan]Tip of the Day[/bold cyan]
{tip}"""

    panel = Panel(
        check_content,
        title="Daily Financial Check",
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2)
    )

    console.print()
    console.print(panel)


def display_all_alerts() -> None:
    """Display all active alerts organized by priority."""
    console.print(f"\n[bold cyan]Financial Alerts[/bold cyan]\n")

    alerts = get_active_alerts()

    if not alerts:
        console.print("[green] No alerts! Your finances are in good shape.[/green]\n")
        return

    # Group by type
    critical = [a for a in alerts if a['type'] == 'critical']
    warning = [a for a in alerts if a['type'] == 'warning']
    info = [a for a in alerts if a['type'] == 'info']
    success = [a for a in alerts if a['type'] == 'success']

    if critical:
        console.print("[bold red]=� CRITICAL ALERTS:[/bold red]")
        for alert in critical:
            console.print(f"  [red]• {alert['message']}[/red]")
        console.print()

    if warning:
        console.print("[bold yellow]   WARNING ALERTS:[/bold yellow]")
        for alert in warning:
            console.print(f"  [yellow]• {alert['message']}[/yellow]")
        console.print()

    if info:
        console.print("[bold blue]9  INFO:[/bold blue]")
        for alert in info:
            console.print(f"  [blue]• {alert['message']}[/blue]")
        console.print()

    if success:
        console.print("[bold green] ACHIEVEMENTS:[/bold green]")
        for alert in success:
            console.print(f"  [green]• {alert['message']}[/green]")
        console.print()


def display_smart_recommendations() -> None:
    """Display smart recommendations based on financial behavior."""
    console.print(f"\n[bold cyan]=� Smart Recommendations[/bold cyan]\n")

    recommendations = generate_all_recommendations()

    if not recommendations:
        console.print("[green] No recommendations right now. Keep up the good work![/green]\n")
        return

    for i, rec in enumerate(recommendations, 1):
        console.print(f"  {i}. {rec}")

    console.print()


def display_savings_opportunities() -> None:
    """Display savings opportunities with potential savings."""
    console.print(f"\n[bold cyan]=� Savings Opportunities[/bold cyan]\n")

    opportunities = find_savings_opportunities()

    if not opportunities:
        console.print("[yellow]No major savings opportunities identified. Your spending is well-distributed.[/yellow]\n")
        return

    table = Table(title="Potential Savings", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Current", justify="right")
    table.add_column("% of Total", justify="right")
    table.add_column("Suggested Cut", justify="right")
    table.add_column("Monthly Savings", justify="right", style="green")
    table.add_column("Annual Savings", justify="right", style="green bold")

    for opp in opportunities:
        table.add_row(
            opp['category'],
            format_amount(opp['current_spending']),
            f"{opp['percentage_of_total']:.1f}%",
            f"{opp['suggested_reduction']}%",
            format_amount(opp['potential_monthly_savings']),
            format_amount(opp['potential_annual_savings'])
        )

    console.print(table)
    console.print()


def display_all_goals() -> None:
    """Display all financial goals with progress."""
    console.print(f"\n[bold cyan]<� Financial Goals[/bold cyan]\n")

    goals = read_goals()

    if not goals:
        console.print("[yellow]No goals set yet. Create a goal to start tracking your progress![/yellow]\n")
        return

    for goal in goals:
        progress = calculate_goal_progress(goal)
        days_left = calculate_days_until_deadline(goal['deadline'])
        required_monthly = calculate_required_monthly_savings(goal)
        on_track = is_goal_on_track(goal)

        # Progress bar
        filled = int(progress / 10)
        bar = "�" * filled + "�" * (10 - filled)

        status_color = "green" if on_track else "yellow" if days_left > 0 else "red"
        status_text = "On Track " if on_track else "Behind Schedule  " if days_left > 0 else "Past Deadline L"

        console.print(f"[bold]{goal['name']}[/bold] ({goal['goal_type']})")
        console.print(f"Progress: [[{status_color}]{bar}[/{status_color}]] {progress:.1f}%")
        console.print(f"Saved: {format_amount(goal['current_paisa'])} / {format_amount(goal['target_paisa'])}")
        console.print(f"Required: {format_amount(required_monthly)}/month to meet goal")
        console.print(f"Deadline: {goal['deadline']} ({days_left} days) - [{status_color}]{status_text}[/{status_color}]")
        console.print()


def display_goal_summary() -> None:
    """Display quick summary of all goals."""
    goals = read_goals()

    if not goals:
        console.print("[yellow]No goals set[/yellow]")
        return

    total_target = sum(g['target_paisa'] for g in goals)
    total_saved = sum(g['current_paisa'] for g in goals)
    total_remaining = total_target - total_saved

    console.print(f"\n[bold cyan]Goals Summary[/bold cyan]")
    console.print(f"Active Goals: {len(goals)}")
    console.print(f"Total Target: {format_amount(total_target)}")
    console.print(f"Total Saved: {format_amount(total_saved)}")
    console.print(f"Remaining: {format_amount(total_remaining)}\n")


def display_daily_tip() -> None:
    """Display random financial tip."""
    tip = random.choice(FINANCIAL_TIPS)
    panel = Panel(
        tip,
        title="=� Financial Tip of the Day",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print()
    console.print(panel)


def display_what_if_results(scenario: str, monthly_impact: int, annual_impact: int) -> None:
    """Display what-if scenario results.

    Args:
        scenario: Scenario description
        monthly_impact: Monthly impact in paisa
        annual_impact: Annual impact in paisa
    """
    color = "green" if monthly_impact > 0 else "red"

    result = f"""[bold]Scenario:[/bold] {scenario}

[bold]Monthly Impact:[/bold] [{color}]{format_amount(monthly_impact)}[/{color}]
[bold]Annual Impact:[/bold] [{color}]{format_amount(annual_impact)}[/{color}]"""

    panel = Panel(result, title="What-If Analysis", border_style="blue")
    console.print()
    console.print(panel)


# ============================================================================
# FEATURE IMPLEMENTATIONS
# ============================================================================

def daily_check() -> None:
    """Show daily financial check."""
    display_daily_financial_check()


def view_all_alerts() -> None:
    """Show all alerts."""
    display_all_alerts()


def smart_recommendations() -> None:
    """Show smart recommendations."""
    display_smart_recommendations()


def savings_opportunities() -> None:
    """Show savings opportunities."""
    display_savings_opportunities()


def create_goal() -> None:
    """Create a new financial goal."""
    console.print("\n[bold cyan]Create New Goal[/bold cyan]\n")

    # Get goal name
    name = questionary.text(
        "Enter goal name:",
        validate=lambda text: len(text) > 0 or "Goal name cannot be empty"
    ).ask()

    if name is None:
        return

    # Get goal type
    goal_type = questionary.select(
        "Select goal type:",
        choices=GOAL_TYPES
    ).ask()

    if goal_type is None:
        return

    # Get target amount
    while True:
        amount_str = questionary.text(
            "Enter target amount (in Rs):",
            validate=lambda text: len(text) > 0 or "Amount cannot be empty"
        ).ask()

        if amount_str is None:
            return

        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[red]Amount must be positive[/red]")
                continue
            target_paisa = int(amount_float * 100)
            break
        except ValueError:
            console.print("[red]Invalid amount[/red]")

    # Get deadline
    while True:
        deadline_str = questionary.text(
            "Enter deadline (YYYY-MM-DD):",
            validate=lambda text: len(text) > 0 or "Deadline cannot be empty"
        ).ask()

        if deadline_str is None:
            return

        try:
            deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d")
            if deadline_date < datetime.now():
                console.print("[red]Deadline must be in the future[/red]")
                continue
            break
        except ValueError:
            console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")

    # Create goal
    if write_goal(name, target_paisa, deadline_str, goal_type):
        console.print(f"\n[green] Goal '{name}' created successfully![/green]")
        console.print(f"Target: {format_amount(target_paisa)} by {deadline_str}")
    else:
        console.print(f"\n[red] Failed to create goal[/red]")


def view_goals() -> None:
    """View all financial goals."""
    display_all_goals()
    display_goal_summary()


def update_goal() -> None:
    """Update goal progress."""
    goals = read_goals()

    if not goals:
        console.print("[yellow]No goals to update[/yellow]")
        return

    console.print("\n[bold cyan]Update Goal Progress[/bold cyan]\n")

    # Select goal
    goal_names = [g['name'] for g in goals]
    selected_name = questionary.select(
        "Select goal to update:",
        choices=goal_names
    ).ask()

    if selected_name is None:
        return

    goal = get_goal_by_name(selected_name)

    # Show current progress
    progress = calculate_goal_progress(goal)
    console.print(f"\n[bold]Current Progress:[/bold]")
    console.print(f"Saved: {format_amount(goal['current_paisa'])} / {format_amount(goal['target_paisa'])} ({progress:.1f}%)")

    # Get amount to add
    while True:
        amount_str = questionary.text(
            "\nEnter amount to add (in Rs):",
            validate=lambda text: len(text) > 0 or "Amount cannot be empty"
        ).ask()

        if amount_str is None:
            return

        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[red]Amount must be positive[/red]")
                continue
            additional_paisa = int(amount_float * 100)
            break
        except ValueError:
            console.print("[red]Invalid amount[/red]")

    # Update goal
    if update_goal_progress(selected_name, additional_paisa):
        new_progress = calculate_goal_progress(get_goal_by_name(selected_name))
        console.print(f"\n[green] Goal updated! Progress: {new_progress:.1f}%[/green]")

        if new_progress >= 100:
            console.print("[green bold]<� Congratulations! Goal completed![/green bold]")
    else:
        console.print(f"\n[red] Failed to update goal[/red]")


def delete_goal_ui() -> None:
    """Delete a financial goal."""
    goals = read_goals()

    if not goals:
        console.print("[yellow]No goals to delete[/yellow]")
        return

    console.print("\n[bold cyan]Delete Goal[/bold cyan]\n")

    # Select goal
    goal_names = [g['name'] for g in goals]
    selected_name = questionary.select(
        "Select goal to delete:",
        choices=goal_names
    ).ask()

    if selected_name is None:
        return

    # Confirm
    confirm = questionary.confirm(
        f"Are you sure you want to delete '{selected_name}'?",
        default=False
    ).ask()

    if confirm:
        if delete_goal(selected_name):
            console.print(f"\n[green] Goal '{selected_name}' deleted[/green]")
        else:
            console.print(f"\n[red] Failed to delete goal[/red]")


def financial_tips() -> None:
    """Display financial tips."""
    console.print("\n[bold cyan]=� Financial Tips[/bold cyan]\n")

    console.print("Would you like to:")
    choice = questionary.select(
        "",
        choices=[
            "View random tip",
            "View all tips",
            "Back"
        ]
    ).ask()

    if choice == "View random tip":
        display_daily_tip()
    elif choice == "View all tips":
        console.print()
        for i, tip in enumerate(FINANCIAL_TIPS, 1):
            console.print(f"{i}. {tip}")
        console.print()


def what_if_calculator() -> None:
    """What-if scenario calculator."""
    console.print("\n[bold cyan]=� What-If Calculator[/bold cyan]\n")

    choice = questionary.select(
        "Select scenario:",
        choices=[
            "Reduce category spending",
            "Eliminate category completely",
            "Increase income",
            "Increase monthly savings",
            "Back"
        ]
    ).ask()

    if choice is None or choice == "Back":
        return

    current_month = get_current_month()

    if choice == "Reduce category spending":
        # Get category and reduction percentage
        from transactions.transactions import EXPENSE_CATEGORIES

        category = questionary.select("Select category:", choices=EXPENSE_CATEGORIES).ask()
        if category is None:
            return

        reduction_str = questionary.text("Enter reduction percentage (e.g., 20):").ask()
        if reduction_str is None:
            return

        try:
            reduction = float(reduction_str)
            monthly_savings = calculate_potential_savings(category, reduction)
            annual_savings = monthly_savings * 12

            display_what_if_results(
                f"Reduce {category} by {reduction}%",
                monthly_savings,
                annual_savings
            )
        except ValueError:
            console.print("[red]Invalid percentage[/red]")

    elif choice == "Eliminate category completely":
        from transactions.transactions import EXPENSE_CATEGORIES

        category = questionary.select("Select category:", choices=EXPENSE_CATEGORIES).ask()
        if category is None:
            return

        monthly_savings = calculate_potential_savings(category, 100)
        annual_savings = monthly_savings * 12

        display_what_if_results(
            f"Eliminate {category} completely",
            monthly_savings,
            annual_savings
        )

    elif choice == "Increase income":
        increase_str = questionary.text("Enter additional monthly income (in Rs):").ask()
        if increase_str is None:
            return

        try:
            increase_float = float(increase_str)
            increase_paisa = int(increase_float * 100)

            current_income = calculate_total_income_month(current_month)
            current_expenses = calculate_total_spending(current_month)
            new_income = current_income + increase_paisa
            new_savings_rate = ((new_income - current_expenses) / new_income * 100) if new_income > 0 else 0

            console.print(f"\n[bold cyan]Income Increase Analysis[/bold cyan]")
            console.print(f"New Monthly Income: {format_amount(new_income)}")
            console.print(f"New Savings Rate: {new_savings_rate:.1f}%")
            console.print(f"Additional Annual Income: {format_amount(increase_paisa * 12)}\n")
        except ValueError:
            console.print("[red]Invalid amount[/red]")

    elif choice == "Increase monthly savings":
        increase_str = questionary.text("Enter additional monthly savings (in Rs):").ask()
        if increase_str is None:
            return

        try:
            increase_float = float(increase_str)
            increase_paisa = int(increase_float * 100)

            annual_savings = increase_paisa * 12

            console.print(f"\n[bold cyan]Savings Increase Analysis[/bold cyan]")
            console.print(f"Additional Monthly: {format_amount(increase_paisa)}")
            console.print(f"Additional Annual: {format_amount(annual_savings)}")
            console.print(f"5-Year Impact: {format_amount(annual_savings * 5)}\n")

            # Show goal impact
            goals = read_goals()
            if goals:
                console.print("[bold]Impact on Goals:[/bold]")
                for goal in goals:
                    remaining = goal['target_paisa'] - goal['current_paisa']
                    if remaining > 0:
                        months_to_complete = remaining // increase_paisa if increase_paisa > 0 else 999
                        console.print(f"  • {goal['name']}: Complete in ~{months_to_complete} months")
                console.print()
        except ValueError:
            console.print("[red]Invalid amount[/red]")


# ============================================================================
# GOALS SUBMENU
# ============================================================================

def financial_goals_menu() -> None:
    """Financial goals management submenu."""
    while True:
        console.print()
        choice = questionary.select(
            "Financial Goals",
            choices=[
                "Create New Goal",
                "View All Goals",
                "Update Goal Progress",
                "Delete Goal",
                "Back"
            ]
        ).ask()

        if choice is None or choice == "Back":
            break

        if choice == "Create New Goal":
            create_goal()
        elif choice == "View All Goals":
            view_goals()
        elif choice == "Update Goal Progress":
            update_goal()
        elif choice == "Delete Goal":
            delete_goal_ui()


# ============================================================================
# SMART ASSISTANT MENU
# ============================================================================

def smart_assistant_menu() -> None:
    """Display and handle smart assistant menu."""
    while True:
        console.print()
        choice = questionary.select(
            "Smart Financial Assistant",
            choices=[
                "Daily Financial Check",
                "View All Alerts",
                "Smart Recommendations",
                "Savings Opportunities",
                "Financial Goals",
                "Financial Tips",
                "What-If Calculator",
                "Back to Main Menu"
            ]
        ).ask()

        if choice is None or choice == "Back to Main Menu":
            break

        if choice == "Daily Financial Check":
            daily_check()
        elif choice == "View All Alerts":
            view_all_alerts()
        elif choice == "Smart Recommendations":
            smart_recommendations()
        elif choice == "Savings Opportunities":
            savings_opportunities()
        elif choice == "Financial Goals":
            financial_goals_menu()
        elif choice == "Financial Tips":
            financial_tips()
        elif choice == "What-If Calculator":
            what_if_calculator()
