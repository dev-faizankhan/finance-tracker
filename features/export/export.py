"""Data Management & Export Feature

Provides data export, import, backup, restore, and validation capabilities.
"""

import os
import csv
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
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
    write_transaction,
    format_amount,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES
)
from budgets.budgets import read_budgets, get_budget_data
from smart_assistant.smart_assistant import read_goals
from analytics.analytics import (
    calculate_total_income_month,
    calculate_total_spending,
    calculate_monthly_savings,
    calculate_savings_rate,
    calculate_overall_health_score,
    get_current_month,
    get_month_name,
    get_spending_by_category,
    get_income_by_source,
    compare_with_last_month
)

console = Console()

# Constants
EXPORTS_DIR = Path("exports")
BACKUPS_DIR = Path("backups")
DATABASE_DIR = Path("database")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_directories_exist() -> None:
    """Create necessary directories."""
    EXPORTS_DIR.mkdir(exist_ok=True)
    BACKUPS_DIR.mkdir(exist_ok=True)


def convert_paisa_to_rupees(paisa: int) -> float:
    """Convert paisa to rupees for export.

    Args:
        paisa: Amount in paisa

    Returns:
        Amount in rupees
    """
    return paisa / 100.0


def convert_rupees_to_paisa(rupees: float) -> int:
    """Convert rupees to paisa for import.

    Args:
        rupees: Amount in rupees

    Returns:
        Amount in paisa
    """
    return int(rupees * 100)


def generate_timestamp() -> str:
    """Generate timestamp for filenames.

    Returns:
        Timestamp string in YYYYMMDD_HHMMSS format
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ============================================================================
# EXPORT FUNCTIONS - CSV
# ============================================================================

def export_transactions_csv(filters: Optional[Dict] = None) -> Optional[str]:
    """Export transactions to CSV.

    Args:
        filters: Optional filters (date_range, category, type)

    Returns:
        Filename if successful, None otherwise
    """
    ensure_directories_exist()

    transactions = read_transactions()

    # Apply filters if provided
    if filters:
        if 'type' in filters and filters['type']:
            transactions = [t for t in transactions if t['type'] == filters['type']]
        if 'category' in filters and filters['category']:
            transactions = [t for t in transactions if t['category'] == filters['category']]
        if 'date_range' in filters and filters['date_range']:
            start, end = filters['date_range']
            transactions = [t for t in transactions if start <= t['date'] <= end]

    if not transactions:
        console.print("[yellow]No transactions to export[/yellow]")
        return None

    # Generate filename
    timestamp = generate_timestamp()
    filename = EXPORTS_DIR / f"transactions_{timestamp}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])

            # Write data
            for trans in transactions:
                writer.writerow([
                    trans['date'],
                    trans['type'],
                    trans['category'],
                    f"{convert_paisa_to_rupees(trans['amount_paisa']):.2f}",
                    trans['description']
                ])

        return str(filename)
    except Exception as e:
        console.print(f"[red]Error exporting to CSV: {e}[/red]")
        return None


def export_budgets_csv() -> Optional[str]:
    """Export budgets to CSV.

    Returns:
        Filename if successful, None otherwise
    """
    ensure_directories_exist()

    budget_data = get_budget_data()

    if not budget_data:
        console.print("[yellow]No budgets to export[/yellow]")
        return None

    timestamp = generate_timestamp()
    filename = EXPORTS_DIR / f"budgets_{timestamp}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Category', 'Budget', 'Period', 'Spent', 'Remaining', 'Utilization'])

            # Write data
            for budget in budget_data:
                writer.writerow([
                    budget['category'],
                    f"{convert_paisa_to_rupees(budget['limit_paisa']):.2f}",
                    budget['period'],
                    f"{convert_paisa_to_rupees(budget['spent_paisa']):.2f}",
                    f"{convert_paisa_to_rupees(budget['remaining_paisa']):.2f}",
                    f"{budget['utilization']:.1f}%"
                ])

        return str(filename)
    except Exception as e:
        console.print(f"[red]Error exporting budgets to CSV: {e}[/red]")
        return None


# ============================================================================
# EXPORT FUNCTIONS - JSON
# ============================================================================

def export_transactions_json(filters: Optional[Dict] = None) -> Optional[str]:
    """Export transactions to JSON.

    Args:
        filters: Optional filters

    Returns:
        Filename if successful, None otherwise
    """
    ensure_directories_exist()

    transactions = read_transactions()

    # Apply filters
    if filters:
        if 'type' in filters and filters['type']:
            transactions = [t for t in transactions if t['type'] == filters['type']]
        if 'category' in filters and filters['category']:
            transactions = [t for t in transactions if t['category'] == filters['category']]
        if 'date_range' in filters and filters['date_range']:
            start, end = filters['date_range']
            transactions = [t for t in transactions if start <= t['date'] <= end]

    if not transactions:
        console.print("[yellow]No transactions to export[/yellow]")
        return None

    # Prepare data
    export_data = {
        "transactions": [
            {
                "date": t['date'],
                "type": t['type'],
                "category": t['category'],
                "amount_paisa": t['amount_paisa'],
                "amount_rupees": convert_paisa_to_rupees(t['amount_paisa']),
                "description": t['description']
            }
            for t in transactions
        ],
        "exported_at": datetime.now().isoformat(),
        "total_transactions": len(transactions)
    }

    timestamp = generate_timestamp()
    filename = EXPORTS_DIR / f"transactions_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(filename)
    except Exception as e:
        console.print(f"[red]Error exporting to JSON: {e}[/red]")
        return None


def export_budgets_json() -> Optional[str]:
    """Export budgets to JSON.

    Returns:
        Filename if successful, None otherwise
    """
    ensure_directories_exist()

    budget_data = get_budget_data()

    if not budget_data:
        console.print("[yellow]No budgets to export[/yellow]")
        return None

    export_data = {
        "budgets": [
            {
                "category": b['category'],
                "budget_paisa": b['limit_paisa'],
                "budget_rupees": convert_paisa_to_rupees(b['limit_paisa']),
                "period": b['period'],
                "spent_paisa": b['spent_paisa'],
                "spent_rupees": convert_paisa_to_rupees(b['spent_paisa']),
                "remaining_paisa": b['remaining_paisa'],
                "remaining_rupees": convert_paisa_to_rupees(b['remaining_paisa']),
                "utilization_percent": b['utilization']
            }
            for b in budget_data
        ],
        "exported_at": datetime.now().isoformat(),
        "total_budgets": len(budget_data)
    }

    timestamp = generate_timestamp()
    filename = EXPORTS_DIR / f"budgets_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(filename)
    except Exception as e:
        console.print(f"[red]Error exporting budgets to JSON: {e}[/red]")
        return None


def export_monthly_report(month: Optional[str] = None) -> Optional[str]:
    """Export comprehensive monthly report as JSON.

    Args:
        month: Month in YYYY-MM format (None for current month)

    Returns:
        Filename if successful, None otherwise
    """
    ensure_directories_exist()

    if month is None:
        month = get_current_month()

    # Gather all data
    total_income = calculate_total_income_month(month)
    total_expenses = calculate_total_spending(month)
    savings = calculate_monthly_savings(month)
    savings_rate = calculate_savings_rate(month)
    health_score = calculate_overall_health_score()

    income_breakdown = get_income_by_source(month)
    expense_breakdown = get_spending_by_category(month)
    comparison = compare_with_last_month()

    budget_data = get_budget_data()
    budgets_on_track = sum(1 for b in budget_data if b['utilization'] < 100)

    # Get top transactions
    from transactions.transactions import filter_transactions_by_month, filter_by_type
    all_trans = read_transactions()
    month_trans = [t for t in all_trans if t['date'].startswith(month)]
    expenses = [t for t in month_trans if t['type'] == 'expense']
    top_expenses = sorted(expenses, key=lambda x: x['amount_paisa'], reverse=True)[:5]

    # Build report
    report = {
        "report_period": {
            "month": get_month_name(month).split()[0],
            "year": int(month[:4]),
            "date_range": {
                "start": f"{month}-01",
                "end": f"{month}-{datetime(int(month[:4]), int(month[5:7]), 1).day}"
            }
        },
        "summary": {
            "total_income_paisa": total_income,
            "total_income_rupees": convert_paisa_to_rupees(total_income),
            "total_expenses_paisa": total_expenses,
            "total_expenses_rupees": convert_paisa_to_rupees(total_expenses),
            "net_savings_paisa": savings,
            "net_savings_rupees": convert_paisa_to_rupees(savings),
            "savings_rate_percent": savings_rate,
            "transaction_count": len(month_trans)
        },
        "income_breakdown": [
            {
                "source": source,
                "amount_paisa": amount,
                "amount_rupees": convert_paisa_to_rupees(amount),
                "percentage": (amount / total_income * 100) if total_income > 0 else 0
            }
            for source, amount in income_breakdown.items()
        ],
        "expense_breakdown": [
            {
                "category": cat,
                "amount_paisa": amount,
                "amount_rupees": convert_paisa_to_rupees(amount),
                "percentage": (amount / total_expenses * 100) if total_expenses > 0 else 0
            }
            for cat, amount in expense_breakdown.items()
        ],
        "budget_performance": {
            "total_budgets": len(budget_data),
            "categories_on_track": budgets_on_track,
            "categories_over_budget": len(budget_data) - budgets_on_track
        },
        "financial_health": {
            "score": health_score,
            "rating": "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair" if health_score >= 40 else "Poor"
        },
        "top_transactions": [
            {
                "date": t['date'],
                "type": t['type'],
                "category": t['category'],
                "amount_rupees": convert_paisa_to_rupees(t['amount_paisa']),
                "description": t['description']
            }
            for t in top_expenses
        ],
        "generated_at": datetime.now().isoformat()
    }

    filename = EXPORTS_DIR / f"monthly_report_{month.replace('-', '_')}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(filename)
    except Exception as e:
        console.print(f"[red]Error exporting monthly report: {e}[/red]")
        return None


# ============================================================================
# IMPORT FUNCTIONS
# ============================================================================

def import_transactions_csv(filename: str) -> Optional[Dict]:
    """Import transactions from CSV file.

    Args:
        filename: Path to CSV file

    Returns:
        Import summary dict or None if failed
    """
    if not Path(filename).exists():
        console.print(f"[red]File not found: {filename}[/red]")
        return None

    imported = 0
    skipped = 0
    failed = 0
    errors = []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate headers
            expected_headers = {'Date', 'Type', 'Category', 'Amount', 'Description'}
            if not expected_headers.issubset(set(reader.fieldnames or [])):
                console.print(f"[red]Invalid CSV format. Expected headers: {expected_headers}[/red]")
                return None

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validate and parse row
                    date = row['Date'].strip()
                    trans_type = row['Type'].strip().lower()
                    category = row['Category'].strip()
                    amount_str = row['Amount'].strip()
                    description = row['Description'].strip()

                    # Validate date
                    datetime.strptime(date, "%Y-%m-%d")

                    # Validate type
                    if trans_type not in ['expense', 'income']:
                        errors.append(f"Row {row_num}: Invalid type '{trans_type}'")
                        failed += 1
                        continue

                    # Validate category
                    valid_categories = EXPENSE_CATEGORIES if trans_type == 'expense' else INCOME_CATEGORIES
                    if category not in valid_categories:
                        errors.append(f"Row {row_num}: Invalid category '{category}'")
                        failed += 1
                        continue

                    # Validate amount
                    amount_float = float(amount_str)
                    if amount_float <= 0:
                        errors.append(f"Row {row_num}: Amount must be positive")
                        failed += 1
                        continue

                    amount_paisa = convert_rupees_to_paisa(amount_float)

                    # Check for duplicates
                    existing = read_transactions()
                    is_duplicate = any(
                        t['date'] == date and
                        t['type'] == trans_type and
                        t['category'] == category and
                        t['amount_paisa'] == amount_paisa and
                        t['description'] == description
                        for t in existing
                    )

                    if is_duplicate:
                        skipped += 1
                        continue

                    # Import transaction
                    if write_transaction(date, trans_type, category, amount_paisa, description):
                        imported += 1
                    else:
                        failed += 1
                        errors.append(f"Row {row_num}: Failed to write transaction")

                except ValueError as e:
                    failed += 1
                    errors.append(f"Row {row_num}: {str(e)}")
                except Exception as e:
                    failed += 1
                    errors.append(f"Row {row_num}: {str(e)}")

        return {
            'imported': imported,
            'skipped': skipped,
            'failed': failed,
            'errors': errors
        }

    except Exception as e:
        console.print(f"[red]Error reading CSV file: {e}[/red]")
        return None


# ============================================================================
# BACKUP & RESTORE FUNCTIONS
# ============================================================================

def create_backup() -> Optional[str]:
    """Create backup of all data files.

    Returns:
        Backup filename if successful, None otherwise
    """
    ensure_directories_exist()

    timestamp = generate_timestamp()
    backup_filename = BACKUPS_DIR / f"backup_{timestamp}.zip"

    # Count files
    trans_count = len(read_transactions())
    budget_count = len(read_budgets())
    goal_count = len(read_goals())

    # Create backup info
    backup_info = {
        "backup_date": datetime.now().isoformat(),
        "transaction_count": trans_count,
        "budget_count": budget_count,
        "goal_count": goal_count,
        "version": "1.0"
    }

    try:
        with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add data files
            for filename in ['transactions.txt', 'budgets.txt', 'goals.txt']:
                filepath = DATABASE_DIR / filename
                if filepath.exists():
                    zipf.write(filepath, filename)

            # Add backup info
            info_path = DATABASE_DIR / 'backup_info.json'
            with open(info_path, 'w') as f:
                json.dump(backup_info, f, indent=2)
            zipf.write(info_path, 'backup_info.json')
            info_path.unlink()  # Delete temp file

        return str(backup_filename)
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")
        return None


def list_backups() -> List[Dict]:
    """List all available backups.

    Returns:
        List of backup info dicts
    """
    ensure_directories_exist()

    backups = []
    for backup_file in sorted(BACKUPS_DIR.glob("backup_*.zip"), reverse=True):
        try:
            # Extract backup info
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                if 'backup_info.json' in zipf.namelist():
                    with zipf.open('backup_info.json') as f:
                        info = json.load(f)
                        info['filename'] = backup_file.name
                        info['size'] = backup_file.stat().st_size
                        backups.append(info)
        except:
            pass

    return backups


def restore_from_backup(backup_filename: str) -> bool:
    """Restore data from backup.

    Args:
        backup_filename: Name of backup file

    Returns:
        True if successful, False otherwise
    """
    backup_path = BACKUPS_DIR / backup_filename

    if not backup_path.exists():
        console.print(f"[red]Backup file not found: {backup_filename}[/red]")
        return False

    try:
        # Create backup of current data first
        console.print("[yellow]Creating backup of current data...[/yellow]")
        create_backup()

        # Extract backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(DATABASE_DIR)

        # Remove backup_info.json (not needed in database)
        info_file = DATABASE_DIR / 'backup_info.json'
        if info_file.exists():
            info_file.unlink()

        return True
    except Exception as e:
        console.print(f"[red]Error restoring backup: {e}[/red]")
        return False


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_all_data() -> Dict:
    """Validate all data files.

    Returns:
        Dict with validation results
    """
    results = {
        'transactions': {'valid': 0, 'invalid': 0, 'issues': []},
        'budgets': {'valid': 0, 'invalid': 0, 'issues': []},
        'goals': {'valid': 0, 'invalid': 0, 'issues': []}
    }

    # Validate transactions
    transactions = read_transactions()
    for i, trans in enumerate(transactions, 1):
        try:
            # Check required fields
            datetime.strptime(trans['date'], "%Y-%m-%d")
            if trans['type'] not in ['expense', 'income']:
                raise ValueError(f"Invalid type: {trans['type']}")
            if trans['amount_paisa'] <= 0:
                raise ValueError("Amount must be positive")
            results['transactions']['valid'] += 1
        except Exception as e:
            results['transactions']['invalid'] += 1
            results['transactions']['issues'].append(f"Transaction {i}: {str(e)}")

    # Validate budgets
    budgets = read_budgets()
    for i, budget in enumerate(budgets, 1):
        try:
            if budget['limit_paisa'] <= 0:
                raise ValueError("Budget limit must be positive")
            if budget['period'] not in ['monthly', 'weekly']:
                raise ValueError(f"Invalid period: {budget['period']}")
            results['budgets']['valid'] += 1
        except Exception as e:
            results['budgets']['invalid'] += 1
            results['budgets']['issues'].append(f"Budget {i}: {str(e)}")

    # Validate goals
    goals = read_goals()
    for i, goal in enumerate(goals, 1):
        try:
            if goal['target_paisa'] <= 0:
                raise ValueError("Target must be positive")
            datetime.strptime(goal['deadline'], "%Y-%m-%d")
            results['goals']['valid'] += 1
        except Exception as e:
            results['goals']['invalid'] += 1
            results['goals']['issues'].append(f"Goal {i}: {str(e)}")

    return results


def get_database_statistics() -> Dict:
    """Get database statistics.

    Returns:
        Dict with statistics
    """
    transactions = read_transactions()
    budgets = read_budgets()
    goals = read_goals()

    # Calculate stats
    total_income = sum(t['amount_paisa'] for t in transactions if t['type'] == 'income')
    total_expenses = sum(t['amount_paisa'] for t in transactions if t['type'] == 'expense')

    dates = [t['date'] for t in transactions] if transactions else []

    # File sizes
    trans_size = (DATABASE_DIR / 'transactions.txt').stat().st_size if (DATABASE_DIR / 'transactions.txt').exists() else 0
    budget_size = (DATABASE_DIR / 'budgets.txt').stat().st_size if (DATABASE_DIR / 'budgets.txt').exists() else 0
    goals_size = (DATABASE_DIR / 'goals.txt').stat().st_size if (DATABASE_DIR / 'goals.txt').exists() else 0

    # Last backup
    backups = list_backups()
    last_backup = backups[0]['backup_date'] if backups else "Never"

    return {
        'total_transactions': len(transactions),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'date_range': {
            'oldest': min(dates) if dates else "N/A",
            'newest': max(dates) if dates else "N/A"
        },
        'categories_used': len(set(t['category'] for t in transactions)),
        'active_budgets': len(budgets),
        'active_goals': len(goals),
        'file_sizes': {
            'transactions': trans_size,
            'budgets': budget_size,
            'goals': goals_size,
            'total': trans_size + budget_size + goals_size
        },
        'last_backup': last_backup
    }


# ============================================================================
# FEATURE IMPLEMENTATIONS
# ============================================================================

def export_transactions_ui() -> None:
    """Export transactions UI."""
    console.print("\n[bold cyan]Export Transactions[/bold cyan]\n")

    format_choice = questionary.select(
        "Select export format:",
        choices=["CSV", "JSON", "Back"]
    ).ask()

    if format_choice == "Back" or format_choice is None:
        return

    # Ask for filters
    use_filters = questionary.confirm("Apply filters?", default=False).ask()

    filters = None
    if use_filters:
        filters = {}

        # Type filter
        type_choice = questionary.select(
            "Filter by type:",
            choices=["All", "Expense Only", "Income Only"]
        ).ask()

        if type_choice == "Expense Only":
            filters['type'] = 'expense'
        elif type_choice == "Income Only":
            filters['type'] = 'income'

        # Date range filter
        use_date_range = questionary.confirm("Filter by date range?", default=False).ask()
        if use_date_range:
            start_date = questionary.text("Start date (YYYY-MM-DD):").ask()
            end_date = questionary.text("End date (YYYY-MM-DD):").ask()
            if start_date and end_date:
                filters['date_range'] = (start_date, end_date)

    # Export
    if format_choice == "CSV":
        filename = export_transactions_csv(filters)
    else:
        filename = export_transactions_json(filters)

    if filename:
        console.print(f"\n[green] Exported successfully to:[/green]")
        console.print(f"  {filename}\n")


def export_budgets_ui() -> None:
    """Export budgets UI."""
    console.print("\n[bold cyan]Export Budgets[/bold cyan]\n")

    format_choice = questionary.select(
        "Select export format:",
        choices=["CSV", "JSON", "Back"]
    ).ask()

    if format_choice == "Back" or format_choice is None:
        return

    if format_choice == "CSV":
        filename = export_budgets_csv()
    else:
        filename = export_budgets_json()

    if filename:
        console.print(f"\n[green] Exported successfully to:[/green]")
        console.print(f"  {filename}\n")


def export_monthly_report_ui() -> None:
    """Export monthly report UI."""
    console.print("\n[bold cyan]Export Monthly Report[/bold cyan]\n")

    month_choice = questionary.select(
        "Select month:",
        choices=["Current Month", "Specify Month"]
    ).ask()

    if month_choice is None:
        return

    month = None
    if month_choice == "Specify Month":
        month_str = questionary.text("Enter month (YYYY-MM):").ask()
        if month_str:
            month = month_str

    filename = export_monthly_report(month)

    if filename:
        console.print(f"\n[green] Report exported successfully to:[/green]")
        console.print(f"  {filename}\n")


def import_transactions_ui() -> None:
    """Import transactions UI."""
    console.print("\n[bold cyan]Import Transactions[/bold cyan]\n")

    filename = questionary.text(
        "Enter CSV file path:",
        validate=lambda text: len(text) > 0 or "Path cannot be empty"
    ).ask()

    if filename is None:
        return

    console.print("\n[yellow]Importing...[/yellow]\n")

    result = import_transactions_csv(filename)

    if result:
        console.print("[bold cyan]Import Complete![/bold cyan]\n")
        console.print(f"[green] Successfully imported: {result['imported']} transactions[/green]")
        if result['skipped'] > 0:
            console.print(f"[yellow]   Skipped (duplicates): {result['skipped']} transactions[/yellow]")
        if result['failed'] > 0:
            console.print(f"[red] Failed (invalid): {result['failed']} transactions[/red]")
            if result['errors']:
                console.print("\n[bold]Errors:[/bold]")
                for error in result['errors'][:10]:  # Show first 10 errors
                    console.print(f"  {error}")
                if len(result['errors']) > 10:
                    console.print(f"  ... and {len(result['errors']) - 10} more errors")
        console.print()


def backup_restore_menu() -> None:
    """Backup and restore submenu."""
    while True:
        console.print()
        choice = questionary.select(
            "Backup & Restore",
            choices=[
                "Create Backup",
                "Restore from Backup",
                "View Backups",
                "Back"
            ]
        ).ask()

        if choice is None or choice == "Back":
            break

        if choice == "Create Backup":
            console.print("\n[yellow]Creating backup...[/yellow]\n")
            filename = create_backup()
            if filename:
                console.print(f"[green] Backup created:[/green] {filename}\n")

        elif choice == "Restore from Backup":
            backups = list_backups()
            if not backups:
                console.print("[yellow]No backups available[/yellow]")
                continue

            # Show backups
            backup_choices = [
                f"{b['filename']} ({b['backup_date'][:10]} - {b['transaction_count']} transactions)"
                for b in backups
            ]
            backup_choices.append("Cancel")

            selected = questionary.select(
                "Select backup to restore:",
                choices=backup_choices
            ).ask()

            if selected and selected != "Cancel":
                backup_file = selected.split()[0]
                confirm = questionary.confirm(
                    "This will overwrite current data. Continue?",
                    default=False
                ).ask()

                if confirm:
                    if restore_from_backup(backup_file):
                        console.print(f"\n[green] Restored from backup successfully[/green]\n")
                    else:
                        console.print(f"\n[red] Restore failed[/red]\n")

        elif choice == "View Backups":
            backups = list_backups()
            if not backups:
                console.print("[yellow]No backups available[/yellow]")
                continue

            table = Table(title="Available Backups", show_header=True, header_style="bold magenta", box=box.ROUNDED)
            table.add_column("Filename", style="cyan")
            table.add_column("Date", style="white")
            table.add_column("Transactions", justify="right")
            table.add_column("Budgets", justify="right")
            table.add_column("Goals", justify="right")
            table.add_column("Size", justify="right")

            for backup in backups:
                size_kb = backup['size'] / 1024
                table.add_row(
                    backup['filename'],
                    backup['backup_date'][:10],
                    str(backup['transaction_count']),
                    str(backup['budget_count']),
                    str(backup['goal_count']),
                    f"{size_kb:.1f} KB"
                )

            console.print()
            console.print(table)


def data_validation_ui() -> None:
    """Data validation UI."""
    console.print("\n[bold cyan]Data Validation[/bold cyan]\n")
    console.print("[yellow]Running validation checks...[/yellow]\n")

    results = validate_all_data()

    # Display results
    table = Table(title="Validation Results", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Data Type", style="cyan")
    table.add_column("Valid", justify="right", style="green")
    table.add_column("Invalid", justify="right", style="red")
    table.add_column("Status")

    for data_type, result in results.items():
        status = " OK" if result['invalid'] == 0 else " Issues Found"
        status_color = "green" if result['invalid'] == 0 else "red"
        table.add_row(
            data_type.capitalize(),
            str(result['valid']),
            str(result['invalid']),
            f"[{status_color}]{status}[/{status_color}]"
        )

    console.print(table)

    # Show issues if any
    has_issues = any(r['invalid'] > 0 for r in results.values())
    if has_issues:
        console.print("\n[bold red]Issues Found:[/bold red]\n")
        for data_type, result in results.items():
            if result['issues']:
                console.print(f"[bold]{data_type.capitalize()}:[/bold]")
                for issue in result['issues'][:5]:
                    console.print(f"  • {issue}")
                if len(result['issues']) > 5:
                    console.print(f"  ... and {len(result['issues']) - 5} more issues")
                console.print()
    else:
        console.print("\n[green] All data is valid![/green]\n")


def database_statistics_ui() -> None:
    """Database statistics UI."""
    console.print("\n[bold cyan]Database Statistics[/bold cyan]\n")

    stats = get_database_statistics()

    content = f"""[bold yellow]Transaction Statistics:[/bold yellow]
Total Transactions:  {stats['total_transactions']}
Date Range:          {stats['date_range']['oldest']} to {stats['date_range']['newest']}
Total Income:        {format_amount(stats['total_income'])}
Total Expenses:      {format_amount(stats['total_expenses'])}
Categories Used:     {stats['categories_used']}

[bold yellow]Database Info:[/bold yellow]
Active Budgets:      {stats['active_budgets']}
Active Goals:        {stats['active_goals']}
Total Size:          {stats['file_sizes']['total'] / 1024:.2f} KB

[bold yellow]Backup Info:[/bold yellow]
Last Backup:         {stats['last_backup']}"""

    panel = Panel(content, title="Database Overview", border_style="blue", box=box.ROUNDED)
    console.print(panel)
    console.print()


# ============================================================================
# EXPORT MENU
# ============================================================================

def export_menu() -> None:
    """Display and handle export menu."""
    while True:
        console.print()
        choice = questionary.select(
            "Data Management & Export",
            choices=[
                "Export Transactions",
                "Export Budgets",
                "Export Monthly Report",
                "Import Transactions",
                "Backup & Restore",
                "Data Validation",
                "Database Statistics",
                "Back to Main Menu"
            ]
        ).ask()

        if choice is None or choice == "Back to Main Menu":
            break

        if choice == "Export Transactions":
            export_transactions_ui()
        elif choice == "Export Budgets":
            export_budgets_ui()
        elif choice == "Export Monthly Report":
            export_monthly_report_ui()
        elif choice == "Import Transactions":
            import_transactions_ui()
        elif choice == "Backup & Restore":
            backup_restore_menu()
        elif choice == "Data Validation":
            data_validation_ui()
        elif choice == "Database Statistics":
            database_statistics_ui()
