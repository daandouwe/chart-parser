#!/usr/bin/env bash
MIN_COUNT=2

HOR_MARKOV=1
VERT_MARKOV=1

MARKOV="v${VERT_MARKOV}h${HOR_MARKOV}"


mkdir -p data train dev test


# Get trees from the benepar if needed.
if [[ ! -e data/train.trees ]]; then
    echo 'Downloading tree data.'
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/02-21.10way.clean \
        -P data/train.trees
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/22.auto.clean \
        -P data/dev.trees
    wget https://raw.githubusercontent.com/nikitakit/self-attentive-parser/master/data/23.auto.clean \
        -P data/test.trees
fi


# Get EVALB if needed.
if [[ ! -d ../EVALB ]]; then
    echo 'Downloading EVALB.'
    cd ..  # Install EVALB in main directory.
    wget https://nlp.cs.nyu.edu/evalb/EVALB.tgz
    tar -xzf EVALB.tgz
    rm EVALB.tgz
    cd EVALB
    sed -i -e 's/#include <malloc.h>/\/* #include <malloc.h> *\//g' evalb.c  # Remove <malloc.h> include.
    make
    cd ../grammar  # Return to the folder grammar for the rest of the processing.
fi


# Get treetools if needed.
if [[ ! -d treetools ]]; then
    echo 'Downloading treetools.'
    git clone https://github.com/wmaier/treetools.git
    cd treetools
    # Edit code to not print all the substitutions to terminal!
    sed -i -e \
        's/print(substitute_terminals.terminals)/# print(substitute_terminals.terminals)/g' \
        trees/transform.py
    python setup.py install --user
    cd ..
fi


# Get terminals from train, dev and test sets.
echo 'Exracting tokens from trees.'
treetools/treetools transform data/train.trees train.tokens \
    --src-format brackets --dest-format terminals

treetools/treetools transform data/dev.trees dev.tokens \
    --src-format brackets --dest-format terminals

treetools/treetools transform data/test.trees test.tokens \
    --src-format brackets --dest-format terminals


# For preprocessing of train-set: gather substitutions.
python get-lex-sub.py train.tokens $MIN_COUNT > train.subs


# Let treetools apply the substitutions to the train set.
echo 'Pre-processing tokens of trees.'
treetools/treetools transform data/train.trees train.processed \
    --trans substitute_terminals --params terminalfile:train.subs \
    --src-format brackets --dest-format brackets


# Treetools messes with the spacing...
python add-space.py train.processed


# Use nltk to convert trees to two types of CNF: vanilla and markovized.
echo 'Making vanilla CNF trees.'
python make-cnf.py train.processed train/train.vanilla.processed --collapse-unaries

echo "Making Markov CNF trees (${MARKOV})."
python make-cnf.py train.processed train/train.markov.${MARKOV}.processed --collapse-unaries --markov ${VERT_MARKOV}:${HOR_MARKOV}

for name in train.vanilla train.markov.${MARKOV}; do
    echo 'Extracting grammar from' $name

    # Get rules from grammar
    treetools/treetools grammar train/$name.processed train/$name \
        leftright --src-format brackets --dest-format lopar

    # Process the grammar output to our own format.
    python custom-format.py train/$name.gram train/$name.lex > train/$name.grammar
done


# Cleanup.
rm train.subs
mv train.tokens vocab.json train
mv dev.tokens dev
mv test.tokens test
