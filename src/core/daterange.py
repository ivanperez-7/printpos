from datetime import date

from PySide6.QtCore import QDate


class DateRange:
    MIN_DATE = QDate(1900, 1, 1)
    MAX_DATE = QDate.currentDate()

    def __init__(self, desde: QDate = MIN_DATE, hasta: QDate = MAX_DATE):
        self.desde: date = desde.toPython()
        self.hasta: date = hasta.toPython()

    def __repr__(self):
        return f"DateRange({self.desde}, {self.hasta})"
