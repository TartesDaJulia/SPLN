import re
import codecs
find = re.compile(r"^[^.]*")

filepath = 'DicionarioParallel9.ttl'
indexes = []
fp = open(filepath, encoding="utf-8")
#with open(filepath, encoding="utf-8") as fp:
lines = fp.read().splitlines()
fp.close()

for i in range(len(lines)):
    if re.match('^[a-zA-Z]+', lines[i]) is not None:
        lines[i-1] = lines[i-1] + lines[i]
        indexes.append(i)
        print('linha:' + str(i))

for i in reversed(indexes):
    del lines[i]

lines = [ele for ele in lines if ele != []] 
fp = codecs.open('DicionarioNOCARRIAGERETURN.ttl','w+','utf-8')
for line in lines:
    fp.write('\n'+line)
#line = fp.readline()
#cnt = 1
#while line:
#     if 'Significado' in line: 
#         #print("Line {}: {}".format(cnt, line.strip()))
#         print('regex')
#         print(re.search(find, line).group(0))
#         line = line.rstrip()
#         print(line)
#     
#     line = fp.readline()
#     cnt += 1