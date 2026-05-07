# CiteRoots-Endorsement Consent Protocol

This document describes what authors saw, what they consented to, and what is and is not redistributed in the released CiteRoots-Endorsement layer.

## Outreach protocol

Authors of recently-published scientific papers were contacted via the email address listed on their public S2ORC author profile or on the focal paper itself. Each contacted author was sent:

1. The title and corpusid of one of their own recent papers (the "focal paper").
2. A brief description of the research project: building a benchmark to evaluate AI systems on prospective intellectual-roots prediction.
3. A request to identify which prior works they regarded as generative inspirations for the focal paper, with optional free-text rationales.
4. An explicit statement of what their response would be used for and how it would be redistributed.

Authors who did not respond, who declined to participate, or who responded with a request to opt out at any later point are excluded from the released cohort.

## Consent statement (as shown to authors)

The following consent statement was presented to every contacted author, in writing:

> Your responses will be used to construct a public research benchmark for AI-driven scientific literature retrieval. The benchmark will be released under a permissive academic license. We will redistribute only the structured outcome of your response — specifically, which prior works you identified as generative inspirations, in the form of paper-identifier pairs (focal paper → inspiration paper). We will NOT redistribute your free-text rationales, your email address, your name beyond what is already publicly listed in the S2ORC author tables, or any other personally identifying information. You may withdraw your consent at any time before publication, and we will exclude your responses from the released cohort upon request.

## What authors consented to redistribute

- Paper-identifier pairs `(focal_corpusid, candidate_corpusid)` where the candidate was identified as a generative inspiration.
- Aggregate statistics over their responses (counts per field, year, journal family — never individually identifiable).
- A coarse audit verdict per pair, indicating whether the pair passed our review for review-paper status, self-citation conflict, and consent.

## What authors did NOT consent to redistribute, and is therefore excluded

- Free-text rationales describing why a particular prior work was inspirational.
- Free-text descriptions of non-paper inspirations (collaborators, experimental observations, clinical needs, etc.).
- Email addresses, phone numbers, or any other contact information.
- Author names beyond what is already publicly listed in the S2ORC author tables.
- Any internal review notes, our adjudication conversations, or workbench logs.

## Audit and human review

Every author response was reviewed by a human annotator before entering the released cohort. The review applied three filters:

1. **Review-paper filter**: focal papers identified as commentary, review, or editorial were excluded from the released non-review cohort, since those papers do not have generative-inspiration semantics in the same way as primary research.
2. **Self-citation filter**: candidate papers where the citing-paper authors and the cited-paper authors substantially overlapped were flagged via an `eligibility_flag` so downstream users can choose whether to include them.
3. **Consent filter**: any pair where the author later requested removal was excluded.

The released parquet `endorsement_pairs.parquet` carries the audit verdict per pair so downstream users can apply additional filters as desired.

## What is in the released artifact

The released `endorsement_pairs.parquet` schema:

| Column | Type | Description |
|--------|------|-------------|
| `focal_corpusid` | int64 | S2ORC corpusid of the citing (focal) paper |
| `candidate_corpusid` | int64 | S2ORC corpusid of the cited (inspiration) paper |
| `audit_status` | string | Verdict from human review: `passed`, `flagged_self_cite`, `flagged_review_paper`, `excluded` |
| `eligibility_flags` | list[string] | Detailed flags for downstream filtering |
| `is_context_linked` | bool | Whether the pair is in the 435-pair context-linked subset |
| `is_retrieval_evaluable` | bool | Whether the pair is in the 402-pair retrieval-evaluable subset |
| `field_family` | string | Coarse field family of the focal paper (Biology, CS, Medicine, Engineering, Chemistry, Other) |

No free-text columns. No author-identifying columns beyond what `corpusid` indirectly exposes via S2ORC's public author tables.

## Maintenance

If an author requests post-publication removal of their data, we will:

1. Remove the relevant rows from the released parquet.
2. Cut a new patch release with a new version number (see `MAINTENANCE.md`).
3. Update the CHANGELOG to document the removal (without identifying the requestor or the specific rows).

This protocol matches the spirit of GDPR Article 17 (right to erasure) and remains available indefinitely.

## Contact

Anonymized at submission. See `MAINTENANCE.md` for the post-submission contact protocol.
