import os

a = "../inverted_indexes/2019101021/index"
b = ".txt"
c = "file : "
total_words = 0
file_index = -1
up_lim = 5000

def merge_files(i,j):
    file1 = open(a+str(i)+b,'r')
    file2 = open(a+str(j)+b,'r')
    fh = open(a+"temp"+b,'w+')
    p1 = file1.readline()
    p2 = file2.readline()
    while(p1 and p2):
        word1 = p1.split("-")
        word2 = p2.split("-")
        if(word1[0] < word2[0]):
            fh.write(p1)
            p1 = file1.readline()
        elif(word1[0]>word2[0]):
            fh.write(p2)
            p2 = file2.readline()
        else:
            stemp = word1[0]+"-"+word1[1].rstrip()+word2[1]
            fh.write(stemp)
            p1 = file1.readline()
            p2 = file2.readline()
    while(p1):
        fh.write(p1)
        p1 = file1.readline()
    while(p2):
        fh.write(p2)
        p2 = file2.readline()
    fh.close()
    file1.close()
    file2.close()
    os.remove(a+str(i)+b)
    os.rename(a+"temp"+b,a+str(i)+b)

def write_stats():
    fh = open("./stat.txt","r")
    lines = fh.readlines()
    size = os.path.getsize("../inverted_indexes/2019101021/index1.txt")
    size = size/(1024*1024)
    print("size",size)
    fh.close()
    fh = open("./stats.txt","w+")
    fh.write(str(size)+"\n")
    for i in lines:
        fh.write(i)

def write_total_lines():
    stat = open("./total_lines.txt",'w+')
    stat.write(str(total_words)+"\n")

def split_files():
    global total_words,file_index
    fh = open(a + str(1) + b,"r")
    line = fh.readline()
    fh1 = open(a+"_word"+b,'w+')
    fh2 = open(a+"_"+str(0)+b,'w+')
    while(line):
        temp = line.split('-')
        if(total_words%up_lim == 0):
            file_index+=1
            fh2.close()
            fh2 = open(a+"_"+str(file_index)+b,'w+')
            fh1.write(temp[0]+"\n")
        fh2.write(line)
        total_words += 1
        line = fh.readline()
    fh1.close()
    fh2.close()
    os.remove(a+str(1)+b)

if __name__=="__main__":
    ti = 0
    all_files = os.listdir("../inverted_indexes/2019101021")
    for i in reversed(sorted(all_files)):
        if "index" in i:
            ti +=1
    ti +=1
    while(ti>2):
        for i in range(1,ti,2):
            if(i+1 == ti):
                print(c + str(i))
                os.rename(a+str(i)+b,a+str((i+1)//2)+b)
            else:
                print(c+ str(i) + " || " + c + str((i+1)))
                merge_files(i,i+1)
                os.rename(a+str(i)+b,a+str((i+1)//2)+b)
                os.remove(a+str(i+1)+b)
        if(ti%2 == 0):
            ti = ((ti+1)//2)+1
        else:
            ti = (ti+1)//2
    write_stats()
    split_files()
    write_total_lines()
