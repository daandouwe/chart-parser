#!/usr/bin/env python
import os
import argparse
import time

import numpy as np
from nltk import tokenize, Tree

from parser import Parser
from predict import predict_from_trees, predict_from_file, predict_from_file_parallel
from evaluate import evalb
from syneval import syneval
from utils import show, SENT, GOLD


def main(args):

    parser = Parser(args.grammar, args.expand_binaries)
    print(
        'Grammar rules:',
        f'{parser.grammar.num_lexical_rules:,} lexical,',
        f'{parser.grammar.num_unary_rules:,} unary,',
        f'{parser.grammar.num_binary_rules:,} binary.'
    )

    if args.infile:

        print(f'Predicting trees for tokens in `{args.infile}`.')
        print(f'Writing trees to file `{args.outfile}`...')

        if args.parallel:
            trees = predict_from_file_parallel(
                parser, args.infile, args.num_lines, args.tokenize)
        else:
            trees = predict_from_file(
                parser, args.infile, args.num_lines, args.tokenize)

        with open(args.outfile, 'w') as fout:
            print('\n'.join(trees), file=fout)

        if args.show:
            show(args.outfile)

        print('Evaluating bracket score...')
        if args.goldfile:
            try:
                evalb(args.evalb_dir, args.outfile, args.goldfile, args.result, args.ignore_empty)
                if args.show:
                    show(args.result)
            except:
                exit('Could not evaluate trees. Maybe you did not parse the entire file?')

        print(f'Finished. Results saved to `{args.result}`.')

    elif args.treefile:
        num_trees = 10 if args.num_lines == None else args.num_lines

        parses = predict_from_trees(parser, args.treefile)

        fscores = []
        for i in range(num_trees):
            gold, pred, prec, rec, fscore = next(parses)
            fscores.append(fscore)

            print(f'Tree {i}, f1={fscore:.3f}.')
            print()
            print('Gold:')
            gold.pretty_print()
            print()
            print('Pred:')
            pred.pretty_print()
            print()

        print()
        print('All F1 =', ' '.join([f'{fscore:.3f}' for fscore in fscores]))
        print('Avg F1 = ', sum(fscores) / len(fscores))

    elif args.syneval:
        syneval(parser, args.syneval, args.outfile, parallel=args.parallel, short=args.short)

    else:
        if args.sent:
            sentence = tokenize.word_tokenize(args.sent)
        else:
            # Demo: use a default test-sentence with gold tree.
            sentence, gold = SENT.split(), GOLD

        print('Parsing sentence...')
        start = time.time()
        tree, score = parser.parse(sentence, use_numpy=args.use_numpy)
        elapsed = time.time() - start
        tree.un_chomsky_normal_form()

        print('Predicted.')
        print()
        tree.pretty_print()
        print('Logprob:', score)
        print()

        if not args.sent:
            gold = Tree.fromstring(gold)
            prec, recall, fscore = parser.evalb(
                gold.pformat(margin=np.inf), tree.pformat(margin=np.inf))
            print('Gold.')
            gold.pretty_print()
            print(f'Precision = {prec:.3f}')
            print(f'Recall = {recall:.3f}')
            print(f'F1 = {fscore:.3f}')
            print()

        print(f'Parse-time: {elapsed:.3f}s.')

        if args.perplexity:
            perplexity = parser.perplexity(sentence)
            print('Perplexity:', round(perplexity, 2))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    argparser.add_argument('--grammar', type=str, default='grammar/train/train.vanilla.grammar')
    argparser.add_argument('--sent', type=str, default='')
    argparser.add_argument('--infile', type=str, default='')
    argparser.add_argument('--outfile', type=str, default='pred.trees')
    argparser.add_argument('--goldfile', type=str, default='')
    argparser.add_argument('--syneval', type=str, default='')
    argparser.add_argument('--result', type=str, default='result.txt')
    argparser.add_argument('--treefile', type=str, default='')
    argparser.add_argument('--evalb_dir', type=str, default='EVALB')
    argparser.add_argument('--use-numpy', action='store_true')
    argparser.add_argument('--perplexity', action='store_true')
    argparser.add_argument('--short', action='store_true')
    argparser.add_argument('-n', '--num-lines', type=int, default=None)
    argparser.add_argument('-q', '--ignore-empty', type=int, default=1000, help='let evalb ignore empty lines')
    argparser.add_argument('-t', '--tokenize', action='store_true')
    argparser.add_argument('-p', '--parallel', action='store_true')
    argparser.add_argument('-s', '--show', action='store_true')
    argparser.add_argument('-b', '--expand-binaries', action='store_true', help='expand binary rules with each possible unary')

    args = argparser.parse_args()

    main(args)
