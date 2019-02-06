import numpy as np
from tqdm import tqdm
from nltk import Tree
from PYEVALB import scorer
from PYEVALB import parser as evalb_parser

from pcfg import PCFG
from utils import process_sentence
from cky import _cky, cky_numpy


class Parser:
    def __init__(self, grammar_path, expand_binaries=False):
        self.grammar = PCFG.from_file(grammar_path, expand_binaries)

    def __call__(self, sentence, verbose=True, use_numpy=False, num_trees=10):
        processed_sentence = process_sentence(sentence, self.grammar.w2i)
        if verbose:
            print('Processed sentence: `{}`'.format(' '.join(processed_sentence)))
            print('Running CKY...')
        score, back = self.cky(processed_sentence, use_numpy=use_numpy)
        if verbose:
            print('Finding spanning nodes...')
        roots = self.get_spanning_roots(score)

        if verbose:
            print('Building trees...')
        best_trees = [(self.build_tree(back, sentence, root), score) for root, score in roots[:num_trees]]

        return best_trees

    def perplexity(self, sentence):
        processed_sentence = process_sentence(sentence, self.grammar.w2i)

        print('Computing the perplexity.')
        sent_len = len(sentence)

        sentence_array = np.array(
            [self.grammar.w2i[word] for word in processed_sentence], dtype=np.int32)

        score = -np.inf * np.ones(
            (self.grammar.num_nonterminals, sent_len+1, sent_len+1), dtype=np.float32)

        back = -1 * np.ones(
            (self.grammar.num_nonterminals, sent_len+1, sent_len+1, 3), dtype=np.int32)

        # Inside recursion
        logprob = _cky.inside(
            sentence_array,
            sent_len,
            score,
            self.grammar.num_lex_rules,
            self.grammar.num_unary_rules,
            self.grammar.num_binary_rules,
            self.grammar.num_nonterminals,
            self.grammar.lex,
            self.grammar.unary,
            self.grammar.binary,
            self.grammar.lex_prob,
            self.grammar.unary_prob,
            self.grammar.binary_prob
        )

        return np.exp(-logprob / sent_len)

    def get_spanning_roots(self, score):
        spanning_scores = score[:, 0, -1]  # All nodes that span 0 to sent_len.
        spanning_nodes = [(i, score) for i, score in enumerate(spanning_scores) if score > -np.inf]
        return sorted(spanning_nodes, key=lambda x: x[1], reverse=True)

    def cky(self, sentence, use_numpy=False):
        sent_len = len(sentence)
        sentence_array = np.array(
            [self.grammar.w2i[word] for word in sentence], dtype=np.int32)

        score = -np.inf * np.ones(
            (self.grammar.num_nonterminals, sent_len+1, sent_len+1), dtype=np.float32)

        back = -1 * np.ones(
            (self.grammar.num_nonterminals, sent_len+1, sent_len+1, 3), dtype=np.int32)

        if not use_numpy:
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
            score, back = np.asarray(score), np.asarray(back)

        else:
            print('Warning: using slow NumPy CKY!')
            score, back = cky_numpy.cky(
                sentence_array,
                score,
                back,
                self.grammar.lex,
                self.grammar.unary,
                self.grammar.binary,
                self.grammar.lex_prob,
                self.grammar.unary_prob,
                self.grammar.binary_prob
            )

        return score, back

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
        gold = evalb_parser.create_from_bracket_string(gold)
        pred = evalb_parser.create_from_bracket_string(pred)
        result = scorer.Scorer().score_trees(gold, pred)
        prec, recall = result.prec, result.recall
        fscore = 2 * (prec * recall) / (prec + recall)
        return prec, recall, fscore
