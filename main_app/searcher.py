from threading import current_thread
from .apps import MainAppConfig
from ERC_deploy.settings import BASE_DIR

import json
import hdfs
import os
import shutil
import re
import sh
import pickle

def search_query_cub(query_list):
    result = set(range(20000))
    queries = []
    for query in query_list:
        json_query = json.loads(query)
        if json_query['bodypart'] == 'body':
            bodypart = ""
        else:
            bodypart = json_query['bodypart']+"_"
        key = f"has_{bodypart}{json_query['feature']}::{json_query['value']}"
        queries.append(key)
        result = result.intersection(MainAppConfig.metadataSearchTable[key])
    
    datadir = "/home/jjlee/ERC_deploy/rawdata/"
    filename = "unlabeled_data.pickle"
    with open(datadir + filename, 'rb') as f:
        data = pickle.load(f)
    
    download_path = os.path.join(BASE_DIR, 'main_app/static/assets/img/CUB/')
    shutil.rmtree(download_path, ignore_errors=True)
    os.mkdir(download_path)

    client = hdfs.InsecureClient('http://sun01:10871', user='jjlee')
    hdfs_dir = "/user/jjlee/CUB/"
    current_files = client.list(hdfs_dir)

    documents = {}
    for index in result:
        img_index = -1
        for i in range(len(data['index'])):
            if int(data['index'][i]) == index:
                img_index = i
                break
        title = MainAppConfig.images[index-1].split('/')[-1]
        if title in current_files:
            client.download(hdfs_dir+title, download_path, overwrite=True)
            url = 'assets/img/CUB/'+title
            metadata = data['attributes_predicted_names'][img_index]
            metadata_query = [met for met in metadata if met in queries]
            documents[index] = {'title': title, 'url': url, 'metadata': metadata, 'metadata_query':metadata_query}
    return queries, documents
    

def search_query_trec(request, query, topN=10):
    data_dir = os.path.join(BASE_DIR, 'search_data')

    index_path = os.path.join(data_dir, 'index.cord19-LASER_500-b8')
    topic_temp_path = os.path.join(data_dir, 'topic_temp.tsv')
    output_temp_path = os.path.join(data_dir, 'run_temp.tsv')

    analyzer = MainAppConfig.analyzer
    uid2top10terms = MainAppConfig.uid2top10terms
    uid2contents = MainAppConfig.uid2contents
    tokenizer = MainAppConfig.tokenizer
    query2qid = MainAppConfig.query2qid
    qid2rels = MainAppConfig.qid2rels

    query_tokenized = tokenizer.tokenize(str(query))
    with open(topic_temp_path, 'wt') as f:
        f.write(f'1\t{" ".join(query_tokenized)}')

    rels = {}
    if query2qid.get(query.lower()) is not None:
        print("Exact same in exmple queries")
        qid = query2qid[query.lower()]
        rels = qid2rels[qid]
    
    os.system(f'{data_dir}/anserini/target/appassembler/bin/SearchCollection -index {index_path} ' +
        f'-topicreader TsvInt -topics {topic_temp_path} ' +
        f'-removedups -impact -pretokenized -hits {topN} ' +
        f'-output {output_temp_path}')

    documents = {}
    with open(output_temp_path, 'rt') as f:
        cnt = 1
        for line in f:
            _, _, uid, rank, _, _ = line.rstrip().split()
            if len(uid2contents[uid]) < 2:
                continue
            title = uid2contents[uid][0]
            abstract = uid2contents[uid][1].split()
            summary = abstract[:50]
            
            top10_terms = uid2top10terms[uid]
            top10_terms = [re.sub(r'[^\w\s]','', t).lower() for t in top10_terms]

            query_overlapped_term = []
            analyzed_query = analyzer.analyze(query)
            for _, w in enumerate(abstract):
                analyzed_terms = analyzer.analyze(w)
                if len(analyzed_terms) > 0 and analyzed_terms[0] in set(analyzed_query):
                    query_overlapped_term.append(w)
            query_overlapped_term = set(query_overlapped_term)

            score = -1
            if rels.get(uid) is not None:
                score = rels[uid]

            score2relevance = {-1: 'Not judged', 0: 'Irrelevant', 1: 'Partially relevant', 2: 'Fully relevant'}
            relevance = score2relevance[score]

            documents[cnt] = {'title': title, 'abstract': abstract, 'summary':summary, 'relevance':relevance, 'top10_terms': top10_terms, 'query_overlapped_term': query_overlapped_term}
            cnt += 1
            # print(f'RANK: {rank}\nUID: {uid}\nRELEVANCE: {relevance}\nTITLE: {title}\nABSTRACT: {abstract}\nTOP10 TERMS: {" ".join(top10_terms)}')
            # print(f'######################################')

    return documents