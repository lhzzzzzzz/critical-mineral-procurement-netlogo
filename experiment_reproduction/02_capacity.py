"""第 2 组：基准产能 60/80/100 × 风险 0/2%；区分总量不足与闲置。"""
from common import begin, finish, select, paired, mean, fmt


def main():
    args, rows, groups = begin(2)
    pairs = {f"capacity-risk{risk}-k{k}-{cap}minus60": paired(select(rows, k=k, risk=risk, capacity=60), select(rows, k=k, risk=risk, capacity=cap))
             for risk in (0, 2) for k in (1, 2, 3) for cap in (80, 100)}
    conclusions = []
    for cap in (60, 80, 100):
        service0 = [mean(groups, "service", capacity=cap, risk=0, k=k) for k in (1, 2, 3)]
        service2 = [mean(groups, "service", capacity=cap, risk=2, k=k) for k in (1, 2, 3)]
        conclusions.append(f"产能基准 {cap}：无断供时 k=1/2/3 的满足率为 {' / '.join(fmt(v) for v in service0)}%；风险 2% 时为 {' / '.join(fmt(v) for v in service2)}%。")
    ratios = [mean(groups, "capacity_ratio", capacity=cap, risk=0) for cap in (60, 80, 100)]
    if all(x is not None for x in ratios):
        conclusions.append(f"基准产能 60/80/100 的平均实际总产能/总需求为 {' / '.join(fmt(v, 3) for v in ratios)}。60 时总量不足；提高伙伴数不能凭空增加供货能力。")
        idle = mean(groups, "avg_unused", capacity=100, risk=0, k=1)
        conclusions.append(f"产能基准 100、无断供、单供应商时，平均闲置可用产能 {fmt(idle, 1)} 单位/周期，同时满足率仅 {fmt(mean(groups, 'service', capacity=100, risk=0, k=1))}%。这支持固定合同下的分配拥堵解释。闲置产能不代表当前客户都能通过既有合同调用它。")
    else:
        conclusions.append("普通 CSV 可以复现满足率/开支，但缺少实际总产能、累计可用产能，不能数值复现‘总产能/需求’与‘闲置产能’；请使用观测副本的 CSV。")
    finish(args, rows, groups, pairs, 2, conclusions)


if __name__ == "__main__":
    main()
