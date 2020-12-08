import math
cimport cython
cimport numpy as np

from collections import Counter


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef float compute_bleu(
    tuple references,
    tuple translations,
    int max_order=4,
    int use_bp=1):
  """Computes BLEU score of translated segments against one or more references.
  """
  cdef int reference_length = 0
  cdef int translation_length = 0
  cdef float bp = 1.0
  cdef float geo_mean = 0.0

  cdef list matches_by_order = [0] * max_order
  cdef list possible_matches_by_order = [0] * max_order
  cdef list precisions = []

  cdef list references_tokens = references[0]
  ref_ngram_counts = references[1]

  cdef list translations_tokens = translations[0]
  translation_ngram_counts = translations[1]

  reference_length = len(references_tokens)
  translation_length = len(translations_tokens)

  cdef dict overlap

  overlap = {}
  cdef tuple ngram
  
  for ngram in ref_ngram_counts:
    count = ref_ngram_counts[ngram]
    overlap[ngram] = min(count, translation_ngram_counts[ngram])

  cdef float p_log_sum
  cdef float ratio

  for ngram in overlap:
    matches_by_order[len(ngram) - 1] += overlap[ngram]

  for ngram in translation_ngram_counts:
    possible_matches_by_order[len(ngram)-1] += translation_ngram_counts[ngram]

  # with Timer('the rest of bleu score'):
  precisions = [0.0] * max_order
  cdef float smooth = 1.0
  cdef int i

  for i in range(0, max_order):
    if possible_matches_by_order[i] > 0:
      precisions[i] = matches_by_order[i] / possible_matches_by_order[i]
      if matches_by_order[i] > 0:
        precisions[i] = matches_by_order[i] / possible_matches_by_order[i]
      else:
        smooth *= 2.0
        precisions[i] = 1.0 / (smooth * possible_matches_by_order[i])
    else:
      precisions[i] = 0.0


  cdef float p
  
  if max(precisions) > 0:
    p_log_sum = 0.0
    for p in precisions:
      if p != 0:
        p_log_sum += math.log(p)
    geo_mean = math.exp(p_log_sum/max_order)

  if use_bp == 1:
    if reference_length == 0:
      bp = 1.0
    else:
      ratio = translation_length * 1.0 / reference_length
      if ratio <= 0.0:
        bp = 0.0
      elif ratio >= 1.0:
        bp = 1.0
      else:
        bp = math.exp(1.0 - 1. / ratio)
  bleu = geo_mean * bp
  return float(bleu)