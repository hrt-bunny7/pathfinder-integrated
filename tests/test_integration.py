"""Run from the backend folder:  python -m unittest discover -s tests -v
Exercises Members 2, 3 and 4 through adapters.py (no web framework needed)."""
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adapters  # noqa: E402

RESUME_TEXT = """Rahul Sharma
Education
B.Tech Computer Science and Engineering, 2021 - 2025
Skills
Python, JavaScript, ReactJS, Node.js, Express, Next.js, Tailwind CSS, SQL, PostgreSQL, Git, Docker, REST APIs, TypeScript
Experience
Web Developer Intern, ABC Corp, 2024 - 2025
Projects
1. Job Portal - React and Node
2. Chat App - Socket.io
"""


def make_docx(text: str) -> bytes:
    import docx
    d = docx.Document()
    for line in text.split("\n"):
        d.add_paragraph(line)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def make_pdf(text: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    for line in text.split("\n"):
        c.drawString(50, y, line)
        y -= 18
    c.save()
    return buf.getvalue()


class ResumeTests(unittest.TestCase):
    def check(self, profile):
        names = [s["name"] for s in profile["skills"]]
        for expected in ["Python", "JavaScript", "React", "Node.js", "Express", "SQL", "Git", "Docker"]:
            self.assertIn(expected, names)
        self.assertNotIn("Express.Js", names)          # normalised to the website's name
        self.assertEqual(len(names), len({n.lower() for n in names}))
        self.assertEqual(profile["education"], "B.Tech CSE")
        self.assertGreaterEqual(profile["experience_years"], 1)
        self.assertTrue(profile["summary"])
        for s in profile["skills"]:
            self.assertIn("category", s)

    def test_docx(self):
        self.check(adapters.analyze_resume_bytes("cv.docx", make_docx(RESUME_TEXT), "u1"))

    def test_pdf(self):
        p = adapters.analyze_resume_bytes("cv.pdf", make_pdf(RESUME_TEXT), "u1")
        self.check(p)
        self.assertEqual(p["user_id"], "u1")

    def test_bad_inputs_give_clear_errors(self):
        with self.assertRaises(adapters.ResumeError):
            adapters.analyze_resume_bytes("cv.txt", b"hello", "u")
        with self.assertRaises(adapters.ResumeError):
            adapters.analyze_resume_bytes("cv.pdf", b"", "u")
        with self.assertRaises(adapters.ResumeError):
            adapters.analyze_resume_bytes("cv.docx", b"not a zip", "u")
        with self.assertRaises(adapters.ResumeError):
            adapters.analyze_resume_bytes("cv.pdf", make_pdf("Nothing useful in this file at all, sorry folks."), "u")


class CareerTests(unittest.TestCase):
    def test_web_profile(self):
        profile = {"skills": [{"name": n} for n in ["Python", "JavaScript", "React", "SQL", "Git", "HTML", "CSS", "REST APIs"]]}
        out = adapters.recommend(profile)
        self.assertTrue(1 <= len(out) <= 3)
        for c in out:
            self.assertEqual(set(c), {"role", "fit", "reason"})
            self.assertIs(type(c["role"]), str)            # not numpy.str_
            self.assertIs(type(c["fit"]), int)
        self.assertIn(out[0]["role"], {"Full Stack Developer", "Frontend Developer", "Backend Developer"})

    def test_unknown_skills_do_not_crash(self):
        self.assertEqual(adapters.recommend({"skills": [{"name": "Basket weaving"}]}), [])
        self.assertEqual(adapters.recommend({"skills": []}), [])


class RoadmapTests(unittest.TestCase):
    GAP = {
        "score": 40,
        "matched": [{"name": "Python", "weight": 2}, {"name": "Git", "weight": 1}],
        "partial": [{"name": "Django", "weight": 1.5, "via": "Flask"}],
        "missing": [{"name": "Docker", "weight": 2}, {"name": "Kubernetes", "weight": 1.5},
                    {"name": "Next.js", "weight": 1}, {"name": "REST APIs", "weight": 1},
                    {"name": "Supabase", "weight": 1}, {"name": "Machine Learning", "weight": 0.5}],
    }

    def test_shape_and_contract_rules(self):
        plan = adapters.build_roadmap({"title": "Backend Dev"}, self.GAP)
        weeks = plan["weeks"]
        self.assertTrue(weeks)
        gap_names = {s["name"] for k in ("missing", "partial") for s in self.GAP[k]}
        self.assertEqual([w["week"] for w in weeks], list(range(1, len(weeks) + 1)))
        for w in weeks:
            self.assertIn(w["skill"], gap_names)            # ticking a week must change the match %
            self.assertEqual(set(w), {"week", "skill", "topics", "project", "resources"})
            self.assertTrue(w["topics"] and w["project"])
            self.assertTrue(w["resources"])
            for r in w["resources"]:
                self.assertTrue(r["title"] and r["url"].startswith("http"))

    def test_prerequisites_come_first(self):
        order = [w["skill"] for w in adapters.build_roadmap({}, self.GAP, limit=10)["weeks"]]
        self.assertLess(order.index("Docker"), order.index("Kubernetes"))

    def test_skills_missing_from_member4_data_still_get_resources(self):
        weeks = {w["skill"]: w for w in adapters.build_roadmap({}, self.GAP)["weeks"]}
        self.assertIn("nextjs.org", weeks["Next.js"]["resources"][0]["url"])
        self.assertIn("supabase", weeks["Supabase"]["resources"][0]["url"])

    def test_empty_gap(self):
        self.assertEqual(adapters.build_roadmap({}, {"matched": [], "partial": [], "missing": []}), {"weeks": []})


class NameTests(unittest.TestCase):
    def test_canonical(self):
        for raw, want in [("ReactJS", "React"), ("express.js", "Express"), ("Vue.js", "Vue"),
                          ("Scikit-Learn", "Scikit-learn"), ("Google Cloud", "GCP"),
                          ("Natural Language Processing", "NLP"), ("Object-Oriented Programming", "OOP")]:
            self.assertEqual(adapters.canonical_skill(raw), want)

    def test_every_website_skill_has_resources(self):
        for skill in adapters.SKILLS:
            info = adapters._resources_for(skill)
            self.assertTrue(info["resources"], skill)


if __name__ == "__main__":
    unittest.main()
