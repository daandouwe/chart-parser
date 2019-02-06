#!/usr/bin/env python
import time
import argparse

import numpy as np
import matplotlib.pyplot as plt

from parser import Parser


SENT = "the cat ".split()


def fit(times):
    times = np.array(times)
    lengths = np.arange(len(times))
    coeffs = np.polyfit(lengths, times, deg=3)
    polynomial = lambda x: sum(c * x**i for i, c in enumerate(coeffs)) / 25
    plt.plot(lengths, times, 'o')
    x = np.linspace(0, len(times), 100)
    plt.plot(x, list(map(polynomial, x)))
    plt.savefig('fit.pdf')


def main(args):
    parser = Parser(args.grammar, args.expand_binaries)
    times = []
    for length in range(args.length):
        start = time.time()
        for rep in range(args.reps):
            sentence = SENT * length
            trees = parser(sentence, verbose=False)
        elapsed = time.time() - start
        times.append(elapsed / args.reps)
        print(f'Length {length} took {elapsed} seconds')
    fit(times)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--grammar', type=str, default='grammar/train/train.grammar')
    argparser.add_argument('--reps', type=int, default=1)
    argparser.add_argument('--length', type=int, default=5)
    argparser.add_argument('--expand-binaries', action='store_true')
    args = argparser.parse_args()

    main(args)
