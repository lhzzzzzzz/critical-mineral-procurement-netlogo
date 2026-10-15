"""七组分析共用的读取与统计工具。仅用 Python 标准库，不需要 pandas。

重要口径：先算每场的满足率/单位开支，再对 30 场取平均；配对差按 seed 对齐。
历史 reference 只在 verify_reference() 中读取，不能填补新的输入数据。
"""
from pathlib import Path
from collections import defaultdict
from itertools import product
import argparse
import csv
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parent
T_29 = 2.045229642132703  # 双侧 95% Student-t 临界值，df=30-1，与原报告一致。
SEEDS = set(range(2026, 2056))
PARAMS = ["k", "risk", "capacity", "target", "freight", "alpha", "F", "H"]
DEFAULTS = dict(k=1, risk=2, capacity=100, target=1, freight=3, alpha=.2, F=50, H=1)
METRICS = ["service", "unit_cost", "cost", "met", "unmet", "received", "avg_stock", "terminal_stock", "initial_stock",
           "avg_unused", "available_util", "capacity_ratio", "out_pct", "buyer_short_pct", "used_suppliers", "largest_customer_group",
           "purchase", "transport", "links_cost", "holding"]
OPTIONAL_COLUMNS = {
    "stock_sum": "repro-stock-sum", "available_sum": "repro-available-sum", "unused_sum": "repro-unused-sum",
    "out_supplier_cycles": "repro-out-sum", "buyer_shortage_cycles": "repro-buyer-short-sum",
    "congested_supplier_cycles": "repro-congested-sum", "shortage_cycles": "repro-shortage-cycles",
    "normal_capacity": "sum [capacity] of suppliers", "demand_per_cycle": "sum [demand] of manufacturers",
    "used_suppliers": "count suppliers with [any? my-in-contracts]", "largest_customer_group": "max [count my-in-contracts] of suppliers",
}
FAMILIES = {
    0: ("00_baseline", "第 0 组：统一基准下的三种采购策略", "01_risk", {}),
    1: ("01_risk", "第 1 组：断供风险", "01_risk", {"risk": [0, 2, 5]}),
    2: ("02_capacity", "第 2 组：供应商产能", "02_capacity", {"capacity": [60, 80, 100], "risk": [0, 2]}),
    3: ("03_inventory", "第 3 组：库存目标", "03_inventory", {"target": [0, 1, 2], "risk": [0, 2]}),
    4: ("04_transport", "第 4 组：运输系数", "04_transport", {"freight": [2, 3, 4]}),
    5: ("05_price_feedback", "第 5 组：价格反馈", "05_price_feedback", {"alpha": [0, .2, .4], "risk": [0, 2]}),
    6: ("06_fees", "第 6 组：维护费与持有费", "06_fees", {"F": [0, 50, 100], "H": [0, 1, 2], "target": [0, 1, 2]}),
}


def number(value, label):
    if value in (None, "", "false", "true"):
        raise ValueError(f"{label} 缺失或不是数值：{value!r}")
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{label} 不是有限数值。")
    return x


def close(a, b, label, rel=1e-9, absolute=1e-5):
    if not math.isclose(a, b, rel_tol=rel, abs_tol=absolute):
        raise ValueError(f"{label}: {a} != {b}")


def ratio(a, b, multiplier=1):
    return None if a is None or b is None or b == 0 else multiplier * a / b


def read_behaviorspace(path):
    """识别 Table 导出元信息。若逐步记录，按 run number 取最后一行，而非把 cycle 当样本。"""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        all_rows = list(csv.reader(stream))
    header_index = next((i for i, row in enumerate(all_rows) if row and row[0] == "[run number]" and "[step]" in row), None)
    if header_index is None:
        raise ValueError("未找到 BehaviorSpace Table 表头；请导出 Table CSV，而非 Spreadsheet 格式。")
    header = all_rows[header_index]
    if len(header) != len(set(header)):
        raise ValueError("CSV 有重复列名。")
    runs = {}
    seen_steps = set()
    for line_number, values in enumerate(all_rows[header_index + 1:], header_index + 2):
        if not values:
            continue
        if len(values) != len(header):
            raise ValueError(f"第 {line_number} 行列数异常；可能是未完成的导出。")
        d = dict(zip(header, values))
        run, step = number(d["[run number]"], "run"), number(d["[step]"], "step")
        if (run, step) in seen_steps:
            raise ValueError(f"重复 run/step: {run}/{step}")
        seen_steps.add((run, step))
        if run not in runs or step > number(runs[run]["[step]"], "step"):
            runs[run] = d
    normalized = []
    for run, d in sorted(runs.items()):
        n = lambda name, default=None: number(d.get(name, default), name)
        r = dict(run=run, seed=n("scenario-seed"), map=n("map-seed", n("scenario-seed") - 2025),
                 k=n("supplier-count"), risk=n("outage-risk"), capacity=n("supplier-capacity"),
                 target=n("inventory-target-multiplier", 1), freight=n("transport-cost-per-distance"),
                 alpha=n("price-response", .2), F=n("relationship-fee", 50), H=n("holding-fee-per-unit", 1),
                 cycles=n("[step]"), suppliers=n("total-suppliers"), manufacturers=n("total-manufacturers"))
        for param, expected in {"total-suppliers": 5, "total-manufacturers": 10, "min-demand": 30, "max-demand": 50,
                                "duration-min": 1, "duration-max": 10, "outage-supplier": 0}.items():
            close(n(param), expected, f"与报告的控制条件不同：{param}", rel=0, absolute=0)
        if r["cycles"] != 500 or r["map"] != r["seed"] - 2025:
            raise ValueError(f"Run {run}: 需要完整 500 周期和 map=seed-2025 的配对设置。")
        for metric, column in {
            "met": "cumulative-fulfilled", "unmet": "cumulative-unmet", "received": "cumulative-received",
            "cost": "cumulative-total-cost", "initial_stock": "initial-inventory-total", "terminal_stock": "total-inventory",
            "purchase": "cumulative-purchase-cost", "transport": "cumulative-transport-cost",
            "links_cost": "cumulative-relationship-cost", "holding": "cumulative-holding-cost",
        }.items():
            r[metric] = n(column)
            if r[metric] < -1e-6:
                raise ValueError(f"Run {run}: {metric} 不应为负。")
        r["demand"] = r["met"] + r["unmet"]
        r["links"] = n("count contracts", r["k"] * r["manufacturers"])
        r["service"] = ratio(r["met"], r["demand"], 100)
        r["unit_cost"] = ratio(r["cost"], r["met"])
        for metric, column in OPTIONAL_COLUMNS.items():
            r[metric] = n(column) if column in d else None
        if r["stock_sum"] is None and r["H"] > 0:
            r["stock_sum"] = r["holding"] / r["H"]
            r["stock_source"] = "holding_cost / positive_holding_fee"
        else:
            r["stock_source"] = "observation" if r["stock_sum"] is not None else "unavailable"
        close(r["initial_stock"] + r["received"], r["met"] + r["terminal_stock"], "库存守恒")
        close(r["cost"], sum(r[k] for k in ["purchase", "transport", "links_cost", "holding"]), "成本守恒")
        close(r["links"], r["manufacturers"] * r["k"], "固定合同数")
        close(r["links_cost"], r["F"] * r["links"] * r["cycles"], "维护费")
        close(n("overall-service-level"), r["service"], "满足率口径")
        close(n("operating-cost-per-unit-met"), r["unit_cost"], "单位开支口径")
        if r["stock_sum"] is not None:
            close(r["holding"], r["H"] * r["stock_sum"], "持有费")
        elif r["H"] == 0:
            close(r["holding"], 0, "零持有费")
        if r["available_sum"] is not None and r["unused_sum"] is not None:
            close(r["available_sum"], r["received"] + r["unused_sum"], "可用产能守恒")
        if r["demand_per_cycle"] is not None:
            close(r["demand"], r["cycles"] * r["demand_per_cycle"], "固定需求")
        normalized.append(r)
    # 普通费用 CSV 的 H=0 无法由费用反推库存；可从同文件、同情景同策略的 H>0 行恢复。
    stock_by_physical_case = {}
    physical_key = lambda r: tuple(r[k] for k in ["seed", "k", "risk", "capacity", "target", "freight", "alpha"])
    physical_metrics = ["met", "received", "terminal_stock", "purchase", "transport", "initial_stock"]
    for r in normalized:
        key = physical_key(r)
        if key in stock_by_physical_case:
            prior = stock_by_physical_case[key]
            for m in physical_metrics:
                close(r[m], prior[m], f"费用不应改变实物流/采购运费：{m}")
            if prior["stock_sum"] is not None and r["stock_sum"] is not None:
                close(prior["stock_sum"], r["stock_sum"], "费用不应改变库存轨迹")
        if key not in stock_by_physical_case or r["stock_sum"] is not None:
            stock_by_physical_case[key] = r
    for r in normalized:
        if r["stock_sum"] is None:
            donor = stock_by_physical_case[physical_key(r)]
            if donor["stock_sum"] is not None:
                r["stock_sum"] = donor["stock_sum"]
                r["stock_source"] = "same_physical_case_positive_fee_row_in_same_csv"
        r.update(avg_stock=ratio(r["stock_sum"], r["cycles"]), avg_unused=ratio(r["unused_sum"], r["cycles"]),
                 available_util=ratio(r["received"], r["available_sum"], 100),
                 capacity_ratio=ratio(r["normal_capacity"], r["demand_per_cycle"]),
                 out_pct=ratio(r["out_supplier_cycles"], r["suppliers"] * r["cycles"], 100),
                 buyer_short_pct=ratio(r["buyer_shortage_cycles"], r["manufacturers"] * r["cycles"], 100))
    return normalized


def expected_conditions(family):
    varying = {"k": [1, 2, 3], **FAMILIES[family][3]}
    return [dict(DEFAULTS, **dict(zip(varying, combination))) for combination in product(*varying.values())]


def validate_grid(rows, family):
    expected = {tuple(c[k] for k in PARAMS) + (seed,) for c in expected_conditions(family) for seed in SEEDS}
    keys = [tuple(r[k] for k in PARAMS) + (r["seed"],) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("相同参数/seed 有重复运行，不能把它们当独立样本。")
    missing, extra = expected - set(keys), set(keys) - expected
    if missing or extra:
        raise ValueError(f"实验网格不完整或参数不符：缺少 {len(missing)}，多出 {len(extra)}；要求每条件 seeds=2026..2055。")


def stat(values):
    """不裁剪百分比区间，不把缺失指标当成 0，不把 500 个 cycle 当 n=500。"""
    if any(v is None for v in values):
        return None
    if len(values) != 30:
        raise ValueError(f"本复现协议要求 n=30；实际 {len(values)}。")
    mean, sd = statistics.mean(values), statistics.stdev(values)
    half = T_29 * sd / math.sqrt(len(values))
    return dict(mean=mean, lo=mean - half, hi=mean + half, sd=sd, n=len(values))


def select(rows, **params):
    condition = dict(DEFAULTS, **params)
    return sorted([r for r in rows if all(r[k] == v for k, v in condition.items())], key=lambda r: r["seed"])


def grouped(rows):
    buckets = defaultdict(list)
    for r in rows:
        buckets[tuple(r[k] for k in PARAMS)].append(r)
    return [dict(zip(PARAMS, key), stats={m: stat([r[m] for r in rs]) for m in METRICS}) for key, rs in sorted(buckets.items())]


def paired(before, after):
    a, b = {r["seed"]: r for r in before}, {r["seed"]: r for r in after}
    if set(a) != SEEDS or set(b) != SEEDS:
        raise ValueError("配对样本没有完整且相同的 30 个 seed。")
    return {m: stat([None if a[s][m] is None or b[s][m] is None else b[s][m] - a[s][m] for s in sorted(SEEDS)]) for m in METRICS}


def write_csv(path, records):
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for r in records for k in r))
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def verify_reference(rows, groups, pairs, family, reference):
    """逐场、逐指标、逐区间校验历史结果；不能用历史值覆盖新值。"""
    if not reference.exists():
        return {"status": "not_run", "reason": "历史参考目录不存在；分析仍可独立完成。"}, []
    with (reference / "results-500.csv").open(newline="", encoding="utf-8-sig") as stream:
        old_rows = [{k: v if k == "id" else number(v, k) for k, v in r.items()} for r in csv.DictReader(stream)]
    core = ["seed", "k", "risk", "capacity", "target", "freight", "alpha"]
    old_index = {tuple(r[k] for k in core): r for r in old_rows}
    old_summary = json.loads((reference / "summary.json").read_text(encoding="utf-8"))
    comparisons = []

    def compare(kind, key, metric, actual, expected):
        if actual is None:
            comparisons.append(dict(kind=kind, case=key, metric=metric, actual=None, expected=expected, absolute_error=None, status="unavailable"))
            return
        delta = abs(actual - expected)
        ok = math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-6)
        comparisons.append(dict(kind=kind, case=key, metric=metric, actual=actual, expected=expected, absolute_error=delta, status="pass" if ok else "fail"))

    for r in rows:
        key = tuple(r[k] for k in core)
        old = old_index[key]
        fee_cost = old["purchase"] + old["transport"] + r["F"] * old["links"] * 500 + r["H"] * old["stock_sum"]
        overrides = dict(cost=fee_cost, unit_cost=fee_cost / old["met"], links_cost=r["F"] * old["links"] * 500, holding=r["H"] * old["stock_sum"])
        label = str(key + (r["F"], r["H"]))
        for m in METRICS:
            compare("run", label, m, r[m], overrides.get(m, old[m]))
    for group in groups:
        condition = {k: group[k] for k in PARAMS}
        if family == 6:
            old = next(g for g in old_summary["fees"] if all(g[k] == condition[k] for k in ["k", "F", "H", "target"]))
            historical_stats = {m: old[m] for m in ["service", "unit_cost", "avg_stock"]}
        else:
            old = next(g for g in old_summary["groups"] if all(g[k] == condition[k] for k in PARAMS[:6]))
            historical_stats = old["stats"]
        for metric, summary in historical_stats.items():
            for field in ["mean", "lo", "hi", "sd", "n"]:
                actual = group["stats"][metric]
                compare("group", str(condition), f"{metric}.{field}", None if actual is None else actual[field], summary[field])
    for name, stats in pairs.items():
        if name not in old_summary["pairs"]:
            continue  # 新增的易读对比没有旧汇总，可由逐场结果独立追溯。
        for metric, summary in old_summary["pairs"][name].items():
            for field in ["mean", "lo", "hi", "sd", "n"]:
                actual = stats[metric]
                compare("paired", name, f"{metric}.{field}", None if actual is None else actual[field], summary[field])
    failures = sum(r["status"] == "fail" for r in comparisons)
    unavailable = sum(r["status"] == "unavailable" for r in comparisons)
    result = {"status": "fail" if failures else ("partial" if unavailable else "pass"), "comparisons": len(comparisons),
              "failures": failures, "unavailable": unavailable,
              "max_absolute_error": max((r["absolute_error"] for r in comparisons if r["absolute_error"] is not None), default=0),
              "relative_tolerance": 1e-9, "absolute_tolerance": 1e-6,
              "reference": str(reference.resolve())}
    return result, comparisons


def begin(family):
    folder, title, filename, _ = FAMILIES[family]
    parser = argparse.ArgumentParser(description=title + "：读取 BehaviorSpace Table CSV，保存逐场、汇总、配对差和中文结论。")
    parser.add_argument("--input", type=Path, default=ROOT / "raw" / f"{filename}.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / folder)
    parser.add_argument("--reference", type=Path, default=ROOT / "reference")
    args = parser.parse_args()
    rows = read_behaviorspace(args.input)
    if family == 0:
        rows = [r for r in rows if all(r[k] == v for k, v in DEFAULTS.items() if k != "k")]
    validate_grid(rows, family)
    args.output.mkdir(parents=True, exist_ok=True)
    return args, rows, grouped(rows)


def mean(groups, metric, **params):
    condition = dict(DEFAULTS, **params)
    group = next(g for g in groups if all(g[k] == v for k, v in condition.items()))
    s = group["stats"][metric]
    return None if s is None else s["mean"]


def fmt(value, digits=2):
    return "不可用（CSV 未记录）" if value is None else f"{value:.{digits}f}"


def finish(args, rows, groups, pairs, family, conclusions, extra_checks=None):
    checks, comparisons = verify_reference(rows, groups, pairs, family, args.reference)
    missing = sorted({m for g in groups for m, v in g["stats"].items() if v is None})
    summary = {"family": family, "title": FAMILIES[family][1], "input": str(args.input.resolve()),
               "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(), "rows": len(rows), "conditions": len(groups),
               "replicates_per_condition": 30, "cycles": 500, "groups": groups, "pairs": pairs,
               "unavailable_metrics": missing, "reference_check": checks, "mechanism_checks": extra_checks or {}, "conclusions": conclusions}
    write_csv(args.output / "runs.csv", rows)
    group_rows = []
    for g in groups:
        for metric, stats in g["stats"].items():
            group_rows.append({**{p: g[p] for p in PARAMS}, "metric": metric, **(stats or {"mean": None, "lo": None, "hi": None, "sd": None, "n": None}), "available": stats is not None})
    write_csv(args.output / "summary.csv", group_rows)
    pair_rows = []
    for name, stats in pairs.items():
        for metric, s in stats.items():
            pair_rows.append(dict(comparison=name, metric=metric, **(s or {"mean": None, "lo": None, "hi": None, "sd": None, "n": None}), available=s is not None))
    write_csv(args.output / "paired_differences.csv", pair_rows)
    write_csv(args.output / "reference_comparison.csv", comparisons)
    (args.output / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    notes = [FAMILIES[family][1], "=" * 48, f"数据：{args.input}", f"{len(groups)} 个条件 × 30 情景 = {len(rows)} 场，每场 500 cycle。", ""]
    notes.extend(f"{i}. {text}" for i, text in enumerate(conclusions, 1))
    notes += ["", "统计口径：先计算逐场比例，再取 30 场算术平均；95% 区间 = mean ± 2.045229642132703 × sample SD / sqrt(30)。",
              "配对比较先按 seed 计算后者减前者，再统计差值；区间未做多重比较校正。", "金额为抽象运营开支，初始库存未计购入成本，不能直接解释为利润或真实世界最优策略。",
              f"历史参考检查：{checks['status']}；详见 reference_comparison.csv。"]
    if missing:
        notes += ["当前 CSV 缺少观测，未用历史结果填充：" + ", ".join(missing), "需要这些指标时，运行 run_behaviorspace.py 生成观测副本和新的 CSV。"]
    (args.output / "conclusions.zh.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print(f"{FAMILIES[family][0]}: {len(rows)} rows; historical check={checks['status']}; output={args.output}")
    if checks["status"] == "fail":
        raise SystemExit("新结果与历史参考不一致，已保留差异记录。")
    return summary
