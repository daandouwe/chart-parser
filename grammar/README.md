# Grammar
To obtain a grammar, run `./get-grammar.sh`. The script does the following:
* Download the ptb trees from [benepar](https://github.com/nikitakit/self-attentive-parser/tree/master/data) if you don't have them yet.
* Download [EVALB](https://nlp.cs.nyu.edu/evalb/), which is used to score predicted trees.
* Download [treetools](https://nlp.cs.nyu.edu/evalb/), which is used to extract the grammar.
* Processes the training trees:
  * Lowercase all words.
  * Replace all numbers with `<num>`.
  * Replace with `<unk>` everything beyond a certain threshold (default vocab size is 10k).
* Obtain a binarized grammar in CNF from the training set in `lopar` format using `treetools`.
* Two types of grammars are extracted: a vanilla CNF grammar, and a v1:h1 Markovized CNF grammar (see [Klein and Manning 2003](http://delivery.acm.org/10.1145/1080000/1075150/p423-klein.pdf?ip=89.99.242.224&id=1075150&acc=OPEN&key=4D4702B0C3E38B35%2E4D4702B0C3E38B35%2E4D4702B0C3E38B35%2E6D218144511F3437&__acm__=1535987878_fdb08a617541f60b68baf3aff0d6ad99)).
* Rewrite the `lopar` format to a custom format.

The final grammar is stored in `grammar/train/train.grammar` and has the following format:
```
PP RB ADJP 8.448264937588443e-05
WHPP TO WHNP 0.04603580562659847
X DT 0.022988505747126436
JJR [lesser] 0.002657218777679362
NN [air-freight] 7.534545892919034e-06
NN [air-traffic] 3.767272946459517e-05
```
