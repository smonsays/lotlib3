
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from lotlib3.DataAndObjects import FunctionData

def make_data(size=1, alpha=0.99):
    return [FunctionData(input=['aaaa'], output=True, alpha=alpha),
            FunctionData(input=['aaab'], output=False, alpha=alpha),
            FunctionData(input=['aabb'], output=False, alpha=alpha),
            FunctionData(input=['aaba'], output=False, alpha=alpha),
            FunctionData(input=['aca'], output=True, alpha=alpha),
            FunctionData(input=['aaca'], output=True, alpha=alpha),
            FunctionData(input=['a'], output=True, alpha=alpha)] * size

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from lotlib3.Grammar import Grammar

grammar = Grammar()

grammar.add_rule('START', '', ['EXPR'], 1.0)

grammar.add_rule('EXPR', '(%s*)', ['EXPR'], 1.0)
grammar.add_rule('EXPR', '(%s?)', ['EXPR'], 1.0)
grammar.add_rule('EXPR', '(%s+)', ['EXPR'], 1.0)
grammar.add_rule('EXPR', '(%s|%s)', ['EXPR', 'EXPR'], 1.0)
grammar.add_rule('EXPR', '%s%s', ['TERMINAL', 'EXPR'], 5.0)
grammar.add_rule('EXPR', '%s', ['TERMINAL'], 5.0)

for v in 'abc.':
    grammar.add_rule('TERMINAL', v, None, 1.0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from lotlib3.FunctionNode import isFunctionNode
from lotlib3.Hypotheses.LOTHypothesis import LOTHypothesis
from lotlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood
from lotlib3.Eval import EvaluationException
import re

class MyHypothesis(BinaryLikelihood, LOTHypothesis):
    """Define a special hypothesis for regular expressions.

    This requires overwriting compile_function to use our custom interpretation model on trees -- not just
    simple eval.
    """

    def __init__(self, **kwargs):
        LOTHypothesis.__init__(self, grammar, **kwargs)

    def compile_function(self):
        c = re.compile(str(self.value))
        return (lambda s: (c.match(s) is not None))

    def __str__(self):
        return str(self.value)

    def __call__(self, *args):
        try:
            return LOTHypothesis.__call__(self, *args)
        except EvaluationException:
            return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    from lotlib3 import break_ctrlc
    from lotlib3.Miscellaneous import qq
    from lotlib3.TopN import TopN
    from lotlib3.Samplers.MetropolisHastings import MetropolisHastingsSampler

    h0   = MyHypothesis()
    data = make_data()
    top  = TopN(N=10)
    thin = 100

    for i, h in enumerate(break_ctrlc(MetropolisHastingsSampler(h0, data))):

        top << h

        if i % thin == 0:
            print("#", i, h.posterior_score, h.prior, h.likelihood, qq(h))

    for h in top:
        print(h.posterior_score, h.prior, h.likelihood, qq(h))