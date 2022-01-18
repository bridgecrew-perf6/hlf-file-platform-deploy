from django.apps import AppConfig
from collections import defaultdict
from ERC_deploy.settings import BASE_DIR
from transformers import BertTokenizerFast
from pyserini.analysis import Analyzer, get_lucene_analyzer
import os
import pickle
import time

class MainAppConfig(AppConfig):
    name = 'main_app'

    images = []
    with open(os.getcwd() + "/rawdata/images.txt", 'r') as f:
        for line in f.readlines():
            images.append(line.split()[1])
    
    data_dir = os.path.join(BASE_DIR, 'search_data')
    index_path = os.path.join(data_dir, 'metadataSearchTable.data')
    attr_path = os.path.join(data_dir, 'attributeSearchTable.pickle')

    metadataSearchTable = defaultdict(set)
    if os.path.isfile(index_path):
        f = open(index_path, 'rb')
        metadataSearchTable = pickle.load(f)
        f.close()
    else:
        with open(os.getcwd() + "/rawdata/unlabeled_data.pickle", 'rb') as f:
            data = pickle.load(f)
        for i in range(len(data['index'])):
            for metadata in data['attributes_predicted_names'][i]:
                metadataSearchTable[metadata].add(int(data['index'][i]))
        f = open(index_path, 'wb')
        pickle.dump(metadataSearchTable, f)
        f.close()

    attributeSearchTable = defaultdict(set)
    if os.path.isfile(attr_path):
        f = open(attr_path, 'rb')
        attributeSearchTable = pickle.load(f)
        f.close()

    data_dir = os.path.join(BASE_DIR, 'search_data')
    uid2top10terms_path = os.path.join(data_dir, 'uid2top10terms.pkl')
    collection_path = os.path.join(data_dir, 'collection_covid19.tsv')
    query2qid_path = os.path.join(data_dir, 'topics.question.covid19.raw.tsv')
    qrels_path = os.path.join(data_dir, 'qrels.covid-complete.txt')

    with open(uid2top10terms_path, 'rb') as f:
        uid2top10terms = pickle.load(f)  

    uid2contents = dict()
    with open(collection_path) as f:
        for line in f:
            lines = line.rstrip().split('\t')
            uid = lines[0]
            if len(lines) == 1:
                uid2contents[uid] = ['']
                continue
            uid2contents[uid] = lines[1:] # title, contents

    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

    query2qid = dict()
    qid2query = dict()
    with open(query2qid_path) as f:
        for line in f:
            qid, query = line.rstrip().split('\t')
            query2qid[query.lower()] = qid
            qid2query[qid] = query.lower()
    
    qid2rels = dict()
    with open(qrels_path) as f:
        for line in f:
            qid, _, uid, score = line.rstrip().split()
            if qid2rels.get(qid) is None:
                qid2rels[qid] = {uid: int(score)}
            else:
                qid2rels[qid][uid] = int(score)
                
    analyzer = Analyzer(get_lucene_analyzer(stemmer='porter'))