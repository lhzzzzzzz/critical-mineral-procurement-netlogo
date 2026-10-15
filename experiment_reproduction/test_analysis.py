"""对用户实际 CSV 工作流的验证；使用已保存数据，临时修改仅发生在临时目录。"""
from pathlib import Path
import csv
import json
import random
import subprocess
import sys
import tempfile
import unittest
from common import ROOT, FAMILIES, OPTIONAL_COLUMNS, read_behaviorspace, validate_grid, paired, select


def load_table(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.reader(stream))
    index = next(i for i, r in enumerate(rows) if r and r[0] == "[run number]")
    return rows[:index], rows[index], rows[index + 1:]


def save_table(path, meta, header, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerows(meta + [header] + rows)


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_all_seven_accept_real_plain_exports(self):
        """移除附加观测列，七个脚本仍能独立分析；缺失记录为 partial，不伪造数据。"""
        inputs = self.tmp / "raw"
        inputs.mkdir()
        for name in {x[2] for x in FAMILIES.values()}:
            meta, header, rows = load_table(ROOT / "raw" / f"{name}.csv")
            keep = [i for i, field in enumerate(header) if field not in set(OPTIONAL_COLUMNS.values()) | {"count contracts"}]
            save_table(inputs / f"{name}.csv", meta, [header[i] for i in keep], [[r[i] for i in keep] for r in rows])
        for family, (name, _, input_name, _) in FAMILIES.items():
            out = self.tmp / name
            p = subprocess.run([sys.executable, str(ROOT / f"{name}.py"), "--input", str(inputs / f"{input_name}.csv"), "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            actual = json.loads((out / "results.json").read_text())
            reference = json.loads((ROOT / "outputs" / name / "results.json").read_text())
            self.assertEqual(actual["reference_check"]["status"], "partial")
            self.assertEqual(actual["reference_check"]["failures"], 0)
            for a, b in zip(actual["groups"], reference["groups"]):
                for metric in ["service", "unit_cost", "avg_stock"]:
                    self.assertAlmostEqual(a["stats"][metric]["mean"], b["stats"][metric]["mean"], places=8)
            if family == 6:
                self.assertTrue(actual["mechanism_checks"]["repricing_matches_all_reruns"])

    def test_pairing_is_seed_based_not_row_order(self):
        rows = read_behaviorspace(ROOT / "raw/01_risk.csv")
        a, b = select(rows, k=1), select(rows, k=2)
        expected = paired(a, b)
        random.Random(42).shuffle(a)
        random.Random(7).shuffle(b)
        self.assertEqual(paired(a, b), expected)

    def test_missing_or_duplicated_scenarios_rejected(self):
        rows = read_behaviorspace(ROOT / "raw/01_risk.csv")
        with self.assertRaisesRegex(ValueError, "缺少"):
            validate_grid(rows[:-1], 1)
        with self.assertRaisesRegex(ValueError, "重复"):
            validate_grid(rows + [rows[0]], 1)

    def test_unfinished_run_rejected(self):
        meta, header, rows = load_table(ROOT / "raw/01_risk.csv")
        rows[0][header.index("[step]")] = "499"
        path = self.tmp / "incomplete.csv"
        save_table(path, meta, header, rows)
        with self.assertRaisesRegex(ValueError, "完整 500"):
            read_behaviorspace(path)

    def test_broken_cost_and_changed_controls_rejected(self):
        for field, value, message in [("cumulative-total-cost", "1", "成本守恒"), ("total-manufacturers", "20", "控制条件")]:
            meta, header, rows = load_table(ROOT / "raw/01_risk.csv")
            rows[0][header.index(field)] = value
            path = self.tmp / f"{field}.csv"
            save_table(path, meta, header, rows)
            with self.assertRaisesRegex(ValueError, message):
                read_behaviorspace(path)

    def test_duplicate_step_rejected(self):
        meta, header, rows = load_table(ROOT / "raw/01_risk.csv")
        path = self.tmp / "duplicated.csv"
        save_table(path, meta, header, rows + [rows[0]])
        with self.assertRaisesRegex(ValueError, "重复 run/step"):
            read_behaviorspace(path)

    def test_extra_cycle_rows_not_counted_as_replicates(self):
        meta, header, rows = load_table(ROOT / "raw/01_risk.csv")
        earlier = list(rows[0])
        earlier[header.index("[step]")] = "100"
        # 模拟逐周期导出：较早记录不应进入终点分析，也不能把行数当 n。
        path = self.tmp / "per_step.csv"
        save_table(path, meta, header, [earlier] + rows)
        normalized = read_behaviorspace(path)
        self.assertEqual(len(normalized), 270)
        validate_grid(normalized, 1)


if __name__ == "__main__":
    unittest.main()
