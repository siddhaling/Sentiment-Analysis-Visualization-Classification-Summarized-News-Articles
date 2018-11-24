from vader import SentimentIntensityAnalyzer
import numpy as np
import os
import re
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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


#perform 3D column chart of noun compound score and thier occurance
def plotMatrix3DColumnNounCompundScoreOccurence(sentiment_scoresForAnArticle):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    nElements=len(sentiment_scoresForAnArticle)
    xs=[i for i in range(nElements)]
    ys=[sei[0][0][1] for  sei in sentiment_scoresForAnArticle ]
    zs=[0]*nElements
    dx=[0.4]*nElements
    dy=[0.4]*nElements
    dz=[np.abs(sei[1]['compoundScore']) for  sei in sentiment_scoresForAnArticle ]
    colors_ar=[]
    for aSenti in sentiment_scoresForAnArticle:
        if aSenti[1]['compoundScore']>0:
            colors_ar.append('b')
        elif aSenti[1]['compoundScore']==0:
            colors_ar.append('g')
        else:
            colors_ar.append('r')    
    
    ax.bar3d(xs,ys,zs,dx,dy,dz,color=colors_ar)
    ax.plot([],[],color='b',label='Positve Sentiment')
    ax.plot([],[],color='g',label='Neutral Sentiment')
    ax.plot([],[],color='r',label='Negative Sentiment')
    nounNms=[sei[0][0][0] for sei in sentiment_scoresForAnArticle]
    #ax.set_xlabel('Noun')
    ax.set_xticklabels(nounNms)
    ax.set_ylabel('Num. of Noun Occurences')
    ax.set_zlabel('Compound Score')
    plt.legend()
    plt.show()    

#perform 3D column chart of noun, positive and negative score
def plotMatrix3DColumnNounPosiNegiScore(sentiment_scoresForAnArticle):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    nElements=len(sentiment_scoresForAnArticle)
    xs=[i for i in range(nElements)]
    ys=[sei[1]['negScore'] for  sei in sentiment_scoresForAnArticle]
    zs=[0]*nElements
    dx=[0.5]*nElements
    dy=[0.005]*nElements
    dz=[sei[1]['posScore'] for  sei in sentiment_scoresForAnArticle ] 
    colors_ar=['b']*nElements
    ax.bar3d(xs,ys,zs,dx,dy,dz,color=colors_ar)
    nounNms=[sei[0][0][0] for sei in sentiment_scoresForAnArticle]
    #ax.set_xlabel('Noun')
    ax.set_ylabel('Negative Score')
    ax.set_zlabel('Positive Score')
    ax.set_xticklabels(nounNms)
    ax.plot([],[],color='b',label='Positve Sentiment')
    plt.legend()
    plt.show()    


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

#perform sentiment informaiton 3D visualization
plotMatrix3DColumnNounPosiNegiScore(sentiment_scoresForAnArticle)
plotMatrix3DColumnNounCompundScoreOccurence(sentiment_scoresForAnArticle)