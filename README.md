# Fabric Mirror Testing Project

A Python-based data population tool for testing Microsoft Fabric mirroring capabilities between local and remote SQL Server instances.

## 📋 Project Overview

This project provides scripts to populate sample Australian address data into both local and remote SQL Server databases. It's specifically designed for testing data mirroring functionality in Microsoft Fabric by creating consistent test datasets across different database instances.

## 🏗️ Project Structure

```
fabric_mirror/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules (protects credentials)
├── config.ini.template        # Configuration template
├── create_config.py           # Interactive config file generator
├── create_table.sql           # SQL script to create the Addresses table
├── populate_table_local.py    # Populate local SQL Server instance
├── populate_table.py          # Populate remote SQL Server instance
└── config.ini                 # Configuration file (auto-generated, git-ignored)
```

## 🎯 Use Cases

- **Fabric Mirroring Testing**: Create consistent datasets for testing data synchronization
- **Database Migration Testing**: Validate data consistency between environments
- **Performance Testing**: Generate sample data for load testing scenarios
- **Development Environment Setup**: Quick sample data population for development

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

### 2. Create Database Table

Run the SQL script on your target databases:

```sql
-- Execute create_table.sql on both local and remote instances
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

### 3. Configure Database Connections

Run the interactive configuration script:

```bash
python create_config.py
```

This will prompt you for:
- Local SQL Server details (for WSL: typically `host.docker.internal`)
- Remote SQL Server details (Azure SQL Database or remote instance)
- Database credentials (securely masked during input)

### 4. Populate Sample Data

**For Local Instance:**
```bash
python populate_table_local.py
```

**For Remote Instance:**
```bash
python populate_table.py
```

Each script generates 10 rows of realistic Australian address data using the Faker library.

## 🛠️ Configuration

### Configuration Sections

The `config.ini` file contains three sections:

- **DEFAULT**: Fallback configuration values
- **LOCAL**: Local SQL Server instance settings
- **REMOTE**: Remote SQL Server instance settings

### Sample Configuration Structure

```ini
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

## 📊 Generated Data

Each run generates 10 rows of realistic Australian address data including:

- **Street Address**: Realistic Australian street addresses
- **City**: Australian city names
- **State**: Australian state abbreviations (NSW, VIC, QLD, etc.)
- **Postal Code**: Valid Australian postal codes
- **Country**: Fixed as "Australia"
- **Created Timestamp**: Automatic timestamp

Example output:
```
AddressID | StreetAddress        | City      | State | PostalCode | Country   | CreatedAt
----------|---------------------|-----------|-------|------------|-----------|------------------
1         | 123 Collins Street  | Melbourne | VIC   | 3000       | Australia | 2025-09-10 14:30:00
2         | 456 George Street   | Sydney    | NSW   | 2000       | Australia | 2025-09-10 14:30:01
```

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

This project is specifically designed for testing Microsoft Fabric mirroring:

1. **Setup**: Create identical table structures on source and target databases
2. **Populate**: Use these scripts to generate consistent test data
3. **Mirror**: Configure Fabric mirroring between the instances
4. **Validate**: Compare data consistency between source and mirrored instances
5. **Monitor**: Track synchronization performance and latency

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
