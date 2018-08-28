#!/usr/bin/env bash
TREETOOLS=~/treetools
TRAIN=02-21.10way
DEV=22.auto
TEST=23.auto
VOCAB_SIZE=10000

set -x  # echo on

mkdir -p data train dev test

if [[ ! -e data/$TRAIN.clean ]]; then
    wget \
      https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/02-21.10way.clean -P data \
      https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/22.auto.clean -P data \
      https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/23.auto.clean -P data
fi

# Get terminals from train, dev and test sets.
$TREETOOLS/./treetools transform data/$TRAIN.clean $TRAIN.tokens \
    --src-format brackets --dest-format terminals
$TREETOOLS/./treetools transform data/$DEV.clean $DEV.tokens \
    --src-format brackets --dest-format terminals
$TREETOOLS/./treetools transform data/$TEST.clean $TEST.tokens \
    --src-format brackets --dest-format terminals

# For preprocessing of train-set: gather substitutions (lowercase, <unk>, and <num>).
python get-lex-sub.py $TRAIN.tokens $VOCAB_SIZE > $TRAIN.subs

# Let treetools apply the substitutions to the train set.
$TREETOOLS/./treetools transform data/$TRAIN.clean $TRAIN.processed \
    --trans substitute_terminals --params terminalfile:$TRAIN.subs \
    --src-format brackets --dest-format brackets

# Treetools messes with the spacing...
./add-space.py $TRAIN.processed

# Get a CNF grammar from the training set.
$TREETOOLS/./treetools grammar $TRAIN.processed train/train \
    leftright --src-format brackets --dest-format lopar

# Process the grammar output to our own format.
./custom-format.py train/train.gram train/train.lex > train/train.grammar

rm $TRAIN.subs
mv $TRAIN.processed $TRAIN.tokens vocab.json train
mv $DEV.tokens dev
mv $TEST.tokens test
