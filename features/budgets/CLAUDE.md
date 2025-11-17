# Budget Management Feature

## Goal

Set monthly budgets for categories and track spending against them.

## Core Concepts

- Budget: Planned spending limit for a category
- Budget Utilization: Percentage of budget used
- Budget Overspending: Expenses exceed budget
- Budget Tracking: Monitor spending vs planned amount

## Features to Implement

### 1. Set Budget

Flow:

1. Ask category (Food, Transport, Shopping, Bills, Entertainment, Health)
2. Ask monthly budget amount
3. Ask period (monthly or weekly)
4. Convert amount to paisa
5. Save to budgets.txt
6. Show confirmation

Validation:

- Amount must be positive
- Category must be valid
- Check if budget already exists for category
- If exists, ask to update or cancel

### 2. View Budgets

Display Rich table with columns:

- Category
- Budget Amount (Rs)
- Spent (current month in Rs)
- Remaining (Rs)
- Utilization (%)
- Status
- Progress Bar

Status Color Coding:

- Green: Under 70% used (OK)
- Yellow: 70-100% used (Warning)
- Red: Over 100% used (Over Budget)

Sort by utilization percentage (highest first).

### 3. Budget Summary

Display:

- Total Monthly Budget
- Total Spent (current month)
- Total Remaining
- Overall Utilization %
- Number of categories over budget
- Number of categories at warning level
- Average utilization across all categories

### 4. Budget Analysis

Show:

- Categories over budget (highlighted in red)
- Categories at warning level (highlighted in yellow)
- Categories with most room (highlighted in green)
- Spending trends compared to budget
- Recommendations for adjustments

### 5. Budget Alerts

Check and display:

- Which categories exceeded budget
- Which categories are at 80%+ utilization
- Which categories are at 90%+ utilization
- Suggest reducing spending in over-budget categories

### 6. Edit Budget

Flow:

1. List all budgets
2. Ask which category to edit
3. Show current budget
4. Ask for new amount
5. Update budgets.txt
6. Show confirmation

### 7. Delete Budget

Flow:

1. List all budgets
2. Ask which category to delete
3. Confirm deletion
4. Remove from budgets.txt

### 8. Budget Recommendations

Analyze spending patterns and suggest:

- Budget increases for frequently overspent categories
- Budget decreases for under-utilized categories
- Ideal budget allocation based on last 3 months
- Savings opportunities

## File Format

budgets.txt uses pipe-delimited format:

```
category|limit_paisa|period
```

## Calculation Functions

### Core Calculations

- get_budget_for_category(category) -> int: Get budget limit in paisa
- get_current_month_spending(category) -> int: Total spent this month in paisa
- calculate_remaining(budget, spent) -> int: Budget minus spent
- calculate_utilization(spent, budget) -> float: (spent/budget) \* 100
- get_budget_status(utilization) -> str: "OK", "Warning", or "Over"

### Analysis Functions

- get_overbudget_categories() -> List[str]: Categories exceeding budget
- get_warning_categories() -> List[str]: Categories at 70-100%
- get_healthy_categories() -> List[str]: Categories under 70%
- calculate_total_budget() -> int: Sum of all budgets
- calculate_total_spent() -> int: Sum of all current month expenses
- calculate_overall_utilization() -> float: Total spent / total budget

### Time Functions

- get_current_month() -> str: Return YYYY-MM format
- filter_current_month_transactions() -> List[Dict]: Get this month's transactions
- get_month_from_date(date_str) -> str: Extract month from date
- is_same_month(date1, date2) -> bool: Check if same month

## UI Components

### Progress Bar Display

Use Rich Progress for utilization:

- Green bar: 0-70%
- Yellow bar: 70-100%
- Red bar: 100%+

### Table Layout

```
Category    | Budget    | Spent     | Remaining | Used  | Status
------------|-----------|-----------|-----------|-------|--------
Food        | Rs 20,000 | Rs 15,000 | Rs 5,000  | 75%   | ⚠️ Warning
Transport   | Rs 10,000 | Rs 12,000 | -Rs 2,000 | 120%  | ❌ Over
Shopping    | Rs 15,000 | Rs 8,000  | Rs 7,000  | 53%   | ✅ OK
```

### Summary Panel

Use Rich Panel to display:

```
╔══════════════════════════════════════╗
║       Budget Summary - Nov 2024      ║
╠══════════════════════════════════════╣
║ Total Budget:    Rs 100,000          ║
║ Total Spent:     Rs 85,000           ║
║ Remaining:       Rs 15,000           ║
║ Utilization:     85%                 ║
║                                      ║
║ ❌ Over Budget:   2 categories       ║
║ ⚠️ Warning:       3 categories       ║
║ ✅ Healthy:       5 categories       ║
╚══════════════════════════════════════╝
```

## Validation Rules

- Budget amount must be positive
- Category must exist in predefined list
- Cannot set duplicate budgets for same category/period
- Period must be "monthly" or "weekly"

## File Operations

- ensure_budgets_file_exists(): Create budgets.txt if missing
- read_budgets() -> List[Dict]: Read all budgets
- write_budget(category, limit_paisa, period): Add new budget
- update_budget(category, new_limit_paisa): Update existing budget
- delete_budget(category): Remove budget
- budget_exists(category) -> bool: Check if budget set

## Integration with Transactions

- Must read transactions.txt to calculate spent amounts
- Filter transactions by current month
- Filter by expense type only (ignore income)
- Match transaction category with budget category
- Sum amounts in paisa

## Menu Options

1. Set New Budget
2. View All Budgets
3. Budget Summary
4. Budget Analysis
5. Budget Alerts
6. Edit Budget
7. Delete Budget
8. Budget Recommendations
9. Back to Main Menu

## Success Criteria

- Can set monthly budgets per category
- Can view budget vs actual spending
- Shows utilization percentage with progress bars
- Highlights over-budget categories in red
- Shows warning categories in yellow
- Budget calculations accurate for current month
- Budget resets automatically each month
- Can edit and delete budgets
- Recommendations based on spending patterns

## Testing Checklist

- Set budget for new category
- Try to set duplicate budget (should prompt to update)
- View budgets with no spending
- View budgets with partial spending
- View budgets with overspending
- Calculate utilization for different percentages
- Test with no budgets set
- Test with no transactions for budgeted category
- Edit budget amount
- Delete budget
- View summary with mixed status categories
- Test month rollover (spending from last month should not count)
- Test with transactions from multiple months

## Edge Cases to Handle

- No budgets set yet
- No transactions for current month
- Category has budget but no transactions
- Category has transactions but no budget
- Budget amount is zero
- All categories over budget
- All categories under budget
- Month transition (Jan to Feb)
