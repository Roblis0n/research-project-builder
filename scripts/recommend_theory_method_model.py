#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import extract_idea, output_dir_from_args, read_csv_dicts, read_text, write_text


def selected_topic(out_dir: Path, override: str) -> str:
    if override:
        return override.strip()
    recommendation = read_text(out_dir / "topic_recommendation.md")
    patterns = [
        r"My default recommendation is:\s*\*\*(.+?)\*\*",
    ]
    for pattern in patterns:
        match = re.search(pattern, recommendation, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return extract_idea(out_dir) or "the provisionally selected research topic"


def infer_route(topic: str) -> dict[str, str]:
    lower = topic.lower()

    # Evidence-synthesis routes should be detected before generic mechanism or impact terms.
    if any(
        marker in lower
        for marker in [
            "review",
            "scoping",
            "evidence-map",
            "evidence map",
            "gap-driven",
            "evidence synthesis",
            "systematic map",
        ]
    ):
        return {
            "route_name": "Evidence synthesis route",
            "primary_theory": "PCC/SPIDER/PICO framing plus a gap taxonomy",
            "why_this_theory": "The project needs disciplined scope definition and evidence classification before it commits to empirical data or causal language.",
            "avoid_theory": "Do not force causal theory before the evidence map shows stable constructs, outcomes, and study families.",
            "method": "Scoping review, systematic mapping, bibliometric analysis, or thematic synthesis.",
            "baseline": "Transparent search protocol, inclusion/exclusion criteria, and extraction table",
            "models": "evidence matrix, thematic coding, bibliometric network, gap taxonomy, optional expert validation",
            "metrics": "database coverage, screening agreement, extraction completeness, theme saturation, citation/source transparency",
            "tools": "OpenAlex, Semantic Scholar, Zotero, Rayyan/Excel, VOSviewer or bibliometrix if bibliometric, Python for metadata cleaning",
            "data_unit": "paper, dataset, guideline, tool, project report, or trial record",
            "first_week": "Lock inclusion/exclusion rules and extract 20 papers into a matrix with object, method, theory, data, and gap columns.",
        }

    if any(marker in lower for marker in ["predict", "prediction", "classification", "model", "machine learning", "forecast"]):
        return {
            "route_name": "Prediction / classification route",
            "primary_theory": "CRISP-DM plus domain theory",
            "why_this_theory": "The project depends on data understanding, feature construction, baseline modeling, evaluation, and deployment limits.",
            "avoid_theory": "Do not use a social theory as decoration unless it changes feature design, subgroup analysis, or error interpretation.",
            "method": "Prediction/modeling route with a transparent baseline first.",
            "baseline": "rules-based baseline, majority-class baseline, or logistic/linear regression depending on target type",
            "models": "regularized regression, random forest, gradient boosting, calibrated probabilistic model; deep learning only if sample size and labels justify it",
            "metrics": "primary metric matched to target, calibration if probabilities matter, subgroup error, decision utility if decisions are involved",
            "tools": "Python, pandas, scikit-learn, statsmodels, matplotlib, SHAP only after baseline, DVC or a simple data-version folder",
            "data_unit": "one row per case, record, document, person, or event with clear target Y and features X",
            "first_week": "Define Y, build a 30-row pilot dataset, create a data dictionary, and run a trivial baseline.",
        }

    if any(
        marker in lower
        for marker in [
            "mechanism",
            "mechanisms",
            "mediation",
            "moderation",
            "mediator",
            "moderator",
            "identity",
            "self-efficacy",
            "anxiety",
            "capability",
        ]
    ):
        return {
            "route_name": "Mechanism explanation route",
            "primary_theory": "Social cognitive theory with self-efficacy / academic identity mechanism",
            "why_this_theory": "The project asks how an exposure changes behavior, confidence, identity, anxiety, or performance through an internal mechanism.",
            "avoid_theory": "Technology acceptance is too shallow if the outcome is academic development rather than mere tool adoption.",
            "method": "Mechanism explanation using validated constructs, mediation/moderation, SEM, qualitative mechanism tracing, or mixed methods.",
            "baseline": "descriptive association, construct reliability, and a simple mediation or thematic mechanism map",
            "models": "mediation/moderation, SEM, multilevel model if nested data exist, or explanatory sequential mixed methods",
            "metrics": "construct reliability, effect sizes, model fit, robustness across subgroups, qualitative triangulation",
            "tools": "R lavaan or Python statsmodels, survey platform, interview guide, Taguette/NVivo/Excel for coding, Zotero for theory papers",
            "data_unit": "one respondent, case, interview, or document with exposure, mechanism, outcome, and context variables",
            "first_week": "Write a 3-link mechanism chain, identify validated scales or interview probes, and pilot 5 cases or 20 survey responses.",
        }

    if any(marker in lower for marker in ["carbon", "emission", "esg", "disclosure", "climate"]):
        return {
            "route_name": "Data-first empirical / scenario route",
            "primary_theory": "Stakeholder theory plus institutional theory",
            "why_this_theory": "The project involves organizational disclosure, compliance pressure, legitimacy, and environmental accountability.",
            "avoid_theory": "Do not start with complex forecasting theory if the measurement basis is unstable.",
            "method": "Data-first empirical route or transparent scenario route depending on label availability.",
            "baseline": "public-data proxy audit and descriptive baseline before prediction or panel modeling",
            "models": "panel regression, interpretable forecasting baseline, scenario model, Monte Carlo sensitivity analysis, or difference-in-differences if a policy shock exists",
            "metrics": "proxy validity, missingness, sensitivity bands, out-of-sample error if predictive, robustness to alternative proxies",
            "tools": "Python/R, pandas, public disclosure scraping where legal, ESG/public-report matrix, statsmodels/plm, simple simulation notebook",
            "data_unit": "firm-year, region-year, industry-year, or scenario-year",
            "first_week": "Build a source-by-variable matrix and test whether the outcome can be measured for at least 30 units.",
        }

    return {
        "route_name": "Gap-driven mixed empirical route",
        "primary_theory": "Closest domain theory from the evidence matrix plus a lightweight conceptual framework",
        "why_this_theory": "The current topic needs theory only insofar as it defines variables, mechanisms, and boundary conditions.",
        "avoid_theory": "Do not choose theory by name recognition; choose it by whether it changes measurement and analysis.",
        "method": "Mixed empirical route: evidence matrix first, then descriptive baseline, qualitative validation, or simple statistical model.",
        "baseline": "descriptive evidence map and simple association baseline",
        "models": "regression, thematic analysis, SEM, interpretable ML, or simulation depending on data",
        "metrics": "validity, reliability, effect size, robustness, interpretability, and practical usefulness",
        "tools": "Zotero, spreadsheet evidence matrix, Python/R, qualitative coding sheet, reproducible notebook",
        "data_unit": "the smallest observable case that contains exposure, context, mechanism, and outcome evidence",
        "first_week": "Define unit of analysis, outcome, and a 20-item pilot evidence/data table before choosing advanced methods.",
    }


def infer_construct_rows(topic: str, route: dict[str, str]) -> str:
    lower = topic.lower()
    if any(m in lower for m in ["ai", "chatgpt", "llm", "generative"]):
        return """| Role | Construct / variable | Measurement | Data source |
|---|---|---|---|
| Antecedent | AI use intensity / AI involvement mode | frequency, task type, logs, self-report scale | survey, interview, tool logs |
| Mechanism | self-efficacy, cognitive load, academic identity, anxiety | validated scale, interview coding, task performance | survey, interview, task data |
| Outcome | research topic quality, research capability, anxiety level, output quality | rating scale, expert assessment, text-quality indicator, output record | survey, expert scoring, text corpus |
| Moderator | field, cohort, supervisor support, AI literacy | group variable or continuous scale | background questionnaire, interview |"""
    if any(m in lower for m in ["carbon", "emission", "esg", "climate"]):
        return """| Role | Construct / variable | Measurement | Data source |
|---|---|---|---|
| Antecedent | policy pressure / ESG disclosure / industry attribute | policy event, disclosure rating, industry classification | government files, ESG data, annual reports |
| Mechanism | disclosure quality, governance pressure, green investment | text indicators, investment amount, governance structure | annual reports, ESG reports, databases |
| Outcome | carbon emissions / carbon intensity / green performance | Scope indicators, emission intensity, proxy variable | disclosure reports, industry statistics, public databases |
| Moderator | firm size, region, regulatory intensity, ownership | control or grouping variable | annual reports, statistical yearbooks, public databases |"""
    return """| Role | Construct / variable | Measurement | Data source |
|---|---|---|---|
| Antecedent | context / exposure | survey scale, observed event, document feature, or dataset-derived measure | public data, survey, interviews, institutional records |
| Mechanism | capability, anxiety, trust, self-efficacy, process change, or data-readiness construct | validated scale, coded interview themes, behavioral indicators | survey, interview, log data |
| Outcome | performance, risk, adoption, emission, quality, or target outcome | outcome label, score, productivity indicator, quality rating, or proxy | dataset, registry, reports, administrative records |
| Moderator | field, cohort, organization, policy, baseline skill, or data quality | group indicator or continuous measure | metadata or questionnaire |
| Quality control | measurement validity | missingness, reliability, coding agreement, proxy sensitivity | audit table and robustness checks |"""


def hypothesis_block(route: dict[str, str]) -> str:
    if "Prediction" in route["route_name"]:
        return """H1: The baseline feature set predicts the target better than a trivial baseline.

H2: Candidate models improve only if they remain stable after calibration, subgroup checks, and error analysis.

H3: Interpretability analysis identifies stable predictors that align with domain knowledge rather than noise."""
    if "Mechanism" in route["route_name"]:
        return """H1: The focal exposure is associated with the primary outcome after controlling for baseline context.

H2: The relationship is mediated by the proposed mechanism variable.

H3: The relationship is moderated by a boundary condition such as field, cohort, baseline capability, data quality, or organizational context."""
    if "Evidence synthesis" in route["route_name"]:
        return """P1: Existing studies cluster into identifiable object-method-theory-data patterns.

P2: The strongest gap is not a blank topic, but a weakly connected combination of context, data, method, or mechanism.

P3: A defensible next project can be derived from the evidence-map gap taxonomy."""
    return """H1/P1: The focal exposure or context is meaningfully linked to the outcome or phenomenon under study.

H2/P2: The proposed mechanism explains part of that relationship.

H3/P3: The relationship depends on a boundary condition such as context, cohort, data quality, or institutional setting."""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deep theory, method, and model expansion pack.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--topic", default="", help="Optional selected topic override.")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    topic = selected_topic(out_dir, args.topic)
    route = infer_route(topic)
    rows = read_csv_dicts(out_dir / "evidence_matrix.csv")
    nearest = sorted(rows, key=lambda row: float(row.get("similarity_score") or 0), reverse=True)[:5]
    evidence = "\n".join(f"- {row.get('id')}: {row.get('title')} ({row.get('year')})" for row in nearest) or "- No evidence rows available; run topic-landing search first."

    pack = f"""# Theory / Method / Model Pack

## 1. Selected Topic

{topic}

Route classification: **{route['route_name']}**.

## 2. Theory Candidate Table

| Theory | Fit | Explanatory value | Limitation | Recommendation |
|---|---|---|---|---|
| {route['primary_theory']} | High | {route['why_this_theory']} | Must be adapted to the exact field, population, and measurable variables. | Strong |
| Technology acceptance / affordance perspective | Medium | Explains tool adoption, perceived usefulness, affordances, and behavioral change. | Too generic if not linked to domain outcomes. | Conditional |
| Self-efficacy / capability perspective | Medium | Explains confidence, skill development, anxiety, and performance pathways. | Needs reliable construct measurement. | Conditional |
| Institutional / stakeholder perspective | Medium | Explains contextual pressures, legitimacy, organizational incentives, and governance. | Fits better for organizational, policy, or disclosure topics. | Conditional |
| Evidence synthesis / gap taxonomy | Medium | Clarifies what is already known and what is executable next. | Not enough if the final aim requires empirical causal or predictive claims. | Conditional |

## 3. Recommended Main Theory

Recommended framework: **{route['primary_theory']}**.

Why this and not a decorative theory: {route['why_this_theory']}

What to avoid: {route['avoid_theory']}

## 4. Why Not Use Other Theories

| Candidate not used as primary theory | Why it is not primary | When it can supplement |
|---|---|---|
| Technology acceptance / affordance perspective | It can collapse into simple tool-adoption logic and miss the outcome or mechanism. | When the question turns to intention to use, affordances, or human-tool workflow. |
| Self-efficacy / capability perspective | Without reliable scales or behavioral indicators, it becomes a label rather than an explanation. | When the mechanism is capability, confidence, anxiety, identity, or performance. |
| Institutional / stakeholder perspective | It fits organizations, policies, governance, and disclosure better than individual-level topics. | When the sample unit is an organization, region, industry, or policy event. |
| Evidence synthesis / gap taxonomy | It can locate a gap, but it does not replace empirical testing. | When data is not yet available and a scoping review or evidence map is the right MVP. |

Use a theory only if it changes at least one of these:

- what variables or constructs are measured;
- what data is collected;
- what model or analysis is used;
- what mechanism or boundary condition is tested;
- how findings are interpreted.

## 5. Conceptual Model

```mermaid
flowchart LR
    A[Context / exposure] --> B[Mechanism or capability]
    B --> C[Primary outcome]
    D[Boundary condition] -.-> B
    E[Data quality / measurement] -.-> C
```

Interpretation:
- A is what changes or differs across cases.
- B is the mechanism that explains how A matters.
- C is the outcome that makes the project worth doing.
- D defines when the mechanism is stronger or weaker.
- E prevents overclaiming when data quality is limited.

## 6. Constructs/Variables

{infer_construct_rows(topic, route)}

## 7. Hypotheses or Propositions

{hypothesis_block(route)}

## 8. Data Plan

Minimum viable data:

- Unit of analysis: {route['data_unit']}.
- One measurable outcome.
- Traceable exposure or predictor variables.
- Context metadata for subgroup or boundary-condition checks.
- Data dictionary with source, definition, missingness, and proxy risk.
- Enough records or cases to support the chosen method.

Evidence to reuse:
{evidence}

Data decision rule:

- If labels or outcomes exist, use empirical modeling or mechanism testing.
- If labels do not exist but documents or cases exist, use qualitative or evidence-map route.
- If the target is future-facing, use scenario analysis rather than overconfident prediction.
- If no data source can measure the outcome, redesign the topic before modeling.

## 9. Method Route

Primary route: **{route['method']}**.

Steps:
1. Define the unit of analysis, target outcome, and inclusion/exclusion rules.
2. Create a codebook or data dictionary.
3. Build a baseline descriptive analysis.
4. Fit the minimal model or qualitative synthesis needed to answer the question.
5. Run robustness checks and error analysis.
6. Interpret findings against the evidence matrix rather than as absolute novelty.

## 10. Statistical Model / Machine Learning Model / Simulation Model

### baseline
{route['baseline']}.

### candidate models
{route['models']}.

### evaluation metrics
{route['metrics']}.

### robustness checks
- Alternative operationalization of key variables.
- Subgroup or context-specific analysis.
- Sensitivity to missing data and proxy choice.
- Compare against a simple baseline.
- Inspect failure cases or contradictory evidence.
- If qualitative, check coding consistency and negative cases.

### Method/model execution explanation

| Component | why to use it | which research question it answers | what data it requires | how to replace it if it fails | How its output becomes a paper section or project-plan deliverable |
|---|---|---|---|---|---|
| baseline | It prevents complex methods from hiding weak data or unmeasurable variables. | Whether the minimum model can already explain, predict, classify, or synthesize the target. | Clear unit of analysis, target variable, basic features, or coding categories. | Use descriptive statistics, evidence mapping, or qualitative coding. | Put it in the method section as the baseline design and in results as the comparison table. |
| candidate models | They test whether more complex methods produce a substantive improvement. | Whether the advanced method answers the main question better than the baseline. | Enough sample size, labels/constructs, features, missing-data handling, and validation split. | Downgrade to regularized models, group comparisons, thematic coding, or case analysis. | Put it in model comparison, robustness, and limitations. |
| evaluation metrics | They turn vague “good performance” into reportable criteria. | Whether the method output meets the research objective. | Prediction labels, scoring rules, coding agreement, scale reliability, or outcome indicators. | Use more transparent process indicators, expert scoring, or sensitivity analysis. | Put it in result tables, evaluation metric tables, and robustness paragraphs. |
| robustness checks | They prevent conclusions from depending on one proxy variable or sample cut. | Whether conclusions remain stable under alternative measurement, subgroups, and missing-data treatment. | Alternative variables, subgroup metadata, missingness notes, or repeated coding. | Use negative-case analysis, boundary-condition discussion, or explicit data-limit statements. | Put it in robustness checks and the discussion section. |

## 15. Tool Stack

{route['tools']}.

Minimum setup:

- `/data/raw` for untouched data;
- `/data/processed` for cleaned data;
- `/notebooks` or `/analysis` for reproducible work;
- `/outputs` for tables, figures, and evidence logs;
- Zotero or an equivalent reference manager;
- a decision log for assumptions.

## 16. MVP

Produce a small, defensible pilot:

- 20-50 key papers in the evidence matrix or a clearly scoped public/pilot dataset;
- one main research question;
- one baseline method;
- one robustness check;
- one concise write-up of feasibility, contribution, and risk.

First executable week:

{route['first_week']}

## 17. 12-Week Execution Plan

| Week | Execution focus | Deliverable |
|---:|---|---|
| 1 | Scope lock | refined question, non-negotiable core, inclusion/exclusion rules |
| 2 | Evidence refresh | updated live sources, evidence matrix, closest-work buckets |
| 3 | Data readiness | data dictionary, source access check, missingness/proxy notes |
| 4 | Pilot data | 20-50 cases/records/interviews/papers sampled and cleaned |
| 5 | baseline | descriptive baseline, first model/synthesis, first table/figure |
| 6 | candidate models | candidate method/model comparison or qualitative coding pass |
| 7 | evaluation metrics | metrics, reliability, validity, fit, calibration, or coding agreement |
| 8 | robustness checks | sensitivity checks, subgroup checks, negative cases, proxy alternatives |
| 9 | Interpretation | link findings to theory, mechanism, and evidence matrix |
| 10 | Draft method/results | method section, data section, initial results narrative |
| 11 | Draft introduction/literature | gap framing, closest work, contribution, limitations |
| 12 | Final integration | full project plan/manuscript skeleton, risk register, next-step decision |

## 18. Risks and Fallback Routes

| Risk | Fallback route |
|---|---|
| Search may miss field-specific databases or non-English literature. | Add domain databases, citation chaining, and bilingual query families. |
| API metadata can omit methods, sample details, and theory. | Verify the top records through full text or abstracts before final claims. |
| Data availability may force a narrower project. | Switch to public-data MVP, proxy design, or evidence-readiness audit. |
| Theory fit may be weak. | Use a lighter conceptual framework and state theory choice as provisional. |
| Modeling may outrun labels or sample size. | Keep a transparent baseline and prefer descriptive or qualitative routes when needed. |
| User constraints change. | Preserve assumptions in the decision log and update the plan without restarting. |

## 19. Writing Structure

1. Introduction: problem, closest literature, why the current formulation needs redesign.
2. Literature: highly similar work, adjacent work, method/theory borrowing.
3. Research question and framework: constructs, mechanism, boundary condition.
4. Data: unit, source, measurement, missingness, proxy risks.
5. Method: baseline, main analysis/model, robustness.
6. Results or expected analysis: what would count as evidence.
7. Discussion: contribution, limitations, execution boundary, next project.
"""

    write_text(out_dir / "theory_method_model_pack.md", pack)
    print("Wrote theory_method_model_pack.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
