import os

from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from qt_ui import liberation_install, liberation_theme
from qt_ui.liberation_theme import THEMES, get_theme_index, set_theme_index


class QLiberationPreferences(QFrame):
    def __init__(self):
        super(QLiberationPreferences, self).__init__()
        self.saved_game_dir = ""
        self.dcs_install_dir = ""
        self.install_dir_ignore_warning = False

        self.dcs_install_dir = liberation_install.get_dcs_install_directory()
        self.saved_game_dir = liberation_install.get_saved_game_dir()

        self.edit_dcs_install_dir = QLineEdit(self.dcs_install_dir)
        self.edit_saved_game_dir = QLineEdit(self.saved_game_dir)

        self.edit_dcs_install_dir.setMinimumWidth(300)
        self.edit_saved_game_dir.setMinimumWidth(300)

        self.browse_saved_game = QPushButton("Обзор...")
        self.browse_saved_game.clicked.connect(self.on_browse_saved_games)
        self.browse_install_dir = QPushButton("Обзор...")
        self.browse_install_dir.clicked.connect(self.on_browse_installation_dir)
        self.themeSelect = QComboBox()
        [self.themeSelect.addItem(y["themeName"]) for x, y in THEMES.items()]

        self.initUi()

    def initUi(self):
        main_layout = QVBoxLayout()
        layout = QGridLayout()
        layout.addWidget(
            QLabel("<strong>Папка Saved Games DCS:</strong>"),
            0,
            0,
            alignment=Qt.AlignLeft,
        )
        layout.addWidget(self.edit_saved_game_dir, 1, 0, alignment=Qt.AlignRight)
        layout.addWidget(self.browse_saved_game, 1, 1, alignment=Qt.AlignRight)
        layout.addWidget(
            QLabel("<strong>Папка установки DCS:</strong>"),
            2,
            0,
            alignment=Qt.AlignLeft,
        )
        layout.addWidget(self.edit_dcs_install_dir, 3, 0, alignment=Qt.AlignRight)
        layout.addWidget(self.browse_install_dir, 3, 1, alignment=Qt.AlignRight)
        layout.addWidget(QLabel("<strong>Тема (нужен перезапуск)</strong>"), 4, 0)
        layout.addWidget(self.themeSelect, 4, 1, alignment=Qt.AlignRight)
        self.themeSelect.setCurrentIndex(get_theme_index())

        main_layout.addLayout(layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def on_browse_saved_games(self):
        saved_game_dir = str(
            QFileDialog.getExistingDirectory(self, "Выберите папку Saved Games DCS")
        )
        if saved_game_dir:
            self.saved_game_dir = saved_game_dir
            self.edit_saved_game_dir.setText(saved_game_dir)

    def on_browse_installation_dir(self):
        install_dir = str(
            QFileDialog.getExistingDirectory(self, "Выберите папку установки DCS")
        )
        if install_dir:
            self.dcs_install_dir = install_dir
            self.edit_dcs_install_dir.setText(install_dir)

    def apply(self):
        print("Применение изменений")
        self.saved_game_dir = self.edit_saved_game_dir.text()
        self.dcs_install_dir = self.edit_dcs_install_dir.text()
        set_theme_index(self.themeSelect.currentIndex())

        if not os.path.isdir(self.saved_game_dir):
            error_dialog = QMessageBox.critical(
                self,
                "Неверная папка Saved Games DCS.",
                self.saved_game_dir + " — неверная папка",
                QMessageBox.StandardButton.Ok,
            )
            error_dialog.exec_()
            return False

        if self.install_dir_ignore_warning and self.dcs_install_dir == "":
            warning_dialog = QMessageBox.warning(
                self,
                "Папка установки DCS не указана",
                "Папка установки DCS не указана!"
                "<br/><br/>Без неё DCS Liberation не сможет заменить MissionScripting.lua и не будет работать правильно."
                "В этом случае отредактируйте MissionScripting.lua сами. Проще всего заменить оригинальный файл (&lt;dcs_installation_directory&gt;/Scripts/MissionScripting.lua) файлом из дистрибутива dcs-liberation (&lt;dcs_liberation_installation&gt;/resources/scripts/MissionScripting.lua)."
                "<br/><br/>Подробнее о ручном изменении этого файла — в Liberation Wiki на GitHub (страница: Dedicated Server Guide).</p>"
                "<br/><br/>Точно оставить папку установки пустой?"
                "<br/><br/><strong>Рекомендуется только опытным пользователям!</strong>",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if warning_dialog == QMessageBox.No:
                return False
        elif not os.path.isdir(self.dcs_install_dir):
            error_dialog = QMessageBox.critical(
                self,
                "Неверная папка установки DCS.",
                self.dcs_install_dir
                + " — неверная папка. DCS Liberation нужна папка установки, чтобы заменить MissionScripting.lua"
                "<br/><br/>Если проигнорировать эту ошибку, DCS Liberation не сможет нормально работать."
                "В этом случае отредактируйте MissionScripting.lua сами. Проще всего заменить оригинальный файл (&lt;dcs_installation_directory&gt;/Scripts/MissionScripting.lua) файлом из дистрибутива dcs-liberation (&lt;dcs_liberation_installation&gt;/resources/scripts/MissionScripting.lua)."
                "<br/><br/>Подробнее о ручном изменении этого файла — в Liberation Wiki на GitHub (страница: Dedicated Server Guide).</p>"
                "<br/><br/><strong>Рекомендуется только опытным пользователям!</strong>",
                QMessageBox.StandardButton.Ignore,
                QMessageBox.StandardButton.Ok,
            )
            if error_dialog == QMessageBox.Ignore:
                self.install_dir_ignore_warning = True
            return False
        elif not os.path.isdir(
            os.path.join(self.dcs_install_dir, "Scripts")
        ) and os.path.isfile(os.path.join(self.dcs_install_dir, "bin", "DCS.exe")):
            error_dialog = QMessageBox.critical(
                self,
                "Неверная папка установки DCS.",
                self.dcs_install_dir + " — неверная папка установки DCS",
                QMessageBox.StandardButton.Ok,
            )
            error_dialog.exec_()
            return False

        liberation_install.setup(self.saved_game_dir, self.dcs_install_dir)
        liberation_install.save_config()
        liberation_theme.save_theme_config()
        return True
