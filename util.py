import sys
import csv
import collections
import numpy as np

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


def mean_absolute_percentage_error(y_true, y_pred, percentErrors):
    for i in range(len(y_true)):
        # print "true", y_true[i], "experimental", y_pred[i]
        percentErrors.append(abs(y_true[i] - y_pred[i]) / y_true[i])
        # print percentErrors[i]
    #percentErrors = np.abs((y_true - y_pred) / y_true)
    return np.mean(np.array(percentErrors))


SENTENCE_LENGTH_DIGITS = 7
def convertSentenceToDays(sentenceLength):
    ''' 
    Arguments: 
        sentenceLength is a string that represents the sentence length in the
        condensed format of the database

    Returns: 
        Length of the sentence in days. Returns sys.maxint if sentenceLength
        is a life sentence, which is represented by 9999998
    '''
    if sentenceLength == "9999998":
        return 100 * 365
    else:
        numDigits = len(sentenceLength)
        sentenceLength = "0" * (SENTENCE_LENGTH_DIGITS - numDigits) + sentenceLength
        yearsString = sentenceLength[:3]
        monthsString = sentenceLength[3:5]
        daysString = sentenceLength[5:]
        if daysString:
            days = int(daysString)
            # print "days:", days
        else:
            days = 0
        if monthsString:
            months = int(monthsString)
            # print "months:",  months
        else:
            months = 0
        if yearsString:
            years = int(yearsString)
            # print "years:", years
        else:
            years = 0

        return days + months * 30 + years * 365


def createSentenceModesMap():
    prevSentenceModesMap = {}
    currentSentenceModesMap = {}

    with open('INMATE_ACTIVE_OFFENSES_prpr.csv', 'rb') as csvfile:
        previousOffensesReader = csv.reader(csvfile)
        for row in previousOffensesReader:
            inmate_id = row[0]
            prisonTerm = row[6]
            crimeDescription = 'PREV_' + row[9]
            if inmate_id == 'DCNumber':
                attributes = [crimeDescription, prisonTerm]
            else:
                if crimeDescription in prevSentenceModesMap:
                    prevSentenceModesMap[crimeDescription].append(convertSentenceToDays(prisonTerm))
                else:
                    prevSentenceModesMap[crimeDescription] = [convertSentenceToDays(prisonTerm)]

    with open('INMATE_ACTIVE_OFFENSES_CPS.csv', 'rb') as csvfile:
        currentOffensesReader = csv.reader(csvfile)
        for row in currentOffensesReader:
            inmate_id = row[0]
            prisonTerm = row[6]
            crimeDescription = 'CURRENT_' + row[9]
            if inmate_id == 'DCNumber':
                attributes = [crimeDescription, prisonTerm]
            else:
                if crimeDescription in currentSentenceModesMap:
                    currentSentenceModesMap[crimeDescription].append(convertSentenceToDays(prisonTerm))
                else:
                    currentSentenceModesMap[crimeDescription] = [convertSentenceToDays(prisonTerm)]

    for crime in prevSentenceModesMap:
        sentenceLengths = prevSentenceModesMap[crime]
        b = collections.Counter(sentenceLengths)
        mode, numAppearances = b.most_common(1)[0]
        prevSentenceModesMap[crime] = mode

    for crime in currentSentenceModesMap:
        sentenceLengths = currentSentenceModesMap[crime]
        b = collections.Counter(sentenceLengths)
        mode, numAppearances = b.most_common(1)[0]
        currentSentenceModesMap[crime] = mode

    w = csv.writer(open("prevCrimeSentenceModes.csv", "w"))
    for key, val in prevSentenceModesMap.items():
        w.writerow([key, val])

    w = csv.writer(open("currentCrimeSentenceModes.csv", "w"))
    for key, val in currentSentenceModesMap.items():
        w.writerow([key, val])

createSentenceModesMap()

