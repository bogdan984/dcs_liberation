import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from game.version import BUILD_NUMBER, GIT_SHA, VERSION_NUMBER


class BugReportDialog(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle("Сообщить об ошибке")
        self.setModal(True)
        self.setMaximumWidth(600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        components = [f"DCS Liberation {VERSION_NUMBER}"]
        if BUILD_NUMBER is not None:
            components.append(f"Сборка {BUILD_NUMBER}")
        if GIT_SHA is not None:
            components.append(f"Ревизия Git {GIT_SHA}")

        self.report_data = "\n".join(components)

        label = QLabel(
            "Нажмите кнопку ниже, чтобы сообщить об ошибке. Информация о версии будет"
            "автоматически скопирована в буфер обмена. Вставьте её в"
            "поле шаблона, где спрашивается версия.<br />"
            "<br />"
            "<strong>Перед отправкой поищите, нет ли уже такой ошибки.</strong><br />"
            "<br />"
            "<strong>Если шаблон просит файл сохранения, он обязателен. Какой бы"
            "легко воспроизводимой ни казалась ошибка, это почти никогда не так. Будь она"
            "очевидной, вы были бы не первым, кто её нашёл.</strong><br />"
            "<br />"
            f"{'<br />'.join(components)}<br />"
        )
        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
            | Qt.LinksAccessibleByMouse
            | Qt.LinksAccessibleByKeyboard
        )
        label.setWordWrap(True)
        label.setOpenExternalLinks(True)
        layout.addWidget(label)

        copy_button = QPushButton("Скопировать данные и перейти на страницу ошибок")
        copy_button.clicked.connect(self.on_file_bug)
        layout.addWidget(copy_button)

    def on_file_bug(self) -> None:
        QGuiApplication.clipboard().setText(self.report_data)
        webbrowser.open_new_tab(
            "https://github.com/dcs-liberation/dcs_liberation/issues/new/choose"
        )
