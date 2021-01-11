#coding=utf-8
import os
import sys
import time

import numpy as np
import pandas as pd

passage_id = sys.argv[1]
output_path = '***YOUR_PATH***'
top_n_paper = 5


def recommend(similarities_file, indexes_file, var_list, passage_id, top_n=5):
    for sim, var in zip(similarities_file, var_list):
        sim_mat_res = np.loadtxt(sim)
        passage_index = indexes_file[indexes_file.id ==
                                     passage_id].values[0][0]
        sim_vec = sim_mat_res[passage_index, :]
        indexes_file[var] = [round(x * 100, 2) for x in sim_vec]

    indexes_file['average_sim'] = np.mean(indexes_file[var_list], axis=1)
    indexes_file = indexes_file.sort_values('average_sim',
                                            ascending=False).head(10)

    print('Top %s Similar Passages of Passage #%s' % (top_n_paper, passage_id))
    print('\n   \tPassage ID\t\t\t\t %s_similarity' %
          '_similarity\tAverage_similarity'.join(var_list))

    to_prints = indexes_file[['id'] + var_list + ['average_sim']].values
    for to_print in to_prints:
        print('   %s\t\t\t   %s%%' %
              (to_print[0], '%%\t\t'.join([str(x)
                                           for x in list(to_print)[1:]])))


similarities_file = [
    x for x in os.listdir(output_path) if 'similarity_matrix_' in x
]
var_list = [x.replace('similarity_matrix_', '') for x in similarities_file]
indexes_file = pd.read_csv(output_path + '/indexes.csv')

recommend(similarities_file, indexes_file, var_list, passage_id, top_n_paper)
