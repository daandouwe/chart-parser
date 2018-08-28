#!/usr/bin/env python
import sys
from collections import defaultdict


def main(path):
    lhs_count = defaultdict(int)
    # First get total count.
    with open(path) as fin:
        lines = fin.readlines()
    for line in lines:
        count, lhs, *rhs = line.split()
        lhs_count[lhs] += int(count)
    # Then format rules
    rules = []
    with open(path) as fin:
        lines = fin.readlines()
    for line in lines:
        count, lhs, *rhs = line.split()
        count = int(count)
        if len(rhs) == 1:
            rules.append('{} -> {} [{}]'.format(lhs, rhs[0], count/lhs_count[lhs]))
        elif len(rhs) == 2:
            rules.append('{} -> {} {} [{}]'.format(lhs, rhs[0], rhs[1], count/lhs_count[lhs]))
        else:
            raise ValueError(f'strange right hand side of rule: {rhs}')
    print('\n'.join(rules))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        main(path)
    else:
        exit('Specify path.')
