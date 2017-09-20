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
parser.add_argument("-src", "--src_file", dest="src_file",
                    help="src file")
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
                    print "%s: %0.4f"%(m, sc)
                    output.append(sc)
            else:
                print "%s: %0.4f"%(method, score)
                output.append(score)
        return output

def eval(out_file, src_file, tgt_file, isDIn = False, num_pairs = 500):
    """
        Given a filename, calculate the metric scores for that prediction file
        isDin: boolean value to check whether input file is DirectIn.txt
    """

    pairs = []
    with open(src_file, 'r') as infile:
        for line in infile:
            pair = {}
            pair['tokenized_sentence'] = line[:-1]
            pairs.append(pair)

    with open(tgt_file, "r") as infile:
        cnt = 0
        for line in infile:
            pairs[cnt]['tokenized_question'] = line[:-1]
            cnt += 1

    output = []
    with open(out_file, 'r') as infile:
        for line in infile:
            line = line[:-1]
            output.append(line)

    for idx, pair in enumerate(pairs):
        pair['prediction'] = output[idx]

    ## eval
    from eval import QGEvalCap
    import json
    from json import encoder
    encoder.FLOAT_REPR = lambda o: format(o, '.4f')

    res = defaultdict(lambda: [])
    gts = defaultdict(lambda: [])
    for pair in pairs[:]:
        key = pair['tokenized_sentence']
        res[key] = [pair['prediction'].encode('utf-8')]

        ## gts 
        gts[key].append(pair['tokenized_question'].encode('utf-8'))

    QGEval = QGEvalCap(gts, res)
    return QGEval.evaluate()

def find_n_best(para_file, src_file):
    paragraphs =[]    
    with open(para_file, 'r') as infile:
        for line in infile:            
            paragraphs.append(line[:-1])
    
    sentences =[]    
    with open(src_file, 'r') as infile:
        for line in infile:            
            sentences.append(line[:-1])
    
    pairs = {}
    paragraph_set = set()
    for paragraph, sentence in zip(paragraphs, sentences):
        if paragraph not in paragraph_set:
            paragraph_set.add(paragraph)
            pairs[paragraph] = set()
        pairs[paragraph].add(sentence)
        
    # To find the maxinum # of sentences belonging to the same paragraph
    n_best = 0
    for paragraph in pairs.keys():
        if len(pairs[paragraph]) > n_best:
            n_best = len(pairs[paragraph])
    print("The maxinum # of sentences belonging to the same paragraph is:\t%d" % n_best)
    return n_best
    

def eval_squad(out_file, simplified_para_file, para_file, src_file, tgt_file, n_best, isDIn = False, num_pairs = 500):
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
    
    sentences =[]    
    with open(src_file, 'r') as infile:
        for line in infile:            
            sentences.append(line[:-1])
    
    questions =[]    
    with open(tgt_file, 'r') as infile:
        for line in infile:            
            questions.append(line[:-1])
            
    pairs = defaultdict(lambda: {'sentences':set(), 'questions':[], 'predictions':[]})
    for paragraph, sentence, question in zip(paragraphs, sentences, questions):
        pairs[paragraph]['sentences'].add(sentence)
        pairs[paragraph]['questions'].append(question)
        pairs[paragraph]['predictions'] = para_prediciton_map[paragraph]
    
    # Clean up redundant predictions     
    for paragraph in pairs.keys():
        while len(pairs[paragraph]['sentences']) != len(pairs[paragraph]['predictions']):
            del pairs[paragraph]['predictions'][-1]

    ## eval
    from eval import QGEvalCap
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
    n_best = find_n_best(args.para_file, args.src_file)
    
    # Step 2: Evaluation
    print "scores: \n"
    # eval(args.out_file, args.src_file, args.tgt_file)
    
    # Evaluation for SQUAD
    eval_squad(args.out_file, args.simplified_para_file, args.para_file, args.src_file, args.tgt_file, n_best)
    

if __name__ == "__main__":
    main()


