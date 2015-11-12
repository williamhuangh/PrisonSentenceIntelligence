import csv

def addCurrentOffenses(currentOffensesReader, inmatesMap):
	for row in currentOffensesReader:
		if row[0] == 'DCNumber':
			attributes = [row[2], row[4], row[6], row[7], row[8], row[9]]
		else:
			if 'CURRENT_OFFENSES' not in inmatesMap[row[0]]:
				inmatesMap[row[0]]['CURRENT_OFFENSES'] = [{attributes[0]: row[2], attributes[1]: row[4], attributes[2]: row[7], attributes[3]: row[8], attributes[4]: row[9]}]
			else:
				inmatesMap[row[0]]['CURRENT_OFFENSES'].append({attributes[0]: row[2], attributes[1]: row[4], attributes[2]: row[7], attributes[3]: row[8], attributes[4]: row[9]})

def addPreviousOffenses(previousOffensesReader, inmatesMap):
	for row in previousOffensesReader:
		if row[0] == 'DCNumber':
			attributes = [row[2], row[4], row[6], row[7], row[8], row[9]]
		else:
			if 'PREVIOUS_OFFENSES' not in inmatesMap[row[0]]:
				inmatesMap[row[0]]['PREVIOUS_OFFENSES'] = [{attributes[0]: row[2], attributes[1]: row[4], attributes[2]: row[7], attributes[3]: row[8], attributes[4]: row[9]}]
			else:
				inmatesMap[row[0]]['PREVIOUS_OFFENSES'].append({attributes[0]: row[2], attributes[1]: row[4], attributes[2]: row[7], attributes[3]: row[8], attributes[4]: row[9]})

def addScars(scarsMarkReader, inmatesMap):
	for row in scarsMarkReader:
		if row[0] != 'DCNumber':
			if 'TATTOOS' not in inmatesMap[row[0]]:
				inmatesMap[row[0]]['TATTOOS'] = 1
			else:
				inmatesMap[row[0]]['TATTOOS'] += 1

def createInmates(rootReader, inmatesMap):
	attributes = []
	for row in rootReader:
		if row[0] == 'DCNumber':
			for attribute in row:
				attributes.append(attribute)
		else:
			inmateAttributeMap = {}
			for i in range(1, len(row)):
				inmateAttributeMap[attributes[i]] = row[i]
			inmatesMap[row[0]] = inmateAttributeMap


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

mapCreator()