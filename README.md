## Collect data for Vietnamese-English Neural Machine Translation.

We have access to Vietnamese and English bilingual books **without** paragraph level alignment. By making use of translation models in vietai/dab, we provide a weak alignment signal for a dynamic programming pair-matching algorithm and output large number of new training data (>90% of sentences are matched).

We tested and show that the method provides ~99% precision, compare to much worse pair matching using greedy/beam search algorithms.


### Algorithm

``` python
# Input: English book (M lines), Vietnamese book (N lines)

# First translate the two books to the other language.
en2vi_book = vietai_dab_translate_envi(english_book)
vi2en_book = vietai_dab_translate_vien(vietnamese_book)
## Collect data for Vietnamese-English Neural Machine Translation.

We have access to Vietnamese and English bilingual books **without** paragraph level alignment. By making use of translation models in vietai/dab, we provide a weak alignment signal for a dynamic programming pair-matching algorithm and output large number of new training data (>90% of sentences are matched).

We tested and show that the method provides ~99% precision, compare to much worse pair matching using greedy/beam search algorithms.


### Algorithm

``` python
# Input: English book (M lines), Vietnamese book (N lines)

# First translate the two books to the other language.
en2vi_book = vietai_dab_translate_envi(english_book)
vi2en_book = vietai_dab_translate_vien(vietnamese_book)

# Next compute M x N BLEU scores:
M = len(en2vi_book)
N = len(vi2en_book)
bleu_score = np.zero((M, N))

for en_line, en2vi_line in zip(english_book, en2vi_book):
  for vi_line, vi2en_line in zip(vietnamese_book, vi2en_book):

    bleu_score[m, n] = bleu(en_line, vi2en_line) + bleu(vi_line, en2vi_line)

# Dynamic Programming for pair matching:
# F[m, n] is sum of bleu scores of all pairs in the best matching between en_book[:m] and vi_book[:n], then:
# F[m, n] = max(F[m-1, n-1] + bleu_score[m, n], 
#               F[m-1, n], 
#               F[m, n-1])
```

### Results

TODO(ntkchinh): add more results here.

# Next compute M x N BLEU scores:
M = len(en2vi_book)
N = len(vi2en_book)
bleu_score = np.zero((M, N))

for en_line, en2vi_line in zip(english_book, en2vi_book):
  for vi_line, vi2en_line in zip(vietnamese_book, vi2en_book):

    bleu_score[m, n] = bleu(en_line, vi2en_line) + bleu(vi_line, en2vi_line)

# Dynamic Programming for pair matching:
# F[m, n] is sum of bleu scores of all pairs in the best matching between en_book[:m] and vi_book[:n], then:
# F[m, n] = max(F[m-1, n-1] + bleu_score[m, n], 
#               F[m-1, n], 
#               F[m, n-1])
```

### Results

TODO(ntkchinh): add more results here.


### Acknowledgement

Special thanks to Trieu H. Trinh (thtrieu@) for guidance on this project. 