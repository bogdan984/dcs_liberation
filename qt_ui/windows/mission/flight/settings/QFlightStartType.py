from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from game.ato.flight import Flight
from game.ato.starttype import StartType
from game.theater import OffMapSpawn
from qt_ui.models import PackageModel


class QFlightStartType(QGroupBox):
    def __init__(self, package_model: PackageModel, flight: Flight):
        super().__init__()
        self.package_model = package_model
        self.flight = flight

        self.layout = QVBoxLayout()
        self.main_row = QHBoxLayout()
        self.start_type_label = QLabel("Тип старта:")
        self.start_type = QComboBox()

        for start_type in StartType:
            self.start_type.addItem(start_type.display_name, start_type)
        self.start_type.setCurrentText(flight.start_type.display_name)

        if isinstance(self.flight.departure, OffMapSpawn):
            self.start_type.setEnabled(False)

        self.start_type.currentTextChanged.connect(self._on_start_type_selected)
        self.main_row.addWidget(self.start_type_label)
        self.main_row.addWidget(self.start_type)

        self.layout.addLayout(self.main_row)
        self.layout.addWidget(
            QLabel(
                "Любой вариант, кроме холодного старта, делает звено недоступным"
                + "для ударов OCA/Aircraft. Это повлияет на баланс игры."
            )
        )
        self.setLayout(self.layout)

    def _on_start_type_selected(self):
        selected = self.start_type.currentData()
        self.flight.start_type = selected
        self.package_model.update_tot()
