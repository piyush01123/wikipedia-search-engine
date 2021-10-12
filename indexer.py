import xml.sax
import sys
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict
import re
import time
import os
import operator

stop_words=set(stopwords.words('english'))
titles=[]
start_time=time.time()
index_map=defaultdict(list)
dictID={}
no_of_pages=0
file_count=0
offset=0

def create_index(title,body,infobox,categories,external_links,references):
	global no_of_pages
	global index_map
	global file_count
	global dictID
	global offset

	words=defaultdict(int)

	title_dict=defaultdict(int)
	for i in range(len(title)):
		title_dict[title[i]]+=1
		words[title[i]]+=1

	body_dict=defaultdict(int)
	for i in range(len(body)):
		body_dict[body[i]]+=1
		words[body[i]]+=1

	infobox_dict=defaultdict(int)
	for i in range(len(infobox)):
		infobox_dict[infobox[i]]+=1
		words[infobox[i]]+=1

	categories_dict=defaultdict(int)
	for i in range(len(categories)):
		categories_dict[categories[i]]+=1
		words[categories[i]]+=1

	external_links_dict=defaultdict(int)
	for i in range(len(external_links)):
		external_links_dict[external_links[i]]+=1
		words[external_links[i]]+=1

	references_dict=defaultdict(int)
	for i in range(len(references)):
		references_dict[references[i]]+=1
		words[references[i]]+=1

	no_of_pages+=1

	for word in words.keys():
            temp = 'd'+str(no_of_pages-1)
            if title_dict[word]:
                temp += 't' + str(title_dict[word])
            if body_dict[word]:
                temp += 'b' + str(body_dict[word])
            if infobox_dict[word]:
                temp += 'i' + str(infobox_dict[word])
            if categories_dict[word]:
                temp += 'c' + str(categories_dict[word])
            if external_links_dict[word]:
                temp += 'l' + str(external_links_dict[word])
            if references_dict[word]:
                temp += 'r' + str(references_dict[word])

            index_map[word].append(temp)

	if not no_of_pages%25000:
		write_into_temp_files()


def write_into_temp_files():
	global index_map
	global file_count
	global dictID
	global offset
	data=[]
	prev_title_offset=offset
	for key in sorted(index_map.keys()):
		postings = index_map[key]
		string = key + ' '
		string += ' '.join(postings)
		data.append(string)

	with open('./data/index' + str(file_count) + '.txt', 'w') as file:
		file.write('\n'.join(data))

	dataOffset = []
	data = []
	for key in sorted(dictID):
		dataOffset.append(str(prev_title_offset))
		temp = str(key) + ' ' + dictID[key].strip()
		data.append(temp)
		prev_title_offset += len(temp) + 1

	with open('./data/title.txt', 'a') as file:
		file.write('\n'.join(data))
		file.write('\n')

	with open('./data/titleOffset.txt', 'a') as file:
		file.write('\n'.join(dataOffset))
		file.write('\n')

	offset = prev_title_offset
	index_map = defaultdict(list)
	dictID={}
	file_count+=1

def final_processing(data):
	data=data.strip().encode("ascii",errors="ignore").decode()
	#data=re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',' ',data)
	data=re.sub(r'\`|\~|\!|\@|\#|\"|\'|\$|\%|\^|\&|\*|\(|\)|\-|\_|\=|\+|\\|\||\]|\[|\}|\{|\;|\:|\/|\?|\.|\>|\,|\<|\'|\n|\||\|\/"',r' ',data)
	data=re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;',r' ',data)
	#Above code removes any special character
	final_data=[]
	ss=SnowballStemmer('english')
	data=data.split()
	for w in data:
		if not w.strip() in stop_words:
			w=ss.stem(w)
			final_data.append(w)
	return final_data

def get_infobar(data):
	data=data.split('\n')
	length=len(data)
	ret=[]
	flag=0
	for i in range(length):
		if flag%2==0 and re.search(r'\{\{infobox',data[i]):
			flag=1
			ret.append(re.sub(r'\{\{infobox','',data[i]))
		elif flag%2==1:
			if data[i]=='}}':
				flag=flag+1
				continue
			ret.append(data[i])
		elif flag==0:
			if i*100/length > 50:
				break

	return final_processing(' '.join(ret))

def get_categories(data):
	data=re.findall(r'\[\[category:.*\]\]',data)
	ret=[]
	for i in data:
		ret.append(i[11:len(i)-2])

	return final_processing(' '.join(ret))

def get_external_links(text):
	data=text.split('==external links==')
	if len(data)==1:
		data=text.split('==external links ==')
	if len(data)==1:
		data=text.split('== external links==')
	if len(data)==1:
		data=text.split('== external links ==')
	if len(data)==1:
		return []
	data=data[1]
	data=re.findall(r'\*\s*\[.*\]',data)
	ret=[]
	for i in data:
		ret.append(i[2:len(i)-1])
	return final_processing(' '.join(ret))

def get_references(text):
	ret=[]
	data1=re.findall(r'\|\s*title[^\|]*',text)
	for i in data1:
		ret.append(i[i.find('=')+1:len(i)-1])
	return final_processing(' '.join(ret))

def process_text(text,title):
	text=text.lower()
	references=[]
	categories=[]
	external_links=[]
	data=text.split('==references==')
	if data[0]==text:
		data=text.split('==references ==')
	if data[0]==text:
		data=text.split('== references==')
	if data[0]==text:
		data=text.split('== references ==')
	if data[0]==text:
		categories=get_categories(data[0])
		external_links=get_external_links(data[0])
	else:
		categories=get_categories(data[1])
		external_links=get_external_links(data[1])
		references=get_references(data[1])

	info_bar=get_infobar(data[0])
	data[0]=re.sub(r'\{\{.*\}\}',r' ',data[0])
	body=final_processing(data[0])
	title=final_processing(title.lower())
	return title,body,info_bar,categories,external_links,references


class Handler(xml.sax.ContentHandler):
	def __init__(self):
		self.tag=""
		self.title=""
		self.text=""
		self.id=""
		self.idFlag=0#so that it does not read ids of revesion

	def startElement(self,name,attrs):
		self.tag=name

	def endElement(self,name):
		global no_of_pages
		if name=='page':
			self.title=self.title.strip().encode("ascii",errors="ignore").decode()
			dictID[no_of_pages]=self.title
			title,body,infobox,categories,external_links,references=process_text(self.text,self.title)
			create_index(title,body,infobox,categories,external_links,references)
			self.tag=""
			self.title=""
			self.text=""
			self.id=""
			self.idFlag=0

	def characters(self, content):
		if self.tag == 'text':
			self.text+=content
		if self.tag == 'title':
			self.title+=content
		if self.tag == 'id' and self.idFlag==0:
			self.id = content
			self.idFlag=1


def main():
	global no_of_pages
	global index_map
	global file_count
	global dictID
	global offset
	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces,False)
	handler = Handler()
	parser.setContentHandler(handler)
	output=parser.parse(sys.argv[1]) # argv[1] is supposed to be the big XML file.

	with open('./data/fileNumbers.txt','w') as f:
		f.write(str(no_of_pages))

	write_into_temp_files()

	print("File COunt:"+str(file_count))

	with open('./data/file_count.txt','w') as f:
		f.write(str(file_count))

if __name__ == '__main__':
	main()
