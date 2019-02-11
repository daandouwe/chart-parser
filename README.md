# Chart parser
A simple chart parser in python with a CKY in cython for speed.

Inspired by the recent success of [benepar](https://github.com/nikitakit/self-attentive-parser) and the [minimal-span parser](https://github.com/mitchellstern/minimal-span-parser) I wanted to revisit chart parsing with CKY on binarized trees. No neural networks here however, just rule probabilities estimated by maximum likelihood.

## Setup
To obtain the data and grammar, use:
```bash
cd grammar
./get-grammar.sh
```
To compile cky, use:
```bash
cd cky
python setup.py build_ext --inplace
```

## Usage
To run a quick test, use:
```bash
python main.py
```
To parse a sentence, use:
```bash
python main.py --sent "The horse raced past the barn fell."
```
To parse the dev-set and compute f-score, use:
```bash
python main.py --infile grammar/dev/dev.tokens --outfile grammar/dev/dev.pred.trees --goldfile grammar/data/dev.trees
```
This can be done in parallel by adding `--parallel`.

To parse 5 sentences from the dev-set, show predicted and gold parses, and compute their individual f-scores, use:
```bash
python main.py --treefile grammar/data/dev.trees -n 5
```

The default grammar used is the vanilla CNF. To use the (v1h1) Markovized grammar, use:
```bash
python main.py --grammar grammar/train/train.markov.grammar
```

## Speed
To speed up the CKY parsing, we use a (simple) [cythonized version](https://github.com/daandouwe/chart-parser/blob/master/cky/_cky.pyx) that is _almost_ a numpy implementation.
We also provide a [numpy cky](https://github.com/daandouwe/chart-parser/blob/master/cky/cky_numpy.py). To use this, add the flag `--use-numpy`.
The speed difference is very significant: the cython CKY parses a 20-word sentence in ~1 second, the numpy CKY takes ~90 seconds.

Parsing the entire development set in parallel with 8 processes (for my quad-core machine) takes around 15 minutes.

## Accuracy
The Markovized CNF gives these results on the development set:
```
=== Summary ===

-- All --
Number of sentence        =   1700
Number of Error sentence  =      0
Number of Skip  sentence  =      0
Number of Valid sentence  =   1700
Bracketing Recall         =  77.90
Bracketing Precision      =  76.39
Bracketing FMeasure       =  77.13
Complete match            =  14.35
Average crossing          =   2.32
No crossing               =  42.59
2 or less crossing        =  67.76
Tagging accuracy          =  93.62
```
The vanilla CNF gives these results:
```
=== Summary ===

-- All --
Number of sentence        =    200
Number of Error sentence  =      0
Number of Skip  sentence  =      0
Number of Valid sentence  =    200
Bracketing Recall         =  71.67
Bracketing Precision      =  69.66
Bracketing FMeasure       =  70.65
Complete match            =   9.00
Average crossing          =   3.12
No crossing               =  35.50
2 or less crossing        =  60.50
Tagging accuracy          =  91.35
```
This is what we should expect based on the numbers that [Klein and Manning (2003)](https://nlp.stanford.edu/manning/papers/unlexicalized-parsing.pdf) report on the unrefined and Markovized grammars.

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
- [X] More elaborate unking scheme (e.g. `UNK-DASH-ity`)
- [ ] Write a `setup.py` to make collaboration easier. See [this example](https://github.com/kmkurn/pytorch-rnng/blob/master/setup.py).
- [ ] Add tests. See [this example](https://github.com/kmkurn/pytorch-rnng/tree/master/tests).
