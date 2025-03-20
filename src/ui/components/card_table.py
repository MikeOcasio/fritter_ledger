from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QFrame, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal

class CardTable(QScrollArea):
    view_clicked = pyqtSignal(int)
    download_clicked = pyqtSignal(int)
    
    def __init__(self, with_actions=False, parent=None):
        super().__init__(parent)
        self.with_actions = with_actions
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
        card = Card(data, self.with_actions, self)
        if self.with_actions:
            card.view_clicked.connect(self.on_view_clicked)
            card.download_clicked.connect(self.on_download_clicked)
        self.layout.addWidget(card)

    def clear_cards(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def on_view_clicked(self, item_id):
        self.view_clicked.emit(item_id)
        
    def on_download_clicked(self, item_id):
        self.download_clicked.emit(item_id)


class Card(QFrame):
    view_clicked = pyqtSignal(int)
    download_clicked = pyqtSignal(int)
    
    def __init__(self, data, with_actions=False, parent=None):
        super().__init__(parent)
        self.data = data
        self.with_actions = with_actions
        self.item_id = data.get('ID')  # Store ID for reference
        self.init_ui()

    def init_ui(self):
        # Set up card appearance
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setProperty("class", "card")

        # Create layout
        main_layout = QVBoxLayout(self)
        
        # Add data to card
        data_layout = QVBoxLayout()
        for key, value in self.data.items():
            if key != 'ID':  # Skip ID field
                row = QHBoxLayout()
                label = QLabel(f"{key}:")
                label.setProperty("class", "title")
                value_label = QLabel(str(value))
                row.addWidget(label)
                row.addWidget(value_label)
                row.addStretch()
                data_layout.addLayout(row)
        
        main_layout.addLayout(data_layout)
        
        # Add action buttons if needed
        if self.with_actions and self.item_id:
            actions_layout = QHBoxLayout()
            
            view_btn = QPushButton("View")
            view_btn.clicked.connect(self.on_view_clicked)
            
            download_btn = QPushButton("Download")
            download_btn.clicked.connect(self.on_download_clicked)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(download_btn)
            actions_layout.addStretch()
            
            main_layout.addLayout(actions_layout)
    
    def on_view_clicked(self):
        if self.item_id:
            self.view_clicked.emit(self.item_id)
    
    def on_download_clicked(self):
        if self.item_id:
            self.download_clicked.emit(self.item_id)