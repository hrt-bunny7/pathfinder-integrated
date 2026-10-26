# Person 3 — Skill-Gap Analysis and Learning Roadmap

## What changed

1. Unified `skill_gap.py` and `roadmap.py`: the main skill-gap implementation lives in `skill_gap.py`; `roadmap.py` is a compatibility entry point for the rest of the project.
2. Added the six Data Scientist implicit skills to both `skills` and `all_skill_weights`, so they now show up in the required skill-gap analysis.
3. Added prerequisite edges for the Data Scientist implicit skills and related data-analysis concepts.
4. Replaced generic YouTube search entries with specific learning/documentation pages when a suitable resource could be identified. The remaining fallback searches are explicitly labelled.
5. Added skill-specific practice tasks and mini-projects for the six Data Scientist skills.
6. Added `DATA_QUALITY_REPORT.md` and `data_quality_report.json` with coverage counts and known limitations.

The six new Data Scientist skill weights are initial project estimates, not validated hiring-market statistics. Confirm them with the team/TA before presenting them as empirical scores.

## Run the tests

Open a terminal in the project folder, then run:

```bash
cd skill_gap
python -m unittest -v
```

The tests cover the basic skill gap, unknown roles, case-insensitive matching, prerequisite ordering, roadmap categories, resource availability, and all 75 listed career roles.

## Try the roadmap demo

From the `skill_gap` directory, run:

```bash
python roadmap.py
```

The demo generates a Data Scientist roadmap for a sample student who already knows Python, SQL, and Pandas.

## Integration interface

The compatibility module provides:

```python
from roadmap import generate_roadmap

roadmap = generate_roadmap(
    career="Data Scientist",
    user_skills=["Python", "SQL", "Pandas"],
    display=False,
)
```

`roadmap` is a dictionary grouped into `Foundation`, `Core`, `Advanced`, and `Optional`. Each item contains a skill name and its learning-resource data. `user_skills` can be a list or a dictionary of skill names to levels.

## Known limitation

There are learning-resource entries for all skills referenced by the career dataset. However, not every career skill has an explicit node in `prerequisites.json`; the audit report lists the uncovered skills. The current code treats an absent node as having no configured dependencies, so those roadmaps may need further prerequisite curation. Resource URLs across the entire dataset have not all been individually opened and verified.
