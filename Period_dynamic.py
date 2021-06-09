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

from bleu_hook import _get_ngrams
from profiling import Timer
import profiling
from datetime import datetime


def find_latest_hk(name_of_file):
  path = 'working_dir/nothing.{}_*_*'.format(name_of_file)
  files = glob.glob(path)
  hk_str = [filename.split('_')[-2:] for filename in files]
  hk = sorted([(int(h), int(k)) for h, k in hk_str])
  if not hk:
    return [0, 0]
  else:
    return hk[-1]


def find_latest_i(name_of_file, h, k):
  path = 'working_dir/{}_{}_{}_*'.format(name_of_file, h, k)
  files = glob.glob(path)
  i_str = [filename.split('_')[-1] for filename in files]
  latest_i = sorted([int(i) for i in i_str])
  if not latest_i:
    return 0
  else:
    return latest_i[-1]


def read_nonempty(filename):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()
            if line.strip() not in ['', '.']]


def read_lines(filename):
  with open(filename, 'r') as f:
    return [line.strip() for line in f.readlines()]

# bleu_score & tokenize # tensor2tensor
def tokenize(string):
  return bleu_hook.bleu_tokenize(string)


def tokenize_then_ngram(list_of_string):
  result = []
  for string in list_of_string:
    with Timer('tok_ngram'):
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


def Dynamic_matching(eng_file, viet_file, en2vi, vi2en, name_of_file, input_segment=0):
  print('Start time: ', datetime.now().time())
  cr_dir = os.getcwd()
  eng_file_fixed = eng_file + '.fixed'
  viet_file_fixed = viet_file + '.fixed'

  ef_sentences = read_lines(eng_file_fixed)
  etf_sentences = read_lines(en2vi)
  vf_sentences = read_lines(viet_file_fixed)
  vtf_sentences = read_lines(vi2en)
  
  if len(ef_sentences) != len(etf_sentences) or len(vf_sentences) != len(vtf_sentences):
    print(len(ef_sentences), len(etf_sentences))
    print(eng_file, viet_file)
    return
  
  if not os.path.exists(cr_dir + '/Output_Data/Pairs_index{}.nparray'.format(name_of_file)):
    print('Calculating')
   
    print('Tokenizing & ngramming ...')
    print('eng file')
    ef_ngrams = tokenize_then_ngram(ef_sentences)
    print('en2vi')
    etf_ngrams = tokenize_then_ngram(etf_sentences)
    print('vi file')
    vf_ngrams = tokenize_then_ngram(vf_sentences)
    print('vi2en file')
    vtf_ngrams = tokenize_then_ngram(vtf_sentences)

    print('LENGTHs:', len(ef_ngrams), len(vf_ngrams)) 

    print('Finish tokenize & ngram time: ', datetime.now().time())
    
    #  OLD
      # if len(ef_ngrams) < 2000 or len(vf_ngrams) < 2000:
      #   set_segment = min(len(vf_ngrams), len(ef_ngrams))
      # elif len(ef_ngrams) <= 4000 or len(vf_ngrams) <= 4000:
      #   set_segment = 2000
      # else:
      #   set_segment = 3000

      # if input_segment != 0:
      #   segment = input_segment
      # else:
      #   segment = set_segment

      # print('segment: ', segment)
    
    # NEW
    if input_segment != 0:
      segment_i = input_segment
      segment_j = input_segment
    else:
      if len(ef_ngrams) < 2000 or len(vf_ngrams) < 2000:
        segment_i = len(ef_ngrams)
        segment_j = len(vf_ngrams)
      elif len(ef_ngrams) <= 4000 or len(vf_ngrams) <= 4000:
        segment_i = 2000
        segment_j = 2000
      else:
        segment_i = 3000
        segment_j = 3000

    # print('segment: ', segment)

    i, j = find_latest_hk(name_of_file)
    result = []
  
    while True:
      # i_end = i + segment
      # j_end = j + segment
      i_end = i + segment_i
      j_end = j + segment_j


      if i_end >= len(ef_ngrams) or j_end >= len(vf_ngrams):
        i_end = len(ef_ngrams)
        j_end = len(vf_ngrams)

      ef_ngrams_i, etf_ngrams_i  = ef_ngrams[i:i_end], etf_ngrams[i:i_end]
      vf_ngrams_j, vtf_ngrams_j  = vf_ngrams[j:j_end], vtf_ngrams[j:j_end]

      pairs = bleu_then_match(ef_ngrams_i, etf_ngrams_i,
                              vf_ngrams_j, vtf_ngrams_j,
                              name_of_file, i, j)
      
      for m, n in pairs:
        result.append([m+i, n+j]) 
      
      if i_end == len(ef_ngrams):
        break

      i, j = result[-1]
      i += 1
      j += 1 
    with open('Output_Data/Pairs_index{}.nparray'.format(name_of_file), 'wb') as f:
      np.save(f, result)
    print('Finish Calculation: ', datetime.now().time())
  
  if not os.path.exists(cr_dir + '/Output_Data/{}_pairs.txt'.format(name_of_file)):
    print('Saving ...')
    with open('Output_Data/Pairs_index{}.nparray'.format(name_of_file), 'rb') as f:
      result = np.load(f)

    with open('Output_Data/{}_pairs.txt'.format(name_of_file), 'w') as f:
      f.write('Input: {} x {} \n\n'.format(len(ef_sentences),len(vf_sentences)))
      f.write('Output: {} pairs \n\n'.format(len(result)))
      for (i, j) in result:
        eng_sent = (ef_sentences[i])
        vie_sent = (vf_sentences[j])
        f.write('{}\n{}\n\n'.format(eng_sent, vie_sent)) 
  
  print('Done')
  print('finish time: ', datetime.now().time())


def bleu_then_match(ef_ngrams, etf_ngrams, vf_ngrams, vtf_ngrams,
                    name_of_file, h, k):
  latest_i = find_latest_i(name_of_file, h, k)
  name_of_file = '{}_{}_{}'.format(name_of_file, h, k)
  f = open('working_dir/nothing.{}'.format(name_of_file), 'wb')
  # bleu_fn = compute_bleu
  bleu_fn = cython_bleu.compute_bleu
  bleu_list = []

  if not os.path.exists('working_dir/Bleu_{}.nparray'.format(name_of_file)):
    for i in range(latest_i, len(ef_ngrams)):
      if i % 5 == 0:
        np.save(f,bleu_list)
        f.close()
        bleu_list = []
        f = open('working_dir/{}_{:04d}'.format(name_of_file, i), 'wb')
      for j in range(len(vf_ngrams)):
        bleu = bleu_fn(ef_ngrams[i], vtf_ngrams[j])
        bleu += bleu_fn(vtf_ngrams[j], ef_ngrams[i])
        bleu += bleu_fn(vf_ngrams[j], etf_ngrams[i])
        bleu += bleu_fn(etf_ngrams[i], vf_ngrams[j])
        bleu_list += [bleu]
    np.save(f, np.float32(bleu_list))
    f.close()


  import find_best_pairs
  X = []
  if not os.path.exists('working_dir/Bleu_{}.nparray'.format(name_of_file)):
    for i in range(len(ef_ngrams)):
      if i%5==0:
        with open('working_dir/{}_{:04d}'.format(name_of_file, i), 'rb') as f:
          X += list(np.load(f))
    X = np.array(X)
    X = X.reshape([len(ef_ngrams), len(vf_ngrams)])
    with open('working_dir/Bleu_{}.nparray'.format(name_of_file), 'wb') as f:
      np.save(f, X)

    with open('working_dir/Bleu_{}.nparray'.format(name_of_file), 'rb') as f:
      X_read = np.load(f)

    if X != []:
      assert np.array_equal(X_read, X)

    X = X_read

  with open('working_dir/Bleu_{}.nparray'.format(name_of_file), 'rb') as f:
    X_read = np.load(f)

  pairs = find_best_pairs.fill_in_table(X_read)
  return pairs
  

if __name__ == '__main__':
  # test_bleu()
  argv = list(sys.argv)
  argv += [None] * 10

  name_of_file = argv[1]
  # if argv[2] != None:
  #   segment = argv[2]
  # else:
  #   segment = 0
  
  if name_of_file is None:
    print("Nothing to do")
    exit()

  eng_file = name_of_file + '_en.txt'
  viet_file = name_of_file + '_vi.txt'
  Dynamic_matching(eng_file, viet_file, name_of_file)
