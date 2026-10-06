# Contributing

1. Pick an open Issue (ordered; check "Depends on").
2. Branch `issue-N-short-name`; commits reference `#N`.
3. New dynamics need unit tests anchored to an exact solution (the sin^2
   Rabi limit and the e^{-2 gamma t} coherence decay are the templates).
4. Google-style docstrings with the defining formula in each public
   function.
5. `pytest` must be green before PR.
6. Keep the "no physical quantum-brain claim" phrasing in all docs; the
   model is a probabilistic dynamical system for behaviour.
