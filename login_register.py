# 导入必要的库
import json  # 用于处理JSON数据
import os  # 用于操作系统功能，如文件检查
import hashlib  # 用于密码加密
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTabWidget, QCheckBox,
                            QMessageBox, QGraphicsDropShadowEffect)  # 导入Qt部件用于创建GUI
from PyQt5.QtGui import QColor, QFont, QPalette, QBrush, QLinearGradient, QPixmap  # 导入Qt图形相关类
from PyQt5.QtCore import Qt, pyqtSignal  # 导入Qt核心类，包括信号

class LoginRegisterWidget(QWidget):
    # 定义信号
    login_successful = pyqtSignal(str)  # 创建登录成功信号，用于通知主程序
    
    def __init__(self):
        super().__init__()  # 调用父类初始化方法
        
        # 设置窗口属性
        self.setWindowTitle("商场视频监控异常行为检测系统 - 登录")  # 设置窗口标题
        self.setMinimumSize(500, 600)  # 设置窗口最小尺寸
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # 设置窗口标志，只显示关闭和最小化按钮
        
        # 设置背景渐变
        self.set_gradient_background()  # 调用方法设置渐变背景
        
        # 初始化用户数据
        self.user_data_file = "user_data.json"  # 设置用户数据文件名
        self.init_user_data()  # 调用初始化用户数据方法
        
        # 创建界面
        self.init_ui()  # 调用初始化界面方法
    
    def set_gradient_background(self):
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())  # 创建线性渐变对象
        gradient.setColorAt(0, QColor(25, 118, 210))  # 设置起始颜色
        gradient.setColorAt(1, QColor(66, 165, 245))  # 设置结束颜色
        
        palette = self.palette()  # 获取当前调色板
        palette.setBrush(QPalette.Window, QBrush(gradient))  # 设置窗口背景为渐变
        self.setPalette(palette)  # 应用调色板
        self.setAutoFillBackground(True)  # 启用自动填充背景
    
    def init_user_data(self):
        # 如果用户数据文件不存在，创建一个包含默认管理员账户的文件
        if not os.path.exists(self.user_data_file):  # 检查用户数据文件是否存在
            default_admin = {  # 创建默认管理员账户
                "admin": {
                    "password": self.hash_password("admin123"),  # 加密默认密码
                    "is_admin": True  # 设置为管理员
                }
            }
            with open(self.user_data_file, "w") as f:  # 打开文件进行写入
                json.dump(default_admin, f, indent=4)  # 写入默认管理员数据
    
    def hash_password(self, password):
        # 使用SHA-256加密密码
        return hashlib.sha256(password.encode()).hexdigest()  # 对密码进行加密并返回十六进制字符串
    
    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()  # 创建垂直布局
        main_layout.setContentsMargins(50, 50, 50, 50)  # 设置布局边距
        
        # 标题
        title_label = QLabel("商场视频监控异常行为检测系统")  # 创建标题标签
        title_label.setFont(QFont("Arial", 18, QFont.Bold))  # 设置字体
        title_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")  # 设置样式
        
        # 卡片式容器
        card_widget = QWidget()  # 创建卡片容器部件
        card_widget.setObjectName("card")  # 设置对象名称，用于CSS选择器
        card_widget.setStyleSheet("""
            #card {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 20px;
            }
        """)  # 设置卡片样式
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()  # 创建阴影效果
        shadow.setBlurRadius(20)  # 设置模糊半径
        shadow.setColor(QColor(0, 0, 0, 80))  # 设置阴影颜色和透明度
        shadow.setOffset(0, 0)  # 设置阴影偏移
        card_widget.setGraphicsEffect(shadow)  # 应用阴影效果
        
        card_layout = QVBoxLayout(card_widget)  # 创建卡片内部布局
        
        # 选项卡
        tab_widget = QTabWidget()  # 创建选项卡部件
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #e0e0e0;
                color: #555;
                padding: 8px 15px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3f87f5;
                color: white;
            }
        """)  # 设置选项卡样式
        
        # 登录选项卡
        login_tab = QWidget()  # 创建登录选项卡
        login_layout = QVBoxLayout(login_tab)  # 创建登录选项卡布局
        login_layout.setSpacing(15)  # 设置部件间距
        
        # 用户名输入
        username_label = QLabel("用户名:")  # 创建用户名标签
        username_label.setFont(QFont("Arial", 10))  # 设置字体
        self.login_username = QLineEdit()  # 创建用户名输入框
        self.login_username.setPlaceholderText("请输入用户名")  # 设置占位文本
        self.login_username.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3f87f5;
            }
        """)  # 设置输入框样式
        
        # 密码输入
        password_label = QLabel("密码:")  # 创建密码标签
        password_label.setFont(QFont("Arial", 10))  # 设置字体
        self.login_password = QLineEdit()  # 创建密码输入框
        self.login_password.setPlaceholderText("请输入密码")  # 设置占位文本
        self.login_password.setEchoMode(QLineEdit.Password)  # 设置为密码模式
        self.login_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3f87f5;
            }
        """)  # 设置输入框样式
        
        # 记住密码选项
        self.remember_checkbox = QCheckBox("记住密码")  # 创建复选框
        self.remember_checkbox.setFont(QFont("Arial", 10))  # 设置字体
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #555;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)  # 设置复选框样式
        
        # 登录按钮
        login_button = QPushButton("登录")  # 创建登录按钮
        login_button.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时为手型光标
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3f87f5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3978d8;
            }
            QPushButton:pressed {
                background-color: #2c5aa0;
            }
        """)  # 设置按钮样式
        login_button.clicked.connect(self.login)  # 连接点击事件到登录方法
        
        # 添加到登录布局
        login_layout.addWidget(username_label)  # 添加用户名标签
        login_layout.addWidget(self.login_username)  # 添加用户名输入框
        login_layout.addWidget(password_label)  # 添加密码标签
        login_layout.addWidget(self.login_password)  # 添加密码输入框
        login_layout.addWidget(self.remember_checkbox)  # 添加记住密码复选框
        login_layout.addWidget(login_button)  # 添加登录按钮
        login_layout.addStretch()  # 添加弹性空间
        
        # 注册选项卡
        register_tab = QWidget()  # 创建注册选项卡
        register_layout = QVBoxLayout(register_tab)  # 创建注册选项卡布局
        register_layout.setSpacing(15)  # 设置部件间距
        
        # 注册用户名
        reg_username_label = QLabel("用户名:")  # 创建用户名标签
        reg_username_label.setFont(QFont("Arial", 10))  # 设置字体
        self.reg_username = QLineEdit()  # 创建用户名输入框
        self.reg_username.setPlaceholderText("请输入用户名")  # 设置占位文本
        self.reg_username.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3f87f5;
            }
        """)  # 设置输入框样式
        
        # 注册密码
        reg_password_label = QLabel("密码:")  # 创建密码标签
        reg_password_label.setFont(QFont("Arial", 10))  # 设置字体
        self.reg_password = QLineEdit()  # 创建密码输入框
        self.reg_password.setPlaceholderText("请输入密码")  # 设置占位文本
        self.reg_password.setEchoMode(QLineEdit.Password)  # 设置为密码模式
        self.reg_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3f87f5;
            }
        """)  # 设置输入框样式
        
        # 确认密码
        confirm_password_label = QLabel("确认密码:")  # 创建确认密码标签
        confirm_password_label.setFont(QFont("Arial", 10))  # 设置字体
        self.confirm_password = QLineEdit()  # 创建确认密码输入框
        self.confirm_password.setPlaceholderText("请再次输入密码")  # 设置占位文本
        self.confirm_password.setEchoMode(QLineEdit.Password)  # 设置为密码模式
        self.confirm_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3f87f5;
            }
        """)  # 设置输入框样式
        
        # 注册按钮
        register_button = QPushButton("注册")  # 创建注册按钮
        register_button.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时为手型光标
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #3f87f5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3978d8;
            }
            QPushButton:pressed {
                background-color: #2c5aa0;
            }
        """)  # 设置按钮样式
        register_button.clicked.connect(self.register)  # 连接点击事件到注册方法
        
        # 添加到注册布局
        register_layout.addWidget(reg_username_label)  # 添加用户名标签
        register_layout.addWidget(self.reg_username)  # 添加用户名输入框
        register_layout.addWidget(reg_password_label)  # 添加密码标签
        register_layout.addWidget(self.reg_password)  # 添加密码输入框
        register_layout.addWidget(confirm_password_label)  # 添加确认密码标签
        register_layout.addWidget(self.confirm_password)  # 添加确认密码输入框
        register_layout.addWidget(register_button)  # 添加注册按钮
        register_layout.addStretch()  # 添加弹性空间
        
        # 添加选项卡
        tab_widget.addTab(login_tab, "登录")  # 添加登录选项卡
        tab_widget.addTab(register_tab, "注册")  # 添加注册选项卡
        
        # 添加到卡片布局
        card_layout.addWidget(tab_widget)  # 把选项卡添加到卡片布局
        
        # 添加到主布局
        main_layout.addWidget(title_label)  # 添加标题
        main_layout.addWidget(card_widget)  # 添加卡片容器
        main_layout.addStretch()  # 添加弹性空间
        
        # 版权信息
        copyright_label = QLabel("© 2025 商场视频监控异常行为检测系统")  # 创建版权标签
        copyright_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        copyright_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")  # 设置样式
        main_layout.addWidget(copyright_label)  # 添加版权标签
        
        # 设置布局
        self.setLayout(main_layout)  # 为窗口设置主布局
    
    def login(self):
        username = self.login_username.text()  # 获取用户名
        password = self.login_password.text()  # 获取密码
        
        if not username or not password:  # 检查是否有空字段
            QMessageBox.warning(self, "登录失败", "用户名和密码不能为空")  # 显示警告消息
            return
        
        # 检查用户是否存在
        with open(self.user_data_file, "r") as f:  # 打开用户数据文件
            user_data = json.load(f)  # 加载用户数据
        
        if username not in user_data:  # 检查用户名是否存在
            QMessageBox.warning(self, "登录失败", "用户名不存在")  # 显示警告消息
            return
        
        # 验证密码
        hashed_password = self.hash_password(password)  # 对输入的密码进行加密
        if user_data[username]["password"] != hashed_password:  # 比较密码是否匹配
            QMessageBox.warning(self, "登录失败", "密码错误")  # 显示警告消息
            return
        
        # 登录成功
        QMessageBox.information(self, "登录成功", f"欢迎回来, {username}!")  # 显示成功消息
        self.login_successful.emit(username)  # 发射登录成功信号，传递用户名
    
    def register(self):
        username = self.reg_username.text()  # 获取注册用户名
        password = self.reg_password.text()  # 获取注册密码
        confirm = self.confirm_password.text()  # 获取确认密码
        
        # 验证输入
        if not username or not password or not confirm:  # 检查是否有空字段
            QMessageBox.warning(self, "注册失败", "所有字段都必须填写")  # 显示警告消息
            return
        
        if password != confirm:  # 检查两次输入的密码是否一致
            QMessageBox.warning(self, "注册失败", "两次输入的密码不一致")  # 显示警告消息
            return
        
        # 检查用户名是否已存在
        with open(self.user_data_file, "r") as f:  # 打开用户数据文件
            user_data = json.load(f)  # 加载用户数据
        
        if username in user_data:  # 检查用户名是否已存在
            QMessageBox.warning(self, "注册失败", "用户名已存在")  # 显示警告消息
            return
        
        # 添加新用户
        user_data[username] = {
            "password": self.hash_password(password),  # 对密码进行加密
            "is_admin": False  # 设置为非管理员
        }
        
        with open(self.user_data_file, "w") as f:  # 打开用户数据文件用于写入
            json.dump(user_data, f, indent=4)  # 写入更新后的用户数据
        
        # 注册成功
        QMessageBox.information(self, "注册成功", "账户已创建，现在可以登录了")  # 显示成功消息
        
        # 清空表单并切换到登录选项卡
        self.reg_username.clear()  # 清空用户名输入框
        self.reg_password.clear()  # 清空密码输入框
        self.confirm_password.clear()  # 清空确认密码输入框
        tab_widget = self.findChild(QTabWidget)  # 查找选项卡部件
        tab_widget.setCurrentIndex(0)  # 切换到登录选项卡
    
    def resizeEvent(self, event):
        # 窗口大小改变时更新渐变
        self.set_gradient_background()  # 更新渐变背景
        super().resizeEvent(event)  # 调用父类的resizeEvent方法 