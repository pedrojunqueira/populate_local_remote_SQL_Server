#!/usr/bin/env python3
"""
Table Creation Wizard - Interactive tool to create new SQL Server tables.

This script helps you:
1. Define table name and columns interactively
2. Choose appropriate data types
3. Set constraints and defaults
4. Generate SQL CREATE TABLE script
5. Optionally execute the script on the database
"""

import os
import re
import pyodbc
import configparser
import sys
from pathlib import Path

class TableCreationWizard:
    def __init__(self):
        """Initialize the table creation wizard."""
        self.table_name = ""
        self.columns = []
        
        # Common SQL Server data types
        self.data_types = {
            '1': 'NVARCHAR(100)',
            '2': 'INT',
            '3': 'DECIMAL(10,2)',
            '4': 'DATETIME2',
            '5': 'BIT',
            '6': 'BIGINT',
            '7': 'NVARCHAR(50)',
            '8': 'NVARCHAR(255)',
            '9': 'DATE',
            '10': 'FLOAT'
        }
    
    def display_data_types(self):
        """Display available data types."""
        print("\n📊 Available Data Types:")
        print("1.  NVARCHAR(100)  - Text (up to 100 characters)")
        print("2.  INT            - Integer number")
        print("3.  DECIMAL(10,2)  - Decimal number (10 digits, 2 decimal places)")
        print("4.  DATETIME2      - Date and time")
        print("5.  BIT            - Boolean (True/False)")
        print("6.  BIGINT         - Large integer")
        print("7.  NVARCHAR(50)   - Short text (up to 50 characters)")
        print("8.  NVARCHAR(255)  - Long text (up to 255 characters)")
        print("9.  DATE           - Date only")
        print("10. FLOAT          - Floating point number")
        print("11. Custom         - Enter your own data type")
    
    def get_table_name(self):
        """Get table name from user."""
        while True:
            name = input("\n📋 Enter table name: ").strip()
            if name and re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
                self.table_name = name
                break
            else:
                print("❌ Table name must start with a letter and contain only letters, numbers, and underscores")
    
    def add_column(self):
        """Add a column interactively."""
        print(f"\n➕ Adding column to table '{self.table_name}'")
        
        # Column name
        while True:
            col_name = input("Column name: ").strip()
            if col_name and re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', col_name):
                # Check if column already exists
                if any(col['name'] == col_name for col in self.columns):
                    print(f"❌ Column '{col_name}' already exists!")
                    continue
                break
            else:
                print("❌ Column name must start with a letter and contain only letters, numbers, and underscores")
        
        # Data type
        self.display_data_types()
        while True:
            type_choice = input("\nSelect data type (1-11): ").strip()
            if type_choice in self.data_types:
                data_type = self.data_types[type_choice]
                break
            elif type_choice == '11':
                custom_type = input("Enter custom data type: ").strip()
                if custom_type:
                    data_type = custom_type
                    break
                else:
                    print("❌ Custom data type cannot be empty")
            else:
                print("❌ Please select a valid option (1-11)")
        
        # Nullable
        nullable = input("Allow NULL values? (y/n, default: y): ").strip().lower()
        is_nullable = nullable in ['', 'y', 'yes']
        
        # Primary key
        is_primary = False
        if not any(col.get('primary_key', False) for col in self.columns):
            primary = input("Is this a primary key? (y/n, default: n): ").strip().lower()
            is_primary = primary in ['y', 'yes']
        
        # Identity (auto-increment) for primary keys
        is_identity = False
        if is_primary and any(t in data_type.upper() for t in ['INT', 'BIGINT']):
            identity = input("Auto-increment (IDENTITY)? (y/n, default: y): ").strip().lower()
            is_identity = identity in ['', 'y', 'yes']
        
        # Default value
        default_value = None
        if not is_identity:
            default = input("Default value (leave empty for none): ").strip()
            if default:
                # Smart defaults based on data type
                if 'DATETIME' in data_type.upper() or 'DATE' in data_type.upper():
                    if default.lower() in ['now', 'current', 'sysdatetime']:
                        default_value = 'SYSDATETIME()'
                    else:
                        default_value = f"'{default}'"
                elif any(t in data_type.upper() for t in ['NVARCHAR', 'VARCHAR', 'CHAR']):
                    default_value = f"'{default}'"
                else:
                    default_value = default
        
        # Add column to list
        column = {
            'name': col_name,
            'type': data_type,
            'nullable': is_nullable,
            'primary_key': is_primary,
            'identity': is_identity,
            'default': default_value
        }
        
        self.columns.append(column)
        print(f"✅ Added column: {col_name} ({data_type})")
    
    def display_current_table(self):
        """Display current table structure."""
        if not self.columns:
            print("📋 No columns defined yet")
            return
        
        print(f"\n📋 Current table structure for '{self.table_name}':")
        print("-" * 60)
        for i, col in enumerate(self.columns, 1):
            nullable_str = "NULL" if col['nullable'] else "NOT NULL"
            pk_str = " (PK)" if col['primary_key'] else ""
            identity_str = " IDENTITY" if col['identity'] else ""
            default_str = f" DEFAULT {col['default']}" if col['default'] else ""
            
            print(f"{i:2}. {col['name']:<20} {col['type']:<15} {nullable_str:<8}{pk_str}{identity_str}{default_str}")
    
    def generate_sql(self):
        """Generate CREATE TABLE SQL script."""
        if not self.columns:
            return None
        
        sql_lines = [f"CREATE TABLE {self.table_name} ("]
        
        column_definitions = []
        primary_keys = []
        
        for col in self.columns:
            # Build column definition
            col_def = f"    {col['name']} {col['type']}"
            
            # Add IDENTITY
            if col['identity']:
                col_def += " IDENTITY(1,1)"
            
            # Add NULL/NOT NULL
            if not col['nullable']:
                col_def += " NOT NULL"
            
            # Add DEFAULT
            if col['default']:
                col_def += f" DEFAULT {col['default']}"
            
            column_definitions.append(col_def)
            
            # Track primary keys
            if col['primary_key']:
                primary_keys.append(col['name'])
        
        # Add column definitions
        sql_lines.extend([def_ + "," for def_ in column_definitions])
        
        # Add primary key constraint
        if primary_keys:
            pk_constraint = f"    CONSTRAINT PK_{self.table_name} PRIMARY KEY ({', '.join(primary_keys)})"
            sql_lines.append(pk_constraint)
        else:
            # Remove trailing comma from last column
            sql_lines[-1] = sql_lines[-1].rstrip(',')
        
        sql_lines.append(");")
        
        return '\n'.join(sql_lines)
    
    def save_sql_file(self, sql_content):
        """Save SQL to file."""
        filename = f"create_table_{self.table_name.lower()}.sql"
        
        try:
            with open(filename, 'w') as f:
                f.write(sql_content)
            print(f"💾 SQL script saved as '{filename}'")
            return filename
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None
    
    def run_wizard(self):
        """Run the interactive table creation wizard."""
        print("🎯 Table Creation Wizard")
        print("=" * 40)
        print("This wizard will help you create a new SQL Server table.")
        print("You can define columns, data types, constraints, and defaults.")
        
        # Get table name
        self.get_table_name()
        
        # Add columns
        while True:
            if self.columns:
                self.display_current_table()
            
            print(f"\n🔧 Options for table '{self.table_name}':")
            print("1. Add column")
            if self.columns:
                print("2. Remove column")
                print("3. Generate SQL script")
                print("4. Save and exit")
            print("0. Exit without saving")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.add_column()
            elif choice == '2' and self.columns:
                self.remove_column()
            elif choice == '3' and self.columns:
                self.preview_sql()
            elif choice == '4' and self.columns:
                self.finalize_table()
                break
            elif choice == '0':
                print("👋 Exiting without saving")
                break
            else:
                print("❌ Invalid option")
    
    def remove_column(self):
        """Remove a column."""
        self.display_current_table()
        try:
            index = int(input(f"\nEnter column number to remove (1-{len(self.columns)}): ")) - 1
            if 0 <= index < len(self.columns):
                removed_col = self.columns.pop(index)
                print(f"🗑️  Removed column: {removed_col['name']}")
            else:
                print("❌ Invalid column number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def preview_sql(self):
        """Preview the generated SQL."""
        sql = self.generate_sql()
        if sql:
            print("\n📄 Generated SQL:")
            print("-" * 40)
            print(sql)
            print("-" * 40)
    
    def finalize_table(self):
        """Finalize and save the table."""
        sql = self.generate_sql()
        if not sql:
            print("❌ No columns defined")
            return
        
        # Preview SQL
        self.preview_sql()
        
        # Save to file
        filename = self.save_sql_file(sql)
        
        if filename:
            print(f"\n🎉 Table '{self.table_name}' definition complete!")
            print(f"📄 SQL file: {filename}")
            print(f"🚀 You can now use 'populate_tables_generic.py' to populate this table with data!")

def main():
    """Main function."""
    wizard = TableCreationWizard()
    wizard.run_wizard()

if __name__ == "__main__":
    main()
