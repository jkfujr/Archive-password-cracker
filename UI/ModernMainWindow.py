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


class ModernCard(QFrame):
    """ui卡片组件"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)
        self.layout.setSpacing(10)
        
        if title:
            self.title_label = QLabel(title)
            self.layout.addWidget(self.title_label)


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
    START_CRACK = "开始破解"
    STOP_CRACK = "停止破解"
    START_EXPORT = "开始导出"
    STOP_EXPORT = "停止导出"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("压缩文件密码破解器")
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)
        
        # 设置窗口图标
        try:
            self.setWindowIcon(QIcon("res/icon.ico"))
        except:
            pass
        
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
        
        # 标题区域
        self.create_header(main_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        # 状态栏
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("就绪")

    def create_header(self, parent_layout):
        """创建标题区域"""
        header_card = ModernCard()
        header_layout = QHBoxLayout()
        header_card.layout.addLayout(header_layout)
        
        # 标题
        title_label = QLabel("🔐 压缩文件密码破解器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2196F3;
                margin: 10px 0;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 系统配置区域
        config_layout = QHBoxLayout()
        
        # CPU核心数配置
        cpu_label = QLabel("CPU核心:")
        cpu_label.setStyleSheet("font-weight: bold; color: #666;")
        config_layout.addWidget(cpu_label)
        
        self.core_num = QLCDNumber(2)
        self.core_num.setFixedSize(60, 30)
        self.core_num.display(cpu_count())  # 设置初始值
        config_layout.addWidget(self.core_num)
        
        self.cpu_slider = ModernSlider()
        self.cpu_slider.setMinimum(1)
        self.cpu_slider.setMaximum(cpu_count())
        self.cpu_slider.setValue(cpu_count())
        self.cpu_slider.setFixedWidth(120)
        config_layout.addWidget(self.cpu_slider)
        
        # 批量处理数配置
        batch_label = QLabel("批量处理:")
        batch_label.setStyleSheet("font-weight: bold; color: #666; margin-left: 20px;")
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
        self.batch_dial.setStyleSheet(self.cpu_slider.styleSheet())
        config_layout.addWidget(self.batch_dial)
        
        header_layout.addLayout(config_layout)
        parent_layout.addWidget(header_card)

    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(15)
        
        # 字典配置区域
        dict_card = ModernCard("📚 字典配置")
        
        # 字典源选择
        self.dict_source = QTabWidget()
        dict_card.layout.addWidget(self.dict_source)
        
        # 内置字典标签页
        internal_tab = QWidget()
        internal_layout = QVBoxLayout(internal_tab)
        internal_layout.setSpacing(15)
        
        # 字符集选择
        charset_group = QGroupBox("字符集选择")
        charset_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
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
        digit_group.setStyleSheet(charset_group.styleSheet())
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
        export_group.setStyleSheet(charset_group.styleSheet())
        export_layout = QVBoxLayout(export_group)
        
        path_layout = QHBoxLayout()
        self.export_path = QLineEdit()
        self.export_path.setPlaceholderText("选择字典导出路径...")
        path_layout.addWidget(self.export_path)
        
        self.button_export_path = ModernButton("浏览", "secondary")
        self.button_export_path.setFixedWidth(80)
        path_layout.addWidget(self.button_export_path)
        export_layout.addLayout(path_layout)
        
        export_control_layout = QHBoxLayout()
        self.button_export = ModernButton("开始导出", "primary")
        export_control_layout.addWidget(self.button_export)
        
        self.progress_export = ModernProgressBar()
        export_control_layout.addWidget(self.progress_export)
        export_layout.addLayout(export_control_layout)
        
        internal_layout.addWidget(export_group)
        
        self.dict_source.addTab(internal_tab, "内置字典")
        
        # 外部字典标签页
        external_tab = QWidget()
        external_layout = QVBoxLayout(external_tab)
        
        external_group = QGroupBox("自定义字典文件")
        external_group.setStyleSheet(charset_group.styleSheet())
        external_group_layout = QVBoxLayout(external_group)
        
        dict_path_layout = QHBoxLayout()
        self.dict_path = QLineEdit()
        self.dict_path.setPlaceholderText("选择自定义字典文件...")
        dict_path_layout.addWidget(self.dict_path)
        
        self.button_dict_path = ModernButton("浏览", "secondary")
        self.button_dict_path.setFixedWidth(80)
        dict_path_layout.addWidget(self.button_dict_path)
        
        external_group_layout.addLayout(dict_path_layout)
        external_layout.addWidget(external_group)
        external_layout.addStretch()
        
        self.dict_source.addTab(external_tab, "外部字典")
        
        left_layout.addWidget(dict_card)
        left_layout.addStretch()
        
        return left_widget

    def create_right_panel(self):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 破解配置区域
        crack_card = ModernCard("🔓 密码破解")
        
        # 文件选择区域
        file_group = QGroupBox("文件配置")
        file_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        file_layout = QVBoxLayout(file_group)
        
        # 压缩文件选择
        zip_layout = QHBoxLayout()
        zip_layout.addWidget(QLabel("压缩文件:"))
        self.zipfile_path = QLineEdit()
        self.zipfile_path.setPlaceholderText("选择要破解的压缩文件...")
        zip_layout.addWidget(self.zipfile_path)
        
        self.button_zipfile_path = ModernButton("浏览", "secondary")
        self.button_zipfile_path.setFixedWidth(80)
        zip_layout.addWidget(self.button_zipfile_path)
        file_layout.addLayout(zip_layout)
        
        # 解压路径选择
        extract_layout = QHBoxLayout()
        extract_layout.addWidget(QLabel("解压路径:"))
        self.extract_path = QLineEdit()
        self.extract_path.setPlaceholderText("选择解压输出路径...")
        extract_layout.addWidget(self.extract_path)
        
        self.button_extract_path = ModernButton("浏览", "secondary")
        self.button_extract_path.setFixedWidth(80)
        extract_layout.addWidget(self.button_extract_path)
        file_layout.addLayout(extract_layout)
        
        crack_card.layout.addWidget(file_group)
        
        # 破解控制区域
        control_group = QGroupBox("破解控制")
        control_group.setStyleSheet(file_group.styleSheet())
        control_layout = QVBoxLayout(control_group)
        
        # 破解按钮和进度
        crack_control_layout = QHBoxLayout()
        self.button_crack = ModernButton("开始破解", "primary")
        self.button_crack.setFixedWidth(120)
        crack_control_layout.addWidget(self.button_crack)
        
        self.progress_crack = ModernProgressBar()
        crack_control_layout.addWidget(self.progress_crack)
        control_layout.addLayout(crack_control_layout)
        
        # 结果显示
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("破解结果:"))
        self.password = QLineEdit()
        self.password.setReadOnly(True)
        self.password.setPlaceholderText("密码将在这里显示...")
        result_layout.addWidget(self.password)
        control_layout.addLayout(result_layout)
        
        crack_card.layout.addWidget(control_group)
        
        # 日志区域
        log_card = ModernCard("📋 运行日志")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        # 扩展日志区域
        self.log_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        log_card.layout.addWidget(self.log_text)

        # 使用垂直分割器，提高日志区可用空间
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(crack_card)
        splitter.addWidget(log_card)
        splitter.setSizes([400, 600])
        right_layout.addWidget(splitter)
        
        # 退出按钮
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        self.button_close = ModernButton("退出程序", "danger")
        self.button_close.setFixedWidth(120)
        exit_layout.addWidget(self.button_close)
        right_layout.addLayout(exit_layout)
        
        return right_widget

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
        self.button_export_path.clicked.connect(self.select_export_path)
        self.button_dict_path.clicked.connect(self.select_dict_path)
        self.button_zipfile_path.clicked.connect(self.select_zipfile_path)
        self.button_extract_path.clicked.connect(self.select_extract_path)
        
        # 功能按钮
        self.button_export.clicked.connect(self.on_export_dict)
        self.button_crack.clicked.connect(self.on_crack_password)
        self.button_close.clicked.connect(self.close)
        
        # 进度条变化
        self.progress_export.valueChanged.connect(self.on_export_progress_changed)
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
        export_path = self.export_path.text().strip()
        if not export_path:
            QMessageBox().warning(self, self.WARNING, self.SELECT_EXPORT_PATH, QMessageBox.Ok)
            return ""
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
    def select_export_path(self) -> str:
        """选择导出路径"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择字典导出路径", "", self.FILE_FILTER_TXT
        )
        if file_path:
            self.export_path.setText(file_path)
        return file_path

    @pyqtSlot()
    def on_export_dict(self):
        """导出字典"""
        if self.export_dict_thread is None or self.export_dict_thread.isFinished():
            seed_selection = self.get_seed_selection()
            digit_range = self.get_range()
            file_path = self.get_export_path()
            if file_path and any(seed_selection):
                self.export_dict_thread = ExportDict(
                    "export_dict", seed_selection, digit_range,
                    file_path, self.core_num.intValue(), self.batch_size.intValue()
                )
                self.progress_export.setMaximum(self.export_dict_thread.get_batch_count())
                self.export_dict_thread.consuming_passwords_num.connect(self.on_consuming_passwords_num)
                self.export_dict_thread.producing_password.connect(self.on_exporting_dict)
                self.export_dict_thread.consuming_passwords.connect(self.on_exporting_dict)
                self.export_dict_thread.start()
                self.button_export.setText(self.STOP_EXPORT)
                self.log_message("开始导出字典...")
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
        """破解密码状态更新"""
        self.statusbar.showMessage(passwords)
        self.log_message(passwords)
        
        if CrackPassword.CRACK_SUCCEED in passwords:
            password = passwords[len(CrackPassword.CRACK_SUCCEED):]
            self.password.setText(password)
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.log_message(f"破解成功！密码是: {password}")
            QMessageBox().information(self, self.INFO, passwords, QMessageBox.Ok)
        elif CrackPassword.NO_PASSWORD in passwords:
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.password.setText("空")
            self.log_message("破解成功！密码为空")
            QMessageBox().information(self, self.INFO, CrackPassword.NO_PASSWORD, QMessageBox.Ok)
        elif CrackPassword.CRACK_FAILED in passwords:
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.password.setText("")
            self.log_message("破解失败，未找到密码")
            QMessageBox().information(self, self.INFO, CrackPassword.CRACK_FAILED, QMessageBox.Ok)

    @pyqtSlot(int)
    def on_consuming_passwords_num(self, passwords_num: int):
        """消费密码数量更新"""
        self.progress_export.setValue(passwords_num)

    @pyqtSlot(int)
    def on_cracking_passwords_num(self, passwords_num: int):
        """破解密码数量更新"""
        self.progress_crack.setValue(passwords_num)

    @pyqtSlot(int)
    def on_export_progress_changed(self, progress: int):
        """导出进度变化"""
        if progress == self.progress_export.maximum():
            self.button_export.setText(self.START_EXPORT)
            if self.export_dict_thread:
                self.export_dict_thread.wait()
                self.export_dict_thread = None
            self.log_message("字典导出完成！")

    @pyqtSlot(int)
    def on_crack_progress_changed(self, progress: int):
        """破解进度变化"""
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
        """开始破解密码"""
        if self.password_cracker is None or self.password_cracker.isFinished():
            seed_selection = self.get_seed_selection()
            digit_range = self.get_range()
            consumer_number = self.core_num.intValue()
            batch_size = self.batch_size.intValue()
            dict_source = self.dict_source.currentIndex()
            zipfile_path = self.get_zipfile_path()
            extract_path = self.get_extract_path()
            
            # 根据字典源类型获取字典路径
            if dict_source == 0:  # 内置字典
                dict_path = ""  # 内置字典不需要路径
            else:  # 外部字典
                dict_path = self.get_dict_path()
                if not dict_path:  # 外部字典必须有路径
                    return
            
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
                if dict_source == 0:
                    self.log_message("开始使用内置字典破解密码...")
                else:
                    self.log_message("开始使用外部字典破解密码...")
        else:
            self.password_cracker.stop()
            self.button_crack.setText(self.START_CRACK)
            self.log_message("停止破解密码")


if __name__ == "__main__":
    app = QApplication(argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示窗口
    window = ModernMainWindow()
    
    exit(app.exec())