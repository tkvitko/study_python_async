import sys

from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QMainWindow, \
    QLabel, QVBoxLayout

from db import ServerDatabase

db = ServerDatabase()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle('Chat admin panel')
    layout = QVBoxLayout()

    # Таблица пользователей
    layout.addWidget(QLabel(text="User's list:"))
    users = db.get_users()
    table = QTableWidget(2, len(users))
    table.setHorizontalHeaderLabels(["Login", "Online"])

    row = 0
    for login, online in users:
        table.setItem(row, 0, QTableWidgetItem(login))
        table.setItem(row, 1, QTableWidgetItem(str(online)))
        row += 1
    layout.addWidget(table)

    # Подключение к базе данных
    engine_text = f'DB connection: {db.engine}'
    text_box = QLabel(text=engine_text)
    layout.addWidget(text_box)

    # Построение финального окна
    widget = QWidget()
    widget.setLayout(layout)
    window.setCentralWidget(widget)
    window.show()

    sys.exit(app.exec())
