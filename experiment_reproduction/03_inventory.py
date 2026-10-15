"""第 3 组：目标库存 0/1/2 倍需求；初始库存抽样保持相同。"""
from common import begin, finish, select, paired, mean, fmt, close, SEEDS


def main():
    args, rows, groups = begin(3)
    pairs = {f"inventory-risk{risk}-k{k}-{target}minus0": paired(select(rows, k=k, risk=risk, target=0), select(rows, k=k, risk=risk, target=target))
             for risk in (0, 2) for k in (1, 2, 3) for target in (1, 2)}
    for k in (1, 2, 3):
        pairs[f"inventory-risk2-k{k}-2minus1"] = paired(select(rows, k=k, target=1), select(rows, k=k, target=2))
    for seed in SEEDS:
        same = [r for r in rows if r["seed"] == seed]
        for r in same:
            close(r["initial_stock"], same[0]["initial_stock"], "初始库存必须在政策间匹配")
    service = [mean(groups, "service", k=3, target=t) for t in (0, 1, 2)]
    stock = [mean(groups, "avg_stock", k=3, target=t) for t in (0, 1, 2)]
    first, second = pairs["inventory-risk2-k3-1minus0"]["service"], pairs["inventory-risk2-k3-2minus1"]["service"]
    conclusions = [
        f"风险 2%、三供应商：目标 0/1/2 的满足率为 {' / '.join(fmt(v) for v in service)}%；实际平均库存为 {' / '.join(fmt(v, 1) for v in stock)}。",
        f"目标 1−0：服务增加 {first['mean']:.2f} 个百分点，95% CI [{first['lo']:.2f}, {first['hi']:.2f}]；目标 2−1：增加 {second['mean']:.2f}，95% CI [{second['lo']:.2f}, {second['hi']:.2f}]。",
        f"第二份目标的服务增益{'较小' if second['mean'] < first['mean'] else '未较小'}，同时带来更高实际库存；这是当前参数范围的边际比较。",
        f"无断供、三供应商时，目标 1−0 的服务增益仍为 {pairs['inventory-risk0-k3-1minus0']['service']['mean']:.2f} 个百分点。目标会进入补货公式 Q=max(0,D+T−I)，因此实验同时包含补货政策作用和库存缓冲。",
        f"风险 2%、单供应商的目标 0/1/2 满足率为 {' / '.join(fmt(mean(groups, 'service', k=1, target=t)) for t in (0, 1, 2))}%，库存目标不能替代持续的供给能力。",
        "所有目标使用相同初始库存；目标 0 不是初始库存 0。报告一处正文把 63.585… 写成 63.58，按两位小数四舍五入应为 63.59；原报告表格及原始数据一致。",
    ]
    finish(args, rows, groups, pairs, 3, conclusions, {"initial_stock_matched": True})


if __name__ == "__main__":
    main()
