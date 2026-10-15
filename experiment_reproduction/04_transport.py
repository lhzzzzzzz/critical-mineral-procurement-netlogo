"""第 4 组：运费 2/3/4 在初始化选商之前生效，不只是事后重算账单。"""
from common import begin, finish, select, paired, mean, fmt


def main():
    args, rows, groups = begin(4)
    pairs = {f"freight-k{k}-4minus2": paired(select(rows, k=k, freight=2), select(rows, k=k, freight=4)) for k in (1, 2, 3)}
    conclusions = [f"合作 {k} 家，在运费系数 2/3/4 下满足率为 {' / '.join(fmt(mean(groups, 'service', k=k, freight=f)) for f in (2, 3, 4))}%。" for k in (1, 2, 3)]
    conclusions.append(f"单供应商的单位开支从系数 2 时的 {fmt(mean(groups, 'unit_cost', k=1, freight=2))} 增至系数 4 时的 {fmt(mean(groups, 'unit_cost', k=1, freight=4))}。")
    ordering = all(mean(groups, "service", k=3, freight=f) > mean(groups, "service", k=2, freight=f) > mean(groups, "service", k=1, freight=f) for f in (2, 3, 4))
    conclusions += ["三供应商的平均满足率在三档运费下均最高。" if ordering else "采购策略的服务排序随运费变化，不能概括成固定排序。",
                    "运费在初始化选商前进入到货成本，所以会改变合作网络、份额和运输账单。服务变化不能解释为单纯把同一批交付的运价调高；这是地理权重变化下的模型比较，不是真实运价估计。"]
    finish(args, rows, groups, pairs, 4, conclusions, {"service_order_3_gt_2_gt_1": ordering})


if __name__ == "__main__":
    main()
