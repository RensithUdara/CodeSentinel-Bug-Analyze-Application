#!/usr/bin/env python3
"""
Entry point for the CodeSentinel desktop application.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.database.db_manager import DatabaseManager
from app.ui.theme import APP_DATA_DIR


def main():
    db_path = os.path.join(os.path.expanduser("~"), APP_DATA_DIR, "codesentinel.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = DatabaseManager(db_path)
    db.initialize()

    app = QApplication(sys.argv)

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
