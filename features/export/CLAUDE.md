# Data Management & Export Feature

## Goal

Professional data export, import, and backup features for data portability and protection.

## Core Concepts

- Data Export: Download financial data for external use
- Data Portability: Moving data between systems
- Audit Trail: Complete transaction history
- Data Backup: Protecting financial information
- Data Integrity: Ensuring data accuracy and consistency

## Features to Implement

### 1. Export Transactions

Export all or filtered transactions to multiple formats.

**CSV Export:**

- Header row with column names
- Comma-separated values
- Amounts in rupees (not paisa)
- Date in readable format
- Compatible with Excel/Google Sheets

CSV Format:

```csv
Date,Type,Category,Amount,Description
2024-11-16,expense,food,12.50,Lunch at restaurant
2024-11-16,income,salary,50000.00,Monthly salary
```

**JSON Export:**

- Structured data format
- Include all fields
- Amounts in paisa (for accuracy)
- Machine-readable format

JSON Format:

```json
{
  "transactions": [
    {
      "date": "2024-11-16",
      "type": "expense",
      "category": "food",
      "amount_paisa": 1250,
      "amount_rupees": 12.5,
      "description": "Lunch at restaurant"
    }
  ],
  "exported_at": "2024-11-18T10:30:00",
  "total_transactions": 1
}
```

**Export Options:**

- All transactions
- Date range filter (from date to date)
- Category filter
- Type filter (expense/income)
- Custom month/year

### 2. Export Budgets

Export budget allocations and usage.

**CSV Format:**

```csv
Category,Budget,Period,Spent,Remaining,Utilization
food,20000.00,monthly,15000.00,5000.00,75%
transport,10000.00,monthly,12000.00,-2000.00,120%
```

**JSON Format:**

```json
{
  "budgets": [
    {
      "category": "food",
      "budget_paisa": 2000000,
      "budget_rupees": 20000.0,
      "period": "monthly",
      "spent_paisa": 1500000,
      "spent_rupees": 15000.0,
      "remaining_paisa": 500000,
      "remaining_rupees": 5000.0,
      "utilization_percent": 75.0
    }
  ],
  "exported_at": "2024-11-18T10:30:00",
  "total_budgets": 2
}
```

### 3. Export Monthly Report

Comprehensive JSON export with complete financial overview.

**Report Structure:**

```json
{
  "report_period": {
    "month": "November",
    "year": 2024,
    "date_range": {
      "start": "2024-11-01",
      "end": "2024-11-30"
    }
  },
  "summary": {
    "total_income_paisa": 5000000,
    "total_income_rupees": 50000.0,
    "total_expenses_paisa": 3500000,
    "total_expenses_rupees": 35000.0,
    "net_savings_paisa": 1500000,
    "net_savings_rupees": 15000.0,
    "savings_rate_percent": 30.0,
    "transaction_count": 45
  },
  "income_breakdown": [
    {
      "source": "salary",
      "amount_paisa": 4500000,
      "amount_rupees": 45000.0,
      "percentage": 90.0
    }
  ],
  "expense_breakdown": [
    {
      "category": "food",
      "amount_paisa": 1200000,
      "amount_rupees": 12000.0,
      "percentage": 34.3,
      "budget_paisa": 2000000,
      "utilization_percent": 60.0
    }
  ],
  "budget_performance": {
    "total_budget_paisa": 10000000,
    "total_spent_paisa": 3500000,
    "overall_utilization_percent": 35.0,
    "categories_on_track": 4,
    "categories_over_budget": 2
  },
  "financial_health": {
    "score": 78,
    "rating": "Good",
    "breakdown": {
      "savings_score": 25,
      "budget_adherence_score": 18,
      "balance_score": 20,
      "consistency_score": 15
    }
  },
  "top_transactions": [
    {
      "date": "2024-11-05",
      "type": "expense",
      "category": "shopping",
      "amount_rupees": 5000.0,
      "description": "New laptop"
    }
  ],
  "insights": [
    "Spending decreased by 12% vs last month",
    "Income increased by 5% vs last month",
    "Food spending up 15% - consider meal planning"
  ],
  "recommendations": [
    "Maintain current savings rate",
    "Reduce food expenses by Rs 2,000",
    "Consider increasing transport budget"
  ],
  "generated_at": "2024-11-18T10:30:00"
}
```

### 4. Import Transactions

Import transactions from CSV with validation.

**Import Flow:**

1. Select CSV file to import
2. Validate file format (check headers)
3. Parse each row
4. Validate data (date, amount, category)
5. Check for duplicates
6. Show preview of transactions to import
7. Confirm import
8. Import transactions
9. Show import summary

**Validation Rules:**

- Date must be valid YYYY-MM-DD format
- Type must be "expense" or "income"
- Category must exist in predefined lists
- Amount must be positive number
- Description cannot be empty
- Check for exact duplicates (same date, amount, description)

**Expected CSV Format:**

```csv
Date,Type,Category,Amount,Description
2024-11-16,expense,food,12.50,Lunch
```

**Import Summary:**

```
Import Complete!
✅ Successfully imported: 45 transactions
⚠️  Skipped (duplicates): 3 transactions
❌ Failed (invalid): 2 transactions

Details:
- Income transactions: 5
- Expense transactions: 40
- Date range: 2024-11-01 to 2024-11-15
```

### 5. Backup System

Create complete backup of all financial data.

**Backup Features:**

- Timestamped backup files
- Include all data files (transactions.txt, budgets.txt, goals.txt)
- Compress into ZIP archive
- Store in backups/ directory
- Auto-cleanup (keep only last 10 backups)

**Backup Filename Format:**

```
backup_YYYYMMDD_HHMMSS.zip
Example: backup_20241118_103045.zip
```

**Backup Contents:**

```
backup_20241118_103045.zip
├── transactions.txt
├── budgets.txt
├── goals.txt
└── backup_info.json
```

**backup_info.json:**

```json
{
  "backup_date": "2024-11-18T10:30:45",
  "transaction_count": 150,
  "budget_count": 6,
  "goal_count": 2,
  "version": "1.0"
}
```

### 6. Restore System

Restore data from backup archive.

**Restore Flow:**

1. List available backups (sorted by date)
2. Show backup details (date, transaction count)
3. Confirm restore (warn about overwriting current data)
4. Create backup of current data before restore
5. Extract and restore files
6. Validate restored data
7. Show restore summary

**Safety Features:**

- Always backup current data before restore
- Validate backup file before extracting
- Verify data integrity after restore
- Show detailed restore report

### 7. Data Validation

Check and repair data integrity issues.

**Validation Checks:**

- File format validation (correct delimiters)
- Required fields present
- Data type validation (dates, numbers)
- Category validation (exists in predefined lists)
- Amount validation (positive, not zero)
- Duplicate detection
- Orphaned data (budgets without categories)
- Corrupt lines (incomplete data)

**Validation Report:**

```
Data Validation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Valid Transactions: 145
❌ Invalid Transactions: 5

Issues Found:
1. Line 23: Invalid date format "16-11-2024"
2. Line 45: Negative amount "-1250"
3. Line 67: Missing description
4. Line 89: Invalid category "fastfood"
5. Line 102: Corrupt data (incomplete fields)

Recommendations:
- Fix invalid dates (use YYYY-MM-DD format)
- Remove negative amounts or change type
- Add descriptions to transactions
- Use valid categories: Food, Transport, etc.
- Remove corrupt lines
```

**Auto-Fix Options:**

- Fix date formats automatically
- Convert negative amounts to positive
- Fill empty descriptions with "No description"
- Map similar categories (fastfood → food)
- Remove completely corrupt lines

### 8. Data Statistics

Show overview of all stored data.

**Display:**

- Total transactions
- Date range (oldest to newest)
- Total income (all time)
- Total expenses (all time)
- Number of categories used
- Number of active budgets
- Number of goals
- Database file sizes
- Last backup date

## File Operations

### Export Functions

- export_transactions_csv(filename, filters=None): Export to CSV
- export_transactions_json(filename, filters=None): Export to JSON
- export_budgets_csv(filename): Export budgets to CSV
- export_budgets_json(filename): Export budgets to JSON
- export_monthly_report(month, year, filename): Generate report JSON

### Import Functions

- import_transactions_csv(filename): Import from CSV
- validate_csv_format(filename) -> bool: Check file structure
- parse_csv_row(row) -> Dict: Parse single row
- check_duplicate_transaction(transaction) -> bool: Detect duplicates
- preview_import(filename) -> List[Dict]: Show what will be imported

### Backup Functions

- create_backup() -> str: Create timestamped backup, return filename
- list_backups() -> List[Dict]: Get all available backups with details
- restore_from_backup(backup_filename): Restore data
- cleanup_old_backups(keep=10): Remove old backups
- validate_backup_file(filename) -> bool: Check backup integrity

### Validation Functions

- validate_all_data() -> Dict: Run all validation checks
- validate_transactions() -> List[Dict]: Check transaction data
- validate_budgets() -> List[Dict]: Check budget data
- validate_goals() -> List[Dict]: Check goal data
- fix_data_issues(issues, auto_fix=False): Repair data

### Utility Functions

- get_database_statistics() -> Dict: Get data overview
- compress_to_zip(files, output_filename): Create ZIP archive
- extract_from_zip(zip_filename, output_dir): Extract ZIP
- convert_paisa_to_rupees_for_export(amount) -> float: Format for export
- convert_rupees_to_paisa_for_import(amount) -> int: Parse import

## Export Destinations

### Default Export Path

- Create exports/ directory
- Save all exports there
- Format: exports/transactions_20241118_103045.csv

### User Choice

- Allow custom export path
- Validate path exists
- Create directory if needed

## Menu Options

1. Export Transactions
   - Export to CSV
   - Export to JSON
   - Export with Filters
2. Export Budgets
   - Export to CSV
   - Export to JSON
3. Export Monthly Report
4. Import Transactions
   - Import from CSV
   - Preview Import
5. Backup & Restore
   - Create Backup
   - Restore from Backup
   - View Backups
   - Cleanup Old Backups
6. Data Validation
   - Run Validation
   - View Issues
   - Auto-Fix Issues
7. Database Statistics
8. Back to Main Menu

## Success Criteria

- Can export transactions to CSV with proper formatting
- Can export transactions to JSON with complete data
- Can export budgets to both formats
- Can export comprehensive monthly reports
- Can import transactions from CSV with validation
- Can detect and skip duplicate transactions
- Backup creates timestamped ZIP archive
- Restore successfully recovers all data
- Backup before restore works automatically
- Data validation finds and reports issues
- Auto-fix resolves common issues
- Database statistics display correctly
- Old backups cleanup works
- All exports save to correct location

## Testing Checklist

- Export empty transaction list
- Export single transaction
- Export all transactions
- Export with date range filter
- Export with category filter
- Export budgets with no budgets set
- Export monthly report with no data
- Import valid CSV file
- Import CSV with invalid dates
- Import CSV with negative amounts
- Import CSV with invalid categories
- Import CSV with duplicates
- Import CSV with wrong headers
- Create backup with all files
- Create backup with missing files
- Restore from valid backup
- Restore from corrupt backup
- List backups when none exist
- Cleanup backups with <10 backups
- Cleanup backups with >10 backups
- Validate clean data (no issues)
- Validate corrupt data (multiple issues)
- Auto-fix common issues
- Get statistics with no data
- Get statistics with complete data
- Test export to custom path
- Test export with file permissions issue

## Edge Cases to Handle

- No data to export (empty files)
- Export filename already exists (overwrite/rename)
- Invalid export path (create directory)
- CSV file too large to import
- Malformed CSV (wrong delimiter, encoding issues)
- Import CSV with extra columns
- Import CSV with missing columns
- Backup while files are being modified
- Restore while application is running
- Corrupted backup ZIP file
- Disk full during export/backup
- Permission denied on export/backup
- Invalid characters in filenames
- Very old backup format (version mismatch)
- Backup with no transaction file
- Import with all rows being duplicates
- Import with all rows being invalid
- Validation on empty database
- Auto-fix creates new issues

## File Encoding

- Always use UTF-8 encoding for all files
- Handle BOM (Byte Order Mark) in CSV imports
- Support international characters in descriptions
- Test with non-ASCII characters

## Security Considerations

- Do not export sensitive data without encryption (future)
- Validate file paths to prevent directory traversal
- Sanitize filenames (remove special characters)
- Check file size limits before import
- Validate ZIP contents before extraction
- Never execute code from imported files

## Performance Optimization

- Stream large CSV files (don't load all in memory)
- Show progress bar for large imports/exports
- Batch process transactions for better performance
- Compress backups to save space
- Index transactions for faster filtering

## Error Handling

- Handle file not found errors gracefully
- Handle permission denied errors
- Handle disk full errors
- Handle corrupted file errors
- Handle network path errors (if applicable)
- Provide clear error messages
- Suggest solutions for common errors
- Log errors for debugging

## Export File Naming Convention

```
transactions_YYYYMMDD_HHMMSS.csv
transactions_YYYYMMDD_HHMMSS.json
budgets_YYYYMMDD_HHMMSS.csv
budgets_YYYYMMDD_HHMMSS.json
monthly_report_YYYY_MM.json
backup_YYYYMMDD_HHMMSS.zip
```

## Import Duplicate Detection Strategy

Consider transactions duplicate if ALL fields match:

- Same date
- Same type
- Same category
- Same amount (in paisa)
- Same description

Allow option to:

- Skip duplicates (default)
- Import duplicates anyway
- Update existing (if IDs available)
