from nltk.corpus import stopwords
from Stemmer import Stemmer
from collections import defaultdict
import datetime
import xml.sax
import math
import sys
import re
import os

other = {"gt","lt","quot","amp","apos","eacute","infobox","http","www","com","reference","redirect",
        "references","reflist","also","see","wikisource","cite","url","category","defaultsort","name",
        "title","date","ref","list","image","images","web","https","org","author","short","first","archive",
        "archives","caption","jpg","type","types","new","titles","description","page","article","articles",
        "wikipedia","edit","size","file","index","captions","id","pages","stub","publish","include",
        "commons","00"}

upper_limit = 20000000
file_index = 1
doc_id = 0
req_dict = defaultdict(dict)
stop_dict = {}
total_count = 0
dict_count = 0
titles = []
title_limit = 5000

class wikihandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.title = ""
        self.text = ""
        self.ps = Stemmer('porter')
        self.title_file = open("../inverted_indexes/wii/title_0.txt",'w+')
        self.cur_til = 0

    # when start tag is reached :
    def startElement(self, name, attrs):
        self.CurrentData = name

    # when end tag is reached :
    def endElement(self, name):
        global doc_id
        global file_index
        global req_dict
        global dict_count
        if(name == "page"):
            doc_id += 1
            self.createindex()
            self.write_title()
            self.text = ""
            self.title = ""
            temp = math.floor(total_count/upper_limit)
            if(temp >= file_index):
                print("Completed % : " + str((doc_id*100)/21384756))
                write2file(file_index)
                file_index+=1
                dict_count += len(req_dict)
                req_dict = defaultdict(dict)

    # if a word is read :
    def characters(self, content):
        if(self.CurrentData == "text"):
            self.text += content.lower()
        elif(self.CurrentData == "title"):
            self.title += content.lower()
    
    # stemming and tokenising :
    def stem_tok(self,text):
        global total_count
        tok_text = re.split(r'[^0-9a-z]+', text)
        temp_list = []
        for w in tok_text :
            if w not in stop_dict and len(w)<25:
                sword = self.ps.stemWord(w)
                if len(sword)>1:
                    temp_list.append(sword)
        total_count += len(temp_list)
        return temp_list

    def update_dict(self,words,val):
        for i in words:
            if doc_id not in req_dict[i]:
                req_dict[i][doc_id]=[0,0,0,0,0,0]
            req_dict[i][doc_id][val]+=1    
    
    def update_dict2(self,words,val):
        global req_dict
        for i in words:
            if (doc_id in req_dict[i]) and (req_dict[i][doc_id][val] > 0):
                req_dict[i][doc_id][val]-=1
    
    # create index for feild query
    def createindex(self):
        #remove comments:
        comments = self.text.split("!--")
        text = comments[0]
        for i in range(1,len(comments)):
            com = comments[i].split("--",1)
            if(len(com)>1):
                text += com[1]
        self.text = text

        # title :
        titles.append(self.title)
        tword = self.stem_tok(self.title)
        self.update_dict(tword,0)

        #body :
        filtered_n = filter(lambda x:x.lstrip()!="",self.text.split("\n"))
        bodies = " ".join(filter(lambda x:(x.lstrip()[0]!='|' and x.lstrip()[0]!="=" and x.lstrip()[0]!="["),filtered_n))
        bword = self.stem_tok(bodies)
        self.update_dict(bword,2)

        #infobox :
        infobox = self.text.split("{{infobox")
        if len(infobox) > 1:
            temp = len(infobox)
            for i in range(1,temp):
                info_t = infobox[i].split("}}\n", 1)
                iword = self.stem_tok(info_t[0])
                self.update_dict(iword,1)

        #category :
        categories = ' '.join(filter(lambda x:x.lstrip()[0]=="[",filtered_n))
        if categories:
            cword = self.stem_tok(' '.join(categories))
            self.update_dict(cword,3)

        #links :
        links = self.text.split("==external links==")
        if len(links) > 1:
            lin = ""
            links = re.split(r'[\n]',links[1])
            for line in links:
                if len(line)>0 and line and line[0] == '*':
                    lin += line+" "
            lword = self.stem_tok(lin)
            self.update_dict(lword,4)
            self.update_dict2(lword,2)

        #references :
        cate = "[[category"
        refs = self.text.split("==notes==")
        refer_w = ""
        if len(refs)>1 :
            refs = re.split(r"[\n]",refs[1])
            for j in refs:
                if  ("==" in j) or ("{{" in j) or (cate in j): break
                refer_w =refer_w+j+" "
            rword = self.stem_tok(refer_w)
            self.update_dict(rword,5)
            self.update_dict2(rword,2)
        
        refs = self.text.split("==bibliography==")
        refer_w = ""
        if len(refs)>1 :
            refs = re.split(r"[\n]",refs[1])
            for j in refs:
                if  ("==" in j) or ("{{" in j) or (cate in j): break
                refer_w =refer_w+j+" "
            rword = self.stem_tok(refer_w)
            self.update_dict(rword,5)
            self.update_dict2(rword,2)
        
        refs = self.text.split("==references==")
        refer_w = ""
        if len(refs)>1 :
            refs = re.split(r"[\n]",refs[1])
            for j in refs:
                if  ("==" in j) or ("{{" in j) or (cate in j): break
                refer_w =refer_w+j+" "
            rword = self.stem_tok(refer_w)
            self.update_dict(rword,5)
            self.update_dict2(rword,2)

    def write_title(self):
        global titles
        if(((doc_id-1)//title_limit) == self.cur_til):
            self.title_file.write(self.title.rstrip()+'\n')
        else:
            self.cur_til = (doc_id-1)//title_limit
            self.title_file.close()
            self.title_file = open("../inverted_indexes/wii/title_"+str(self.cur_til) + ".txt",'w+')
            self.title_file.write(self.title.rstrip()+'\n')
            titles = []

def write2file(file_index):
    fields = ['t', 'i', 'b', 'c', 'l', 'r']
    # location of saving files "../inverted_indexes/wii/"
    name_ = 'index' + str(file_index) + '.txt'
    fh = open(os.path.join("../inverted_indexes/wii",name_),'w+')
    for i in sorted(req_dict.keys()):
        fh.write(i+"-")
        for j in req_dict[i]:
            fh.write("d"+str(j))
            for k in range(6):
                if(req_dict[i][j][k]):
                    fh.write(fields[k]+str(req_dict[i][j][k]))
        fh.write("\n")

def write_stats():
    # location of stat.txt "./"
    fh2 = open("./stat.txt",'w+')
    fh2.write(str(total_count) + "\n" + str(file_index))

def check_directory():
    try: os.mkdir("../results")
    except: print("result directory already present")
    try: os.mkdir("../inverted_indexes")
    except: print("inverted_indexes folder already exists")
    os.system("rm -rf ../inverted_indexes/wii")
    os.mkdir("../inverted_indexes/wii")

if __name__=="__main__":
    check_directory()
    wikidump = sys.argv[1]
    stop_words = set(stopwords.words('english'))
    for i in stop_words:
        stop_dict[i]=True
    for i in other:
        stop_dict[i]=True
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = wikihandler()
    parser.setContentHandler(Handler)
    parser.parse(wikidump)
    write_stats()
    write2file(file_index)
