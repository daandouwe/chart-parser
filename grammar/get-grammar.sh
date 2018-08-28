#!/usr/bin/env bash
TREETOOLS=~/treetools
VOCAB_SIZE=10000

set -x  # echo on

mkdir -p data train dev test

if [[ ! -e data/train.trees ]]; then
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/02-21.10way.clean \
        -P data/train.trees
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/22.auto.clean \
        -P data/dev.trees
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/23.auto.clean \
        -P data/test.trees
fi

# Get terminals from train, dev and test sets.
$TREETOOLS/./treetools transform data/train.clean train.tokens \
    --src-format brackets --dest-format terminals
$TREETOOLS/./treetools transform data/dev.clean dev.tokens \
    --src-format brackets --dest-format terminals
$TREETOOLS/./treetools transform data/test.clean test.tokens \
    --src-format brackets --dest-format terminals

# For preprocessing of train-set: gather substitutions (lowercase, <unk>, and <num>).
python get-lex-sub.py train.tokens $VOCAB_SIZE > train.subs

# Let treetools apply the substitutions to the train set.
$TREETOOLS/./treetools transform data/train.clean train.processed \
    --trans substitute_terminals --params terminalfile:train.subs \
    --src-format brackets --dest-format brackets

# Treetools messes with the spacing...
./add-space.py train.processed

# Get a CNF grammar from the training set.
$TREETOOLS/./treetools grammar train.processed train/train \
    leftright --src-format brackets --dest-format lopar

# Process the grammar output to our own format.
./custom-format.py train/train.gram train/train.lex > train/train.grammar

# Cleanup.
rm train.subs
mv train.processed train.tokens vocab.json train
mv dev.tokens dev
mv test.tokens test
