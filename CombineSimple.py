from claim_tree import *

import re
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
import spacy
import requests

nlpNP = spacy.load('en', disable = ['textcat'])
nlp = spacy.load('en')
nlpL = spacy.load('en', disable=['ner', 'parser'])
nlpL.add_pipe(nlpL.create_pipe('sentencizer'))


StopWordsFile = open("Stopwords", "r")
stopwords= [word.replace("\n","") for word in StopWordsFile]
StopWordsFile.close()


def processAllPatents(allPatentsTree):
    patentsProcessed = 0
    
    for app in allPatentsTree.iter("us-patent-grant"):
        edges, infos = create_patent_dict(app)
        graph_class = ClaimSet(app)
        patentsProcessed += 1
        if patentsProcessed % 1000 == 0:
            print(patentsProcessed,' patents processed')
        combineInfo(graph_class)
    return (patentsProcessed)


# should allow this to check whether a file is patent or application, rather than passing parameter
def processPatentOrApp(inputFileName, isPatent):
    # global appsProcessed
    start_time = time()
    f = open(inputFileName, 'rU')
    # parser = etree.XMLParser(resolve_entities=False, target=applicationTreeBuilder())
    parser = etree.XMLParser(resolve_entities=False)
    allAppsTree = etree.parse(f, parser)
    elapsed_time = time() - start_time
    print('parsing took ', elapsed_time, ' seconds')
    if isPatent:
        (numProcessed) = processAllPatents(allAppsTree)
        print('%d patents processed' % numProcessed)

def lemmatize(text):
    # Extracts roots of words
    lemma = " "
    for w in text:
        if(not w.lemma_ in stopwords):
            lemma+= re.sub(r"[0-9]+"," ", w.lemma_) + " "
    return lemma

def check_similarity(phrase1, phrase2):
    return phrase1.similarity(phrase2)

def combineInfo(graph):
	combined_info_dict = {}
	nodes = graph.nodes_dict
	for node in nodes:
		ancestors = graph.find_ancestors(node)
		info = ""		
		claim_ref_p = re.findall(r"(.*)claim|$", info)
		if(len(claim_ref_p)==0):
			info = nodes[node].info.replace("\n", " ")
		prev_ref = lemmatize(nlpL(str(claim_ref_p[0])))
		prev_ref = nlp(prev_ref)
		number = nodes[node].number
		anc_rev = ancestors[::-1]
		for ancestor in anc_rev:
			prev_ref_a = re.findall(r"(.*)claim", nodes[ancestor].info.replace("\n", " "))
			i = True
			for p in prev_ref_a:
				prev_ref_a = lemmatize(nlpL(p))
				prev_ref_aN = nlp(prev_ref_a)
				if(check_similarity(prev_ref_aN, prev_ref)==1):
					i = False
					info += "\n" + nodes[ancestor].info.replace(prev_ref_a, "\n")
			if(i):
			 	info += "\n" + nodes[ancestor].info
		info += nodes[node].info.replace("\n", " ")
		combined_info_dict[number] = info
		print("_________________________________________")
		print("Claim number %s\n %s\n\n" % (number, info))
		print("_________________________________________")
		#print("Claim number %s\n %s\n\n" %(number, info))
	return combined_info_dict

def processAllInFolder(folderPath, isPatent):
    for single_root_file in os.listdir(folderPath):
        if single_root_file.endswith("_SR.xml"):
            print(single_root_file)
            singleRootFilePath = os.path.join(folderPath, single_root_file)
            processPatentOrApp(singleRootFilePath, isPatent)
            


if __name__ == "__main__":
    # main(argv[1:])
    # main(["--path", "/media/alderucci/Data/patent data/ipa181108.xml"])
    # main(["--file", "/media/alderucci/Data/patent data/ipa181108_SR.xml"])

    # file name of a file containing XML for a single patent application
    # inputFileName = "ipa181108/US20180317366A1.txt"

    dataDirectory = "patents"
    isPatent = True # will be given patents not applications
    processAllInFolder(dataDirectory, isPatent)


    # start_time = time()
    # inputFileName = "/media/alderucci/Data/patent data/ipg181113_SR.xml"
    #
    # # main(["--file", outputFileName])
    #
    # processPatentOrApp(inputFileName, isPatent = True)
    # elapsed_time = time() - start_time
    # print('total elapsed program time:', elapsed_time, ' seconds')

    print('Program complete.' )
