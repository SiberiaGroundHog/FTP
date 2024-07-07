from ftplib import FTP

class MyFTP():

    ftpStatus = False

    def __init__(self,host, username, password): 
        super().__init__()
        try:
            self.ftp = FTP(host=host, user=username, passwd=password)
            print(f"host: {host}, username: {username}, password: {password}")
            print(self.ftp.getwelcome())
            self.ftpStatus = True
        except:
            ftpStatus = False
            print('FTP连接失败')
        
    def getStatus(self):
        return self.ftpStatus
    
    def pwd(self):
        try:
            return self.ftp.pwd()
        except:
            pass
    
    def listdir(self):
        try:
            dir_list = []
            self.ftp.retrlines('LIST',dir_list.append)
            return dir_list
        except:
            pass

    def SetPath(self,path):
        try:
            self.ftp.cwd(path)
        except:
            pass

    def CreateNewDir(self,newDirName):
        try:
            self.ftp.mkd(newDirName)
        except:
            pass

    def RemoveDir(self,dirName):
        try:
            self.ftp.rmd(dirName)
        except:
            pass

    def RemoveFile(self,fileName):
        try:
            self.ftp.delete(fileName)
        except:
            pass

    def UploadFile(self,clientFile,serverFile):
        try:
            #上传文件
            self.ftp.storbinary('STOR '+ serverFile, open(clientFile, 'rb'))
            pass
        except:
            pass

    def DownloadFile(self,clientFile,serverFile):
        try:
            #下载文件
            self.ftp.retrbinary('RETR '+ serverFile, open(clientFile, 'wb').write)
            pass
        except:
            pass

    def getDirectory(self):
        # try:
        # directory = {}
        allDirList = ['/']
        for dirname in allDirList:
            self.SetPath(dirname)
            list = self.listdir()
            listname = []
            extracted_info = [(s[0], s.split()[-1]) for s in list] 
            for item in extracted_info:
                if item[0] == 'd':
                    allDirList.append(dirname + item[1] + '/')
                listname.append(item[1])
            # directory[dirname] = listname
        print(allDirList)
        return allDirList
        # return directory
        # except:
            # print('getDirectory()--ERROR')