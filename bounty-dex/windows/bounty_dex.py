import ipaddress
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QByteArray, QProcess, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QPlainTextEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QScrollArea, QInputDialog
)

# In a PyInstaller build, keep tools beside the EXE, not in the temporary bundle.
ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
ADB = str(ROOT / "tools" / "platform-tools" / "adb.exe")
SCRCPY = str(ROOT / "tools" / "scrcpy" / "scrcpy.exe")



SVG = {
 "refresh": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 7v5h-5M4 17v-5h5M5.6 9A7 7 0 0 1 18 6l2 6M4 12l2 6a7 7 0 0 0 12.4-3" fill="none" stroke="#dceaff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "usb": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 3v18m0-18 3 3m-3-3L9 6m3 15 4-3m-4 3-4-3M8 11H5V8m11 3h3V8" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "wifi": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 8.8a15 15 0 0 1 20 0M5 12a10 10 0 0 1 14 0m-11 3a6 6 0 0 1 8 0M12 19h.01" fill="none" stroke="#dceaff" stroke-width="1.8" stroke-linecap="round"/></svg>',
 "apps": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="2" fill="none" stroke="#dceaff" stroke-width="1.8"/><rect x="14" y="3" width="7" height="7" rx="2" fill="none" stroke="#dceaff" stroke-width="1.8"/><rect x="3" y="14" width="7" height="7" rx="2" fill="none" stroke="#dceaff" stroke-width="1.8"/><rect x="14" y="14" width="7" height="7" rx="2" fill="none" stroke="#dceaff" stroke-width="1.8"/></svg>',
 "launch": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="m8 5 11 7-11 7z" fill="none" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"/></svg>'
}
def make_svg_icon(source, size=18):
    renderer = QSvgRenderer(QByteArray(source.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

def find_tool(local_path, command_name):
    return local_path if Path(local_path).is_file() else shutil.which(command_name)


class BountyDex(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BOUNTY Dex")
        self.resize(1160, 820)
        self.setMinimumSize(900, 680)
        self.adb = find_tool(ADB, "adb")
        self.scrcpy = find_tool(SCRCPY, "scrcpy")
        self.process = QProcess(self)
        self.apps_data = []
        self.build_ui()
        self.refresh_devices()

    def build_ui(self):
        self.setStyleSheet("""
          QWidget { background:#0d0f14; color:#f5f5f7; font-family:'Segoe UI'; font-size:13px; }
          QFrame#panel { background:#171a22; border:1px solid #292e3a; border-radius:18px; }
          QLabel#brand { font-size:25px; font-weight:800; letter-spacing:-1px; }
          QLabel#muted { color:#a0a5b2; }
          QLabel#heading { font-size:20px; font-weight:700; }
          QPushButton { background:#252a35; color:#f5f5f7; border:1px solid #343b4a; border-radius:11px; padding:10px 14px; font-weight:600; }
          QPushButton:hover { background:#303747; }
          QPushButton#primary { background:#0a84ff; color:white; border:0; }
          QPushButton#primary:hover { background:#2997ff; }
          QLineEdit,QComboBox { background:#10141c; border:1px solid #343b4a; border-radius:10px; padding:10px; color:#f5f5f7; selection-background-color:#0a84ff; }
          QListWidget { background:#10141c; border:1px solid #292e3a; border-radius:12px; padding:6px; outline:0; }
          QListWidget::item { padding:8px 10px; border-radius:8px; }
          QListWidget::item:selected { background:#173b60; color:white; }
          QListWidget::item:hover { background:#202a38; }
          QPlainTextEdit { background:#10141c; border:1px solid #292e3a; border-radius:11px; padding:8px; color:#bdc6d6; }
        """)

        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(16)

        sidebar = QFrame()
        sidebar.setObjectName("panel")
        sidebar.setFixedWidth(215)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(17, 20, 17, 18)
        brand = QLabel("BOUNTY <span style='color:#0a84ff'>Dex</span>")
        brand.setObjectName("brand")
        sl.addWidget(brand)
        caption = QLabel("ANDROID DESKTOP")
        caption.setObjectName("muted")
        sl.addWidget(caption)
        sl.addSpacing(25)
        for item in ("⌂  Рабочий стол", "▦  Приложения", "◉  Подключение", "⚙  Настройки"):
            b = QPushButton(item)
            b.setStyleSheet("text-align:left; padding:12px; background:transparent; border:0;")
            sl.addWidget(b)
        sl.addStretch()
        note = QLabel("Тёмная тема\nPrototype 0.2")
        note.setObjectName("muted")
        sl.addWidget(note)
        outer.addWidget(sidebar)

        main = QVBoxLayout()
        main.setSpacing(12)
        outer.addLayout(main, 1)

        head = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Рабочее пространство")
        title.setObjectName("heading")
        titles.addWidget(title)
        sub = QLabel("Подключай телефон, открывай приложения и управляй ими с ПК.")
        sub.setObjectName("muted")
        titles.addWidget(sub)
        head.addLayout(titles)
        head.addStretch()
        guide_button = QPushButton("Как пользоваться")
        guide_button.setIcon(make_svg_icon(SVG["apps"]))
        guide_button.clicked.connect(self.show_guide)
        head.addWidget(guide_button)
        self.status = QLabel("● Проверка компонентов")
        self.status.setStyleSheet("color:#f5c451;font-weight:700")
        head.addWidget(self.status)
        main.addLayout(head)

        connect_panel = QFrame()
        connect_panel.setObjectName("panel")
        pl = QVBoxLayout(connect_panel)
        pl.setContentsMargins(17, 15, 17, 15)
        h = QLabel("Подключение устройства")
        h.setObjectName("heading")
        pl.addWidget(h)
        hint = QLabel("USB • Подключи кабель и подтверди USB-отладку на телефоне.")
        hint.setObjectName("muted")
        pl.addWidget(hint)

        row = QHBoxLayout()
        self.devices = QComboBox()
        self.devices.setMinimumWidth(220)
        row.addWidget(self.devices, 1)
        refresh = QPushButton("Обновить")
        refresh.setIcon(make_svg_icon(SVG["refresh"]))
        refresh.clicked.connect(self.refresh_devices)
        row.addWidget(refresh)
        usb = QPushButton("Зеркалировать USB")
        usb.setIcon(make_svg_icon(SVG["usb"]))
        usb.setObjectName("primary")
        usb.clicked.connect(self.connect_usb)
        row.addWidget(usb)
        pl.addLayout(row)

        wifirow = QHBoxLayout()
        self.ip = QLineEdit()
        self.ip.setPlaceholderText("IP телефона, например 192.168.1.25")
        wifirow.addWidget(self.ip, 1)
        wifi = QPushButton("Подключить по Wi-Fi")
        wifi.setIcon(make_svg_icon(SVG["wifi"]))
        wifi.clicked.connect(self.connect_wifi)
        wifirow.addWidget(wifi)
        pl.addLayout(wifirow)

        pairrow = QHBoxLayout()
        self.pair_address = QLineEdit()
        self.pair_address.setPlaceholderText("Wireless debugging: IP:порт сопряжения")
        pairrow.addWidget(self.pair_address, 1)
        self.pair_code = QLineEdit()
        self.pair_code.setPlaceholderText("Код сопряжения")
        self.pair_code.setMaximumWidth(150)
        pairrow.addWidget(self.pair_code)
        pair = QPushButton("Сопрячь Wi-Fi")
        pair.setIcon(make_svg_icon(SVG["wifi"]))
        pair.clicked.connect(self.pair_wifi)
        pairrow.addWidget(pair)
        pl.addLayout(pairrow)

        streamrow = QHBoxLayout()
        streamrow.addWidget(QLabel("Ориентация"))
        self.orientation = QComboBox()
        self.orientation.addItem("Горизонтально →", "90")
        self.orientation.addItem("Горизонтально ←", "270")
        self.orientation.addItem("Как на телефоне", "0")
        self.orientation.addItem("Перевёрнуто", "180")
        streamrow.addWidget(self.orientation, 1)
        streamrow.addWidget(QLabel("Размер"))
        self.stream_size = QComboBox()
        self.stream_size.addItem("Экономно · 720p", "720")
        self.stream_size.addItem("Сбалансировано · 1280p", "1280")
        self.stream_size.addItem("Чётко · 1600p", "1600")
        self.stream_size.addItem("Максимум · 1920p", "1920")
        streamrow.addWidget(self.stream_size, 1)
        streamrow.addWidget(QLabel("FPS"))
        self.stream_fps = QComboBox()
        self.stream_fps.addItem("30 FPS", "30")
        self.stream_fps.addItem("45 FPS", "45")
        self.stream_fps.addItem("60 FPS", "60")
        streamrow.addWidget(self.stream_fps)
        pl.addLayout(streamrow)
        stream_hint = QLabel("Трансляция экрана телефона на ПК в реальном времени. Размер сохраняет пропорции экрана.")
        stream_hint.setObjectName("muted")
        stream_hint.setWordWrap(True)
        pl.addWidget(stream_hint)
        main.addWidget(connect_panel)

        apps_panel = QFrame()
        apps_panel.setObjectName("panel")
        al = QVBoxLayout(apps_panel)
        al.setContentsMargins(17, 15, 17, 15)
        apps_head = QHBoxLayout()
        apps_title = QLabel("Приложения Android")
        apps_title.setObjectName("heading")
        apps_head.addWidget(apps_title)
        apps_head.addStretch()
        self.apps_count = QLabel("Телефон не подключён")
        self.apps_count.setObjectName("muted")
        apps_head.addWidget(self.apps_count)
        al.addLayout(apps_head)

        searchrow = QHBoxLayout()
        self.app_filter = QLineEdit()
        self.app_filter.setPlaceholderText("Поиск приложения или пакета…")
        self.app_filter.textChanged.connect(self.filter_apps)
        searchrow.addWidget(self.app_filter, 1)
        app_refresh = QPushButton("Загрузить все")
        app_refresh.setIcon(make_svg_icon(SVG["refresh"]))
        app_refresh.clicked.connect(self.load_apps)
        searchrow.addWidget(app_refresh)
        al.addLayout(searchrow)

        self.app_list = QListWidget()
        self.app_list.setMinimumHeight(145)
        self.app_list.setMaximumHeight(205)
        self.app_list.itemDoubleClicked.connect(lambda _item: self.launch_selected_app())
        al.addWidget(self.app_list)

        app_actions = QHBoxLayout()
        app_note = QLabel("Показываются приложения с иконкой запуска, включая системные.")
        app_note.setObjectName("muted")
        app_actions.addWidget(app_note, 1)
        launch = QPushButton("Открыть приложение")
        launch.setIcon(make_svg_icon(SVG["launch"]))
        launch.setObjectName("primary")
        launch.clicked.connect(self.launch_selected_app)
        app_actions.addWidget(launch)
        al.addLayout(app_actions)
        main.addWidget(apps_panel)

        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (tag, heading, desc) in enumerate([
            ("ЭКРАН", "Зеркалирование", "Экран Android открывается в окне scrcpy."),
            ("УПРАВЛЕНИЕ", "Мышь и клавиатура", "Ввод передаётся на телефон через scrcpy."),
            ("СВЯЗЬ", "USB и Wi-Fi", "Кабель или локальная беспроводная сеть."),
            ("ПРИЛОЖЕНИЯ", "Каталог телефона", "Ищи и запускай доступные Android-приложения.")
        ]):
            card = QFrame()
            card.setObjectName("panel")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(13, 12, 13, 12)
            tag_label = QLabel(tag)
            tag_label.setStyleSheet("color:#62aaff;font-size:10px;font-weight:800")
            hh = QLabel(heading)
            hh.setStyleSheet("font-size:15px;font-weight:700")
            dd = QLabel(desc)
            dd.setObjectName("muted")
            dd.setWordWrap(True)
            cl.addWidget(tag_label)
            cl.addWidget(hh)
            cl.addWidget(dd)
            grid.addWidget(card, i // 2, i % 2)
        main.addLayout(grid)

        log_panel = QFrame()
        log_panel.setObjectName("panel")
        ll = QVBoxLayout(log_panel)
        ll.setContentsMargins(14, 10, 14, 10)
        ll.addWidget(QLabel("Журнал"))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(200)
        self.log.setFixedHeight(72)
        ll.addWidget(self.log)
        main.addWidget(log_panel)

        self.write("BOUNTY Dex 0.3 запущен.")
        missing = []
        if not self.adb:
            missing.append("ADB")
        if not self.scrcpy:
            missing.append("scrcpy")
        if missing:
            self.status.setText("● Не найдены: " + ", ".join(missing))
            self.status.setStyleSheet("color:#ff7777;font-weight:700")
            self.write("Проверь tools/platform-tools/ и tools/scrcpy/ рядом с приложением.")
        else:
            self.status.setText("● Компоненты готовы")
            self.status.setStyleSheet("color:#65d69a;font-weight:700")


    def show_guide(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("BOUNTY Dex — инструкция")
        dialog.resize(760, 690)
        dialog.setMinimumSize(620, 520)
        dialog.setStyleSheet("QDialog{background:#0d0f14;color:#f5f5f7;} QLabel{color:#f5f5f7;} QLabel#muted{color:#a0a5b2;} QFrame#guideCard{background:#171a22;border:1px solid #292e3a;border-radius:16px;} QScrollArea{border:0;background:transparent;}")
        outer = QVBoxLayout(dialog)
        title = QLabel("Подключи Samsung к компьютеру")
        title.setStyleSheet("font-size:22px;font-weight:800")
        outer.addWidget(title)
        intro = QLabel("Иллюстрированная инструкция для первого запуска BOUNTY Dex.")
        intro.setObjectName("muted")
        outer.addWidget(intro)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(12)

        def add_step(number, heading, description, art):
            card = QFrame()
            card.setObjectName("guideCard")
            row = QHBoxLayout(card)
            row.setContentsMargins(14, 12, 14, 12)
            illustration = QSvgWidget()
            illustration.load(QByteArray(art.encode("utf-8")))
            illustration.setFixedSize(116, 100)
            row.addWidget(illustration)
            text_col = QVBoxLayout()
            h = QLabel(f"{number}. {heading}")
            h.setStyleSheet("font-size:15px;font-weight:750")
            p = QLabel(description)
            p.setObjectName("muted")
            p.setWordWrap(True)
            text_col.addWidget(h)
            text_col.addWidget(p)
            text_col.addStretch()
            row.addLayout(text_col, 1)
            column.addWidget(card)

        phone = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 116 100"><rect x="35" y="3" width="46" height="94" rx="9" fill="#26364c" stroke="#8ba6c7"/><rect x="40" y="12" width="36" height="74" rx="4" fill="#101824"/><rect x="45" y="22" width="26" height="6" rx="2" fill="#0a84ff"/><rect x="45" y="35" width="26" height="4" rx="2" fill="#637b99"/><rect x="45" y="44" width="26" height="4" rx="2" fill="#637b99"/><circle cx="58" cy="91" r="2" fill="#91a4bc"/></svg>'
        taps = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 116 100"><rect x="12" y="12" width="92" height="76" rx="9" fill="#182538" stroke="#536b88"/><text x="23" y="32" fill="#9db2cc" font-size="8">Номер сборки</text><rect x="20" y="40" width="76" height="30" rx="6" fill="#24466a"/><text x="58" y="59" text-anchor="middle" fill="#fff" font-size="11" font-weight="bold">7 ×</text></svg>'
        usb = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 116 100"><path d="M58 12v67m0-67 9 9m-9-9-9 9m9 58 13-12m-13 12L45 67M45 44H29V29" fill="none" stroke="#82bfff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><rect x="20" y="18" width="15" height="15" rx="4" fill="#0a84ff"/><circle cx="58" cy="83" r="5" fill="#0a84ff"/></svg>'
        pc = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 116 100"><rect x="5" y="13" width="106" height="66" rx="7" fill="#26364c" stroke="#8ba6c7"/><rect x="11" y="19" width="94" height="54" rx="3" fill="#0d1522"/><rect x="18" y="27" width="80" height="9" rx="3" fill="#1b3653"/><rect x="18" y="42" width="35" height="23" rx="4" fill="#0a84ff"/><rect x="59" y="42" width="39" height="23" rx="4" fill="#25364b"/><path d="M43 80h30l7 7H36z" fill="#667a94"/></svg>'
        add_step(1, "Открой параметры телефона", "Настройки → Сведения о телефоне → Сведения о ПО.", phone)
        add_step(2, "Включи режим разработчика", "Найди «Номер сборки» и нажми на него 7 раз. При необходимости введи PIN-код.", taps)
        add_step(3, "Разреши USB-отладку", "Параметры разработчика → USB-отладка. Подключи кабель и подтверди запрос на экране телефона.", usb)
        add_step(4, "Запусти трансляцию", "В BOUNTY Dex нажми «Обновить», выбери Samsung и нажми «Зеркалировать USB». Экран телефона появится на ПК в отдельном окне; мышь и клавиатура будут управлять телефоном.", pc)
        wifi_note = QLabel("<b>Горизонтальный экран:</b> перед подключением выбери «Горизонтально →» или «Горизонтально ←». Если приложение на телефоне само не поддерживает альбомный режим, поворот картинки на ПК не заставит его перестроить интерфейс. Для переключения ориентации самого телефона в окне scrcpy нажми Alt+R. <br><br><b>Размер:</b> 720p/1280p/1600p/1920p уменьшают или повышают разрешение потока, сохраняя пропорции. Для слабого ПК начни с 720p и 30 FPS.")
        wifi_note.setWordWrap(True)
        wifi_note.setStyleSheet("background:#17263a;border:1px solid #2d4b6d;border-radius:12px;padding:13px;color:#dceaff;")
        column.addWidget(wifi_note)
        wifi_note = QLabel("<b>Wi-Fi:</b> телефон и ПК должны быть в одной сети. Сначала подключи USB, затем введи IP телефона в поле Wi-Fi. На Android 16 / One UI 8.5 используй «Беспроводная отладка» → «Сопряжение с кодом», затем введи отдельный основной порт подключения.")
        wifi_note.setWordWrap(True)
        wifi_note.setStyleSheet("background:#17263a;border:1px solid #2d4b6d;border-radius:12px;padding:13px;color:#dceaff;")
        column.addWidget(wifi_note)
        note = QLabel("<b>Важно:</b> для зеркалирования нужны ADB и полный пакет scrcpy в папках tools/platform-tools и tools/scrcpy рядом с EXE. APK на телефоне — помощник с инструкциями; трансляцию выполняет программа Windows.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        column.addWidget(note)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
        close = QPushButton("Понятно")
        close.setObjectName("primary")
        close.clicked.connect(dialog.accept)
        outer.addWidget(close)
        dialog.exec()

    def write(self, message):
        self.log.appendPlainText(str(message))

    def adb_call(self, args, serial=None, timeout=25):
        if not self.adb:
            raise RuntimeError("ADB не найден. Проверь папку tools/platform-tools.")
        command = [self.adb]
        if serial:
            command.extend(["-s", serial])
        command.extend(args)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        if result.returncode != 0:
            raise RuntimeError(output or "Команда ADB завершилась с ошибкой.")
        return output

    def refresh_devices(self):
        self.devices.clear()
        self.app_list.clear()
        self.apps_data = []
        self.apps_count.setText("Поиск устройств…")
        if not self.adb:
            self.apps_count.setText("ADB не найден")
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
            self.write("Найдено подключённых устройств: " + str(len(found)))
            if found:
                self.load_apps()
            else:
                self.apps_count.setText("Телефон не подключён")
                self.write("Проверь USB-отладку, кабель или ADB по Wi-Fi.")
        except Exception as exc:
            self.apps_count.setText("Ошибка ADB")
            self.write("ADB: " + str(exc))

    def load_apps(self):
        serial = self.devices.currentText().strip()
        if not serial:
            self.apps_count.setText("Сначала подключи телефон")
            return
        self.app_list.clear()
        self.apps_data = []
        self.apps_count.setText("Загрузка…")
        try:
            # Query MAIN/LAUNCHER activities so the list contains apps the user can open,
            # including preinstalled/system apps, not just third-party packages.
            try:
                output = self.adb_call([
                    "shell", "cmd", "package", "query-activities", "--brief",
                    "-a", "android.intent.action.MAIN",
                    "-c", "android.intent.category.LAUNCHER"
                ], serial=serial, timeout=45)
                packages = sorted(set(re.findall(
                    r"^([A-Za-z0-9_.$]+)/[^\s]+$", output, flags=re.MULTILINE
                )))
                if not packages:
                    raise RuntimeError("Команда не вернула список приложений.")
            except Exception:
                # Older Android builds may not support query-activities.
                output = self.adb_call(["shell", "pm", "list", "packages"], serial=serial, timeout=45)
                packages = sorted(set(re.findall(r"^package:([^\s]+)$", output, flags=re.MULTILINE)))
            self.apps_data = packages
            for package_name in packages:
                short_name = package_name.rsplit(".", 1)[-1].replace("_", " ").replace("$", " ").strip()
                display_name = short_name[:1].upper() + short_name[1:] if short_name else package_name
                item = QListWidgetItem("◈  " + display_name)
                item.setData(Qt.UserRole, package_name)
                item.setToolTip(package_name)
                self.app_list.addItem(item)
            self.apps_count.setText(str(len(packages)) + " приложений")
            self.filter_apps(self.app_filter.text())
            self.write("Загружено Android-приложений: " + str(len(packages)))
        except Exception as exc:
            self.apps_count.setText("Не удалось загрузить")
            self.write("Ошибка списка приложений: " + str(exc))
            QMessageBox.warning(
                self, "Список приложений",
                "Не удалось получить список приложений телефона.\n\n" + str(exc)
            )

    def filter_apps(self, query):
        needle = query.strip().casefold()
        for index in range(self.app_list.count()):
            item = self.app_list.item(index)
            package_name = item.data(Qt.UserRole) or ""
            item.setHidden(needle not in item.text().casefold() and needle not in package_name.casefold())

    def launch_selected_app(self):
        serial = self.devices.currentText().strip()
        item = self.app_list.currentItem()
        if not serial:
            QMessageBox.information(self, "Нет телефона", "Сначала подключи Android-телефон.")
            return
        if item is None:
            QMessageBox.information(self, "Приложение не выбрано", "Выбери приложение в списке.")
            return
        package_name = item.data(Qt.UserRole)
        try:
            output = self.adb_call([
                "shell", "monkey", "-p", package_name,
                "-c", "android.intent.category.LAUNCHER", "1"
            ], serial=serial)
            if "No activities found" in output or "monkey aborted" in output.lower():
                raise RuntimeError("У этого пакета нет доступного экрана запуска.")
            self.write("Запущено приложение: " + package_name)
        except Exception as exc:
            self.write("Не удалось открыть " + package_name + ": " + str(exc))
            QMessageBox.warning(self, "Не удалось открыть приложение", str(exc))

    def launch_scrcpy(self, serial=None):
        if not self.scrcpy:
            QMessageBox.warning(
                self, "Нет scrcpy",
                "Распакуй полный архив scrcpy в tools/scrcpy рядом с приложением."
            )
            return
        if self.process.state() != QProcess.NotRunning:
            self.write("Окно зеркалирования уже запущено.")
            return
        # Orientation rotates the mirrored picture on the PC; it does not
        # force every Android app to support landscape mode.
        orientation = self.orientation.currentData() if hasattr(self, "orientation") else "90"
        max_size = self.stream_size.currentData() if hasattr(self, "stream_size") else "1280"
        max_fps = self.stream_fps.currentData() if hasattr(self, "stream_fps") else "30"
        args = (["-s", serial] if serial else []) + [
            "--window-title", "BOUNTY Dex — Android",
            "--orientation=" + str(orientation),
            "--max-size=" + str(max_size),
            "--max-fps=" + str(max_fps),
            "--stay-awake",
            "--clipboard-autosync"
        ]
        self.process.setProgram(self.scrcpy)
        self.process.setArguments(args)
        self.process.start()
        if self.process.waitForStarted(3000):
            self.write("Трансляция экрана запущена: ориентация " + str(orientation) + "°, до " + str(max_size) + " px, " + str(max_fps) + " FPS.")
        else:
            self.write("Не удалось запустить scrcpy: " + self.process.errorString())

    def connect_usb(self):
        serial = self.devices.currentText().strip()
        if not serial:
            QMessageBox.information(
                self, "Нет устройства",
                "Подключи телефон, включи USB-отладку, подтверди запрос на телефоне и обнови список."
            )
            return
        self.launch_scrcpy(serial)

    def pair_wifi(self):
        endpoint = self.pair_address.text().strip()
        code = self.pair_code.text().strip()
        if not re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}", endpoint):
            QMessageBox.warning(self, "Адрес сопряжения", "Введи адрес и порт из экрана «Беспроводная отладка», например 192.168.1.25:37123.")
            return
        try:
            host, port_text = endpoint.rsplit(":", 1)
            ipaddress.IPv4Address(host)
            port = int(port_text)
            if not 1 <= port <= 65535:
                raise ValueError("Порт должен быть от 1 до 65535.")
            if not re.fullmatch(r"\d{6}", code):
                raise ValueError("Код сопряжения должен состоять из 6 цифр.")
            result = self.adb_call(["pair", endpoint, code], timeout=35)
            self.write(result)
            if "successfully paired" not in result.lower():
                raise RuntimeError(result or "ADB не подтвердил сопряжение.")
            # Clear the USB selection so connect_wifi asks for the dynamic
            # Wireless debugging port instead of switching the phone to tcpip:5555.
            self.devices.setCurrentIndex(-1)
            QMessageBox.information(self, "Сопряжение выполнено", "Теперь посмотри в настройках «Беспроводная отладка» основной IP:порт подключения (это другой порт, не порт сопряжения). Введи IP выше и нажми «Подключить по Wi-Fi», затем введи основной порт.")
        except Exception as exc:
            self.write("Ошибка сопряжения Wi-Fi: " + str(exc))
            QMessageBox.warning(self, "Не удалось выполнить сопряжение", str(exc))

    def connect_wifi(self):
        address = self.ip.text().strip()
        try:
            address = str(ipaddress.IPv4Address(address))
        except ipaddress.AddressValueError:
            QMessageBox.warning(
                self, "IP-адрес",
                "Введи корректный IPv4-адрес телефона, например 192.168.1.25."
            )
            return

        try:
            selected = self.devices.currentText().strip()
            if selected and ":" not in selected:
                # USB path: switch the authorized device to ADB TCP/IP.
                self.adb_call(["tcpip", "5555"], serial=selected)
                port = 5555
            else:
                port_text, ok = QInputDialog.getText(
                    self, "Порт Wi-Fi ADB",
                    "Введи основной порт из экрана «Беспроводная отладка» (не порт сопряжения):",
                    text="5555"
                )
                if not ok:
                    return
                port = int(port_text)
                if not 1 <= port <= 65535:
                    raise ValueError("Порт должен быть от 1 до 65535.")
            wifi_serial = address + ":" + str(port)
            result = self.adb_call(["connect", wifi_serial])
            self.write(result)
            self.refresh_devices()
            index = self.devices.findText(wifi_serial)
            if index >= 0:
                self.devices.setCurrentIndex(index)
                self.load_apps()
                self.launch_scrcpy(wifi_serial)
            else:
                QMessageBox.warning(
                    self, "Устройство не найдено",
                    "ADB не добавил Wi-Fi-устройство в список. Проверь IP, порт и что телефон и ПК в одной сети."
                )
        except Exception as exc:
            QMessageBox.warning(
                self, "Не удалось подключиться",
                str(exc) + "\nДля Android 11+ сначала используй «Беспроводная отладка» → «Сопряжение с кодом»."
            )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BOUNTY Dex")
    window = BountyDex()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
