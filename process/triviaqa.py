'''
Created on Sep 11, 2017

@author: Angus
'''

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

import numpy
import matplotlib.pyplot as plt;
plt.rcdefaults()

from nltk.tokenize import sent_tokenize

def plot(array):
    n, bins, patches = plt.hist(array)    
    plt.show()

def analyze(file_path, word_set, line_set):
    word_length_array = []
    sentence_length_array = []
    
    with open(file_path, "r") as file:
        lines = file.readlines()
        print("# records is:\t %s" % len(lines))
        for line in lines:            
            line_set.add(line)
            
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
                # print(e)
                sentences = line.split(".")
            sentence_length_array.append(len(sentences))
    
    '''
    # Distribution of DINSTINC lines   
    for line in line_set:
        words = line.strip().split()
        word_length = 0
        for word in words:
            if word != "":
                word_set.add(word)
                word_length += 1
        word_length_array.append(word_length)
    '''
            
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
    print("The maximum # of sentences is:\t %s" % max(sentence_length_array))
    
    # plot(sentence_length_array)
    
        
def main():
    word_set = set()
    
    train_line_set = set()
    dev_line_set = set()
    test_line_set = set()
    
    file_path = "../data/squad/data/processed/para-train.txt"
    analyze(file_path, word_set, train_line_set)
    print("***********************************")
    
    file_path = "../data/squad/data/processed/para-dev.txt"
    analyze(file_path, word_set, dev_line_set)
    print("***********************************")
    
    file_path = "../data/squad/data/processed/para-test.txt"
    analyze(file_path, word_set, test_line_set)
    print("***********************************")
    
    print("To check whether there is overlap between the training & validation paragraphs")
    dev_overlap_line = 0
    for line in dev_line_set:
        if line in train_line_set:
            dev_overlap_line += 1
    print("# dev overlap lines is:\t %s" % dev_overlap_line)
        
    print("To check whether there is overlap between the training & validation & testing paragraphs")
    test_overlap_line = 0
    for line in test_line_set:
        if line in train_line_set or line in dev_line_set:
            test_overlap_line += 1
    print("# test overlap lines is:\t %s" % test_overlap_line)
            
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
