from LOTlib.Hypotheses.RecursiveLOTHypothesis import RecursiveLOTHypothesis
from LOTlib.Miscellaneous import log, Infinity, log1mexp
from LOTlib.Evaluation.EvaluationException import EvaluationException

# ============================================================================================================
#  Define a class for running MH

ALPHA = 0.75    # the probability of uttering something true
GAMMA = -30.0   # the log probability penalty for recursion
LG_1MGAMMA = log1mexp(GAMMA)
MAX_NODES = 50  # How many FunctionNodes are allowed in a hypothesis? If we make this 20, things may slow

class NumberExpression(RecursiveLOTHypothesis):
    
    def __init__(self, grammar, value=None, f=None, proposal_function=None, args=['x'], **kwargs):
        RecursiveLOTHypothesis.__init__(self, grammar, value=value, proposal_function=proposal_function, args=['x'], **kwargs)

    def __call__(self, *args):
        try:
            return RecursiveLOTHypothesis.__call__(self, *args)
        except EvaluationException: # catch recursion and too big
            return None

    def compute_prior(self):
        """Compute the number model prior.

        Log_probability() with a penalty on whether or not recursion is used.

        """
        if self.value.count_nodes() > MAX_NODES:
            self.prior = -Infinity
        else:
            if self.value.contains_function(self.recurse):
                recursion_penalty = GAMMA
            else:
                recursion_penalty = LG_1MGAMMA

            self.prior = (recursion_penalty + self.value.log_probability()) / self.prior_temperature

        self.update_posterior()

        return self.prior

    def compute_single_likelihood(self, datum):
        """Computes the likelihood of data.

            TODO: Make sure this precisely matches the number paper.

        """

        response = self(*datum.input)
        if response == 'undef' or response == None:
            return log(1.0/10.0) # if undefined, just sample from a base distribution
        else:
            return log((1.0 - ALPHA)/10.0 + ALPHA * (response == datum.output))

