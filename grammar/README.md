# Grammar
To obtain a grammar, run `./get-grammar.sh`. The script does the following:
1. Processes the training trees:
  * Lowercase all words.
  * Replace all numbers with `<num>`.
  * Replace with `<unk>` everything beyond a certain threshold (default vocab size is 10k).
2. Obtain a binarized grammar in CNF from the training set in `lopar` format.
3. Rewrite the `lopar` format to a custom format.

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
