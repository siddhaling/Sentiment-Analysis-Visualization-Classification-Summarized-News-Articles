from vader import SentimentIntensityAnalyzer
from textSummarizationForNewsArticle_1 import mainSummaryCalling
import numpy as np
import os
import re
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
import xlsxwriter

stopWords = set(stopwords.words('english'))
stopWords.update(['"', "'", ':', '(', ')', '[', ']', '{', '}']) #'.',  ',', '?', '!', ';'
#path name containing the news files
bbcNewsFldr='BBCNews'

#Identify the noun position
def getNounPositions(type,tagged):
    nounPosi={}
    for item in tagged:
        if item[1]==type:
            nounPosi[item[0]]=-1
    
    for key in nounPosi.keys():
        regExpression=r'\b'+key.lower()+r'\b'
        nounsi=[m.start() for m in re.finditer(regExpression, lineIn.lower())]
        nounPosi[key]=nounsi
    return nounPosi
#obtain words from sentence
def getWords(sentence):
	return word_tokenize(sentence)

#using pos_tag obtain the tags for words
def getTagsForWords(textLn2):
    tokens=word_tokenize(textLn2)
    tagged=pos_tag(tokens)
    return(tagged)
#remove stop words
def stopwordRemove(wordlist):
	stopword_list = set(stopwords.words('english'))
	return [stopped for stopped in wordlist if stopped not in stopword_list]
#get top three nouns and their frequency
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

#read text into a single file
def readFromSingleFile(fullFileNm):
    newsContent=[]
    dataFile=open(fullFileNm)
    for l in dataFile:
        print(len(l))
        if(len(l)<=1):
            continue
        newsContent.append(l.rstrip('\n'))
    dataFile.close()
    return newsContent

#write the sentiment informaiton to a file
def writeToExclNounSenti(sentiment_scoresForAnArticle):
    row=0
    col=0
    workbook=xlsxwriter.Workbook('sentimentStaticsAfterSummary.xlsx')
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

cnt=0
percentageOfSummary=[i for i in range(100,0,-10)]
positiveScores=[]
negativeScores=[]
compoundScores=[]
sentiment_scoresForAnArticle=[]
#read the files from give path
for filename in os.listdir(bbcNewsFldr):    
    cnt=cnt+1
    if (cnt>1): 
        break
    text=readFromSingleFile(bbcNewsFldr+'/'+filename)
    lineIn='\n'.join(text)
    
    tagged=getTagsForWords(lineIn)
    NNP=getNounPositions('NNP',tagged)
    top3Noun=getTop3NounAndFreq(NNP)
    #perform the summarization multiple time and compute sentiment information each time
    for pi in percentageOfSummary:
        reducedSummaryWithReplc=mainSummaryCalling(lineIn,pi)    
        review_tokens = [getWords(asdf.lower()) for asdf in reducedSummaryWithReplc]
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
        positiveScores.append(sentiment_scores['posScore'])
        negativeScores.append(sentiment_scores['negScore'])
        compoundScores.append(sentiment_scores['compoundScore'])
        sentiment_scoresForAnArticle.append([top3Noun,sentiment_scores])
        print(sentiment_scores['posScore'])
#write the sentiment information to excel
writeToExclNounSenti(sentiment_scoresForAnArticle)