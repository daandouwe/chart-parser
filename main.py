#!/usr/bin/env python
import argparse
import pickle
from collections import defaultdict

import numpy as np
from nltk import tokenize
import multiprocessing as mp
from tqdm import tqdm
from PYEVALB import scorer

from parser import Parser
from util import unbinarize


def predict(parser, in_path):
    with open(in_path) as fin:
        lines = fin.readlines()
        sentences = [tokenize.word_tokenize(line.strip()) for line in lines]
    predicted = []
    for sentence in sentences:
        trees = parser(sentence, verbose=False)
        if not trees:
            predicted.append('')  # TODO: why empty trees?
        else:
            tree, _ = trees[0]
            tree = tree.pformat(margin=np.inf)
            predicted.append(tree)
    with open(args.outfile, 'w') as fout:
        print('\n'.join(trees), file=fout)


def predict_parallel(parser, in_path, size=8):
    print(f'Predicting parallel with {size} processes...')

    def worker(parser, sentences, rank, return_dict):
        predicted = []
        if rank == 0:
            sentences = tqdm(sentences)
        for sentence in sentences:
            trees = parser(sentence, verbose=False)
            if not trees:
                predicted.append('')  # TODO: why empty trees?
            else:
                tree, _ = trees[0]
                tree = tree.pformat(margin=np.inf)
                predicted.append(tree)
        return_dict[rank] = predicted

    # Read sentences and partition them to be distributed among processes.
    with open(in_path) as fin:
        lines = fin.readlines()
        sentences = [tokenize.word_tokenize(line.strip()) for line in lines]
    chunk_size = len(sentences) // size
    partitioned = [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]
    # Spawn processes.
    manager = mp.Manager()
    return_dict = manager.dict()
    processes = []
    for rank in range(size):
        p = mp.Process(target=worker, args=(parser, partitioned[rank], rank, return_dict))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    trees = sum([return_dict[rank] for rank in range(size)], [])
    with open(args.outfile, 'w') as fout:
        print('\n'.join(trees), file=fout)


def evalb(pred_path, gold_path, result_path):
    tree_scorer = scorer.Scorer()
    tree_scorer.evalb(gold_path, pred_path, result_path)


def main(args):
    parser = Parser(args.grammar, args.expand_binaries)
    if args.infile:
        print(f'Predicting trees for lines in {args.infile}')
        # predict(parser, args.infile)
        predict_parallel(parser, args.infile)
        if args.gold:
            evalb(args.outfile, args.gold)
        print('Finished.')
    else:
        if args.sent:
            sentence = tokenize.word_tokenize(args.sent)
        else:
            sentence = 'The horse walked past the barn fell .'.split()
        print('Parsing sentence..')
        trees = parser(sentence)
        for tree, score in reversed(trees[:10]):
            print('prob: ', score)
            tree.pretty_print()
            unbinarize(tree).pretty_print()
            print(79*'-')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--grammar', type=str, default='grammar/train/train.grammar')
    argparser.add_argument('--sent', type=str, default='')
    argparser.add_argument('--infile', type=str, default='')
    argparser.add_argument('--outfile', type=str, default='pred.trees')
    argparser.add_argument('--gold', type=str, default='')
    argparser.add_argument('--expand-binaries', action='store_true')
    args = argparser.parse_args()

    main(args)
