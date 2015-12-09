import csv
import time
import datetime
import decimal
import numpy
import scipy
from sklearn.linear_model import SGDRegressor

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
            offense = {attributes[0]: currentTime, attributes[1]: county, attributes[2]: prisonTerm, \
                        attributes[3]: probationTerm, attributes[4]: paroleTerm, attributes[5]: crimeDescription}
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
            offense = {attributes[0]: currentTime, attributes[1]: county, attributes[2]: prisonTerm, \
                        attributes[3]: probationTerm, attributes[4]: paroleTerm, attributes[5]: crimeDescription}
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
                elif attributes[i] == 'PrisonReleaseDate':
                    inmateAttributeMap[attributes[i]] = datetime.datetime(2100, 01, 01)
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
	return inmatesMap

def createFeatureVector():
	featureVector = ['TATTOOS', \
                    'len_PREVIOUS_OFFENSES', 'len_CURRENT_OFFENSES']
	with open('facilities.txt', 'r') as f:
		for row in f:
			featureVector.append('FAC_' + row.rstrip('\n'))
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
	return featureVector

def increment(d1, scale, d2):
    """
    Implements d1 += scale * d2 for sparse vectors.
    @param dict d1: the feature vector which is mutated.
    @param float scale
    @param dict d2: a feature vector.
    """
    for f, v in d2.items():
        #print d1.get(f, 0), v, scale
        d1[f] = d1.get(f, 0) + v * scale

def dotProduct(d1, d2):
    """
    @param dict d1: a feature vector represented by a mapping from a feature (string) to a weight (float).
    @param dict d2: same as d1
    @return float: the dot product between d1 and d2
    """
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        #print d2.items()
        #print sum(d1.get(f, 0) * v for f, v in d2.items())
        return sum(d1.get(f, 0) * v for f, v in d2.items())

def extractFeatures(person, featureVector):
    currentOffenses = []
    if 'CURRENT_OFFENSES' in person:
        currentOffenses = person['CURRENT_OFFENSES']
    pastOffenses = []
    if "PREVIOUS_OFFENSES" in person:
        pastOffenses = person['PREVIOUS_OFFENSES']
    inmateVector = []
    for feature in featureVector:
        if feature[0:4] == "FAC_":
            if person["FACILITY_description"] == feature[4:]:
                inmateVector.append(1)
            else:
                inmateVector.append(0)
        elif feature[0:4] == "EYE_":
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
        elif feature == "len_PREVIOUS_OFFENSES":
            inmateVector.append(len(pastOffenses))
        elif feature == "len_CURRENT_OFFENSES":
            inmateVector.append(len(currentOffenses))
        elif feature == "BirthDate":
            inmateVector.append((person["BirthDate"] - datetime.datetime(1900, 01, 01)).days)
        elif feature == "ReceiptDate":
            inmateVector.append((person["ReceiptDate"] - datetime.datetime(1950, 01, 01)).days)
        elif feature == "Weight":
            if person[feature] != '':
                inmateVector.append(float(person[feature]))
            else:
                inmateVector.append(150)
        elif feature == "Height":
            if person[feature] != '':
                inmateVector.append(float(person[feature]))
            else:
                inmateVector.append(510)
        elif feature == "TATTOOS":
            if feature in person:
                inmateVector.append(float(person[feature]))
            else:
                inmateVector.append(0)
    return inmateVector

def learnPredictor(trainExamples, testExamples, featureExtractor, featureVector):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, return the weight vector (sparse feature vector) learned.

    You should implement stochastic gradient descent.

    Note: only use the trainExamples for training!
    You should call evaluatePredictor() on both trainExamples and testExamples
    to see how you're doing as you learn after each iteration.
    numIters refers to a variable you need to declare. It is not passed in.
    '''
    weights = {}  # feature => weight
    numIters = 20
    eta = 0.01
    for i in range(numIters):
        for person in trainExamples:
            features = featureExtractor(person, featureVector)
            correctPrediction = (person['PrisonReleaseDate'] - person['ReceiptDate']).days
            predictionScore = dotProduct(weights, features)
            margin = predictionScore * correctPrediction
            loss = predictionScore - correctPrediction
            gradientLoss = {}
            for word in features:
                if loss > 0:
                    gradientLoss[word] = features[word]
                else:
                    gradientLoss[word] = -features[word]
                #print predictionScore, correctPrediction, features[word]
            #print gradientLoss
            increment(weights, -eta, gradientLoss)
            #if 'SEX_F' in features:
                #print weights
        #trainingCorrectness = evaluatePredictor(trainExamples, lambda x: sign(dotProduct(featureExtractor(x), weights)))
        #testCorrectness = evaluatePredictor(testExamples,  lambda x: sign(dotProduct(featureExtractor(x), weights)))
        #print "Iteration " + str(i)
        #print "Training error is " + str(1 - trainingCorrectness)
        #print "Test error is " + str(1 - testCorrectness)
    return weights

def main():
    inmatesMap = mapCreator()
    featureVector = createFeatureVector()
    #releaseIndex = featureVector.index("PrisonReleaseDate")
    #receiptIndex = featureVector.index("ReceiptDate")
    allInmates = []
    allInmateYValues = []
    for inmate in inmatesMap:
        currentPerson = extractFeatures(inmatesMap[inmate], featureVector)
        allInmates.append(currentPerson)
        allInmateYValues.append((inmatesMap[inmate]["PrisonReleaseDate"] - inmatesMap[inmate]["ReceiptDate"]).days)
    testSet = [allInmates[i] for i in range(0, 10000)]
    testSetY = [allInmateYValues[i] for i in range(0, 10000)]
    clf = SGDRegressor(loss='epsilon_insensitive', fit_intercept=False, learning_rate='constant', n_iter=1, penalty='none', epsilon=20)
    clf.fit(allInmates, allInmateYValues)
    #print clf.predict(allInmates[1])
    #print allInmateYValues[1]
    i = 0
    for coef in clf.coef_:
        print featureVector[i], coef
        i += 1
    #weights = learnPredictor(allInmates, None, extractFeatures, featureVector)
    #print weights

if __name__ == "__main__":
    main()
