# Grammar
To obtain a grammar, run `./get-grammar.sh`. The script does the following:
1. Download the ptb trees from [benepar](https://github.com/nikitakit/self-attentive-parser/tree/master/data) if you don't have them yet.
2. Processes the training trees:
  1. Lowercase all words.
  2. Replace all numbers with `<num>`.
  3. Replace with `<unk>` everything beyond a certain threshold (default vocab size is 10k).
3. Obtain a binarized grammar in CNF from the training set in `lopar` format.
4. Rewrite the `lopar` format to a custom format.

# Grammar format
We produce a grammar in the format:
```
PP RB ADJP 8.448264937588443e-05
WHPP TO WHNP 0.04603580562659847
X DT 0.022988505747126436
JJR [lesser] 0.002657218777679362
NN [air-freight] 7.534545892919034e-06
NN [air-traffic] 3.767272946459517e-05
```
