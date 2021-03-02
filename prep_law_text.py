import os
import glob
import pathlib

files = glob.glob('law_texts/*')


# files.sort(key=lambda x:
#         pathlib.Path(x).stat().st_ctime
# )

files.sort()

count = 0

f0 = None
f1 = None

pairs = []
skip = []


while files:

    if f0 is None:
        f0 = files.pop()
    if f1 is None:
        f1 = files.pop()

    if f0.split('_m_')[0] == f1.split('_m_')[0]:
        count += 1

        print(count, f0, f1)
        # input()
        pairs.append((f0, f1))
        f0, f1 = None, None
    else:
        print('skip ', f0)
        skip.append(f0)
        f0 = f1
        f1 = None

print('{} pairs'.format(len(pairs)))
print('{} skips'.format(len(skip)))


import tqdm

count = 0
for f1, f2 in tqdm.tqdm(pairs):
    count += 1
    name = 'pair.{:05d}'.format(count)
    os.system('cp {} law_pairs/{}.f1.doc'.format(f1, name))
    os.system('cp {} law_pairs/{}.f2.doc'.format(f2, name))
