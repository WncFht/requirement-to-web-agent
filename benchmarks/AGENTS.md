# Benchmark snapshots

`arc-bench/<date>/` holds byte-preserved official platform inputs, public assertions and source artifacts. Its manifest records source URLs, hashes, availability gaps and separately labeled local audits. Do not format, weaken, silently refresh or execute upstream contents. Update a snapshot only through an explicit import with provenance; preserve the old snapshot when the source changes.

Binary archives use Git LFS. Keep credentials, private profiles, submissions and run outputs outside this tree. Materialize inputs and external acceptance into separate ignored directories using `scripts/platform_materials.py`; never pass external assertions into model context. A collected suite is not a passed suite, and public tests are not the hidden platform evaluator.
