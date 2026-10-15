"""第 5 组：alpha=0/0.20/0.40 的消融；把服务效应与价格账单分开。"""
from common import begin, finish, select, paired, mean, fmt, close


def main():
    args, rows, groups = begin(5)
    pairs = {f"alpha-risk{risk}-k{k}-{alpha}minus0": paired(select(rows, k=k, risk=risk, alpha=0), select(rows, k=k, risk=risk, alpha=alpha))
             for risk in (0, 2) for k in (1, 2, 3) for alpha in (.2, .4)}
    for risk in (0, 2):
        base = select(rows, k=1, risk=risk, alpha=0)
        for alpha in (.2, .4):
            for a, b in zip(base, select(rows, k=1, risk=risk, alpha=alpha)):
                for metric in ["met", "received", "terminal_stock", "stock_sum"]:
                    close(a[metric], b[metric], f"单供应商的 {metric} 不应随 alpha 改变")
    conclusions = []
    for k in (1, 2, 3):
        d = pairs[f"alpha-risk2-k{k}-0.2minus0"]
        s, c = d["service"], d["unit_cost"]
        conclusions.append(f"风险 2%、合作 {k} 家：alpha 0.20−0 的服务差 {s['mean']:+.3f} 个百分点，95% CI [{s['lo']:.3f}, {s['hi']:.3f}]；单位开支差 {c['mean']:+.2f}，95% CI [{c['lo']:.2f}, {c['hi']:.2f}]。")
    conclusions += [f"alpha=0.40 时，双/三供应商满足率为 {fmt(mean(groups, 'service', k=2, alpha=.4))}% / {fmt(mean(groups, 'service', k=3, alpha=.4))}%。",
                    "当前反馈的服务改善很小，成本变化更大；统计区间可辨别的差异不代表业务影响很大。",
                    "单供应商在两档风险、30 个配对情景中，累计生产/交付、期末库存和库存总和均不受 alpha 影响。唯一伙伴无法通过报价改变订单份额，但采购账单会改变。"]
    finish(args, rows, groups, pairs, 5, conclusions, {"single_partner_physical_results_unchanged": True})


if __name__ == "__main__":
    main()
