# Career Recommendation Data Quality Report

Generated: 2026-10-22

## Coverage summary

- Career roles: **75**
- Unique skills referenced by career data: **314**
- Resource coverage: **314/314 skills**
- Learning-resource skill entries: **317**
- Resource items: **323**
- Remaining explicitly labelled YouTube search fallbacks: **87**
- Prerequisite graph nodes: **92**
- Career skills without a configured prerequisite node: **228**

## Data Scientist changes

The six skills formerly listed only under `skill_types.implicit`—Data Cleaning, Exploratory Data Analysis, Feature Engineering, Model Evaluation, Data Storytelling, and Critical Thinking—are now also included in `skills` and `all_skill_weights`. The existing roadmap categorizer therefore keeps them in the **Core** category, and the skill-gap engine now surfaces them as required gaps.

Their weights are initial project estimates, not empirical market-demand figures. Have the team/TA validate these before describing them as measured job-market importance. Each skill now has skill-specific practice/project guidance and a direct learning resource.

## Resource curation

Replaced **156** generic YouTube-search entries with more relevant direct learning/documentation links where a specific resource could be identified. Remaining YouTube search links are labelled `Search Fallback (YouTube)` so the interface does not imply an individual video has been curated.

Key Data Scientist resources include Kaggle Learn for data cleaning, visualization, and feature engineering; scikit-learn documentation for model evaluation; Tableau's free Data Literacy training for data storytelling; and the University of Sussex Critical Thinking Skills Hub.

Not every URL across the entire dataset has been individually checked for availability. Review links before final submission.

## Remaining prerequisite-graph limitation

Resources are present for all **314** unique skills referenced by the career data, but the prerequisite graph does not have an explicit node for **228** of them. The current code treats an absent node like a skill with no configured dependencies, so some roadmaps outside Data Scientist may not show all prerequisite steps. `data_quality_report.json` includes the full list. An absent prerequisite node must not be interpreted as proof that a skill has no prerequisites.
