from faker import Faker
import pyodbc
import configparser
import os
import sys

# Initialize Faker with Australian locale
fake = Faker('en_AU')

def load_config(section='DEFAULT'):
    """Load configuration from config.ini file."""
    config_file = 'config.ini'
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file '{config_file}' not found!")
        print("Please run 'python create_config.py' first to create the configuration file.")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if section not in config:
        print(f"❌ Section '{section}' not found in configuration file!")
        print(f"Available sections: {list(config.sections())}")
        sys.exit(1)
    
    return config[section]

# Load configuration
print("📖 Loading configuration...")
config = load_config('DEFAULT')  # Use DEFAULT section instead of LOCAL

# Extract connection parameters from config
server = config.get('server')
database = config.get('database')
username = config.get('username')
password = config.get('password')
driver = config.get('driver')
trust_cert = config.get('trust_server_certificate', 'yes')
encrypt = config.get('encrypt', 'no')
timeout = config.get('connection_timeout', '30')

print(f"🔗 Connecting to server: {server}")
print(f"📊 Database: {database}")
print(f"👤 Username: {username}")

# Connect to SQL Server
try:
    conn = pyodbc.connect(
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'TrustServerCertificate={trust_cert};'
        f'Encrypt={encrypt};'
        f'Connection Timeout={timeout}'
    )
    cursor = conn.cursor()
    print("✅ Successfully connected to SQL Server!")
    
except pyodbc.Error as e:
    print(f"❌ Failed to connect to SQL Server: {e}")
    sys.exit(1)

# Insert 10 rows of fake address data
for _ in range(10):
    street = fake.street_address()
    city = fake.city()
    state = fake.state_abbr()
    postal_code = fake.postcode()
    # print(f"Inserting: {street}, {city}, {state}, {postal_code}")
    insert_query = """
    INSERT INTO Addresses (StreetAddress, City, State, PostalCode)
    VALUES (?, ?, ?, ?)
    """
    cursor.execute(insert_query, (street, city, state, postal_code))

# Commit the transaction
conn.commit()

# Close the connection
cursor.close()
conn.close()