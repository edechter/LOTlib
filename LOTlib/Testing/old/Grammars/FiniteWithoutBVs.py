"""
        A small finite grammar without bound variables.
"""


from LOTlib.Grammar import Grammar
import math

g = Grammar()

g.add_rule("START", "S", ["NP", "VP"], 1)
g.add_rule("NP", "NP", ["det", "N"], 1)
g.add_rule("VP", "VP", ["V", "NP"], 1)
g.add_rule("det", "the", None, 1)
g.add_rule("det", "a", None, 1)
g.add_rule("N", "cat", None, 1)
g.add_rule("N", "human", None, 1)
g.add_rule("V", "likes", None, 1)
g.add_rule("V", "kills", None, 1)
g.add_rule("V", "eats", None, 1)


def log_probability(tree):
    # every tree has an equal probability of being generated
    return math.log(0.5*0.5*(1.0/3)*0.5*0.5)


if __name__ == "__main__":
    for i in xrange(100):
        print(g.generate())
