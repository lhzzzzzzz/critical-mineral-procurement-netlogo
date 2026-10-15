"""第 0 组：从风险实验提取 risk=2 的基准，比较 k=1/2/3；不新增模拟。"""
from common import begin, finish, select, paired, mean, fmt


def main():
    args, rows, groups = begin(0)
    pairs = {f"baseline-k{b}minus{a}": paired(select(rows, k=a), select(rows, k=b)) for a, b in [(1, 2), (2, 3), (1, 3)]}
    conclusions = [
        f"合作 {k} 家：平均满足率 {fmt(mean(groups, 'service', k=k))}%；平均总开支 {fmt(mean(groups, 'cost', k=k))}；平均单位开支 {fmt(mean(groups, 'unit_cost', k=k))}。"
        for k in (1, 2, 3)
    ]
    for a, b in [(1, 2), (2, 3)]:
        d = pairs[f"baseline-k{b}minus{a}"]
        s, c = d["service"], d["unit_cost"]
        conclusions.append(f"{b} 家减 {a} 家：满足率 +{s['mean']:.2f} 个百分点，95% CI [{s['lo']:.2f}, {s['hi']:.2f}]；单位开支 +{c['mean']:.2f}，95% CI [{c['lo']:.2f}, {c['hi']:.2f}]。")
    conclusions.append("第 0 组是统一基准的汇总，90 场来自第 1 组，不是新增的独立实验。更多伙伴的服务优势必须与其单位开支一起解释，不能据此选择利润最优策略。")
    finish(args, rows, groups, pairs, 0, conclusions)


if __name__ == "__main__":
    main()
