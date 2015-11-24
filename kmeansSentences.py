import csv
import time
import datetime
import decimal

def addCurrentOffenses(currentOffensesReader, sentenceClusterArray):
    attributes = []
    for row in currentOffensesReader:
        inmate_id = row[0]
        prisonTerm = row[6]
        crimeDescription = 'CURRENT_' + row[9]
        if inmate_id == 'DCNumber':
            attributes = [crimeDescription, prisonTerm]
        else:
            sentenceClusterArray.append((crimeDescription, int(prisonTerm)));

def addPreviousOffenses(previousOffensesReader, sentenceClusterArray):
    attributes = []
    for row in previousOffensesReader:
        inmate_id = row[0]
        prisonTerm = row[6]
        crimeDescription = 'PREV_' + row[9]
        if inmate_id == 'DCNumber':
            attributes = [crimeDescription, prisonTerm]
        else:
            sentenceClusterArray.append((crimeDescription, int(prisonTerm)));

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

def main():
    (previousOffenses, currentOffenses) = tuplesCreator()

if __name__ == "__main__":
    main()