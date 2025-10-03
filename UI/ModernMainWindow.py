# -*- coding: utf-8 -*-
"""
主窗口
"""

from os import cpu_count
from sys import argv, exit
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QTabWidget, QCheckBox, QSpinBox, QLineEdit, QPushButton, 
    QToolButton, QProgressBar, QSlider, QLCDNumber, QLabel, QMessageBox, 
    QFileDialog, QFrame, QSplitter, QScrollArea, QSizePolicy, QSpacerItem,
    QButtonGroup, QRadioButton, QComboBox, QTextEdit, QStatusBar
)
from PyQt5.QtCore import Qt, pyqtSlot, QFileInfo, QDir, QTime, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter, QBrush, QLinearGradient
from ExportDict import ExportDict
from CrackPassword import CrackPassword

# 统一暗色主题下的组框样式（标题与边框融为一体）
UNIFIED_GROUPBOX_STYLE_DARK = """
    QGroupBox {
        font-weight: bold;
        font-size: 24px;    /* 提升区域标题字号 */
        color: #dddddd;
        border: 1px solid #666666;
        border-radius: 6px;
        margin-top: 12px;   /* 与标题融合需要顶部留白 */
        padding-top: 14px;  /* 与标题融合需要内边距 */
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 6px;
    }
"""


class ModernCard(QGroupBox):
    """统一风格的区域容器（标题与边框一体）"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(UNIFIED_GROUPBOX_STYLE_DARK)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 10, 12, 12)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)


class ModernButton(QPushButton):
    """ui按钮组件"""
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
    
    def apply_style(self):
        # 完全移除自定义样式，使用系统主题
        self.setStyleSheet("")


class ModernProgressBar(QProgressBar):
    """ui进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(8)
        # 使用系统默认样式
        self.setStyleSheet("")


class ModernSlider(QSlider):
    """ui滑块"""
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("")


class ModernMainWindow(QMainWindow):
    """ui主窗口类"""
    
    # 常量定义
    WARNING = "警告"
    INFO = "提示"
    SELECT_BOOLEAN = "请至少勾选一项"
    SELECT_EXPORT_PATH = "请选择字典导出路径"
    SELECT_ZIPFILE_PATH = "请选择压缩文件路径"
    SELECT_EXTRACT_PATH = "请选择解压路径"
    SELECT_DICT_PATH = "请选择字典路径"
    SUPPORTED_FILE_TYPES = ["zip", "rar", "7z"]
    UNSUPPORTED_FILE_TYPES = "不支持的文件格式，目前仅支持%s文件" % ', '.join(SUPPORTED_FILE_TYPES)
    EXPORT_COMPLETED = ExportDict.EXPORT_COMPLETED
    FILE_FILTER_TXT = "文本文件 (*.txt);;全部文件 (*)"
    FILE_FILTER_ZIP = "压缩文件 (*.zip;*.rar;*.7z);;ZIP压缩文件 (*.zip);;RAR压缩文件 (*.rar);;7Z压缩文件 (*.7z);;全部文件 (*)"
    START_CRACK = "开始遍历"
    STOP_CRACK = "停止遍历"
    START_EXPORT = "开始导出"
    STOP_EXPORT = "停止导出"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("压缩文件密码破解器")
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)
        
        # 初始化变量
        self.export_dict_thread = None
        self.password_cracker = None
        
        # 设置主题样式
        self.setup_theme()
        
        # 创建UI
        self.setup_ui()
        
        # 连接信号
        self.connect_signals()
        
        # 显示窗口
        self.show()

    def setup_theme(self):
        """设置主题样式"""
        # 不使用自定义样式，主题通过应用级暗色调色板统一控制
        self.setStyleSheet("")

    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 10)
        main_layout.setSpacing(20)
        
        # 顶部行：字典配置 + 密码破解（部件向上对齐）
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        # 设置面板大小策略，使其按内容高度并向上对齐
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        top_layout.addWidget(left_panel, 1, Qt.AlignTop)
        top_layout.addWidget(right_panel, 1, Qt.AlignTop)

        main_layout.addWidget(top_widget)

        # 底部行：运行日志
        log_widget = self.create_log_panel()
        main_layout.addWidget(log_widget)
        
        # 状态栏
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("就绪")

    def create_header(self, parent_layout):
        """已弃用：旧的标题区域（保留以兼容，但不再使用）"""
        pass

    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(15)
        
        # 字典配置区域（合并为单页）
        dict_card = ModernCard("字典配置")
        
        # 模式选择（自动 / 仅遍历 / 仅字典）
        mode_group = QGroupBox("模式选择")
        mode_group.setStyleSheet(UNIFIED_GROUPBOX_STYLE_DARK)
        mode_layout = QHBoxLayout(mode_group)

        self.radio_mode_auto = QRadioButton("自动（优先使用外部字典）")
        self.radio_mode_bruteforce = QRadioButton("仅遍历")
        self.radio_mode_dict = QRadioButton("仅字典")
        self.radio_mode_auto.setChecked(True)

        self.mode_buttons = QButtonGroup(self)
        self.mode_buttons.addButton(self.radio_mode_auto, 0)
        self.mode_buttons.addButton(self.radio_mode_bruteforce, 1)
        self.mode_buttons.addButton(self.radio_mode_dict, 2)

        mode_layout.addWidget(self.radio_mode_auto)
        mode_layout.addWidget(self.radio_mode_bruteforce)
        mode_layout.addWidget(self.radio_mode_dict)
        dict_card.layout.addWidget(mode_group)

        # 字符集与位数等内置遍历配置（原“内置字典”页内容）
        internal_layout = QVBoxLayout()
        internal_layout.setSpacing(15)
        
        # 字符集选择
        charset_group = QGroupBox("字符集选择")
        charset_group.setStyleSheet(UNIFIED_GROUPBOX_STYLE_DARK)
        charset_layout = QGridLayout(charset_group)
        
        self.checkBox_num = QCheckBox("数字 (0-9)")
        self.checkBox_num.setChecked(True)
        self.checkBox_lower_letter = QCheckBox("小写字母 (a-z)")
        self.checkBox_upper_letter = QCheckBox("大写字母 (A-Z)")
        self.checkBox_symbols = QCheckBox("特殊符号 (!@#$...)")
        
        charset_layout.addWidget(self.checkBox_num, 0, 0)
        charset_layout.addWidget(self.checkBox_lower_letter, 0, 1)
        charset_layout.addWidget(self.checkBox_upper_letter, 1, 0)
        charset_layout.addWidget(self.checkBox_symbols, 1, 1)
        
        internal_layout.addWidget(charset_group)
        
        # 位数设置
        digit_group = QGroupBox("密码位数")
        digit_group.setStyleSheet(UNIFIED_GROUPBOX_STYLE_DARK)
        digit_layout = QHBoxLayout(digit_group)
        
        digit_layout.addWidget(QLabel("最小位数:"))
        self.digit_min = QSpinBox()
        self.digit_min.setMinimum(1)
        self.digit_min.setMaximum(8)
        self.digit_min.setValue(1)
        digit_layout.addWidget(self.digit_min)
        
        digit_layout.addWidget(QLabel("最大位数:"))
        self.digit_max = QSpinBox()
        self.digit_max.setMinimum(1)
        self.digit_max.setMaximum(8)
        self.digit_max.setValue(4)
        digit_layout.addWidget(self.digit_max)
        
        internal_layout.addWidget(digit_group)
        
        # 导出字典区域
        export_group = QGroupBox("字典导出")
        export_group.setStyleSheet(UNIFIED_GROUPBOX_STYLE_DARK)
        export_layout = QVBoxLayout(export_group)
        
        # 只保留导出按钮
        export_control_layout = QHBoxLayout()
        self.button_export = ModernButton("字典导出", "primary")
        export_control_layout.addWidget(self.button_export)
        export_layout.addLayout(export_control_layout)
        
        internal_layout.addWidget(export_group)
        
        # 自定义字典文件（迁移到同一页，不分页）
        external_group = QGroupBox("自定义字典文件")
        external_group.setStyleSheet(UNIFIED_GROUPBOX_STYLE_DARK)
        external_group_layout = QVBoxLayout(external_group)
        
        dict_path_layout = QHBoxLayout()
        self.dict_path = QLineEdit()
        self.dict_path.setPlaceholderText("选择自定义字典文件...")
        dict_path_layout.addWidget(self.dict_path)
        
        self.button_dict_path = ModernButton("浏览", "secondary")
        self.button_dict_path.setFixedWidth(80)
        dict_path_layout.addWidget(self.button_dict_path)
        
        external_group_layout.addLayout(dict_path_layout)
        
        # 将内置配置与外部字典选择依次加入字典卡片
        dict_card.layout.addLayout(internal_layout)
        dict_card.layout.addWidget(external_group)
        
        left_layout.addWidget(dict_card)
        left_layout.addStretch()
        
        return left_widget

    def create_right_panel(self):
        """创建右侧面板（仅包含密码破解区域）"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(15)

        # 密码遍历配置区域
        crack_card = ModernCard("遍历配置")

        # 系统配置（从旧标题区域迁移到破解卡片顶部）
        config_layout = QHBoxLayout()
        cpu_label = QLabel("CPU核心:")
        config_layout.addWidget(cpu_label)

        self.core_num = QLCDNumber(2)
        self.core_num.setFixedSize(60, 30)
        self.core_num.display(cpu_count())
        config_layout.addWidget(self.core_num)

        self.cpu_slider = ModernSlider()
        self.cpu_slider.setMinimum(1)
        self.cpu_slider.setMaximum(cpu_count())
        self.cpu_slider.setValue(cpu_count())
        self.cpu_slider.setFixedWidth(120)
        config_layout.addWidget(self.cpu_slider)

        batch_label = QLabel("批量处理:")
        config_layout.addWidget(batch_label)

        self.batch_size = QLCDNumber(5)
        self.batch_size.setFixedSize(80, 30)
        self.batch_size.display(20000)
        config_layout.addWidget(self.batch_size)

        self.batch_dial = QSlider(Qt.Horizontal)
        self.batch_dial.setMinimum(1)
        self.batch_dial.setMaximum(20000)
        self.batch_dial.setValue(20000)
        self.batch_dial.setFixedWidth(120)
        config_layout.addWidget(self.batch_dial)

        crack_card.layout.addLayout(config_layout)
        
        # 文件选择区域（直接放入“密码遍历”卡片，不再嵌套分组）
        # 压缩文件选择
        zip_layout = QHBoxLayout()
        zip_layout.addWidget(QLabel("压缩文件:"))
        self.zipfile_path = QLineEdit()
        self.zipfile_path.setPlaceholderText("选择要遍历的压缩文件...")
        zip_layout.addWidget(self.zipfile_path)

        self.button_zipfile_path = ModernButton("浏览", "secondary")
        self.button_zipfile_path.setFixedWidth(80)
        zip_layout.addWidget(self.button_zipfile_path)
        crack_card.layout.addLayout(zip_layout)

        # 解压路径选择
        extract_layout = QHBoxLayout()
        extract_layout.addWidget(QLabel("解压路径:"))
        self.extract_path = QLineEdit()
        self.extract_path.setPlaceholderText("选择解压输出路径...")
        extract_layout.addWidget(self.extract_path)

        self.button_extract_path = ModernButton("浏览", "secondary")
        self.button_extract_path.setFixedWidth(80)
        extract_layout.addWidget(self.button_extract_path)
        crack_card.layout.addLayout(extract_layout)

        # 结果显示（并入卡片底部）
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("遍历结果:"))
        self.password = QLineEdit()
        self.password.setReadOnly(True)
        self.password.setPlaceholderText("密码将在这里显示...")
        result_layout.addWidget(self.password)
        crack_card.layout.addLayout(result_layout)

        # 将密码遍历卡片加入右侧面板
        right_layout.addWidget(crack_card)

        # 操作按钮占用整行，位于“密码遍历”列布局下方
        self.button_crack = ModernButton(self.START_CRACK, "primary")
        self.button_crack.setMinimumHeight(48)
        self.button_crack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right_layout.addWidget(self.button_crack)

        # 进度条放置在按钮下方，占用一行
        self.progress_crack = ModernProgressBar()
        right_layout.addWidget(self.progress_crack)
        return right_widget

    def create_log_panel(self):
        """创建底部日志面板（单独一行）"""
        log_card = ModernCard("📋 运行日志")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        log_card.layout.addWidget(self.log_text)
        return log_card

    def connect_signals(self):
        """连接信号和槽"""
        # CPU滑块连接
        self.cpu_slider.valueChanged.connect(self.core_num.display)
        
        # 批量处理滑块连接
        self.batch_dial.valueChanged.connect(self.batch_size.display)
        
        # 复选框验证
        self.checkBox_num.clicked.connect(self.validate_bool)
        self.checkBox_lower_letter.clicked.connect(self.validate_bool)
        self.checkBox_upper_letter.clicked.connect(self.validate_bool)
        self.checkBox_symbols.clicked.connect(self.validate_bool)
        
        # 文件选择按钮
        self.button_dict_path.clicked.connect(self.select_dict_path)
        self.button_zipfile_path.clicked.connect(self.select_zipfile_path)
        self.button_extract_path.clicked.connect(self.select_extract_path)
        
        # 功能按钮
        self.button_export.clicked.connect(self.on_export_dict)
        self.button_crack.clicked.connect(self.on_crack_password)
        
        # 进度条变化
        self.progress_crack.valueChanged.connect(self.on_crack_progress_changed)

    def log_message(self, message):
        """添加日志消息"""
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.log_text.append(f"[{current_time}] {message}")
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)

    # 以下是原有的功能方法，保持不变
    @pyqtSlot()
    def validate_bool(self) -> tuple:
        """验证复选框选择"""
        if not any(self.get_seed_selection()):
            QMessageBox().warning(self, self.WARNING, self.SELECT_BOOLEAN, QMessageBox.Ok)
            self.sender().setChecked(True)
        return self.get_seed_selection()

    def get_seed_selection(self) -> tuple:
        """获取种子选择"""
        return (
            self.checkBox_num.isChecked(),
            self.checkBox_lower_letter.isChecked(),
            self.checkBox_upper_letter.isChecked(),
            self.checkBox_symbols.isChecked()
        )

    def get_range(self) -> range:
        """获取位数范围"""
        return range(self.digit_min.value(), self.digit_max.value() + 1)

    @classmethod
    def check_supported_types(cls, zipfile_path: str) -> bool:
        """检查支持的文件类型"""
        for file_type in cls.SUPPORTED_FILE_TYPES:
            if zipfile_path.lower().endswith("." + file_type):
                return True
        return False

    def get_export_path(self) -> str:
        """获取导出路径"""
        export_path = "output\\字典导出"
        # 确保目录存在
        if not QDir(export_path).exists():
            QDir().mkpath(export_path)
        return export_path

    def get_extract_path(self) -> str:
        """获取解压路径"""
        extract_path = self.extract_path.text().strip()
        if not extract_path:
            QMessageBox().warning(self, self.WARNING, self.SELECT_EXTRACT_PATH, QMessageBox.Ok)
            return ""
        if not QDir(extract_path).exists():
            QDir().mkpath(extract_path)
        return extract_path

    def get_zipfile_path(self) -> str:
        """获取压缩文件路径"""
        zipfile_path = self.zipfile_path.text().strip()
        if not zipfile_path:
            QMessageBox().warning(self, self.WARNING, self.SELECT_ZIPFILE_PATH, QMessageBox.Ok)
            return ""
        if not QFileInfo(zipfile_path).exists():
            QMessageBox().warning(self, self.WARNING, "文件不存在", QMessageBox.Ok)
            return ""
        if not self.check_supported_types(zipfile_path):
            QMessageBox().warning(self, self.WARNING, self.UNSUPPORTED_FILE_TYPES, QMessageBox.Ok)
            return ""
        return zipfile_path

    def get_dict_path(self) -> str:
        """获取字典路径"""
        dict_path = self.dict_path.text().strip()
        if not dict_path:
            QMessageBox().warning(self, self.WARNING, self.SELECT_DICT_PATH, QMessageBox.Ok)
            return ""
        if not QFileInfo(dict_path).exists():
            QMessageBox().warning(self, self.WARNING, "字典文件不存在", QMessageBox.Ok)
            return ""
        return dict_path



    @pyqtSlot()
    def on_export_dict(self):
        """导出字典"""
        if self.export_dict_thread is None or self.export_dict_thread.isFinished():
            seed_selection = self.get_seed_selection()
            digit_range = self.get_range()
            export_dir = self.get_export_path()
            if export_dir and any(seed_selection):
                # 生成带时间戳的文件名
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                file_path = f"{export_dir}\\{timestamp}_字典导出.txt"
                
                self.export_dict_thread = ExportDict(
                    "export_dict", seed_selection, digit_range,
                    file_path, self.core_num.intValue(), self.batch_size.intValue()
                )
                self.export_dict_thread.producing_password.connect(self.on_exporting_dict)
                self.export_dict_thread.consuming_passwords.connect(self.on_exporting_dict)
                self.export_dict_thread.start()
                self.button_export.setText(self.STOP_EXPORT)
                self.log_message(f"开始导出字典到: {file_path}")
        else:
            self.export_dict_thread.stop()
            self.button_export.setText(self.START_EXPORT)
            self.log_message("停止导出字典")

    @pyqtSlot(str)
    def on_exporting_dict(self, password: str):
        """导出字典状态更新"""
        self.statusbar.showMessage(password)
        if password:
            self.log_message(password)

    @pyqtSlot(str)
    def on_cracking_passwords(self, passwords: str):
        """遍历密码状态更新"""
        self.statusbar.showMessage(passwords)
        self.log_message(passwords)
        
        if CrackPassword.CRACK_SUCCEED in passwords:
            password = passwords[len(CrackPassword.CRACK_SUCCEED):]
            self.password.setText(password)
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.log_message(f"遍历成功！找到密码: {password}")
            QMessageBox().information(self, self.INFO, passwords, QMessageBox.Ok)
        elif CrackPassword.NO_PASSWORD in passwords:
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.password.setText("空")
            self.log_message("遍历成功！密码为空")
            QMessageBox().information(self, self.INFO, CrackPassword.NO_PASSWORD, QMessageBox.Ok)
        elif CrackPassword.CRACK_FAILED in passwords:
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.password.setText("")
            self.log_message("遍历失败，未找到密码")
            QMessageBox().information(self, self.INFO, CrackPassword.CRACK_FAILED, QMessageBox.Ok)

    @pyqtSlot(int)
    def on_cracking_passwords_num(self, passwords_num: int):
        """遍历密码数量更新"""
        self.progress_crack.setValue(passwords_num)

    @pyqtSlot(int)
    def on_crack_progress_changed(self, progress: int):
        """遍历进度变化"""
        if progress == self.progress_crack.maximum():
            self.button_crack.setText(self.START_CRACK)
            if self.password_cracker:
                self.password_cracker.wait()
                self.password_cracker = None

    @pyqtSlot()
    def select_zipfile_path(self) -> str:
        """选择压缩文件路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择压缩文件", "", self.FILE_FILTER_ZIP
        )
        if file_path:
            self.zipfile_path.setText(file_path)
        return file_path

    @pyqtSlot()
    def select_extract_path(self) -> str:
        """选择解压路径"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择解压路径")
        if dir_path:
            self.extract_path.setText(dir_path)
        return dir_path

    @pyqtSlot()
    def select_dict_path(self) -> str:
        """选择字典路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择字典文件", "", self.FILE_FILTER_TXT
        )
        if file_path:
            self.dict_path.setText(file_path)
        return file_path

    @pyqtSlot()
    def on_crack_password(self):
        """开始遍历密码"""
        if self.password_cracker is None or self.password_cracker.isFinished():
            seed_selection = self.get_seed_selection()
            digit_range = self.get_range()
            consumer_number = self.core_num.intValue()
            batch_size = self.batch_size.intValue()
            # 根据模式选择决定字典来源
            mode_id = self.mode_buttons.checkedId()  # 0: 自动, 1: 仅遍历, 2: 仅字典
            dict_source = 0
            dict_path = ""
            if mode_id == 0:  # 自动（混合）：优先外部字典，否则按遍历
                candidate_path = self.dict_path.text().strip()
                if candidate_path and QFileInfo(candidate_path).exists():
                    dict_source = 1
                    dict_path = candidate_path
                else:
                    dict_source = 0
                    dict_path = ""
            elif mode_id == 1:  # 仅遍历
                dict_source = 0
                dict_path = ""
            elif mode_id == 2:  # 仅字典
                dict_source = 1
                dict_path = self.get_dict_path()
                if not dict_path:
                    # 未选择外部字典则直接提示并退出
                    return
            zipfile_path = self.get_zipfile_path()
            extract_path = self.get_extract_path()
            
            if zipfile_path and extract_path:
                self.password_cracker = CrackPassword(
                    "password_crack", seed_selection, digit_range,
                    dict_path, consumer_number, batch_size, dict_source,
                    zipfile_path, extract_path
                )
                self.progress_crack.setMaximum(self.password_cracker.get_batch_count() + 1)
                self.password_cracker.consuming_passwords_num.connect(self.on_cracking_passwords_num)
                self.password_cracker.producing_password.connect(self.on_cracking_passwords)
                self.password_cracker.consuming_passwords.connect(self.on_cracking_passwords)
                self.password_cracker.start()
                self.button_crack.setText(self.STOP_CRACK)
                if dict_source == 1:
                    if mode_id == 0:
                        self.log_message("自动模式：优先使用外部字典遍历密码...")
                    else:
                        self.log_message("开始使用外部字典遍历密码...")
                else:
                    if mode_id == 0:
                        self.log_message("自动模式：未选择外部字典，改用字符集遍历...")
                    else:
                        self.log_message("开始使用字符集遍历密码...")
        else:
            self.password_cracker.stop()
            self.button_crack.setText(self.START_CRACK)
            self.log_message("停止遍历密码")


if __name__ == "__main__":
    app = QApplication(argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示窗口
    window = ModernMainWindow()
    
    exit(app.exec())