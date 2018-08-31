#!/usr/bin/env bash
TREETOOLS=~/treetools  # Path where treetools is installed
VOCAB_SIZE=10000
MARKOV=false

set -x  # echo on

mkdir -p data train dev test

# Optionally, get trees from the benepar.
if [[ ! -e data/train.trees ]]; then
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/02-21.10way.clean \
        -P data/train.trees
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/22.auto.clean \
        -P data/dev.trees
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/23.auto.clean \
        -P data/test.trees
fi

# Get terminals from train, dev and test sets.
$TREETOOLS/treetools transform data/train.clean train.tokens \
    --src-format brackets --dest-format terminals
$TREETOOLS/treetools transform data/dev.clean dev.tokens \
    --src-format brackets --dest-format terminals
$TREETOOLS/treetools transform data/test.clean test.tokens \
    --src-format brackets --dest-format terminals

# For preprocessing of train-set: gather substitutions (lowercase, <unk>, and <num>).
python get-lex-sub.py train.tokens $VOCAB_SIZE > train.subs

# Let treetools apply the substitutions to the train set.
$TREETOOLS/treetools transform data/train.clean train.processed \
    --trans substitute_terminals --params terminalfile:train.subs \
    --src-format brackets --dest-format brackets

# Treetools messes with the spacing...
./add-space.py train.processed

# Use nltk to convert trees to CNF with optional Markovivization.
if [ $MARKOV = true ]; then
    echo Markovize the grammar: v1:h1
    ./nltk-cnf.py train/train.processed train/train.markov.processed --markov 1:1 --collapse-unaries

    NAME=train.markov
else
    ./nltk-cnf.py train/train.processed train/train.processed --collapse-unaries

    NAME=train
fi

# Get rules from grammar
$TREETOOLS/treetools grammar train/$NAME.processed train/$NAME \
    leftright --src-format brackets --dest-format lopar

# Process the grammar output to our own format.
./custom-format.py train/$NAME.gram train/$NAME.lex > train/$NAME.grammar


# Cleanup.
rm train.subs
mv $NAME.processed train.tokens vocab.json train
mv dev.tokens dev
mv test.tokens test
