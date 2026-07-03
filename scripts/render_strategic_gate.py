#!/usr/bin/env python3
from __future__ import annotations

import argparse

from _common import output_dir_from_args, slugify, write_text


DEFAULT_IDEA = "You provided an early research idea that needs strategic routing before execution."


def strategic_gate_text(idea: str) -> str:
    idea = " ".join((idea or DEFAULT_IDEA).split())
    return f"""# Strategic Decision Gate

## My current reading of the rough idea

Your rough research idea is: {idea}

I will not turn this directly into a research question yet. I will first lock the seven route-changing decisions that determine evidence search, topic redesign, data reality, method depth, and project risk.

## D1. Target output

Options:
A. Paper  
B. Thesis/proposal  
C. Grant proposal  
D. System prototype  
E. Model/algorithm  
F. Data analysis report

Default recommendation:
Treat the project as paper/proposal-ready first. That keeps the literature position, gap claim, data path, method choice, and writing structure defensible.

Choice consequence:
If the target output is a paper, the next step is closest-literature search, gap diagnosis, and a minimal defensible method. If it is a system or model, the next step is data, labels, baseline, metrics, and evaluation protocol.

Why this changes the route:
The output type determines theory depth, method complexity, evidence standard, writing structure, and MVP size.

## D2. Non-negotiable core

What must stay fixed?
A. Research object  
B. Context  
C. Method  
D. Theory problem  
E. Data source  
F. Application goal

Default judgment:
Keep the research object and core problem fixed. Allow context, method, theory, and data route to be redesigned.

Choice consequence:
If the object is fixed, I will avoid crowded literature by changing context, data, method, or mechanism. If the method is fixed, the question and data must be selected backward from what that method can legitimately answer.

Why this changes the route:
The non-negotiable core determines what can be sacrificed, what cannot be changed, and where the project can still find a defensible contribution.

## D3. Data reality

Current data status:
A. Existing private data  
B. Scrapeable data  
C. Interview/survey data  
D. Experimental data  
E. No data yet  
F. Public data only

Default judgment:
Assume no private data is available. Start from public data, small pilot survey/interview data, document evidence, or reproducible metadata.

Data reality judgment:
Without a clear data source, do not assume causal inference, machine learning, deep learning, or complex experiments. First design a minimum data path that can be tested in week one.

Why this changes the route:
Data reality determines whether the project can use causal inference, statistics, machine learning, qualitative work, evidence synthesis, simulation, or system prototyping.

## D4. Method complexity

Acceptable method level:
A. Literature review  
B. Qualitative interviews  
C. Survey/statistics  
D. Causal inference  
E. Machine learning  
F. Deep learning  
G. Simulation  
H. System design

Default recommendation:
Start with the minimal defensible method: evidence matrix plus descriptive analysis, content analysis, basic statistics, or a small qualitative pilot. Upgrade only when the data can support it.

Method complexity judgment:
Baseline first, complex model later. Variables and sample first, algorithm later. Interpretable output first, decorative complexity never.

Why this changes the route:
Method complexity determines sample size, variable design, tool stack, time cost, failure risk, and interpretability.

## D5. Innovation-feasibility trade-off

Preference:
A. Conservative and finishable  
B. Robust and publishable  
C. High-risk / high-novelty

Default recommendation:
Choose B: robust and publishable. First make the project finishable and defensible, then find a small but hard contribution.

Risk judgment:
High-novelty routes usually require stronger data, a narrower object, or higher method cost. Robust routes are better for landing the topic and building an evidence-backed project.

Why this changes the route:
This trade-off decides whether to pursue low-risk validation, contextual extension, mechanism deepening, new data, or a new model.

## D6. Time window

Options:
A. 1-2 weeks  
B. 1 month  
C. 3 months  
D. 6 months  
E. More than 1 year

Default judgment:
Design an 8-12 week MVP. Avoid routes that depend on long tracking, complex experiments, or hard-to-authorize data.

Time-window judgment:
Short windows support topic landing, evidence matrix, public-data MVP, or small pilots. Longer windows can support experiments, longitudinal data, or complex systems.

Why this changes the route:
The time window determines whether the project can use long-term data, experiments, complex models, deep interviews, prototypes, or only topic landing.

## D7. Current stage

Options:
A. Topic only  
B. Topic plus closest literature  
C. Topic plus method outline  
D. Full project plan  
E. Expand theory/modeling later

Default recommendation:
Do topic plus closest literature plus method outline first. Do not write the full project plan before search evidence and data feasibility are checked.

Next execution action:
After authorization, I will run live search, build an evidence matrix, then return 3-5 executable topic candidates and one default recommendation.

Why this changes the route:
The current stage determines output depth. Writing a full plan too early turns unsearched assumptions into false certainty.

## Default strategy

Based on the rough idea alone, my default strategy is:

- do not write a full project plan yet;
- lock the non-negotiable core and data reality first;
- after one lightweight authorization, run live closest-literature search;
- build executable topic candidates and one default recommendation;
- expand theory, method, modeling, and project plan only after a topic is provisionally selected.

## You can reply with

1. "Run defaults"
2. "Use default strategy"
3. "start search"
4. "Change D2/D3/D5 to ..."
5. "Topic only; do not expand theory or modeling yet"
6. "Go directly to the full project plan"

You do not need to answer every item. One sentence such as "Run defaults" or "Use default strategy" is enough.

This gate is not a demand that you make expert judgments. It only asks for decisions that actually change the research route.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Stage 0 Strategic Decision Gate for direct Codex display.")
    parser.add_argument("--idea", default="", help="User's rough research idea.")
    parser.add_argument("--out-dir", default="", help="Output directory for codex_inline_response.txt.")
    args = parser.parse_args()

    idea = args.idea.strip() or DEFAULT_IDEA
    out_dir = output_dir_from_args(args.out_dir or None, slugify(idea))
    text = strategic_gate_text(idea)
    write_text(out_dir / "codex_inline_response.txt", text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
