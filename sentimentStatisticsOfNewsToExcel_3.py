from vader import SentimentIntensityAnalyzer
import os
import re
import xlsxwriter
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords

#Folder containing BBC news articles. Only few samples kept here
bbcNewsFldr='BBCNews'

#collect all stop words
stopWords = set(stopwords.words('english'))
#update stop words
stopWords.update(['"', "'", ':', '(', ')', '[', ']', '{', '}']) #'.',  ',', '?', '!', ';'

#obtain the noun position in the text
def getNounPositions(type,tagged,lineIn):
    nounPosi={}
    for item in tagged:
        if item[1]==type:
            nounPosi[item[0]]=-1
    
    for key in nounPosi.keys():
        regExpression=r'\b'+key.lower()+r'\b'
        nounsi=[m.start() for m in re.finditer(regExpression, lineIn.lower())]
        nounPosi[key]=nounsi
    return nounPosi

#tokenize and obtain the words
def getWords(sentence):
	return word_tokenize(sentence)
#get tags for each word 
def getTagsForWords(textLn2):
    tokens=word_tokenize(textLn2)
    tagged=pos_tag(tokens)
    return(tagged)
#remove stop word from the word list
def stopwordRemove(wordlist):
	stopword_list = set(stopwords.words('english'))
	return [stopped for stopped in wordlist if stopped not in stopword_list]

#collect top 3 nouns based on their occurances
def getTop3NounAndFreq(NNP):
    top3Noun=[]*3
    nounSortedByFreq=sorted(NNP.items(), key=lambda item: len(item[1]), reverse=True)    
    for ni in range(len(nounSortedByFreq)):
        if ni>2:
            break
        nounNm=nounSortedByFreq[ni][0]
        freqNm=len(nounSortedByFreq[ni][1])
        top3Noun.append((nounNm,freqNm))
    return(top3Noun)

#read the news text from a single file
def readFromSingleFile(bbcNewsFldr,fileNm):
    path=bbcNewsFldr+'/'+fileNm
    reviewContent=[]
    dataFile=open(path)
    for l in dataFile:
        print(len(l))
        if(len(l)<=1):
            continue
        reviewContent.append(l.rstrip('\n'))
    dataFile.close()
    return reviewContent

#write to excel the sentiment information about the text files
def writeToExclNounSenti(sentiment_scoresForAnArticle):
    row=0
    col=0
    workbook=xlsxwriter.Workbook('sentimentStatistics.xlsx')
    worksheet=workbook.add_worksheet()
    worksheet.write(row,col,'Article')
    worksheet.write(row,col+1,'NegScore')
    worksheet.write(row,col+2,'NeuScore')
    worksheet.write(row,col+3,'PosScore')
    worksheet.write(row,col+4,'CompScore')
    worksheet.write(row,col+5,'NumOfNegSentiWords')
    worksheet.write(row,col+6,'NumOfNeuSentiWords')
    worksheet.write(row,col+7,'NumOfPosSentiWords')
    row=row+1
    for  sei in sentiment_scoresForAnArticle:
        print(row,col,sei[1]['negScore'])
        worksheet.write(row,col,str(sei[0]))
        worksheet.write(row,col+1,sei[1]['negScore'])
        worksheet.write(row,col+2,sei[1]['neuScore'])
        worksheet.write(row,col+3,sei[1]['posScore'])
        worksheet.write(row,col+4,sei[1]['compoundScore'])
        worksheet.write(row,col+5,sei[1]['numOfNegSentiWords'])
        worksheet.write(row,col+6,sei[1]['numOfNeuSentiWords'])
        worksheet.write(row,col+7,sei[1]['numOfPosSentiWords'])
        row+=1
    workbook.close()
    
#read all news files from given path and perform the sentiment analysis
cnt=0
sentiment_scoresForAnArticle=[]
for filename in os.listdir(bbcNewsFldr):    
    cnt=cnt+1
    text=readFromSingleFile(bbcNewsFldr,filename)
    lineIn='\n'.join(text)
    tagged=getTagsForWords(lineIn)
    NNP=getNounPositions('NNP',tagged,lineIn)
    top3Noun=getTop3NounAndFreq(NNP)
    review_tokens = [getWords(asdf.lower()) for asdf in text]
    stopped_sent = [stopwordRemove(sentence) for sentence in review_tokens]
    sents = []
    for i in stopped_sent:
        asdf = ''
        for j in i:
            asdf = asdf + j + ' '
        sents.append(asdf)
    sid = SentimentIntensityAnalyzer()
    allReviews=' '.join(sent for sent in sents)
    sentiment_scores=sid.polarity_scores(allReviews)
    sentiment_scoresForAnArticle.append([top3Noun,sentiment_scores])


#write the sentiment informaiton to excel file
writeToExclNounSenti(sentiment_scoresForAnArticle)
