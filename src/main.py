import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.database.db_manager import DatabaseManager

def main():
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    # Start Qt application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()