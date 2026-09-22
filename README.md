# A Phase Transition on the Third Subset Diagonal of the Avoid-or-Compress Lemma

Ryutaro Yonezu — Independent Researcher

This repository contains the paper source, compiled PDF, and an independent verifier for the third subset diagonal of the avoid-or-compress lemma.

## Main result

For synchronizing strongly connected DFAs with `|S|-|A|=3`, writing `s=|S|`, the exact worst-case value is

- `1` if `s=n`,
- `3` if `s=n-1`,
- `n-s+3` if `s<=n-2`.

The lower bounds in the last two cases are attained by binary, strongly connected, synchronizing automata.

The proper-subset construction splits by `L=n-|A| mod 3` and uses a three-token corridor with a constant-size tail defect.

## Files

- `Yonezu_2026_No18_Third_Diagonal.pdf` — compiled revised preprint.
- `Yonezu_2026_No18_Third_Diagonal.tex` — LaTeX source.
- `NO18_THIRD_DIAGONAL_VERIFY_V3.py` — independent verifier.
- `VERIFICATION_OUTPUT.txt` — summary from the default audit.
- `NO18_AUDIT_FULL.json` — per-instance audit output for all 1,680 proper-subset constructions.
- `SHA256SUMS.txt` — SHA-256 manifest.
- `CITATION.cff` — citation metadata; archival DOI to be added after publication.

## Reproduce the audit

Requirements: Python 3.9+; no external packages.

```bash
python NO18_THIRD_DIAGONAL_VERIFY_V3.py
```

Expected summary:

```json
{
  "r_range": [1, 30],
  "L_range": [5, 60],
  "cases": 1680,
  "failures": 0,
  "all_pass": true,
  "max_n": 90,
  "max_subset_states_seen": 67
}
```

The verifier checks every proper-subset construction for:

1. exact breadth-first first-success distance `L`;
2. success of the closed-form length-`L` witness;
3. strong connectivity;
4. synchronizability by the complete unordered-pair criterion;
5. the symbolic core/reset identities used in the synchronization proof.

To export the complete per-instance audit:

```bash
python NO18_THIRD_DIAGONAL_VERIFY_V3.py --json NO18_AUDIT_FULL.json
```

## Proof/computation boundary

The theorem is proved analytically in the paper. The finite computation is reproducibility support and independently checks the constructions and synchronization identities; it is not used as a substitute for the proof.

## Version

Prepared as a release candidate on 22 September 2026. The No.17 companion citation is currently linked to its GitHub v1.0.0 release and should be updated with its archival DOI when Zenodo ingestion completes.
