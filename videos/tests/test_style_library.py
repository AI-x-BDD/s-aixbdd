"""固定風格庫及實際建置入口的故障守門；不以此代替美術驗收。"""
from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

VIDEOS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VIDEOS / "scripts"))
import style_library as library
import motion_project as project


class FixedLibraryGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="fixed-style-library-")
        cls.root = Path(cls.temp.name)
        cls.lib = cls.root / "style-library"
        shutil.copytree(VIDEOS / "style-library", cls.lib)
        shutil.copytree(VIDEOS / ".agents/skills/huashu-art-motion",
                        cls.root / ".agents/skills/huashu-art-motion",
                        ignore=shutil.ignore_patterns("__pycache__"))
        cls.catalog = library.read(cls.lib / "catalog.json")
        cls.selection = cls.root / "selection.json"

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        # Simulate a separately carried tool package with its own fixed library.
        root_patch = patch.object(project, "TOOL_ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        library.write(self.lib / "catalog.json", self.catalog)
        self.choice = {"catalog_sha256": library.digest(self.lib / "catalog.json"),
                       "choices": [{"id": "y3_whiteboard", "content_reason": "逐步解釋借閱通知交接",
                                    "adaptation": "換成到期日、寄送系統及借閱者，按語音揭示後停留"}]}
        library.write(self.selection, self.choice)

    def test_current_library_and_selection(self):
        result = library.check(self.lib, self.selection)
        self.assertEqual("pass", result["status"], result["issues"])
        self.assertEqual({"explainer": 8, "art": 35}, result["counts"])
        self.assertEqual({"explainer": 7, "art": 34}, result["selectable_counts"])
        self.assertEqual(41, result["selectable"])

    def test_unknown_research_and_weak_ids_block(self):
        for name in ("invented-style", "research-paper-cut", "32_rembrandt", "y4_storytime"):
            with self.subTest(name=name):
                self.choice["choices"][0]["id"] = name
                library.write(self.selection, self.choice)
                self.assertEqual("fail", library.check(self.lib, self.selection)["status"])

    def test_stale_catalog_and_missing_content_reason_block(self):
        self.choice["catalog_sha256"] = "old-version"
        library.write(self.selection, self.choice)
        self.assertEqual("fail", library.check(self.lib, self.selection)["status"])
        self.choice["catalog_sha256"] = library.digest(self.lib / "catalog.json")
        self.choice["choices"][0]["content_reason"] = "  "
        library.write(self.selection, self.choice)
        self.assertEqual("fail", library.check(self.lib, self.selection)["status"])

    def test_missing_and_changed_preview_block(self):
        target = self.lib / self.catalog["entries"][0]["preview"]
        original = target.read_bytes()
        try:
            target.unlink()
            self.assertEqual("fail", library.check(self.lib)["status"])
            target.write_bytes(b"different encoded movie")
            self.assertEqual("fail", library.check(self.lib)["status"])
        finally:
            target.write_bytes(original)

    def test_changed_upstream_and_update_marker_block(self):
        upstream = self.root / ".agents/skills/huashu-art-motion"
        target = upstream / "SKILL.md"
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\nmodified\n")
            self.assertEqual("fail", library.check(self.lib)["status"])
        finally:
            target.write_bytes(original)
        marker = upstream / ".last-update-check"
        try:
            marker.write_text("uncontrolled update marker")
            self.assertEqual("fail", library.check(self.lib)["status"])
        finally:
            marker.unlink()

    def test_changed_preview_spec_blocks(self):
        entry = next(e for e in self.catalog["entries"] if e.get("spec_sha256"))
        target = self.lib / entry["spec"]
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\n ")
            self.assertEqual("fail", library.check(self.lib)["status"])
        finally:
            target.write_bytes(original)

    def test_build_gate_blocks_before_any_output(self):
        config_path = self.root / "new-film.toml"
        config_path.write_text('id="fresh-topic"\nstyle_library_required=true\n'
                               'style_library="style-library"\nstyle_selection="selection.json"\n')
        item = project.load_project(config_path, source_root=self.root)
        item["tool_root"] = self.root
        # Real subprocess check, including relative selection resolution.
        project.check_style_library(item)
        self.choice["choices"][0]["id"] = "invented-style"
        library.write(self.selection, self.choice)
        for operation in (project.command_prepare, project.command_render,
                          project.command_review, project.command_deliver):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(project.ProjectError):
                    operation(item)
                self.assertFalse(item["workspace"].exists())
                self.assertFalse(item["output"].exists())
        library.write(self.selection, {**self.choice, "choices": []})
        saved = self.lib / "catalog.saved"
        (self.lib / "catalog.json").rename(saved)
        try:
            with self.assertRaises(project.ProjectError):
                project.command_prepare(item)
        finally:
            saved.rename(self.lib / "catalog.json")

    def test_init_enables_library_for_new_profiles(self):
        target = self.root / "initialized.toml"
        if target.exists():
            target.unlink()
        data = project.load_project(target, allow_missing=True)
        self.assertTrue(data["config"]["style_library_required"])
        self.assertEqual("style-library", data["config"]["style_library"])

    def test_missing_gate_field_and_unexplained_opt_out_block(self):
        item = {"config": {}}
        with self.assertRaises(project.ProjectError):
            project.check_style_library(item)
        item["config"]["style_library_required"] = False
        with self.assertRaises(project.ProjectError):
            project.check_style_library(item)
        item["config"]["legacy_style_reason"] = "歷史重建隔離設定"
        project.check_style_library(item)

    def test_reuse_requires_current_real_decision_evidence(self):
        evidence = self.root / "user-decision.md"
        evidence.write_text("使用者確認沿用既有方向；本測試為人造證據檔。")
        reuse = {"catalog_sha256": library.digest(self.lib / "catalog.json"),
                 "reuse": {"evidence": evidence.name, "sha256": library.digest(evidence),
                           "adaptation": "新題材調整責任主體與實際語音時間"}}
        library.write(self.selection, reuse)
        self.assertEqual("pass", library.check(self.lib, self.selection)["status"])
        evidence.write_text("changed")
        self.assertEqual("fail", library.check(self.lib, self.selection)["status"])

    def test_malformed_choices_rejected(self):
        self.choice["choices"] = ["not-an-object"]
        library.write(self.selection, self.choice)
        with self.assertRaises(ValueError):
            library.check(self.lib, self.selection)

    def test_replacement_library_path_blocks(self):
        item = {"tool_root": self.root, "config": {"style_library_required": True,
                "style_library": "invented-library", "style_selection": "selection.json"}}
        with self.assertRaises(project.ProjectError):
            project.check_style_library(item)

    def test_config_ancestor_cannot_spoof_executable_tool_root(self):
        fake = self.root / "outside-tool-package"
        item = {"tool_root": fake, "config": {"style_library_required": True,
                "style_library": str(fake / "style-library"), "style_selection": "selection.json"}}
        with self.assertRaises(project.ProjectError):
            project.check_style_library(item)


if __name__ == "__main__":
    unittest.main()
