#!/usr/bin/env python
import os
import argparse

import numpy as np
from nltk import tokenize, Tree

from parser import Parser
from predict import predict_from_trees, predict_from_file, predict_from_file_parallel
from util import cleanup_tree, evalb, show


def main(args):
    parser = Parser(args.grammar, args.expand_binaries)
    print(
        'Grammar:',
        'lex', parser.grammar.num_lex_rules,
        'unary', parser.grammar.num_unary_rules,
        'binary', parser.grammar.num_binary_rules
    )
    if args.infile:
        print(f'Predicting trees for `{args.infile}` to `{args.outfile}`...')
        if args.parallel:
            predict_from_file_parallel(parser, args.infile, args.outfile, args.num_lines)
        else:
            predict_from_file(parser, args.infile, args.outfile, args.num_lines)
        if args.show: show(args.outfile)
        print('Evaluation bracket score...')
        if args.goldfile:
            try:
                evalb(args.outfile, args.goldfile, args.result)
                if args.show: show(args.result)
            except:
                exit('Could note evaluate trees. Maybe you did not parse the entire file?')
        print('Finished.')
    elif args.treefile:
        num_trees = 10 if args.num_lines == -1 else args.num_lines
        fscores = []
        parses = predict_from_trees(parser, args.treefile)
        for i in range(num_trees):
            gold, pred, prec, rec, fscore = next(parses)
            print('*'*79)
            print(f'Tree {i}, f1={fscore:.3f}.')
            print('Gold:')
            gold.pretty_print()
            print('Pred:')
            pred.pretty_print()
            print()
            fscores.append(fscore)
        print('*'*79)
        print('All F1 =', ' '.join([f'{fscore:.3f}' for fscore in fscores]))
        print('Avg F1 = ', sum(fscores) / len(fscores))
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
        tree, score = trees[0]
        tree = cleanup_tree(tree)
        print(79*'*')
        print('Predicted.')
        print('logprob: ', score)
        tree.pretty_print()
        print(79*'*')
        if not args.sent:
            gold = Tree.fromstring(gold)
            prec, recall, fscore = parser.evalb(gold.pformat(margin=np.inf), tree.pformat(margin=np.inf))
            print('Gold.')
            gold.pretty_print()
            print(f'Precision = {prec:.3f}')
            print(f'Recall = {recall:.3f}')
            print(f'F1 = {fscore:.3f}')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--grammar', type=str, default='grammar/train/train.grammar')
    argparser.add_argument('--sent', type=str, default='')
    argparser.add_argument('--infile', type=str, default='')
    argparser.add_argument('--outfile', type=str, default='pred.trees')
    argparser.add_argument('--goldfile', type=str, default='')
    argparser.add_argument('--result', type=str, default='result.txt')
    argparser.add_argument('--treefile', type=str, default='')
    argparser.add_argument('--parallel', action='store_true')
    argparser.add_argument('-n', '--num-lines', type=int, default=10)
    argparser.add_argument('-s', '--show', action='store_true')
    argparser.add_argument('--expand-binaries', action='store_true')
    args = argparser.parse_args()

    main(args)
