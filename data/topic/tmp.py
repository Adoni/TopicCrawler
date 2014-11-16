f1=open('./topics.data').readlines()
f2=open('./hosts.data').readlines()
topic1=[]
topic2=[]
for l in f1:
    topic1.append(l.split('\t')[0])
f3=open('./hosts.data','w')
for l in f2:
    if not l.split('\t')[0] in topic1:
        continue
    f3.write(l)
