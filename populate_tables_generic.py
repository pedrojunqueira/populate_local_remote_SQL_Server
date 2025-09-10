#!/usr/bin/env python3
"""
Generic Table Populator - A flexible data population tool for SQL Server tables.

This script can:
1. Detect existing table SQL files
2. Parse table schemas to understand column types
3. Generate appropriate fake data for each column type
4. Populate tables with specified number of records
"""

import os
import re
import pyodbc
import configparser
import sys
from faker import Faker
from pathlib import Path

# Initialize Faker with Australian locale
fake = Faker('en_AU')

class TablePopulator:
    def __init__(self):
        """Initialize the table populator."""
        self.config = None
        self.connection = None
        self.cursor = None
        
    def select_database_config(self):
        """Allow user to select which database configuration to use."""
        config_file = 'config.ini'
        
        if not os.path.exists(config_file):
            print(f"❌ Configuration file '{config_file}' not found!")
            print("Please run 'python create_config.py' first to create the configuration file.")
            sys.exit(1)
        
        config = configparser.ConfigParser()
        config.read(config_file)
        
        available_sections = [section for section in config.sections() if section in ['LOCAL', 'REMOTE']]
        
        if not available_sections:
            # Fall back to DEFAULT if no LOCAL/REMOTE sections
            if 'DEFAULT' in config:
                print("⚠️  No LOCAL or REMOTE sections found, using DEFAULT configuration")
                self.config = config['DEFAULT']
                return
            else:
                print("❌ No valid configuration sections found!")
                sys.exit(1)
        
        if len(available_sections) == 1:
            # Only one option available
            selected_section = available_sections[0]
            print(f"✅ Using {selected_section} configuration (only option available)")
            self.config = config[selected_section]
            return
        
        # Multiple options available - let user choose
        print("\n🗂️  Available Database Configurations:")
        for i, section in enumerate(available_sections, 1):
            server = config[section].get('server', 'Unknown')
            database = config[section].get('database', 'Unknown')
            print(f"   {i}. {section:<8} → {server} / {database}")
        
        while True:
            try:
                choice = input(f"\nSelect database configuration (1-{len(available_sections)}): ").strip()
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(available_sections):
                    selected_section = available_sections[choice_index]
                    print(f"✅ Selected {selected_section} configuration")
                    self.config = config[selected_section]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(available_sections)}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def connect_to_database(self):
        """Establish connection to the database."""
        if not self.config:
            print("❌ No configuration selected!")
            return False
            
        try:
            server = self.config.get('server')
            database = self.config.get('database')
            username = self.config.get('username')
            password = self.config.get('password')
            driver = self.config.get('driver')
            trust_cert = self.config.get('trust_server_certificate', 'yes')
            encrypt = self.config.get('encrypt', 'no')
            timeout = self.config.get('connection_timeout', '30')
            
            print(f"🔗 Connecting to server: {server}")
            print(f"📊 Database: {database}")
            print(f"👤 Username: {username}")
            
            self.connection = pyodbc.connect(
                f'DRIVER={driver};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
                f'TrustServerCertificate={trust_cert};'
                f'Encrypt={encrypt};'
                f'Connection Timeout={timeout}'
            )
            self.cursor = self.connection.cursor()
            print("✅ Successfully connected to SQL Server!")
            return True
            
        except pyodbc.Error as e:
            print(f"❌ Failed to connect to SQL Server: {e}")
            return False
    
    def discover_table_files(self):
        """Discover all SQL table files in the current directory."""
        sql_files = []
        current_dir = Path('.')
        
        for file in current_dir.glob('*.sql'):
            if file.name.lower().startswith('create_table') or file.name.lower().endswith('_table.sql'):
                sql_files.append(file)
        
        return sql_files
    
    def parse_table_schema(self, sql_file):
        """Parse a SQL CREATE TABLE file to extract table name and column information."""
        try:
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', sql_content, re.IGNORECASE)
            if not table_match:
                return None
            
            table_name = table_match.group(1)
            
            # Extract columns (simplified parser)
            columns = []
            column_pattern = r'(\w+)\s+([\w\(\)\,\s]+)(?:NOT\s+NULL|NULL)?(?:DEFAULT\s+[^,\)]+)?'
            
            # Find the content between parentheses after CREATE TABLE
            table_def_match = re.search(r'CREATE\s+TABLE\s+\w+\s*\((.*)\)', sql_content, re.IGNORECASE | re.DOTALL)
            if table_def_match:
                table_definition = table_def_match.group(1)
                
                # Split by commas but be careful with function calls like SYSDATETIME()
                lines = table_definition.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('--') and not 'PRIMARY KEY' in line.upper() and not 'CONSTRAINT' in line.upper():
                        # Extract column name and type
                        parts = line.split()
                        if len(parts) >= 2:
                            col_name = parts[0].strip(',')
                            col_type = parts[1].upper()
                            
                            # Skip IDENTITY columns for data generation
                            if 'IDENTITY' not in line.upper():
                                columns.append({
                                    'name': col_name,
                                    'type': col_type,
                                    'nullable': 'NOT NULL' not in line.upper(),
                                    'has_default': 'DEFAULT' in line.upper()
                                })
            
            return {
                'table_name': table_name,
                'columns': columns,
                'file_path': sql_file
            }
            
        except Exception as e:
            print(f"❌ Error parsing {sql_file}: {e}")
            return None
    
    def generate_fake_data(self, column):
        """Generate fake data based on column type."""
        col_type = column['type'].upper()
        col_name = column['name'].lower()
        
        # Handle columns with default values
        if column['has_default'] and 'created' in col_name:
            return None  # Let database handle it
        
        # String/Text types
        if any(t in col_type for t in ['NVARCHAR', 'VARCHAR', 'CHAR', 'TEXT']):
            if 'address' in col_name or 'street' in col_name:
                return fake.street_address()
            elif 'city' in col_name:
                return fake.city()
            elif 'state' in col_name:
                return fake.state_abbr()
            elif 'postal' in col_name or 'zip' in col_name:
                return fake.postcode()
            elif 'country' in col_name:
                return 'Australia'
            elif 'name' in col_name:
                if 'first' in col_name:
                    return fake.first_name()
                elif 'last' in col_name:
                    return fake.last_name()
                else:
                    return fake.name()
            elif 'email' in col_name:
                return fake.email()
            elif 'phone' in col_name:
                return fake.phone_number()
            elif 'company' in col_name:
                return fake.company()
            else:
                # Extract length if specified
                length_match = re.search(r'\((\d+)\)', col_type)
                max_length = int(length_match.group(1)) if length_match else 50
                return fake.text(max_length // 2)[:max_length]
        
        # Numeric types
        elif any(t in col_type for t in ['INT', 'BIGINT', 'SMALLINT']):
            if 'age' in col_name:
                return fake.random_int(min=18, max=80)
            elif 'year' in col_name:
                return fake.random_int(min=1950, max=2025)
            else:
                return fake.random_int(min=1, max=1000)
        
        # Decimal/Float types
        elif any(t in col_type for t in ['DECIMAL', 'FLOAT', 'MONEY']):
            if 'price' in col_name or 'cost' in col_name or 'amount' in col_name:
                return round(fake.random.uniform(10.0, 1000.0), 2)
            else:
                return round(fake.random.uniform(1.0, 100.0), 2)
        
        # Date/Time types
        elif any(t in col_type for t in ['DATE', 'DATETIME', 'DATETIME2']):
            if 'birth' in col_name:
                return fake.date_of_birth()
            else:
                return fake.date_time_between(start_date='-1y', end_date='now')
        
        # Boolean types
        elif 'BIT' in col_type:
            return fake.boolean()
        
        # Default fallback
        else:
            return fake.word()
    
    def populate_table(self, table_info, record_count):
        """Populate a table with fake data."""
        table_name = table_info['table_name']
        columns = [col for col in table_info['columns'] if not col['has_default']]
        
        if not columns:
            print(f"⚠️  No columns to populate in {table_name} (all have defaults)")
            return
        
        column_names = [col['name'] for col in columns]
        placeholders = ', '.join(['?' for _ in columns])
        
        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(column_names)})
        VALUES ({placeholders})
        """
        
        print(f"📝 Generating {record_count} records for table '{table_name}'...")
        print(f"🔹 Columns to populate: {', '.join(column_names)}")
        
        for i in range(record_count):
            values = []
            for column in columns:
                fake_value = self.generate_fake_data(column)
                values.append(fake_value)
            
            try:
                self.cursor.execute(insert_query, values)
                if (i + 1) % 100 == 0 or i == record_count - 1:
                    print(f"   ✅ Generated {i + 1}/{record_count} records")
            except pyodbc.Error as e:
                print(f"❌ Error inserting record {i + 1}: {e}")
                return False
        
        # Commit all records
        self.connection.commit()
        print(f"🎉 Successfully populated {record_count} records into '{table_name}'!")
        return True
    
    def close_connection(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def main():
    """Main interactive function."""
    print("🎯 Generic Table Populator")
    print("=" * 40)
    
    # Initialize populator
    populator = TablePopulator()
    
    # Select database configuration
    populator.select_database_config()
    
    # Connect to database
    if not populator.connect_to_database():
        return
    
    try:
        # Discover table files
        print("\n📁 Discovering SQL table files...")
        table_files = populator.discover_table_files()
        
        if not table_files:
            print("❌ No SQL table files found!")
            print("Create files like 'create_table_<name>.sql' or '<name>_table.sql'")
            return
        
        # Parse table schemas
        tables = []
        for sql_file in table_files:
            table_info = populator.parse_table_schema(sql_file)
            if table_info:
                tables.append(table_info)
        
        if not tables:
            print("❌ No valid table schemas found!")
            return
        
        # Display available tables
        print(f"\n📋 Found {len(tables)} table(s):")
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table['table_name']} ({len(table['columns'])} columns)")
        
        # Table selection
        while True:
            try:
                choice = input(f"\nSelect table to populate (1-{len(tables)}): ").strip()
                table_index = int(choice) - 1
                if 0 <= table_index < len(tables):
                    selected_table = tables[table_index]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(tables)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Record count selection
        while True:
            try:
                count = input("How many records to generate? (default: 10): ").strip()
                if not count:
                    record_count = 10
                else:
                    record_count = int(count)
                if record_count > 0:
                    break
                else:
                    print("❌ Please enter a positive number")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Populate table
        print(f"\n🚀 Starting data population...")
        success = populator.populate_table(selected_table, record_count)
        
        if success:
            print(f"\n✅ Data population completed successfully!")
        else:
            print(f"\n❌ Data population failed!")
    
    finally:
        populator.close_connection()

if __name__ == "__main__":
    main()
