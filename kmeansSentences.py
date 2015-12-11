import csv
import math
import collections
import numpy as np
import util
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def createCrimeSentenceDict(crimeArray):
    crimeSentenceDict = {}
    for crime, sentenceLength in crimeArray:
        if crime in crimeSentenceDict:
            crimeSentenceDict[crime].append(sentenceLength)
        else:
            crimeSentenceDict[crime] = [sentenceLength]
    return crimeSentenceDict


def createCrimeSentenceMedians(crimeDict):
    crimeSentenceMediansDict = {}
    for crime in crimeDict:
        median = np.median(crimeDict[crime])
        mean = np.mean(crimeDict[crime])

        b = collections.Counter(crimeDict[crime])
        mode, numAppearances = b.most_common(1)[0]
        crimeSentenceMediansDict[crime] = [median, mean, mode]
    return crimeSentenceMediansDict


def createCrimeSentenceMeans(crimeDict):
    crimeSentenceMeansDict = {}
    for crime in crimeDict:
        mean = np.mean(crimeDict[crime])
        crimeSentenceMeansDict[crime] = mean
    return crimeSentenceMeansDict


def addCurrentOffenses(currentOffensesReader, sentenceClusterArray):
    attributes = []
    for row in currentOffensesReader:
        inmate_id = row[0]
        prisonTerm = row[6]
        crimeDescription = 'CURRENT_' + row[9]
        if inmate_id == 'DCNumber':
            attributes = [crimeDescription, prisonTerm]
        else:
            sentenceClusterArray.append((crimeDescription, \
                int(util.convertSentenceToDays(prisonTerm))))

def addPreviousOffenses(previousOffensesReader, sentenceClusterArray):
    attributes = []
    for row in previousOffensesReader:
        inmate_id = row[0]
        prisonTerm = row[6]
        crimeDescription = 'PREV_' + row[9]
        if inmate_id == 'DCNumber':
            attributes = [crimeDescription, prisonTerm]
        else:
            sentenceClusterArray.append((crimeDescription, \
                math.log(int(util.convertSentenceToDays(prisonTerm)))))


def tuplesCreator():
    sentenceClusterArrayPrev = []
    sentenceClusterArrayCurrent = []
    # with open('INMATE_ACTIVE_OFFENSES_prpr.csv', 'rb') as csvfile:
    #     previousOffensesReader = csv.reader(csvfile)
    #     addPreviousOffenses(previousOffensesReader, sentenceClusterArrayPrev)
    with open('INMATE_ACTIVE_OFFENSES_CPS.csv', 'rb') as csvfile:
        currentOffensesReader = csv.reader(csvfile)
        addCurrentOffenses(currentOffensesReader, sentenceClusterArrayCurrent)
    # return (sentenceClusterArrayPrev, sentenceClusterArrayCurrent)
    return sentenceClusterArrayCurrent


def main():
    currentOffenses = tuplesCreator()
    currentCrimeSentenceDict = createCrimeSentenceDict(currentOffenses)
    currentSentenceMediansDict = createCrimeSentenceMedians(currentCrimeSentenceDict)
    currentSentenceMeansDict = createCrimeSentenceMeans(currentCrimeSentenceDict)
    # print currentSentenceMeansDict

    X = []
    for crime in currentSentenceMediansDict:
        X.append(currentSentenceMediansDict[crime])
    X = np.array(X)
    estimator = KMeans(n_clusters=20, init='random')
    estimator.fit(X)
    estimators
    # clusterMap = {}
    # for crimeIndex, label in enumerate(estimator.labels_):
    #     crime, sentenceLength = currentOffenses[crimeIndex]
    #     if label in clusterMap:
    #         clusterMap[label].append(crime)
    #     else:
    #         clusterMap[label] = [crime]

    colors = cm.spectral(cluster_labels.astype(float) / n_clusters)
    ax2.scatter(X[:, 0], X[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                c=colors)

    print estimator.cluster_centers_

if __name__ == "__main__":
    main()