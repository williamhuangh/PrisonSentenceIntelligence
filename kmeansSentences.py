import csv
import math
import collections
import numpy as np
import util
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


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
                int(util.convertSentenceToDays(prisonTerm))))


def tuplesCreator():
    sentenceClusterArrayPrev = []
    sentenceClusterArrayCurrent = []
    with open('INMATE_ACTIVE_OFFENSES_prpr.csv', 'rb') as csvfile:
        previousOffensesReader = csv.reader(csvfile)
        addPreviousOffenses(previousOffensesReader, sentenceClusterArrayPrev)
    with open('INMATE_ACTIVE_OFFENSES_CPS.csv', 'rb') as csvfile:
        currentOffensesReader = csv.reader(csvfile)
        addCurrentOffenses(currentOffensesReader, sentenceClusterArrayCurrent)
    return (sentenceClusterArrayPrev, sentenceClusterArrayCurrent)


def createCrimeSentenceDict(crimeArray):
    crimeSentenceDict = {}
    for crime, sentenceLength in crimeArray:
        if crime in crimeSentenceDict:
            crimeSentenceDict[crime].append(sentenceLength)
        else:
            crimeSentenceDict[crime] = [sentenceLength]
    return crimeSentenceDict


def createSentenceVectorDict(crimeDict):
    sentenceVectorDict = {}
    for crime in crimeDict:
        median = np.median(crimeDict[crime])
        mean = np.mean(crimeDict[crime])

        b = collections.Counter(crimeDict[crime])
        mode, numAppearances = b.most_common(1)[0]
        sentenceVectorDict[crime] = [mode, median, mean]
    return sentenceVectorDict


def createCrimeToClusterMap(clusterToCrimeMap):
    crimeToClusterMap = {}
    # Maps crime to array of all instances of clusters it falls under
    for cluster in clusterToCrimeMap:
        for crime in clusterToCrimeMap[cluster]:
            if crime in crimeToClusterMap:
                crimeToClusterMap[crime].append(cluster)
            else:
                crimeToClusterMap[crime] = [cluster]

    # Maps the crime to a single cluster based on the mode of the clusters it falls under
    for crime in crimeToClusterMap:
        clusters = crimeToClusterMap[crime]
        b = collections.Counter(clusters)
        mode, numAppearances = b.most_common(1)[0]
        crimeToClusterMap[crime] = mode

    return crimeToClusterMap


def getCrimeToClusterMap(crimes, clusters = 20):
    X = []
    for crime, sentenceLength in crimes:
        X.append([sentenceLength])
    estimator = KMeans(n_clusters=clusters)
    estimator.fit(X)

    clusterToCrimeMap = {}
    for crimeIndex, label in enumerate(estimator.labels_):
        crime, sentenceLength = crimes[crimeIndex]
        if label in clusterToCrimeMap:
            clusterToCrimeMap[label].append(crime)
        else:
            clusterToCrimeMap[label] = [crime]

    crimeToClusterMap = createCrimeToClusterMap(clusterToCrimeMap)

    # print estimator.cluster_centers_
    return crimeToClusterMap



def main():
    pastCrimes, currentCrimes = tuplesCreator()
    pastCrimesClusterMap = getCrimeToClusterMap(pastCrimes)
    currentCrimesClusterMap = getCrimeToClusterMap(currentCrimes)

    w = csv.writer(open("prevCrimeClusters.csv", "w"))
    for key, val in pastCrimesClusterMap.items():
        w.writerow([key, val])

    w = csv.writer(open("currentCrimeClusters.csv", "w"))
    for key, val in currentCrimesClusterMap.items():
        w.writerow([key, val])




if __name__ == "__main__":
    main()