# MUSES Release — Maintenance Plan

This document describes how the MUSES release will be maintained over time. It is required by the NeurIPS 2026 Evaluations & Datasets track hosting guidelines.

## Versioning

The release follows [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version increments for breaking schema changes, breaking-cohort-redefinitions, or any change that invalidates previously-reported headline numbers.
- **MINOR** version increments for additive changes: new dataset slices, new prediction baselines, expanded endorsement cohort, additional rhetorical labels, new judge releases.
- **PATCH** version increments for non-substantive corrections: documentation fixes, file-format normalization, broken-link repairs, schema-non-breaking erratum corrections.

This release is **`v1.0.0`**. Subsequent releases will be tagged on the GitHub repository and surfaced as separate HuggingFace dataset/model revisions.

## Release cadence

- We commit to keeping this release publicly available for at least **5 years** from the camera-ready date.
- Patch releases will be cut as needed, typically within 30 days of a confirmed issue.
- Minor releases will be cut roughly every 6–12 months as the endorsement cohort and judge are updated.
- A major release would only be cut for a structural redefinition of the benchmark; we do not anticipate one within the first 24 months.

## Erratum protocol

If a user identifies a defect in the release (e.g., a corpusid that should not be in the candidate pool, a label-aggregation bug, an endorsement pair that fails the audit retroactively):

1. **Report**: open an issue on the GitHub repository (URL in `RELEASE_INVENTORY.md`).
2. **Triage**: maintainers acknowledge within 14 days; substantive issues triaged within 30 days.
3. **Fix**: the fix is staged on a branch, validated with the released eval scripts, and merged.
4. **Patch release**: a new patch version is cut on the same week as the merge; the CHANGELOG documents the fix.
5. **Notification**: HuggingFace dataset/model card revisions are bumped; subscribers to the GitHub repo see a release notification.

For changes that materially affect headline numbers, we additionally publish a public erratum referencing the change.

## Right-to-erasure protocol

If an author who participated in the CiteRoots-Endorsement workbench requests post-publication removal of their data:

1. The relevant `(focal_corpusid, candidate_corpusid)` rows are removed from `endorsement_pairs.parquet`.
2. A new patch release is cut.
3. The CHANGELOG documents the removal *without* identifying the requestor or the specific rows (to avoid disclosure-by-omission).
4. Cohort statistics are recomputed and the corresponding aggregate files are updated.

This protocol matches the spirit of GDPR Article 17 and remains available indefinitely.

## Long-term hosting

| Asset | Primary host | Secondary mirror |
|-------|--------------|------------------|
| MUSES dataset (identifier files) | HuggingFace Hub | Zenodo (archival snapshot at major releases) |
| CiteRoots dataset (label files) | HuggingFace Hub | Zenodo (archival snapshot at major releases) |
| Distilled judge weights | HuggingFace Hub | (not mirrored — base model lives on HF anyway) |
| Code repository | GitHub | Software Heritage (automatic archival) |
| Datasheet, license, maintenance | GitHub + each HF entity | Same as code repo |

If HuggingFace becomes unavailable for any reason, we will mirror the dataset entities on a comparable open-data platform (Zenodo, OSF, or a successor) within 90 days and update the canonical URLs.

## Contact

Anonymized at submission. The post-submission contact will be:

- **Issue tracker**: GitHub issues on the canonical repository
- **Email**: a maintainer-team alias to be set up at de-anonymization
- **Office-hours channel**: a recurring open-office-hours slot on a community Discord/Slack to be set up at de-anonymization

## Backwards compatibility

We commit to never silently changing the schema of any released parquet within a major version. Schema additions (new columns) are MINOR-version events. Schema removals or column-type changes are MAJOR-version events.

The split definitions (`instance_splits.parquet`) are frozen at v1.0.0 and will not change within the v1.x series, so reproducibility of headline numbers is guaranteed across patch and minor releases.

## Citation

When citing this dataset, please cite the version you used. At de-anonymization we will add a `CITATION.cff` file to the code repository with versioned citation entries.

## License

See `LICENSE.md`.
