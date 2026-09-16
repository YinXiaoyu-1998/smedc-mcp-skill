import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "smedc-mcp"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def old_identity_terms() -> list[str]:
    old_product = "Enterprise" + " Hub"
    old_slug = "enterprise" + "-hub"
    old_snake = "enterprise" + "_hub"
    old_typo = "enterprice" + "hub"
    old_tenant_en = "Mai" + "jia"
    old_tenant_slug = "mai" + "jia"
    old_tenant_zh = "麦" + "家"
    return [
        old_product,
        old_slug,
        old_snake,
        old_typo,
        old_tenant_en,
        old_tenant_slug,
        old_tenant_zh,
    ]


class SmedcSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read(SKILL_ROOT / "SKILL.md")
        cls.openai_yaml = read(SKILL_ROOT / "agents" / "openai.yaml")
        cls.update_guide = read(SKILL_ROOT / "references" / "update-skill.md")
        cls.readme_text = read(ROOT / "README.md")
        cls.readme_zh_text = read(ROOT / "README.zh.md")
        cls.current_text = "\n".join(
            [
                cls.skill_text,
                cls.openai_yaml,
                cls.update_guide,
                cls.readme_text,
                cls.readme_zh_text,
            ]
        )

    def test_current_smedc_contract_is_documented(self) -> None:
        expected_terms = [
            "smedc-mcp",
            "smedc-mcp-launcher@0.5.0",
            "SMEDC_BASE_URL",
            "smedc",
            "smedc_login",
            "smedc_logout",
            "smedc_auth_status",
            "smedc_get_current_user",
            "smedc_list_skills",
            "smedc-business-analysis",
            "smedc-delivery-ledger",
            "YinXiaoyu-1998/smedc-companion-skills",
            "organizationName",
            "YinXiaoyu-1998/smedc-mcp-skill",
        ]

        for term in expected_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.current_text)

    def test_companions_require_explicit_authorization(self) -> None:
        self.assertIn("## Optional Companion Skills", self.skill_text)
        self.assertRegex(self.skill_text, r"explicitly authorizes its\s+installation")
        self.assertIn("Never install it silently", self.skill_text)
        self.assertIn("not required for ordinary SMEDC work", self.skill_text)

    def test_install_guidance_uses_current_repository_and_skill_name(self) -> None:
        for content in [self.readme_text, self.readme_zh_text]:
            with self.subTest(language=content.splitlines()[0]):
                self.assertIn("YinXiaoyu-1998/smedc-mcp-skill", content)
                self.assertIn("~/.agents/skills/smedc-mcp", content)
                self.assertIn("skills/smedc-mcp", content)
                self.assertIn("smedc-mcp-launcher@0.5.0", content)
                self.assertIn("SMEDC_BASE_URL=https://api.smedatacenter.xyz", content)

    def test_old_current_identities_are_absent_from_current_docs(self) -> None:
        for term in old_identity_terms():
            with self.subTest(term=term):
                self.assertNotIn(term, self.current_text)


if __name__ == "__main__":
    unittest.main()
