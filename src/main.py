import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.database.db_manager import DatabaseManager
from src.utils.db_migrate import (add_reference_id_to_receipts, add_fields_to_income, 
                                 add_clients_table, add_receipt_reference_to_expenses)

def main():
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    # Run database migrations
    try:
        add_reference_id_to_receipts()
        add_fields_to_income()
        add_clients_table()
        add_receipt_reference_to_expenses()  # Added new migration
    except Exception as e:
        print(f"Error during database migration: {str(e)}")
    
    # Create data directory for reference counters
    import os
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
    
    # Start Qt application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()