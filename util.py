import sys


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
        return sys.maxint
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


