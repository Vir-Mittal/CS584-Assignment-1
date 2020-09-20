import pandas as pd
from collections import defaultdict

import re
import nltk
from nltk.tokenize import sent_tokenize
import regex

infile = './Assignment1GoldStandardSet.xlsx'
outfile = './vir_mittal_assignment1_output.xlsx'
lexiconfile = './COVID-Twitter-Symptom-Lexicon.txt'


def load_file(f_path):
    '''
    Loads the labels

    :param f_path:
    :return:
    '''
    labeled_df = pd.read_excel(f_path)
    labeled_dict = {}
    for index,row in labeled_df.iterrows():
        id_ = row['ID']
        if(id_):
        	labeled_dict[id_] = row['TEXT']
    return labeled_dict

infile_dict = load_file(infile)

def write_file(write_list):

	# Create a Pandas dataframe from some data.
	df = pd.DataFrame(write_list,columns = ['ID','Symptom CUIs','Negation Flag']) 

	# Create a Pandas Excel writer using XlsxWriter as the engine.
	writer = pd.ExcelWriter(outfile, engine='xlsxwriter')

	# Convert the dataframe to an XlsxWriter Excel object.
	df.to_excel(writer, sheet_name='Sheet1', index=False)

	# Close the Pandas Excel writer and output the Excel file.
	writer.save()

result_list = []

symptom_dict = {}
infile = open(lexiconfile)
lines = infile.readlines()
for line in lines:
	line = line.rstrip("\n")
	terms = line.split('\t')
	symptom_dict[terms[2]] = terms[1]

neg_words = ['no', 'not', 'without', 'absence of', 'cannot', "couldn't", 'could not', "didn't", "did not", "denied", "denies", "free of", "negative for", "never had", "resolved", "exclude", "with no", "rule out", "free", "aside from", "except", "apart from"]

for id_ in infile_dict:
	result_dict = {}
	text = infile_dict[id_]
	sentences = sent_tokenize(str(text))
	result_dict["ID"] = id_
	cuids_list = []
	cuids = ""
	negation_flags = ""
	for symptom in symptom_dict:
		found = False
		is_pos = False
		is_neg = False
		for index, sentence in enumerate(sentences):
			#match symptom and return the 4 words before the match
			pat = re.compile(r"(?:\S+\s+){0,4}\b%s\b"%symptom,re.IGNORECASE)
			matched_object = re.findall(pat, sentence)
			for match in matched_object:
				found = True
				words = match
				words = words.split(' ')
				words.pop()
				neg = False
				# check if symptom is negated
				for neg_word in neg_words:
					if len(neg_word.split(" "))>1 and neg_word in words:
						neg = True
					elif len(neg_word.split(" "))==1 and neg_word in words:
						neg = True
				if neg:
					is_neg = True
				else:
					is_pos = True

		#check if symptom is present
		if found:
			#check if symptom was positive even once
			if is_pos and (str(symptom_dict[symptom])+"-0") not in cuids_list:
				cuids_list.append((str(symptom_dict[symptom])+"-0"))
				cuids += ("$$$" + str(symptom_dict[symptom]))
				negation_flags += ("$$$" + "0")
			#check if symptom was negative even once
			if is_neg and (str(symptom_dict[symptom])+"-1") not in cuids_list:
				cuids_list.append((str(symptom_dict[symptom])+"-1"))
				cuids += ("$$$" + str(symptom_dict[symptom]))
				negation_flags += ("$$$" + "1")


	cuids += "$$$"
	negation_flags += "$$$"
	result_dict["Symptom CUIs"] = cuids
	result_dict["Negation Flag"] = negation_flags
	result_list.append(result_dict)

write_file(result_list)
