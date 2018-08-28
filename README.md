# Chart parser
A simple chart parser with a cythonized CKY for speed.


To obtain the data and grammar, type:
```
cd grammar
./get-grammar.sh
```
To compile cky, type:
```
cd cky
python setup.py build_ext --inplace
```
To parse a sentence, type:
```
./main.py --sent "The horse raced past the barn fell."
```
To parse the dev-set, type:
```
./main.py --in-file grammar/dev/22.auto.tokens --out-file grammar/dev/22.auto.trees
```
