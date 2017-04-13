import os, sys

print('初始路径：', os.getcwd())
os.chdir(os.path.dirname(sys.argv[0])+"/mc_trans")
print('重定位路径：', os.getcwd())

import mc_trans
from mc_trans import  server

if __name__ == "__main__":
    server.run()
    print(2344)
