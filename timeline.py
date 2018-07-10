import os
import time
def timeline():
    res = []
    for i in os.listdir():
        file_info = os.stat(i)
        a = time.localtime(file_info.st_ctime)
        b = time.ctime(file_info.st_ctime)
        x = (a,i,b)
        res.append(x)
    fin_res = sorted(res)
    for i in fin_res:
        print(str(i[-2])+" "+str(i[-1]))
