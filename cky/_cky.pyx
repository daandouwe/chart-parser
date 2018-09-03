#cython: language_level=3, boundscheck=False, wraparound=False, profile=True
import cython
import numpy as np
cimport numpy as np
from libc.math cimport log


def cky(
    int[:] sentence,
    int sent_len,
    float[:,:,:] score,
    int[:,:,:,:] back,
    int num_lex_rules,
    int num_unary_rules,
    int num_binary_rules,
    int[:,:] lex_rules,
    int[:,:] unary_rules,
    int[:,:] binary_rules,
    float[:] lex_prob,
    float[:] unary_prob,
    float[:] binary_prob
    ):

    cdef int i, j
    cdef int span, begin, end, split
    cdef int A, B, C, w
    cdef float prob, rule_prob

    for i in range(sent_len):
        for j in range(num_lex_rules):
            A, w = lex_rules[j][0], lex_rules[j][1]  # A -> w
            if w == sentence[i]:
                score[A][i][i+1] = log(lex_prob[j])
                # Handle unaries.
                # for k in range(num_unary_rules):
                #     B, C = unary_rules[k][0], unary_rules[k][1]  # B -> C
                #     if C == A:  # from  B -> A  and  A -> w  derive  B -> w
                #         score[C][i][i+1] = lex_prob[j] * unary_prob[k]

    for span in range(2, sent_len + 1):
        for begin in range(0, sent_len - span + 1):
            end = begin + span
            for split in range(begin + 1, end):
                for i in range(num_binary_rules):
                    A, B, C = binary_rules[i][0], binary_rules[i][1], binary_rules[i][2]
                    rule_prob = binary_prob[i]
                    prob = score[B][begin][split] + score[C][split][end] + log(rule_prob)
                    if prob > score[A][begin][end]:
                        score[A][begin][end] = prob
                        back[A][begin][end][0] = split
                        back[A][begin][end][1] = B
                        back[A][begin][end][2] = C

    return score, back
