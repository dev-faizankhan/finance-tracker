# Financial Analytics Feature

## Goal

Analyze spending patterns and provide financial insights like real fintech apps.

## Core Concepts

- Spending Pattern: Money distribution across categories
- Burn Rate: Average daily spending
- Savings Rate: Percentage of income saved
- Financial Health Score: Overall financial wellness metric (0-100)
- Category Trends: Spending increases/decreases over time

## Features to Implement

### 1. Spending Analysis

Display:

- Total spending for current month
- Breakdown by category (amount and percentage)
- Top 3 spending categories
- Average daily expense (burn rate)
- Comparison with last month (percentage change)
- Spending trends (increasing/decreasing)
- ASCII bar chart for category distribution

### 2. Income Analysis

Display:

- Total income for current month
- Income by source (Salary, Freelance, etc.)
- Average income per source
- Comparison with last month
- Income stability score (regular vs irregular)
- Income trend over last 3 months

### 3. Savings Analysis

Display:

- Monthly savings (income - expenses)
- Savings rate percentage
- Savings trend (last 3 months)
- Average monthly savings
- Projected annual savings
- Comparison with recommended savings rate (20%)

### 4. Financial Health Score

Calculate score out of 100 based on:

- Savings Rate (30 points): >20% = full points
- Budget Adherence (25 points): Staying within budgets
- Income vs Expenses (25 points): Positive balance
- Spending Consistency (20 points): Not overspending categories

Display:

- Overall score with color coding
- Score interpretation (Excellent/Good/Fair/Poor)
- Breakdown by factor
- Recommendations to improve score

Score Interpretation:

- 80-100: Excellent (Green)
- 60-79: Good (Yellow)
- 40-59: Fair (Orange)
- 0-39: Poor (Red)

### 5. Category Trends

Analyze:

- Which categories spending increased
- Which categories spending decreased
- Percentage change per category
- Month-over-month comparison
- Identify unusual spending spikes

### 6. Monthly Report

Generate comprehensive report with:

- Report period (month/year)
- Income summary
- Expense summary
- Category breakdown
- Budget performance
- Savings achieved
- Top 5 transactions (highest expenses)
- Financial health score
- Trends and patterns
- Recommendations for next month
- Projected spending for next month

### 7. Insights & Recommendations

Provide actionable insights:

- "You spent 40% more on Food this month"
- "Great job staying under budget in 4/6 categories"
- "Consider reducing Shopping expenses by 15%"
- "Your savings rate is below recommended 20%"
- "Income increased by 10% compared to last month"

## Calculation Functions

### Spending Calculations

- calculate_total_spending(month) -> int: Total expenses for month in paisa
- calculate_category_spending(category, month) -> int: Spending per category
- calculate_category_percentage(category, total) -> float: Category as % of total
- calculate_average_daily_spending(month) -> int: Total / days in month
- calculate_burn_rate() -> int: Average daily spending
- get_top_spending_categories(n=3) -> List[Tuple]: Top N categories by amount

### Income Calculations

- calculate_total_income(month) -> int: Total income for month
- calculate_income_by_source(source, month) -> int: Income per source
- calculate_average_income() -> int: Average monthly income
- calculate_income_stability() -> float: Variance in monthly income

### Savings Calculations

- calculate_monthly_savings(month) -> int: Income minus expenses
- calculate_savings_rate(month) -> float: (savings/income) \* 100
- calculate_average_savings(months=3) -> int: Average savings over period
- calculate_projected_annual_savings() -> int: Current rate \* 12

### Trend Calculations

- calculate_month_over_month_change(category) -> float: % change
- get_spending_trend(category, months=3) -> str: "increasing"/"decreasing"/"stable"
- compare_with_last_month() -> Dict: All comparisons
- detect_spending_spikes() -> List[Dict]: Unusual transactions

### Health Score Calculations

- calculate_savings_score() -> int: Max 30 points
- calculate_budget_adherence_score() -> int: Max 25 points
- calculate_balance_score() -> int: Max 25 points
- calculate_consistency_score() -> int: Max 20 points
- calculate_overall_health_score() -> int: Sum of all scores (0-100)
- get_health_interpretation(score) -> str: Excellent/Good/Fair/Poor

## Display Functions

### ASCII Visualizations

- display_category_bar_chart(categories): Show horizontal bars
- display_spending_distribution(): ASCII pie chart representation
- display_trend_indicator(change): Up/down arrows with percentage

Example Bar Chart:

```
Spending by Category:
Food         ████████████████ 40% (Rs 8,000)
Transport    ████████ 20% (Rs 4,000)
Shopping     ██████████ 25% (Rs 5,000)
Bills        █████ 10% (Rs 2,000)
Other        ██ 5% (Rs 1,000)
```

### Rich Tables

- display_spending_analysis(): Table with categories and amounts
- display_income_breakdown(): Table with income sources
- display_monthly_comparison(): Side-by-side current vs last month
- display_health_score_breakdown(): Score components

### Rich Panels

- display_summary_panel(): Quick overview
- display_insights_panel(): Key insights and recommendations
- display_score_panel(): Health score with interpretation

## Report Generation

### Monthly Report Structure

```
╔══════════════════════════════════════════════════════╗
║          Monthly Financial Report - November 2024     ║
╠══════════════════════════════════════════════════════╣
║ INCOME SUMMARY                                        ║
║ Total Income:        Rs 50,000                        ║
║ Salary:              Rs 45,000                        ║
║ Freelance:           Rs 5,000                         ║
║                                                       ║
║ EXPENSE SUMMARY                                       ║
║ Total Expenses:      Rs 35,000                        ║
║ Average Daily:       Rs 1,167                         ║
║                                                       ║
║ TOP SPENDING CATEGORIES                               ║
║ 1. Food              Rs 12,000 (34%)                  ║
║ 2. Transport         Rs 8,000  (23%)                  ║
║ 3. Shopping          Rs 7,000  (20%)                  ║
║                                                       ║
║ SAVINGS                                               ║
║ Amount Saved:        Rs 15,000                        ║
║ Savings Rate:        30%                              ║
║ Status:              Above Target ✅                   ║
║                                                       ║
║ BUDGET PERFORMANCE                                    ║
║ Categories On Track: 4/6                              ║
║ Over Budget:         2 categories                     ║
║                                                       ║
║ FINANCIAL HEALTH SCORE                                ║
║ Score:               78/100                           ║
║ Rating:              Good ⭐⭐⭐                         ║
║                                                       ║
║ KEY INSIGHTS                                          ║
║ • Spending decreased by 12% vs last month            ║
║ • Income increased by 5% vs last month               ║
║ • Food spending up 15% - consider meal planning      ║
║                                                       ║
║ RECOMMENDATIONS                                       ║
║ • Maintain current savings rate                       ║
║ • Reduce food expenses by Rs 2,000                   ║
║ • Consider increasing transport budget                ║
╚══════════════════════════════════════════════════════╝
```

## Data Aggregation

### Time Periods

- get_current_month_data() -> Dict: All data for current month
- get_last_month_data() -> Dict: Previous month data
- get_last_n_months_data(n) -> List[Dict]: Historical data
- get_year_to_date_data() -> Dict: All data for current year

### Filtering

- filter_transactions_by_month(month) -> List[Dict]
- filter_transactions_by_category(category) -> List[Dict]
- filter_transactions_by_type(type) -> List[Dict]
- filter_transactions_by_date_range(start, end) -> List[Dict]

## Insight Generation

### Pattern Detection

- detect_high_spending_day() -> str: Day with highest spending
- detect_low_income_months() -> List[str]: Months with below-average income
- detect_budget_violations() -> List[str]: Consistently over-budget categories
- detect_saving_opportunities() -> List[str]: Areas to cut spending

### Recommendations

Based on analysis, generate recommendations:

- Spending too high in category X
- Income below last month average
- Savings rate below 20% target
- Budget needs adjustment for category Y
- Good financial habits to continue

## Menu Options

1. Spending Analysis
2. Income Analysis
3. Savings Analysis
4. Financial Health Score
5. Category Trends
6. Monthly Report
7. Compare Months
8. View Insights
9. Back to Main Menu

## Success Criteria

- Shows spending breakdown by category with percentages
- Calculates and displays burn rate
- Calculates and displays savings rate
- Generates financial health score (0-100)
- Compares current month vs last month
- Creates comprehensive monthly report
- Provides actionable recommendations
- Displays ASCII visualizations
- Shows trends with up/down indicators
- Color codes based on performance

## Testing Checklist

- Test with no transactions
- Test with only expenses (no income)
- Test with only income (no expenses)
- Test with single transaction
- Test with multiple months of data
- Test savings rate calculation (income > expenses)
- Test negative savings (expenses > income)
- Test health score at different levels
- Test month-over-month comparison with no previous month
- Test category trends with increasing spending
- Test category trends with decreasing spending
- Test report generation with complete data
- Test with missing budget data
- Verify all percentages sum to 100%
- Verify ASCII charts display correctly

## Edge Cases to Handle

- Division by zero (no income, no expenses)
- First month (no previous data for comparison)
- No budgets set (skip budget adherence score)
- Single category spending (100%)
- Zero spending in category
- Negative savings (expenses > income)
- Very large numbers (formatting)
- Very small percentages (<1%)
