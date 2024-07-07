from ftplib import FTP

def FtpLogin():
    host = '47.236.114.79'
    # user='user'
    # passwd='user123'
    # host = input('请输入服务器IP:')
    user = input('请输入用户名:')
    passwd = input('请输入密码:')
    while True:
        try:
            print('Connecting...')
            ftp = FTP(host=host, user=user, passwd=passwd)# connect to host, default port
            break;
        except:
            print('用户名或密码错误！！！')
            user = input('请重新输入用户名:')
            passwd = input('请重新输入密码:')
    print(ftp.getwelcome())
    return ftp

def PrintCommands():
    commands = {
        1:'退出',
        2:'查询指令集',
        3:'查询当前目录',
        4:'设置当前服务器目录',
        5:'查询当前目录下全部文件（详细信息）',
        6:'查询当前目录下全部文件（仅含文件名）',
        7:'创建新目录',
        8:'删除指定目录',
        9:'删除指定文件',
        10:'上传文件',
        11:'下载文件',
    }
    for number, description in commands.items():  
        print(f"{number}: {description}")  

def SetPath(ftp):
    try:
        Path = input('请输入路径:')
        ftp.cwd(Path)
    except:
        print('--未知路径，设置失败--')

def CreateNewDir(ftp):
    try:
        newDirName = input('请输出新目录名称:') #在服务器端设置新文件夹
        ftp.mkd(newDirName)
    except:
        print('--权限不足，创建失败--')

def RemoveDir(ftp):
    try:
        dirName = input('请输入要删除目录名称:')
        ftp.rmd(dirName)
    except:
        print('--未找到指定目录，删除失败--')

def RemoveFile(ftp):
    fileName = input('请输入要删除的文件名:')
    try:
        ftp.delete(fileName)
    except:
        print('--未找到指定文件，删除失败--')
    
def UploadFile(ftp):
    try:
        upLoadFile_client = input('请输入待上传文件本地路径:') #客户端待上传文件路径及文件名
        upLoadFile_server = input('请输入文件在服务器存储位置:') #服务器上传文件储存路径及文件名
        #上传文件
        ftp.storbinary('STOR '+ upLoadFile_server, open(upLoadFile_client, 'rb'))
        print('上传成功')
    except:
        print('--未找到指定文件--')

def DownloadFile(ftp):
    try:
        downLoadFile_server = input('请输入待下载文件服务器路径:') #服务器端待下载文件路径及文件名
        downLoadFile_client = input('请输入下载文件本地存储位置:') #客户端下载文件储存路径及文件名
        #下载文件
        ftp.retrbinary('RETR '+ downLoadFile_server, open(downLoadFile_client, 'wb').write)
        print('下载成功')
    except:
        print('--未找到指定文件--')


if __name__ == "__main__":
    ftp = FtpLogin()
    PrintCommands()
    while True:
        command = input('请输入指令编号：')
        if command=='1':
            ftp.quit()
            print('Connection closed!')
            break;
        elif command=='2':
            PrintCommands()
        elif command=='3':
            print(ftp.pwd())
        elif command=='4':
            SetPath(ftp)
        elif command=='5':
            ftp.retrlines('LIST') #列出当前目录下文件列表（详细信息）
        elif command=='6':
            ftp.retrlines('NLST') #列出当前目录下文件列表（仅包含文件名）
        elif command=='7':
            CreateNewDir(ftp)
        elif command=='8':
            RemoveDir(ftp)
        elif command=='9':
            RemoveFile(ftp)
        elif command=='10':
            UploadFile(ftp)
        elif command=='11':
            DownloadFile(ftp)
        else:
            print('--指令错误--')