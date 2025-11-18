"""Personal Finance Tracker CLI

Professional CLI application for tracking expenses, income, budgets,
and generating financial insights.
"""

import sys
from pathlib import Path
import questionary
from rich.console import Console
from rich.panel import Panel
from rich import box

# Add features directory to path
sys.path.append(str(Path(__file__).parent))

from features.transactions.transactions import transaction_menu
from features.budgets.budgets import budget_menu
from features.analytics.analytics import analytics_menu

console = Console()


def show_welcome() -> None:
    """Display welcome banner."""
    welcome_text = """
[bold cyan]Personal Finance Tracker[/bold cyan]

Track your expenses, income, and budgets with ease.
Manage your financial health from the command line.
    """
    panel = Panel(
        welcome_text,
        box=box.DOUBLE,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def show_coming_soon(feature: str) -> None:
    """Display coming soon message for features under development.

    Args:
        feature: Name of the feature
    """
    console.print(f"\n[yellow]{feature} feature is coming soon![/yellow]")
    console.print("[dim]This feature will be available in the next update.[/dim]\n")


def main_menu() -> None:
    """Display and handle main menu."""
    while True:
        console.print()
        choice = questionary.select(
            "Main Menu",
            choices=[
                "Transactions",
                "Budgets",
                "Analytics",
                "Export",
                "Exit"
            ],
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan'),
            ])
        ).ask()

        if choice is None or choice == "Exit":
            console.print("\n[cyan]Thank you for using Personal Finance Tracker![/cyan]")
            console.print("[dim]Your financial data has been saved.[/dim]\n")
            break

        if choice == "Transactions":
            transaction_menu()
        elif choice == "Budgets":
            budget_menu()
        elif choice == "Analytics":
            analytics_menu()
        elif choice == "Export":
            show_coming_soon("Export")


def main() -> None:
    """Main entry point for the application."""
    try:
        show_welcome()
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Application interrupted by user[/yellow]")
        console.print("[cyan]Goodbye![/cyan]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {e}[/red]")
        console.print("[dim]Please report this issue if it persists.[/dim]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
