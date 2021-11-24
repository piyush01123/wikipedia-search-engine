
import xml.sax
import sys
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict
import re
import time
import os
import operator


def FinalIndexCreator(data, finalCount, offsetSize):
	body = defaultdict(dict)
	title = defaultdict(dict)
	info = defaultdict(dict)
	distinctWords = []
	link = defaultdict(dict)
	reference = defaultdict(dict)
	category = defaultdict(dict)
	offset = []

	for key in sorted(data.keys()):
		temp = []
		docs = data[key]

		for i in range(len(docs)):
			docID = re.sub(r'.*d([0-9]*).*', r'\1', docs[i])
			temp = re.sub(r'.*t([0-9]*).*', r'\1', docs[i])
			posting = docs[i]

			if temp != docs[i]:
				temp=float(temp)
				title[key][docID] = temp

			temp = re.sub(r'.*b([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				body[key][docID] = temp

			temp = re.sub(r'.*i([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				info[key][docID] = temp

			temp = re.sub(r'.*c([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				category[key][docID] = temp

			temp = re.sub(r'.*l([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				link[key][docID] = temp

			temp = re.sub(r'.*r([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				reference[key][docID] = temp

		distinctWords.append(key + ' ' + str(finalCount) + ' ' + str(len(docs)))
		offset.append(str(offsetSize))
		offsetSize += len(key + ' ' + str(finalCount) + ' ' + str(len(docs))) + 1

	titleData = list()
	titleOffset = list()
	prevTitle = 0

	bodyData = list()
	bodyOffset = list()
	prevBody = 0

	infoData = list()
	infoOffset = list()
	prevInfo = 0

	linkData = list()
	linkOffset = list()
	prevLink = 0

	categoryOffset = list()
	categoryData = list()
	prevCategory = 0

	referenceOffset = list()
	referenceData = list()
	prevReference = 0

	for key in sorted(data.keys()):
		if key in title:
			string = key + ' '
			docs = sorted(title[key], key = title[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(title[key][docs[i]]) + ' '
			titleOffset.append(str(prevTitle) + ' ' + str(len(docs)))
			titleData.append(string)
			prevTitle += len(string) + 1

		if key in body:
			string = key + ' '
			docs = sorted(body[key], key = body[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(body[key][docs[i]]) + ' '
			bodyOffset.append(str(prevBody) + ' ' + str(len(docs)))
			bodyData.append(string)
			prevBody += len(string) + 1

		if key in info:
			string = key + ' '
			docs = sorted(info[key], key = info[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(info[key][docs[i]]) + ' '
			infoOffset.append(str(prevInfo) + ' ' + str(len(docs)))
			infoData.append(string)
			prevInfo += len(string) + 1

		if key in category:
			string = key + ' '
			docs = sorted(category[key], key = category[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(category[key][docs[i]]) + ' '
			categoryOffset.append(str(prevCategory) + ' ' + str(len(docs)))
			categoryData.append(string)
			prevCategory += len(string) + 1

		if key in link:
			string = key + ' '
			docs = sorted(link[key], key = link[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(link[key][docs[i]]) + ' '
			linkOffset.append(str(prevLink) + ' ' + str(len(docs)))
			linkData.append(string)
			prevLink += len(string) + 1

		if key in reference:
			string = key + ' '
			docs = sorted(reference[key], key = reference[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(reference[key][docs[i]]) + ' '
			referenceOffset.append(str(prevReference) + ' ' + str(len(docs)))
			referenceData.append(string)
			prevReference += len(string) + 1

	with open('./data/offset_b' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(bodyOffset))
	with open('./data/b' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(bodyData))

	with open('./data/offset_i' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(infoOffset))
	with open('./data/i' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(infoData))

	with open('./data/offset_t' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(titleOffset))
	with open('./data/t' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(titleData))

	with open('./data/offset_l' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(linkOffset))
	with open('./data/l' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(linkData))

	with open('./data/offset_r' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(referenceOffset))
	with open('./data/r' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(referenceData))

	with open('./data/offset_c' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(categoryOffset))
	with open('./data/c' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(categoryData))

	with open('./data/vocab.txt', 'a') as file:
		file.write('\n'.join(distinctWords))
		file.write('\n')

	with open('./data/offset.txt', 'a') as file:
		file.write('\n'.join(offset))
		file.write('\n')

	finalCount=finalCount+1
	return finalCount, offsetSize


def merge_files(fileCount):
	flag = [0] * fileCount
	count = 0
	offsetSize = 0
	finalCount = 0
	data = defaultdict(list)
	array = list()
	words = {}
	files = {}
	top = {}

	for i in range(fileCount):
		files[i] = open('./data/index' + str(i) + '.txt', 'r')
		top[i] = files[i].readline().strip()
		flag[i] = 1
		words[i] = top[i].split()
		first = words[i][0]
		if first not in array:
			array.append(words[i][0])
	array.sort()
	while any(flag):
		count += 1
		temp = array[0]
		array.pop(0)
		if not count%100000:
			rrr = finalCount
			finalCount, offsetSize = FinalIndexCreator(data, finalCount, offsetSize)
			oldFileCount=rrr
			if oldFileCount != finalCount:
				data = defaultdict(list)
		for i in range(fileCount):
			if flag[i] and words[i][0] == temp:
				top[i] = files[i].readline()
				data[temp].extend(words[i][1:])
				top[i] = top[i].strip()
				if len(top[i]) == 0:
					print("SFFD")
					files[i].close()
					flag[i] = 0
					os.remove('./data/index' + str(i) + '.txt')
				else:
					words[i] = top[i].split()
					first=words[i][0]
					if first not in array:
						array.append(words[i][0])
						array.sort()
	finalCount, offsetSize = FinalIndexCreator(data, finalCount, offsetSize)


def main():
	with open('./data/file_count.txt','r') as f:
		file_count = int(f.read())
	merge_files(file_count)


if __name__ == '__main__':
	main()
