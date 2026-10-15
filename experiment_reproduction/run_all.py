"""运行 00–06 分析，检查跨组重复基准，生成中文总览；默认使用已有 CSV。"""
from pathlib import Path
import argparse
import html
import json
import subprocess
import sys
from common import ROOT, FAMILIES, METRICS, PARAMS, close, write_csv


def cross_family_check(summaries):
    """交叉核对重叠实验，但不把重复运行平均成额外样本。"""
    index, duplicate_rows = {}, 0
    for family in range(1, 6):
        path = Path(summaries[family]["output_dir"]) / "runs.csv"
        import csv
        with path.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        for r in rows:
            key = tuple(float(r[k]) for k in PARAMS + ["seed"])
            if key in index:
                duplicate_rows += 1
                for metric in METRICS:
                    if r[metric] and index[key][metric]:
                        close(float(r[metric]), float(index[key][metric]), "跨组重叠基准不一致：" + metric)
            else:
                index[key] = r
    if len(index) != 1530 or duplicate_rows != 630:
        raise ValueError("前五组去重后的参数/seed 数量不符。")
    return {"first_five_rows": 2160, "distinct_core_runs": len(index), "duplicate_rows_not_independent": duplicate_rows,
            "all_overlapping_results_agree": True, "baseline_reuses_risk_rows": 90,
            "fee_rerun_rows": 2430, "fee_physical_cases": 270, "scenarios_per_condition": 30}


def render(summaries, output, audit):
    esc = html.escape
    sections = []
    nav = []
    readable = ["第 0–6 组实验复现总览", "=" * 60,
                "六份新的 BehaviorSpace Table CSV → 七份独立 Python 分析 → 与原 HTML 内嵌参考逐场核对。",
                "第 0 组复用第 1 组的基准；费用组为实际重跑，并独立验证重计价。", ""]
    checks = []
    for family, s in enumerate(summaries):
        name = FAMILIES[family][0]
        ref = s["reference_check"]
        checks.append(dict(family=family, title=s["title"], runs=s["rows"], conditions=s["conditions"], status=ref["status"],
                           comparisons=ref.get("comparisons", 0), failures=ref.get("failures", 0), unavailable=ref.get("unavailable", 0), max_absolute_error=ref.get("max_absolute_error")))
        nav.append(f'<a href="#e{family}">{family:02d} {esc(s["title"].split("：")[-1])}</a>')
        readable += [s["title"], f"{s['rows']} 场 / {s['conditions']} 个条件；核对状态：{ref['status']}", *s["conclusions"], ""]
        conclusions = "".join(f"<li>{esc(c)}</li>" for c in s["conclusions"])
        table = []
        for g in s["groups"]:
            values = [str(g[p]) for p in PARAMS]
            for metric in ["service", "unit_cost", "avg_stock", "avg_unused"]:
                stat = g["stats"][metric]
                values.append("不可用" if stat is None else f"{stat['mean']:.3f} [{stat['lo']:.3f}, {stat['hi']:.3f}]")
            table.append("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in values) + "</tr>")
        headers = ["k", "风险 %", "产能", "目标倍数", "运费", "α", "F", "H", "满足率 % [95% CI]", "单位开支 [95% CI]", "平均库存 [95% CI]", "闲置产能 [95% CI]"]
        sections.append(f'''<section id="e{family}"><h2>{esc(s['title'])}</h2>
<p class="status">{esc(ref['status'].upper())} · {s['rows']} 场 · {s['conditions']} 个条件 · 每条件 30 个情景</p>
<ol>{conclusions}</ol><p><a href="{name}/conclusions.zh.txt">中文结论</a> · <a href="{name}/summary.csv">均值及区间 CSV</a> · <a href="{name}/paired_differences.csv">配对差 CSV</a> · <a href="{name}/reference_comparison.csv">历史数值核对</a> · <a href="{name}/results.json">完整 JSON</a></p>
<details><summary>展开全部条件：均值与 95% 区间</summary><div class="scroll"><table><thead><tr>{''.join('<th>'+esc(h)+'</th>' for h in headers)}</tr></thead><tbody>{''.join(table)}</tbody></table></div></details></section>''')
    write_csv(output / "reproduction_check.csv", checks)
    result = {"status": "pass" if all(s["reference_check"]["status"] == "pass" for s in summaries) else "partial",
              "families": checks, "cross_family_checks": audit,
              "scope": "E0 overview and E1–E6, 500 cycles. The report's separate 1000-cycle horizon check and 200-cycle outage demonstration are outside this reproduction.",
              "numerical_tolerance": {"absolute": 1e-6, "relative": 1e-9}}
    (output / "reproduction_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "all_conclusions.zh.txt").write_text("\n".join(readable), encoding="utf-8")
    document = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>第 0–6 组实验复现结果</title><style>
body{font:16px/1.75 system-ui,sans-serif;color:#24343a;background:#f5f7f6;margin:0}main{max-width:1200px;margin:auto;padding:36px 24px 70px}h1{font-size:32px;line-height:1.3}h2{font-size:23px}a{color:#09656b}nav{display:flex;gap:10px 20px;flex-wrap:wrap;padding:16px 0}section{background:white;border:1px solid #d7e2de;padding:24px;margin:24px 0;scroll-margin-top:16px}.status{color:#28604e;font-weight:600}.note{color:#53666b}li{margin:10px 0}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px;white-space:nowrap;margin-top:16px}td,th{border-bottom:1px solid #d7e2de;padding:8px 12px;text-align:right}th{background:#ecf3f0}summary{cursor:pointer}footer{border-top:1px solid #ccd9d2;padding-top:24px}@media print{details{display:block}section{break-inside:avoid}nav{display:none}}
</style><main><h1>第 0–6 组实验复现结果</h1>
<p>新的 BehaviorSpace CSV → 独立 Python 计算 → 原报告参考核对。第 0 组复用基准；第 6 组实际重跑并验证重新计价。</p>
<p class="note">每场 500 cycle、每条件 30 个配对情景。均值是逐场比例的算术平均。区间使用 df=29 的 Student-t 临界值；策略差异按同一 seed 配对。</p>
<p><a href="reproduction_check.csv">七组核对汇总</a> · <a href="all_conclusions.zh.txt">全部中文结论</a> · <a href="../README.zh.md">运行说明</a></p><nav>'''+"".join(nav)+"</nav>"+"".join(sections)+'''
<footer><p>前五组 2,160 条记录，去重后 1,530 个参数/情景组合。费用重跑 2,430 场复用 270 种物理情景，不增加独立样本。未把 E0 或跨组重叠基准重复计入统计。</p>
<p>本次范围是原报告 00–06 的主实验；额外的 1,000-cycle 长期窗口检查和 200-cycle 指定断供演示不属于本次七组分析。人工参数的有限时域比较不证明真实供应链最优策略。</p></footer></main></html>'''
    (output / "index.html").write_text(document, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--reference", type=Path, default=ROOT / "reference")
    parser.add_argument("--simulate", action="store_true", help="先用本机 NetLogo 完整重跑六组。")
    args = parser.parse_args()
    if args.simulate:
        subprocess.run([sys.executable, str(ROOT / "run_behaviorspace.py"), "--output", str(args.input_dir)], check=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for family, (folder, _, input_name, _) in FAMILIES.items():
        out = args.output_dir / folder
        subprocess.run([sys.executable, str(ROOT / f"{folder}.py"), "--input", str(args.input_dir / f"{input_name}.csv"),
                        "--output", str(out), "--reference", str(args.reference)], check=True)
        summary = json.loads((out / "results.json").read_text(encoding="utf-8"))
        summary["output_dir"] = str(out)
        summaries.append(summary)
    audit = cross_family_check(summaries)
    render(summaries, args.output_dir, audit)
    print(f"Summary: {args.output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
