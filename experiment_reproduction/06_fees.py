"""第 6 组：读取 2,430 场费用重跑，同时独立用同文件 F50/H1 轨迹重新计价。"""
from common import begin, finish, select, paired, mean, fmt, close, write_csv


def main():
    args, rows, groups = begin(6)
    base = {(r["seed"], r["k"], r["target"]): r for r in rows if r["F"] == 50 and r["H"] == 1}
    repriced = []
    for r in rows:
        original = base[r["seed"], r["k"], r["target"]]
        expected = original["purchase"] + original["transport"] + r["F"] * original["links"] * 500 + r["H"] * original["stock_sum"]
        for metric in ["met", "received", "terminal_stock", "stock_sum", "purchase", "transport"]:
            close(r[metric], original[metric], f"费用不会改变 {metric}")
        close(r["cost"], expected, "实际重跑必须与同轨迹重计价一致")
        repriced.append(dict(seed=r["seed"], k=r["k"], target=r["target"], F=r["F"], H=r["H"], actual_cost=r["cost"], repriced_cost=expected, difference=r["cost"] - expected))
    write_csv(args.output / "rerun_vs_repricing.csv", repriced)
    pairs = {}
    for k in (1, 2, 3):
        for target in (0, 1, 2):
            pairs[f"fee-F100minus0-k{k}-target{target}-H1"] = paired(select(rows, k=k, target=target, F=0, H=1), select(rows, k=k, target=target, F=100, H=1))
            pairs[f"fee-H2minus0-k{k}-target{target}-F50"] = paired(select(rows, k=k, target=target, F=50, H=0), select(rows, k=k, target=target, F=50, H=2))
    conclusions = ["全部 2,430 场费用重跑，与从该 CSV 的 270 条 F50/H1 基准轨迹重新计价一致。这里是实际运行次数，不是 2,430 个独立情景；每个条件仍只有 30 个配对情景。",
                   "重计价公式：采购费 + 运输费 + F × 合同数 × 500 + H × 各周期期末库存总和。该校验不使用历史报告的数据。"]
    for k in (1, 2, 3):
        fs = [mean(groups, "unit_cost", k=k, target=1, F=f, H=1) for f in (0, 50, 100)]
        hs = [mean(groups, "unit_cost", k=k, target=2, F=50, H=h) for h in (0, 1, 2)]
        conclusions.append(f"合作 {k} 家：目标 1、H=1 时，F=0/50/100 的单位开支为 {' / '.join(fmt(v) for v in fs)}；目标 2、F=50 时，H=0/1/2 的单位开支为 {' / '.join(fmt(v) for v in hs)}。")
    conclusions += ["所有费用变体的生产、交付和库存结果一致。当前费用只参与记账，不会触发重新选商、减少伙伴或降低目标库存。",
                    "因此本组检验既定策略对费用假设的敏感程度；没有收入或缺货损失，不能推断经济最优策略。"]
    finish(args, rows, groups, pairs, 6, conclusions, {"repricing_matches_all_reruns": True, "physical_trajectories_for_repricing": len(base), "fee_variants_per_trajectory": 9})


if __name__ == "__main__":
    main()
