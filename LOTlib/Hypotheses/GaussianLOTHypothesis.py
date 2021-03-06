from LOTHypothesis import LOTHypothesis
from LOTlib.Miscellaneous import Infinity, normlogpdf
from copy import copy, deepcopy
from math import isnan

class GaussianLOTHypothesis(LOTHypothesis):
    """
            Like LOTHypothesis but has a Gaussian likelihood
    """

    def __init__(self, grammar, value=None, f=None, prior_temperature=1.0, **kwargs):
        self.__dict__.update(locals()) # must come first or else proposal_function is overwritten
        LOTHypothesis.__init__(self, grammar, value=value, f=f,  **kwargs)


    def compute_single_likelihood(self, datum):
        """ Compute the likelihood with a Gaussian. Wraps to avoid nan"""
        
        ret = normlogpdf(self(*datum.input), datum.output, datum.ll_sd)
        
        if isnan(ret):
            return -Infinity
        else:
            return ret
