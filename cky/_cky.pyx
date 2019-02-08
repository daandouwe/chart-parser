#cython: language_level=3, boundscheck=False, wraparound=False
import cython
import numpy as np
cimport numpy as np
from libc.math cimport log, exp
from numpy.math cimport INFINITY


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
        int[:,:] top_rules,
        float[:] lex_prob,
        float[:] unary_prob,
        float[:] binary_prob,
        float[:] top_prob
    ):

    cdef int i, j
    cdef int span, begin, end, split
    cdef int A, B, C, w
    cdef float logprob, rule_prob

    # recognize the lexical rules
    for i in range(sent_len):
        for j in range(num_lex_rules):
            A, w = lex_rules[j][0], lex_rules[j][1]  # A -> w
            if w == sentence[i]:
                score[A][i][i+1] = log(lex_prob[j])

    # recognize part of speech unary rules
    for i in range(sent_len):
        for j in range(num_unary_rules):
            A, B = unary_rules[j][0], unary_rules[j][1]  # A -> B
            rule_prob = unary_prob[j]
            logprob = score[B][i][i+1] + log(rule_prob)
            if logprob > score[A][i][i+1]:
                score[A][i][i+1] = logprob
                back[A][i][i+1][0] = -2
                back[A][i][i+1][1] = B
                back[A][i][i+1][2] = -2

    # recognize the binary rules
    for span in range(2, sent_len + 1):
        for begin in range(0, sent_len - span + 1):
            end = begin + span
            for split in range(begin + 1, end):
                for i in range(num_binary_rules):
                    A, B, C = binary_rules[i][0], binary_rules[i][1], binary_rules[i][2]  # A -> B C
                    rule_prob = binary_prob[i]
                    logprob = score[B][begin][split] + score[C][split][end] + log(rule_prob)
                    if logprob > score[A][begin][end]:
                        score[A][begin][end] = logprob
                        back[A][begin][end][0] = split
                        back[A][begin][end][1] = B
                        back[A][begin][end][2] = C

    # recognize the unary top-rules
    begin, end = 0, sent_len
    for i in range(top_rules.shape[0]):
        A, B = top_rules[i][0], top_rules[i][1]  # A -> B
        rule_prob = top_prob[i]
        logprob = score[B][begin][end] + log(rule_prob)
        if logprob > score[A][begin][end]:
            score[A][begin][end] = logprob
            back[A][begin][end][0] = -2
            back[A][begin][end][1] = B
            back[A][begin][end][2] = -2

    return score, back


def inside(
        int[:] sentence,
        int sent_len,
        float[:,:,:] score,
        int num_lex_rules,
        int num_unary_rules,
        int num_binary_rules,
        int num_nonterminals,
        int[:,:] lex_rules,
        int[:,:] unary_rules,
        int[:,:] binary_rules,
        int[:,:] top_rules,
        float[:] lex_prob,
        float[:] unary_prob,
        float[:] binary_prob,
        float[:] top_prob,
    ):

    cdef int i, j
    cdef int span, begin, end, split
    cdef int A, B, C, w
    cdef float logprob, rule_prob

    for i in range(sent_len):
        for j in range(num_lex_rules):
            A, w = lex_rules[j][0], lex_rules[j][1]  # A -> w
            if w == sentence[i]:
                score[A][i][i+1] = log(lex_prob[j])

    # recognize part of speech unary rules
    for i in range(sent_len):
        for j in range(num_unary_rules):
            A, B = unary_rules[j][0], unary_rules[j][1]  # A -> B
            rule_prob = unary_prob[j]
            logprob = score[B][i][i+1] + log(rule_prob)
            if logprob > score[A][i][i+1]:
                score[A][i][i+1] = logprob

    # sum over the binary rules
    for span in range(2, sent_len + 1):
        for begin in range(0, sent_len - span + 1):
            end = begin + span
            for split in range(begin + 1, end):
                for i in range(num_binary_rules):
                    A, B, C = binary_rules[i][0], binary_rules[i][1], binary_rules[i][2]  # A -> B C
                    rule_prob = binary_prob[i]
                    logprob = score[B][begin][split] + score[C][split][end] + log(rule_prob)
                    # accumulate sums (in log domain)
                    if score[A][begin][end] == -INFINITY:
                        score[A][begin][end] = logprob
                    else:
                        score[A][begin][end] = log_add_exp(logprob, score[A][begin][end])

    # sum over the unary top-rules:
    begin, end = 0, sent_len
    inside = -INFINITY  # accumulator
    for i in range(top_rules.shape[0]):
        A, B = top_rules[i][0], top_rules[i][1]  # A -> B
        rule_prob = top_prob[i]
        logprob = score[B][begin][end] + log(rule_prob)
        if logprob > -INFINITY:
           if inside == -INFINITY:
               inside = logprob  # first assingment
           else:
               inside = log_add_exp(inside, logprob)

    return inside


cdef float log_add_exp(float a, float b):
    """Compute log(exp(a) + exp(b)) in a numerically stable way."""
    if a - b < b - a:  # choose the smaller exponent
        return b + log(1 + exp(a - b))
    else:
        return a + log(1 + exp(b - a))
