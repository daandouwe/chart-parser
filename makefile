DEV=grammar/dev/dev.tokens
TEST=grammar/test/test.tokens

SYN ?= /Users/daan/data/syneval/data/converted

MARKOV_VERT ?= 1
MARKOV_HORZ ?= 1

MARKOV=markov.v${MARKOV_VERT}h${MARKOV_HORZ}


eval-dev:
	python main.py \
		--infile=grammar/dev/dev.tokens \
		--outfile=grammar/dev/dev.pred.trees \
		--goldfile=grammar/data/dev.trees \
		--grammar=grammar/train/train.vanilla.grammar \
		--result=results/results.vanilla.txt \
		--parallel

eval-test:
	python main.py \
		--infile=grammar/test/test.tokens \
		--outfile=grammar/test/test.pred.trees \
		--goldfile=grammar/data/test.trees \
		--grammar=grammar/train/train.vanilla.grammar \
		--result=results/results.vanilla.txt \
		--parallel

eval-dev-markov:
	python main.py \
		--infile=grammar/dev/dev.tokens \
		--outfile=grammar/dev/dev.pred.trees \
		--goldfile=grammar/data/dev.trees \
		--grammar=grammar/train/train.${MARKOV}.grammar \
		--result=results/results.${MARKOV}.txt \
		--parallel

eval-test-markov:
	python main.py \
		--infile=grammar/test/test.tokens \
		--outfile=grammar/test/test.pred.trees \
		--goldfile=grammar/data/test.trees \
		--grammar=grammar/train/train.${MARKOV}.grammar \
		--result=results/results.${MARKOV}.txt \
		--parallel

syneval:
	python main.py \
		--syneval=${SYN} \
		--outfile=results/syneval_results.vanilla.tsv \
		--grammar=grammar/train/train.vanilla.grammar \
		--parallel

syneval-markov:
	python main.py \
		--syneval=${SYN} \
		--outfile=results/syneval_results.${MARKOV}.tsv \
		--grammar=grammar/train/train.${MARKOV}.grammar \
		--parallel
