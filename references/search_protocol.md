# Search Protocol

Stage 1 requires both live web evidence and structured scholarly API search.

## Required sources

Core structured sources:

- OpenAlex
- Semantic Scholar
- Crossref

Conditional structured sources:

- PubMed / NCBI E-utilities for biomedical, health, clinical, or psychology topics.
- arXiv and Papers with Code for AI, computer science, modeling, or benchmark topics.
- ERIC for education topics.
- ClinicalTrials.gov for clinical intervention or trial topics.

Live web evidence:

- current datasets;
- standards and guidelines;
- tool or benchmark documentation;
- institutional or policy documents;
- recent grey literature;
- pages not represented well in scholarly APIs.

## Required artifacts

- `live_web_sources.json`
- `search_manifest.json`
- `raw_results.jsonl`
- `normalized_sources.jsonl`
- `scored_sources.jsonl`
- `evidence_matrix.csv`

## Claim standard

Use scoped claims only. A gap claim is limited to the recorded search scope until domain databases, citation chasing, and full-text inspection have been added.
