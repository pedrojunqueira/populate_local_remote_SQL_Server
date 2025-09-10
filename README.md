# Fabric Mirror Testing Project

A comprehensive Python-based data population and table management toolkit for testing Microsoft Fabric mirroring capabilities between local and remote SQL Server instances.

## 📋 Project Overview

This project provides a complete framework for creating, managing, and populating SQL Server tables with realistic test data. It features both legacy scripts for specific use cases and modern generic tools that can handle any table structure. The system is specifically designed for testing data mirroring functionality in Microsoft Fabric by creating consistent test datasets across different database instances.

## 🏗️ Project Structure

```
fabric_mirror/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .gitignore                    # Git ignore rules (protects credentials)
├── config.ini.template          # Configuration template
├── create_config.py              # Interactive config file generator
├── LICENSE                       # MIT License
│
├── 🎯 Generic Tools (Recommended)
├── populate_tables_generic.py    # Generic table populator with DB selection
├── create_table_wizard.py        # Interactive table creation wizard
│
├── 📄 Table Definitions
├── create_table_addresses.sql    # Addresses table definition
├── create_table_person.sql       # Person table definition (example)
│
├── 🔧 Legacy Scripts
├── populate_table_local.py       # Legacy: Populate specific local instance
├── populate_table.py             # Legacy: Populate specific remote instance
└── config.ini                    # Configuration file (auto-generated, git-ignored)
```

## 🎯 Use Cases

- **Fabric Mirroring Testing**: Create consistent datasets for testing data synchronization
- **Database Migration Testing**: Validate data consistency between environments
- **Performance Testing**: Generate sample data for load testing scenarios
- **Development Environment Setup**: Quick sample data population for development
- **Schema Management**: Create and modify table structures interactively
- **Multi-Environment Testing**: Seamlessly switch between local and remote databases

## 🚀 Quick Start

### Prerequisites

- Python 3.7+ installed
- SQL Server ODBC Driver 18 installed
- Access to local and/or remote SQL Server instances
- Docker Desktop (for WSL2 users connecting to Windows SQL Server)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database Connections

Run the interactive configuration script:

```bash
python create_config.py
```

The configuration script offers flexible setup options:

- **Choose what to configure**: You can configure LOCAL only, REMOTE only, or both environments
- **Environment-specific settings**: Each environment has tailored defaults and connection parameters
- **Smart defaults**: 
  - LOCAL: Defaults to `host.docker.internal`, encryption disabled
  - REMOTE: Optimized for Azure SQL Database, encryption enabled

**Configuration prompts:**
1. Configure LOCAL SQL Server connection? (y/n)
2. Configure REMOTE SQL Server connection? (y/n)

For each selected environment, you'll be prompted for:
- Server name/address (with environment-appropriate suggestions)
- Database name
- Username and password (securely masked during input)
- ODBC driver settings

**Resulting sections in config.ini:**
- `[DEFAULT]` - Automatically created from your first configured environment
- `[LOCAL]` - Local development/testing database settings (if configured)
- `[REMOTE]` - Remote/Azure database settings (if configured)

### 3. Create Tables (Choose Your Method)

#### 🎯 Method A: Interactive Table Creation (Recommended)

Create tables using the interactive wizard:

```bash
python create_table_wizard.py
```

**Features:**
- Interactive column-by-column definition
- Smart data type suggestions
- Primary key and constraint setup
- Default value configuration
- Real-time SQL preview
- Automatic file generation

#### 📄 Method B: Manual SQL Files

Create SQL files following the naming convention `create_table_<tablename>.sql`:

```sql
-- Example: create_table_addresses.sql
CREATE TABLE Addresses (
    AddressID INT IDENTITY(1,1) PRIMARY KEY,
    StreetAddress NVARCHAR(100) NOT NULL,
    City NVARCHAR(50) NOT NULL,
    State NVARCHAR(3) NOT NULL,
    PostalCode NVARCHAR(4) NOT NULL,
    Country NVARCHAR(50) NOT NULL DEFAULT 'Australia',
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
```

### 4. Populate Tables with Data

#### 🚀 Generic Table Populator (Recommended)

Use the intelligent generic populator:

```bash
python populate_tables_generic.py
```

**Features:**
- **Database Selection**: Choose between LOCAL and REMOTE at runtime
- **Table Discovery**: Automatically finds all `create_table_*.sql` files
- **Smart Data Generation**: Context-aware fake data based on column names and types
- **Interactive Interface**: Select table and specify record count
- **Flexible**: Works with any table structure

#### 🔧 Legacy Scripts (Specific Use Cases)

For backward compatibility with existing workflows:

```bash
python populate_table_local.py   # Uses DEFAULT/LOCAL configuration
python populate_table.py         # Uses REMOTE configuration (if configured)
```

**Note:** These scripts generate 10 rows of Australian address data and use fallback logic (LOCAL → DEFAULT).

## 🧠 Smart Data Generation

The generic populator includes intelligent data generation based on column names and types:

### **Text/String Columns**
- `*address*`, `*street*` → Realistic street addresses
- `*city*` → Australian city names  
- `*state*` → Australian state abbreviations (NSW, VIC, QLD, etc.)
- `*postal*`, `*zip*` → Valid Australian postal codes
- `*country*` → "Australia" 
- `*first*name*` → First names
- `*last*name*` → Last names
- `*name*` (generic) → Full names
- `*email*` → Email addresses
- `*phone*` → Phone numbers
- `*company*` → Company names

### **Numeric Columns**
- `*age*` → Ages between 18-80
- `*year*` → Years between 1950-2025  
- `*price*`, `*cost*`, `*amount*` → Currency values (10.00-1000.00)
- Other numeric → Random integers/decimals

### **Date/Time Columns**
- `*birth*`, `*dob*` → Birth dates
- `*created*`, `*updated*` → Recent timestamps
- Other dates → Random dates within the last year

### **Special Handling**
- **IDENTITY columns** → Automatically skipped
- **DEFAULT columns** → Let database handle (e.g., SYSDATETIME())
- **Boolean/BIT** → Random true/false values

### **Example Generated Data**
```
PersonID | FirstName | LastName | Age | DOB        | CreatedAt
---------|-----------|----------|-----|------------|-------------------
1        | Sarah     | Wilson   | 34  | 1989-03-15 | 2025-09-10 14:30:22
2        | Michael   | Chen     | 28  | 1995-11-08 | 2025-09-10 14:30:22
3        | Emma      | Taylor   | 42  | 1981-07-22 | 2025-09-10 14:30:22
```

## � Complete Workflow Example

Here's a typical end-to-end workflow for testing Fabric mirroring:

### **Step 1: Setup Configuration**
```bash
python create_config.py
# Configure both LOCAL and REMOTE environments
```

### **Step 2: Create Table Structure**
```bash
python create_table_wizard.py
# Interactively create a "products" table with:
# - ProductID (INT, PK, IDENTITY)  
# - ProductName (NVARCHAR(100))
# - Price (DECIMAL(10,2))
# - CreatedAt (DATETIME2, DEFAULT SYSDATETIME())
```

### **Step 3: Populate Local Environment**
```bash
python populate_tables_generic.py
# Select: 1. LOCAL
# Select: products table  
# Generate: 1000 records
```

### **Step 4: Setup Fabric Mirroring**
- Configure mirroring from LOCAL to REMOTE in Microsoft Fabric
- Monitor initial sync

### **Step 5: Populate More Data & Test Sync**
```bash
python populate_tables_generic.py
# Select: 1. LOCAL  
# Select: products table
# Generate: 500 additional records
```

### **Step 6: Validate Mirroring**
```bash
python populate_tables_generic.py
# Select: 2. REMOTE
# Check record counts and data consistency
```

This workflow creates a complete test scenario for validating data synchronization between environments!

## �🛠️ Configuration

### Flexible Configuration Options

The `create_config.py` script provides flexible configuration management:

1. **Selective Configuration**: Choose to configure LOCAL, REMOTE, or both environments
2. **Automatic DEFAULT Section**: The first configured environment becomes the DEFAULT
3. **Environment-Specific Settings**: Each environment has optimized connection parameters

### Configuration Sections

The `config.ini` file can contain up to three sections:

- **DEFAULT**: Automatically created from your first configured environment (used by `populate_table_local.py`)
- **LOCAL**: Local SQL Server instance settings (optional)
- **REMOTE**: Remote SQL Server instance settings (used by `populate_table.py`)

### Sample Configuration Scenarios

**Scenario 1: Only REMOTE configured**
```ini
[DEFAULT]
server = your-server.database.windows.net
database = your_database
# ... (copies REMOTE settings)

[REMOTE]  
server = your-server.database.windows.net
database = your_database
encrypt = yes
```

**Scenario 2: Both LOCAL and REMOTE configured**
```ini
[DEFAULT]
server = host.docker.internal
database = sample_db
# ... (copies LOCAL settings)

[LOCAL]
server = host.docker.internal
database = sample_db
username = your_username
password = your_password
driver = {ODBC Driver 18 for SQL Server}
trust_server_certificate = yes
encrypt = no
connection_timeout = 30

[REMOTE]
server = your-server.database.windows.net
database = your_database
username = your_username
password = your_password
driver = {ODBC Driver 18 for SQL Server}
trust_server_certificate = yes
encrypt = yes
connection_timeout = 30
```

## 🐳 Docker Desktop Setup (WSL2 Users)

If you're running this from WSL2 and connecting to a Windows SQL Server instance:

1. **Update Docker Desktop** to the latest version
2. **Enable Host Networking**:
   - Open Docker Desktop Settings
   - Go to **Resources > Networking**
   - Check **"Enable host networking"**
   - Restart Docker Desktop

This enables `host.docker.internal` connectivity from WSL to Windows services.

## 🔒 Security Features

- ✅ **Credential Protection**: Passwords are hidden during input using `getpass`
- ✅ **Secure File Permissions**: Config file automatically set to 600 (owner read/write only)
- ✅ **Git Protection**: `config.ini` automatically added to `.gitignore`
- ✅ **Error Handling**: Clear error messages for missing configurations
- ✅ **Multi-Environment Support**: Separate LOCAL/REMOTE configurations

## 📊 Generated Data Examples

The system can generate realistic data for various table structures:

### **Addresses Table**
```
AddressID | StreetAddress        | City      | State | PostalCode | Country   | CreatedAt
----------|---------------------|-----------|-------|------------|-----------|------------------
1         | 123 Collins Street  | Melbourne | VIC   | 3000       | Australia | 2025-09-10 14:30:00
2         | 456 George Street   | Sydney    | NSW   | 2000       | Australia | 2025-09-10 14:30:01
```

### **Person Table**
```
PersonID | FirstName | LastName | Age | DOB        | CreatedAt
---------|-----------|----------|-----|------------|-------------------
1        | Sarah     | Wilson   | 34  | 1989-03-15 | 2025-09-10 14:30:22
2        | Michael   | Chen     | 28  | 1995-11-08 | 2025-09-10 14:30:22
```

### **Products Table (Example)**
```
ProductID | ProductName        | Price  | Category    | CreatedAt
----------|-------------------|--------|-------------|-------------------
1         | Wireless Mouse    | 45.99  | Electronics | 2025-09-10 14:30:22
2         | Coffee Mug        | 12.50  | Kitchen     | 2025-09-10 14:30:22
```

**Data Volume:** Configure any number of records per table (default: 10, tested with 10,000+ records)

## 🔧 Troubleshooting

### Common Issues

**Connection Timeout (`HYT00` Error)**
- Verify SQL Server is running
- Check firewall settings
- For WSL2: Ensure Docker Desktop host networking is enabled
- Verify server name/connection string format

**Authentication Errors**
- Confirm SQL Server authentication is enabled
- Verify username/password credentials
- Check if user has necessary database permissions

**Missing Configuration**
- Run `python create_config.py` to create configuration file
- Verify `config.ini` exists and contains required sections

### WSL2 Specific Issues

If `host.docker.internal` doesn't work:
1. Update Docker Desktop
2. Enable host networking in Docker settings
3. Restart Docker Desktop
4. Test connection with `ping host.docker.internal`

## 🧪 Testing Fabric Mirroring

This project provides a complete testing framework for Microsoft Fabric mirroring:

### **Enhanced Testing Capabilities**

1. **🏗️ Schema Creation**: Use `create_table_wizard.py` to design test tables with various data types
2. **📊 Data Population**: Generate large datasets with `populate_tables_generic.py`
3. **🔄 Multi-Environment**: Test across LOCAL and REMOTE environments seamlessly
4. **📈 Volume Testing**: Generate thousands of records to test performance
5. **🎯 Targeted Testing**: Create specific table structures for different mirroring scenarios

### **Recommended Testing Workflow**

#### **Phase 1: Baseline Setup**
```bash
# 1. Create test tables
python create_table_wizard.py  # Create: customers, orders, products

# 2. Populate initial dataset  
python populate_tables_generic.py  # LOCAL → 10,000 customers
python populate_tables_generic.py  # LOCAL → 50,000 orders  
python populate_tables_generic.py  # LOCAL → 1,000 products
```

#### **Phase 2: Mirror Configuration**
- Configure Fabric mirroring: LOCAL → REMOTE
- Monitor initial synchronization
- Validate data consistency

#### **Phase 3: Incremental Testing**
```bash
# Generate additional data to test incremental sync
python populate_tables_generic.py  # LOCAL → 5,000 new orders
python populate_tables_generic.py  # LOCAL → 500 new customers

# Validate sync performance and latency
```

#### **Phase 4: Validation**
```bash
# Compare record counts and data integrity
python populate_tables_generic.py  # REMOTE → Check data consistency
```

### **Testing Scenarios**

- **🔄 Continuous Sync**: Regular data generation to test ongoing mirroring
- **📊 Bulk Load**: Large dataset creation for initial sync testing  
- **🎯 Schema Changes**: Create new tables and test structure mirroring
- **⚡ Performance**: High-volume data generation for stress testing
- **🔍 Data Types**: Test various SQL Server data types and constraints

## 📦 Dependencies

```
Faker==19.6.2          # Generate realistic fake data
pyodbc==4.0.39         # SQL Server connectivity
configparser==5.3.0    # Configuration file handling
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the configuration template
3. Ensure all prerequisites are installed
4. Verify network connectivity to your SQL Server instances

---

**Note**: This tool generates sample data for testing purposes. Ensure you have appropriate permissions before running against production databases.
