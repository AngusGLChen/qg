'''
Created on Sep 17, 2017

@author: Angus
'''

def main():
    
    # SQUAD
    para_file = "/Users/Angus/Projects/qg/data/squad/data/processed/para-test.txt"
    # RACE
    para_file = "/Users/Angus/Projects/qg/data/race/all/para-test.txt"
    paragraphs = []
    paragraph_set = set()
    with open(para_file, 'r') as infile:
        for line in infile:
            if line not in paragraph_set:
                paragraph_set.add(line)           
                paragraphs.append(line)
    
    # SQUAD
    simplified_para_file = "/Users/Angus/Projects/qg/data/squad/data/processed/simplified_para-test.txt"
    # RACE
    simplified_para_file = "/Users/Angus/Projects/qg/data/race/all/simplified_para-test.txt"
    with open(simplified_para_file, 'w') as outfile:
        for line in paragraphs:
            outfile.write(line)
    outfile.close()
    

if __name__ == "__main__":
    main()
    print("Done.")