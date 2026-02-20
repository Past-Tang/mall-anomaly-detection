# 导入必要的库
import sys  # 导入系统模块，用于访问命令行参数和退出程序
import os  # 导入操作系统模块，用于文件和路径操作
import cv2  # 导入OpenCV库，用于图像处理和计算机视觉
import time  # 导入时间模块，用于控制帧率和计时
import numpy as np  # 导入NumPy库，用于数值计算和数组操作
from datetime import datetime  # 导入日期时间模块，用于时间戳记录
from PIL import Image, ImageDraw, ImageFont  # 导入PIL库，用于图像处理和绘制中文文本
import io  # 导入io模块，用于处理数据流
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFileDialog, QComboBox, QProgressBar,
                           QMessageBox, QStatusBar, QSplitter, QFrame, QToolBar,
                           QAction, QStackedWidget, QRadioButton, QButtonGroup)  # 导入PyQt5部件，用于创建GUI
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QColor  # 导入PyQt5图形相关类
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QDateTime  # 导入PyQt5核心类
from ultralytics import YOLO  # 导入YOLOv8模型，用于目标检测

# 定义类别映射
CLASS_NAMES = {0: '异常', 1: '正常'}  # 对应 ['anomaly', 'normal']，定义检测类别的映射关系

def cv2_add_chinese_text(img, text, position, textColor=(0, 255, 0), textSize=30):
    """
    使用PIL绘制中文文本到OpenCV图像
    """
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # 将OpenCV图像转换为PIL图像
    
    # 创建一个可以在给定图像上绘制的对象
    draw = ImageDraw.Draw(img)  # 创建绘图对象
    
    # 尝试加载多种中文字体
    fontStyle = None  # 初始化字体对象
    chinese_fonts = [  # 定义多种中文字体，按优先级排序
        "simhei.ttf",               # 黑体
        "simsun.ttc",               # 宋体
        "msyh.ttc",                 # 微软雅黑
        "simkai.ttf",               # 楷体
        "STKAITI.TTF",              # 华文楷体
        "STFANGSO.TTF",             # 华文仿宋
        r"C:\Windows\Fonts\simhei.ttf",  # 完整路径黑体
        r"C:\Windows\Fonts\simsun.ttc",  # 完整路径宋体
        r"C:\Windows\Fonts\msyh.ttc",    # 完整路径微软雅黑
    ]
    
    for font_name in chinese_fonts:  # 遍历字体列表
        try:
            fontStyle = ImageFont.truetype(font_name, textSize, encoding="utf-8")  # 尝试加载字体
            break  # 成功加载后跳出循环
        except IOError:  # 加载失败时继续尝试下一个字体
            continue
    
    # 如果所有字体都无法加载，使用默认字体
    if fontStyle is None:  # 检查是否有可用字体
        fontStyle = ImageFont.load_default()  # 使用默认字体
    
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)  # 在图像上绘制文本
    
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)  # 将PIL图像转换回OpenCV格式

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, list)  # 定义信号，用于传递处理后的帧和检测结果
    progress_signal = pyqtSignal(int)  # 定义信号，用于更新处理进度
    finished_signal = pyqtSignal()  # 定义信号，用于通知处理完成
    
    def __init__(self, video_path, model_path):
        super().__init__()  # 调用父类初始化方法
        self.video_path = video_path  # 设置视频路径
        self.model_path = model_path  # 设置模型路径
        self.running = True  # 设置运行标志
    
    def run(self):
        # 加载YOLOv8模型
        model = YOLO(self.model_path)  # 初始化YOLOv8模型
        
        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)  # 打开视频文件
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 获取视频总帧数
        
        frame_count = 0  # 初始化帧计数器
        while self.running and cap.isOpened():  # 当线程运行且视频文件打开时循环处理
            ret, frame = cap.read()  # 读取一帧
            if not ret:  # 如果读取失败（视频结束）
                break  # 跳出循环
                
            # 使用YOLOv8进行推理
            results = model(frame)  # 对当前帧进行目标检测
            
            # 获取检测结果（用于在主界面中绘制）
            detections = []  # 初始化检测结果列表
            for result in results:  # 遍历检测结果
                boxes = result.boxes.cpu().numpy()  # 获取边界框数据并转换为numpy数组
                for box in boxes:  # 遍历每个边界框
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # 提取边界框坐标并转换为整数
                    confidence = float(box.conf[0])  # 提取置信度并转换为浮点数
                    class_id = int(box.cls[0])  # 提取类别ID并转换为整数
                    detections.append({  # 将检测结果添加到列表中
                        'box': (x1, y1, x2, y2),  # 边界框坐标
                        'confidence': confidence,  # 置信度
                        'class_id': class_id  # 类别ID
                    })
            
            # 发送处理后的帧和检测结果
            self.change_pixmap_signal.emit(frame, detections)  # 发送信号，传递当前帧和检测结果
            
            # 更新进度
            frame_count += 1  # 帧计数器加1
            progress = int(frame_count / total_frames * 100)  # 计算处理进度百分比
            self.progress_signal.emit(progress)  # 发送进度信号
            
            # 控制帧率
            time.sleep(0.01)  # 短暂休眠，控制处理速度
        
        # 释放资源
        cap.release()  # 释放视频捕获对象
        self.finished_signal.emit()  # 发送处理完成信号
    
    def stop(self):
        self.running = False  # 设置运行标志为False，停止循环
        self.wait()  # 等待线程结束

class AnomalyDetectionApp(QMainWindow):
    def __init__(self, username):
        super().__init__()  # 调用父类初始化方法
        
        self.username = username  # 存储当前用户名
        self.video_thread = None  # 初始化视频处理线程为None
        self.model_path = "best.pt"  # 默认模型路径
        self.current_image = None  # 初始化当前图像为None
        self.current_video_path = None  # 初始化当前视频路径为None
        self.current_detections = []  # 初始化当前检测结果列表
        self.mode = "image"  # 默认为图像模式
        
        self.init_ui()  # 初始化用户界面
    
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle("商场视频监控异常行为检测系统")  # 设置窗口标题
        self.setMinimumSize(1200, 800)  # 设置窗口最小尺寸
        
        # 创建中央窗口部件
        central_widget = QWidget()  # 创建中央部件
        self.setCentralWidget(central_widget)  # 设置中央部件
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)  # 创建垂直布局
        main_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距
        
        # 创建工具栏
        self.create_toolbar()  # 调用创建工具栏方法
        
        # 创建主界面分割器
        splitter = QSplitter(Qt.Horizontal)  # 创建水平分割器
        
        # 创建控制面板
        control_panel = self.create_control_panel()  # 调用创建控制面板方法
        
        # 创建显示区域
        display_panel = self.create_display_panel()  # 调用创建显示面板方法
        
        # 添加到分割器
        splitter.addWidget(control_panel)  # 将控制面板添加到分割器
        splitter.addWidget(display_panel)  # 将显示面板添加到分割器
        
        # 设置分割器初始大小
        splitter.setSizes([300, 900])  # 设置初始宽度分配
        
        # 添加到主布局
        main_layout.addWidget(splitter)  # 将分割器添加到主布局
        
        # 创建状态栏
        self.create_status_bar()  # 调用创建状态栏方法
        
        # 设置样式
        self.set_styles()  # 调用设置样式方法
        
        # 启动时钟更新状态栏
        self.start_clock()  # 调用启动时钟方法
    
    def create_toolbar(self):
        # 创建工具栏
        toolbar = QToolBar("主工具栏")  # 创建工具栏并设置名称
        toolbar.setIconSize(QSize(24, 24))  # 设置图标大小
        toolbar.setMovable(False)  # 设置工具栏不可移动
        self.addToolBar(toolbar)  # 将工具栏添加到主窗口
        
        # 添加操作
        about_action = QAction(QIcon(""), "关于", self)  # 创建关于操作
        toolbar.addAction(about_action)  # 将关于操作添加到工具栏
        about_action.triggered.connect(self.show_about)  # 连接触发信号到显示关于方法
        
        # 添加分隔符
        toolbar.addSeparator()  # 添加分隔符
        
        exit_action = QAction(QIcon(""), "退出", self)  # 创建退出操作
        toolbar.addAction(exit_action)  # 将退出操作添加到工具栏
        exit_action.triggered.connect(self.close)  # 连接触发信号到关闭窗口方法
    
    def create_control_panel(self):
        # 创建控制面板
        control_panel = QWidget()  # 创建控制面板部件
        control_panel.setMaximumWidth(350)  # 设置最大宽度
        control_layout = QVBoxLayout(control_panel)  # 创建垂直布局
        
        # 控制面板标题
        title_label = QLabel("控制面板")  # 创建标题标签
        title_label.setFont(QFont("Arial", 14, QFont.Bold))  # 设置字体
        title_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        title_label.setStyleSheet("color: #3f87f5; margin: 10px 0;")  # 设置样式
        
        # 分割线
        line = QFrame()  # 创建分割线框架
        line.setFrameShape(QFrame.HLine)  # 设置为水平线
        line.setFrameShadow(QFrame.Sunken)  # 设置为下沉样式
        
        # 检测模式选择
        mode_group_label = QLabel("检测模式:")  # 创建模式组标签
        mode_group_label.setFont(QFont("Arial", 10, QFont.Bold))  # 设置字体
        
        mode_layout = QHBoxLayout()  # 创建水平布局
        
        self.image_radio = QRadioButton("图像检测")  # 创建图像检测单选按钮
        self.video_radio = QRadioButton("视频检测")  # 创建视频检测单选按钮
        
        # 按钮分组
        mode_group = QButtonGroup(self)  # 创建按钮组
        mode_group.addButton(self.image_radio)  # 添加图像单选按钮到组
        mode_group.addButton(self.video_radio)  # 添加视频单选按钮到组
        
        # 默认选择图像模式
        self.image_radio.setChecked(True)  # 设置图像单选按钮为选中状态
        
        # 连接槽函数
        self.image_radio.toggled.connect(self.on_mode_changed)  # 连接切换信号到模式改变方法
        self.video_radio.toggled.connect(self.on_mode_changed)  # 连接切换信号到模式改变方法
        
        mode_layout.addWidget(self.image_radio)  # 添加图像单选按钮到布局
        mode_layout.addWidget(self.video_radio)  # 添加视频单选按钮到布局
        
        # 文件选择
        file_group_label = QLabel("文件选择:")  # 创建文件组标签
        file_group_label.setFont(QFont("Arial", 10, QFont.Bold))  # 设置字体
        
        self.file_path_label = QLabel("未选择文件")  # 创建文件路径标签
        self.file_path_label.setWordWrap(True)  # 启用自动换行
        self.file_path_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")  # 设置样式
        
        self.select_file_button = QPushButton("选择文件")  # 创建选择文件按钮
        self.select_file_button.clicked.connect(self.select_file)  # 连接点击信号到选择文件方法
        self.select_file_button.setStyleSheet("""
            QPushButton {
                background-color: #3f87f5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #3978d8;
            }
            QPushButton:pressed {
                background-color: #2c5aa0;
            }
        """)  # 设置按钮样式
        
        # 操作按钮
        self.start_button = QPushButton("开始检测")  # 创建开始检测按钮
        self.start_button.clicked.connect(self.start_detection)  # 连接点击信号到开始检测方法
        self.start_button.setEnabled(False)  # 设置按钮初始为禁用状态
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3c8c40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)  # 设置按钮样式
        
        self.stop_button = QPushButton("停止检测")  # 创建停止检测按钮
        self.stop_button.clicked.connect(self.stop_detection)  # 连接点击信号到停止检测方法
        self.stop_button.setEnabled(False)  # 设置按钮初始为禁用状态
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)  # 设置按钮样式
        
        # 进度条
        progress_label = QLabel("检测进度:")  # 创建进度标签
        progress_label.setFont(QFont("Arial", 10, QFont.Bold))  # 设置字体
        
        self.progress_bar = QProgressBar()  # 创建进度条
        self.progress_bar.setRange(0, 100)  # 设置范围为0-100
        self.progress_bar.setValue(0)  # 设置初始值为0
        self.progress_bar.setTextVisible(True)  # 显示进度文本
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdbdbd;
                border-radius: 3px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #3f87f5;
                width: 10px;
            }
        """)  # 设置进度条样式
        
        # 结果显示区域
        results_label = QLabel("检测结果:")  # 创建结果标签
        results_label.setFont(QFont("Arial", 10, QFont.Bold))  # 设置字体
        
        self.results_display = QLabel("无检测结果")  # 创建结果显示标签
        self.results_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # 左上对齐
        self.results_display.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 3px;
            min-height: 150px;
        """)  # 设置样式
        self.results_display.setWordWrap(True)  # 启用自动换行
        
        # 添加所有组件到控制面板布局
        control_layout.addWidget(title_label)  # 添加标题
        control_layout.addWidget(line)  # 添加分割线
        control_layout.addWidget(mode_group_label)  # 添加模式组标签
        control_layout.addLayout(mode_layout)  # 添加模式选择布局
        control_layout.addWidget(file_group_label)  # 添加文件组标签
        control_layout.addWidget(self.file_path_label)  # 添加文件路径标签
        control_layout.addWidget(self.select_file_button)  # 添加选择文件按钮
        control_layout.addWidget(self.start_button)  # 添加开始按钮
        control_layout.addWidget(self.stop_button)  # 添加停止按钮
        control_layout.addWidget(progress_label)  # 添加进度标签
        control_layout.addWidget(self.progress_bar)  # 添加进度条
        control_layout.addWidget(results_label)  # 添加结果标签
        control_layout.addWidget(self.results_display)  # 添加结果显示区域
        control_layout.addStretch()  # 添加弹性空间
        
        return control_panel  # 返回控制面板
    
    def create_display_panel(self):
        # 创建显示区域
        display_panel = QWidget()  # 创建显示面板部件
        display_layout = QVBoxLayout(display_panel)  # 创建垂直布局
        
        # 显示区域标题
        title_label = QLabel("监控显示区域")  # 创建标题标签
        title_label.setFont(QFont("Arial", 14, QFont.Bold))  # 设置字体
        title_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        title_label.setStyleSheet("color: #3f87f5; margin: 10px 0;")  # 设置样式
        
        # 分割线
        line = QFrame()  # 创建分割线框架
        line.setFrameShape(QFrame.HLine)  # 设置为水平线
        line.setFrameShadow(QFrame.Sunken)  # 设置为下沉样式
        
        # 图像/视频显示区域
        self.image_label = QLabel()  # 创建图像标签
        self.image_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.image_label.setStyleSheet("background-color: #2c3e50; border-radius: 5px;")  # 设置样式
        self.image_label.setMinimumHeight(500)  # 设置最小高度
        
        # 设置初始图像
        placeholder = QPixmap(800, 500)  # 创建占位图像
        placeholder.fill(QColor(44, 62, 80))  # 填充背景色
        self.image_label.setPixmap(placeholder)  # 设置为图像标签的图像
        
        # 添加到布局
        display_layout.addWidget(title_label)  # 添加标题
        display_layout.addWidget(line)  # 添加分割线
        display_layout.addWidget(self.image_label)  # 添加图像标签
        display_layout.addStretch()  # 添加弹性空间
        
        return display_panel  # 返回显示面板
    
    def create_status_bar(self):
        # 创建状态栏
        status_bar = QStatusBar()  # 创建状态栏
        self.setStatusBar(status_bar)  # 设置为窗口的状态栏
        
        # 用户信息标签
        self.user_label = QLabel(f"当前用户: {self.username}")  # 创建用户标签并显示当前用户名
        status_bar.addWidget(self.user_label)  # 添加用户标签到状态栏
        
        # 添加永久的分隔符
        status_bar.addPermanentWidget(QLabel("|"))  # 添加垂直分隔符
        
        # 添加时间标签
        self.time_label = QLabel()  # 创建时间标签
        status_bar.addPermanentWidget(self.time_label)  # 添加时间标签到状态栏右侧
    
    def set_styles(self):
        # 设置应用程序样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QToolBar {
                background-color: #3f87f5;
                color: white;
                border: none;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QToolBar QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QToolBar QToolButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QStatusBar {
                background-color: #f0f0f0;
                color: #333333;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
            }
            QRadioButton {
                color: #333333;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
        """)  # 定义应用程序的全局样式表
    
    def start_clock(self):
        # 启动时钟
        self.timer = QTimer(self)  # 创建定时器
        self.timer.timeout.connect(self.update_clock)  # 连接超时信号到更新时钟方法
        self.timer.start(1000)  # 每秒触发一次
        self.update_clock()  # 立即更新一次时钟
    
    def update_clock(self):
        # 更新时间标签
        current_time = QDateTime.currentDateTime()  # 获取当前日期时间
        formatted_time = current_time.toString("yyyy-MM-dd hh:mm:ss")  # 格式化日期时间
        self.time_label.setText(formatted_time)  # 更新时间标签文本
    
    def on_mode_changed(self):
        # 模式切换处理
        if self.image_radio.isChecked():  # 如果图像单选按钮被选中
            self.mode = "image"  # 设置模式为图像
        else:  # 否则
            self.mode = "video"  # 设置模式为视频
        
        # 重置文件选择
        self.file_path_label.setText("未选择文件")  # 重置文件路径标签
        self.current_image = None  # 清除当前图像
        self.current_video_path = None  # 清除当前视频路径
        self.start_button.setEnabled(False)  # 禁用开始按钮
        
        # 重置显示区域
        placeholder = QPixmap(800, 500)  # 创建占位图像
        placeholder.fill(QColor(44, 62, 80))  # 填充背景色
        self.image_label.setPixmap(placeholder)  # 重置图像标签
        
        # 重置检测结果
        self.results_display.setText("无检测结果")  # 重置结果显示
        self.progress_bar.setValue(0)  # 重置进度条
    
    def select_file(self):
        # 选择文件
        if self.mode == "image":  # 如果是图像模式
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择图像文件", "", "图像文件 (*.jpg *.jpeg *.png *.bmp)"
            )  # 打开文件对话框选择图像
            if file_path:  # 如果选择了文件
                self.file_path_label.setText(file_path)  # 更新文件路径标签
                self.current_image = cv2.imread(file_path)  # 读取图像
                self.display_image(self.current_image)  # 显示图像
                self.start_button.setEnabled(True)  # 启用开始按钮
        else:  # 视频模式
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv)"
            )  # 打开文件对话框选择视频
            if file_path:  # 如果选择了文件
                self.file_path_label.setText(file_path)  # 更新文件路径标签
                self.current_video_path = file_path  # 保存视频路径
                # 显示视频第一帧
                cap = cv2.VideoCapture(file_path)  # 打开视频文件
                ret, frame = cap.read()  # 读取第一帧
                if ret:  # 如果读取成功
                    self.display_image(frame)  # 显示第一帧
                cap.release()  # 释放视频捕获对象
                self.start_button.setEnabled(True)  # 启用开始按钮
    
    def start_detection(self):
        # 开始检测
        if not os.path.exists(self.model_path):  # 检查模型文件是否存在
            QMessageBox.critical(self, "错误", f"模型文件 {self.model_path} 不存在!")  # 显示错误消息
            return  # 退出方法
        
        if self.mode == "image" and self.current_image is not None:  # 如果是图像模式且已选择图像
            # 图像模式检测
            self.start_button.setEnabled(False)  # 禁用开始按钮
            self.stop_button.setEnabled(False)  # 禁用停止按钮
            self.progress_bar.setValue(10)  # 设置进度为10%
            
            # 加载模型
            try:
                model = YOLO(self.model_path)  # 初始化YOLOv8模型
                
                # 推理
                self.progress_bar.setValue(50)  # 设置进度为50%
                results = model(self.current_image)  # 对图像进行目标检测
                
                # 获取原始图像的副本
                img_with_boxes = self.current_image.copy()  # 复制原图像用于绘制
                
                # 生成检测结果文本
                detections = []  # 初始化检测结果列表
                for result in results:  # 遍历检测结果
                    boxes = result.boxes.cpu().numpy()  # 获取边界框数据
                    for i, box in enumerate(boxes):  # 遍历每个边界框
                        x1, y1, x2, y2 = map(int, box.xyxy[0])  # 提取边界框坐标
                        confidence = float(box.conf[0])  # 提取置信度
                        class_id = int(box.cls[0])  # 提取类别ID
                        
                        # 绘制边界框
                        cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 绘制矩形边界框
                        
                        # 获取中文类别名称
                        class_name = CLASS_NAMES.get(class_id, f"类别{class_id}")  # 获取类别名称
                        
                        # 绘制中文标签
                        label_text = f"{class_name}: {confidence:.2f}"  # 生成标签文本
                        img_with_boxes = cv2_add_chinese_text(
                            img_with_boxes, 
                            label_text, 
                            (x1, y1 - 35), 
                            textColor=(0, 255, 0), 
                            textSize=25
                        )  # 添加中文文本标签
                        
                        detections.append({  # 添加检测结果到列表
                            'id': i+1,  # 目标ID
                            'class_id': class_id,  # 类别ID
                            'confidence': confidence,  # 置信度
                            'box': (x1, y1, x2, y2)  # 边界框坐标
                        })
                
                # 显示图像
                self.display_image(img_with_boxes)  # 显示添加了边界框的图像
                
                # 更新结果显示
                if detections:  # 如果有检测结果
                    result_text = "检测到以下结果:\n"  # 初始化结果文本
                    for d in detections:  # 遍历检测结果
                        class_name = CLASS_NAMES.get(d['class_id'], f"类别{d['class_id']}")  # 获取类别名称
                        result_text += f"- 目标 {d['id']}: {class_name}, 置信度 {d['confidence']:.2f}\n"  # 添加结果信息
                    self.results_display.setText(result_text)  # 更新结果显示
                else:  # 没有检测到目标
                    self.results_display.setText("未检测到目标")  # 更新结果显示
                
                self.progress_bar.setValue(100)  # 设置进度为100%
                self.start_button.setEnabled(True)  # 启用开始按钮
                
            except Exception as e:  # 捕获异常
                QMessageBox.critical(self, "错误", f"检测过程中发生错误: {str(e)}")  # 显示错误消息
                self.progress_bar.setValue(0)  # 重置进度条
                self.start_button.setEnabled(True)  # 启用开始按钮
        
        elif self.mode == "video" and self.current_video_path is not None:  # 如果是视频模式且已选择视频
            # 视频模式检测
            self.start_button.setEnabled(False)  # 禁用开始按钮
            self.stop_button.setEnabled(True)  # 启用停止按钮
            
            # 重置进度条
            self.progress_bar.setValue(0)  # 设置进度条为0
            
            # 创建并启动视频处理线程
            self.video_thread = VideoThread(self.current_video_path, self.model_path)  # 创建视频处理线程
            self.video_thread.change_pixmap_signal.connect(self.update_video_frame)  # 连接信号到更新视频帧方法
            self.video_thread.progress_signal.connect(self.update_progress)  # 连接信号到更新进度方法
            self.video_thread.finished_signal.connect(self.on_video_finished)  # 连接信号到视频完成方法
            self.video_thread.start()  # 启动线程
    
    def stop_detection(self):
        # 停止检测
        if self.video_thread is not None and self.video_thread.isRunning():  # 如果视频线程存在且正在运行
            self.video_thread.stop()  # 停止视频线程
            self.stop_button.setEnabled(False)  # 禁用停止按钮
            self.start_button.setEnabled(True)  # 启用开始按钮
    
    def update_video_frame(self, frame, detections):
        # 更新视频帧和检测结果
        self.current_detections = detections  # 保存当前检测结果
        
        # 绘制检测结果
        frame_with_boxes = frame.copy()  # 复制原帧用于绘制
        for d in detections:  # 遍历检测结果
            x1, y1, x2, y2 = d['box']  # 获取边界框坐标
            confidence = d['confidence']  # 获取置信度
            class_id = int(d['class_id'])  # 获取类别ID
            
            # 绘制边界框
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 绘制矩形边界框
            
            # 获取中文类别名称
            class_name = CLASS_NAMES.get(class_id, f"类别{class_id}")  # 获取类别名称
            
            # 绘制中文标签
            label_text = f"{class_name}: {confidence:.2f}"  # 生成标签文本
            # 使用自定义函数添加中文文本
            frame_with_boxes = cv2_add_chinese_text(
                frame_with_boxes, 
                label_text, 
                (x1, y1 - 35), 
                textColor=(0, 255, 0), 
                textSize=25
            )  # 添加中文文本标签
        
        # 显示帧
        self.display_image(frame_with_boxes)  # 显示添加了边界框的帧
        
        # 更新检测结果文本
        if detections:  # 如果有检测结果
            result_text = "检测到以下结果:\n"  # 初始化结果文本
            for i, d in enumerate(detections):  # 遍历检测结果
                class_id = int(d['class_id'])  # 获取类别ID
                class_name = CLASS_NAMES.get(class_id, f"类别{class_id}")  # 获取类别名称
                result_text += f"- 目标 {i+1}: {class_name}, 置信度 {d['confidence']:.2f}\n"  # 添加结果信息
            self.results_display.setText(result_text)  # 更新结果显示
        else:  # 没有检测到目标
            self.results_display.setText("未检测到目标")  # 更新结果显示
    
    def update_progress(self, value):
        # 更新进度条
        self.progress_bar.setValue(value)  # 设置进度条值
    
    def on_video_finished(self):
        # 视频处理完成
        self.stop_button.setEnabled(False)  # 禁用停止按钮
        self.start_button.setEnabled(True)  # 启用开始按钮
        QMessageBox.information(self, "完成", "视频检测已完成!")  # 显示完成消息
    
    def display_image(self, cv_img):
        # 将OpenCV图像转换为QPixmap并显示
        if cv_img is None:  # 如果图像为空
            return  # 直接返回
            
        # 调整图像大小以适应标签
        h, w, ch = cv_img.shape  # 获取图像尺寸和通道数
        label_size = self.image_label.size()  # 获取标签尺寸
        
        # 计算要保持纵横比的新尺寸
        scale = min(label_size.width() / w, label_size.height() / h)  # 计算缩放比例
        new_w = int(w * scale)  # 计算新宽度
        new_h = int(h * scale)  # 计算新高度
        
        # 调整大小
        cv_img = cv2.resize(cv_img, (new_w, new_h))  # 调整图像大小
        
        # 转换颜色空间
        bytes_per_line = ch * new_w  # 计算每行字节数
        convert_to_Qt_format = QImage(cv_img.data, new_w, new_h, bytes_per_line, QImage.Format_BGR888)  # 转换为Qt图像格式
        pixmap = QPixmap.fromImage(convert_to_Qt_format)  # 转换为QPixmap
        
        # 显示图像
        self.image_label.setPixmap(pixmap)  # 设置图像到标签
    
    def show_about(self):
        # 显示关于对话框
        about_text = """
        <h2>商场视频监控异常行为检测系统</h2>
        <p>版本: 1.0.0</p>
        <p>基于YOLOv8的异常行为检测系统</p>
        <p>使用PyQt5构建的现代化界面</p>
        <p>© 2025 保留所有权利</p>
        """  # 定义关于文本
        
        QMessageBox.about(self, "关于", about_text)  # 显示关于对话框
    
    def closeEvent(self, event):
        # 关闭事件处理
        if self.video_thread is not None and self.video_thread.isRunning():  # 如果视频线程存在且正在运行
            self.video_thread.stop()  # 停止视频线程
        event.accept()  # 接受关闭事件 