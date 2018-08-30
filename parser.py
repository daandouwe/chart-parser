import numpy as np
from tqdm import tqdm
from nltk import Tree
from PYEVALB import scorer, parser

from pcfg import PCFG
from util import process_sentence
from cky import _cky


class Parser:
    def __init__(self, grammar_path, expand_binaries=False):
        self.grammar = PCFG.from_file(grammar_path, expand_binaries)

    def __call__(self, sentence, verbose=True):
        processed_sentence = process_sentence(sentence, self.grammar.w2i)
        if verbose: print('Processed sentence: `{}`'.format(' '.join(processed_sentence)))
        if verbose: print('Running CKY...')
        score, back = self.cky(processed_sentence)
        if verbose: print('Finding spanning nodes...')
        roots = self.get_spanning_roots(score)
        if verbose: print('Building trees...')
        return [(self.build_tree(back, sentence, root), score) for root, score in roots[:10]]

    def get_spanning_roots(self, score):
        spanning_scores = score[:, 0, -1]
        spanning_nodes = [(i, score) for i, score in enumerate(spanning_scores) if score > -np.inf]
        return sorted(spanning_nodes, key=lambda x: x[1], reverse=True)

    def cky(self, sentence):
        sent_len = len(sentence)
        sentence_array = np.array(
            [self.grammar.w2i[word] for word in sentence],
            dtype=np.int32
        )
        score = -np.inf * np.ones(
            (self.grammar.num_nonterminals, sent_len+1, sent_len+1),
            dtype=np.float32
        )
        back = -1 * np.ones(
            (self.grammar.num_nonterminals, sent_len+1, sent_len+1, 3),
            dtype=np.int32
        )
        score, back = _cky.cky(
            sentence_array,
            sent_len,
            score,
            back,
            self.grammar.num_lex_rules,
            self.grammar.num_unary_rules,
            self.grammar.num_binary_rules,
            self.grammar.lex,
            self.grammar.unary,
            self.grammar.binary,
            self.grammar.lex_prob,
            self.grammar.unary_prob,
            self.grammar.binary_prob
        )
        return np.asarray(score), np.asarray(back)

    def build_tree(self, back, sentence, root):

        def recursion(begin, end, A):
            backpointer = back[A][begin][end]
            A = self.grammar.i2n[A]
            if backpointer[0] > -1:
                split, B, C = backpointer
                return Tree(A, [recursion(begin, split, B), recursion(split, end, C)])
            else:
                word = sentence[begin]
                return Tree(A, [word])

        return recursion(0, len(sentence), root)

    def evalb(self, gold, pred):
        gold = parser.create_from_bracket_string(gold)
        pred = parser.create_from_bracket_string(pred)
        result = scorer.Scorer().score_trees(gold, pred)
        prec, recall = result.prec, result.recall
        fscore = 2 * (prec * recall) / (prec + recall)
        return prec, recall, fscore
