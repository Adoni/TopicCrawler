#coding:utf8
file_in_name='./candidates.seed'
lines=open(file_in_name).readlines()
file_out_name='./candidates.seed2'
file_out=open(file_out_name, 'w')
for line in lines:
    line=line.split('\t')[1]
    file_out.write(line.decode('utf8').encode('utf8')+'\n')
file_out.close()
