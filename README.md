## Collect data for Vietnamese-English Neural Machine Translation.

We have access to Vietnamese and English bilingual documents **without** paragraph level alignment. By making use of translation models in vietai/dab, we provide a weak alignment signal for a dynamic programming pair-matching algorithm and output large number of new training data (>90% of sentences are matched).

We tested and show that the method provides ~99% precision, compare to much worse pair matching using greedy/beam search algorithms.


### Algorithm

```
# Input: English document, Vietnamese document

# Output: Pairs of sentences, each includes an english sentence and a vietnamese sentence with closed meaning.

```

### Results 
Translate from English to Vietnamese

<table align="center">
<thead>
<tr>
<th></th>
<th>BLEU score</th>
<!-- <th>Vietnamese to English</th> -->
<th>With extra training data</th>
</tr>
</thead>

<tbody>
<tr>
<td>This project</td>
<td>37.60</td>
<!-- <td></td> -->
<td>yes</td>
</tr>

<tr>
<td>Google translate</td>
<td>37.06</td>
<!-- <td></td> -->
<td>yes</td>
</tr>

<tr>
<td>Transformer+BPE-dropout</td>
<td>33.27</td>
<!-- <td></td> -->
<td>no</td>
</tr>

<tr>
<td>Transformer+BPE+FixNorm+ScaleNorm</td>
<td>32.8</td>
<!-- <td></td> -->
<td>no</td>
</tr>

<tr>
<td>Transformer+LayerNorm-simple</td>
<td>31.4</td>
<!-- <td></td> -->
<td>no</td>
</tr>

<tr>
<td>CVT</td>
<td>29.6</td>
<!-- <td></td> -->
<td>yes</td>
</tr>

</tbody>
</table>

### Acknowledgement

Special thanks to Trieu H. Trinh (thtrieu@) for guidance on this project.

