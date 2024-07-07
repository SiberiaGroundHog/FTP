import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout,QHBoxLayout, QWidget, QTreeView, QLabel, QFileSystemModel, QDialog
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import QModelIndex
from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# 导入自定义模块
import myftp
import MyModel

class LoginThread(QThread):

    def __init__(self,  signal, host, username, password):
        super().__init__()
        self.login_complet_signal = signal
        self.host = host
        self.username = username
        self.password = password

    def start_login(self):
        self.ftp = myftp.MyFTP(self.host, self.username, self.password)
        print(self.ftp.getStatus())
        if self.ftp.getStatus(): 
             self.login_complet_signal.emit(self.ftp)
        
    def run(self):
        self.start_login()


class InitservermodelThread(QThread):
    def __init__(self, signal, ftp):
        super().__init__()
        self.init_servermodel_signal = signal
        self.ftp = ftp
        
    def run(self):
        self.ftp.SetPath('/')
        self.serverfile_model = MyModel.ServerFileModel(self.ftp)
        self.init_servermodel_signal.emit(self.serverfile_model)

class DownloadThread(QThread):
    def __init__(self, signal, ftp, clientPath, serverPath):
        super().__init__()
        self.download_signal = signal
        self.ftp = ftp
        self.clientPath = clientPath
        self.serverPath = serverPath
        
    def run(self):
        self.ftp.DownloadFile(self.clientPath, self.serverPath)
        self.download_signal.emit('downloadSuccess')
        

class UploadThread(QThread):
    def __init__(self, signal, ftp, clientPath, serverPath):
        super().__init__()
        self.upload_signal = signal
        self.ftp = ftp
        self.clientPath = clientPath
        self.serverPath = serverPath
        
    def run(self):
        self.ftp.UploadFile(self.clientPath, self.serverPath)
        self.upload_signal.emit(self.serverPath)
       

class MainWindow(QMainWindow):  
    init_servermodel_signal = pyqtSignal(object)
    download_signal = pyqtSignal(str)
    upload_signal = pyqtSignal(str)

    # 主窗口类，包含文件浏览器和操作按钮
    def __init__(self,ftp):  
        super().__init__()
        self.ftp = ftp
        self.clientPath = os.path.abspath(__file__)
        self.serverPath = '/'
        self.upload_signal.connect(self.task_done)
        self.download_signal.connect(self.task_done)
        
        self.initUI()  
  
    def initUI(self):  
        # 初始化用户界面  
        self.setWindowTitle('FTP client')  
        self.setWindowIcon(QIcon('C:\\Users\\23659\\Desktop\\exData\\communicationPyhon\\FTPclient\\ftp.svg')) # 设置窗口图标
        self.setGeometry(300, 300, 2000, 1000)  
  
         # 创建按钮
        self.btn_download = QPushButton('下载')
        self.btn_upload = QPushButton('上传')
        self.btn_delete = QPushButton('删除')
        self.btn_refresh = QPushButton('刷新')
  
        # 创建布局  
        button_layout = QHBoxLayout()  
        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_upload)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_refresh)

        self.btn_download.clicked.connect(self.on_download_clicked)
        self.btn_upload.clicked.connect(self.on_upload_clicked)
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        self.btn_refresh.clicked.connect(self.on_refresh_clicked)
  
        # 设置文件系统模型  
        self.clientfile_model = QFileSystemModel()  
        self.clientfile_model.setRootPath('')  # 设置根目录  
        self.clientfile_model.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries) 
        
        
        # 单开线程初始化服务器端文件模型
        self.init_servermodel_signal.connect(self.init_servermodel_slot)
        self.init_servermodelThread = InitservermodelThread(self.init_servermodel_signal,self.ftp)
        self.init_servermodelThread.start()

         # 设置视图  
        # 创建本地 QTreeView 实例
        self.clientFileTreeView = QTreeView()  
        self.clientFileTreeView.setModel(self.clientfile_model)  
        self.clientFileTreeView.setRootIndex(self.clientfile_model.index(QDir.rootPath()))  
        self.clientFileTreeView.setSortingEnabled(True)  
        self.clientFileTreeView.clicked.connect(self.on_clientfile_clicked) 
        self.clientFileTreeView.setColumnHidden(1,True) 
        self.clientFileTreeView.setColumnHidden(2,True)
        self.clientFileTreeView.setColumnHidden(3,True)

        # 创建服务器 QTreeView 实例
        self.serverFileTreeView = QTreeView()  
          
        # 设置本地文件和服务器路径路径标签
        self.client_path_label = QLabel('本地路径：')
        self.client_path_label.setText(f"本地路径：{self.clientPath}")
        self.server_path_label = QLabel('服务器路径：')
        self.server_path_label.setText(f"服务器路径：加载中...")
        
        middle_left_layout = QVBoxLayout()
        middle_left_layout.addWidget(self.client_path_label)
        middle_left_layout.addWidget(self.clientFileTreeView)

        middle_right_layout = QVBoxLayout()
        middle_right_layout.addWidget(self.server_path_label)
        middle_right_layout.addWidget(self.serverFileTreeView)

        middle_layout = QHBoxLayout()
        middle_layout.addLayout(middle_left_layout, 1) # 本地文件浏览器占1份空间  
        middle_layout.addLayout(middle_right_layout, 1) # 服务器端文件浏览器占1份空间  
  
        # 创建状态标签  
        self.status_label = QLabel('就绪', self)
  
        # 创建主布局  
        main_layout = QVBoxLayout()  
        main_layout.addLayout(button_layout)  
        main_layout.addLayout(middle_layout)  
        main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter) 
  
        # 设置中央部件  
        central_widget = QWidget()  
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget) 

    def init_servermodel_slot(self, model):
        self.serverfile_model = model
        self.server_path_label.setText(f"服务器路径：{self.serverPath}")
        self.serverFileTreeView.setModel(self.serverfile_model)  
        self.serverFileTreeView.setSortingEnabled(True)  
        self.serverFileTreeView.clicked.connect(self.on_serverfile_clicked)
        self.btn_refresh.setEnabled(True)
        self.status_label.setText('就绪')
  
    def on_clientfile_clicked(self, index):  
        """处理本地文件点击事件"""
        if not index.parent().isValid():  # 如果点击的是根目录项，则不处理  
            return  
        file_info = self.clientfile_model.fileInfo(index)  
        self.clientPath = f"{file_info.absoluteFilePath()}"
        if file_info.isFile():  
            self.client_path_label.setText("本地路径:"+self.clientPath)
            print(f"File clicked: {file_info.absoluteFilePath()}")  

        elif file_info.isDir():  
            self.client_path_label.setText(f"本地路径：{file_info.absoluteFilePath()}")
            print(f"Dir clicked: {file_info.absoluteFilePath()}")
        
    def on_serverfile_clicked(self, index: QModelIndex):  
        """处理服务器文件点击事件"""
        item = self.serverfile_model.itemFromIndex(index)
        if item:
            # 获取点击项及其所有父项的文本
            path = '/'
            texts = []
            current_index = index
            while current_index.isValid():
                current_item = self.serverfile_model.itemFromIndex(current_index)
                if current_item:
                    texts.append(current_item.text())
                current_index = current_index.parent()
            # 反转列表以正确的顺序打印
            texts.reverse()
            path = path +"/".join(texts)
            self.serverPath = path
            self.server_path_label.setText(f"服务器路径：{self.serverPath}")
            print("Path:", path)

    def on_download_clicked(self):  
        """处理下载按钮点击事件"""
        print("点击下载")
        self.btn_download.setEnabled(False)
        filename = self.serverPath.split('/')[-1]
        self.status_label.setText('下载中...')
        self.downloadThread = DownloadThread(self.download_signal, self.ftp, self.clientPath+'/'+filename, self.serverPath)
        self.downloadThread.start()

    def on_upload_clicked(self):  
        """处理上传按钮点击事件"""
        print("点击上传")
        self.btn_upload.setEnabled(False)
        filename = self.clientPath.split('/')[-1]
        self.status_label.setText('上传中...')
        self.uploadThread = UploadThread(self.upload_signal, self.ftp, self.clientPath, self.serverPath+'/'+filename)
        self.uploadThread.start()
        

    def on_delete_clicked(self):  
        """处理删除按钮点击事件"""
        print("点击删除")
        self.ftp.RemoveFile(self.serverPath)
        self.serverfile_model.del_item(self.serverPath)
        self.ftp.RemoveFile(self.serverPath)
        self.serverfile_model.del_item(self.serverPath)
        self.serverFileTreeView.reset()

    def on_refresh_clicked(self):  
        """处理刷新按钮点击事件"""
        print("点击刷新")
        self.btn_refresh.setEnabled(False)
        self.status_label.setText('刷新中...')
        self.init_servermodelThread = InitservermodelThread(self.init_servermodel_signal,self.ftp)
        self.init_servermodelThread.start()

    def task_done(self,status):
        if status == 'downloadSuccess':
            self.btn_download.setEnabled(True)
            self.status_label.setText('就绪')
        else :
            self.btn_upload.setEnabled(True)
            self.serverfile_model.add_item(status)
            self.serverFileTreeView.reset()
            self.status_label.setText('就绪')
            

    
class LoginWindow(QDialog):
    login_complete_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('登录界面')
        self.setWindowIcon(QIcon('C:\\Users\\23659\\Desktop\\exData\\communicationPyhon\\FTPclient\\ftp.svg')) # 设置窗口图标
        self.setGeometry(500, 400, 500, 300) # 设置窗口大小和位置
        # 创建标签
        self.label_host = QLabel('服务器ip:')
        self.label_username = QLabel('用户名:')
        self.label_password = QLabel('密码:')

        # 创建输入框
        self.input_host = QLineEdit()
        self.input_host.setText('47.236.114.79')
        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)  # 密码输入框

        # 创建按钮
        self.btn_login = QPushButton('登录')
        self.btn_login.clicked.connect(self.on_login_clicked)

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.label_host)
        layout.addWidget(self.input_host)
        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)
        
        self.login_complete_signal.connect(self.login_complete_slot)

    def on_login_clicked(self):
        host = self.input_host.text()
        username = self.input_username.text()
        password = self.input_password.text()
        self.loginThread = LoginThread(self.login_complete_signal, host, username, password)
        self.loginThread.start()

    def login_complete_slot(self, ftp):
        self.mainWindow = MainWindow(ftp)
        self.mainWindow.show()
        self.close()


if __name__ == '__main__':  
    app = QApplication(sys.argv)  
    loginWindow = LoginWindow()  
    loginWindow.show()
    sys.exit(app.exec_())

