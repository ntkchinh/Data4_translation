import os
import glob
from collections import defaultdict as ddict
import tqdm
from matplotlib import pyplot as plt
import numpy as np
import lib

def get_num2txt(files):

    files.sort()

    # assert all(['_m_' in f for f in files])


    def extract_num(fname):
        # return fname.split('_m_')[0]
        return fname.split('_')[0]


    num2txt = ddict(lambda: [])

    for f in files:
        num = extract_num(f)
        # print(num)
        # input()
        if num is None:
            continue

        num2txt[num] += [f]

    num2txt_fail = {
        num: fs
        for num, fs in num2txt.items()
        if len(fs) != 2
    }
    # print(len(num2txt_fail))
    # print(num2txt_fail)

    num2txt = {
        num: fs
        for num, fs in num2txt.items()
        if len(fs) == 2
    }
    # print(len(num2txt))
    
    # assert len(num2txt_fail) == 0
    return num2txt

# num2txt = get_num2txt(glob.glob('fix/*'))
# print(len(num2txt))
# with open('remain in pair.txt', 'w')

def fix_files(f):
    with open(f, 'r') as fi:
        lines = fi.readlines()
    bf_len = len(lines)
    # print('len file: ', len(lines))
    fixed_lines = ['']
    string = ''
    for line in tqdm.tqdm(lines):
        if line != '\n':
            string += ' '
            string += line.strip()
            # print(string)
            # input()
        else:
            fixed_lines.append(string)
            string = ''
    # print('after fix 1: ', len(fixed_lines))
    af_len = len(fixed_lines)
    
    # # replace '\n' --> ' '
    # # replace '\n\n'.. -> '\n'
    # for line in lines:
    #     line = line.strip()

    #     if '|' in line:
    #         continue
    
    #     if line != '':
    #         fixed_lines[-1] += ' ' + line
    #     else:
    #         if fixed_lines[-1] != '':
    #             fixed_lines.append('')
    #remove short sentences
    
    # output_lines = []
    # for l0 in fixed_lines:
    #     if len(lines) > 20:
    #         output_lines.append(l0)
    # print('after fix 2: ', len(output_lines))
    # for i in range(100):
    #     print(output_lines[i])
    # new_f = f + new
    with open(f , 'w') as fo:
        for l in fixed_lines:
            fo.write(l + '\n')
    return bf_len, af_len

def split_files(f):
    with open(f, 'r') as f:
        lines = f.readlines()
    bf_len = len(lines)
    output_lines = []
    for l in lines:
        fix_lines = l.split('.')
    for l in fix_lines:
        if len(l)>20:
            output_lines.append(l)

    af_len = len(output_lines)
    for i in range(20000,20200):
        print(output_lines[i])

    
    # with open(f , 'w') as fo:
    #     for l in output_lines:
    #         fo.write(l + '\n')
    

work_dir = os.path.join(os.getcwd(), 'law_txt')
files = os.listdir(work_dir)
print(len(files))

# len_change = ddict(lambda: [])
numb_sent_en = 0
numb_sent_vi = 0
for i in tqdm.tqdm(range(1, 10433)):
    enf = os.path.join(work_dir, '{}_en.txt'.format(i))
    vif = os.path.join(work_dir, '{}_vi.txt'.format(i))
    if os.path.exists(enf):
        numb_sent_en += len(lib.read_nonempty(enf))
#         len_change[i] += [af, bf]

    if os.path.exists(vif):
        numb_sent_vi += len(lib.read_nonempty(vif))
#         bf, af = fix_files(vif)
#         len_change[i] += [af, bf]
print(numb_sent_en)
print(numb_sent_vi)

def wc_l(f):
    with open(f, 'r') as fi:
        return len(fi.readlines())

def counting():
    diffs = []
    fracs = []
    rm_files = []

    num2txt = get_num2txt(glob.glob('fix/*'))
    num_list = []
    for num, (f1, f2) in num2txt.items():
        num_list.append(num)
    with open('num_list.txt', 'w') as f:
        for num in num_list:
            f.write(str(num) + '\n')
        # l1 = wc_l(f1)
        # l2 = wc_l(f2)

        # d = abs(l1-l2)
        # diffs.append(d)
        # # fracs.append(d*1.0/min(l1, l2))
        # fracs.append(max(l1/l2, l2/l1))
        # if max(l1/l2, l2/l1) > 1.5:
        #     rm_files.append([f1, f2])
    # print(len(rm_files))
    return num_list


        # if d == 1893:
        #     os.system('code ' + f1)
        #     os.system('code ' + f2)

    # diffs.sort()
    # fracs.sort()
    # # print(diffs[-20:])
    # # plt.hist(diffs, bins=100, range=(0, 1.))
    # print(fracs[0:10])
    # print(fracs[-10:])
    # to_eliminate = []
    # for num in fracs:
    #     if num > 1.5:
    #         to_eliminate.append(num)
    # print(to_eliminate)
    # print(len(to_eliminate))
    # plt.hist(fracs, bins=10, range=(0, 2))
    # plt.show()

    # count = ddict(lambda: 0)

    # old_d = None

    # for d in diffs:
    #     count[d] += 1

    # xy = []

    # s =  0
    # for d, n in sorted(count.items())[::-1]:
    #     s += n
    #     xy.append((d, s))

    # x, y = zip(*xy[::-1])

    # plt.plot(x, y)
    # plt.show()
   
# num_list = counting()
# print(num_list)
# print(len(rm_files))
# for [f0, f1] in rm_files:
#     os.system('mv {} fix/long_to_far'.format(f0))
#     os.system('mv {} fix/long_to_far'.format(f1))


def show_hist():
    all_lens = []
    files = glob.glob('fix/*')

    for f in files:
        all_lens.append(wc_l(f))

    print(sum(all_lens))

    plt.hist(all_lens, bins=100, range=(0, 1500))
    plt.show()

# show_hist()


def rename_envi():

    def test_vi(f):
        with open(f, 'r') as fi:
            lines = fi.readlines()
        return any([' và ' in line for line in lines])


    def test_en(f):
        with open(f, 'r') as fi:
            lines = fi.readlines()
        return any([' and ' in line for line in lines])
    num2txt = get_num2txt(glob.glob('pass/*'))
    items = list(num2txt.items())
    count = 10381
    
    for num, (f1, f2) in items:
        count += 1
        vi1, en1 = test_vi(f1), test_en(f1)
        vi2, en2 = test_vi(f2), test_en(f2)

        check1 = vi1 != en1  # a = b + c  ....    a = plus(b, c)
        check2 = vi2 != en2  # a = b == c ....   a = equal(b, c)
        check3 = vi1 == en2
        check4 = vi2 == en1

        if not (check1 and check2 and check3 and check4):
            import pdb; pdb.set_trace()

        if vi2:
            f1, f2 = f2, f1

        os.system('mv {} {}.vi'.format(f1, count))
        os.system('mv {} {}.en'.format(f2, count))

# rename_envi()

def extract_fail():


    def test_vi(f):
        with open(f, 'r') as fi:
            lines = fi.readlines()
        return any([' và ' in line for line in lines])


    def test_en(f):
        with open(f, 'r') as fi:
            lines = fi.readlines()
        return any([' and ' in line for line in lines])


    def show(f1, f2):
        with open(f1, 'r') as f1i:
            lines1 = f1i.read()
        with open(f2, 'r') as f2i:
            lines2 = f2i.read()
        
        print(lines1)
        print('=============================')
        print(lines2)
        


    count = 0


    items = list(num2txt.items())

    for num, (f1, f2) in items:
        vi1, en1 = test_vi(f1), test_en(f1)
        vi2, en2 = test_vi(f2), test_en(f2)

        check1 = vi1 != en1  # a = b + c  ....    a = plus(b, c)
        check2 = vi2 != en2  # a = b == c ....   a = equal(b, c)
        check3 = vi1 == en2
        check4 = vi2 == en1

        if not (check1 and check2 and check3 and check4):
            # os.system('code '+f1)
            # os.system('code '+f2)
            # show(f1, f2)
            # input()
            count += 1
            num2txt_fail[num] = (f1, f2)
            num2txt.pop(num)
            print(f1, f2)

    print(len(num2txt_fail))
    print(len(num2txt))

    for num, fs in num2txt_fail.items():
        for f in fs:
            os.system('cp {} fail'.format(f))
            os.system('rm {}'.format(f))

# def test_vi(f):
#         with open(f, 'r') as fi:
#             lines = fi.readlines()
#         return any([' và ' in line for line in lines])


# def test_en(f):
#     with open(f, 'r') as fi:
#         lines = fi.readlines()
#     return any([' and ' in line for line in lines])

# num2txt = get_num2txt(glob.glob('fix/*'))
# items = list(num2txt.items())
# print(len(items))
# # print(items[:10])
# count = 10381


# work_dir = os.path.join(os.getcwd(), 'pass')
# files = os.listdir(work_dir)
# files.sort()
# # print(len(files))
# for f in tqdm(files):
#     f = os.path.join(work_dir, f)
#     # fix_files(f)
#     print(f)
# old_dir = os.path.join(crd, 'pass')
# for num in range(10382, 10433):
#     newenf = os.path.join(crd, 'pass', "{}_en.txt".format(num))
#     newvif = os.path.join(crd, 'pass', "{}_vi.txt".format(num))
#     print(os.path.exists(newenf))
#     print(os.path.exists(newvif))
#     input()
    # os.system('mv {} {}'.format(newenf))
    # os.system('mv {} {}'.format(newvif))



#in fix/ ; 20_854 ~ 10_427 pairs



#################
# 
# !mv $crd/10428.vi.txt $crd/10428_vi.txt
# !mv $crd/10429.en.txt $crd/10429_en.txt
# !mv $crd/10429.v.txt 10429_vi.txt
# !mv $crd/10430.en.txt 10430_en.txt
# !mv $crd/10430.vi.txt 10430_vi.txt
# !mv $crd/10431.en.txt 10431_en.txt
# !mv $crd/10431.vi.txt 10431_vi.txt
# !mv $crd/10432.en.txt 10432_en.txt
# !mv $crd/10432.vi.txt 10432_vi.txt
