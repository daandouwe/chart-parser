#!/usr/bin/env bash
TREETOOLS=~/treetools
VOCAB_SIZE=10000

set -x  # echo on

./nltk-cnf.py train/train.processed train/train.markov.processed --markov 1:1 --collapse-unaries

# Get a CNF grammar from the training set.
$TREETOOLS/./treetools grammar train/train.markov.processed train/train.markov \
    leftright --src-format brackets --dest-format lopar

# Process the grammar output to our own format.
./custom-format.py train/train.markov.gram train/train.markov.lex > train/train.markov.grammar
