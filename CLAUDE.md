# Personal Finance Tracker CLI

## Project Overview

Professional CLI application for tracking expenses, income, budgets, and generating financial insights.

## Tech Stack

- Python 3.11+
- Questionary (interactive menus)
- Rich (tables, panels, formatting)
- UV (package manager)
- Plain text file storage

## Project Structure

```
finance-tracker/
├── claude.md
├── main.py
├── database/
│   ├── transactions.txt
│   └── budgets.txt
└── features/
    ├── transactions/
    │   ├── CLAUDE.md
    │   └── transactions.py
    ├── budgets/
    │   ├── CLAUDE.md
    │   └── budgets.py
    ├── analytics/
    │   ├── CLAUDE.md
    │   └── analytics.py
    └── export/
        ├── CLAUDE.md
        └── export.py
```

## Critical Rules

### Money Storage

Store all monetary values as integers in paisa (smallest unit).

- Store: 1250 (represents Rs 12.50)
- Display: amount / 100

### Data File Formats

**transactions.txt**

```
date|type|category|amount_paisa|description
2024-11-16|expense|food|1250|Lunch at restaurant
2024-11-16|income|salary|500000|Monthly salary
```

**budgets.txt**

```
category|limit_paisa|period
food|2000000|monthly
transport|1000000|monthly
```

## Categories

**Expense Categories**: Food, Transport, Shopping, Bills, Entertainment, Health, Other

**Income Categories**: Salary, Freelance, Business, Investment, Gift, Other

## Core Features

### Transaction Management

- Add transaction
- View transactions with filters
- Edit transaction
- Delete transaction
- Search transactions

### Budget Management

- Set budgets per category
- View budget vs actual
- Budget alerts
- Budget recommendations

### Analytics

- Monthly spending summary
- Category breakdowns
- Income vs expense comparison
- Spending trends
- Financial health score (0-100)

### Reports

- Monthly reports
- Spending patterns
- Saving suggestions
- Income analysis

### Export

- CSV export
- JSON export
- Date range filters

## Main Menu Structure

1. Transactions (Add, View, Edit, Delete, Search)
2. Budgets (Set, View, Analysis, Alerts)
3. Analytics (Summary, Breakdown, Trends, Health Score)
4. Export (CSV, JSON)
5. Settings
6. Exit

## Code Standards

- Use type hints
- Validate all inputs
- Handle empty files
- Use UTF-8 encoding
- Clear error messages
- Use Questionary for inputs
- Use Rich for outputs

## Development Phases

1. Foundation: Project setup, file handlers, basic CRUD
2. Core Features: Budget management, analytics
3. Insights: Health scoring, pattern detection, reports
4. Export: CSV/JSON functionality
5. Dashboard: Optional Streamlit interface

## File Operations

- Create database/ directory if missing
- Create .txt files if missing
- Always use UTF-8 encoding
- Parse pipe-delimited format
- Validate data on read

## UI Patterns

- Questionary select for menus
- Rich tables for data display
- Rich panels for messages
- Progress bars for operations
- Color coding: green (income), red (expense)

## Validation Requirements

- Validate amount is positive number
- Validate date format (YYYY-MM-DD)
- Validate category against predefined lists
- Validate file format on read
- Handle corrupted data gracefully

## Helper Functions Needed

- read_transactions() -> List[Dict]
- write_transaction()
- read_budgets() -> List[Dict]
- write_budget()
- calculate_total_expenses() -> int
- calculate_total_income() -> int
- format_amount(paisa: int) -> str
- get_category_spending(category: str) -> int
- calculate_financial_health() -> int
