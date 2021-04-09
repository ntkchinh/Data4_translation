from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import math
import os
import os.path
import re
import sys
import time
import six
import cython_bleu
import glob
import tqdm

import find_best_pairs

from bleu_hook import _get_ngrams, bleu_tokenize, compute_bleu
from profiling import Timer
import profiling
from datetime import datetime


def read_nonempty(filename):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()
            if line.strip() not in ['', '.']]

# bleu_score & tokenize # tensor2tensor
def tokenize(string):
  return bleu_tokenize(string)


def get_latest_i(numb_of_book):
  path = 'working_dir/*.book{}'.format(numb_of_book)
  files = glob.glob(path)
  files = [f.split('/')[-1] for f in files if 'nothing' not in f]
  files = [f.split('.')[0] for f in files]
  if not files:
    return 0
  else:
    return max([int(f) for f in files])


def tokenize_then_ngram(list_of_string):
  result = []
  for string in tqdm.tqdm(list_of_string):
    # with Timer('tok_ngram'):
    tokens = tokenize(string)
    ngrams = _get_ngrams(tokens, max_order=4)
    result.append((tokens, ngrams))
  # profiling.print_records()
  return result


def Bleu_calculate(trans_file, ref_file, name_to_save):
  if not os.path.exists('working_dir/{}_bleu.nparray'.format(name_to_save)):
  
    print('Tokenizing & ngramming ...')
    print('trans file')
    with open(trans_file,'r') as f:
      trans_lines = f.readlines() 
    trans_ngrams = tokenize_then_ngram(trans_file)

    print('ref file')
    with open(ref_file,'r') as f:
      ref_lines = f.readlines() 
    ref_ngrams = tokenize_then_ngram(ref_file)

    assert len(trans_ngrams)==len(ref_ngrams)

    print('LENGTHs:', len(trans_ngrams), len(ref_ngrams)) 
    print('Finish tokenize & ngram time: ')

    f = open('working_dir/{}_bleu.nparray'.format(name_to_save), 'wb')
    bleu_fn = cython_bleu.compute_bleu
    bleu_list = []
    
    for i in tqdm.tqdm(range(len(ref_ngrams))):
      bleu = bleu_fn(trans_ngrams[i], ref_ngrams[i])
      bleu += bleu_fn(ref_ngrams[i], trans_ngrams[i])
      bleu_list += [bleu]
    np.save(f, bleu_list)

    f.close()
  
  print('Done working on {}'.format(name_to_save))


# ef = '8_ccalign.en'
# vf = '8_ccalign.vi'
# en2vi = '8_ccalign.en2vi'
# vi2en = '8_ccalign.vi2en'
# Bleu_calculate(ef, vf, en2vi, vi2en, 'try8')
# print('done')