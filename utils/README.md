# Utils Directory

This directory contains utility scripts and tools for AssetManager development and maintenance.

## Structure

### `/migrations`
Database migration scripts for schema changes:
- `migrate_add_benchmarks.py` - Add benchmark tracking columns
- `migrate_fix_column_names.py` - Fix column naming inconsistencies
- `migrate_snapshots.py` - Migrate to new snapshot schema
- `verify_migration.py` - Verify migration success

### `/debug`
Debugging and analysis tools:
- `balance_check.py` - Check account balances and verify API integration
- `analyze_balance.py` - Analyze balance data structure

## Usage

These scripts are typically one-time use or infrequent maintenance tools. Run them from the project root:

```bash
# Example: Run a migration
python utils/migrations/migrate_add_benchmarks.py

# Example: Check balances
python utils/debug/balance_check.py
```

## Note

- Migration scripts should be run in order and only once
- Debug scripts can be run anytime for troubleshooting
- Always backup your database before running migrations
