"""Transaction Management Feature

Handles all transaction operations including adding, viewing, editing,
deleting, and searching transactions.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Constants
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]
DATABASE_DIR = Path("database")
TRANSACTIONS_FILE = DATABASE_DIR / "transactions.txt"


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensure_database_exists() -> None:
    """Create database directory and files if they don't exist."""
    DATABASE_DIR.mkdir(exist_ok=True)
    if not TRANSACTIONS_FILE.exists():
        TRANSACTIONS_FILE.touch()


def read_transactions() -> List[Dict]:
    """Read all transactions from file.

    Returns:
        List of transaction dictionaries with keys: date, type, category, amount_paisa, description
    """
    ensure_database_exists()
    transactions = []

    if not TRANSACTIONS_FILE.exists() or TRANSACTIONS_FILE.stat().st_size == 0:
        return transactions

    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    parts = line.split('|')
                    if len(parts) != 5:
                        console.print(f"[yellow]Warning: Skipping malformed line {line_num}[/yellow]")
                        continue

                    date, trans_type, category, amount_paisa, description = parts

                    # Validate data
                    if trans_type not in ["expense", "income"]:
                        console.print(f"[yellow]Warning: Invalid type on line {line_num}[/yellow]")
                        continue

                    transactions.append({
                        "date": date,
                        "type": trans_type,
                        "category": category,
                        "amount_paisa": int(amount_paisa),
                        "description": description
                    })
                except (ValueError, IndexError) as e:
                    console.print(f"[yellow]Warning: Error parsing line {line_num}: {e}[/yellow]")
                    continue
    except Exception as e:
        console.print(f"[red]Error reading transactions file: {e}[/red]")

    return transactions


def write_transaction(date: str, trans_type: str, category: str, amount_paisa: int, description: str) -> bool:
    """Append a new transaction to file.

    Args:
        date: Transaction date in YYYY-MM-DD format
        trans_type: "expense" or "income"
        category: Transaction category
        amount_paisa: Amount in paisa (smallest unit)
        description: Transaction description

    Returns:
        True if successful, False otherwise
    """
    ensure_database_exists()

    try:
        with open(TRANSACTIONS_FILE, 'a', encoding='utf-8') as f:
            line = f"{date}|{trans_type}|{category}|{amount_paisa}|{description}\n"
            f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error writing transaction: {e}[/red]")
        return False


def update_transaction(index: int, updated_data: Dict) -> bool:
    """Update an existing transaction.

    Args:
        index: Index of transaction to update (0-based)
        updated_data: Dictionary with updated transaction data

    Returns:
        True if successful, False otherwise
    """
    transactions = read_transactions()

    if index < 0 or index >= len(transactions):
        console.print("[red]Invalid transaction index[/red]")
        return False

    transactions[index] = updated_data

    try:
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            for trans in transactions:
                line = f"{trans['date']}|{trans['type']}|{trans['category']}|{trans['amount_paisa']}|{trans['description']}\n"
                f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error updating transaction: {e}[/red]")
        return False


def delete_transaction(index: int) -> bool:
    """Delete a transaction.

    Args:
        index: Index of transaction to delete (0-based)

    Returns:
        True if successful, False otherwise
    """
    transactions = read_transactions()

    if index < 0 or index >= len(transactions):
        console.print("[red]Invalid transaction index[/red]")
        return False

    transactions.pop(index)

    try:
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            for trans in transactions:
                line = f"{trans['date']}|{trans['type']}|{trans['category']}|{trans['amount_paisa']}|{trans['description']}\n"
                f.write(line)
        return True
    except Exception as e:
        console.print(f"[red]Error deleting transaction: {e}[/red]")
        return False


# ============================================================================
# INPUT FUNCTIONS
# ============================================================================

def get_amount() -> Optional[int]:
    """Get amount from user and convert to paisa.

    Returns:
        Amount in paisa (int) or None if invalid
    """
    while True:
        amount_str = questionary.text(
            "Enter amount (in Rs):",
            validate=lambda text: len(text) > 0 or "Amount cannot be empty"
        ).ask()

        if amount_str is None:  # User cancelled
            return None

        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[red]Amount must be positive[/red]")
                continue

            # Convert to paisa (multiply by 100)
            amount_paisa = int(amount_float * 100)
            return amount_paisa
        except ValueError:
            console.print("[red]Invalid amount. Please enter a valid number[/red]")


def get_category(transaction_type: str) -> Optional[str]:
    """Get category based on transaction type.

    Args:
        transaction_type: "expense" or "income"

    Returns:
        Selected category or None if cancelled
    """
    categories = EXPENSE_CATEGORIES if transaction_type == "expense" else INCOME_CATEGORIES

    category = questionary.select(
        f"Select {'expense' if transaction_type == 'expense' else 'income'} category:",
        choices=categories
    ).ask()

    return category


def get_description() -> Optional[str]:
    """Get transaction description from user.

    Returns:
        Description string or None if cancelled
    """
    description = questionary.text(
        "Enter description:",
        validate=lambda text: len(text) > 0 or "Description cannot be empty"
    ).ask()

    return description


def get_date() -> Optional[str]:
    """Get date from user (default: today).

    Returns:
        Date in YYYY-MM-DD format or None if cancelled
    """
    today = datetime.now().strftime("%Y-%m-%d")

    use_today = questionary.confirm(
        f"Use today's date ({today})?",
        default=True
    ).ask()

    if use_today is None:  # User cancelled
        return None

    if use_today:
        return today

    while True:
        date_str = questionary.text(
            "Enter date (YYYY-MM-DD):",
            validate=lambda text: len(text) > 0 or "Date cannot be empty"
        ).ask()

        if date_str is None:  # User cancelled
            return None

        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM-DD[/red]")


def get_transaction_type() -> Optional[str]:
    """Get transaction type from user.

    Returns:
        "expense" or "income" or None if cancelled
    """
    trans_type = questionary.select(
        "Select transaction type:",
        choices=["Expense", "Income"]
    ).ask()

    if trans_type is None:
        return None

    return trans_type.lower()


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_total_income(transactions: List[Dict]) -> int:
    """Calculate total income in paisa.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Total income in paisa
    """
    return sum(t['amount_paisa'] for t in transactions if t['type'] == 'income')


def calculate_total_expenses(transactions: List[Dict]) -> int:
    """Calculate total expenses in paisa.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Total expenses in paisa
    """
    return sum(t['amount_paisa'] for t in transactions if t['type'] == 'expense')


def calculate_balance(transactions: List[Dict]) -> int:
    """Calculate balance (income - expenses) in paisa.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Balance in paisa
    """
    return calculate_total_income(transactions) - calculate_total_expenses(transactions)


def get_category_total(transactions: List[Dict], category: str) -> int:
    """Get total for a specific category in paisa.

    Args:
        transactions: List of transaction dictionaries
        category: Category name

    Returns:
        Total amount in paisa for the category
    """
    return sum(t['amount_paisa'] for t in transactions if t['category'] == category)


# ============================================================================
# FILTER FUNCTIONS
# ============================================================================

def filter_by_date_range(transactions: List[Dict], start_date: str, end_date: str) -> List[Dict]:
    """Filter transactions by date range.

    Args:
        transactions: List of transaction dictionaries
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Filtered list of transactions
    """
    return [t for t in transactions if start_date <= t['date'] <= end_date]


def filter_by_type(transactions: List[Dict], trans_type: str) -> List[Dict]:
    """Filter transactions by type.

    Args:
        transactions: List of transaction dictionaries
        trans_type: "expense" or "income"

    Returns:
        Filtered list of transactions
    """
    return [t for t in transactions if t['type'] == trans_type]


def filter_by_category(transactions: List[Dict], category: str) -> List[Dict]:
    """Filter transactions by category.

    Args:
        transactions: List of transaction dictionaries
        category: Category name

    Returns:
        Filtered list of transactions
    """
    return [t for t in transactions if t['category'] == category]


def filter_last_n_days(transactions: List[Dict], n: int) -> List[Dict]:
    """Filter transactions from last N days.

    Args:
        transactions: List of transaction dictionaries
        n: Number of days

    Returns:
        Filtered list of transactions
    """
    cutoff_date = (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")
    return [t for t in transactions if t['date'] >= cutoff_date]


def search_description(transactions: List[Dict], keyword: str) -> List[Dict]:
    """Search transactions by description keyword.

    Args:
        transactions: List of transaction dictionaries
        keyword: Search keyword (case-insensitive)

    Returns:
        Filtered list of transactions
    """
    keyword_lower = keyword.lower()
    return [t for t in transactions if keyword_lower in t['description'].lower()]


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def format_amount(paisa: int) -> str:
    """Format paisa to rupees string.

    Args:
        paisa: Amount in paisa

    Returns:
        Formatted string like "Rs 12.50"
    """
    rupees = paisa / 100
    return f"Rs {rupees:.2f}"


def display_transactions(transactions: List[Dict], title: str = "Transactions") -> None:
    """Display transactions in a rich table.

    Args:
        transactions: List of transaction dictionaries
        title: Table title
    """
    if not transactions:
        console.print("[yellow]No transactions found[/yellow]")
        return

    # Sort by date (newest first)
    sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Date", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Category", style="blue")
    table.add_column("Description", style="white")
    table.add_column("Amount", justify="right")

    for trans in sorted_transactions:
        amount_color = "green" if trans['type'] == 'income' else "red"
        type_display = trans['type'].capitalize()

        table.add_row(
            trans['date'],
            type_display,
            trans['category'],
            trans['description'],
            f"[{amount_color}]{format_amount(trans['amount_paisa'])}[/{amount_color}]"
        )

    console.print(table)


def display_balance(transactions: List[Dict], period: str = "All Time") -> None:
    """Display income, expenses, and balance summary.

    Args:
        transactions: List of transaction dictionaries
        period: Period description for display
    """
    total_income = calculate_total_income(transactions)
    total_expenses = calculate_total_expenses(transactions)
    balance = calculate_balance(transactions)

    balance_color = "green" if balance >= 0 else "red"

    summary = f"""[green]Total Income:[/green]  {format_amount(total_income)}
[red]Total Expenses:[/red] {format_amount(total_expenses)}
[{balance_color}]Balance:[/{balance_color}]        {format_amount(balance)}"""

    panel = Panel(summary, title=f"Financial Summary - {period}", border_style="blue")
    console.print(panel)


def show_success(message: str) -> None:
    """Display success message.

    Args:
        message: Success message to display
    """
    console.print(f"[green] {message}[/green]")


def show_error(message: str) -> None:
    """Display error message.

    Args:
        message: Error message to display
    """
    console.print(f"[red] {message}[/red]")


# ============================================================================
# FEATURE IMPLEMENTATIONS
# ============================================================================

def add_expense() -> None:
    """Add a new expense transaction."""
    console.print("\n[bold cyan]Add Expense[/bold cyan]\n")

    amount_paisa = get_amount()
    if amount_paisa is None:
        return

    category = get_category("expense")
    if category is None:
        return

    description = get_description()
    if description is None:
        return

    date = get_date()
    if date is None:
        return

    if write_transaction(date, "expense", category, amount_paisa, description):
        show_success(f"Expense of {format_amount(amount_paisa)} added successfully!")
    else:
        show_error("Failed to add expense")


def add_income() -> None:
    """Add a new income transaction."""
    console.print("\n[bold cyan]Add Income[/bold cyan]\n")

    amount_paisa = get_amount()
    if amount_paisa is None:
        return

    category = get_category("income")
    if category is None:
        return

    description = get_description()
    if description is None:
        return

    date = get_date()
    if date is None:
        return

    if write_transaction(date, "income", category, amount_paisa, description):
        show_success(f"Income of {format_amount(amount_paisa)} added successfully!")
    else:
        show_error("Failed to add income")


def view_transactions() -> None:
    """View transactions with filtering options."""
    transactions = read_transactions()

    if not transactions:
        console.print("[yellow]No transactions found[/yellow]")
        return

    filter_choice = questionary.select(
        "Select view option:",
        choices=[
            "All Transactions",
            "Last 7 Days",
            "Last 30 Days",
            "Only Expenses",
            "Only Income",
            "By Category",
            "Custom Date Range"
        ]
    ).ask()

    if filter_choice is None:
        return

    if filter_choice == "All Transactions":
        display_transactions(transactions)
    elif filter_choice == "Last 7 Days":
        filtered = filter_last_n_days(transactions, 7)
        display_transactions(filtered, "Transactions - Last 7 Days")
    elif filter_choice == "Last 30 Days":
        filtered = filter_last_n_days(transactions, 30)
        display_transactions(filtered, "Transactions - Last 30 Days")
    elif filter_choice == "Only Expenses":
        filtered = filter_by_type(transactions, "expense")
        display_transactions(filtered, "Expense Transactions")
    elif filter_choice == "Only Income":
        filtered = filter_by_type(transactions, "income")
        display_transactions(filtered, "Income Transactions")
    elif filter_choice == "By Category":
        # Get all unique categories
        categories = sorted(set(t['category'] for t in transactions))
        category = questionary.select("Select category:", choices=categories).ask()
        if category:
            filtered = filter_by_category(transactions, category)
            display_transactions(filtered, f"Transactions - {category}")
    elif filter_choice == "Custom Date Range":
        start_date = questionary.text("Enter start date (YYYY-MM-DD):").ask()
        end_date = questionary.text("Enter end date (YYYY-MM-DD):").ask()
        if start_date and end_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
                filtered = filter_by_date_range(transactions, start_date, end_date)
                display_transactions(filtered, f"Transactions - {start_date} to {end_date}")
            except ValueError:
                show_error("Invalid date format")


def view_balance() -> None:
    """View balance summary with period options."""
    transactions = read_transactions()

    if not transactions:
        console.print("[yellow]No transactions found[/yellow]")
        return

    period_choice = questionary.select(
        "Select period:",
        choices=[
            "All Time",
            "Current Month",
            "Last 30 Days",
            "Last 7 Days"
        ]
    ).ask()

    if period_choice is None:
        return

    if period_choice == "All Time":
        display_balance(transactions, "All Time")
    elif period_choice == "Current Month":
        today = datetime.now()
        start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
        end_of_month = today.strftime("%Y-%m-%d")
        filtered = filter_by_date_range(transactions, start_of_month, end_of_month)
        display_balance(filtered, "Current Month")
    elif period_choice == "Last 30 Days":
        filtered = filter_last_n_days(transactions, 30)
        display_balance(filtered, "Last 30 Days")
    elif period_choice == "Last 7 Days":
        filtered = filter_last_n_days(transactions, 7)
        display_balance(filtered, "Last 7 Days")


def edit_transaction() -> None:
    """Edit an existing transaction."""
    transactions = read_transactions()

    if not transactions:
        console.print("[yellow]No transactions to edit[/yellow]")
        return

    # Display transactions with index numbers
    console.print("\n[bold cyan]Select Transaction to Edit[/bold cyan]\n")

    # Create choices with index
    choices = []
    for i, trans in enumerate(transactions):
        amount_str = format_amount(trans['amount_paisa'])
        choice_str = f"{i+1}. {trans['date']} | {trans['type'].capitalize()} | {trans['category']} | {amount_str} | {trans['description']}"
        choices.append(choice_str)

    selected = questionary.select(
        "Select transaction:",
        choices=choices
    ).ask()

    if selected is None:
        return

    # Extract index from selection
    index = int(selected.split('.')[0]) - 1
    trans = transactions[index]

    # Show current values and ask what to edit
    console.print(f"\n[bold]Current values:[/bold]")
    console.print(f"Date: {trans['date']}")
    console.print(f"Type: {trans['type'].capitalize()}")
    console.print(f"Category: {trans['category']}")
    console.print(f"Amount: {format_amount(trans['amount_paisa'])}")
    console.print(f"Description: {trans['description']}\n")

    # Ask which field to edit
    field = questionary.select(
        "What would you like to edit?",
        choices=["Amount", "Category", "Description", "Date", "Cancel"]
    ).ask()

    if field is None or field == "Cancel":
        return

    updated_trans = trans.copy()

    if field == "Amount":
        new_amount = get_amount()
        if new_amount is not None:
            updated_trans['amount_paisa'] = new_amount
    elif field == "Category":
        new_category = get_category(trans['type'])
        if new_category is not None:
            updated_trans['category'] = new_category
    elif field == "Description":
        new_description = get_description()
        if new_description is not None:
            updated_trans['description'] = new_description
    elif field == "Date":
        new_date = get_date()
        if new_date is not None:
            updated_trans['date'] = new_date

    if update_transaction(index, updated_trans):
        show_success("Transaction updated successfully!")
    else:
        show_error("Failed to update transaction")


def delete_transaction_ui() -> None:
    """Delete a transaction."""
    transactions = read_transactions()

    if not transactions:
        console.print("[yellow]No transactions to delete[/yellow]")
        return

    # Display transactions with index numbers
    console.print("\n[bold cyan]Select Transaction to Delete[/bold cyan]\n")

    # Create choices with index
    choices = []
    for i, trans in enumerate(transactions):
        amount_str = format_amount(trans['amount_paisa'])
        choice_str = f"{i+1}. {trans['date']} | {trans['type'].capitalize()} | {trans['category']} | {amount_str} | {trans['description']}"
        choices.append(choice_str)

    selected = questionary.select(
        "Select transaction to delete:",
        choices=choices
    ).ask()

    if selected is None:
        return

    # Extract index from selection
    index = int(selected.split('.')[0]) - 1
    trans = transactions[index]

    # Confirm deletion
    confirm = questionary.confirm(
        f"Are you sure you want to delete this transaction?\n{trans['date']} | {trans['type'].capitalize()} | {trans['category']} | {format_amount(trans['amount_paisa'])} | {trans['description']}",
        default=False
    ).ask()

    if confirm:
        if delete_transaction(index):
            show_success("Transaction deleted successfully!")
        else:
            show_error("Failed to delete transaction")


def search_transactions() -> None:
    """Search transactions by description."""
    transactions = read_transactions()

    if not transactions:
        console.print("[yellow]No transactions found[/yellow]")
        return

    keyword = questionary.text(
        "Enter search keyword:",
        validate=lambda text: len(text) > 0 or "Keyword cannot be empty"
    ).ask()

    if keyword is None:
        return

    results = search_description(transactions, keyword)

    if results:
        display_transactions(results, f"Search Results for '{keyword}'")
    else:
        console.print(f"[yellow]No transactions found matching '{keyword}'[/yellow]")


# ============================================================================
# TRANSACTION MENU
# ============================================================================

def transaction_menu() -> None:
    """Display and handle transaction management menu."""
    while True:
        console.print()
        choice = questionary.select(
            "Transaction Management",
            choices=[
                "Add Expense",
                "Add Income",
                "View Transactions",
                "View Balance",
                "Search Transactions",
                "Edit Transaction",
                "Delete Transaction",
                "Back to Main Menu"
            ]
        ).ask()

        if choice is None or choice == "Back to Main Menu":
            break

        if choice == "Add Expense":
            add_expense()
        elif choice == "Add Income":
            add_income()
        elif choice == "View Transactions":
            view_transactions()
        elif choice == "View Balance":
            view_balance()
        elif choice == "Search Transactions":
            search_transactions()
        elif choice == "Edit Transaction":
            edit_transaction()
        elif choice == "Delete Transaction":
            delete_transaction_ui()
