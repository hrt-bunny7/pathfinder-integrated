"""Regression tests for the skill-gap and roadmap modules. Run: python test.py"""
import unittest

from skill_gap import (
    find_skill_gaps,
    find_prerequisites,
    get_complete_skill_gap,
    order_skills,
    categorize_skills,
    get_learning_resources,
    generate_roadmap,
    estimate_skills_for_new_career,
)


class SkillGapTests(unittest.TestCase):
    def test_basic_gap(self):
        gap = find_skill_gaps(["python", " SQL ", "PANDAS"], "Data Scientist")
        self.assertEqual(gap, [
            "Statistics", "Machine Learning", "Data Analysis",
            "Data Cleaning", "Exploratory Data Analysis", "Feature Engineering",
            "Model Evaluation", "Data Storytelling", "Critical Thinking",
        ])
        self.assertNotIn("Python", gap)
        self.assertNotIn("SQL", gap)

    def test_unknown_career(self):
        self.assertIsNone(find_skill_gaps([], "Unlisted Career XYZ"))
        self.assertIsNone(generate_roadmap([], "Unlisted Career XYZ", display=False))

    def test_prerequisites_are_recursive_and_ordered(self):
        result = find_prerequisites("Machine Learning", ["Python", "SQL", "Pandas"])
        self.assertIn("Statistics", result)
        self.assertIn("Mathematics", result)
        self.assertEqual(len({x.casefold() for x in result}), len(result))

    def test_complete_gap_has_no_duplicates(self):
        gap = get_complete_skill_gap(["Python", "SQL", "Pandas"], "Data Scientist")
        self.assertIsNotNone(gap)
        self.assertEqual(len(gap), len({x.casefold() for x in gap}))
        self.assertIn("Machine Learning", gap)
        self.assertIn("Data Analysis", gap)

    def test_order_places_prerequisites_first(self):
        skills = ["Machine Learning", "Statistics", "Mathematics", "Computer Fundamentals"]
        ordered = order_skills(skills)
        positions = {skill.casefold(): i for i, skill in enumerate(ordered)}
        self.assertLess(positions["computer fundamentals"], positions["mathematics"])
        self.assertLess(positions["mathematics"], positions["statistics"])
        self.assertLess(positions["statistics"], positions["machine learning"])

    def test_categories_cover_all_skills(self):
        skills = get_complete_skill_gap(["Python", "SQL", "Pandas"], "Data Scientist")
        categories = categorize_skills(order_skills(skills), "Data Scientist")
        flattened = [skill for values in categories.values() for skill in values]
        self.assertCountEqual(flattened, skills)
        self.assertEqual(set(categories), {"Foundation", "Core", "Advanced", "Optional"})

    def test_resources_case_insensitive(self):
        self.assertTrue(get_learning_resources("python").get("resources"))

    def test_unknown_career_estimate_is_safe(self):
        # It may return a rough estimate if similar dataset roles exist, but must not crash.
        result = estimate_skills_for_new_career("Data Scientist Specialist")
        self.assertTrue(result is None or isinstance(result, dict))

    def test_all_75_careers_generate_roadmaps(self):
        # Dataset-wide regression: every listed role should produce a usable roadmap.
        from skill_gap import career_skills

        self.assertEqual(len(career_skills), 75)
        for career in career_skills:
            with self.subTest(career=career):
                roadmap = generate_roadmap([], career, display=False)
                self.assertIsInstance(roadmap, dict)
                skills = [entry["skill"] for entries in roadmap.values() for entry in entries]
                self.assertEqual(len(skills), len({skill.casefold() for skill in skills}))
                for entries in roadmap.values():
                    for entry in entries:
                        self.assertTrue(entry["resources"].get("resources"),
                                        f"No learning resources for {career}: {entry['skill']}")

    def test_all_prerequisite_references_exist(self):
        from skill_gap import prerequisites, _find_name

        for skill, data in prerequisites.items():
            prereq_list = data.get("prerequisites", []) if isinstance(data, dict) else data
            self.assertIsInstance(prereq_list, list, f"Invalid prerequisite list for {skill}")
            for prereq in prereq_list:
                with self.subTest(skill=skill, prerequisite=prereq):
                    self.assertIsNotNone(_find_name(prereq, prerequisites),
                                         f"Unknown prerequisite {prereq!r} referenced by {skill!r}")

    def test_all_implicit_data_scientist_skills_are_required(self):
        from skill_gap import career_skills

        data = career_skills["Data Scientist"]
        implicit = data["skill_types"]["implicit"]
        for skill in implicit:
            with self.subTest(skill=skill):
                self.assertIn(skill, data["skills"])
                self.assertIn(skill, data["all_skill_weights"])
                self.assertTrue(get_learning_resources(skill).get("resources"))

    def test_data_scientist_specific_resources_are_curated(self):
        from skill_gap import learning_resources

        required = [
            "Data Cleaning", "Exploratory Data Analysis", "Feature Engineering",
            "Model Evaluation", "Data Storytelling", "Critical Thinking",
        ]
        for skill in required:
            with self.subTest(skill=skill):
                urls = [r.get("url", "") for r in learning_resources[skill]["resources"]]
                self.assertTrue(urls)
                self.assertTrue(all("youtube.com/results?" not in url for url in urls))

    def test_every_career_referenced_skill_has_a_resource_entry(self):
        from skill_gap import career_skills, learning_resources

        referenced = set()
        for role in career_skills.values():
            for field in ("skills", "all_skill_weights"):
                value = role.get(field, {})
                if isinstance(value, dict):
                    referenced.update(value)
                elif isinstance(value, list):
                    referenced.update(value)
            for values in role.get("skill_types", {}).values():
                if isinstance(values, list):
                    referenced.update(values)
        self.assertFalse(sorted(referenced - set(learning_resources)))

    def test_roadmap_shape(self):
        roadmap = generate_roadmap(["Python", "SQL", "Pandas"], "Data Scientist", display=False)
        self.assertIsInstance(roadmap, dict)
        self.assertIn("Foundation", roadmap)
        for entries in roadmap.values():
            for entry in entries:
                self.assertEqual(set(entry), {"skill", "resources"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
