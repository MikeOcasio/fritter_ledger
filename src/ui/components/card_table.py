from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QFrame, QPushButton)
from PyQt6.QtCore import Qt

class CardTable(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create main widget and layout
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Make scroll area look good
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.container)

    def add_card(self, data):
        card = Card(data)
        self.layout.addWidget(card)

    def clear_cards(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

class Card(QFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.init_ui()

    def init_ui(self):
        # Set up card appearance
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            Card {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)

        # Create layout
        layout = QVBoxLayout(self)
        
        # Add data to card
        for key, value in self.data.items():
            if key != 'id' and key != 'receipt_image':  # Skip certain fields
                row = QHBoxLayout()
                label = QLabel(f"{key.title()}:")
                label.setStyleSheet("font-weight: bold;")
                value_label = QLabel(str(value))
                row.addWidget(label)
                row.addWidget(value_label)
                row.addStretch()
                layout.addLayout(row)