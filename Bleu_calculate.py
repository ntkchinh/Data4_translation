from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from tensor2tensor.data_generators import text_encoder
# from tensor2tensor.utils import bleu_hook

import bleu_hook
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import collections
import math
import os
import os.path
import re
import sys
import time
import unicodedata
import numpy as np
import pandas as pd
import six
import problems_vien
import lib
import cython_bleu
import sys
import glob
import tqdm

import find_best_pairs

from bleu_hook import _get_ngrams
from profiling import Timer
import profiling
from datetime import datetime


def read_nonempty(filename):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()
            if line.strip() not in ['', '.']]

# bleu_score & tokenize # tensor2tensor
def tokenize(string):
  return bleu_hook.bleu_tokenize(string)


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


def compute_bleu(references,
                 translations,
                 max_order=4,
                 use_bp=True):
  """Computes BLEU score of translated segments against one or more references.

  Args:
    reference_corpus: list of references for each translation. Each
        reference should be tokenized into a list of tokens.
    translation_corpus: list of translations to score. Each translation
        should be tokenized into a list of tokens.
    max_order: Maximum n-gram order to use when computing BLEU score.
    use_bp: boolean, whether to apply brevity penalty.

  Returns:
    BLEU score.
  """
  reference_length = 0
  translation_length = 0
  bp = 1.0
  geo_mean = 0

  matches_by_order = [0] * max_order
  possible_matches_by_order = [0] * max_order
  precisions = []

  references_tokens, ref_ngram_counts = references
  translations_tokens, translation_ngram_counts = translations

  reference_length += len(references_tokens)
  translation_length += len(translations_tokens)

  overlap = dict((ngram,
                  min(count, translation_ngram_counts[ngram]))
                for ngram, count in ref_ngram_counts.items())

  for ngram in overlap:
    matches_by_order[len(ngram) - 1] += overlap[ngram]
  for ngram in translation_ngram_counts:
    possible_matches_by_order[len(ngram)-1] += translation_ngram_counts[ngram]

  # with Timer('the rest of bleu score'):
  precisions = [0] * max_order
  smooth = 1.0
  for i in range(0, max_order):
    if possible_matches_by_order[i] > 0:
      precisions[i] = matches_by_order[i] / possible_matches_by_order[i]
      if matches_by_order[i] > 0:
        precisions[i] = matches_by_order[i] / possible_matches_by_order[i]
      else:
        smooth *= 2
        precisions[i] = 1.0 / (smooth * possible_matches_by_order[i])
    else:
      precisions[i] = 0.0

  if max(precisions) > 0:
    p_log_sum = sum(math.log(p) for p in precisions if p)
    geo_mean = math.exp(p_log_sum/max_order)

  if use_bp:
    if not reference_length:
      bp = 1.0
    else:
      ratio = translation_length / reference_length
      if ratio <= 0.0:
        bp = 0.0
      elif ratio >= 1.0:
        bp = 1.0
      else:
        bp = math.exp(1 - 1. / ratio)
  bleu = geo_mean * bp
  # print_records()
  return np.float32(bleu)


def test_bleu():

  string1 = 'hello world how are you'
  string2 = string1

  bleu = compute_bleu(
    tokenize_then_ngram([string1])[0],
    tokenize_then_ngram([string2])[0]
  )

  bleu = cython_bleu.compute_bleu(
    tokenize_then_ngram([string1])[0],
    tokenize_then_ngram([string2])[0]
  )

  assert bleu == 1.0, bleu
  print('OK')

  string3 = 'this sentence has no overlapping'

  bleu = cython_bleu.compute_bleu(
    tokenize_then_ngram([string1])[0],
    tokenize_then_ngram([string3])[0]
  )

  original_bleu = bleu_hook.compute_bleu(
      reference_corpus=[bleu_hook.bleu_tokenize(string1)],
      translation_corpus=[bleu_hook.bleu_tokenize(string3)],
  )

  assert abs(bleu - original_bleu)<1e-7, (bleu, original_bleu)
  print('OK')


def Bleu_calculate(eng_file, viet_file, en2vi, vi2en, name_to_save, bad=[]):
  if not os.path.exists('working_dir/ccalign{}_bleu.nparray'.format(name_to_save)):
  
    print('Tokenizing & ngramming ...')
    print('eng file')
    ef_ngrams = tokenize_then_ngram(read_nonempty(eng_file))
    print('en2vi')
    etf_ngrams = tokenize_then_ngram(read_nonempty(en2vi))
    print('vi file')
    vf_ngrams = tokenize_then_ngram(read_nonempty(viet_file))
    print('vi2en file')
    vtf_ngrams = tokenize_then_ngram(read_nonempty(vi2en))

    # assert len(ef_ngrams)==len(etf_ngrams)
    # assert 
    # assert len(ef_ngrams)==len(vf_ngrams)
    if len(ef_ngrams)!=len(etf_ngrams) or 
       len(vf_ngrams)!=len(vtf_ngrams) or 
       len(ef_ngrams)!=len(vf_ngrams):
       bad.append(name_to_save)


    print('LENGTHs:', len(ef_ngrams), len(vf_ngrams)) 
    print('Finish tokenize & ngram time: ', datetime.now().time())

    # ENG bleu:

    f = open('working_dir/ccalign{}_bleu.nparray'.format(name_to_save), 'wb')
    # bleu_fn = compute_bleu
    bleu_fn = cython_bleu.compute_bleu
    bleu_list = []
    
    for i in tqdm.tqdm(range(len(ef_ngrams))):
      bleu = bleu_fn(ef_ngrams[i], vtf_ngrams[i])
      bleu += bleu_fn(vtf_ngrams[i], ef_ngrams[i])
      bleu += bleu_fn(vf_ngrams[i], etf_ngrams[i])
      bleu += bleu_fn(etf_ngrams[i], vf_ngrams[i])
      bleu_list += [bleu]
    
    np.save(f, bleu_list)
    f.close()
  
  print('Done working on ccalign_{}'.format(name_to_save))
return bad

# if __name__ == '__main__':
#   test_bleu()

#   argv = list(sys.argv)
#   argv += [None] * 10

#   numb_of_book = argv[1]
#   start_point = argv[2]

#   if numb_of_book is None:
#     print("Nothing to do")
#     exit()
    
#   eng_file = numb_of_book + '_en.txt'
#   viet_file = numb_of_book + '_vi.txt'

#   print('working on {} and {}'.format(eng_file, viet_file))
#   Dynamic_matching(eng_file, viet_file, numb_of_book, start_point)