from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.utils import bleu_hook


import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import collections
import math
import os
import re
import sys
import time
import unicodedata
import numpy as np
import pandas as pd
import six

def read_nonempty(filename):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()
            if line.strip() not in ['', '.']]

# bleu_score & tokenize # tensor2tensor
def tokenize(string):
  return bleu_hook.bleu_tokenize(string)


def tokenize_n(string, n=3):
  result = []

  for s in tokenize(string):
    i = 0
    while i < len(s):
      result.append(s[i:i+n])
      i += n

  return result


def bleu_score(ref_string, hyp_string, case_sensitive=False):
  """Compute BLEU for two strings (ref and hypothesis translation)."""
  
  # assert len(ref_string) == len(hyp_string), ("{} != {}".format(
  #     len(ref_string), len(hyp_string)))
  if not case_sensitive:
    ref_string = ref_string.lower()
    hyp_string = hyp_string.lower()
  ref_tokens = [tokenize(ref_string)]
  hyp_tokens = [tokenize(hyp_string)]
  return bleu_hook.compute_bleu(ref_tokens, hyp_tokens)


def check_mrs(content, i):
  is_mr = (i >= 2 and 
           content[i-2:i].lower() in ['mr', 'ms'] and
           (i < 3 or content[i-3] == ' '))
  is_mrs = (i >= 3 and 
            content[i-3:i].lower() == 'mrs' and 
            (i < 4 or content[i-4] == ' '))
  return is_mr or is_mrs


def check_ABB_mid(content, i):
  if i <= 0:
    return False
  if i >= len(content)-1:
    return False
  l, r = content[i-1], content[i+1]
  return l.isupper() and r.isupper()


def check_ABB_end(content, i):
  if i <= 0:
    return False
  l = content[i-1]
  return l.isupper()


def fix_file(filename):
  if not os.path.exists(filename + '.fixed'):
    with open(filename, 'r') as file:
      contents = file.read()
    contents = fix_contents(contents)

    with open(filename+'.fixed', 'w') as file:
      file.write(contents)

  return filename + '.fixed'


def fix_contents(contents):
  # first step: replace special characters 
  check_list = ['\uFE16', '\uFE15', '\u0027','\u2018', '\u2019',
                '“', '”', '\u3164', '\u1160', 
                '\u0022', '\u201c', '\u201d', '"',
                '[', '\ufe47', '(', '\u208d'
                ']', '\ufe48', ')' , '\u208e', '—', '_']
  alter_chars = ['?', '!', '&apos;', '&apos;', '&apos;',
                 '&quot;', '&quot;', '&quot;', '&quot;', 
                 '&quot;', '&quot;', '&quot;', '&quot;', 
                 '&#91;', '&#91;', '&#91;', '&#91;',
                 '&#93;', '&#93;', '&#93;', '&#93;', '-', '-']

  replace_dict = dict(zip(check_list, alter_chars))

  new_contents = ''
  for char in contents:
    new_contents += replace_dict.get(char, char)
  contents = new_contents

  # second: add spaces
  check_sp_list = [',', '?', '!', '&apos;', '&quot;', '&#91;', '&#93;', '-']
  rpl_list = [' , ', ' ? ', ' ! ', ' &apos;', ' &quot; ', ' &#91; ', ' &#93; ', ' - ']
  replace_dict = dict(zip(check_sp_list, rpl_list))

  new_contents = ''
  
  i = 0
  while i < len(contents):
    char = contents[i]

    found = False
    for string in replace_dict:
      if string == contents[i: i+len(string)]:
        new_contents += replace_dict[string]
        i += len(string)
        found = True
        break
    
    if not found:
      new_contents += char
      i += 1

  contents = new_contents

  # contents = contents.replace('.', ' . ')
  new_contents = ''
  for i, char in enumerate(contents):
    if char != '.':
      new_contents += char
      continue
    elif check_mrs(contents, i):
      # case 1: Mr. Mrs. Ms.
      new_contents += '. '
    elif check_ABB_mid(contents, i):
      # case 2: U[.]S.A.
      new_contents += '.'
    elif check_ABB_end(contents, i):
      # case 3: U.S.A[.]
      new_contents += '. '
    else:
      new_contents += ' . '

  contents = new_contents
  
  # third: remove not necessary spaces.

  new_contents = ''
  for char in contents:
    if new_contents and new_contents[-1] == ' ' and char == ' ':
      continue
    new_contents += char
  contents = new_contents
  contents = contents.replace('* . \n', "* ." )
  
  return contents.strip()


def run(cmd):
  print('\n================')
  print(cmd)
  print('================\n')
  os.system(cmd)


# translate # Trieu Trinh # https://github.com/thtrieu
def translate_ev(decode_from_file): # name of file "abc.."
  # Set up
  problem = 'translate_envi_iwslt32k'  # @param
  hparams_set = 'transformer_tiny'  # @param
  data_dir = 'data/translate_envi_iwslt32k'  # @param
  logdir = 'checkpoints/translate_envi_iwslt32k_tiny'  # @param
  tmp_dir = 'raw'  # @param
  is_demo = True  # @param {type: "boolean"}
  use_tpu = False
  cr_dir = os.getcwd()

  # Now we make all the paths absolute.

  logdir = os.path.join(cr_dir, logdir)
  data_dir = os.path.join(cr_dir, data_dir)
  tmp_dir = os.path.join(cr_dir, tmp_dir)

  if is_demo:
    run_logdir = os.path.join(logdir, 'demo')
    if tf.io.gfile.exists(run_logdir):
      tf.io.gfile.deleterecursively(run_logdir)
  else:
    run_logdir = logdir

  decode_from_file = os.path.join(cr_dir, decode_from_file)
  decode_to_file = os.path.join(cr_dir, '{}.en2vi'.format(decode_from_file))

  if use_tpu:
    # TPU wants the paths to begin with gs://
    ckpt_dir = logdir.replace(mount_point, 'gs://{}'.format(google_cloud_bucket))

  print('Decode to file {}'.format(decode_to_file))

  run('python t2t_decoder.py' +
      ' --data_dir="{}"'.format(data_dir) + ' --problem={}'.format(problem) +
      ' --hparams_set={}'.format(hparams_set) +
      ' --model={}'.format('transformer') +
      ' --decode_hparams={}'.format("beam_size=4,alpha=0.6") +
      ' --decode_from_file="{}"'.format(decode_from_file) +
      ' --decode_to_file="{}"'.format(decode_to_file) +
      ' --output_dir="{}"'.format(logdir)
    )


def translate_ve(decode_from_file): # name of file "abc.."
  # Set up
  problem = 'translate_vien_iwslt32k'  # @param
  hparams_set = 'transformer_tiny'  # @param
  data_dir = 'data/translate_vien_iwslt32k'  # @param
  logdir = 'checkpoints/translate_vien_iwslt32k_tiny'  # @param
  tmp_dir = 'raw'  # @param
  is_demo = True  # @param {type: "boolean"}
  use_tpu = False
  cr_dir = os.getcwd()

  # Now we make all the paths absolute.
  logdir = os.path.join(cr_dir, logdir)
  data_dir = os.path.join(cr_dir, data_dir)
  tmp_dir = os.path.join(cr_dir, tmp_dir)

  if is_demo:
    run_logdir = os.path.join(logdir, 'demo')
    if tf.io.gfile.exists(run_logdir):
      tf.io.gfile.deleterecursively(run_logdir)
  else:
    run_logdir = logdir

  decode_from_file = os.path.join(cr_dir, decode_from_file)
  decode_to_file = os.path.join(cr_dir, '{}.vi2en'.format(decode_from_file))
   
  if use_tpu:
    # TPU wants the paths to begin with gs://
    ckpt_dir = logdir.replace(mount_point, 'gs://{}'.format(google_cloud_bucket))

  print('Decode to file {}'.format(decode_to_file))

  run('python t2t_decoder.py' +
      ' --data_dir="{}"'.format(data_dir) + ' --problem={}'.format(problem) +
      ' --hparams_set={}'.format(hparams_set) +
      ' --model={}'.format('transformer') +
      ' --decode_hparams={}'.format("beam_size=4,alpha=0.6") +
      ' --decode_from_file="{}"'.format(decode_from_file) +
      ' --decode_to_file="{}"'.format(decode_to_file) +
      ' --output_dir="{}"'.format(logdir)
    )


def compare(cand, cand_transl,  ## list of 1 item;
            ref, ref_transl, library, ## list of items.
            h=1, z=1):
  similarity = []
  data = []
  pair_list = []
  # len_rate_list = []

  for j in range(min(h, len(ref))):
    if not cand:
      print('None of cand left')
      return bleu_list, index_list, outpairs
    if not ref:
      print('None of ref left')
      return bleu_list, index_list, outpairs
    # print('j', j)  

    c, ct = cand, cand_transl
    r, rt = ref[j], ref_transl[j]
    q = tuple([c,r])
    len_ratio = 0
    if len(c) <= len(r):
      len_ratio = round(len(c)/len(r), 2)
    else:
      len_ratio = round(len(r)/len(c), 2)
    # print('>:', c, r)
    # print('*: ',len(c), len(r), len_ratio)
    # input()
    # len_rate_list += [len_ratio]
    if q not in library:
      data.append((
        (bleu_score(ct, r), ct, r),
        (bleu_score(r, ct), r, ct),
        (bleu_score(c, rt), c, rt),
        (bleu_score(rt, c), rt, c)
      ))
      bleu = round(sum([b for b, _, _ in data[-1]])/len(data[-1]), 3)
      if len_ratio < 0.5:
        bleu = 0

      similarity.append(bleu)
      pair_list.append([c,r])
      library[q] = bleu
    else:
      # print('bleu from lib')
      similarity.append(library[q])
      pair_list.append(q)

  index_list = []
  outpairs = []
  bleu_list = []

  temp = max(similarity)
  m = similarity.index(temp)
  index_list.append(m)
  bleu_list.append(temp)
  outpairs.append(pair_list[m])

  for i in range (z-1): 
    similarity[m] = 0
    temp = max(similarity)
    m = similarity.index(temp)
    index_list.append(m)
    bleu_list.append(temp)
    outpairs.append(pair_list[m])
  #   input()

  return bleu_list, index_list, outpairs, library


def ladder_compare(cand, cand_transl,  ## list of more than 3 items
                   ref, ref_transl,  ##library,  ## list of more than 3 items
                   H=1, k=0.2, r=5):
  library = {}
  bleu_frequen = []
  output_list = []
  del_count = 0
  h_list = []
  max_i = min(len(cand), len(ref))
  print('max_i', max_i)
  # input()
  for i in range(max_i):
    print('\n round', i)
    h = int(abs((len(ref) - len(cand)) * H) + 1)
    # h = int(min(abs((len(ref) - len(cand)) * H) + 1, 7))
    h_list.append(h)
    bleu_list, index_list,\
    outpairs, new_library = compare(cand[0], cand_transl[0],
                                    ref, ref_transl, library,
                                    h=h, z=3)
    bleu_divide_list = []
    bleu_divide_pair = []
    ind_divide_list = []
    library = new_library
    m = bleu_list.index(max(bleu_list)) 
    for j in range(len(index_list)):        
      ind = index_list[j]
      bl0 = []
      for numb in range(r):
        h = int(abs((len(ref) - len(cand)) * H) + 1)
        h_list.append(h)
        bl, il, ol, new_lib = compare(cand[1+numb], cand_transl[1+numb],
                                      ref[(1+ind) : ],
                                      ref_transl[(1+ind) : ],
                                      library, h=h, z=1)
        library = new_lib
        ind += il[-1]+1
        bl0 += bl
        if len(cand) < 1:
          break
        if len(ref) < h:
          break
      bleu_divide_list += [bl0]
      
    check_bleu_list = []
    print('len(bleu_divide_list[-1]:', len(bleu_divide_list[-1]))
    for j in range(len(index_list)):
      check_bleu_list += [sum(bleu_divide_list[j])]
    
    n = check_bleu_list.index(max(check_bleu_list))
    print('max check_bleu_list:', check_bleu_list[n])
    if m != n:
      print(check_bleu_list[n])
      if check_bleu_list[n] <= k * r:
        n = m
        print('n=m')
      else:
        print('n=n')
    # input()
    if bleu_list[n] > k and check_bleu_list[n] > k * r:
      output_list.append('**{}, {}\n >> {}\n >> {}\n'.format(
          i, bleu_list[n], outpairs[n][0], outpairs[n][-1]))
      # output_list.append('>> \n {}\n >> {}\n'.format(
      #     outpairs[n][0], outpairs[n][-1]))
      del ref[0:index_list[n]+1]
      del ref_transl[0:index_list[n]+1]
    else:
      ref.pop(0)
      ref_transl.pop(0)
      del_count += 1
    cand.pop(0)
    cand_transl.pop(0)

    print('end round:{} \n cand:{}, ref:{}, lib:{}'.format(
        i, len(cand), len(ref), len(library)))
    
    h = int(abs((len(ref) - len(cand)) * H) + 1)
    if len(cand) < (r+1):
      print("case 1")
      return output_list, library, del_count, bleu_frequen, h_list
    if len(ref) < h*(r+1): ## *1200: ## 
      return output_list, library, del_count, bleu_frequen, h_list
  print('case 3')
  return output_list, library, del_count, bleu_frequen, h_list


def beam_compare(cand, cand_transl, ref, ref_transl,
                 H=1, k=0.2, r=5):
  history = []
  h_list = []
  if os.path.exists('checkpoint'):
    with open('checkpoint', 'r') as f:
      history = f.readlines()

    cl, rl = history[-1].strip().split()
    cl, rl = int(cl), int(rl)
    print('Remain {} {}'.format(cl, rl))
    cand = cand[-cl:]
    cand_transl = cand_transl[-cl:]
    ref = ref[-rl:]
    ref_transl = ref_transl[-rl:]

  assert len(cand) == len(cand_transl)
  assert len(ref) == len(ref_transl)
  print('AT THE BEGINNING: cand:{}, ref:{}'.format(len(cand), len(ref)))

  if not cand:
    print('end, no cand')
    return
  if not ref:
    print('end, no ref')
    return
  
  h = int(abs((len(ref) - len(cand)) * H) + 1)

  if len(cand) >= (r+1) and len(ref) >= h*(r+1):
    output_list, library,\
    del_count, bleu_frequen, nh_list = ladder_compare(cand, cand_transl,
                                            ref, ref_transl,
                                            H=H, k=k, r=r)
  print('out of ladder_compare')
  print('cand: {}, ref: {}, output_list:{}'.format(len(cand),
                                                    len(ref),
                                                    len(output_list)))
  # input()
  h_list += nh_list

  # 1 item left in cand or less than 4 left in ref => no beam loop
  while cand and ref:
    h = int(abs((len(ref) - len(cand)) * H) + 1)
    bleu_list, index_list, outpairs, new_lib = compare(cand[0], cand_transl[0],
                                              ref, ref_transl, library,
                                              h=h, z=1)
    library = new_lib
    cand.pop(0)
    cand_transl.pop(0)

    for b in bleu_list:
      bleu_frequen+= [b]

    if bleu_list[-1] > k:
      output_list.append('**{} \n {}\n >> {}\n >> {}\n'.format(
          r, bleu_list[-1], outpairs[-1][0], outpairs[-1][-1]))
      # output_list.append('>> \n {}\n >> {}\n'.format(
      #     outpairs[-1][0], outpairs[-1][-1]))
      print('1 added')
      del ref[0:index_list[-1]+1]
      del ref_transl[0:index_list[-1]+1]
    else:
      del_count += 1
      ref.pop(0)
      ref_transl.pop(0)

    if not cand:
      print('end, no cand')
      break
    if not ref:
      print('end, no ref')
      break

  print('*** output_list:', len(output_list))
  print('*** number of eliminate:', del_count)

  print('out of while loop. Recording output...')


  # with open('checkpoint', 'w') as f:
  #   [f.write(line) for line in history]
  #   f.write('{} {}\n'.format(len(cand), len(ref)))

  print('output:',len(output_list))
  plt.title("H range", fontsize=14)
  plt.hist(h_list, 10)
  plt.show()
  return output_list

def pair_matching(listv,listv2e, liste, liste2v, H=1):
  print('Pairing ...')

  if len(listv) <= len(liste):
    output_list = beam_compare(listv, listv2e, liste, liste2v, H=H)
  else:
    output_list = beam_compare(liste, liste2v, listv, listv2e, H=H)
  print('Done') 
  return output_list