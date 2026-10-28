import re
import json
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

    def test_published_cost_card_workflow_is_directory_and_local_csv_only(self) -> None:
        self.assertIn("references/cost-cards.md", self.skill_text)
        guide = read(SKILL_ROOT / "references" / "cost-cards.md")
        for contract in ["Launcher `0.14.0` is published and independently verified", "matching service rollout", "35", "38",
                         "query_structured_dataset", "download_cost_cards", "costCardIds",
                         "sourceDocumentId", "importBatchId", "revision", "finally",
                         "matched_product_name", "24 hours", "100", "32 KiB"]:
            with self.subTest(contract=contract):
                self.assertIn(contract, guide)
        self.assertIn("server-side detail filtering or aggregation", guide)
        self.assertIn("not an upload template", guide)
        self.assertIn("entire batch", guide)
        self.assertIn("Explicit IDs", guide)
        self.assertIn("same name", guide)
        for field in ["cost_card_id", "enterprise_name", "source_namespace", "spu_id", "sku_id",
                      "dish_name", "specification_name", "base_category_name", "sale_price",
                      "has_cost_card", "source_dish_deleted", "revision", "source_document_id",
                      "import_batch_id", "item_row_count", "recipe_count", "byte_size", "csv_schema_version"]:
            self.assertIn(f"`{field}`", guide)
        self.assertIn("archiving an original leaves active card", guide)
        self.assertIn("old successful idempotency key does not restore", guide)
        self.assertIn("group-level", guide)
        self.assertIn("no default grants", guide)
        self.assertIn("safe asynchronous", guide)
        self.assertIn("Only an `applied` batch", guide)
        self.assertIn("importBatch.publicationSummary", guide)
        self.assertIn("readable `sourceSheetSummary` remains an array", guide)
        for invariant in ["metadataPolicy: \"none\"", "selection is flat", "retryable 409",
                          "value.createdCount", "saving or resolving unsaved drafts",
                          "get_import_status({importBatchId})", "cost_card_<costCardId>.csv",
                          "archive_cost_card({costCardId})", "plus `fileName`", "Revoked access returns 404"]:
            self.assertIn(invariant, guide)

    def test_settled_orders_require_current_authorization_with_parameter_safe_examples(self) -> None:
        self.assertIn("references/settled-orders.md", self.skill_text)
        guide = read(SKILL_ROOT / "references" / "settled-orders.md")
        for contract in ["published, independently verified launcher `0.14.0`", "approved exact installation pin",
                         "`0.14.0`", "matching", "no grants", "finally", "31 columns", "结账方式JSON"]:
            with self.subTest(contract=contract):
                self.assertIn(contract, guide)
        examples = [(name, json.loads(payload)) for name, payload in re.findall(
            r"`([a-z_]+)` —[^\n]*\n\n```json\n([\s\S]*?)\n```", guide)]
        self.assertEqual(7, len(examples))
        upload = examples[0][1]
        self.assertEqual("settled_orders", upload["dataset"])
        self.assertEqual("path", upload["file"]["encoding"])
        self.assertNotIn("snapshotDate", upload)
        self.assertEqual({"requestId": "pd_synthetic_example"}, examples[-1][1])
        self.assertEqual("download_structured_partitions", examples[-1][0])

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
                self.assertEqual({"0.14.0"}, set(versions))

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

    def test_published_archive_reference_matches_install_pins(self) -> None:
        for path in sorted(SKILL_ROOT.rglob("*")):
            if path.suffix in {".md", ".yaml"}:
                with self.subTest(path=path.relative_to(SKILL_ROOT)):
                    self.assertTrue(set(launcher_versions(read(path))) <= {"0.14.0", "..."})
        reference = read(SKILL_ROOT / "references" / "ledger-pdf-tools.md")
        self.assertIn("0.14.0 is published and independently verified", reference)
        self.assertNotIn("once published", reference)
        self.assertIn("service archive delivery", reference)
        self.assertIn("references/ledger-pdf-tools.md", self.skill_text)

    def test_partition_bundle_flow_is_release_gated_and_parameter_safe(self) -> None:
        range_guide = section(self.skill_text, "Filtered Partition Range Downloads (Release Gated)")
        self.assertIn("`0.8.0`", range_guide)
        self.assertIn("`storeNameContains`", range_guide)
        self.assertNotIn("prepare_structured_partition_download", range_guide)
        self.assertNotIn("get_structured_partition_download_status", range_guide)
        guide = section(self.skill_text, "Optional Partition Bundle Downloads (Release Gated)")
        for text in ["approved exact pin", "Launcher `0.14.0`", "published and independently verified",
                     "server endpoints to be deployed", "prepare_structured_partition_download",
                     "get_structured_partition_download_status", "retryAfterSeconds", "isError",
                     "with only `requestId`", "does not wait for packaging", "1–128", "1–2000",
                     "case-sensitive", "NFC", "failed", "expired", "valid empty local extract",
                     "operator-only", "last consumer", "Range download is the default", "Tools/list alone cannot establish", "regenerate a saved"]:
            self.assertIn(text, guide)

    def test_archive_tool_table_exposes_only_frozen_public_inputs(self) -> None:
        reference = read(SKILL_ROOT / "references" / "ledger-pdf-tools.md")
        rows = ["| " + " | ".join(cell.strip() for cell in line.strip("|").split("|")) + " |"
                for line in reference.splitlines() if line.startswith("| `")]
        self.assertEqual(rows, [
            "| `describe_ledger_pdf_coverage` | date selection | `storeNames`, `cursor` |",
            "| `get_ledger_pdf_request_status` | `requestId` | `cursor` |",
            "| `prepare_ledger_pdf_download` | `storeNames`, date selection, `idempotencyKey` | none |",
            "| `get_ledger_pdf_download_url` | `requestId` | none |",
        ])

    def test_employee_archive_guidance_uses_scheduled_generation_only(self) -> None:
        reference = read(SKILL_ROOT / "references" / "ledger-pdf-tools.md")
        self.assertNotIn("refresh_ledger_pdfs", reference)
        self.assertIn("Employee agents cannot trigger", reference)
        self.assertIn("including admins", reference)
        self.assertIn("not PDF completion", self.skill_text)
        self.assertIn("cannot trigger generation through MCP or HTTP", self.skill_text)

    def test_store_review_examples_cover_platform_facts_and_omit_unread_text(self) -> None:
        guide = read(SKILL_ROOT / "references" / "store-reviews.md")
        examples = [(name, json.loads(payload)) for name, payload in re.findall(
            r"`(upsert_store_reviews|query_store_reviews)` —[^\n]*\n\n```json\n([\s\S]*?)\n```", guide)]
        self.assertEqual(11, len(examples))
        rows = [row for name, payload in examples if name == "upsert_store_reviews" for row in payload["reviews"]]
        self.assertEqual({"replied", "unreplied_no_content", "unreplied_with_content", "needs_verification"}, {row["replyStatus"] for row in rows if "replyStatus" in row})
        unknown = [row for row in rows if row.get("replyStatus") == "needs_verification"]
        self.assertTrue(unknown)
        self.assertNotIn("content", unknown[0])
        self.assertNotIn("merchantReply", unknown[0])
        self.assertEqual(["unreplied_no_content", "unreplied_with_content"], examples[-1][1]["replyStatuses"])
        self.assertFalse(examples[-1][1]["hasReply"])
        for row in rows:
            self.assertNotIn("draftReply", row)
            self.assertNotIn("aiSource", row)

    def test_published_feedback_examples_keep_same_minute_records_distinct(self) -> None:
        guide = read(SKILL_ROOT / "references" / "store-reviews.md")
        examples = [(name, json.loads(payload)) for name, payload in re.findall(
            r"`(upsert_store_reviews|query_store_reviews)` —[^\n]*\n\n```json\n([\s\S]*?)\n```", guide)]
        rows = [row for name, payload in examples if name == "upsert_store_reviews" for row in payload["reviews"] if "feedbackId" in row]
        self.assertEqual(["feedback-test-a", "feedback-test-b"], [row["feedbackId"] for row in rows])
        self.assertEqual(rows[0]["reviewerName"], rows[1]["reviewerName"])
        self.assertEqual(rows[0]["reviewedAt"], rows[1]["reviewedAt"])
        queries = [payload for name, payload in examples if name == "query_store_reviews" and "feedbackId" in payload]
        self.assertEqual("feedback-test-a", queries[0]["feedbackId"])

    def test_distributed_skill_has_no_retired_product_or_tenant_names(self) -> None:
        retired = re.compile(
            r"enterprise[- _]?hub|enterpricehub|maijia|麦家", re.IGNORECASE
        )
        for path in sorted(SKILL_ROOT.rglob("*")):
            if path.suffix not in {".md", ".yaml"}:
                continue
            with self.subTest(path=path.relative_to(SKILL_ROOT)):
                self.assertIsNone(retired.search(read(path)))


if __name__ == "__main__":
    unittest.main()
