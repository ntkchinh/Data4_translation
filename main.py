import tensorflow as tf
import numpy as np
import os
import os.path

import lib
import problems_vien



def read_nonempty(filename):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()
            if line.strip() not in ['', '.']]

eng_file = '21_en.txt'
viet_file = '21_vi.txt'


cr_dir = os.getcwd()

print("input files: {}, {}".format(eng_file, viet_file))
print(cr_dir)
vi2en = '{}.fixed.vi2en.txt'.format(viet_file)
en2vi = '{}.fixed.en2vi.txt'.format(eng_file)


# def test_preprocess():
    input_string = '(One) two.Three Mr. Four   Mrs.Five—Ms. Six Seven U.S.A,is_not easy! [at all ]right? Eight.'
    goal_string = '&#91; One &#93; two . Three Mr. Four Mrs. Five - Ms. Six Seven U.S.A , is - not easy ! &#91; at all &#93; right ? Eight .'
                 # &#91; One &#93; two . Three Mr. Four Mrs. Five Ms. Six Seven U.S.A , is not easy ! &#91; at all &#93; right ? Eight . 
    output_string =  lib.fix_contents(input_string)

    if len(output_string) != len(goal_string):
      print(output_string)
      print(goal_string)
      raise ValueError(
          'output length = {}, goal length = {}'.format(len(output_string), len(goal_string)))

    for i, (c1, c2) in enumerate(zip(goal_string, output_string)):
      if c1 != c2:
        raise ValueError('{} != {}'.format(goal_string[i-3:i+3], output_string[i-3:i+3]))

    input('Test OK!')

# test_preprocess()


    # Add more similar examples here.
    # assert preprocess(input_string) == goal_string

eng_file_fixed = lib.fix_file(eng_file)
if not os.path.exists(os.path.join(cr_dir, en2vi)):
	lib.translate_ev(eng_file_fixed)


viet_file_fixed = lib.fix_file(viet_file)
if not os.path.exists(os.path.join(cr_dir, vi2en)):
	lib.translate_ve(viet_file_fixed)

ef_list = read_nonempty(eng_file_fixed)
etf_list = read_nonempty(en2vi)

vf_list = read_nonempty(viet_file_fixed)
vtf_list = read_nonempty(vi2en)


lib.pair_matching(vf_list, vtf_list, ef_list, etf_list);
