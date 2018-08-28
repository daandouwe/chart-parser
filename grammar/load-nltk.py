from nltk import PCFG

with open('dev/dev.nltk') as fin:
    rules = fin.read()

grammar = PCFG.fromstring(rules)
