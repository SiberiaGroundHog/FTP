import sys  
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import myftp
  
# 自定义的FTP模型类  
class ServerFileModel(QStandardItemModel):  
    def __init__(self, ftp, parent=None):  
        super().__init__(parent)  
        self.ftp = ftp  
        self.setHorizontalHeaderLabels(['文件名'])
        self.initDir()

    def initDir(self):  
        self.directory = self.ftp.pwd()
        self.removeRows(0, self.rowCount())#清空模型中的所有行。
        self.loadDirectory(self.directory, self.invisibleRootItem())#从根目录开始加载目录结构。

    def loadDirectory(self, directory, parent_item):
        self.ftp.SetPath(directory)  
        files = self.ftp.listdir()  # 返回文件列表
        extracted_info = [(s[0], s.split()[-1]) for s in files]
        for item in extracted_info:
            standard_item = QStandardItem(item[1])
            parent_item.appendRow(standard_item)
            if item[0] == 'd':  # 判断是否为目录
                self.loadDirectory(directory + item[1] + '/', standard_item)

    def refresh(self):
        self.ftp.SetPath('/')  
        self.initDir()

    def add_item(self,addFilePath):
        path_parts = addFilePath.split('/')
        self.ftp.SetPath('/')
        current_item = self.invisibleRootItem()
        for part in path_parts[:-1]:
            for row in range(current_item.rowCount()):
                child_item = current_item.child(row)
                if child_item.text() == part:
                    current_item = child_item
                    break
        for row in range(current_item.rowCount()):
            child_item = current_item.child(row)
            if child_item.text() == path_parts[-1]:
                print(f"文件已覆盖:{addFilePath}")
                return
        new_sub_item = QStandardItem(path_parts[-1])
        current_item.appendRow(new_sub_item)
        print(f"上传成功：{addFilePath}")


    def del_item(self,delFilePath):
        path_parts = delFilePath.split('/')
        current_item = self.invisibleRootItem()
        for part in path_parts:
            for row in range(current_item.rowCount()):
                child_item = current_item.child(row)
                if child_item.text() == part:
                    current_item = child_item
                    if current_item.text() == path_parts[-1]:
                        current_item.parent().removeRow(current_item.row())
                    break
        


#  ###############################################################
#         self.model = QStandardItemModel()
 
#         self.model.setHorizontalHeaderLabels(['分类', '书名', '作者', '价格'])
    
#         bookType1 = QStandardItem("Java类")
#         bookType1.appendRow(
#             [QStandardItem(""), QStandardItem('Java编程思想'), QStandardItem('埃克尔'), QStandardItem('109')])  # 添加二级节点
#         bookType1.appendRow(
#             [QStandardItem(""), QStandardItem('Java从入门到精通'), QStandardItem('码牛逼'), QStandardItem('99')])  # 添加二级节点
    
#         self.model.appendRow(bookType1)  # 添加一级节点
    
#         bookType2 = QStandardItem("Python类")
#         bookType2.appendRow(
#             [QStandardItem(""), QStandardItem('Python编程思想'), QStandardItem('老王'), QStandardItem('10')])  # 添加二级节点
#         bookType2.appendRow(
#             [QStandardItem(""), QStandardItem('Python跟我学'), QStandardItem('老六'), QStandardItem('20')])  # 添加二级节点
#         self.model.appendRow(bookType2)  # 添加一级节点
    
#         bookType3 = QStandardItem("Go类")
#         bookType3.appendRow(
#             [QStandardItem(""), QStandardItem('Go编程思想'), QStandardItem('老王'), QStandardItem('10')])  # 添加二级节点
#         self.model.appendRow(bookType3)  # 添加一级节点
#         ################################################################
        
        