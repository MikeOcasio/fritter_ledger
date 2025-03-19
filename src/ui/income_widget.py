from PyQt6 import QtWidgets
from ..models.income import Income

class IncomeWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Income Tracker")
        self.layout = QtWidgets.QVBoxLayout()

        self.amount_label = QtWidgets.QLabel("Amount:")
        self.amount_input = QtWidgets.QLineEdit()
        self.date_label = QtWidgets.QLabel("Date:")
        self.date_input = QtWidgets.QDateEdit()
        self.source_label = QtWidgets.QLabel("Source:")
        self.source_input = QtWidgets.QLineEdit()

        self.add_button = QtWidgets.QPushButton("Add Income")
        self.add_button.clicked.connect(self.add_income)

        self.layout.addWidget(self.amount_label)
        self.layout.addWidget(self.amount_input)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)
        self.layout.addWidget(self.source_label)
        self.layout.addWidget(self.source_input)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_income(self):
        amount = float(self.amount_input.text())
        date = self.date_input.date().toPyDate()
        source = self.source_input.text()

        new_income = Income(amount=amount, date=date, source=source)
        # Here you would typically save the new_income to the database
        print(f"Added income: {new_income}")