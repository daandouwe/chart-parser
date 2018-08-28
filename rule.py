from symbol import Symbol


class Rule:

    def __init__(self, lhs, rhs, prob):
        """
        Constructs a Rule.
        A Rule takes a LHS symbol and a list/tuple of RHS symbols.

        :param lhs: the LHS nonterminal
        :param rhs: a sequence of RHS symbols (terminal or nonterminal)
        :param prob: probability of the rule
        """

        assert isinstance(lhs, Symbol), 'LHS must be an instance of Symbol'
        assert len(rhs) > 0, 'If you want an empty RHS, use an epsilon Terminal EPS'
        assert all(isinstance(s, Symbol) for s in rhs), 'RHS must be a sequence of Symbol objects'
        self._lhs = lhs
        self._rhs = tuple(rhs)
        self._prob = prob


    def __eq__(self, other):
        return self._lhs == other._lhs and self._rhs == other._rhs and self._prob == other._prob

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self._lhs, self._rhs, self._prob))

    def __repr__(self):
        return '%s -> %s (%s)' % (self._lhs,
                ' '.join(str(sym) for sym in self._rhs),
                self.prob)

    def is_binary(self):
        """True if Rule is binary: A -> B C"""
        return len(self._rhs) == 2

    def is_unary(self):
        """True if Rule is unary: A -> w"""
        return len(self._rhs) == 1

    @property
    def lhs(self):
        """Returns the lhs of the rule"""
        return self._lhs

    @property
    def rhs(self):
        """Returns the rhs of the rule"""
        return self._rhs

    @property
    def prob(self):
        """Returns the probability of the rule"""
        return self._prob
