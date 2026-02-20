# 导入必要的库
import sys  # 导入系统模块，用于访问命令行参数和退出程序
from PyQt5.QtWidgets import QApplication  # 导入Qt应用程序类
from login_register import LoginRegisterWidget  # 导入登录/注册窗口
from anomaly_detection_app import AnomalyDetectionApp  # 导入异常检测应用窗口

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)  # 创建Qt应用程序实例
        
        # 启动登录/注册窗口
        self.login_window = LoginRegisterWidget()  # 创建登录/注册窗口实例
        self.login_window.login_successful.connect(self.on_login_success)  # 连接登录成功信号到处理函数
        self.login_window.show()  # 显示登录窗口
        
        # 初始化主应用窗口，但不显示
        self.main_window = None  # 主窗口初始为空
    
    def on_login_success(self, username):
        # 登录成功后的处理
        # 隐藏登录窗口
        self.login_window.hide()  # 隐藏登录窗口
        
        # 创建并显示主应用窗口
        self.main_window = AnomalyDetectionApp(username)  # 创建主应用窗口实例，传入用户名
        self.main_window.show()  # 显示主应用窗口
    
    def run(self):
        # 运行应用程序
        return self.app.exec_()  # 启动应用程序事件循环

if __name__ == "__main__":
    main_app = MainApp()  # 创建主应用程序实例
    sys.exit(main_app.run())  # 运行应用程序并在退出时返回状态码 