from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QPlainTextEdit,
    QTextEdit,
)

from qt_ui.windows.preferences.QLiberationPreferences import QLiberationPreferences


class QLiberationFirstStartWindow(QDialog):
    def __init__(self):
        super(QLiberationFirstStartWindow, self).__init__()

        self.setModal(True)
        self.setWindowTitle("Первоначальная настройка")
        self.setMinimumSize(500, 200)
        self.setWindowIcon(QIcon("./resources/icon.png"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.WindowTitleHint)
        self.setWindowModality(Qt.WindowModal)
        self.preferences = QLiberationPreferences()

        WARN_TEXT = """
        <strong>Добро пожаловать в DCS Liberation!</strong>
        <br/><br>
        <strong>Пожалуйста, потратьте 30 секунд и прочитайте это:</strong>
        
        <p>DCS Liberation изменит этот файл в папке установки DCS:</p>
        <br/>
        <strong>&lt;dcs_installation_directory&gt;/Scripts/MissionScripting.lua</strong><br/> 
        
        <p>
        Это отключит часть ограничений безопасности среды Lua-скриптов DCS World, чтобы DCS World и DCS Liberation могли обмениваться данными.
        Однако такое изменение потенциально может дать вредоносным файлам миссий DCS доступ к вашей файловой системе.
        </p>
        
        <p>Поэтому, пока запущен DCS Liberation, не заходите на недоверенные серверы и не открывайте недоверенные миссии в DCS World.</p>
        
        <p>
        При закрытии DCS Liberation восстановит исходный файл MissionScripting.        
        </p>
        
        <p>
        Но если DCS Liberation неожиданно аварийно завершится (чего быть не должно), файл MissionScripting может остаться не восстановленным.
        В этом случае используйте резервную копию в папке DCS Liberation:
        </p>
        
        <br/>
        <strong>./resources/scripts/MissionScripting.original.lua</strong><br/>
        
        <p>Затем скопируйте её в папку установки DCS вместо этого файла:</p>
        
        <br/>
        <strong>&lt;dcs_installation_directory&gt;/Scripts/MissionScripting.lua</strong><br/>
        
        <p>После нажатия кнопки ниже файл в папке установки DCS будет заменён.</p>
        
        <br/>
        <p>Если оставить папку установки DCS пустой, DCS Liberation не сможет автоматически заменить MissionScripting.lua и не будет работать правильно!
        В этом случае отредактируйте файл сами. Проще всего заменить оригинальный файл файлом из дистрибутива dcs-liberation (&lt;dcs_liberation_installation&gt;/resources/scripts/MissionScripting.lua).
        <br/><br/>Подробнее о ручном изменении этого файла — в Liberation Wiki на GitHub (страница: Dedicated Server Guide).</p>

        
        <br/><br/>
        
        <strong>Спасибо, что прочитали!</strong>
        """
        self.warning_text = QTextEdit(WARN_TEXT)
        self.warning_text.setReadOnly(True)
        self.apply_button = QPushButton("Я всё прочитал(а) и принимаю")
        self.apply_button.clicked.connect(lambda: self.apply())
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.preferences)
        layout.addWidget(self.warning_text)
        layout.addStretch()
        apply_btn_layout = QHBoxLayout()
        apply_btn_layout.addStretch()
        apply_btn_layout.addWidget(self.apply_button)
        layout.addLayout(apply_btn_layout)
        self.setLayout(layout)

    def apply(self):
        print("Применение изменений")
        if self.preferences.apply():
            self.close()
