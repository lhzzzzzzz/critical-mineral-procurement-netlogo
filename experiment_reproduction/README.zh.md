# 第 0–6 组实验：从 BehaviorSpace CSV 到结论

先打开 [复现结果总览](outputs/index.html)，或阅读 [全部中文结论](outputs/all_conclusions.zh.txt)。

这里保存了 **7 个可单独运行的分析文件、6 份重新生成的 BehaviorSpace Table CSV、每组统计输出和历史对照记录**。不需要从 HTML 中手动抄参数，也不需要安装 pandas。Python 3.9 或以上即可完成分析。

## 七个文件分别做什么

| 脚本 | 输入 CSV（`raw/`） | 实验 | 输入行数 |
|---|---|---|---:|
| `00_baseline.py` | `01_risk.csv` 中风险 2% 的行 | 同一基准下 k=1/2/3 | 提取 90 |
| `01_risk.py` | `01_risk.csv` | 风险 0/2/5% | 270 |
| `02_capacity.py` | `02_capacity.csv` | 产能 60/80/100 × 风险 0/2% | 540 |
| `03_inventory.py` | `03_inventory.csv` | 目标库存 0/1/2 倍需求 × 风险 0/2% | 540 |
| `04_transport.py` | `04_transport.csv` | 运费系数 2/3/4，风险 2% | 270 |
| `05_price_feedback.py` | `05_price_feedback.csv` | 反馈 0/0.20/0.40 × 风险 0/2% | 540 |
| `06_fees.py` | `06_fees.csv` | 目标 0/1/2 × F=0/50/100 × H=0/1/2，风险 2% | 2,430 |

所有条件均比较 k=1/2/3，使用 30 个情景（scenario-seed 2026–2055，map-seed 1–30），每场 500 cycle。每组只改变表中因素，其余参数采用原报告基准：5 家供应商、10 家制造商、产能基准 100、需求 30–50、初始库存 40–80、目标倍数 1、运费 3、价格反馈 0.20、维护费 50、持有费 1、随机故障时长 1–10，指定断供关闭。

**第 0 组是基准总览，不需要第七份 BehaviorSpace 导出。** 它从风险实验中筛出 90 场基准。前五个模拟网格共有 2,160 行，但去除跨组重叠后是 1,530 个参数/情景组合。费用组的 2,430 场对应 270 条物理情景 × 9 种费用变体，不能当成新增的独立样本。

## 直接重算已保存的 CSV

在项目根目录运行：

```bash
python3 experiment_reproduction/run_all.py
```

这只重新读取 CSV、计算统计和生成总览，不重新运行 NetLogo。

单独重算一组：

```bash
python3 experiment_reproduction/03_inventory.py
```

使用自己从 BehaviorSpace 导出的文件，输入输出路径均可指定：

```bash
python3 experiment_reproduction/03_inventory.py --input "/你的路径/inventory.csv" --output "/你的路径/inventory_results"
```

BehaviorSpace 导出时选择 **Table output**。脚本会自动找到真正的表头，跳过前面的 NetLogo 元信息。若勾选了逐周期记录，会按运行编号取最后一行；最后一步必须为 500。缺少情景、重复参数/seed、未完成运行、控制参数不一致、数量或费用不守恒都会报错，不会生成“看起来正常”的统计结论。

当前脚本专门复现原报告的网格和 30 个情景；改变种子范围、周期或实验参数后，需要同步调整实验协议与统计校验，不能直接声称复现了原报告。

## 每组 output 怎么看

输出在 `outputs/00_baseline/` 到 `outputs/06_fees/`：

- `conclusions.zh.txt`：带数值的中文解释，适合复习和 viva。
- `runs.csv`：清理后的逐场数据；没有把每个 cycle 当作一行独立样本。
- `summary.csv`：每个条件、每个指标的 mean、lo、hi、sample SD、n。`lo/hi` 是 95% 区间端点。
- `paired_differences.csv`：同 seed 的“后者 − 前者”，再统计均值与区间。差值名称说明方向，例如 `baseline-k2minus1`。
- `results.json`：同一结果的结构化版本，包含输入文件 SHA-256、指标缺失情况和验证状态。
- `reference_comparison.csv`：新计算值与原报告逐项对照，保留误差及 pass/fail/unavailable。
- 费用组另有 `rerun_vs_repricing.csv`：每场实际成本与独立重新计价的差值。

总览文件包括 `outputs/index.html`、`outputs/all_conclusions.zh.txt`、`outputs/reproduction_check.csv` 和 `.json`。CSV 以 UTF-8 BOM 保存，方便表格软件读取中文；空白指标表示不可用，不表示 0。

## 核心计算规则

1. 每场满足率 = 累计满足需求 / 累计需求 × 100%。累计需求可由“满足 + 未满足”恢复。
2. 每场单位开支 = 累计总开支 / 累计满足需求。先算每场比率，再对 30 场取算术平均；**不是把 30 场分子分母汇总后再相除**。
3. 均值 95% 区间 = mean ± 2.045229642132703 × sample SD / √30，使用 29 个自由度；不裁剪区间，也没有多重比较校正。
4. 策略差异先按同一个情景 seed 配对，计算差值，再对 30 个差值使用相同区间公式。CSV 的导出顺序无关紧要。
5. 平均实际库存 = 各周期期末库存之和 / 500。持有费率为正且固定时，可由“累计持有费 / 费率 / 500”恢复；它不是最终库存，也不是目标库存。
6. 费用组独立重新计价 = 采购费 + 运费 + F × 合同数 × 500 + H × 各周期期末库存之和。基准取自**新费用 CSV 自己的 F50/H1 行**，不依赖历史参考。

## 普通 CSV 足够吗

根目录模型的六组默认导出能复现满足率、费用、期末库存、平均库存等主要结论。不过原报告还分析了实际总产能、闲置产能、断供暴露、客户缺货周期等。普通 CSV 没有这些累计观测，不能事后凭空推算。

本次 `run_behaviorspace.py` 在 `models/` 中保留两份副本：

- `source.nlogox`：此次运行依据的原模型快照。
- `observed.nlogox`：只增加计数变量、记录过程和输出指标。每期先调用原来的 `go`，再在 `with-local-randomness` 中记录。原模型的选商、报价、下单、断供、分配和库存规则不变，根目录模型文件没有被本任务改写。

`raw/` 的六份 CSV 是使用 **实际 NetLogo BehaviorSpace** 在观测副本上重新生成的，并非从旧报告改写出来的 CSV。它们包含标准指标及附加观测，足够复现 00–06 的原有主指标和机制结论。原始 CSV、日志、模型快照、运行命令与文件哈希都保留了。

如果更习惯在界面里运行，可以在 NetLogo 打开 `models/observed.nlogox`，进入 Tools → BehaviorSpace，运行对应实验并导出 Table CSV。该副本仍有相同六组参数定义，导出的列包含上述附加观测；把文件交给相应编号的 Python 脚本即可。

分析脚本也接受根目录模型的普通 CSV：能算的指标正常计算，缺少的指标明确记为 unavailable，历史核对记为 partial。费用 H=0 的库存总和可从同一 CSV 中同 seed/策略/库存目标、H>0 的配对行恢复，同时检查费用变体的实物结果确实相同；不从历史文件借用数据。

## 从头重新跑 NetLogo

需要本机 Java 与 NetLogo 7.0.4；分析 CSV 本身不需要它们。

```bash
python3 experiment_reproduction/run_behaviorspace.py
python3 experiment_reproduction/run_all.py
```

默认使用两个后台工作线程，依次运行六组。首次运行会创建模型副本；每组完成后才把 `.partial.csv` 改成正式 `.csv`，并保存日志和 `raw/run_manifest.json`。重新执行会覆盖本目录对应输出，要保留不同批次时指定 `--output`。

安装位置不同可明确指定：

```bash
python3 experiment_reproduction/run_behaviorspace.py --netlogo "/你的路径/NetLogo 7.0.4" --java "/你的路径/bin/java"
```

仅重跑一个实验，例如费用组：

```bash
python3 experiment_reproduction/run_behaviorspace.py --only 06_fees --output "/你的路径/new_run/raw"
```

该命令会把对应模型副本保存到 `new_run/models/`。`--plain` 可以原样运行根目录模型，输出不含附加观测；请选不同输出目录，以保留本次完整观测结果。

## 原报告参考与复现范围

`extract_reference.py` 从根目录 `experiment-results.html` 的内嵌 ZIP 提取 `reference/`。这里保留历史逐场 CSV、统计 JSON、参数清单、模型与原分析程序，以及来源哈希。历史文件只在结果计算之后用于核对，**不参与新统计、不补缺失指标、不执行历史脚本**。

后续变量精简删除了根目录模型中三个未使用的记录变量。这里已经产生结果的模型快照和 CSV 保留原样，以维持哈希与来源对应；再次运行脚本会读取当前根目录模型。删除清单和回归说明见 [变量检查](../docs/variable-audit.zh.md)。

```bash
python3 experiment_reproduction/extract_reference.py
```

逐场指标、组均值/区间和原有配对比较采用绝对容差 1e-6、相对容差 1e-9；CSV 数值会保留浮点舍入差，不强行替换成旧值。`outputs/reproduction_check.json` 是本次实际核对状态。

范围是报告的 **00 基准和 01–06 主实验**。报告末尾另外的 1,000-cycle 长期窗口检查、200-cycle 指定断供演示不属于这七组，没有冒充本次已重新运行。模型中的金额是抽象运营开支，初始库存未计购入成本、终端库存无抵扣，因此不能从成本直接推断利润或现实最优策略。

原 HTML 有一处正文舍入笔误：单供应商、风险 2%、目标 2 的满足率精确均值为 63.585065868421935%，保留两位应为 **63.59%**；原正文写成 63.58%，其数据表与原始数据正确。本文件夹按原始数值计算，没有修改原报告。

## 检查分析程序

```bash
python3 -m unittest discover -s experiment_reproduction -p 'test_analysis.py' -v
```

检查重点包括真实普通 CSV 的兼容性、费用为零时的处理、乱序配对、重复/缺失情景的拒绝、未完成运行和账目错误的拒绝。主要统计公式集中在 `common.py`；七个编号脚本分别保留各组的对比选择与中文解释。
