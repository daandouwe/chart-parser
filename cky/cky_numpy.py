"""
A Numpy CKY.

This cky is almost identical to _cky.pyx, but not typed,
and not cythonized, and is around 80 times slower.
"""

import numpy as np

def cky(
    sentence,
    score,
    back,
    lex_rules,
    unary_rules,
    binary_rules,
    lex_prob,
    unary_prob,
    binary_prob
    ):

    sent_len = sentence.shape[0]
    num_lex_rules = lex_rules.shape[0]
    num_unary_rules = lex_rules.shape[0]
    num_binary_rules = lex_rules.shape[0]

    for i in range(sent_len):
        for j in range(num_lex_rules):
            A, w = lex_rules[j][0], lex_rules[j][1]  # A -> w
            if w == sentence[i]:
                score[A][i][i+1] = np.log(lex_prob[j])

    for span in range(2, sent_len + 1):
        for begin in range(0, sent_len - span + 1):
            end = begin + span
            for split in range(begin + 1, end):
                for i in range(num_binary_rules):
                    A, B, C = binary_rules[i][0], binary_rules[i][1], binary_rules[i][2]
                    rule_prob = binary_prob[i]
                    prob = score[B][begin][split] + score[C][split][end] + np.log(rule_prob)
                    if prob > score[A][begin][end]:
                        score[A][begin][end] = prob
                        back[A][begin][end][0] = split
                        back[A][begin][end][1] = B
                        back[A][begin][end][2] = C

    return score, back
