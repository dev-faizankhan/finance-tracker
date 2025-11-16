# Transaction Management Feature

## Goal

Build core transaction tracking for expenses and income.

## Core Concepts

- Transaction: Any money movement (in or out)
- Debit: Money going out (expense)
- Credit: Money coming in (income)
- Categories: Group transactions for analysis

## Features to Implement

### 1. Add Expense

Flow:

1. Ask amount (validate positive number)
2. Ask category (Food, Transport, Shopping, Bills, Entertainment, Health, Other)
3. Ask description
4. Ask date (default: today, allow custom)
5. Convert amount to paisa
6. Save to transactions.txt

### 2. Add Income

Flow:

1. Ask amount (validate positive number)
2. Ask source (Salary, Freelance, Business, Investment, Gift, Other)
3. Ask description
4. Ask date (default: today, allow custom)
5. Convert amount to paisa
6. Save to transactions.txt

### 3. List Transactions

Display:

- Rich table with columns: Date, Type, Category, Description, Amount
- Color coding: Red (expenses), Green (income)
- Sort by date (newest first)
- Convert paisa to rupees for display

Filters:

- Last 7 days
- Last 30 days
- Only expenses
- Only income
- By category
- Date range

### 4. Balance Command

Display:

- Total Income (green)
- Total Expenses (red)
- Current Balance (green if positive, red if negative)
- Show for current month by default
- Optional: All time balance

### 5. Edit Transaction

Flow:

1. List all transactions with index numbers
2. Ask which transaction to edit
3. Show current values
4. Allow editing any field
5. Save changes

### 6. Delete Transaction

Flow:

1. List all transactions with index numbers
2. Ask which transaction to delete
3. Confirm deletion
4. Remove from file

### 7. Search Transactions

Search by:

- Description (partial match)
- Category
- Date range
- Amount range

## Money Handling

- Always store as integers in paisa
- Input: Accept rupees from user (e.g., 12.50)
- Convert: Multiply by 100 to get paisa (1250)
- Store: Save as integer (1250)
- Display: Divide by 100 to show rupees (12.50)

## File Format

transactions.txt uses pipe-delimited format:

```
date|type|category|amount_paisa|description
```

## Validation Rules

- Amount must be positive number
- Date must be valid YYYY-MM-DD format
- Category must be from predefined list
- Description cannot be empty
- Type must be "expense" or "income"

## Functions to Create

### File Operations

- ensure_database_exists(): Create database/ directory and files
- read_transactions() -> List[Dict]: Read all transactions
- write_transaction(date, type, category, amount_paisa, description): Append new transaction
- update_transaction(index, updated_data): Modify existing transaction
- delete_transaction(index): Remove transaction

### Input Functions

- get_amount() -> int: Get amount from user, convert to paisa
- get_category(transaction_type) -> str: Get category based on type
- get_description() -> str: Get transaction description
- get_date() -> str: Get date (default today)
- get_transaction_type() -> str: Get expense or income

### Display Functions

- display_transactions(transactions, filters=None): Show transactions table
- display_balance(transactions): Show income/expense/balance summary
- show_success(message): Display success message
- show_error(message): Display error message

### Calculation Functions

- calculate_total_income(transactions) -> int: Sum all income in paisa
- calculate_total_expenses(transactions) -> int: Sum all expenses in paisa
- calculate_balance(transactions) -> int: Income minus expenses
- get_category_total(transactions, category) -> int: Total for specific category

### Filter Functions

- filter_by_date_range(transactions, start_date, end_date) -> List[Dict]
- filter_by_type(transactions, type) -> List[Dict]
- filter_by_category(transactions, category) -> List[Dict]
- filter_last_n_days(transactions, n) -> List[Dict]
- search_description(transactions, keyword) -> List[Dict]

## UI Components

- Use Questionary select for category selection
- Use Questionary text for amount, description, date
- Use Rich Table for transaction listing
- Use Rich Panel for balance display
- Use Rich Console for colored output

## Error Handling

- Handle invalid amount input (non-numeric)
- Handle invalid date format
- Handle empty description
- Handle corrupted file lines
- Handle missing database directory
- Handle empty transaction list

## Menu Options

1. Add Expense
2. Add Income
3. View All Transactions
4. View Last 7 Days
5. View Last 30 Days
6. View Balance
7. Search Transactions
8. Edit Transaction
9. Delete Transaction
10. Back to Main Menu

## Success Criteria

- Can add expenses with validation
- Can add income with validation
- Can list all transactions
- Can filter transactions
- Can see current balance
- Money calculations are accurate (no float errors)
- Colored output working
- Can edit transactions
- Can delete transactions
- Can search transactions

## Testing Checklist

- Add expense with decimal amount (e.g., 12.50)
- Add income with large amount
- List empty transactions
- List single transaction
- Filter with no results
- Calculate balance with no transactions
- Edit transaction and verify changes
- Delete transaction and verify removal
- Search with partial match
- Handle invalid date input
- Handle negative amount input
- Handle empty description
