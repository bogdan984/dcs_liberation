from typing import Optional

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from game import Game
from game.income import Income
from qt_ui.windows.intel import IntelWindow


class QIntelBox(QGroupBox):
    def __init__(self, game: Game) -> None:
        super().__init__("Разведка")
        self.setProperty("style", "IntelSummary")

        self.game = game

        columns = QHBoxLayout()
        self.setLayout(columns)

        summary = QGridLayout()
        summary.setContentsMargins(5, 5, 5, 5)

        air_superiority = QLabel("Превосходство в воздухе:")
        summary.addWidget(air_superiority, 0, 0)
        self.air_strength = QLabel()
        summary.addWidget(self.air_strength, 0, 1)

        front_line = QLabel("Линия фронта:")
        summary.addWidget(front_line, 1, 0)
        self.ground_strength = QLabel()
        summary.addWidget(self.ground_strength, 1, 1)

        economy = QLabel("Экономика:")
        summary.addWidget(economy, 2, 0)
        self.economic_strength = QLabel()
        summary.addWidget(self.economic_strength, 2, 1)

        self.details = QPushButton()
        self.details.setMinimumHeight(50)
        self.details.setMinimumWidth(210)
        self.details.setLayout(summary)
        columns.addWidget(self.details)
        self.details.clicked.connect(self.open_details_window)
        self.details.setEnabled(False)

        self.update_summary()

        self.details_window: Optional[IntelWindow] = None

    def set_game(self, game: Optional[Game]) -> None:
        self.game = game
        self.details.setEnabled(True)
        self.update_summary()

    @staticmethod
    def forces_strength_text(own: int, enemy: int) -> str:
        if not enemy:
            return "противник уничтожен"

        ratio = own / enemy
        if ratio < 0.6:
            return "outnumbered"
        if ratio < 0.8:
            return "небольшое отставание"
        if ratio < 1.2:
            return "равенство сил"
        if ratio < 1.4:
            return "небольшое преимущество"
        return "большое преимущество"

    def economic_strength_text(self) -> str:
        assert self.game is not None
        own = Income(self.game, player=True).total
        enemy = Income(self.game, player=False).total

        if not enemy:
            return "экономика противника разрушена"

        ratio = own / enemy
        if ratio < 0.6:
            return "сильное отставание"
        if ratio < 0.8:
            return "небольшое отставание"
        if ratio < 1.2:
            return "равенство сил"
        if ratio < 1.4:
            return "небольшое преимущество"
        return "большое преимущество"

    def update_summary(self) -> None:
        if self.game is None:
            self.air_strength.setText("нет данных")
            self.ground_strength.setText("нет данных")
            self.economic_strength.setText("нет данных")
            return

        data = self.game.game_stats.data_per_turn[-1]

        self.air_strength.setText(
            self.forces_strength_text(
                data.allied_units.aircraft_count, data.enemy_units.aircraft_count
            )
        )
        self.ground_strength.setText(
            self.forces_strength_text(
                data.allied_units.vehicles_count, data.enemy_units.vehicles_count
            )
        )
        self.economic_strength.setText(self.economic_strength_text())

        if self.game.turn == 0:
            self.air_strength.setText("сбор разведданных")
            self.ground_strength.setText("сбор разведданных")

    def open_details_window(self) -> None:
        self.details_window = IntelWindow(self.game)
        self.details_window.show()
