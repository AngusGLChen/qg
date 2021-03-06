#!/usr/bin/env python
__author__ = 'Angus'

from bleu.bleu import Bleu
from meteor.meteor import Meteor
from rouge.rouge import Rouge
from cider.cider import Cider

from collections import defaultdict
from argparse import ArgumentParser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

parser = ArgumentParser()
parser.add_argument("-out", "--out_file", dest="out_file",
                    help="output file to compare")
parser.add_argument("-tgt", "--tgt_file", dest="tgt_file",
                    help="target file")

parser.add_argument("-para", "--para_file", dest="para_file",
                    help="para file")
parser.add_argument("-simplified_para", "--simplified_para_file", dest="simplified_para_file",
                    help="simplified para file")
parser.add_argument('-n_best', type=int, default=1,
                    help="""If verbose is set, will output the n_best
                    decoded sentences""")

class QGEvalCap:
    def __init__(self, gts, res):
        self.gts = gts
        self.res = res

    def evaluate(self):
        output = []
        scorers = [
            (Bleu(4), ["Bleu_1", "Bleu_2", "Bleu_3", "Bleu_4"]),
            (Meteor(),"METEOR"),
            (Rouge(), "ROUGE_L"),
            # (Cider(), "CIDEr")
        ]

        # =================================================
        # Compute scores
        # =================================================
        for scorer, method in scorers:
            print 'computing %s score...'%(scorer.method())
            score, scores = scorer.compute_score(self.gts, self.res)
            if type(method) == list:
                for sc, scs, m in zip(score, scores, method):
                    print "%s: %0.2f"%(m, sc*100)
                    output.append(sc)
            else:
                print "%s: %0.2f"%(method, score*100)
                output.append(score)
        return output

def find_n_best(para_file, tgt_file):
    paragraphs =[]    
    with open(para_file, 'r') as infile:
        for line in infile:            
            paragraphs.append(line[:-1])
    
    questions =[]    
    with open(tgt_file, 'r') as infile:
        for line in infile:            
            questions.append(line[:-1])
    
    pairs = {}
    paragraph_set = set()
    for paragraph, question in zip(paragraphs, questions):
        if paragraph not in paragraph_set:
            paragraph_set.add(paragraph)
            pairs[paragraph] = set()
        pairs[paragraph].add(question)
        
    # To find the maxinum # of sentences belonging to the same paragraph
    n_best = 0
    for paragraph in pairs.keys():
        if len(pairs[paragraph]) > n_best:
            n_best = len(pairs[paragraph])
    print("The maxinum # of sentences belonging to the same paragraph is:\t%d" % n_best)
    return n_best
    

def eval_race(out_file, simplified_para_file, para_file, tgt_file, n_best, isDIn = False, num_pairs = 500):
    """
        Given a filename, calculate the metric scores for that prediction file
        isDin: boolean value to check whether input file is DirectIn.txt
    """
    
    simplified_paragraphs =[]    
    with open(simplified_para_file, 'r') as infile:
        for line in infile:            
            simplified_paragraphs.append(line[:-1])
    
    predictions = []
    with open(out_file, 'r') as infile:
        for i in range(len(simplified_paragraphs)):
            j = n_best
            array = []
            while j > 0:
                line = infile.readline()
                array.append(line[:-1])
                j -= 1
            predictions.append(array)
    
    assert(len(simplified_paragraphs) == len(predictions))
    
    # Mapping between paragraphs and predictions
    para_prediciton_map = {}
    for i in range(len(simplified_paragraphs)):
        para_prediciton_map[simplified_paragraphs[i]] = predictions[i]
        
    paragraphs =[]    
    with open(para_file, 'r') as infile:
        for line in infile:            
            paragraphs.append(line[:-1])
    
    questions =[]    
    with open(tgt_file, 'r') as infile:
        for line in infile:            
            questions.append(line[:-1])
            
    pairs = defaultdict(lambda: {'sentences':set(), 'predictions':[]})
    for paragraph, question in zip(paragraphs, questions):
        pairs[paragraph]['questions'].append(question)
        pairs[paragraph]['predictions'] = para_prediciton_map[paragraph]
    
    # Clean up redundant predictions     
    for paragraph in pairs.keys():
        while len(pairs[paragraph]['questions']) != len(pairs[paragraph]['predictions']):
            del pairs[paragraph]['predictions'][-1]

    ## eval
    from eval_race import QGEvalCap
    import json
    from json import encoder
    encoder.FLOAT_REPR = lambda o: format(o, '.4f')

    res = defaultdict(lambda: [])
    gts = defaultdict(lambda: [])
    for paragraph in pairs.keys():        
        for prediction in pairs[paragraph]['predictions']:      
            res[paragraph].append(prediction.encode('utf-8'))
        ## gts
        for question in pairs[paragraph]['questions']:
            gts[paragraph].append(question.encode('utf-8'))

    QGEval = QGEvalCap(gts, res)
    return QGEval.evaluate()

def main():
    args = parser.parse_args()
    
    # Step 1: Find n_best
    n_best = find_n_best(args.para_file, args.tgt_file)
    
    # Step 2: Evaluation
    print "scores: \n"
    # Evaluation for RACE
    eval_race(args.out_file, args.simplified_para_file, args.para_file, args.tgt_file, n_best)
    

if __name__ == "__main__":
    main()


