#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any

from _common import extract_idea, output_dir_from_args, read_csv_dicts, read_text, write_text


def infer_fit(report: str) -> str:
    for label in [
        "Highly covered",
        "Partially covered",
        "Adjacent but not direct",
        "Sparse evidence",
        "Infeasible under current resources",
        "Needs data-first redesign",
    ]:
        if label in report:
            return label
    return "Adjacent but not direct"


def topic_set(idea: str, fit: str) -> list[dict[str, Any]]:
    base = idea or "the supplied research idea"
    if fit == "Highly covered":
        return [
            {
                "title": f"External-validation and calibration redesign of {base}",
                "one_sentence": "Turn the crowded topic into a validation, calibration, fairness, or decision-utility study.",
                "object": "The existing model, phenomenon, or intervention in a new dataset, local context, or subgroup.",
                "unit": "Individual records, papers, organizations, cases, or observations depending on the domain.",
                "basis": "Highly similar studies indicate the original version is too close to existing work.",
                "difference": "Novelty depends on local data, external validation, calibration, subgroup fairness, decision utility, or replication quality.",
                "data": "A local/public external dataset with the same target outcome plus enough metadata for validation and subgroup checks.",
                "method": "Transparent baseline model or replication protocol; external validation; calibration; discrimination metric; decision or utility analysis; error audit.",
                "tools": "Python/R, scikit-learn or statsmodels, R rms/caret/tidymodels, spreadsheet evidence matrix, reproducible notebook.",
                "first_step": "Take the top 5 closest studies, extract their target, predictors, sample, and metrics, then define exactly what your external validation changes.",
                "failure": "Fails if no independent dataset exists or if the validation context is not meaningfully different from prior work.",
                "mvp": "Replicate the baseline metric from one closest study on a small external/public dataset and report calibration or error differences.",
                "risk": "Medium: depends on a usable external dataset and careful reporting.",
                "output": "Method paper, validation study, thesis chapter, or applied domain paper.",
                "scores": {"feasibility": 4, "gap": 3, "data": 3, "method_fit": 5, "risk_control": 4},
            },
            {
                "title": f"Data-availability-first MVP for {base}",
                "one_sentence": "Start from the most reliable obtainable dataset and narrow the research question around it.",
                "object": "The subset of the phenomenon for which real data can be obtained now.",
                "unit": "Observable cases in public, institutional, registry, survey, or document data.",
                "basis": "Crowded topics often fail because they chase novelty before data feasibility.",
                "difference": "The contribution becomes feasibility, data construction, transparent measurement, and scoped inference rather than broad novelty.",
                "data": "Public, institutional, registry, survey, or document data that can be obtained within the project timeline.",
                "method": "Descriptive evidence map, data dictionary, missingness audit, baseline analysis, and minimal predictive or explanatory model.",
                "tools": "Python/R, OpenRefine if data cleaning is heavy, pandas, basic regression or thematic coding tools.",
                "first_step": "List 3 realistic data sources, rank them by access/coverage/measurement validity, and build a 20-row pilot table.",
                "failure": "Fails if the available data cannot measure the core outcome or only supports trivial descriptive claims.",
                "mvp": "One cleaned pilot dataset, one outcome definition, one baseline analysis, and one feasibility paragraph.",
                "risk": "Low to medium: less ambitious but more executable.",
                "output": "Pilot study, data paper, proposal, or preregistered MVP.",
                "scores": {"feasibility": 5, "gap": 3, "data": 5, "method_fit": 4, "risk_control": 5},
            },
            {
                "title": f"Mechanism-focused extension of {base}",
                "one_sentence": "Shift from whether the phenomenon exists to how and under what conditions it operates.",
                "object": "The mechanism linking the focal exposure to an outcome, with boundary conditions.",
                "unit": "Participants, organizations, documents, events, or time periods with measurable mechanism indicators.",
                "basis": "Existing studies may cover the association but leave mechanism, mediation, moderation, or context underexplained.",
                "difference": "The gap is a mechanism, mediator, moderator, or boundary condition not fully explained by prior work.",
                "data": "Survey/interview/longitudinal or mixed-method evidence with theory-linked constructs.",
                "method": "Mediation/moderation, SEM, mixed methods, or qualitative mechanism tracing.",
                "tools": "R lavaan, Python statsmodels, NVivo/Taguette/Excel coding, interview protocol, validated scales when available.",
                "first_step": "Extract mechanism variables from the closest literature and decide which one is observable in your setting.",
                "failure": "Fails if mechanism variables cannot be measured or if theory only decorates the study without changing design.",
                "mvp": "A small construct map plus 5-10 pilot interviews or a short survey validating whether the mechanism is plausible.",
                "risk": "Medium: measurement quality and theory fit matter.",
                "output": "Mechanism paper, theory-informed empirical study, or proposal.",
                "scores": {"feasibility": 3, "gap": 5, "data": 3, "method_fit": 4, "risk_control": 3},
            },
        ]
    if fit == "Needs data-first redesign":
        return [
            {
                "title": f"Public-data MVP for {base}",
                "one_sentence": "Shrink the unit of analysis to cases with observable public or collectable data.",
                "object": "The observable subset of the intended population or system.",
                "unit": "Publicly documented cases, firms, cities, papers, records, or reports.",
                "basis": "The original idea implies broad or future-looking data that may not be directly observable.",
                "difference": "The project becomes executable by replacing unavailable universe-level data with traceable proxies.",
                "data": "Listed-company data, public reports, city/industry aggregates, ESG disclosures, platform records, or manually sampled cases.",
                "method": "Data inventory, proxy validation, descriptive modeling, and robustness checks against alternative proxies.",
                "tools": "Python pandas, spreadsheet data dictionary, public APIs or manual scraping where legal, simple regression/visual audit.",
                "first_step": "Create a data-source table with access route, unit, time coverage, variable availability, and proxy validity.",
                "failure": "Fails if proxies do not represent the outcome or if source coverage is systematically biased without correction.",
                "mvp": "30-100 observable cases, one defensible proxy outcome, one descriptive model, and one proxy sensitivity check.",
                "risk": "Medium: proxy validity must be defended.",
                "output": "MVP empirical paper, dataset note, feasibility report, or proposal.",
                "scores": {"feasibility": 5, "gap": 3, "data": 5, "method_fit": 4, "risk_control": 4},
            },
            {
                "title": f"Scenario simulation for {base}",
                "one_sentence": "Use transparent assumptions to simulate plausible future scenarios instead of claiming exact prediction.",
                "object": "A future-facing system where exact labels are unavailable but scenario drivers can be specified.",
                "unit": "Scenario-year, organization-year, region-year, or simulated agent depending on the domain.",
                "basis": "Future prediction is often infeasible without labels; scenario modeling can still support decisions.",
                "difference": "Novelty depends on assumption transparency, sensitivity analysis, and stakeholder-useful scenarios.",
                "data": "Historical public indicators, policy targets, industry-level statistics, and scenario assumptions.",
                "method": "Baseline projection, scenario modeling, sensitivity analysis, uncertainty bands, and assumption audit.",
                "tools": "Python/R simulation notebook, Monte Carlo sampling, simple system dynamics, scenario tables.",
                "first_step": "Define 3 scenarios: baseline, optimistic, pessimistic; then identify the drivers and ranges for each.",
                "failure": "Fails if assumptions are hidden or the output is presented as prediction rather than scenario reasoning.",
                "mvp": "One transparent model with 3 scenarios, one sensitivity plot, and a limitations section.",
                "risk": "Medium to high: assumptions must not be overclaimed.",
                "output": "Policy-style modeling paper, decision-support report, or proposal.",
                "scores": {"feasibility": 4, "gap": 4, "data": 3, "method_fit": 4, "risk_control": 3},
            },
            {
                "title": f"Data-quality audit for {base}",
                "one_sentence": "Evaluate what data exists, what is missing, and which claims are supportable.",
                "object": "The data ecosystem around the research problem.",
                "unit": "Datasets, repositories, reports, platforms, or institutions.",
                "basis": "When data feasibility is unclear, a data-readiness audit prevents false modeling ambition.",
                "difference": "The contribution is a feasibility and evidence-readiness map.",
                "data": "Catalog of public, commercial, institutional, and manually collectable data sources.",
                "method": "Scoping review, data source audit, variable coverage matrix, and MVP recommendation.",
                "tools": "Spreadsheet evidence matrix, OpenAlex/Semantic Scholar, public dataset portals, manual source audit.",
                "first_step": "Build a matrix of sources x variables x access constraints x measurement quality.",
                "failure": "Fails if it stops at description and does not produce a decision rule for what can be studied next.",
                "mvp": "10-20 data sources classified by access, validity, coverage, and recommended use.",
                "risk": "Low: less glamorous but useful before modeling.",
                "output": "Scoping/data feasibility paper or project prospectus.",
                "scores": {"feasibility": 5, "gap": 2, "data": 5, "method_fit": 3, "risk_control": 5},
            },
        ]
    return [
        {
            "title": f"Mechanism explanation study of {base}",
            "one_sentence": "Explain the pathway linking the focal phenomenon to the outcome instead of only testing association.",
            "object": "The mechanism by which the focal phenomenon changes behavior, performance, perception, or system outcomes.",
            "unit": "People, papers, cases, organizations, events, or records depending on the domain.",
            "basis": "Adjacent literature exists, but the exact mechanism/context combination is not fully direct in this run.",
            "difference": "The contribution is the mechanism chain and boundary conditions in a specific context.",
            "data": "Survey, interview, process logs, documents, or mixed-method evidence aligned with constructs.",
            "method": "Theory-guided construct design, mediation/moderation, SEM, qualitative mechanism tracing, or mixed methods.",
            "tools": "Survey tool, interview guide, coding sheet, R lavaan/statsmodels, qualitative coding software if needed.",
            "first_step": "Write a mechanism chain with 3 variables: input, mechanism, outcome; then check whether each can be measured.",
            "failure": "Fails if variables are slogans rather than measurable constructs or if mechanism is inferred without evidence.",
            "mvp": "One construct map, one small pilot data collection or coding sample, and one baseline mechanism test.",
            "risk": "Medium: depends on valid measurement and enough sample or qualitative depth.",
            "output": "Empirical mechanism paper, thesis chapter, or proposal.",
            "scores": {"feasibility": 4, "gap": 5, "data": 3, "method_fit": 4, "risk_control": 3},
        },
        {
            "title": f"Evidence-map and gap-driven topic refinement for {base}",
            "one_sentence": "Convert the initial idea into a scoped evidence map and a sharply bounded research question.",
            "object": "The literature, concepts, methods, and data sources surrounding the idea.",
            "unit": "Published studies, datasets, guidelines, tools, or project reports.",
            "basis": "When direct evidence is unclear, an evidence map prevents arbitrary topic design.",
            "difference": "Novelty is provisional and comes from the exact population, context, outcome, and method combination.",
            "data": "Published literature plus optional small expert/user validation sample.",
            "method": "Scoping review, evidence matrix, bibliometric or thematic synthesis, gap taxonomy.",
            "tools": "OpenAlex/Semantic Scholar/Crossref, Zotero, spreadsheet matrix, VOSviewer or bibliometrix if needed.",
            "first_step": "Define inclusion/exclusion rules and classify 20-50 papers by object, method, theory, data, and gap.",
            "failure": "Fails if it becomes a summary rather than a decision map for selecting an executable project.",
            "mvp": "20-paper evidence matrix, gap taxonomy, and one prioritized research question.",
            "risk": "Low: strong starting point when direct evidence is unclear.",
            "output": "Scoping review, grant background, or thesis proposal chapter.",
            "scores": {"feasibility": 5, "gap": 3, "data": 5, "method_fit": 4, "risk_control": 5},
        },
        {
            "title": f"Minimal predictive or classification model for {base}",
            "one_sentence": "Build a modest model only after defining a realistic target, features, and baseline.",
            "object": "A measurable target outcome derived from records, text, surveys, logs, or public datasets.",
            "unit": "Record, person, document, event, organization, or time unit with features and labels.",
            "basis": "Modeling is viable only if labels, features, and evaluation criteria exist.",
            "difference": "Contribution depends on a meaningful target, transparent baseline, interpretability, and error analysis.",
            "data": "Public dataset, curated corpus, survey records, logs, or institutional data with a clear target label.",
            "method": "Baseline model, cross-validation, interpretable model comparison, error analysis, and robustness checks.",
            "tools": "Python, pandas, scikit-learn, statsmodels, SHAP if justified, reproducible notebook.",
            "first_step": "Define target Y, feature groups X, baseline rule, and one metric before choosing any complex model.",
            "failure": "Fails if the target label is vague, sample size is too small, or model performance has no meaningful baseline.",
            "mvp": "One cleaned dataset, one baseline model, one candidate model, one error analysis table.",
            "risk": "Medium: modeling is only viable if labels and features exist.",
            "output": "Applied modeling paper, prototype, or reproducible analysis package.",
            "scores": {"feasibility": 3, "gap": 3, "data": 2, "method_fit": 4, "risk_control": 2},
        },
    ]


def weighted_score(item: dict[str, Any]) -> float:
    scores = item.get("scores", {})
    weights = {"feasibility": 0.30, "gap": 0.25, "data": 0.20, "method_fit": 0.15, "risk_control": 0.10}
    return sum(float(scores.get(k, 0)) * w for k, w in weights.items())


def choose_default(topics: list[dict[str, Any]]) -> int:
    if not topics:
        return 1
    return max(range(len(topics)), key=lambda i: weighted_score(topics[i])) + 1



def topic_value(item: dict[str, Any], key: str, default: str) -> str:
    return str(item.get(key) or default).strip()


def core_gap(item: dict[str, Any], fit: str) -> str:
    if "Highly covered" in fit:
        return "The core gap is not a vague new topic; it is external validation, context transfer, measurement improvement, mechanism explanation, or data-quality improvement."
    if "data-first" in fit.lower() or "Needs data" in fit:
        return "The core gap is measurable data, proxy validity, data quality, and a reproducible minimum unit of analysis."
    return "Adjacent research exists, but the object-context-mechanism-data-method combination is not highly directly covered within the current search scope."


def data_acquisition(item: dict[str, Any]) -> str:
    data = topic_value(item, "data", "public data, pilot survey/interview data, or literature evidence matrix")
    lower = data.lower()
    if any(token in lower for token in ["public", "api", "registry", "reports", "dataset", "openalex", "semantic"]):
        return "Use public databases, official APIs, public reports, paper metadata, or auditable web documents first; collect a 20-50 item pilot sample before scaling."
    if any(token in lower for token in ["survey", "interview", "questionnaire", "participant"]):
        return "Draft a small survey, interview protocol, or coding sheet first; check ethics/consent requirements before expanding the sample."
    return "List available sources, access constraints, units, variables, and missing-data risk before upgrading to statistical modeling."


def advanced_method(item: dict[str, Any]) -> str:
    method = topic_value(item, "method", "baseline analysis")
    lower = method.lower()
    if any(token in lower for token in ["mediation", "moderation", "sem", "mechanism"]):
        return "Can upgrade to SEM, mediation/moderation, mixed methods, or multilevel modeling if construct measurement is reliable."
    if any(token in lower for token in ["model", "classification", "prediction", "regression", "predictive"]):
        return "Can upgrade to regularized regression, tree models, gradient boosting, calibration assessment, or interpretability analysis after a transparent baseline is built."
    if any(token in lower for token in ["scoping", "bibliometric", "evidence", "review", "synthesis"]):
        return "Can upgrade to bibliometric networks, topic modeling, co-word analysis, or expert validation without weakening inclusion/exclusion rules."
    return "Can upgrade to mixed methods, robustness checks, sensitivity analysis, or a small experiment if data reality allows."


def fallback_option(item: dict[str, Any]) -> str:
    return "If data is insufficient, downgrade to an evidence map, data-availability audit, small qualitative validation, or external-context validation. If the method is too heavy, return to descriptive statistics, content analysis, or a transparent baseline."


def evidence_summary(rows: list[dict[str, str]], n: int = 6) -> str:
    if not rows:
        return "- No matrix rows yet; run the search and matrix scripts first."
    nearest = sorted(rows, key=lambda row: float(row.get("similarity_score") or 0), reverse=True)[:n]
    return "\n".join(
        f"- {row.get('id')}: {row.get('title')} ({row.get('year')}) - {row.get('similarity_class')}, score {row.get('similarity_score')}"
        for row in nearest
    )


def format_rows(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "- No structured-search records in this bucket yet; supplement with live web search, citation chasing, or domain databases."
    return "\n".join(
        f"- {row.get('id')}: {row.get('title')} ({row.get('year')}, {row.get('source_database')}) "
        f"- {row.get('similarity_class')}, score {row.get('similarity_score')}"
        for row in rows
    )


def evidence_buckets(rows: list[dict[str, str]]) -> str:
    if not rows:
        empty = "- No matrix rows yet; run the search and matrix scripts first."
        return f"""### Highly similar
{empty}

### Adjacent research
{empty}

### Method/theory borrowing candidates
{empty}
"""
    high = [row for row in rows if row.get("similarity_class") in {"highly similar", "close adjacent"}]
    adjacent = [row for row in rows if row.get("similarity_class") in {"adjacent", "background"}]
    method_theory = [
        row
        for row in rows
        if any((row.get(field) or "").lower() not in {"", "not clear from metadata", "not explicit in metadata"} for field in ["method", "model", "theory"])
    ]
    return f"""### Highly similar
{format_rows(high[:5])}

### Adjacent research
{format_rows(adjacent[:5])}

### Method/theory borrowing candidates
{format_rows(method_theory[:5])}
"""


def render_topic(index: int, item: dict[str, Any], fit: str) -> str:
    score = weighted_score(item)
    return f"""## Topic {index}

Title: {item['title']}

One-sentence idea: {item['one_sentence']}

Research object: {item['object']}

Unit of analysis: {item['unit']}

Existing literature basis: {item['basis']} See the closest and adjacent records in the evidence matrix; current coverage judgment is {fit}.

Difference from existing work: {item['difference']}

Core gap: {core_gap(item, fit)}

Minimum data: {item['data']}

Data acquisition route: {data_acquisition(item)}

Minimum method: {item['method']}

Optional advanced method: {advanced_method(item)}

Tool stack: {item['tools']}

Expected output: {item['output']}

First-week action: {item['first_step']}

Failure condition: {item['failure']}

Risk: {item['risk']}

Fallback option: {fallback_option(item)}

Later expansion direction: theory framework, constructs/variables, hypotheses, data plan, modeling plan, evaluation metrics, robustness checks, MVP, and writing structure.

What to do: {item['one_sentence']}

Why it is worth doing: it compresses the rough idea into a searchable, measurable, executable object-data-method combination.

Where existing research has reached: the evidence matrix shows closest or adjacent foundations, but coverage must be judged cautiously within the current search scope.

Where this topic can still enter: through a specific object, context, data source, mechanism, validation target, or method-transparency contribution rather than an absolute novelty claim.

What data to use: {item['data']}

What method to use: {item['method']}

What to do first: {item['first_step']}

How to downgrade if blocked: {fallback_option(item)}

Composite recommendation score: {score:.2f} / 5.00.
"""


def strategic_decision_state(default_topic: dict[str, Any]) -> str:
    return f"""## 8. Strategic Decision State

- Default recommendation: continue to Stage 2 with the default Topic unless you later replace it.
- Choice consequence: using the default Topic prioritizes data availability, defensible method, and first-week execution; replacing it requires rechecking data risk and literature crowding.
- Risk judgment: the largest risk is that the data cannot measure the core outcome, or that closest research is more crowded than the current search shows.
- Data reality judgment: assume no private data by default; form the MVP from public data, small pilot collection, evidence matrix, or auditable documents.
- Next execution action: build the default Topic's theory, constructs, data dictionary, baseline, evaluation metrics, and 12-week plan.
- Non-negotiable core: preserve the research object and core problem by default, while allowing method, theory, data source, and context to be redesigned.
- Method complexity: start with the minimum defensible method, then upgrade to statistics, machine learning, causal inference, interviews, simulation, or system design only when data supports it.
- Time window: design for 8-12 weeks by default; week one must produce a checkable evidence/data pilot and feasibility judgment.
"""


def strategic_questions(default_topic: dict[str, Any]) -> str:
    return f"""## 9. Strategic Decision Questions

These are not expert-literature questions. They determine how the project will be executed. If you do not answer, the default assumptions below remain in force.

1. **What data can you actually obtain?**
   - Effect: determines whether the route is empirical modeling, interviews, evidence synthesis, simulation, or prototype work.
   - Default assumption: no private data; use public data, small pilot collection, or literature evidence.
   - Consequence: prioritize an MVP such as `{default_topic['mvp']}` instead of a heavy model.

2. **What is the target output: paper, proposal, grant, system prototype, model, or report?**
   - Effect: determines theory depth, method complexity, and writing structure.
   - Default assumption: paper/proposal-ready output.
   - Consequence: protect the research question, evidence matrix, method route, and risk controls.

3. **Which part of the rough idea cannot change: object, problem, context, method, data source, or output?**
   - Effect: determines the redesign space.
   - Default assumption: preserve the research object and core problem; rebuild method, data, and theory if needed.
   - Consequence: sacrifice surface novelty when needed to gain executability and evidence strength.

4. **What is the time window?**
   - Effect: determines whether long tracking, experiments, complex models, or only an MVP are realistic.
   - Default assumption: 8-12 weeks.
   - Consequence: avoid designs that depend on long permissions, difficult authorization, or complex experimental conditions.

5. **What method ceiling is acceptable?**
   - Effect: determines baseline, statistical model, machine learning, causal inference, interviews, or mixed methods.
   - Default assumption: use the simplest defensible method first.
   - Consequence: baseline first, complex model later.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deep topic options and a default recommendation.")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    idea = extract_idea(out_dir)
    fit_report = read_text(out_dir / "topic_fit_report.md")
    fit = infer_fit(fit_report)
    rows = read_csv_dicts(out_dir / "evidence_matrix.csv")
    topics = topic_set(idea, fit)
    default_index = choose_default(topics)
    default_topic = topics[default_index - 1]

    topic_options = ["# Executable Topic Candidates", "", f"Original idea: {idea or 'Not available.'}", "", f"Coverage Judgment: {fit}", ""]
    for index, item in enumerate(topics, start=1):
        topic_options.append(render_topic(index, item, fit))
    write_text(out_dir / "topic_options.md", "\n".join(topic_options).rstrip() + "\n")

    recommendation = f"""# Topic Recommendation

## 1. My understanding of the rough idea

### Plain-language version
{idea or 'You provided a rough research idea that needs evidence search and redesign.'}

### Research version
Turn the rough idea into a research question that can be positioned in the literature, supported by data, and tested or synthesized with a defensible method.

### Executable version
Start from the current evidence matrix, select a minimum viable question, then expand theory, method, modeling, and data only as needed.

### Provisional assumptions
- You are not required to choose now; I will give a default recommendation.
- Make the topic deep first; expand theory, method, and models later.
- If data is unknown, prioritize public data, a small pilot, or an evidence-map MVP.

## 2. Live Search Scope

Search time: recorded in `search_manifest.json`.

Databases: OpenAlex, Semantic Scholar, Crossref, conditional domain databases, and live web search recorded in `live_web_sources.json`.

Queries: recorded in `search_terms.md` and `search_manifest.json`.

Inclusion criteria: records related to the question, object/context, method, model, outcome, data, or theory, with a traceable source.

Exclusion criteria: pure opinion pieces with no research value, records with no title, and records with no traceable source.

## 3. Closest Existing Research

{evidence_buckets(rows)}

## 4. Coverage Judgment

Within the current search scope, the rough idea is classified as: **{fit}**.

Rationale: see `topic_fit_report.md`. This is a scoped, provisional judgment and can change after supplemental search.

## 5. Executable Topic Candidates

{''.join(render_topic(index, item, fit) for index, item in enumerate(topics, start=1))}

## 6. Default Recommendation

My default recommendation is: **Topic {default_index}: {default_topic['title']}**.

Recommendation logic:
1. It has the strongest balance of executability, data availability, method fit, and risk control.
2. It does not depend on an absolute novelty claim; it depends on a verifiable redesign point.
3. It can produce an MVP first, then decide whether theory, method, model, or prototype depth should be upgraded.

This is not a demand that the user choose now. You are not required to choose; you can continue with this route or replace it later.

## 7. Execution Route for the Default Recommendation

- What to do: {default_topic['one_sentence']}
- Research object: {default_topic['object']}
- Unit of analysis: {default_topic['unit']}
- How to do it: {default_topic['first_step']}
- Tool stack: {default_topic['tools']}
- Minimum data: {default_topic['data']}
- Data acquisition route: {data_acquisition(default_topic)}
- Minimum method: {default_topic['method']}
- Optional advanced method: {advanced_method(default_topic)}
- MVP: {default_topic['mvp']}
- Failure condition: {default_topic['failure']}
- Risk: {default_topic['risk']}
- Fallback option: {fallback_option(default_topic)}

{strategic_decision_state(default_topic)}

{strategic_questions(default_topic)}

## 10. Later Expansion Path

If Topic {default_index} continues, the next layer can expand:

- theory foundation;
- conceptual framework;
- constructs / variables;
- hypotheses / propositions;
- data plan;
- modeling plan;
- evaluation metrics;
- MVP;
- timeline.
"""
    write_text(out_dir / "topic_recommendation.md", recommendation)
    print(f"Recommended Topic {default_index}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
