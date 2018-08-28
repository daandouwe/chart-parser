from collections import defaultdict

import numpy as np
from tqdm import tqdm


class PCFG:
    def __init__(self, n2i, i2n, w2i, i2w, lex, unary, binary, lex_prob, unary_prob, binary_prob):
        self.n2i = n2i
        self.i2n = i2n
        self.w2i = w2i
        self.i2w = i2w
        self.lex = lex
        self.unary = unary
        self.binary = binary
        self.lex_prob = lex_prob
        self.unary_prob = unary_prob
        self.binary_prob = binary_prob

    def from_file(path, expand_binaries=False):
        nlines = sum(1 for _ in open(path))
        nonterminals, vocab = set(), set()
        lex_rules, unary_rules, binary_rules = set(), set(), set()
        print(f'Reading grammar from {path}...')
        with open(path) as fin:
            for line in tqdm(fin, total=nlines):
                line = line.strip()
                if not line:
                    continue
                fields = line.split()
                if len(fields) == 3:
                    lhs, rhs, prob = fields[0], fields[1], float(fields[2])
                    nonterminals.add(lhs)
                    if rhs.startswith('[') and rhs.endswith(']'):
                        word = rhs[1:-1]  # remove brackets
                        vocab.add(word)
                        lex_rules.add((lhs, word, prob))
                    else:
                        nonterminals.add(rhs)
                        unary_rules.add((lhs, rhs, prob))
                elif len(fields) == 4:
                    lhs, rhs_a, rhs_b, prob = fields[0], fields[1], fields[2], float(fields[3])
                    nonterminals.add(lhs)
                    nonterminals.add(rhs_a)
                    nonterminals.add(rhs_b)
                    binary_rules.add((lhs, rhs_a, rhs_b, prob))
                else:
                    raise ValueError('unrecognized line format: {}'.format(fields))

        n2i = dict((nt, i) for i, nt in enumerate(sorted(nonterminals)))
        w2i = dict((word, i) for i, word in enumerate(sorted(vocab)))
        i2n = dict((i, nt) for nt, i in n2i.items())
        i2w = dict((i, word) for word, i in w2i.items())

        if expand_binaries:
            print('Expanding binary rules...')
            print('Before: lex', len(lex_rules), 'unary', len(unary_rules), 'binary', len(binary_rules))
            binary_rules = expand_binaries_with_unaries(binary_rules, unary_rules)
            print('Before: lex', len(lex_rules), 'unary', len(unary_rules), 'binary', len(binary_rules))

        lex_rules, unary_rules, binary_rules = sorted(lex_rules), sorted(unary_rules), sorted(binary_rules)

        lex = np.zeros((len(lex_rules), 2), dtype=np.int32)
        unary = np.zeros((len(unary_rules), 2), dtype=np.int32)
        binary = np.zeros((len(binary_rules), 3), dtype=np.int32)

        lex_prob = np.zeros(len(lex_rules), dtype=np.float32)
        unary_prob = np.zeros(len(unary_rules), dtype=np.float32)
        binary_prob = np.zeros(len(binary_rules), dtype=np.float32)

        for i, rule in enumerate(lex_rules):
            lhs, rhs, prob = rule
            lex[i] = n2i[lhs], w2i[rhs]
            lex_prob[i] = prob
        for i, rule in enumerate(unary_rules):
            lhs, rhs, prob = rule
            unary[i] = n2i[lhs], n2i[rhs]
            unary_prob[i] = prob
        for i, rule in enumerate(binary_rules):
            lhs, rhs_a, rhs_b, prob = rule
            binary[i] = n2i[lhs], n2i[rhs_a], n2i[rhs_b]
            binary_prob[i] = prob

        return PCFG(n2i, i2n, w2i, i2w, lex, unary, binary, lex_prob, unary_prob, binary_prob)

    def __len__(self):
        return self.unary.shape[0] + self.binary.shape[0]

    def __str__(self):
        """Prints the grammar line by line"""
        lines = []
        for lhs, rules in self.items():
            for rule in rules:
                lines.append(str(rule))
        return '\n'.join(lines)

    def lex_rule(self, index):
        lhs, rhs = self.lex[index]
        prob = self.lex_prob[index]
        return self.i2n[lhs], self.i2w[rhs], prob

    def unary_rule(self, index):
        lhs, rhs = self.unary[index]
        prob = self.unary_prob[index]
        return self.i2n[lhs], self.i2n[rhs], prob

    def binary_rule(self, index):
        lhs, rhs_a, rhs_b = self.binary[index]
        prob = self.binary_prob[index]
        return self.i2n[lhs], self.i2n[rhs_a], self.i2n[rhs_b], prob

    def format_lex_rule(self, index):
        return '{} -> {} | {}'.format(*self.lex_rule(index))

    def format_unary_rule(self, index):
        return '{} -> {} | {}'.format(*self.unary_rule(index))

    def format_binary_rule(self, index):
        return '{} -> {} {} | {}'.format(*self.binary_rule(index))

    @property
    def num_nonterminals(self):
        """The list of nonterminal symbols in the grammar"""
        return len(self.n2i)

    @property
    def num_words(self):
        """The list of nonterminal symbols in the grammar"""
        return len(self.w2i)

    @property
    def num_lex_rules(self):
        """The list of nonterminal symbols in the grammar"""
        return self.lex.shape[0]

    @property
    def num_unary_rules(self):
        """The list of nonterminal symbols in the grammar"""
        return self.unary.shape[0]

    @property
    def num_binary_rules(self):
        """The list of nonterminal symbols in the grammar"""
        return self.binary.shape[0]

    @property
    def nonterminals(self):
        """The list of nonterminal symbols in the grammar"""
        return self.n2i.items()

    @property
    def terminals(self):
        """The list of terminal symbols in the grammar"""
        return self.w2i.items()

    @property
    def binary_rules(self):
        """The list of binary rules in the grammar"""
        return [self.binary_rule(i) for i in range(self.binary.shape[0])]

    @property
    def unary_rules(self):
        """The list of unary rules in the grammar"""
        return [self.unary_rule(i) for i in range(self.unary.shape[0])]

    @property
    def lex_rules(self):
        """The list of unary rules in the grammar"""
        return [self.lex_rule(i) for i in range(self.lex.shape[0])]


def expand_binaries_with_unaries(binary_rules, unary_rules):
    expanded_binary_rules = list(binary_rules)  # all binary rules are already part
    for rule in tqdm(binary_rules):
        a, b, c, binary_prob = rule  # a -> b c
        for rule in unary_rules:
            d, e, unary_prob =  rule  # d -> e
            if  d == b:
                expanded = (a, e, c, binary_prob * unary_prob)  # a -> b c  and  d -> e  derives  a -> e c  if b = d
                expanded_binary_rules.append(expanded)
            if  d == c:
                expanded = (a, b, e, binary_prob * unary_prob)  # a -> b c  and  d -> e  derives  a -> b e  if b = c
                expanded_binary_rules.append(expanded)
    return expanded_binary_rules


if __name__ == '__main__':
    grammar = PCFG.from_file('train.grammar')
    for i in range(grammar.num_unary_rules):
        print(grammar.format_unary_rule(i))
