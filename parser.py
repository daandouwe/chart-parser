import numpy as np
from tqdm import tqdm

from symbol import Symbol, Terminal, Nonterminal, Span
from rule import Rule
from grammar import PCFG
from util import process_sentence, make_nltk_tree, unbinarize
from cky import _cky


class Parser:
    def __init__(self, grammar_path):
        self.grammar = PCFG.from_file(grammar_path)

    def __call__(self, sentence):
        processed_sentence = process_sentence(sentence, self.grammar.w2i)
        print('Processed sentence: `{}`'.format(' '.join(processed_sentence)))
        print('Running CKY...')
        score, back = self.cky(processed_sentence)
        print('Finding spanning nodes...')
        roots = self.get_spanning_roots(score)
        # if not roots:
            # exit('Could not parse the sentence: no spanning nonterminals were found.')
        print('Building trees...')
        return [(self.build_tree(back, sentence, root), score) for root, score in roots[:10]]


    def get_spanning_roots(self, score):
        spanning_scores = score[:, 0, -1]
        spanning_nodes = [(i, score) for i, score in enumerate(spanning_scores) if score > 0]
        return sorted(spanning_nodes, key=lambda x: x[1], reverse=True)

    def cky(self, sentence):
        sent_len = len(sentence)
        sentence_array = np.array(
            [self.grammar.w2i[word] for word in sentence],
            dtype=np.int32
        )

        score = np.zeros((self.grammar.num_nonterminals,
                          sent_len + 1,
                          sent_len + 1), dtype=np.float32)

        back = -1 * np.ones((self.grammar.num_nonterminals,
                         sent_len + 1,
                         sent_len + 1,
                         3), dtype=np.int32)

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

        return np.asarray(score),  np.asarray(back)

    def build_tree(self, back, sentence, root):
        derivation = []
        num_words = len(sentence)

        def recursion(begin, end, A):
            backpointer = back[A][begin][end]

            # Recursive case (when backpointer is not -1)
            if backpointer[0] > -1:
                # Catch the elements stored in backpointer
                split, B, C = backpointer

                # Annotate the recognized Nonterminals with spans
                A_span = Span(Nonterminal(self.grammar.i2n[A]), begin, end)
                B_span = Span(Nonterminal(self.grammar.i2n[B]), begin, split)
                C_span = Span(Nonterminal(self.grammar.i2n[C]), split, end)

                # Reconstruct the binary rule
                # (The rule probability is irrelevent at this stage)
                rule = Rule(A_span, [B_span, C_span], prob=None)
                derivation.append(rule)

                # Recursive call
                derivation.extend(recursion(begin, split, B))
                derivation.extend(recursion(split, end, C))

            # Base case
            else:
                # Recover the word from the sentence
                word = Terminal(sentence[begin])

                # Annotate the recognized Nonterminals with spans
                A_span = Span(Nonterminal(self.grammar.i2n[A]), begin, end)
                word_span = Span(word, begin, end)

                # Reconstruct the unary rule
                # (The rule probability is irrelevent at this stage)
                rule = Rule(A_span, [word_span], prob=None)

            return [rule]

        recursion(0, num_words, root)

        return make_nltk_tree(derivation)
