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

    def parse(self, sentence, verbose=True, use_numpy=False, num_trees=10, root='TOP'):
        processed_sentence = process_sentence(sentence, self.grammar.w2i)
        if verbose:
            print('Processed sentence: `{}`'.format(' '.join(processed_sentence)))
            print('Running CKY...')
        score, back = self.cky(processed_sentence, use_numpy=use_numpy)

        root_id = self.grammar.n2i[root]
        score = score[root_id, 0, -1]

        if verbose:
            print('Building tree...')
        tree = self.build_tree(back, sentence, root=root)

        return tree, score

    def perplexity(self, sentence):
        processed_sentence = process_sentence(sentence, self.grammar.w2i)

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
            self.grammar.num_lexical_rules,
            self.grammar.num_unary_rules,
            self.grammar.num_binary_rules,
            self.grammar.num_nonterminals,
            self.grammar.lexical,
            self.grammar.unary,
            self.grammar.binary,
            self.grammar.top,
            self.grammar.lexical_prob,
            self.grammar.unary_prob,
            self.grammar.binary_prob,
            self.grammar.top_prob,
        )

        return np.exp(-logprob / sent_len)

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
                self.grammar.num_lexical_rules,
                self.grammar.num_unary_rules,
                self.grammar.num_binary_rules,
                self.grammar.lexical,
                self.grammar.unary,
                self.grammar.binary,
                self.grammar.top,
                self.grammar.lexical_prob,
                self.grammar.unary_prob,
                self.grammar.binary_prob,
                self.grammar.top_prob
            )
            score, back = np.asarray(score), np.asarray(back)

        else:
            print('Warning: using slow NumPy CKY!')
            score, back = cky_numpy.cky(
                sentence_array,
                score,
                back,
                self.grammar.lexical,
                self.grammar.unary,
                self.grammar.binary,
                self.grammar.lexical_prob,
                self.grammar.unary_prob,
                self.grammar.binary_prob
            )

        return score, back

    def build_tree(self, back, sentence, root='TOP'):

        def recursion(begin, end, A):
            split, B, C = back[A][begin][end]
            A = self.grammar.i2n[A]
            if split == -1:  # a unary rule like Tag -> word
                return Tree(A, [sentence[begin]])
            if split == -2:  # a unary rule like Nonterminal -> Tag
                return Tree(A, [recursion(begin, -1, B)])  # B must be a tag so split is -1
            else:  # a binary rule like A -> B C
                return Tree(A, [recursion(begin, split, B), recursion(split, end, C)])

        # find out what the the root expands to
        _, B, _ = back[self.grammar.n2i[root]][0][len(sentence)]  # TOP -> B
        # build the rest of the binary tree from there
        tree = recursion(0, len(sentence), B)
        # attach the root to the top of the tree
        return Tree(root, [tree])

    def evalb(self, gold, pred):
        gold = evalb_parser.create_from_bracket_string(gold)
        pred = evalb_parser.create_from_bracket_string(pred)
        result = scorer.Scorer().score_trees(gold, pred)
        prec, recall = result.prec, result.recall
        fscore = 2 * (prec * recall) / (prec + recall)
        return prec, recall, fscore
