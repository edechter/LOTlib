"""
Defines different classes for different types of data and models.

It also provides "Obj"s for bundling together features

For functions, we have a data object of the form [output, args]

"""
from copy import deepcopy

from LOTlib.Miscellaneous import weighted_sample, qq


# ------------------------------------------------------------------------------------------------------------

class FunctionData:
    """
    This is a nicely wrapped kind of data--if we give it to a FunctionHypothesis, it knows to extract the
    "input" (NOT the output) and run those on FunctionHypothesis.value(*input) so when you have functional
    hypotheses, this is a convenient form of data

    """
    def __init__(self, input, output, **kwargs):
        """Creates a new FunctionData object; input must be either a list or a tuple."""
        # Since we apply to this, it must be a list
        assert isinstance(input, list) or isinstance(input, tuple), "FunctionData.input must be a list!"
        self.input = input
        self.output = output
        self.__dict__.update(kwargs)

    def __repr__(self):
        return '<' + ','.join(map(str, self.input)) + " -> " + str(self.output) + '>'


# ------------------------------------------------------------------------------------------------------------

class UtteranceData:
    """A wrapper for utterances.

    An utterance data point is a word, in a context, with some set of possible words we could have said.

    """
    def __init__(self, utterance, context, possible_utterances):
        """Creates a new Utterance.

        Arguments:
            utterance (doc?): the word that's spoken
            context (doc?): the environmental/linguistic context in which the word is spoken
            possible_utterances (doc?): a set of other words we could have spoken, given the context

        """
        self.__dict__.update(locals())

    def __repr__(self):
        return qq(str(self.utterance))+' in '+ str(self.context) + " from " + str(self.possible_utterances)


# ------------------------------------------------------------------------------------------------------------

class Obj:
    """ Represent bundles of features"""

    def __init__(self, **f):
        for k, v in f.iteritems():
            setattr(self, k, v)

    def __str__(self):
        outstr = '<OBJECT: '
        for k, v in self.__dict__.iteritems():
            outstr = outstr + str(k) + '=' + str(v) + ' '
        outstr = outstr + '>'
        return outstr

    def __repr__(self): # used for being printed in lists
        return str(self)

    # We may or may not want these, depending on whether we keep Objs in sets...
    #def __eq__(self, other): return str(self) == str(other)
    #def __hash__(self): return hash(str(self))


def make_all_objects(**f):
    """This takes a list of lists and crosses them into all objects.

    Example:
        >>> make_all_objects(size=[1,2,3], color=['red', 'green', 'blue'])
        ### Returns a list of 9 (3x3) objects, each with a different pair of size and color attributes.

    """

    keys = f.keys()
    out_objs = []

    for vi in f[keys[0]]:
        out_objs.append(Obj( **{keys[0]: vi} ))

    for i in range(1, len(keys)): # for every other key
        newout = []
        for o in out_objs:
            for vi in f[keys[i]]:
                ok = deepcopy(o)
                setattr(ok, keys[i], vi)
                newout.append(ok)
        out_objs = newout

    return out_objs


def sample_sets_of_objects(N, objs):
    """
    Makes a set of size N appropriate to using "set" functions on -- this means it must contain copies, not duplicate references
    """
    s = weighted_sample(objs, N=N, returnlist=True) # the set of objects
    return map(deepcopy, s) # the set must NOT be just the pointers sampled, since then set() operations will collapse them!


# ------------------------------------------------------------------------------------------------------------

class Context:
    """
    A context stores a list of objects and list of N-ary relations, represented as tuples,
    as in relations = [  (happy, john), (loved, mary, john) ], with (function, *args)

    Then in a grammar, you can have a terminal like context.relation_('parent', 'barak', 'sasha')

    """
    def __init__(self, objects, relations):
        self.objects = objects
        self.relations = set(relations)

    def relation_(self, *args):
        return tuple(args) in self.relations