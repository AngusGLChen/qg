'''
Created on Sep 18, 2017

@author: Angus
'''


import json, os, nltk, operator

import numpy
import matplotlib.pyplot as plt;
from _collections import defaultdict
plt.rcdefaults()

from nltk.tokenize import sent_tokenize

def plot(array):
    n, bins, patches = plt.hist(array)    
    plt.show()

def analyze(file_path, code, word_set, line_set, word_length_array, sentence_length_array):
        
    files = ["train", "dev", "test"]
    for file in files:
        print("-----------" + file + "-----------")
        path = file_path + code + "-" + file + ".txt"
        
        with open(path, "r") as infile:
            lines = infile.readlines()
            print("# records is:\t %s" % len(lines))
            for line in lines:
#                 if code == 'question' and file == 'train':
#                     if line in line_set:
#                         print(line)            
                line_set.add(line)
        
        # Distribution of DINSTINC lines   
        for line in line_set:
            # Number of words / line
            words = line.strip().split()
            word_length = 0
            for word in words:
                if word != "":
                    word_set.add(word)
                    word_length += 1
            word_length_array.append(word_length)
             
            # Number of sentences / line
            try:
                sentences = sent_tokenize(line)
            except Exception as e:
                print(e)
                print(line)
                print("")
                sentences = line.split(".")
            sentence_length_array.append(len(sentences))
            
        print("Vocabulary size is:\t %s" % len(word_set))
        print("# DISTINCT lines is:\t %s" % len(line_set))
        
        print("")
        
        print("Avg. length of lines is:\t %.2f" % numpy.average(word_length_array))
        print("Shortest line is:\t %s" % min(word_length_array))
        print("Longest line is:\t %s" % max(word_length_array))
        
        # plot(word_length_array)
        
        print("")
            
        print("Avg. # sentences is:\t %.2f" % numpy.average(sentence_length_array))
        print("The minimum # of sentences is:\t %s" % min(sentence_length_array))
        print("The maximum # of sentences is:\t %s" % max(sentence_length_array))        # plot(sentence_length_array)
    
def analyze_dataset(path): 
    codes = ['para', 'question']
    for code in codes:
        print(code)
        word_set = set()
        line_set = set()
        sentence_length_array = []
        word_length_array = []        
        analyze(path, code, word_set, line_set, word_length_array, sentence_length_array)
        print("***********************************")

def tokenize_text(text):
    # Lowercase, replace tabs, striping    
    text = text.lower().replace('\n', ' ').strip()
    return " ".join(nltk.word_tokenize(text))
    
def extract_data_unique(data_path, selected_questions):
    codes = ['train', 'dev', 'test']
    categories = ['middle', 'high']
    for code in codes:
        para_file = open(data_path + "unique/para-" + code + ".txt", "w")
        question_file = open(data_path + "unique/question-" + code + ".txt", "w")
        
        for category in categories:
            folder_path = data_path + code + "/" + category + "/"
            files = os.listdir(folder_path)
            for file in files:
                with open(folder_path + file, "r") as infile:
                    record = json.loads(infile.read())
                    article= record['article']
                    questions = record['questions']                    
                    
                    article = tokenize_text(article)
                    for question in questions:
                        tokenize_question = tokenize_text(question)
                        para_file.write(article + "\n")
                        question_file.write(tokenize_question + "\n")
        para_file.close()
        question_file.close()
        
def extract_data_all(data_path):
    codes = ['train', 'dev', 'test']
    categories = ['middle', 'high']
    for code in codes:
        para_file = open(data_path + "all/para-" + code + ".txt", "w")
        question_file = open(data_path + "all/question-" + code + ".txt", "w")
        
        for category in categories:
            folder_path = data_path + code + "/" + category + "/"
            files = os.listdir(folder_path)
            for file in files:
                with open(folder_path + file, "r") as infile:
                    record = json.loads(infile.read())
                    article= record['article']
                    questions = record['questions']
                    options = record['options']
                    article = tokenize_text(article)
                                        
                    for question, option in zip(questions, options):
                        tokenize_question = tokenize_text(question)
                        for element in option:              
                            para_file.write(article + "\n")
                            tokenize_element = tokenize_text(element)
                            question_file.write(tokenize_question + " " + tokenize_element + "\n")
        para_file.close()
        question_file.close()
        
def get_frequent_questions(data_path, k):
    question_frequency_map = {}
    question_set = set()
    
    codes = ['train', 'dev', 'test']
    categories = ['middle', 'high']
    for code in codes:        
        for category in categories:
            folder_path = data_path + code + "/" + category + "/"
            files = os.listdir(folder_path)
            for file in files:
                with open(folder_path + file, "r") as infile:
                    record = json.loads(infile.read())
                    questions = record['questions']
                    for question in questions:
                        tokenize_question = tokenize_text(question)
                        if tokenize_question not in question_set:
                            question_set.add(tokenize_question)
                            question_frequency_map[tokenize_question] = 0
                        question_frequency_map[tokenize_question] += 1        
    
    # Print top-k frequent questions       
    sorted_map = sorted(question_frequency_map.items(), key=operator.itemgetter(1), reverse=True)
    for i in range(k):
        print("%d\t%s" % (sorted_map[i][1], sorted_map[i][0]))  
    
    selected_questions = set()               
    for question in question_frequency_map.keys():
        if question_frequency_map[question] == 1:
            selected_questions.add(question)
    print("# selected questions is:\t%d" % len(selected_questions))
    return selected_questions

def main():
    data_path = '/Users/Angus/Projects/qg/data/race/'
    
    # Step 0: Get top-k frequent questions
    k = 0
    selected_questions = get_frequent_questions(data_path, k)
    
    # Step 1.1: Extract the dataset => Unique dataset
    # extract_data_unique(data_path, selected_questions)
    # extract_data_all(data_path)
        
    # Step 2: Analyze the dataset
    unique_data_path = data_path + 'unique/'
    # unique_data_path = data_path + 'all/'
    analyze_dataset(unique_data_path)
    
    print("Done.")

if __name__ == "__main__":
    main()



