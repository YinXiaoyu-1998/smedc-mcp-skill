import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CompanionGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = (ROOT / "skills" / "enterprise-hub-mcp" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        cls.readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.readme_zh_text = (ROOT / "README.zh.md").read_text(encoding="utf-8")

    def test_readmes_offer_core_only_and_optional_companion_profiles(self) -> None:
        for content in [self.readme_text, self.readme_zh_text]:
            with self.subTest(language=content.splitlines()[0]):
                self.assertIn("maijia-business-analyses-smedc", content)
                self.assertIn(
                    "https://github.com/YinXiaoyu-1998/maijia-business-analyses-smedc",
                    content,
                )

        self.assertIn("Core-only install", self.readme_text)
        self.assertIn("Optional companion", self.readme_text)
        self.assertIn("仅安装核心", self.readme_zh_text)
        self.assertIn("可选配套", self.readme_zh_text)

    def test_skill_requires_opt_in_before_companion_install(self) -> None:
        self.assertIn("## Optional Companion Skills", self.skill_text)
        self.assertRegex(self.skill_text, r"explicitly authorizes its\s+installation")
        self.assertIn("Never install it silently", self.skill_text)
        self.assertIn("not required for ordinary Enterprise Hub work", self.skill_text)


if __name__ == "__main__":
    unittest.main()
