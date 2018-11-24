import numpy as np
import os
import re
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from collections import Counter

bbcNewsFldr='BBCNews'
#fetch stop words
stopWords = set(stopwords.words('english'))
#update stop words
stopWords.update(['"', "'", ':', '(', ')', '[', ']', '{', '}']) #'.',  ',', '?', '!', ';'

#using pos_tag get the tag of words
def getTagsForWords(textLn2):
    tokens=word_tokenize(textLn2)
    tagged=pos_tag(tokens)
    return(tagged)

#remove stop words
def remStopWordsOur(lineIn):
    stopWords= {'i','a','and','about','an','are','as','at','be','by','com','for','from','how','in','is','it','not','of','on','or','that','the','this','to','was','what','when','where','who','will','with','the','www','your','is','am','some','you','your','I','A','And','About','An','Are','As','At','Be','By','Com','For','From','How','In','Is','It','Not','Of','On','Or','That','The','This','To','Was','What','When','Where','Who','Will','With','The','Www','Your','Is','Am','Some','You','Your','Was'}
    rmdStopWordsLn = ' '.join(w for w in lineIn.split() if w.lower() not in stopWords)
    return rmdStopWordsLn

#preprocessing the text and remove special characters
def preprocessText(lineIn):
    lineInLower=lineIn.lower()
    lineInRmdSplChars=lineInLower.replace('.',' ').replace(';',' ').replace(',',' ').replace('?',' ').replace('!',' ').replace(':',' ')
    return lineInRmdSplChars

#Divide the given text into lines
def getAllLines(lineIn):
    lineInReplcByPeriod=lineIn.replace('.','.§').replace(';',';§').replace(',',',§').replace('?','?§').replace('!','!§').replace('\n','§')
    linesOriginal=lineInReplcByPeriod.split('§')
    linesOriginal2=[item for item in linesOriginal if len(item)>0 ]
    return linesOriginal2

#Identify the noun position
def getNounPositions(type,tagged,lineIn):
    nounPosi={}
    for item in tagged:
        if item[1]==type and item[0]!='[' and item[0]!=']':
            nounPosi[item[0]]=-1
    
    for key in nounPosi.keys():
        print('key=',key)
        regExpression=r'\b'+key.lower()+r'\b'
        nounsi=[m.start() for m in re.finditer(regExpression, lineIn.lower())]
#        print(key,nounsi)
        nounPosi[key]=nounsi
    return nounPosi

#Identify the pronoun position
def getProNounPositions(tagged,lineIn):
    proNounPosi={}
    for item in tagged:
        if item[1]=='PRP': #or item[1]=='PRP$':
            proNounPosi[item[0].lower()]=-1
    
    for key in proNounPosi.keys():
        regExpression=r'\b'+key.lower()+r'\b'
        pronounsi=[m.start() for m in re.finditer(regExpression, lineIn.lower())]
#        print(key,pronounsi)
        proNounPosi[key]=pronounsi
    return proNounPosi

#Obtain nearest previous noun
def getNearestPreviousNoun(NNP,posiOfPronoun,lineIn):
#    print('\t',NNP)    
    minimumDiff=len(lineIn)
    nearKey=''
    for keyNNP in NNP.keys():
        for posNoun in NNP[keyNNP]:
            if(posiOfPronoun>posNoun):
#                print('\t',posiOfPronoun-posNoun)
                if(minimumDiff>(posiOfPronoun-posNoun)):
                    minimumDiff=posiOfPronoun-posNoun
                    nearKey=keyNNP
#    print('\t near key=',nearKey)
    return nearKey

#Replace pronoun by noun
def pronounReplaceWithNearNoun(lineIn,PRP,NNP):
    replacePRP=[]       
    for key in PRP.keys():            
        for pos in PRP[key]:
            print('---------',key,'------',pos ,'-----')
            nearNoun=getNearestPreviousNoun(NNP,pos,lineIn)
            replacePRP.append((key,pos,nearNoun))  
    
    replacePRP=sorted(replacePRP,key=lambda x:(-x[1],x[0],x[2]))
    lineInReplacePronn=lineIn
    for prpRep in replacePRP:
        lineInReplacePronn=lineInReplacePronn[:prpRep[1]]+prpRep[2]+lineInReplacePronn[prpRep[1]+len(prpRep[0]):]
    return lineInReplacePronn

#Based on weightage obtain the priority of lines
def obtainPriorotyOfALine(wtForLine):
    orderdLinesByWt=np.argsort(wtForLine)
    orderdLinesByWt=orderdLinesByWt[::-1]
    priority=[0]*len(wtForLine)
    
    for i in range(len(wtForLine)):
        priority[orderdLinesByWt[i]]=i
    
    sentWtAndPriority=[]    
    for i in range(len(wtForLine)):
        sentWtAndPriority.append((wtForLine[i],priority[i]))
    
    return sentWtAndPriority
#Construct summary by extraction method
def obtainSummary(lineForCalc,lineForExtract,percentageOfSummary,freqOfWords):
    wtForLine=[0]*len(lineForCalc)
    print('Calcualting wt for lines......')
    for li in range(len(lineForCalc)):
    
        wtForLn=0.0
        preproccdLn2=preprocessText(lineForCalc[li])
        wInL=preproccdLn2.split()
        for w in wInL:            
            w=preprocessText(w)
            if w in list(freqOfWords.keys()):    
                wtForLn=wtForLn+freqOfWords[w]
        if(len(wInL)>0):
            wtForLine[li]=(wtForLn/len(wInL))
        else:
            wtForLine[li]=0
        
    sentWtAndPriority=obtainPriorotyOfALine(wtForLine)
    print(sentWtAndPriority)
    numOfLinesInSummary=int((percentageOfSummary*len(lineForCalc))/100)
    reducedSummary=[]
    for li in range(len(lineForExtract)):
        if(sentWtAndPriority[li][1]<numOfLinesInSummary):    
            reducedSummary.append(lineForExtract[li])
    return reducedSummary

#remove week nm and month name
def removeWeekNmMonthNm(NNP):
    entries = ('january','february','march','april','may','june','july','august','september','october','november','december','monday','tuesday','wednesday','thursday','friday','saturday','sunday')
    delKeys=[]
    for key in NNP.keys():
        if key.lower() in entries:
            print(key)
            delKeys.append(key)
    
    for key in delKeys:
        del NNP[key]
    return NNP


#create summary of given text
def mainSummaryCalling(lineIn,percentageOfSummary):
    linePreProcessed=preprocessText(lineIn)
    rmdStopWordsLn= ' '.join(i for i in linePreProcessed.split() if i not in stopWords)
    nt=len(rmdStopWordsLn.split())
    freqOfWords = Counter(re.split(r'\s+',re.sub(r'[.,;\-!?]','',rmdStopWordsLn)))
    for word, freq in freqOfWords.items():          
        freqOfWords[word]=freqOfWords[word]/nt
    print(freqOfWords)
    tagged=getTagsForWords(lineIn)
    NNP=getNounPositions('NNP',tagged,lineIn)
    
    NNP=removeWeekNmMonthNm(NNP)
    PRP=getProNounPositions(tagged,lineIn)
    
    linesOriginal2=getAllLines(lineIn)
    lineInReplacePronn=pronounReplaceWithNearNoun(lineIn,PRP,NNP)
    linesReplacedPronn2=getAllLines(lineInReplacePronn)
    print(percentageOfSummary)
    
    reducedSummaryWithReplc=obtainSummary(linesReplacedPronn2,linesOriginal2,percentageOfSummary,freqOfWords)    
    return (reducedSummaryWithReplc)

#read a file from the given folder and determine its summary
cnt=0
percentageOfSummary=75
for filename in os.listdir(bbcNewsFldr):
    print(filename)
    fileIn=open(bbcNewsFldr+'/'+filename,"r")
    lineIn = fileIn.read()
    reducedSummaryWithReplc=mainSummaryCalling(lineIn,percentageOfSummary)
    reducedSummaryWithReplcText='\n'.join(item for item in reducedSummaryWithReplc)
    print(reducedSummaryWithReplcText)
    fileIn.close()
    