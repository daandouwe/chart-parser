#!/usr/bin/env python
import argparse
import pickle
from collections import defaultdict

import numpy as np
from nltk import tokenize, Tree
import multiprocessing as mp
from tqdm import tqdm

from parser import Parser
from util import TOP, unbinarize, cleanup_tree, evalb


def predict_from_trees(parser, infile):
    with open(infile) as fin:
        trees = [Tree.fromstring(line) for line in fin.readlines()]
    for gold in trees:
        trees = parser(gold.leaves(), verbose=False)
        if not trees:
            yield 0, 0, 0
        else:
            pred, score = trees[0]
            tree = cleanup_tree(pred)
            gold, pred = gold.pformat(margin=np.inf), pred.pformat(margin=np.inf)
            prec, recall, fscore = parser.evalb(gold, pred)
            yield prec, recall, fscore


def predict_from_file(parser, infile, outfile, size=8):
    print(f'Predicting in parallel with {size} processes...')

    def worker(parser, sentences, rank, return_dict):
        predicted = []
        if rank == 0:
            sentences = tqdm(sentences)
        for sentence in sentences:
            trees = parser(sentence, verbose=False)
            if not trees:
                predicted.append('')  # TODO: why empty trees?
                print('Oops, no tree!')
            else:
                tree, score = trees[0]
                tree = cleanup_tree(tree)
                tree = tree.pformat(margin=np.inf)
                predicted.append(tree)
        return_dict[rank] = predicted

    # Read sentences and partition them to be distributed among processes.
    with open(infile) as fin:
        sentences = [tokenize.word_tokenize(line.strip()) for line in fin.readlines()]
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
    with open(outfile, 'w') as fout:
        print('\n'.join(trees), file=fout)


def main(args):
    parser = Parser(args.grammar, args.expand_binaries)
    print(
        'Grarmmar:',
        'lex', parser.grammar.num_lex_rules,
        'unary', parser.grammar.num_unary_rules,
        'binary', parser.grammar.num_binary_rules
    )
    if args.infile:
        print(f'Predicting trees for lines in `{args.infile}` and to `{args.outfile}`...')
        predict_from_file(parser, args.infile, args.outfile)
        if args.gold:
            evalb(args.outfile, args.gold)
        print('Finished.')
    elif args.treefile:
        num_trees = 20
        fscores = []
        parses = predict_from_trees(parser, args.treefile)
        for _ in range(num_trees):
            prec, rec, fscore = next(parses)
            fscores.append(fscore)
            print(f'F1 =', ' '.join([f'{fscore:.3f}' for fscore in fscores]), end='\r')
        print()
        print('Average F1 = ', sum(fscores) / len(fscores))
    else:
        if args.sent:
            sentence = tokenize.word_tokenize(args.sent)
        else:
            sent = 'The bill intends to restrict the RTC to Treasury borrowings only , ' + \
                   'unless the agency receives specific congressional authorization .'
            sentence = sent.split()
            gold = '(TOP (S (NP (DT The) (NN bill)) (VP (VBZ intends) (S (VP (TO to) (VP ' + \
                   '(VB restrict) (NP (DT the) (NNP RTC)) (PP (TO to) (NP (NNP Treasury) ' + \
                   '(NNS borrowings) (RB only)))))) (, ,) (SBAR (IN unless) (S (NP (DT the) ' + \
                   '(NN agency)) (VP (VBZ receives) (NP (JJ specific) (JJ congressional) ' + \
                   '(NN authorization)))))) (. .)))'
        print('Parsing sentence...')
        trees = parser(sentence)
        for tree, score in reversed(trees[:2]):
            print('Predicted.')
            print('logprob: ', score)
            tree = cleanup_tree(tree)
            tree.pretty_print()
            print(79*'*')
        if not args.sent:
            print('Gold.')
            gold = Tree.fromstring(gold)
            gold.pretty_print()
            prec, recall, fscore = parser.evalb(gold.pformat(margin=np.inf), tree.pformat(margin=np.inf))
            print(f'Precision = {prec:.3f}')
            print(f'Recall = {recall:.3f}')
            print(f'F1 = {fscore:.3f}')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--grammar', type=str, default='grammar/train/train.grammar')
    argparser.add_argument('--sent', type=str, default='')
    argparser.add_argument('--infile', type=str, default='')
    argparser.add_argument('--outfile', type=str, default='pred.trees')
    argparser.add_argument('--gold', type=str, default='')
    argparser.add_argument('--treefile', type=str, default='')
    argparser.add_argument('--expand-binaries', action='store_true')
    args = argparser.parse_args()

    main(args)
