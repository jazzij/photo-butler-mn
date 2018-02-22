import csv,os
from shutil import copyfile


ifile  = open('facedata.csv', "rb")
branch = []
writer = csv.reader(ifile)

def check_existance(branch,to_search1,to_search2):
    for x in range(len(branch)):
        #print branch[x]
        if to_search1 in branch[x] or to_search2 in branch[x]:
            return x
    return -1

for x in writer:
    try:
        if float(x[-1]) <= 0.5:
            #print 'SAME PEOPLE WOW'
            tag = check_existance(branch,x[0],x[1])

            if tag >= 0:
                #print 'YO'
                if x[0] in branch[tag]:
                    branch[tag].append(x[1])
                elif x[1] in branch[tag]:
                    branch[tag].append(x[0])
            else:
                branch.append([x[0],x[1]])

    except:
        print ' EXCEPTION CAUGHT '

counter = 0
for x in branch:
    dst = str(counter)+'/'
    src = 'faces/'
    os.mkdir(dst)
    for y in x:
        copyfile(src+y, dst+y)
    counter += 1
    print x
    