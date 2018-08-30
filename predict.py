import multiprocessing as mp

import numpy as np
from nltk import tokenize, Tree
from tqdm import tqdm

from parser import Parser
from util import cleanup_tree


def predict_from_trees(parser, infile):
    with open(infile) as fin:
        trees = [Tree.fromstring(line) for line in fin.readlines()]
    for gold in trees:
        trees = parser(gold.leaves(), verbose=False)
        if not trees:  # TODO: why empty trees?
            yield 0, 0, 0
        else:
            pred, score = trees[0]
            pred = cleanup_tree(pred)
            gold_tree, pred_tree = gold.pformat(margin=np.inf), pred.pformat(margin=np.inf)
            prec, recall, fscore = parser.evalb(gold_tree, pred_tree)
            yield gold, pred, prec, recall, fscore


def predict_from_file(parser, infile, outfile, num_lines=-1):
    with open(infile) as fin:
        sentences = [tokenize.word_tokenize(line.strip()) for line in fin.readlines()]
        sentences = sentences[-num_lines:]
    predicted = []
    failed = 0
    try:
        for i, sentence in enumerate(tqdm(sentences)):
            trees = parser(sentence, verbose=False)
            if not trees:
                predicted.append('')  # TODO: why empty trees?
                failed += 1
            else:
                tree, score = trees[0]
                tree = cleanup_tree(tree)
                tree = tree.pformat(margin=np.inf)
                predicted.append(tree)
    except KeyboardInterrupt:
        print(f'Prediction interrupted at sentence {i}.')
    if failed > 0:
        print(f'Failed to parse {failed} sentences.')
    with open(outfile, 'w') as fout:
        print('\n'.join(predicted), file=fout)


def predict_from_file_parallel(parser, infile, outfile, num_lines=-1):
    size = mp.cpu_count()
    print(f'Predicting in parallel with {size} processes...')

    def worker(parser, sentences, rank, return_dict, failed_dict):
        predicted = []
        failed = 0
        if rank == 0:
            sentences = tqdm(sentences)
        for sentence in sentences:
            trees = parser(sentence, verbose=False)
            if not trees:
                predicted.append('')  # TODO: why empty trees?
                failed += 1
            else:
                tree, score = trees[0]
                tree = cleanup_tree(tree)
                tree = tree.pformat(margin=np.inf)
                predicted.append(tree)
        return_dict[rank] = predicted
        failed_dict[rank] = failed

    # Read sentences and partition them to be distributed among processes.
    with open(infile) as fin:
        sentences = [tokenize.word_tokenize(line.strip()) for line in fin.readlines()]
        sentences = sentences[-num_lines:]
    chunk_size = len(sentences) // size
    partitioned = [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]
    # Spawn processes.
    manager = mp.Manager()
    return_dict = manager.dict()
    failed_dict = manager.dict()
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
    with open(outfile, 'w') as fout:
        print('\n'.join(trees), file=fout)
