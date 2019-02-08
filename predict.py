import multiprocessing as mp

import numpy as np
from nltk import tokenize, Tree
from tqdm import tqdm

from parser import Parser
from utils import ceil_div


def predict_from_trees(parser, infile):
    with open(infile) as fin:
        trees = [Tree.fromstring(line) for line in fin.readlines()]
    for gold in trees:
        pred, score = parser(gold.leaves(), verbose=False)
        # if not trees:  # TODO: why empty trees?
            # yield 0, 0, 0
        # else:
        pred.un_chomsky_normal_form()
        gold_tree, pred_tree = gold.pformat(margin=np.inf), pred.pformat(margin=np.inf)
        prec, recall, fscore = parser.evalb(gold_tree, pred_tree)
        yield gold, pred, prec, recall, fscore


def predict_from_file(parser, infile, max_lines=None, tokenize=False):
    with open(infile) as fin:
        if tokenize:
            sentences = [tokenize.word_tokenize(line.strip()) for line in fin.readlines()]
        else:
            sentences = [line.strip().split() for line in fin.readlines()]
        sentences = sentences if max_lines == None else sentences[:max_lines]
    predicted = []
    failed = 0
    try:
        for i, sentence in enumerate(tqdm(sentences)):
            tree, score = parser(sentence, verbose=False)
            # if not trees:
                # predicted.append('')  # TODO: why empty trees?
                # failed += 1
            # else:
            tree.un_chomsky_normal_form()
            tree = tree.pformat(margin=np.inf)
            predicted.append(tree)
    except KeyboardInterrupt:
        print(f'Prediction interrupted at sentence {i}.')
    if failed > 0:
        print(f'Failed to parse {failed} sentences.')
    return predicted


def predict_from_file_parallel(parser, infile, max_lines=None, tokenize=False):
    size = mp.cpu_count()
    print(f'Predicting in parallel with {size} processes...')

    def worker(parser, sentences, rank, return_dict, failed_dict):
        predicted = []
        failed = 0
        if rank == 0:
            sentences = tqdm(sentences)
        for sentence in sentences:
            tree, score = parser(sentence, verbose=False)
            # if not trees:
                # predicted.append('')  # TODO: why empty trees?
                # failed += 1
            # else:
            tree.un_chomsky_normal_form()
            tree = tree.pformat(margin=np.inf)
            predicted.append(tree)
        return_dict[rank] = predicted
        failed_dict[rank] = failed

    # Read sentences and partition them, to be distributed among processes.
    with open(infile) as fin:
        if tokenize:
            sentences = [tokenize.word_tokenize(line.strip()) for line in fin.readlines()]
        else:
            sentences = [line.strip().split() for line in fin.readlines()]
        sentences = sentences if max_lines == None else sentences[:max_lines]
    chunk_size = ceil_div(len(sentences), size)
    partitioned = [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]  # TODO: we lose some sentences here...

    # Spawn processes.
    manager = mp.Manager()
    return_dict = manager.dict()  # To return trees.
    failed_dict = manager.dict()  # To return number of failed parses.
    processes = []
    for rank in range(size):
        p = mp.Process(target=worker, args=(parser, partitioned[rank], rank, return_dict, failed_dict))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    trees = sum([return_dict[rank] for rank in range(size)], [])
    failed = sum([failed_dict[rank] for rank in range(size)])
    if failed > 0:
        print(f'Failed to parse {failed} sentences.')
    return trees
