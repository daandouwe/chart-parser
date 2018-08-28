# Chart parser
A simple chart parser with a cythonized CKY for speed.

To obtain the grammar, type:
```
grammar/./get-grammar.sh
```
To parse a sentence, type:
```
./main.py --sent "The horse raced past the barn fell."
```
To parse the dev-set, type:
```
./main.py --in-file grammar/dev/22.auto.tokens --out-file grammar/dev/22.auto.trees
```
