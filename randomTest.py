import re

command="Polygonzug[(012578112,534,120,200)]"
split = re.split('\[',command)
split = re.split(',',split[1])
print(split)
for i in range(4):
    split[i] = split[i].replace('[',"")
    split[i] = split[i].replace(']',"")
    split[i] = split[i].replace('(',"")
    split[i] = split[i].replace(')',"")
    t = int( split[i])
    print( t )