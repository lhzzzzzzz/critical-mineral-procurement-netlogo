"""第 1 组：0/2/5% 新故障概率；其余条件固定为基准。"""
from common import begin, finish, select, paired, mean, fmt


def main():
    args, rows, groups = begin(1)
    pairs = {f"risk-k{k}-{risk}minus0": paired(select(rows, k=k, risk=0), select(rows, k=k, risk=risk)) for k in (1, 2, 3) for risk in (2, 5)}
    conclusions = []
    decreasing = True
    for k in (1, 2, 3):
        service = [mean(groups, "service", k=k, risk=risk) for risk in (0, 2, 5)]
        decreasing &= service[0] > service[1] > service[2]
        conclusions.append(f"合作 {k} 家，风险 0/2/5% 的满足率依次为 {' / '.join(fmt(v) for v in service)}%。")
    conclusions.append("三种策略均随风险升高而降低满足率。" if decreasing else "本次结果并非所有策略都随风险升高单调下降，应检查逐条件输出。")
    conclusions.append(f"风险为 0 时，单供应商满足率仍为 {fmt(mean(groups, 'service', k=1, risk=0))}%，因此无断供时已存在供应/分配限制，不能把多元采购的全部收益都称为抗断供收益。")
    exposure = mean(groups, "out_pct", k=1, risk=2)
    conclusions.append(f"2% 是正常供应商当期新故障概率；实际断供暴露为 {fmt(exposure, 3)}% 的供应商周期。持续故障会使暴露比例高于新发概率。" if exposure is not None else "普通 CSV 不记录实际断供暴露，无法仅从 2% 新发概率反推出报告中的约 10% 暴露；需要观测副本。")
    finish(args, rows, groups, pairs, 1, conclusions, {"service_decreases_with_risk": decreasing})


if __name__ == "__main__":
    main()
