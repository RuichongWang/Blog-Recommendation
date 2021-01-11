# coding=utf-8
"""
Based on TF-IDF Algorithm
Calculate the similarity Matrix for 
articles stored in mongoDB
"""

import datetime
import os
import random
import re
import sys
import time

import jieba  # package for splitting chinese sentect
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

REPEAT_RUNNING = True             # new passages will be uploaded to the server,
# so we need to calculating similarity matrix every once in a while

fit_freq = 2                    # time gap between each trainning, in days

# features you want to use when calculating similarity matrix
fit_on_var = sys.argv[1:]
output_path = '***YOUR_PATH***'


class recommend_passage():
    """
    Parameters
    ----------
    new_word_path           : storing user's new words, e.g.: words in specific domain

    passage_index           : recommend passages similar to passage with index k

    n                       : top n similar passages
    """

    def __init__(self, fit_on_var, new_word_path=None):
        self.tic = time.time()    # timer
        self.new_word_path = new_word_path
        self.fit_on_var = fit_on_var
        self.load_passage_from_mongo()

    def load_passage_from_mongo(self):
        client = MongoClient('***YOUR_MONGO_ADDRESS***')
        db = client.***YOUR_DATABASE***
        collection = db.***YOUR_ASSET***

        # extracting passages
        passages_all = []
        indexes = []
        for i, post in enumerate(collection.find()):
            passages_all.append(post)
            indexes.append([i, str(post['_id'])])

        self.passages_all = passages_all
        self.similarity_table = pd.DataFrame(indexes, columns=['index', 'id'])

    def cut_words(self):
        if self.new_word_path:
            # add user's new word to jieba
            jieba.load_userdict(self.new_word_path)
        passage_to_use = [x[self.var] for x in self.passages_all]
        passage_split = [' '.join(jieba.cut(x)) for x in passage_to_use]
        self.passage_split = passage_split

    def tfidf(self):
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(self.passage_split)

        transformer = TfidfTransformer()
        tfidf_res = transformer.fit_transform(X).toarray()
        self.tfidf_res = tfidf_res

    def cos_sim(self):
        sim_mat = [[np.sum(our_file*x) for x in self.tfidf_res]
                   for our_file in self.tfidf_res]
        sim_mat_res = np.array(sim_mat)
        for i in range(len(sim_mat_res)):
            sim_mat_res[i, i] = 0
        self.sim_mat_res = sim_mat_res
        np.savetxt(
            '/'.join([output_path, 'similarity_matrix_%s' % self.var]), self.sim_mat_res)

    def save_result(self):
        passages_all = self.passages_all
        similarities_file = [x for x in os.listdir(
            output_path) if 'similarity_matrix_' in x]
        var_list = [x.replace('similarity_matrix_', '')
                    for x in similarities_file]
        indexes_file = self.similarity_table

        for i, (sim, var) in enumerate(zip(similarities_file, var_list)):
            if i == 0:
                sim_mat_res = np.loadtxt(output_path+'/'+sim)
            else:
                sim_mat_res += np.loadtxt(output_path+'/'+sim)

        def get_dict(sim_mat_vec):
            sim_mat_vec = sim_mat_vec.argsort()[::-1][:10]
            a = ['rank_%s' % x for x in range(1, 11)]
            b = indexes_file.loc[sim_mat_vec].id.to_list()
            return dict(zip(a, b))

        res_dict = [get_dict(x) for x in sim_mat_res]
        indexes_file['ranks'] = res_dict

        for i, c in enumerate(passages_all):
            temp_id = str(passages_all[i]['_id'])
            similarities = indexes_file[indexes_file.id ==
                                        temp_id]['ranks'].values[0]
            passages_all[i].update({'ranks': similarities})

        client = MongoClient('***YOUR_MONGO_ADDRESS***')
        db = client.***YOUR_DATABASE***
        collection = db.***YOUR_ASSET***

        # rename the asset name if you dont want to overwrite the original one
        collection.drop()
        collection.insert_many(passages_all)

    def fit(self, var):
        self.var = var
        self.cut_words()
        self.tfidf()
        self.cos_sim()

    def run_all(self):
        for i, var in enumerate(self.fit_on_var):
            self.fit(var)
        self.save_result()


res = recommend_passage(fit_on_var)
res.run_all()

if REPEAT_RUNNING:
    while True:
        for i in range(24*fit_freq):
            print('%s: Program Sleeping... Retraining in %s hours' % (
                datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"), 24*fit_freq-i))
            time.sleep(3600)
        res = recommend_passage(fit_on_var)
        res.run_all()
