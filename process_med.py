

import glob
import re
import tqdm

tapchi = glob.glob('medic_txt/tapchi_Y-duoc/*.txt')
tonghoi = glob.glob('medic_txt/tonghoiyhoc_txt/*.txt')
all_txt = tapchi + tonghoi


def get_key(lines):
    key = set()
    for l in lines:
        l = l.split(':')
        if len(l) > 1:
            k = l[0].split('. ')[-1].strip().lower()
            k = re.sub('\s+', ' ', k)
            if len(k.split()) >= 8 and len(k.split()) <= 10:
                key.add(k)
    return key

def save_key():
    all_keys = set()
    for txt in tapchi:
        with open(txt, 'r') as f:
            lines = f.readlines()
        all_keys.update(get_key(lines))

    for txt in tonghoi:
        with open(txt, 'r') as f:
            lines = f.readlines()
        all_keys.update(get_key(lines))

    all_keys = list(all_keys)
    all_keys.sort()


    with open('med_keys.8_10.txt', 'w') as f:
        for k in all_keys:
            print(k)
            f.write(k + '\n')
    print(len(all_keys))


def analyse():
    k = 'cơ sở nghiên cứu'
    k = 'background'
    k = 'tổng quan:'
    k = 'tóm tắt:'
    k = 'tóm tắt:'
    k = 'giới thiệu:'
    k = 'introduction and objectives:'
    k = 'introduction:'
    k = 'mở đầu:'
    k = 'hiệu quả:'
    k = 'overview:'
    k = 'kiến nghị:'
    k = 'khuyến nghị:'
    k = 'khái quát:'
    k = 'findings:'
    k = 'purpsose:'
    k = 'targets:'
    k = 'the primary research:'
    k = 'findings:'
    k = 'summary:'
    k = 'material:'
    k = 'patients and intervention:'
    k = 'patients had manifestations:'
    k = 'phương pháp và kết quả:'
    k = 'phương pháp và đối tượng nghiên cứu'

    for txt in tapchi:
        with open(txt, 'r') as f:
            content = f.read().lower()
        if k in content:
            print(content)
            input()

    for txt in tonghoi:
        with open(txt, 'r') as f:
            content = f.read().lower()
        if k in content:
            print(content)
            input()



def process_key():

    with open('med_keys.txt', 'r') as f:
        lines = f.readlines()

    abc = 'abcdefghijklmnopqrstvuwxyz -'

    en, vi = [], []
    for l in lines:
        l = l.strip()
        if any([char not in abc for char in l]):
            vi += [l]
        else:
            en += [l]

    with open('med_keys.envi.txt', 'w') as f:
        [f.write(l + '\n') for l in en]
        f.write('\n')
        [f.write(l + '\n') for l in vi]
    




def get_pairs_and_allkeys():
    with open('med_keys.envi.txt', 'r') as f:
        lines = f.readlines()

    groups = [[]]

    for l in lines:
        l = l.strip()
        if l and l == '-' * len(l):
            continue
        if l and l == '=' * len(l):
            break

        if l == '':
            if groups[-1] != []:
                groups += [[]]
        else:
            groups[-1] += [l]



    groups = groups[:-1]



    assert len(groups) % 2 == 0, len(groups)

    pairs = []
    for i in range(len(groups)//2):
        gen, gvi = groups[2*i], groups[2*i+1]
        pairs += [(gen, gvi)]

    all_keys = set()
    for gen, gvi in pairs:
        for k in gen:
            all_keys.add(k)
            if ' and ' in k:
                all_keys.add(k.replace(' and ', ' & '))
            if not k.startswith('- '):
                all_keys.add('- ' + k)
            else:
                all_keys.add(k[2:])
        for k in gvi:
            all_keys.add(k)
            if ' and ' in k:
                all_keys.add(k.replace(' and ', ' & '))
            if not k.startswith('- '):
                all_keys.add('- ' + k)
            else:
                all_keys.add(k[2:])

    return pairs, all_keys


def save_split():

    pairs, all_keys = get_pairs_and_allkeys()

    print(len(pairs))
    print(len(all_keys))

    for txt in tqdm.tqdm(tapchi + tonghoi):
        with open(txt, 'r') as f:
            lines = f.read()
        
        lines = re.sub('\s+', ' ', lines)

        segments = []
        last_i = 0
        for i in range(len(lines)):
            for k in all_keys:
                if lines[i: i+len(k)+1].lower() == k + ':':
                    if (i == 0 or 
                        lines[i-2:i] in ['. ', ': ', '\n '] or
                        lines[i-1] == '\n'):
                        segments += [lines[last_i:i]]
                        last_i = i
                        break
        
        if last_i < len(lines):
            segments += [lines[last_i:]]

        fname = txt.split('/')[-1]
        with open('medic_split/' + fname, 'w') as f:
            for s in segments:
                s = s.replace('\n', ' ')
                f.write(s.strip() + '\n')


def rm_postfix(l, s):
    if s in l[1:]:
        return s.split(l)[0]
    return l


import os

def pair_matching():
    pairs, all_keys = get_pairs_and_allkeys()

    allfiles = glob.glob('medic_split/*.txt')

    os.system('rm medical.en')
    os.system('rm medical.vi')

    fe, fv = open('medical.en', 'a'), open('medical.vi', 'a')

    for fname in tqdm.tqdm(allfiles):

        with open(fname, 'r') as f:
            lines = f.readlines()

        k2l = []

        for l in lines:
            for k in all_keys:
                if l.lower().startswith(k+':'):
                    k2l += [(k, l[len(k)+1:])]
                    break

        k2l_en, k2l_vi = [], []

        for k, l in k2l:
            for gen, gvi in pairs:
                if k in gen:
                    k2l_en += [(k, l)]
                    break
                elif k in gvi:
                    k2l_vi += [(k, l)]
                    break

        if len(k2l_en) == 0 or len(k2l_vi) == 0:
            continue

        k, l = k2l_vi[-1]
        if ' Abstract:' in l:
            ke = 'abstract'
            l, le = l.split(' Abstract:')
            k2l_vi[-1] = k, l
            k2l_en = [(ke, le)] + k2l_en
        elif ' SUMMARY' in l:
            ke = 'summary'
            l, le = l.split(' SUMMARY')
            k2l_vi[-1] = k, l
            k2l_en = [(ke, le)] + k2l_en

        sent_pairs = []

        for ke, le in k2l_en:
            gvi_match = set()
            for gen, gvi in pairs:
                if ke in gen:
                    gvi_match.update(gvi)

            for i, (kv, lv) in enumerate(k2l_vi):
                if kv in gvi_match:
                    sent_pairs += [(le, lv)]
                    k2l_vi = k2l_vi[i+1:]
                    break

        for le, lv in sent_pairs:
            le = le.replace('±', ' + - ').replace('≥', ' > = ')
            lv = lv.replace('±', ' + - ').replace('≥', ' > = ')

            lv = rm_postfix(lv, ' Tác giả: ')
            lv = rm_postfix(lv, 'Kết quả:')

            fe.write(le.strip() + '\n')
            fv.write(lv.strip() + '\n')
        #     print(le.strip())
        #     print(lv.strip())
        #     print('--------')
        # input()
    fe.flush()
    fv.flush()
    fe.close()
    fv.close()


pair_matching()



