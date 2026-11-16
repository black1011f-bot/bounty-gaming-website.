import re
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton,
    QVBoxLayout, QWidget
)

ROOT = Path(__file__).resolve().parent
ADB = str(ROOT / "tools" / "platform-tools" / "adb.exe")
SCRCPY = str(ROOT / "tools" / "scrcpy" / "scrcpy.exe")

def tool(path, name):
    return path if Path(path).is_file() else shutil.which(name)

class BountyDex(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BOUNTY Dex")
        self.resize(1080, 700)
        self.setMinimumSize(880, 580)
        self.adb = tool(ADB, "adb")
        self.scrcpy = tool(SCRCPY, "scrcpy")
        self.process = QProcess(self)
        self.build_ui()
        self.refresh_devices()

    def build_ui(self):
        self.setStyleSheet("""
          QWidget { background:#10131b; color:#edf1ff; font-family:'Segoe UI'; }
          QFrame#panel { background:#191f2c; border:1px solid #2b3447; border-radius:16px; }
          QLabel#brand { font-size:27px; font-weight:800; }
          QLabel#muted { color:#9ba8bd; }
          QLabel#heading { font-size:21px; font-weight:700; }
          QPushButton { background:#29354b; border:1px solid #3b4963; border-radius:10px; padding:11px 15px; font-weight:600; }
          QPushButton:hover { background:#394966; }
          QPushButton#primary { background:#6473ee; border:0; }
          QLineEdit,QComboBox { background:#101622; border:1px solid #3b4963; border-radius:9px; padding:10px; }
          QPlainTextEdit { background:#0c111a; border:1px solid #29354b; border-radius:10px; padding:8px; color:#bfcae0; }
        """)
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(20,20,20,20)
        outer.setSpacing(18)

        sidebar = QFrame()
        sidebar.setObjectName("panel")
        sidebar.setFixedWidth(220)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(18,20,18,18)
        brand = QLabel("BOUNTY <span style='color:#8290ff'>Dex</span>")
        brand.setObjectName("brand")
        sl.addWidget(brand)
        caption = QLabel("ANDROID DESKTOP EXPERIENCE")
        caption.setObjectName("muted")
        sl.addWidget(caption)
        sl.addSpacing(28)
        for item in ("▦  Рабочий стол", "▣  Подключение", "⚙  Настройки"):
            b = QPushButton(item)
            b.setStyleSheet("text-align:left")
            sl.addWidget(b)
        sl.addStretch()
        sl.addWidget(QLabel("Prototype 0.1"))
        outer.addWidget(sidebar)

        main = QVBoxLayout()
        main.setSpacing(15)
        outer.addLayout(main,1)
        head = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Рабочий стол")
        title.setObjectName("heading")
        titles.addWidget(title)
        sub = QLabel("Подключи Android-смартфон и управляй им с компьютера")
        sub.setObjectName("muted")
        titles.addWidget(sub)
        head.addLayout(titles)
        head.addStretch()
        self.status = QLabel("● Проверка компонентов")
        self.status.setStyleSheet("color:#f2c96b;font-weight:700")
        head.addWidget(self.status)
        main.addLayout(head)

        panel = QFrame()
        panel.setObjectName("panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(20,18,20,18)
        h = QLabel("Подключение устройства")
        h.setObjectName("heading")
        pl.addWidget(h)
        pl.addWidget(QLabel("USB • Подключи кабель и разреши USB-отладку на телефоне"))
        row = QHBoxLayout()
        self.devices = QComboBox()
        self.devices.setMinimumWidth(250)
        row.addWidget(self.devices,1)
        refresh = QPushButton("Обновить устройства")
        refresh.clicked.connect(self.refresh_devices)
        row.addWidget(refresh)
        pl.addLayout(row)
        usb = QPushButton("Подключить по USB")
        usb.setObjectName("primary")
        usb.clicked.connect(self.connect_usb)
        pl.addWidget(usb)

        pl.addSpacing(8)
        pl.addWidget(QLabel("Wi-Fi • Телефон и компьютер должны быть в одной сети"))
        wifirow = QHBoxLayout()
        self.ip = QLineEdit()
        self.ip.setPlaceholderText("IP телефона, например 192.168.1.25")
        wifirow.addWidget(self.ip,1)
        wifi = QPushButton("Подключить по Wi-Fi")
        wifi.clicked.connect(self.connect_wifi)
        wifirow.addWidget(wifi)
        pl.addLayout(wifirow)
        main.addWidget(panel)

        grid = QGridLayout()
        grid.setSpacing(12)
        for i,(tag,heading,desc) in enumerate([
            ("ЗЕРКАЛИРОВАНИЕ","Экран телефона","Трансляция в отдельном окне scrcpy."),
            ("УПРАВЛЕНИЕ","Мышь и клавиатура","Ввод передаётся на Android через scrcpy."),
            ("ПОДКЛЮЧЕНИЕ","USB + Wi-Fi","Кабель или локальная беспроводная сеть."),
            ("ДАЛЬШЕ","Интерфейс DeX","Встраивание экрана и файловый обмен — следующие этапы.")
        ]):
            card = QFrame()
            card.setObjectName("panel")
            cl = QVBoxLayout(card)
            t = QLabel(tag)
            t.setStyleSheet("color:#8793ff;font-size:10px;font-weight:800")
            hh = QLabel(heading)
            hh.setStyleSheet("font-size:16px;font-weight:700")
            dd = QLabel(desc)
            dd.setObjectName("muted")
            dd.setWordWrap(True)
            cl.addWidget(t); cl.addWidget(hh); cl.addWidget(dd)
            grid.addWidget(card,i//2,i%2)
        main.addLayout(grid)

        logpanel = QFrame()
        logpanel.setObjectName("panel")
        ll = QVBoxLayout(logpanel)
        ll.addWidget(QLabel("Журнал"))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(250)
        self.log.setFixedHeight(110)
        ll.addWidget(self.log)
        main.addWidget(logpanel)
        self.write("BOUNTY Dex Prototype 0.1 запущен.")
        missing = []
        if not self.adb: missing.append("ADB")
        if not self.scrcpy: missing.append("scrcpy")
        if missing:
            self.status.setText("● Не найдены: " + ", ".join(missing))
            self.status.setStyleSheet("color:#ff8888;font-weight:700")
            self.write("Помести ADB в windows/tools/platform-tools/ и scrcpy вместе с DLL в windows/tools/scrcpy/.")
        else:
            self.status.setText("● Компоненты готовы")
            self.status.setStyleSheet("color:#79dfa6;font-weight:700")

    def write(self, text):
        self.log.appendPlainText(text)

    def adb_call(self, args):
        if not self.adb:
            raise RuntimeError("ADB не найден. См. инструкцию в bounty-dex/README.md.")
        p = subprocess.run([self.adb,*args],capture_output=True,text=True,timeout=15,
                           creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        result = (p.stdout or "") + (p.stderr or "")
        if p.returncode:
            raise RuntimeError(result.strip() or "Команда ADB завершилась с ошибкой.")
        return result.strip()

    def refresh_devices(self):
        self.devices.clear()
        if not self.adb:
            self.write("ADB не найден.")
            return
        try:
            output = self.adb_call(["devices"])
            found = []
            for line in output.splitlines()[1:]:
                parts = line.split()
                if len(parts) > 1 and parts[1] == "device":
                    found.append(parts[0])
            self.devices.addItems(found)
            self.write(f"Найдено устройств: {len(found)}")
            if not found:
                self.write("Проверь USB-отладку, кабель и подтверждение RSA на телефоне.")
        except Exception as exc:
            self.write("ADB: " + str(exc))

    def launch_scrcpy(self, serial=None):
        if not self.scrcpy:
            QMessageBox.warning(self,"Нет scrcpy","Распакуй полный архив scrcpy в windows/tools/scrcpy/.")
            return
        if self.process.state() != QProcess.NotRunning:
            self.write("Трансляция уже работает.")
            return
        args = (["-s",serial] if serial else []) + ["--window-title","BOUNTY Dex — Android"]
        self.process.setProgram(self.scrcpy)
        self.process.setArguments(args)
        self.process.start()
        if self.process.waitForStarted(3000):
            self.write("Окно зеркалирования запущено.")
        else:
            self.write("Не удалось запустить scrcpy: " + self.process.errorString())

    def connect_usb(self):
        serial = self.devices.currentText()
        if not serial:
            QMessageBox.information(self,"Нет устройства","Подключи телефон, включи USB-отладку, подтверди запрос на телефоне и обнови список.")
            return
        self.launch_scrcpy(serial)

    def connect_wifi(self):
        address = self.ip.text().strip()
        if not re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}",address):
            QMessageBox.warning(self,"IP-адрес","Введи локальный IP телефона, например 192.168.1.25.")
            return
        try:
            self.adb_call(["tcpip","5555"])
            result = self.adb_call(["connect",address + ":5555"])
            self.write(result)
            self.launch_scrcpy(address + ":5555")
        except Exception as exc:
            QMessageBox.warning(self,"Не удалось подключиться",str(exc) + "\nСначала подключи телефон по USB и подтверди отладку.")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BOUNTY Dex")
    window = BountyDex()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
