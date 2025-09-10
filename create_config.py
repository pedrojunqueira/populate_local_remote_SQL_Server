#!/usr/bin/env python3
"""
Script to create a configuration file for SQL Server connection settings.
This will create a config.ini file with separate local and remote database connection parameters.
"""

import configparser
import os
from getpass import getpass

def get_connection_details(environment_name, default_server=None, default_database="sample_db"):
    """Get connection details for a specific environment."""
    print(f"\n🔧 Configuring {environment_name.upper()} SQL Server Connection")
    print("=" * 50)
    
    # Server configuration
    server_prompt = f"Enter {environment_name} server name/address"
    if default_server:
        server_prompt += f" (default: {default_server})"
    server_prompt += ": "
    
    server = input(server_prompt).strip()
    if not server:
        server = default_server or "localhost"
    
    # Database configuration
    database = input(f"Enter {environment_name} database name (default: {default_database}): ").strip()
    if not database:
        database = default_database
    
    # Username configuration
    username = input(f"Enter {environment_name} username: ").strip()
    if not username:
        print("❌ Username is required!")
        return None
    
    # Password configuration
    password = getpass(f"Enter {environment_name} password (input hidden): ")
    if not password:
        print("❌ Password is required!")
        return None
    
    # Driver configuration
    driver = input(f"Enter {environment_name} ODBC driver (default: {{ODBC Driver 18 for SQL Server}}): ").strip()
    if not driver:
        driver = "{ODBC Driver 18 for SQL Server}"
    
    # Environment-specific settings
    if environment_name.lower() == "local":
        trust_cert = "yes"
        encrypt = "no"
    else:  # remote/azure
        trust_cert = "yes"
        encrypt = "yes"
    
    return {
        'server': server,
        'database': database,
        'username': username,
        'password': password,
        'driver': driver,
        'trust_server_certificate': trust_cert,
        'encrypt': encrypt,
        'connection_timeout': '30'
    }

def create_config_file():
    """Create a configuration file with SQL Server connection settings."""
    
    config = configparser.ConfigParser()
    
    print("=== SQL Server Configuration Setup ===")
    print("This script will create a config.ini file with separate local and remote database settings.")
    print("You can configure both or skip one if not needed.")
    print()
    
    # Ask which environments to configure
    configure_local = input("Configure LOCAL SQL Server connection? (y/n, default: y): ").strip().lower()
    configure_local = configure_local in ['', 'y', 'yes']
    
    configure_remote = input("Configure REMOTE SQL Server connection? (y/n, default: y): ").strip().lower()
    configure_remote = configure_remote in ['', 'y', 'yes']
    
    if not configure_local and not configure_remote:
        print("❌ No configurations selected. Exiting.")
        return False
    
    # Configure LOCAL environment
    if configure_local:
        print("\n💻 LOCAL Configuration (typically for development/testing)")
        print("Common local servers: localhost, host.docker.internal, DATA-ENG-PYTHON\\MSSQLSERVER01")
        
        local_config = get_connection_details("local", "host.docker.internal", "sample_db")
        if not local_config:
            return False
        
        config['LOCAL'] = local_config
    
    # Configure REMOTE environment  
    if configure_remote:
        print("\n☁️  REMOTE Configuration (typically for Azure SQL or remote servers)")
        print("Example: your-server.database.windows.net")
        
        remote_config = get_connection_details("remote", None, "sample_db")
        if not remote_config:
            return False
        
        config['REMOTE'] = remote_config
    
    # Create DEFAULT section based on what was configured
    if configure_local:
        config['DEFAULT'] = dict(config['LOCAL'])
    elif configure_remote:
        config['DEFAULT'] = dict(config['REMOTE'])
    
    # Write configuration file
    config_file = 'config.ini'
    try:
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        
        print(f"\n✅ Configuration file '{config_file}' created successfully!")
        print(f"📁 Location: {os.path.abspath(config_file)}")
        
        # Show what was configured
        print(f"\n📋 Configured sections:")
        if configure_local:
            print(f"   🔹 LOCAL: {config['LOCAL']['server']} → {config['LOCAL']['database']}")
        if configure_remote:
            print(f"   🔹 REMOTE: {config['REMOTE']['server']} → {config['REMOTE']['database']}")
        
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("1. 'config.ini' is automatically added to .gitignore")
        print("2. File permissions set to 600 (owner read/write only)")
        print("3. Never share this file or commit it to version control")
        print("4. Passwords are stored in plain text - ensure file security")
        
        # Set secure file permissions
        os.chmod(config_file, 0o600)
        
        print(f"\n🚀 Usage:")
        if configure_local:
            print("   python populate_table_local.py   # Uses LOCAL section")
        if configure_remote:
            print("   python populate_table.py         # Uses REMOTE section")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")
        return False

if __name__ == "__main__":
    success = create_config_file()
    if success:
        print("\n🎉 Setup complete! You can now run your Python scripts safely.")
    else:
        print("\n❌ Setup failed. Please try again.")
