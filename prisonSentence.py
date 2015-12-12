import csv
import time
import datetime
import decimal
import numpy as np
import scipy
import math
import util
from sklearn.linear_model import SGDRegressor
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.utils import check_array
from sklearn import svm

def addIncarhist(incarhistReader, inmatesMap):
    for row in incarhistReader:
        inmate_id = row[0]
        incarcerationDate = row[1]
        releaseDate = row[2]
        if inmate_id != 'DCNumber' and releaseDate == '':
            inmatesMap[inmate_id]['IncarcerationDate'] = datetime.datetime(int(incarcerationDate[6:10]), int(incarcerationDate[0:2]), int(incarcerationDate[3:5]))

def addCurrentOffenses(currentOffensesReader, inmatesMap):
    for row in currentOffensesReader:
        inmate_id = row[0]
        offenseDate = row[2]
        county = row[4]
        prisonTerm = row[6]
        probationTerm = row[7]
        paroleTerm = row[8]
        crimeDescription = row[9]
        if inmate_id == 'DCNumber':
            attributes = [offenseDate, county, prisonTerm, probationTerm, paroleTerm, crimeDescription]
        else:
            currentTime = datetime.datetime(int(offenseDate[6:10]), int(offenseDate[0:2]), int(offenseDate[3:5]))
            offense = {attributes[0]: currentTime, 
                        attributes[1]: county, 
                        attributes[2]: util.convertSentenceToDays(prisonTerm),
                        attributes[3]: probationTerm, 
                        attributes[4]: paroleTerm, 
                        attributes[5]: crimeDescription}
            if 'CURRENT_OFFENSES' not in inmatesMap[inmate_id]:
                inmatesMap[inmate_id]['CURRENT_OFFENSES'] = [offense]
            else:
                inmatesMap[inmate_id]['CURRENT_OFFENSES'].append(offense)

def addPreviousOffenses(previousOffensesReader, inmatesMap):
    for row in previousOffensesReader:
        inmate_id = row[0]
        offenseDate = row[2]
        county = row[4]
        prisonTerm = row[6]
        probationTerm = row[7]
        paroleTerm = row[8]
        crimeDescription = row[9]
        if inmate_id == 'DCNumber':
            attributes = [offenseDate, county, prisonTerm, probationTerm, paroleTerm, crimeDescription]
        else:
            currentTime = datetime.datetime(int(offenseDate[6:10]), int(offenseDate[0:2]), int(offenseDate[3:5]))
            offense = {attributes[0]: currentTime, 
                        attributes[1]: county, 
                        attributes[2]: util.convertSentenceToDays(prisonTerm),
                        attributes[3]: probationTerm, 
                        attributes[4]: paroleTerm, 
                        attributes[5]: crimeDescription}
            if 'PREVIOUS_OFFENSES' not in inmatesMap[inmate_id]:
                inmatesMap[inmate_id]['PREVIOUS_OFFENSES'] = [offense]
            else:
                inmatesMap[inmate_id]['PREVIOUS_OFFENSES'].append(offense)

def addScars(scarsMarkReader, inmatesMap):
    for row in scarsMarkReader:
        inmate_id = row[0]
        if inmate_id != 'DCNumber':
            if 'TATTOOS' not in inmatesMap[inmate_id]:
                inmatesMap[inmate_id]['TATTOOS'] = 1
            else:
                inmatesMap[inmate_id]['TATTOOS'] += 1

def createInmates(rootReader, inmatesMap):
    attributes = []
    for row in rootReader:
        inmate_id = row[0]
        if inmate_id == 'DCNumber': # Get row headers
            for attribute in row:
                attributes.append(attribute)
        else:
            inmateAttributeMap = {}
            for i in range(1, len(row)):
                if attributes[i] == 'ReceiptDate' or attributes[i] == 'BirthDate' or (attributes[i] == 'PrisonReleaseDate' and row[i] != ''):
                    inmateAttributeMap[attributes[i]] = datetime.datetime(int(row[i][6:10]), int(row[i][0:2]), int(row[i][3:5]))
                # elif attributes[i] == 'PrisonReleaseDate':
                #     inmateAttributeMap[attributes[i]] = datetime.datetime(2100, 01, 01)
                else:
                    inmateAttributeMap[attributes[i]] = row[i]
            inmatesMap[inmate_id] = inmateAttributeMap # Map inmate DCNumber to their attributes


def mapCreator():
    inmatesMap = {}
    with open('INMATE_ACTIVE_ROOT.csv', 'rb') as csvfile:
        rootReader = csv.reader(csvfile)
        createInmates(rootReader, inmatesMap)
    with open('INMATE_ACTIVE_SCARSMARKS.csv', 'rb') as csvfile:
        scarsMarkReader = csv.reader(csvfile)
        addScars(scarsMarkReader, inmatesMap)
    with open('INMATE_ACTIVE_OFFENSES_prpr.csv', 'rb') as csvfile:
        previousOffensesReader = csv.reader(csvfile)
        addPreviousOffenses(previousOffensesReader, inmatesMap)
    with open('INMATE_ACTIVE_OFFENSES_CPS.csv', 'rb') as csvfile:
        currentOffensesReader = csv.reader(csvfile)
        addCurrentOffenses(currentOffensesReader, inmatesMap)
    with open('INMATE_ACTIVE_INCARHIST.csv', 'rb') as csvfile:
        incarhistReader = csv.reader(csvfile)
        addIncarhist(incarhistReader, inmatesMap)
    return inmatesMap

def createFeatureVector():
    featureVector = ['TATTOOS', 'Height0', 'Height450', 'Height470', 'Height490', 'Height510', 'Height530', 'Height550', 'Height570', 'Height590', 'Height610', 'Height610+', \
                    'Weight0', 'Weight100', 'Weight120', 'Weight140', 'Weight160', 'Weight180', 'Weight200', 'Weight220', 'Weight240', 'Weight240+', \
                    'Age6000', 'Age8400', 'Age10800', 'Age13200', 'Age15600', 'Age18000', 'Age20400', 'Age22800', 'Age25200', 'Age27600', 'Age30000', 'Age30000+' \
                    ]
    with open('eyecolor.txt', 'r') as f:
        for row in f:
            featureVector.append('EYE_' + row.rstrip('\n'))
    with open('haircolor.txt', 'r') as f:
        for row in f:
            featureVector.append('HAIR_' + row.rstrip('\n'))
    with open('races.txt', 'r') as f:
        for row in f:
            featureVector.append('RACE_' + row.rstrip('\n'))
    with open('sexes.txt', 'r') as f:
        for row in f:
            featureVector.append('SEX_' + row.rstrip('\n'))

	with open('offenses.txt', 'r') as f:
		for row in f:
			featureVector.append('PREV_' + row.rstrip('\n'))
			featureVector.append('CURRENT_' + row.rstrip('\n'))

    # numCrimeClusters = 20
    # for i in range(numCrimeClusters):
    #     name = "CRIME_CLUSTER_" + str(i)
    #     featureVector.append('PREV_' + name)
    #     featureVector.append('CURRENT_' + name)

    return featureVector


def getCrimeToClusterMap(filename):
    crimeToClusterMap = {}
    for key, val in csv.reader(open(filename)):
        crimeToClusterMap[key] = val
    return crimeToClusterMap


def extractFeatures(person, featureVector):
    currentCrimeToClusterMap = getCrimeToClusterMap("currentCrimeClusters.csv")
    prevCrimeToClusterMap = getCrimeToClusterMap("pastCrimeClusters.csv")

    currentOffenses = []
    if 'CURRENT_OFFENSES' in person:
        currentOffenses = person['CURRENT_OFFENSES']
    pastOffenses = []
    if "PREVIOUS_OFFENSES" in person:
        pastOffenses = person['PREVIOUS_OFFENSES']
    inmateVector = []
    for feature in featureVector:
        if feature[0:4] == "EYE_":
            if person["EyeColor"] == feature[4:]:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:5] == "HAIR_":
            if person["HairColor"] == feature[5:]:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:5] == "RACE_":
            if person["Race"] == feature[5:]:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:4] == "SEX_":
            if person["Sex"] == feature[4:]:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:5] == "PREV_":
            total = 0
            for offense in pastOffenses:
                if offense['adjudicationcharge_descr'] == feature[5:]:
                    total += 1
            inmateVector.append(total)
        elif feature[0:8] == "CURRENT_":
            total = 0
            for offense in currentOffenses:
                if offense['adjudicationcharge_descr'] == feature[8:]:
                    total += 1
            inmateVector.append(total)
        elif feature[0:6] == "Height":
            if person[feature[0:6]]:
                height = float(person[feature[0:6]])
            if feature[6:] == '0' and person[feature[0:6]] == '':
                inmateVector.append(1)
            elif feature[6:] == '450' and person[feature[0:6]] != '' and height <= 450 and height > 0:
                inmateVector.append(1)
            elif feature[6:] == '470' and person[feature[0:6]] != '' and height <= 470 and height > 450:
                inmateVector.append(1)
            elif feature[6:] == '490' and person[feature[0:6]] != '' and height <= 490 and height > 470:
                inmateVector.append(1)
            elif feature[6:] == '510' and person[feature[0:6]] != '' and height <= 510 and height > 490:
                inmateVector.append(1)
            elif feature[6:] == '530' and person[feature[0:6]] != '' and height <= 530 and height > 510:
                inmateVector.append(1)
            elif feature[6:] == '550' and person[feature[0:6]] != '' and height <= 550 and height > 530:
                inmateVector.append(1)
            elif feature[6:] == '570' and person[feature[0:6]] != '' and height <= 570 and height > 550:
                inmateVector.append(1)
            elif feature[6:] == '590' and person[feature[0:6]] != '' and height <= 590 and height > 570:
                inmateVector.append(1)
            elif feature[6:] == '610' and person[feature[0:6]] != '' and height <= 610 and height > 590:
                inmateVector.append(1)
            elif feature[6:] == '610+' and person[feature[0:6]] != '' and height > 610:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:6] == "Weight":
            if person[feature[0:6]]:
                weight = float(person[feature[0:6]])
            if feature[6:] == '0' and person[feature[0:6]] == '':
                inmateVector.append(1)
            elif feature[6:] == '100' and person[feature[0:6]] != '' and weight <= 100 and weight > 0:
                inmateVector.append(1)
            elif feature[6:] == '120' and person[feature[0:6]] != '' and weight <= 120 and weight > 100:
                inmateVector.append(1)
            elif feature[6:] == '140' and person[feature[0:6]] != '' and weight <= 140 and weight > 120:
                inmateVector.append(1)
            elif feature[6:] == '160' and person[feature[0:6]] != '' and weight <= 160 and weight > 140:
                inmateVector.append(1)
            elif feature[6:] == '180' and person[feature[0:6]] != '' and weight <= 180 and weight > 160:
                inmateVector.append(1)
            elif feature[6:] == '200' and person[feature[0:6]] != '' and weight <= 200 and weight > 180:
                inmateVector.append(1)
            elif feature[6:] == '220' and person[feature[0:6]] != '' and weight <= 220 and weight > 200:
                inmateVector.append(1)
            elif feature[6:] == '240' and person[feature[0:6]] != '' and weight <= 240 and weight > 220:
                inmateVector.append(1)
            elif feature[6:] == '240+' and person[feature[0:6]] != '' and weight > 240:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:3] == "Age":
            bday = person["BirthDate"]
            incarcerated = person["ReceiptDate"]
            age = (incarcerated - bday).days
            if feature[3:] == '6000' and age <= 6000:
                inmateVector.append(1)
            elif feature[3:] == '8400' and age <= 8400 and age > 0:
                inmateVector.append(1)
            elif feature[3:] == '10800' and age <= 10800 and age > 8400:
                inmateVector.append(1)
            elif feature[3:] == '13200' and age <= 13200 and age > 10800:
                inmateVector.append(1)
            elif feature[3:] == '15600' and age <= 15600 and age > 13200:
                inmateVector.append(1)
            elif feature[3:] == '18000' and age <= 18000 and age > 15600:
                inmateVector.append(1)
            elif feature[3:] == '20400' and age <= 20400 and age > 18000:
                inmateVector.append(1)
            elif feature[3:] == '22800' and age <= 22800 and age > 20400:
                inmateVector.append(1)
            elif feature[3:] == '25200' and age <= 25200 and age > 22800:
                inmateVector.append(1)
            elif feature[3:] == '27600' and age <= 27600 and age > 25200:
                inmateVector.append(1)
            elif feature[3:] == '30000' and age <= 30000 and age > 27600:
                inmateVector.append(1)
            elif feature[3:] == '30000+' and age > 30000:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature == "TATTOOS":
            if feature in person:
                inmateVector.append(float(person[feature]))
            else:
                inmateVector.append(0)
        else:
            print 'ERROR', feature
    return inmateVector


def nbRound(testSetY):
    result = []
    for y in testSetY:
        result.append((round(2 * y) / 2) / 10.0)
    return result


def nbTestTransform(testSet):
    result = []
    for i in range(len(testSet)):
        person = []
        for j in range(len(testSet[i])):
            if testSet[i][j] >= 1:
                person.append(1)
            else:
                person.append(0)
        result.append(person)
    return result


def baselineTest(sampleSet, trueSet):
    currentSentenceModesMap = {}
    for key, val in csv.reader(open("currentCrimeSentenceModes.csv")):
        currentSentenceModesMap[key] = val
    
    predictedSet = []
    for crime in sampleSet:
        predictedSentenceLength = int(currentSentenceModesMap[crime])
        predictedSet.append(predictedSentenceLength)

    percentErrors = []
    print "Baseline Test"
    print "Mean absolute test error:", util.mean_absolute_percentage_error(trueSet, predictedSet, percentErrors)
    print "Standard deviation:", np.std(np.array(percentErrors))




def main():
    inmatesMap = mapCreator()
    featureVector = createFeatureVector()

    allInmateCrimes = []
    allInmateCrimesYValues = []
    allInmates = []
    allInmateYValues = []
    for inmate in inmatesMap:
        if 'IncarcerationDate' not in inmatesMap[inmate]:
            continue
        if inmatesMap[inmate]['PrisonReleaseDate'] == '':
            inmatesMap[inmate]['PrisonReleaseDate'] = inmatesMap[inmate]['IncarcerationDate'] + datetime.timedelta(days=36525)
        if (inmatesMap[inmate]["PrisonReleaseDate"] - inmatesMap[inmate]["IncarcerationDate"]).days <= 0:
            continue

        currentPerson = extractFeatures(inmatesMap[inmate], featureVector)

        sentenceLength = (inmatesMap[inmate]["PrisonReleaseDate"] - inmatesMap[inmate]["IncarcerationDate"]).days
        if 'CURRENT_OFFENSES' in inmatesMap[inmate]:
            for offense in inmatesMap[inmate]['CURRENT_OFFENSES']:
                crimeDescription = "CURRENT_" + offense["adjudicationcharge_descr"]
                allInmateCrimes.append(crimeDescription)
                allInmateCrimesYValues.append(sentenceLength)

        allInmates.append(currentPerson)
        # allInmateYValues.append(inmatesMap[inmate]["prisonterm"])
        allInmateYValues.append(sentenceLength)

    X = allInmates[:10000]
    y = allInmateYValues[:10000]

    # print testSet
    # print testSetY

    sgd = SGDRegressor(loss='epsilon_insensitive', fit_intercept=True, learning_rate='constant', n_iter=4, penalty='none', epsilon=0)
    sgd.fit(X, y)
    sgdPredictedSetY = []
    sgdTrueSetY = []
    for i in range(10001, 20001):
        sgdTrueSetY.append(allInmateYValues[i]);
        sgdPredictedSetY.append(sgd.predict(allInmates[i]))
    percentErrors = []
    print "SGD Mean absolute test error:", util.mean_absolute_percentage_error(sgdTrueSetY, sgdPredictedSetY, percentErrors)
    print "SGD Standard deviation:", np.std(np.array(percentErrors))


    svr = svm.SVR()
    svr.fit(X, y)
    svrPredictedSetY = []
    svrTrueSetY = []
    for i in range(10001, 20001):
        print "true value:", allInmateYValues[i]
        print "predicted value:", svr.predict(allInmates[i])
        print "Difference in true and predicted values:", allInmateYValues[i] - svr.predict(allInmates[i])
        svrTrueSetY.append(allInmateYValues[i]);
        svrPredictedSetY.append(svr.predict(allInmates[i]))
    percentErrors = []
    print "SVR Mean absolute test error:", util.mean_absolute_percentage_error(svrTrueSetY, svrPredictedSetY, percentErrors)
    print "SVR Standard deviation:", np.std(np.array(percentErrors))


    # baselineTest(allInmateCrimes[:10000], allInmateCrimesYValues[:10000])

    nbAllInmates = nbTestTransform(allInmates)
    nbAllInmateYValues = nbRound(allInmateYValues)
    nbTestSet = [nbAllInmates[i] for i in range(0, 10000)]
    nbTestSetY = [nbAllInmateYValues[i] for i in range(0, 10000)]
    nb = BernoulliNB()
    nb.fit(np.array(nbTestSet), np.array(nbTestSetY))
    nbTrueSentenceLength = []
    nbTestSentenceLength = []
    for i in range(10001, 20001):
        nbTrueSentenceLength.append(nbAllInmateYValues[i] * 10.0)
        nbTestSentenceLength.append(nb.predict(nbAllInmates[i] * 10.0))
    # print nbTrueSentenceLength
    # print nbTestSentenceLength
    percentErrors = []
    print "Naive Bayes Mean absolute test error:", util.mean_absolute_percentage_error(nbTrueSentenceLength, nbTestSentenceLength, percentErrors)
    print "Naive Bayes standard deviation:", np.std(np.array(percentErrors))

if __name__ == "__main__":
    main()
