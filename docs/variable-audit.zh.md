# 变量精简检查

本次按“是否被模型决策、界面、六组 BehaviorSpace 输出或现有复现程序使用”检查了开头的全部声明。局部 `let`、NetLogo 内置属性以及界面自动产生的 14 个输入变量不计入以下数量。

**原有 79 个显式声明；确认冗余并删除 3 个，现有 76 个。** 逻辑源码由 675 行减至 667 行，47 个过程未改变。

## 删除清单

| 变量 | 原来记录什么 | 为什么可以删除 |
|---|---|---|
| `unplaced-order` | 希望补货中没有提交给任何伙伴的数量 | 只有赋值，没有后续读取；没有进入决策、界面控件、实验指标或 Python 分析。需要检查时可临时计算 `order-quantity - sum [units-ordered] of my-out-contracts`。 |
| `buyer-cumulative-cost` | 单个制造商的累计总支出 | 只用旧值加本期费用，自我累加后没有消费者；全网累计费用由 `update-network-totals` 独立计算。 |
| `buyer-total-cost` | 单个制造商的本期四类支出之和 | 唯一用途是累加到上面那个未使用的个人累计值；删除个人累计记录后，此变量也成为冗余。 |

`buyer-total-cost` 并非字面意义上的“从未读取”，但它唯一服务的输出没有下游用途，所以整条记录链都可删。删除三项时也删除了相应赋值与加总语句；没有把同样的无用记录改名留下。

删除后，“想补货但没有可用伙伴”的情况仍然存在。模型保留希望补货量 `order-quantity`，实际合同订单为 0；只是没有另存一个未提交量。生产缺口 `unmet-demand` 与它不是一回事，继续保留。

## 声明数量

| 声明区 | 原来 | 现在 |
|---|---:|---:|
| `globals` | 41 | 41 |
| `suppliers-own` | 13 | 13 |
| `contracts-own` | 8 | 8 |
| `manufacturers-own` | 17 | 14 |
| 合计 | **79** | **76** |

## 为什么其余“记录变量”不能直接当成无用

- `cumulative-purchase-cost`、`cumulative-transport-cost`、`cumulative-relationship-cost`、`cumulative-holding-cost` 等：用于 BehaviorSpace CSV，以及费用实验的重新计价。它们不必影响决策，但属于研究输出。
- `initial-inventory-total`、`cumulative-received`：用于库存守恒及逐场结果核对。
- 制造商四项 `buyer-*-cost`：被 `update-network-totals` 读取，组成全网成本分项。
- `pricing-utilization`：记录当前报价所用的历史利用率；一期结束后它与已更新的 `capacity-utilization` 不同，Inspect 时能解释报价时点。
- `order-share`、`order-quantity`、`inventory-at-start`：分别参与分单、下单和生产结算，也帮助解释当期过程。
- 14 个 `*-setting` 内部参数副本：当前代码用它们做校验、场景恢复和运行中参数变更检查，同时为随机抽样与每期规则提供输入。可以重构这套参数读取方式，但它们目前都有实际读取，不属于此次删除的无用记录。

`manufacturer-id`、`route-distance` 等值可以改成即时计算；`pricing-utilization` 也可以通过改变检查方式省去存储。这属于进一步减少缓存/展示状态的重构，会影响 Inspect 中能看到的字段，不应混称为“没有任何作用”。本次保留它们。

## 验证与历史快照

本次对六组 BehaviorSpace 的所有参数取值组合使用情景 2026，进行了 **153 场 × 500 cycle** 的回归对照，检查服务、交付、库存和费用指标是否与原报告一致；另检查完全断供、零产能、零需求等边界。实际检查结果见同目录的 `variable-audit-validation.json`。

当前的两份 viva HTML 及生成程序已同步精简后的完整源码与行号。`experiment_reproduction/models/`、`experiment_reproduction/reference/` 以及原实验报告内嵌的模型是已经产生历史结果的快照，不改写这些文件；因此在历史快照里仍能搜到已删除变量。重新运行 `run_behaviorspace.py` 时默认读取根目录的当前模型。
