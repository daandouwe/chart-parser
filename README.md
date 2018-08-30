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
To run a quick test, run:
```bash
./main.py
```
To parse a sentence, type:
```bash
./main.py --sent "The horse raced past the barn fell."
```
To parse the dev-set and compute f-score, type:
```bash
./main.py --infile grammar/dev/dev.tokens --outfile grammar/dev/dev.pred.trees --goldfile grammar/dev/dev.trees
```
Optionally, this can be done in parallel by adding `--parallel`.
To parse 5 sentences from the dev-set, show predicted and gold parses, and compute their individual f-scores, type:
```bash
./main.py --treefile grammar/data/dev.trees -n 5
```

## Requirements
```
numpy
cython
nltk
tqdm
PYEVALB
```
