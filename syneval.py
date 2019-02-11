"""Evaluate accuracy on the syneval dataset."""
import os
from collections import Counter
import multiprocessing as mp

import numpy as np
from tqdm import tqdm

from utils import process_sentence, ceil_div


ALL = [
    'simple_agrmt',
    'sent_comp',
    'vp_coord',
    'long_vp_coord',
    'prep_anim',
    'prep_inanim',
    'subj_rel',
    'obj_rel_across_anim',
    'obj_rel_across_inanim',
    'obj_rel_no_comp_across_anim',
    'obj_rel_no_comp_across_inanim',
    'obj_rel_no_comp_within_anim',
    'obj_rel_no_comp_within_inanim',
    'obj_rel_within_anim',
    'obj_rel_within_inanim',

    'simple_reflexives',
    'reflexive_sent_comp',
    'reflexives_across',

    'simple_npi_anim',
    'simple_npi_anim_the',
    'simple_npi_inanim',
    'simple_npi_inanim_the',
    'npi_across_anim',
    'npi_across_anim_the',
    'npi_across_inanim',
    'npi_across_inanim_the',
]

SHORT = [
    'simple_agrmt',
    'simple_npi_anim',
    'simple_npi_anim_the',
    'simple_reflexives',
    'vp_coord',
]


def syneval(parser, indir, outpath, parallel=False, short=False, add_period=True):

    print(f'Loading syneval examples from directory `{indir}`.')
    print(f'Writing predictions to `{outpath}`.')

    files = SHORT if short else ALL

    with open(outpath, 'w') as outfile:
        print('\t'.join((
                'name', 'index', 'pos-perplexity', 'neg-perplexity',
                'correct', 'pos-sentence-processed', 'neg-sentence-processed')),
            file=outfile)

        print('Predicting syneval for:', '\n', '\n '.join(files))

        for fname in files:
            print(f'Predicting `{fname}`...')

            inpath = os.path.join(indir, fname)

            with open(inpath + '.pos') as f:
                pos_sents = [line.strip() for line in f.readlines()]
                if add_period:
                    pos_sents = [sent + ' .' for sent in pos_sents]

            with open(inpath + '.neg') as f:
                neg_sents = [line.strip() for line in f.readlines()]
                if add_period:
                    neg_sents = [sent + ' .' for sent in neg_sents]


            pos_sents = [sent.split() for sent in pos_sents]
            neg_sents = [sent.split() for sent in neg_sents]

            assert len(pos_sents) == len(neg_sents)

            if parallel:
                size = mp.cpu_count()
                print(f'Predicting in parallel with {size} processes...')

                chunk_size = ceil_div(len(pos_sents), size)
                pos_parts = [pos_sents[i:i+chunk_size] for i in range(0, len(pos_sents), chunk_size)]
                neg_parts = [neg_sents[i:i+chunk_size] for i in range(0, len(neg_sents), chunk_size)]

                # spawn processes
                manager = mp.Manager()
                return_dict = manager.dict()
                processes = []
                for rank in range(size):
                    p = mp.Process(
                        target=worker, args=(parser, rank, pos_parts[rank], neg_parts[rank], fname, return_dict))
                    p.start()
                    processes.append(p)
                for p in processes:
                    p.join()

                results = sum([return_dict[rank][0] for rank in range(size)], [])  # merge all results
                num_correct = sum([return_dict[rank][1] for rank in range(size)])  # sum number of correct results

            else:
                results = []
                num_correct = 0

                for i, (pos, neg) in enumerate(tqdm(list(zip(pos_sents, neg_sents)))):

                    pos_pp = parser.perplexity(pos)
                    neg_pp = parser.perplexity(neg)
                    correct = pos_pp < neg_pp
                    num_correct += correct

                    # see which words are unked during prediction
                    pos = process_sentence(pos, parser.grammar.w2i)
                    neg = process_sentence(neg, parser.grammar.w2i)

                    result =  (
                        fname,
                        str(i),
                        str(round(pos_pp, 2)),
                        str(round(neg_pp, 2)),
                        str(int(correct)),
                        ' '.join(pos),
                        ' '.join(neg)
                    )
                    results.append(result)

            for result in results:
                print('\t'.join(result), file=outfile)

            print(f'{fname}: {num_correct}/{len(pos_sents)} = {num_correct / len(pos_sents):.2%} correct', '\n')


def worker(parser, rank, pos_sents, neg_sents, name, return_dict):
    """Parallel worker."""
    results = []
    num_correct = 0

    sentences = list(zip(pos_sents, neg_sents))
    if rank == 0:
        sentences = tqdm(list(zip(pos_sents, neg_sents)))

    for i, (pos, neg) in enumerate(sentences):

        pos_pp = parser.perplexity(pos)
        neg_pp = parser.perplexity(neg)
        correct = pos_pp < neg_pp
        num_correct += correct

        # see which words are unked during prediction
        pos = process_sentence(pos, parser.grammar.w2i)
        neg = process_sentence(neg, parser.grammar.w2i)

        result =  (
            name,
            str(i),
            str(round(pos_pp, 2)),
            str(round(neg_pp, 2)),
            str(int(correct)),
            ' '.join(pos),
            ' '.join(neg)
        )
        results.append(result)

    return_dict[rank] = (results, num_correct)
