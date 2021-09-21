from nltk.corpus import stopwords
from datetime import datetime
from Stemmer import Stemmer
from bisect import bisect
import random
import math
import sys
import re
import os

up_lim = 5000
total_docs = 21384756
index_loc = ""
other = ["gt","lt","quot","amp","apos","eacute"]
stop_dict = {}
searching_words = []
zero = ord('0')
fields_dict = {'t':0, 'i':1, 'b':2, 'c':3, 'l':4, 'r':5}
writing_list = []
scores = [195,27,10,7,8,7]
fields = ['t', 'i', 'b', 'c', 'l', 'r']

class searching():
    def __init__(self,queries):
        self.queries = queries
        self.ps = Stemmer('porter')
        self.doc_dict = {}
        self.start = datetime.now()

    def search(self):
        for i in self.queries:
            self.start = datetime.now()
            temp = i.split(":")
            if(len(temp)>1):
                # field query
                self.search_field(i.lower())
            else:
                # normal query
                self.search_normal(i.lower())
            self.doc_dict = {}
        self.write_to_file()
    
    def tok(self,text):
        tok_text = re.split(r'[^0-9a-z]+', text)
        temp_list = []
        for w in tok_text :
            if w not in stop_dict and len(w)>1:
                sword = self.ps.stemWord(w)
                temp_list.append(sword)
        return temp_list

    def ret_pos(self,word):
        pos = bisect(searching_words,(word.strip()+"\n"))-1
        if(pos < 0): return []
        data = open("../inverted_indexes/wii/index_"+str(pos)+".txt","r+").readlines()
        for i in data:
            temp = i.split("-")
            if(temp[0]==word.rstrip()):
                docs = (temp[1].rstrip()).split("d")
                return docs[1:]
        return []

    def ret_docnum(self,d):
        temp = len(d)-1
        for i in range(len(d)):
            if((ord(d[i])-zero<0) or (ord(d[i])-zero>9)):
                temp = i
                break
        return int(d[0:temp])

    def ret_tally(self,d):
        flag=0
        curr='d'
        tally = ['']*6
        for i in d:
            if i in fields:
                flag=flag+1
                curr=i
            elif flag and (i not in fields):
                tally[fields_dict[curr]]=i+tally[fields_dict[curr]]
        for i in range(6):
            if len(tally[i])>0: tally[i] = int(tally[i])*(scores[i])
            else : tally[i]=0
        return tally

    def writing_part(self,val):
        global writing_list
        title_f = val//up_lim
        title_pos = (val%up_lim)-1
        with open("../inverted_indexes/wii/title_"+str(title_f) + ".txt","r") as fp:
            for i,line in enumerate(fp):
                if(i==title_pos):
                    writing_list.append(str(val) + ", " + line)

    def write_to_list(self):
        global writing_list
        count = 0
        for i in sorted(self.doc_dict.items(), key=lambda item: item[1],reverse=True):
            if(count < min(10,len(self.doc_dict))):
                self.writing_part(i[0])
                count+=1
        for i in range(count,10):
            doc_val = random.randint(1,total_docs-3)
            self.writing_part(doc_val)
        b = datetime.now()
        writing_list.append(str(b-self.start)+"\n\n")

    def sep_fields(self,query):
        temp = query.split(":")
        dcit = []
        n = len(temp)-2
        for i in range(n):
            dcit.append([temp[i][-1],temp[i+1][:-1]])
        dcit.append([temp[n][-1],temp[n+1]])
        return dcit

    def up_doc_dict(self,doc_id,sum_tally,idf):
        if(doc_id in self.doc_dict):
            self.doc_dict[doc_id] += idf*math.log2(sum_tally)
        else:
            self.doc_dict[doc_id] = idf*math.log2(sum_tally)

    def search_field(self,query):
        fild_lis = self.sep_fields(query)
        for i in fild_lis:
            pseudo_query = self.tok(i[1])
            for w in  pseudo_query:
                docs = self.ret_pos(w)
                if(len(docs)>0):
                    idf = math.log2(total_docs/len(docs))
                    for d in docs:
                        doc_id = self.ret_docnum(d)
                        tally = self.ret_tally(d)
                        tally[fields_dict[i[0]]]*=10000
                        self.up_doc_dict(doc_id,sum(tally),idf)
        self.write_to_list()

    def search_normal(self,query):
        query = self.tok(query)
        for w in query:
            docs = self.ret_pos(w)
            if(len(docs)>0):
                idf = math.log2(total_docs/len(docs))
                for d in docs:
                    doc_id = self.ret_docnum(d)
                    tally = self.ret_tally(d)
                    self.up_doc_dict(doc_id,sum(tally),idf)
        self.write_to_list()

    def write_to_file(self):
        fh = open("./queries_op.txt",'w+')
        for i in writing_list:
            fh.write(i)

if __name__ == '__main__':
    stop_words = stopwords.words('english')
    for i in stop_words:
        stop_dict[i]=True
    for i in other:
        stop_dict[i]=True
    # sys.argv[1] --> folder location where indexes are stored
    index_loc = sys.argv[1]
    searching_words = open(os.path.join(index_loc,"index_word.txt")).readlines()
    # sys.argv[2] --> location of the queries
    query_loc = sys.argv[2]
    queries = (open(query_loc,'r+')).readlines()
    search_class = searching(queries)
    search_class.search()
