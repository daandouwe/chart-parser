# Chart parser
A simple chart parser with a cythonized CKY for speed.

Inspired by the recent success of [benepar](https://github.com/nikitakit/self-attentive-parser) I wanted to revisit simple CKY for binarized trees.
No neural networks here however, just MLE estimated rule probabilities.

## Usage
To obtain the data and grammar, type:
```bash
cd grammar
./get-grammar.sh
```
To compile cky, type:
```bash
cd cky
python setup.py build_ext --inplace
```
To run a quick test, type:
```bash
./main.py
```
To parse a sentence, type:
```bash
./main.py --sent "The horse raced past the barn fell."
```
To parse the dev-set and compute f-score, type:
```bash
./main.py --infile grammar/dev/dev.tokens --outfile grammar/dev/dev.pred.trees --goldfile grammar/data/dev/dev.trees
```
Optionally, this can be done in parallel by adding `--parallel`.

To parse 5 sentences from the dev-set, show predicted and gold parses, and compute their individual f-scores, type:
```bash
./main.py --treefile grammar/data/dev.trees -n 5
```

## Speed
To speed up the CKY parsing, we use a (simple) cythonized version that is _almost_ a numpy implementation. We also provide a numpy cky. To use this, add the flag `--use-numpy`.
The speed difference is very significant: the cython CKY parses a 20-word sentence in ~1 second, the numpy CKY takes ~90 seconds.

## Accuracy
The Markovized CNF on the development set:
```
Number of sentence        =   1697
Number of Error sentence  =     80
Number of Skip  sentence  =      0
Number of Valid sentence  =   1617
Bracketing Recall         =  55.25
Bracketing Precision      =  49.66
Bracketing FMeasure       =  52.31
Complete match            =   2.78
Average crossing          =   4.28
No crossing               =  20.35
2 or less crossing        =  42.36
Tagging accuracy          =  90.98
```
The accuracy is much lower than what we should expect from this method based on [Klein and Manning 2003](http://delivery.acm.org/10.1145/1080000/1075150/p423-klein.pdf?ip=89.99.242.224&id=1075150&acc=OPEN&key=4D4702B0C3E38B35%2E4D4702B0C3E38B35%2E4D4702B0C3E38B35%2E6D218144511F3437&__acm__=1535987878_fdb08a617541f60b68baf3aff0d6ad99). Is there something awry?

## Requirements
```
numpy
cython
nltk
tqdm
PYEVALB
```

## TODO
- [ ] Quite a number of test-sentences are not recognized, causing empty parses. Why?
