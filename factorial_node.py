from tasks import factorial
dataset = []
for x in range(0,input(),20):
    dataset.append(factorial.delay(x+1,x+20))
while True:
    print ('PROCESSING')
    flag = 1
    for x in dataset:
        if x.ready():
            flag = 1
        else:
            flag = 0
            break
    if flag == 1:
        tot = 1
        for x in dataset:
            tot *= x.get()
        print (tot)
        break
