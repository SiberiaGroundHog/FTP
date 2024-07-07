from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler,ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.log import LogFormatter
import logging

#记录日志，默认情况下日志仅输出到屏幕（终端）
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename='myftpserver.log')
ch.setFormatter(LogFormatter())
fh.setFormatter(LogFormatter())
logger.addHandler(ch) #将日志输出至屏幕
logger.addHandler(fh) #将日志输出至文件

# 实例化虚拟用户，这是FTP验证首要条件
authorizer = DummyAuthorizer()
# 添加用户权限和路径，括号内的参数是(用户名， 密码， 用户目录， 权限),可以为不同的用户添加不同的目录和权限
# e：登录l：列出目录r：读取文件a：追加（写入）文件d：删除文件f：重命名/移动文件m：创建目录w：删除目
authorizer.add_user("user", "user123", "/home/ftp/", perm="elradfmw")
authorizer.add_user("root", "3946", "/home/", perm="elradfmw")
# 添加匿名用户 只需要路径
authorizer.add_anonymous("/home/ftp/anonymous/",perm='elradfmw')
# 初始化ftp句柄
handler = FTPHandler
handler.authorizer = authorizer
handler.banner = "Welcome to my FTP server."  # 可选：设置欢迎信息

#添加被动端口范围
handler.passive_ports = range(2000, 2333)

# 下载上传速度设置
# dtp_handler = ThrottledDTPHandler
# dtp_handler.read_limit = 0 
# dtp_handler.write_limit = 0

# 监听ip 和 端口,linux里需要root用户才能使用21端口
server = FTPServer(("0.0.0.0", 21), handler)

# 最大连接数
server.max_cons = 150
server.max_cons_per_ip = 15

# 开始服务，自带日志打印信息
server.serve_forever()
