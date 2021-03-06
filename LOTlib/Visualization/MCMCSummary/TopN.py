import collections

from LOTlib.Miscellaneous import logsumexp, qq
from LOTlib.Visualization.MCMCSummary import MCMCSummary
from LOTlib.Utilities.FiniteBestSet import FiniteBestSet


class TopN(MCMCSummary):
    """
    This "summary" uses a FiniteBestSet to store the top N

    It replaces where we previously used a FiniteBestSet
    """

    def __init__(self, N=1000, key='posterior_score', thin=1):
        self.__dict__.update(locals())
        self.fbs = FiniteBestSet(N=N, key=key)
        self.count = 0

    def add(self, h):

        self.count += 1

        if self.count % self.thin == 0:
            self.fbs.add(h)

    def get_all(self, sorted=False):
        for h in self.fbs.get_all(sorted=sorted):
            yield h

    def __iter__(self):
        for h in self.fbs.get_all():
            yield h

    def Z(self):
        """
        Normalizer of everything
        """
        return logsumexp([h.posterior_score for h in self.get_all(sorted=False)])

    def normalize(self, d):
        """
        Change the posterior_score on hypotheses so they sum to 1
        """
        Z = self.Z()
        for h in self.fbs.get_all(sorted=False):
            h.posterior_score = h.posterior_score - Z

    def display(self):
        for h in self.get_all():
            print h.posterior_score, h.prior, h.likelihood, qq(h)

    def update(self, y):
        if isinstance(y, TopN):
            assert y.key == self.key
            for h in y.fbs.get_all(sorted=False):
                self.add(h)
        elif isinstance(y, collections.Iterable):
            for yi in y:
                self.update(yi)
        elif isinstance(y, FiniteBestSet):
            self.fbs.merge(y)
        else:
            raise NotImplementedError
