from sqlalchemy import create_engine, MetaData, Table, Column, String, text
import configparser
import os

def add_reference_id_to_receipts():
    # Load config
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    config.read(config_path)
    
    # Create database connection
    db_url = f"postgresql://{config['Database']['user']}:{config['Database']['password']}@{config['Database']['host']}:{config['Database']['port']}/{config['Database']['dbname']}"
    engine = create_engine(db_url)
    
    # Create metadata and reflect existing table
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Check if the receipts table exists
    if 'receipts' in metadata.tables:
        receipts = metadata.tables['receipts']
        
        # Check if the reference_id column exists
        if 'reference_id' not in receipts.columns:
            print("Adding reference_id column to receipts table...")
            
            # Execute ALTER TABLE command using a transaction
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE receipts ADD COLUMN reference_id VARCHAR;"))
                
            print("Column added successfully!")
        else:
            print("reference_id column already exists.")
    else:
        print("receipts table does not exist.")

def add_fields_to_income():
    # Load config
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    config.read(config_path)
    
    # Create database connection
    db_url = f"postgresql://{config['Database']['user']}:{config['Database']['password']}@{config['Database']['host']}:{config['Database']['port']}/{config['Database']['dbname']}"
    engine = create_engine(db_url)
    
    # Create metadata and reflect existing table
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Check if the income table exists
    if 'income' in metadata.tables:
        income = metadata.tables['income']
        
        # Check for each column and add if it doesn't exist
        new_columns = {
            'client': 'VARCHAR',
            'invoice_id': 'VARCHAR',
            'contract_id': 'VARCHAR',
            'status': 'VARCHAR'  # Added status column
        }
        
        for col_name, col_type in new_columns.items():
            if (col_name not in income.columns):
                print(f"Adding {col_name} column to income table...")
                
                # Execute ALTER TABLE command using a transaction
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE income ADD COLUMN {col_name} {col_type};"))
                    
                print(f"Column {col_name} added successfully!")
            else:
                print(f"{col_name} column already exists.")
    else:
        print("income table does not exist.")

def add_clients_table():
    # Load config
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
    config.read(config_path)
    
    # Create database connection
    db_url = f"postgresql://{config['Database']['user']}:{config['Database']['password']}@{config['Database']['host']}:{config['Database']['port']}/{config['Database']['dbname']}"
    engine = create_engine(db_url)
    
    # Create the clients table if it doesn't exist
    with engine.begin() as conn:
        # Check if the clients table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clients')"))
        exists = result.scalar()
        
        if not exists:
            print("Creating clients table...")
            conn.execute(text("""
                CREATE TABLE clients (
                    id SERIAL PRIMARY KEY,
                    business_name VARCHAR NOT NULL,
                    poc VARCHAR,
                    email VARCHAR NOT NULL,
                    phone VARCHAR,
                    address VARCHAR
                )
            """))
            print("Clients table created successfully!")
        else:
            print("Clients table already exists.")

if __name__ == "__main__":
    add_reference_id_to_receipts()
    add_fields_to_income()
    add_clients_table()