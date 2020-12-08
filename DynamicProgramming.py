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

from bleu_hook import _get_ngrams
from profiling import Timer
import profiling
from datetime import datetime

print('Start time: ', datetime.now().time() )
def read_nonempty(filename):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()
            if line.strip() not in ['', '.']]

eng_file = '13_en.txt'
viet_file = '13_vi.txt'

cr_dir = os.getcwd()

vi2en = '{}.fixed.vi2en'.format(viet_file)
en2vi = '{}.fixed.en2vi'.format(eng_file)

eng_file_fixed = lib.fix_file(eng_file)
if not os.path.exists(os.path.join(cr_dir, en2vi)):
	lib.translate_ev(eng_file_fixed)

viet_file_fixed = lib.fix_file(viet_file)
if not os.path.exists(os.path.join(cr_dir, vi2en)):
	lib.translate_ve(viet_file_fixed)


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

# test_bleu()
print('Tokenizing & ngramming ...')
ef_ngrams = tokenize_then_ngram(read_nonempty(eng_file_fixed))
etf_ngrams = tokenize_then_ngram(read_nonempty(en2vi))
vf_ngrams = tokenize_then_ngram(read_nonempty(viet_file_fixed))
vtf_ngrams = tokenize_then_ngram(read_nonempty(vi2en))
# assert len(ef_ngrams) == len(etf_ngrams)
# assert len(vf_ngrams) == len(vtf_ngrams)
# exit()

print('LENGTHs:', len(ef_ngrams), len(vf_ngrams))  # book 20: 3625 x 3596 # book 5: 2479 x 2492
# exit()
print('Finish tokenize & ngram time: ', datetime.now().time())

f = open('working_dir/nothing.book13', 'wb')

# bleu_fn = compute_bleu
bleu_fn = cython_bleu.compute_bleu
bleu_list = []
if not os.path.exists('working_dir/book13_Bleu.nparray'):
  print('Start calculate bleuscores time: ', datetime.now().time())
  print('Calculating Bleuscores ...')
  
  for i in range(len(ef_ngrams)):
  # for i in range(0, 6):
    if i % 5 == 0:
      np.save(f,bleu_list)
      f.close()
      bleu_list = []
      f = open('working_dir/{:04d}.book13'.format(i), 'wb')
    for j in range(len(vf_ngrams)):
      with Timer('bleu'):
        bleu = bleu_fn(ef_ngrams[i], vtf_ngrams[j])
        bleu += bleu_fn(vtf_ngrams[j], ef_ngrams[i])
        bleu += bleu_fn(vf_ngrams[j], etf_ngrams[i])
        bleu += bleu_fn(etf_ngrams[i], vf_ngrams[j])
        bleu_list += [bleu]
  # profiling.print_records()
  np.save(f, bleu_list)
  f.close()


import find_best_pairs
X = []
if not os.path.exists('working_dir/book13_Bleu.nparray'):
  for i in range(len(ef_ngrams)):
  # for i in range(0, 6):
    if i%5==0:
      with open('working_dir/{:04d}.book13'.format(i), 'rb') as f:
        X += list(np.load(f))
  # print(len(X), type(X))
  # exit()
  X = np.array(X)
  X = X.reshape([len(ef_ngrams), len(vf_ngrams)])
  with open('working_dir/book13_Bleu.nparray', 'wb') as f:
    np.save(f, X)

  with open('working_dir/book13_Bleu.nparray', 'rb') as f:
    X_read = np.load(f)

  if X != []:
    assert np.array_equal(X_read, X)

  X = X_read

with open('working_dir/book13_Bleu.nparray', 'rb') as f:
  X_read = np.load(f)

print('Start pairing time: ', datetime.now().time())
print('Pairing ...')
pairs = find_best_pairs.fill_in_table(X_read)

# for (i, j) in pairs[-100:]:
#   eng_sent = ' '.join(ef_ngrams[i][0])
#   vie_sent = ' '.join(vf_ngrams[j][0])
#   print(eng_sent)
#   print(vie_sent)
#   print()
#   input()

print('Finish bleu calculation time: ', datetime.now().time())
print('Saving ...')
with open('Output_Data/book13_pairs.txt', 'w') as f:
  f.write('Input: {} x {} \n\n'.format(len(ef_ngrams),len(vf_ngrams)))
  f.write('Output: {} pairs \n\n'.format(len(pairs)))
  for (i, j) in pairs:
    eng_sent = ' '.join(ef_ngrams[i][0])
    vie_sent = ' '.join(vf_ngrams[j][0])
    f.write('{}\n{}\n\n'.format(eng_sent, vie_sent)) 

print('Done')