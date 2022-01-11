## Collect data for Vietnamese-English Neural Machine Translation.

We have access to Vietnamese and English bilingual documents **without** paragraph level alignment. By making use of translation models in vietai/dab, we provide a weak alignment signal for a dynamic programming pair-matching algorithm and output large number of new training data (>90% of sentences are matched).

We tested and show that the method provides ~99% precision, compare to much worse pair matching using greedy/beam search algorithms.


### Algorithm

```
# Input: English document, Vietnamese document

# Output: Pairs of sentences, each includes an english sentence and a vietnamese sentence with closed meaning.

```

### Results 
This data set is used to train [this State-of-the-art](https://blog.vietai.org/sat/) Machine Translation model for English-Vietnamese.

### Acknowledgement

Special thanks to Trieu H. Trinh (thtrieu@) for guidance on this project.

