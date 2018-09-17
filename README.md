# Chart parser
A simple chart parser with a cythonized CKY for speed.

Inspired by the recent success of [benepar](https://github.com/nikitakit/self-attentive-parser) I wanted to revisit simple CKY for binarized trees.
No neural networks here however, just MLE estimated rule probabilities.

## Setup
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

## Usage
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

The default grammar used is the vanilla CNF. To use the Markovized grammar, type:
```bash
./main.py --grammar grammar/train/train.markov.grammar
```

## Speed
To speed up the CKY parsing, we use a (simple) [cythonized version](https://github.com/daandouwe/chart-parser/blob/master/cky/_cky.pyx) that is _almost_ a numpy implementation.
We also provide a [numpy cky](https://github.com/daandouwe/chart-parser/blob/master/cky/cky_numpy.py). To use this, add the flag `--use-numpy`.
The speed difference is very significant: the cython CKY parses a 20-word sentence in ~1 second, the numpy CKY takes ~90 seconds.

Parsing the entire development set in parallel with 8 processes (for my quad-core machine) takes around 15 minutes.

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
The accuracy is much lower than what we should expect from this method based on [Klein and Manning 2003](https://nlp.stanford.edu/manning/papers/unlexicalized-parsing.pdf). Is there something awry?

## Requirements
```
python>=3.6.0
numpy
cython
nltk
tqdm
flake8
PYEVALB
```

## Contributing
Working to make collaboration easier.
### Run tests
```
Under construction
```
### Run linters
Run `flake8` from the project directory for style guide enforcement. See the [documentaion](http://flake8.pycqa.org/en/latest/) for more info on flake8.

## TODO
- [ ] Quite a number of test-sentences are not recognized, causing empty parses. Why?
- [ ] Write a `setup.py` to make collaboration easier. See [this example](https://github.com/kmkurn/pytorch-rnng/blob/master/setup.py).
- [ ] Add tests. See [this example](https://github.com/kmkurn/pytorch-rnng/tree/master/tests).
