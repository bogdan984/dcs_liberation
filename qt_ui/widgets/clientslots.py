"""Widgets for displaying client slots."""

from PySide6.QtWidgets import QLabel

from qt_ui.models import AtoModel
from qt_ui.widgets.QLabeledWidget import QLabeledWidget


class MaxPlayerCount(QLabeledWidget):
    def __init__(self, ato_model: AtoModel) -> None:
        self.ato_model = ato_model
        self.slots_label = QLabel(str(self.count_client_slots))
        self.ato_model.client_slots_changed.connect(self.update_count)
        super().__init__(
            "Макс. игроков:",
            self.slots_label,
            (
                "Общее число клиентских слотов. Чтобы добавить слоты, измените звено"
                "на панели слева."
            ),
        )

    @property
    def count_client_slots(self) -> int:
        slots = 0
        for package in self.ato_model.packages:
            for flight in package.flights:
                slots += flight.client_count
        return slots

    def update_count(self) -> None:
        self.slots_label.setText(str(self.count_client_slots))
