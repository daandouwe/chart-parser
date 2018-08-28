
class Symbol:
    """
    A symbol in a grammar.
    This class will be used as parent class for Terminal, Nonterminal.
    This way both will be a type of Symbol.
    """
    def __init__(self):
        pass


class Terminal(Symbol):
    """
    Terminal symbols are words in a vocabulary

    E.g. 'I', 'ate', 'salad', 'the'
    """

    def __init__(self, symbol: str):
        assert type(symbol) is str, 'A Terminal takes a python string, got %s' % type(symbol)
        self._symbol = symbol

    def __str__(self):
        return "'%s'" % self._symbol

    def __repr__(self):
        return 'Terminal(%r)' % self._symbol

    def __hash__(self):
        return hash(self._symbol)

    def __len__(self):
        """The length of the underlying python string"""
        return len(self._symbol)

    def __eq__(self, other):
        return type(self) == type(other) and self._symbol == other._symbol

    def __ne__(self, other):
        return not (self == other)

    def is_terminal(self):
        return True

    def is_nonterminal(self):
        return False

    @property
    def obj(self):
        """Returns the underlying python string"""
        return self._symbol


class Nonterminal(Symbol):
    """
    Nonterminal symbols are the grammatical classes in a grammar.

    E.g. S, NP, VP, N, Det, etc.
    """

    def __init__(self, symbol: str):
        assert type(symbol) is str, 'A Nonterminal takes a python string, got %s' % type(symbol)
        self._symbol = symbol

    def __str__(self):
        return "[%s]" % self._symbol

    def __repr__(self):
        return 'Nonterminal(%r)' % self._symbol

    def __hash__(self):
        return hash(self._symbol)

    def __len__(self):
        """The length of the underlying python string"""
        return len(self._symbol)

    def __eq__(self, other):
        return type(self) == type(other) and self._symbol == other._symbol

    def __ne__(self, other):
        return not (self == other)

    def is_terminal(self):
        return False

    def is_nonterminal(self):
        return True

    @property
    def obj(self):
        """Returns the underlying python string"""
        return self._symbol


class Span(Symbol):
    """
    A Span indicates that symbol was recognized between begin and end.

    Example:
        Span(Terminal('the'), 0, 1)
            This means: we found 'the' in the sentence between 0 and 1
        Span(Nonterminal('NP'), 4, 8) represents NP:4-8
            This means: we found an NP that covers the part of the sentence between 4 and 8

    Thus, Span holds a Terminal or a Nonterminal and wraps it between two integers.
    This makes it possible to distinguish between two instances of the same rule in the derrivation.
    Example:
        We can find that the rule NP -> Det N is use twice in the parse derrivation. But that in the first
        case it spans "an elephant" and in the second case it spans "my pajamas". We want to distinguis these.
        So: "an elephant" is covered by [NP]:2-4 -> [Det]:2-3 [N]:3-4
            "my pajamas" is covered by [NP]:5-7 -> [Det]:5-6 [N]:6-7

    Internally, we represent spans with tuples of the kind (symbol, start, end).
    """

    def __init__(self, symbol, start, end):
        assert isinstance(symbol, Symbol), 'A span takes an instance of Symbol, got %s' % type(symbol)
        self._symbol = symbol
        self._start = start
        self._end = end

    def __str__(self):
        """Prints Symbol with span if Symbol is Nonterminal else without (purely aesthetic distinction)"""
        if self.is_terminal():
            return "%s" % (self._symbol)
        else:
            return "%s:%s-%s" % (self._symbol, self._start, self._end)

    def __repr__(self):
        return 'Span(%r, %r, %r)' % (self._symbol, self._start, self._end)

    def __hash__(self):
        return hash((self._symbol, self._start, self._end))

    def __eq__(self, other):
        return type(self) == type(other) and self._symbol == other._symbol and self._start == other._start and self._end == other._end

    def __ne__(self, other):
        return not (self == other)

    def __len__(self):
        return len(str(self))

    def is_terminal(self):
        # a span delegates this to an underlying symbol
        return self._symbol.is_terminal()

    def root(self):
        # Spans are hierarchical symbols, thus we delegate
        return self._symbol.root()

    def obj(self):
        """The underlying python tuple (Symbol, start, end)"""
        return (self._symbol, self._start, self._end)

    def translate(self, target):
        return Span(self._symbol.translate(target), self._start, self._end)
