import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "smedc-mcp"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(document: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in document:
        raise AssertionError(f"Missing active section: {heading}")
    return document.split(marker, 1)[1].split("\n## ", 1)[0]


def prose(content: str) -> str:
    return " ".join(content.split())


def launcher_versions(content: str) -> list[str]:
    # Explicit install references only; bare minimum/history versions are not pins.
    patterns = (
        r"""smedc-mcp-launcher@([^\s`"']+)""",
        r"""launcher[\\/]+versions[\\/]+([^\\/\s`"']+)""",
        r'''"launcherVersion"\s*:\s*"([^"]+)"''',
        r"this document pins launcher\s+(\S+?)(?=[.;]?(?:\s|$))",
    )
    return [
        match.group(1)
        for pattern in patterns
        for match in re.finditer(pattern, content)
    ]


def old_identity_terms() -> list[str]:
    old_product = "Enterprise" + " Hub"
    old_product_lower = "enterprise" + " hub"
    old_slug = "enterprise" + "-hub"
    old_snake = "enterprise" + "_hub"
    old_compact = "enterprise" + "hub"
    old_typo = "enterprice" + "hub"
    old_tenant_en = "Mai" + "jia"
    old_tenant_slug = "mai" + "jia"
    old_tenant_zh = "麦" + "家"
    return [
        old_product,
        old_product_lower,
        old_slug,
        old_snake,
        old_compact,
        old_typo,
        old_tenant_en,
        old_tenant_slug,
        old_tenant_zh,
    ]


def tracked_repository_text_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    paths = []
    for raw_path in completed.stdout.decode("utf-8").split("\0"):
        if not raw_path:
            continue

        path = Path(raw_path)
        parts = set(path.parts)
        suffix = path.suffix.lower()

        # These are not current repository prose/source contract surfaces.
        if parts & {".git", ".worktrees", ".cache", "__pycache__"}:
            continue
        if suffix in {".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf"}:
            continue

        full_path = ROOT / path
        try:
            full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        paths.append(full_path)

    return paths


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
        companions = prose(section(self.skill_text, "Optional Companion Skills"))
        self.assertIn("explicitly authorizes its installation", companions)
        self.assertIn("Never install it silently", companions)
        self.assertIn("not required for ordinary SMEDC work", companions)

    def test_evidence_answers_surface_every_automatic_source_link(self) -> None:
        downloads = prose(section(self.skill_text, "Quarantine Certificates And Source Downloads"))
        self.assertIn("search_document_evidence` already returns `sources[]", downloads)
        self.assertIn("show every entry", downloads)
        self.assertIn("Do not call `get_source_document_download_url` again", downloads)
        self.assertIn("SOURCE_DOWNLOAD_URL_UNAVAILABLE", downloads)

    def test_every_active_launcher_reference_uses_the_exact_pin(self) -> None:
        active = {
            "Skill approved package": self.skill_text.split("\n## ", 1)[0],
            "Skill update pin": section(self.update_guide, "Continue Within The Requested Scope"),
            "README release status": self.readme_text.split("\n## ", 1)[0],
            "README.zh release status": self.readme_zh_text.split("\n## ", 1)[0],
            "README install": section(self.readme_text, "Official Launcher"),
            "README.zh install": section(self.readme_zh_text, "正式 Launcher"),
        }
        for heading in [
            "Official Install Or Update",
            "Device-Code Login Flow",
            "Configure The Invoking Agent",
            "Removal And Complete Uninstall",
        ]:
            active[heading] = section(self.skill_text, heading)
        for label, content in active.items():
            with self.subTest(section=label):
                versions = launcher_versions(content)
                self.assertTrue(versions, f"No launcher references in {label}")
                self.assertEqual({"0.5.2"}, set(versions))

    def test_install_guidance_uses_current_repository_and_skill_name(self) -> None:
        for document, install_heading, update_heading, launcher_heading in [
            (self.readme_text, "Install The Skill", "Update The Skill", "Official Launcher"),
            (self.readme_zh_text, "安装 Skill", "更新 Skill 本体", "正式 Launcher"),
        ]:
            with self.subTest(language=install_heading):
                install = section(document, install_heading)
                self.assertIn("YinXiaoyu-1998/smedc-mcp-skill", section(document, update_heading))
                self.assertIn("~/.agents/skills/smedc-mcp", install)
                self.assertIn("skills/smedc-mcp", install)
                self.assertIn(
                    "SMEDC_BASE_URL=https://api.smedatacenter.xyz",
                    section(document, launcher_heading),
                )

    def test_linux_launcher_support_is_actionable_and_bounded(self) -> None:
        linux_launcher_directory = (
            "${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.5.2"
        )

        install = prose(section(self.skill_text, "Official Install Or Update"))
        device = prose(section(self.skill_text, "Device-Code Login Flow"))
        self.assertIn("macOS, Windows, or Linux", install)
        self.assertIn(linux_launcher_directory, install)
        self.assertIn(linux_launcher_directory, section(self.readme_text, "Official Launcher"))
        self.assertIn(linux_launcher_directory, section(self.readme_zh_text, "正式 Launcher"))
        self.assertIn("headless Linux", device)
        self.assertIn("openedBrowser: false", device)
        self.assertIn("memory only", device)
        self.assertIn("launcher or host restart", device)
        self.assertIn("openclaw mcp add smedc", section(self.skill_text, "Configure The Invoking Agent"))

    def test_admin_only_upload_guidance_precedes_local_file_access(self) -> None:
        upload = section(self.skill_text, "Admin-Only Uploads")
        # Preserve exact canonical wire values; normalize ordinary prose below.
        self.assertIn("`403 UPLOAD_ADMIN_REQUIRED`", upload)
        self.assertIn("`File upload requires the admin role.`", upload)
        self.assertIn("`retryable: false`", upload)
        for term in [
            "Only active accounts with role `admin` may upload",
            "do not read or transform the local file",
            "Do not re-login or retry",
            "remain visible",
            "Do not dynamically hide or remove upload tools",
            "Clearance is not upload permission",
            "above their own clearance",
            "creates no backend audit",
            "file_upload.denied",
            "delivery_ledger",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, prose(upload))
        questions = prose(section(self.skill_text, "SMEDC Data Questions"))
        self.assertNotIn("offer to upload it first", questions)

    def test_old_current_identities_are_absent_from_tracked_text_files(self) -> None:
        matches: list[str] = []

        for path in tracked_repository_text_files():
            relative_path = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                for term in old_identity_terms():
                    if term in line:
                        matches.append(f"{relative_path}:{line_number}: {term}")

        self.assertEqual(
            [],
            matches,
            "Old product, Skill, package, env, MCP, or tenant names remain.",
        )


if __name__ == "__main__":
    unittest.main()
