'''
Features module.

This module should encapsulate all of the functionality necessary
to prepare and train a model then execute search queries against it
for features and the repos that implement those features.
'''
import os
from simserver import SessionServer
from gensim import utils
import sqlitedict
import logging
import exceptions
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

_texts = {}

def service_initialization(directory_path='.'): #'../Extract_features_using_readmeAPIsource/', directory to place this service
    service = SessionServer(directory_path)
    return service
# Takes a directory path. Loads the readme files into simserver.
# Return the number of files loaded if the files were loaded successfully.
# Throw an error is any problem loading the files.
def load_readme_files(directory_path='.'):    #'./Readme/Readme_set_complete', directory where the readme file source is stored.
    def documents_iter(directory=directory_path): 
        for subfolder in os.listdir(directory):
            if subfolder[0] == '.':
                continue
            for file in os.listdir(directory+'/'+subfolder):
                with open(directory+'/'+subfolder+'/'+file,'r') as f:
                    yield (f,file)
    for f,file in documents_iter():
        text = []
        for line in f:
            text.append(line.strip())
        doc = ' '.join(text)
        _texts[file] = doc
    return


# Trains the simserver model.
# Return nothing if the training was successful.
# Throw an error if something goes wrong.
def train_model(service=None):
    if service == None:
        raise ValueError("You should service value in train_model using result from service_initialization.\n")
    corpus = [{'id': file_name, 'tokens': utils.simple_preprocess(text)}
          for file_name, text in _texts.items()]
    utils.upload_chunked(service, corpus, chunksize=1000)
    service.train(corpus, method='lsi')
    service.index(corpus)
    return

# used to do AND search.(It can be used by setting AndSearch into True in function search)
def go_parsing(pre_result= [],search_string=''):
    result = []
    def find_readme_place(filename,top_folder='./Readme/Readme_set_complete'):
        for sub_folder in os.listdir(top_folder):
            if filename in os.listdir(top_folder+'/'+sub_folder):
                return str(top_folder+'/'+sub_folder+'/'+filename)
        return None
    def read_readmefile2string(abs_filename):
        stringa = ''
        with open (abs_filename,'r') as f:
            for line in f:
                stringa = stringa + line.rstrip() + ' '
        return list(map(lambda word: word.lower(),stringa.split()))
    def filter_readme(filename,stringb = search_string):
        target_list = stringb.lower().split()
        for target in target_list:
            if target not in read_readmefile2string(find_readme_place(filename)): 
                return ''
        return filename
    
    for file_item in pre_result:
        a = filter_readme(file_item[0])
        if a != '':
            result.append(file_item)
    return result

# Taks a search query and a similarity threshold.
# Performs a search using the query and threshold against the simserver model.
# Returns a list of search results for the query
# Throw an error if something goes wrong.
def search(query, service,min_score=0.4,max_results=50,AndSearch=False): #query = 'javascript framework'
    doc = {'tokens': utils.simple_preprocess(query)}
    pre_result = service.find_similar(doc, min_score, max_results)
    if AndSearch == True:
        print(go_parsing(pre_result,query))
    else:
        print(pre_result)
    return


#########API
#way to use this module
#do once
'''
service = service_initialization('../Extract_features_complete/')
load_readme_files('./Readme/Readme_set_complete')
train_model(service)
'''

#do as many times as you want
'''
search('javascript framework',service)
'''
