# Chart parser
A simple chart parser with a cythonized CKY for speed.


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
To parse a sentence, type:
```bash
./main.py --sent "The horse raced past the barn fell."
```
To parse the dev-set and compute f-score, type:
```bash
./main.py --in-file grammar/dev/dev.tokens --out-file grammar/dev/dev.pred.trees --gold grammar/dev/dev.trees
```
