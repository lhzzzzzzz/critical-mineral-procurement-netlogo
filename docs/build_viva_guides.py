"""Build two standalone, source-linked viva guides. Uses only Python's standard library."""
from pathlib import Path
import base64
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
RAW = (ROOT / 'model.nlogox').read_text()
MODEL = ET.fromstring(RAW)
CODE = MODEL.findtext('code')
LINES = CODE.splitlines()
SHA = hashlib.sha256((ROOT / 'model.nlogox').read_bytes()).hexdigest()
PROCS = {}
for match in re.finditer(r'(?m)^to(?:-report)? ([^\s\[]+)[^\n]*\n.*?^end(?=\n|$)', CODE, re.S | re.M):
    start = CODE[:match.start()].count('\n') + 1
    PROCS[match.group(1)] = (start, start + match.group().count('\n'), match.group())
assert len(PROCS) == 47

def esc(text):
    return html.escape(str(text), quote=True)

def table(headers, rows):
    return '<div class="table-scroll"><table><thead><tr>' + ''.join(f'<th scope="col">{x}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table></div>'

def src(name, label=None):
    return f'<a href="code-walkthrough.zh.html#proc-{name}"><code>{esc(label or name)}</code></a>'

def box(text):
    return f'<div class="note">{text}</div>'

def qa(q, a):
    return f'<details class="qa"><summary>{q}</summary><div>{a}</div></details>'

CSS = r'''
:root{--ink:#172d33;--muted:#52686c;--accent:#07695e;--soft:#eaf3ef;--line:#d4e2dd;--paper:#fff;--bg:#f4f7f5;--nav:246px}
*{box-sizing:border-box}html{scroll-padding-top:24px}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--accent);text-underline-offset:3px;overflow-wrap:anywhere}a:hover{text-decoration-thickness:2px}button,input,select{font:inherit}button,select{cursor:pointer}button,.button{border:1px solid #9fbcb1;border-radius:5px;color:var(--accent);background:white;padding:8px 13px;font-size:14px;text-decoration:none;line-height:1.5}button:hover,.button:hover{background:var(--soft)}button:disabled{cursor:default;opacity:.45}.primary,button[aria-pressed=true]{background:var(--accent);color:white}.primary:hover,button[aria-pressed=true]:hover{background:#075448}input,select{min-width:0;max-width:100%;background:white;color:var(--ink);padding:8px 10px;border:1px solid #9fbcb1;border-radius:5px}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #b15c19;outline-offset:4px}.skip{position:absolute;left:10px;top:-100px;background:white;z-index:10}.skip:focus{top:10px}
aside{position:fixed;inset:0 auto 0 0;width:var(--nav);overflow-y:auto;padding:30px 20px;background:#edf3ef;border-right:1px solid var(--line)}.brand{font-size:12px;letter-spacing:1px;color:var(--accent);font-weight:700}.nav-title{font-size:21px;line-height:1.5;margin:14px 0 22px;font-weight:700}nav a{display:block;text-decoration:none;padding:8px 10px;font-size:13px;line-height:1.6;margin:3px 0;border-radius:4px}nav a:hover,nav a.active{background:#dceae2}aside .related{border-top:1px solid var(--line);padding-top:18px;margin-top:22px}aside .related a{display:block;margin:9px 0;font-size:13px}.small,.meta{font-size:13px;color:var(--muted)}main{margin-left:var(--nav);padding:38px 45px 80px;max-width:1440px}header{padding:25px 0 32px;border-bottom:2px solid var(--accent)}h1{font-size:clamp(27px,3.2vw,42px);line-height:1.4;letter-spacing:-.7px;margin:13px 0 18px}header p{max-width:780px}.lead{font-size:18px;line-height:1.9}section{scroll-margin-top:24px}h2{font-size:27px;line-height:1.5;margin:55px 0 20px}h3{font-size:21px;line-height:1.6;margin:28px 0 13px}h4{font-size:17px;margin:20px 0 10px}p{margin:13px 0}li{margin:7px 0}ul,ol{padding-left:24px}.toolbar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:18px 0}.toolbar label{display:flex;gap:9px;align-items:center;flex-wrap:wrap}.note{padding:17px 20px;border-left:3px solid var(--accent);background:var(--soft);margin:24px 0}.note p:first-child{margin-top:0}.note p:last-child{margin-bottom:0}.formula{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px;background:#e9f0ee;padding:15px 18px;margin:16px 0;overflow-wrap:anywhere}code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em;background:#e7efeb;padding:2px 4px;border-radius:3px;overflow-wrap:anywhere}pre{margin:0;white-space:pre;overflow:auto;padding:17px 12px;background:#f0f4f2;font-size:12.5px;line-height:1.8;border-top:1px solid var(--line);tab-size:2}pre code{background:none;padding:0;font-size:inherit;overflow-wrap:normal}.code-line{display:block;min-height:1.8em}.ln{display:inline-block;width:42px;padding-right:13px;text-align:right;color:#64796d;user-select:none}.comment{color:#586f61}.keyword{color:#075e6d;font-weight:650}.code-line:target{background:#d4e8db}.table-scroll{overflow-x:auto;max-width:100%;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.8}th,td{text-align:left;vertical-align:top;padding:12px 13px;border-bottom:1px solid var(--line)}th{background:#e6eee9;font-weight:650}tbody tr:nth-child(even){background:#f9fbfa}.table-scroll table{min-width:560px}.narrow table{min-width:0}figure{margin:24px 0}figcaption{font-size:13px;color:var(--muted);margin-top:8px}.route{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:25px 0}.route>div{padding:18px;background:var(--paper);border-top:3px solid var(--accent)}.route strong{display:block}.route p{font-size:14px}.tag{font-size:12px;color:var(--accent);display:inline-block;margin-bottom:4px}.two{display:grid;grid-template-columns:1fr 1fr;gap:22px}.qa{border-bottom:1px solid var(--line);padding:13px 0}.qa summary{cursor:pointer;font-weight:650}.qa>div{padding:5px 0 9px;color:#304b44}.spoken{background:white;border:1px solid var(--line);padding:22px 24px;line-height:2}.spoken[lang=en]{line-height:1.9}.formula small{font-family:inherit}.steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin:18px 0}.steps button{text-align:left;font-size:12px;padding:10px;min-height:56px}.simulator{background:white;border:1px solid #b9d2c6;border-radius:7px;padding:24px}.sim-heading{font-size:23px;margin:10px 0}.phase-count{font-size:13px;color:var(--accent);font-weight:650}.state-flow{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center;margin:18px 0}.state-box{border-top:3px solid var(--accent);padding:12px;background:#eef5f1}.state-box strong{display:block}.state-box span{font-size:14px}.state-arrow{font-size:22px;color:var(--accent)}.step-note{min-height:72px}.status{font-size:13px;color:var(--muted)}.simulator .table-scroll{margin-bottom:8px}.simulator table{min-width:430px}.proc{border-top:1px solid #bccfc4;padding-top:12px;margin-top:32px;scroll-margin-top:24px}.proc h3{font-size:20px;overflow-wrap:anywhere;margin-top:10px}.proc h3 code{background:none;padding:0}.proc .signature{font-size:12px;color:var(--muted)}.proc details.source{background:white;border:1px solid var(--line);border-radius:5px;overflow:hidden;margin:18px 0}.source summary{padding:12px 15px;cursor:pointer;font-size:14px;font-weight:650}.proc:target{border-top:3px solid var(--accent)}.io{display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:14px}.io>div{background:#eaf1ed;padding:12px 16px}.io b{display:block;color:var(--accent)}.proc ol{font-size:15px}.proc .gotcha{font-size:14px;border-left:2px solid #9cb5a8;padding-left:14px}.searchbar{padding:18px;background:#e6efe9}.searchbar input{flex:1;min-width:180px}#procedure-count{min-width:90px}.group-index{display:flex;gap:8px;flex-wrap:wrap}.group-index a{font-size:13px;padding:5px 10px;background:#e5eee8;text-decoration:none;border-radius:4px}.hash{font:12px/1.8 ui-monospace,monospace;overflow-wrap:anywhere;color:var(--muted)}footer{margin-top:45px;border-top:1px solid var(--line);padding-top:18px}.print-only{display:none}[hidden]{display:none!important}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}.calltree{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid var(--line);padding:20px;background:white}.question{font-weight:650}.no-match{padding:22px;border:1px solid var(--line)}
@media(min-width:1600px){main{margin-left:calc(var(--nav) + (100vw - 1600px)/2)}}
@media(max-width:1100px){:root{--nav:215px}aside{padding:22px 13px}main{padding:24px}.route{grid-template-columns:1fr 1fr}.steps{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:780px){aside{position:relative;width:auto;padding:22px}.nav-title{margin:8px 0 12px}aside nav{columns:2}aside .related{display:flex;gap:15px;flex-wrap:wrap;margin-top:10px;padding-top:8px}main{margin-left:0;padding:18px 16px 50px}header{padding-top:8px}body{font-size:15px}h2{font-size:24px}.two,.io{grid-template-columns:1fr;gap:8px}.simulator{padding:17px}.steps button{font-size:12px}.state-flow{grid-template-columns:1fr}.state-arrow{transform:rotate(90deg);text-align:center;line-height:1}.toolbar{gap:8px}button,.button{min-height:42px}.table-scroll table{font-size:13px}.route{gap:9px}.route>div{padding:13px}.source summary{font-size:13px}.spoken{padding:17px}.proc h3{font-size:18px}}
@media(max-width:400px){.route{grid-template-columns:1fr}.steps{grid-template-columns:repeat(2,minmax(0,1fr))}aside nav{columns:1}.lead{font-size:16px}main{padding:15px 12px}.simulator{padding:12px}}
@media print{aside,.toolbar,.steps,.searchbar,.skip,.no-print,.simulator{display:none!important}.print-only{display:block}body{font-size:10.5pt;background:white;color:black}main{margin:0;padding:0;max-width:none}h1{font-size:23pt}h2{font-size:17pt;margin-top:26px}h3{font-size:13pt;break-after:avoid}header{padding-top:0}.note,.spoken,.proc,.source{break-inside:auto}tr{break-inside:avoid}a{color:inherit;text-decoration:none}table{font-size:9pt!important;min-width:0!important}.table-scroll{overflow:visible}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:8pt;overflow:visible}pre code{overflow-wrap:anywhere}.ln{width:30px}.route{grid-template-columns:1fr 1fr}details>summary{list-style:none}.io{grid-template-columns:1fr 1fr}.proc[hidden],.proc-group[hidden]{display:block!important}}
'''

COMMON_JS = r'''
document.querySelectorAll('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
let printState=[];
addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true)});
addEventListener('afterprint',()=>printState.forEach(([d,o])=>d.open=o));
if('IntersectionObserver' in window){const ob=new IntersectionObserver(entries=>{for(const en of entries)if(en.isIntersecting){document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('active',a.hash==='#'+en.target.id))}},{rootMargin:'-5% 0px -70% 0px'});document.querySelectorAll('section[id]').forEach(s=>ob.observe(s))}
'''

def page(title, subtitle, toc, content, js=''):
    nav = ''.join(f'<a href="#{i}">{t}</a>' for i,t in toc)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{esc(subtitle)}"><title>{esc(title)} · COMP90083 Viva</title><style>{CSS}</style></head>
<body id="top"><a class="skip" href="#main">跳到正文</a><aside><div class="brand">COMP90083 · VIVA NOTES</div><div class="nav-title">{title}</div><nav aria-label="本页目录">{nav}</nav><div class="related"><a href="cycle-walkthrough.zh.html">① 建模与 cycle 流程</a><a href="code-walkthrough.zh.html">② 完整代码讲解</a><a href="model-study-guide.zh.html">原界面学习指南</a><a href="../experiment-results.html">完整实验报告</a></div><p class="small">离线可读 · 无外部依赖<br>依据当前模型，2026-10-15</p><button type="button" data-print>打印 / 存为 PDF</button></aside><main id="main"><header><div class="meta">关键矿产采购网络 · NetLogo 7.0.4 · Viva 复习</div><h1>{title}</h1><p class="lead">{subtitle}</p></header>{content}<footer><p>源码依据：<a href="../model.nlogox">model.nlogox</a>，{len(LINES)} 行模型逻辑、47 个过程／reporter。本文是复习材料，教学案例与正式实验结果分别标明。</p><p class="hash">模型文件 SHA-256：{SHA}</p><a href="#top">回到顶部 ↑</a></footer></main><script>{COMMON_JS}\n{js}</script></body></html>'''

# Every procedure has an explanation of context, reads/writes, steps and a viva pitfall.
# Entries are intentionally explicit so a change in the source requires a reviewed update.
NOTES = {
'startup': ('启动钩子', 'Observer', '打开模型', '内部默认设置', ['调用 reset-parameters；只准备内部变量。','没有 create-network，也没有 reset-ticks，因此打开文件不等于已经开始一次模拟。'], '真正创建网络的是 Replay 或 New map。'),
'reset-parameters': ('设置内部默认值', 'Observer', '固定默认参数', '14 个 *-setting 与 settings-ready?', ['逐项写入默认值：5 家供应商、10 家制造商、每家 1 个伙伴；产能基准 100、需求 30–50。','风险 2%、随机时长 1–10、地图和情景种子均为 2026；指定断供编号 0 表示关闭。','末尾设置 settings-ready? 为 true，表示内部参数已经准备。'], '它没有给界面输入框逐一赋值；初始化随后会从界面重新读取。'),
'ensure-settings': ('准备默认设置的保险', 'Observer', 'settings-ready?', '必要时重建内部默认值', ['若 settings-ready? 不等于 true，调用 reset-parameters。','防止 clear-all 后全局变量归零，或未准备设置时直接进入初始化。'], '这是防御性检查，不是在每个 cycle 重置参数。'),
'read-interface-settings': ('把界面输入复制到内部', 'Observer', '14 个界面变量', '14 个 *-setting', ['runresult 执行字符串形式的 reporter，例如 supplier-capacity，并把结果写入 capacity-setting。','参数名和内部名不是总相同：supplier-count 对应 partner-count-setting，而 total-suppliers 对应 supplier-total-setting。','初始化和每次 go 都读取一次，以便检测用户是否中途改动条件。'], '界面变量由 widgets 定义，所以没有再次写入 globals。runresult 是读取值，run 用来执行命令。'),
'settings-snapshot': ('给参数拍快照', 'Observer reporter', '14 个内部设置', '有固定次序的 list', ['把所有受界面控制的值按固定顺序封装成列表。','初始化时保存为 active-settings；运行时把新列表与旧列表比较。','返回列表本身，不改变模型。'], '列表的索引顺序必须与 restore-settings 一致。费用和价格反馈等内部参数不在这 14 项中。'),
'restore-settings': ('清空后恢复参数', 'Observer', 'values 列表', '14 个内部设置、settings-ready?', ['item 0 到 item 13 依次取出快照元素；NetLogo 索引从 0 开始。','这些参数之前会被 clear-all 清掉，局部变量 selected-settings 仍能用于恢复。'], '如果只改变 snapshot 的顺序而不改这里，会把参数串位。'),
'validate-settings': ('拒绝非法条件', 'Observer', '设置快照、范围、名称', '通过或抛出 error', ['foreach 同时遍历值、下界、上界、名称四个列表。先确认数字，再检查整数与上下界。','额外检查伙伴数不能大于供应商总数，断供编号必须存在。','检查 demand-min ≤ demand-max，duration-min ≤ duration-max。','初始化在 clear-all 前验证，避免错误输入先销毁已有结果。'], '滑块步长不等于验证条件：代码要求范围内整数，不要求容量和需求必须是 10 的倍数。'),
'setup': ('New map 入口', 'Observer', '界面值、当前 map-seed', '新地图种子及一场新运行', ['先读入和验证当前设置。','从 1–9999 抽取 next-seed；while 保证它不同于旧地图种子。','run 拼成的 set map-seed 命令更新界面，然后调用 replay-setup。'], '改变地图会改变距离和初始选商；公平比较采购策略应使用 Replay，并保持两个种子不变。'),
'replay-setup': ('Replay 入口', 'Observer', '当前界面值', '使用运费系数 3 的新场景', ['把参数 3 传给 initialize-scenario。','它从头重建场景，而不是从暂停位置继续。'], 'Run / Pause 才是暂停后继续；Replay 会重置库存和累计结果。'),
'initialize-scenario': ('初始化总调度', 'Observer', 'freight-rate 与界面设置', '全新的网络、状态和时钟', ['检查运费必须大于 0；读取和验证设置，局部保存 selected-settings。','clear-all 后按实体总数 configure-map；恢复设置并保存 active-settings。','先设置维护费 50、持有费 1、运费、价格反馈 0.20 和库存目标倍数 1。','create-network 再 reset-network-totals，最后 reset-ticks。'], '运费必须在 establish-contracts 前设置，因为初始选商依赖运费。新增 BehaviorSpace 实验会在初始化前局部保存目标、反馈和费用参数，初始化后再恢复，否则会被默认值覆盖。'),
'supplier-population': ('供应商总数接口', 'Reporter', 'supplier-total-setting', '供应商数', ['直接返回内部供应商总数，供创建节点和编号计算使用。'], '它不返回每家制造商的伙伴数。'),
'manufacturer-population': ('制造商总数接口', 'Reporter', 'manufacturer-total-setting', '制造商数', ['直接返回内部制造商总数。'], '改变人数不会自动调整每家需求或供应商产能。'),
'create-network': ('按依赖顺序建网络', 'Observer', '已验证的设置与费用参数', '供应商、制造商、位置、合同、标签', ['先创建供应商，再创建制造商，保证供应商 who 从 0 开始。','generate-map 为全部节点安排位置；establish-contracts 才能使用真实距离。','最后更新标签。'], '不能先选商再安排位置，否则初始到货成本排序不正确。'),
'initialize-suppliers': ('创建供应商异质性', 'Observer → Supplier', 'scenario-seed + 30000、产能设置', '固定 base-price/capacity 与初始可用状态', ['with-local-randomness 隔离随机流，固定供应商属性的种子。','创建供应商并设图标、大小、颜色；这些是显示属性。','foreach sort suppliers 按 who 稳定顺序抽样：价格 80–120，产能为基准的 80%–120%。','初始报价等于基础价、可用产能等于正常产能，所有断供标记为 false。未显式设置的数值状态默认 0。'], 'capacity-utilization 初始为 0，所以第一个 cycle 没有价格加成。'),
'initialize-manufacturers': ('创建需求与初始库存', 'Observer → Manufacturer', 'scenario-seed、需求上下限、库存目标倍数', '固定 demand、目标与初始库存', ['先创建制造商，编号 who − 供应商数 + 1，显示为 M1 等。','按排序后的制造商抽需求：min + random(max − min + 1)，两端都包含。','inventory-target = demand × inventory-target-multiplier，默认倍数 1；initial-inventory 从 40–80 抽取，把库存与期初快照都设为它。'], '需求只在初始化抽一次；目标库存不是额外赠送的库存。实验修改目标不会改初始库存。'),
'configure-map': ('扩大模型空间并保持视图大小', 'Observer', 'node-count', '世界边界、patch 大小、map-columns', ['列数为 max(4, ceiling(sqrt(node-count)))。','由列数×7.5 算 half-extent，new-width = 2×half-extent+1。','new-patch-size = 495/new-width；扩世界前先缩像素，缩世界后再放大像素。','默认 15 实体是 33×33 patches；最大 70 实体是 71×71。'], '这会扩大真实模型距离，不只是缩放屏幕；因此人口变化也可能影响运费。'),
'generate-map': ('用地图种子放置节点', 'Observer → Turtle', 'map-seed、map-columns、节点 who', '固定 xcor/ycor', ['把所有网格编号 shuffle 后，每个节点取一个独占 cell。','由 cell mod columns 和 floor(cell/columns) 还原列、行。','格距为 7.5，坐标各加 ±0.6 内的小偏移；x 方向整体偏移 1.75。','退出局部随机流后调用 paint-regions。'], '地图种子控制地理位置；同一种子但不同人口可能产生不同位置。'),
'paint-regions': ('绘制装饰性地理背景', 'Observer → Patch', 'map-seed + 20000', 'pcolor', ['随机选 5 个 patch 作为区域中心并着色。','其他 patch 采用最近区域中心的颜色；myself 指当前需要被着色的 patch。','使用独立局部随机流，避免背景消耗影响别处的随机数。'], '区域不控制风险、距离可达性或运输速度；本模型没有区域共同冲击。'),
'establish-contracts': ('选择并固定采购伙伴', 'Observer → Manufacturer → Contract', '所有供应商的价格、距离、k', '每家 k 条有向合同及路线属性', ['每家制造商按 cheaper-supplier? 排序全体供应商。','sublist 取前 k 家，create-contract-to 从制造商指向供应商。','合同记录 link-length、distance×freight 的 transport-rate、报价加运费的 landed-unit-cost。'], '这是一次性选商，没有在 go 内重建合同。只看成本排序，不预测产能拥堵，也不优化全网。'),
'landed-cost-from': ('计算候选供应商到货单价', 'Manufacturer reporter', 'source 的 unit-price、制造商到 source 距离、运费系数', '报价 + 单位运费', ['从 source 读取报价；distance source 从当前制造商的位置计算。','返回两项相加的单位成本，供初始化排序使用。'], '不包括每条合同固定费用和库存持有费；不能从 supplier 上下文直接把它当同一个意思。'),
'cheaper-supplier?': ('可复现的排序比较器', 'Manufacturer reporter', '两个候选供应商', '布尔值：a 是否排在 b 前', ['先比较各自的 landed-cost-from。','若恰好同价，用 who 较小者先排，避免任意平局改变合同。'], 'sort-by 接收的是比较规则，不是直接返回最低价供应商。'),
'reset-network-totals': ('初始化统计账本', 'Observer', '各制造商 initial-inventory', '初始库存总量；周期与累计值清零', ['保存 initial-inventory-total，供累计库存守恒核对。','逐项将需求、收货、满足量、缺口的周期值和累计值清零。','同样清零四类费用及总费用。'], '初始库存已经存在，但初始采购成本没有补记到累计成本。'),
'go': ('一个 cycle 的主程序', 'Observer', '当前网络、界面值、上期状态', '完成一期的所有状态与 ticks', ['没有制造商时先报错，要求初始化。','重新读参数并验证；快照与 active-settings 不同就中止。','按固定顺序执行恢复、报价、下单、新故障、配给、交货、供应商记录、制造商结算。','更新显示和全网统计后 tick，完成时钟推进和图表更新。'], 'ticks 在末尾增加；循环中 current-cycle = ticks + 1。一次 Step 调用完整 go，不是其中一个子过程。'),
'recover-suppliers': ('下单前更新已知可用性', 'Observer → Supplier', 'ticks+1、随机结束期、旧指定故障状态', '旧故障标记、available-capacity', ['如果本期 > random-outage-through，清除随机结束期。','本期 ≤ 结束期时随机故障仍有效，结束期包含在故障内。','scheduled-outage? 使用“原来已知道且本期仍应断供”的 and 条件。','refresh-supplier-availability 将两类状态合并。'], 'and 保证指定故障的第一期仍在下单后才被揭示；后续期才提前知道。恢复后同一期仍可能发生新的随机故障。'),
'update-supplier-prices': ('利用上期发货重新报价', 'Observer → Supplier，再 Contract', 'base-price、上期 capacity-utilization、price-response', 'pricing-utilization、unit-price、所有合同 landed-unit-cost', ['只更新下单前已知可用的供应商；pricing-utilization 拷贝上期利用率。','unit-price = base-price × (1 + 0.20 × 历史利用率)。','遍历合同，把当前报价加固定运费写为 landed-unit-cost。'], '不复利，也不使用本期订单。已知故障时保留旧报价；恢复时因上期发货为 0，报价回基础价。'),
'place-orders': ('计算补货并向既有伙伴分单', 'Observer → Contract；Manufacturer → Contract', '期初库存、需求、目标、当前到货单价与已知可用性', 'inventory-at-start、order-quantity、order-share、units-ordered', ['先把所有合同的本期订单和份额清零，避免上期残留。','制造商拍库存快照，Q = max(0, demand + target − inventory)。','eligible 只含既有、未断供、可用产能 > 0 的合同。','对 eligible 计算 Σ(1/landed-cost)，每条按倒数成本归一化分到订单。','有订单且有可用伙伴时提交全部补货量；没有伙伴则合同订单维持 0，不另存未提交量。'], 'end1 是制造商，end2 是供应商。分单不根据剩余产能优化；即使某供应商必然拥挤，仍可能给它较多订单。'),
'apply-new-outages': ('下单后揭示新故障', 'Observer → Supplier', '本期、指定故障窗口、随机风险与抽样', '两类故障标记、随机结束期、可用产能', ['本期处于指定窗口就开启 scheduled-outage?。','只有风险 > 0、没有指定故障、也没有进行中随机故障的供应商，才尝试新随机故障。','shock 的第一项小于 risk/100 时触发；结束期 = 本期 + 时长 − 1。','刷新可用性，已下订单保留原数量。'], '没有同周期第二次重新分单。进行中的随机故障可与随后开始的指定故障重叠，但指定故障期间不会新抽随机故障。'),
'scheduled-outage-due?': ('判断是否处于指定故障窗口', 'Supplier reporter', 'who、cycle-number、指定编号/起点/时长', 'true 或 false', ['who+1 与界面 S 编号匹配。','本期 ≥ start 且本期 < start+duration，即包含 start、不包含 start+duration。'], 'start=2、duration=3 就是第 2、3、4 期，最早第 5 期恢复。编号 0 不匹配任何供应商。'),
'refresh-supplier-availability': ('合并故障来源', 'Supplier', 'scheduled-outage?、random-outage?、capacity', 'outage-active?、available-capacity', ['任一故障存在即 outage-active? = true。','故障时可用产能是 0，否则恢复为正常 capacity。'], '两种故障不是简单把持续时长相加；必须两者都结束才可用。'),
'allocate-supply': ('供应商按比例配给', 'Observer → Supplier', '所有 incoming 合同订单、可用产能', 'orders-received、fill-ratio', ['先汇总 my-in-contracts 的 units-ordered。','断供时 fill-ratio = 0；正常且没有订单时设为 1，避免除以 0。','其余情况 fill-ratio = min(1, available-capacity/orders-received)。'], '同一供应商对所有客户使用相同比例，先被 ask 的客户不会先抢光产能。'),
'random-shock': ('为供应商和周期生成独立抽样', 'Reporter', 'scenario-seed、cycle-number、supplier-id、时长范围', '[chance duration]', ['种子 = (情景种子 + 10007×周期 + 1000003×供应商ID) mod 2147483647。','在局部随机流中先抽 [0,1) 的 chance，再抽两端包含的整数时长。','返回列表，由调用处决定是否真的故障。'], '这是策略无关的潜在抽样，不是所有供应商每期都会触发。普通 ask 的随机执行顺序不会改变同一 ID/周期的 shock。'),
'deliver-orders': ('合同交货并按交付计费', 'Observer → Contract', 'units-ordered、供应商 fill-ratio/unit-price、transport-rate', 'units-delivered、两类 charge、连线颜色', ['交付 = 订单 × 供应商配给比率。','采购费 = 实际交付 × 报价；运输费 = 实际交付 × 单位运费。','故障连线红色；交付小于订单则橙色；其他为普通颜色。'], '没有为未交付的订单收采购或运费；费用与报价属于同一期。'),
'record-supplier-results': ('记录本期产出供下期定价', 'Observer → Supplier', '合同交货量、正常 capacity', 'amount-shipped、capacity-utilization', ['汇总 incoming 合同实际交付为 amount-shipped。','利用率 = min(1, 发货/正常产能)，正常产能为 0 时设 0。'], '分母是正常产能而不是故障时的零产能；订单/产能不是这里的利用率。它此时不再更新当前报价。'),
'update-manufacturer-results': ('收货、生产、库存与成本结算', 'Observer → Manufacturer', '期初库存、合同交付/费用、需求、费率', '产出、缺口、期末库存、四类费用', ['汇总到货，available = inventory-at-start + amount-received。','production-met = min(demand, available)；缺口 = demand − production-met；库存 = available − production-met。','采购/运输从合同求和，维护费按所有既有合同数，持有费按期末库存。','四类费用随后由 update-network-totals 汇总；有缺口则制造商变橙色。'], 'unmet-demand 是当期丢失的生产需求，不写入下一期 backlog；断供或零下单时仍付合同维护费。'),
'update-supplier-display': ('画供应商状态', 'Observer → Supplier', '故障、订单、正常产能', 'color', ['先判断故障，显示红色。','正常时订单 > capacity 显示橙色，否则绿色。'], '颜色不反馈经济规则；橙色表示供应商超负荷需求，不表示它真的超产能发货。'),
'update-node-labels': ('更新可读标签', 'Observer → Turtle', '节点数、各实体最新结果', 'label', ['节点数 >16 时只显示 S/M 编号；否则供应商显示订单→交货，制造商显示满足量/需求。','precision 只对显示四舍五入，不改内部数值。','with-local-randomness 避免纯显示 ask 的随机遍历消耗外部随机流。'], '编号和标签是展示，不是全部经济状态；详值仍可以 Inspect。'),
'update-network-totals': ('更新全网与累计账本', 'Observer', '本期所有制造商结果、旧累计值', 'period-*、cumulative-*', ['先 sum 每家需求、到货、满足量和缺口，写 period-*。','把本期数量加到 cumulative-*，不能覆盖历史。','汇总采购、运输、维护、持有费用，算 period-total-cost，再加到累计费用。'], '全网到货总量应等于供应商发货总量。累计满足率用累计量相除；不是收货率。'),
'period-fulfillment-text': ('当期满足率显示', 'Reporter', 'period-demand/fulfilled', '百分数字符串或 N/A', ['分母为 0 时返回 N/A；否则返回四舍五入到 1 位小数的百分比。'], '当前主界面用的是累计满足率；这个 reporter 仍可以查询。'),
'cumulative-fulfillment-text': ('累计满足率显示', 'Reporter', 'cumulative-demand/fulfilled', '百分数字符串或 N/A', ['分母为 0 时返回 N/A；否则把累计满足量除累计需求乘 100，再格式化。'], '界面格式化文字与 BehaviorSpace 数字输出分开。'),
'overall-service-level': ('给实验用的数字满足率', 'Reporter', '累计需求和满足量', '0–100 的数值，或 false', ['无需求时返回 false，避免除零且不误写成 0% 服务。','否则返回 100 × 累计满足量/累计需求，不先四舍五入。'], '实验输出单位是百分比，而非 0–1 小数。'),
'operating-cost-per-unit-met': ('单位满足需求的运营支出', 'Reporter', 'cumulative-total-cost、cumulative-fulfilled', '数字或 false', ['累计满足量为 0 时返回 false。','其余返回累计四类成本/累计生产满足量。'], '不是单价，也不是利润。初始库存免费、没有缺货罚金、没有期末库存抵扣。'),
'unit-cost-text': ('单位支出的界面包装', 'Reporter', 'operating-cost-per-unit-met', 'N/A 或两位小数数值', ['先调用真正的指标 reporter。','false 转为 N/A；其余仅格式化 precision 2。'], '数值定义在 operating-cost-per-unit-met，避免界面与实验各写一套计算。'),
'production-text': ('显示当期生产/需求', 'Reporter', 'period-fulfilled、period-demand', '例如 380 / 400 的文本', ['用 word 拼接满足量与需求，满足量显示 1 位小数精度。'], '这不是百分比，也不是到货量。'),
'average-price': ('简单平均报价', 'Reporter', '供应商 unit-price', '均值，空网络为 0', ['没有供应商时避免 mean 空集合。','其余求供应商当前报价的算术平均。'], '包含停供供应商保留的报价；不是按采购量加权的实际单位支出。'),
'average-utilization': ('简单平均利用率', 'Reporter', '供应商 capacity-utilization', '百分比均值，空网络为 0', ['没有供应商则 0；其余平均每家的利用率后乘 100。'], '异质产能下，平均利用率不等于总发货/总产能。'),
'total-inventory': ('全网当前库存', 'Reporter', '制造商 inventory', '库存总和', ['把各制造商的当前库存加总。'], '初始化时是初始库存；每期结束后是期末库存，不是累计库存。'),
'outage-status-text': ('显示当前停供名单', 'Reporter', 'outage-active?、who', 'None、S 编号列表或汇总文字', ['筛出停供供应商并 sort。空列表返回 None。','超过 5 家用数量概括，否则 map 转成 S1 等名字，再 reduce 用逗号连接。'], '只负责显示已记录状态；不会预测下一期停供。'),
}
assert set(NOTES) == set(PROCS)

STAGES = [
('recover-suppliers','恢复与已知状态','读取上期故障；到期恢复。指定断供首期还不揭示。','供应商已知状态 → 本期下单资格'),
('update-supplier-prices','形成本期报价','可用供应商按上期实际利用率重新报价，再更新合同到货单价。','上期利用率 → 本期报价'),
('place-orders','计算补货与分单','先算库存缺口，只向已知可用的已有伙伴按倒数成本分单。','期初库存、报价 → 订单'),
('apply-new-outages','揭示新的断供','订单已提交。本期新故障在此生效，不能在本期重新分单。','新外部冲击 → 实际可用产能'),
('allocate-supply','按产能比例配给','每家供应商汇总全部客户订单，对所有客户使用同一交付比例。','总订单、可用产能 → 配给比例'),
('deliver-orders','交货并计算变动费用','每条合同的交付等于订单乘配给比例；采购和运输只对实际交付收费。','订单、配给比例 → 到货与变动费用'),
('record-supplier-results','保存本期利用率','汇总实际发货，再除正常产能，结果供下一期报价使用。','实际发货 → 下期定价依据'),
('update-manufacturer-results','生产、库存与记账','期初库存加到货先满足本期需求，剩余留库存；同时计算四类费用。','库存、到货 → 生产、期末库存、成本'),
('update-supplier-display','刷新供应商颜色','先显示停供，再显示订单是否超过产能。这里只更新显示。','经济状态 → 节点颜色'),
('update-node-labels','刷新节点标签','供应商显示订单→发货；制造商显示本期满足量/需求。','经济状态 → 可读标签'),
('update-network-totals','汇总全网和累计指标','把制造商本期结果求和，再加入累计账本。','各制造商结果 → 全网指标'),
('go','推进 tick','tick 位于最后：已完成周期数加 1，界面图表随之更新。','本期全部计算完成 → 下一期'),
]

def fmt(v):
    if isinstance(v, str): return v
    return f'{v:,.4f}'.rstrip('0').rstrip('.')

def make_trace():
    """Transparent teaching fixture: 1 buyer, 2 suppliers; no random failures."""
    inventory = 40.0
    utilization = [0.0, 0.0]
    price = [100.0, 100.0]
    cumulative = dict(demand=0., received=0., met=0., unmet=0., cost=0.)
    history = []
    for cycle in range(1, 8):
        opening = inventory
        previous_util = utilization[:]
        known = [cycle in (3,4,5), False]
        for i in range(2):
            if not known[i]: price[i] = 100 * (1 + .2 * utilization[i])
        landed = [p + 20 for p in price]
        q = max(0, 80-opening)
        weights = [0 if known[i] else 1/landed[i] for i in range(2)]
        shares = [w/sum(weights) for w in weights]
        orders = [q*s for s in shares]
        outage = [cycle in (2,3,4,5),False]
        ratios = [0 if outage[i] else min(1,30/orders[i]) if orders[i] else 1 for i in range(2)]
        delivered = [orders[i]*ratios[i] for i in range(2)]
        purchase = [delivered[i]*price[i] for i in range(2)]
        freight = [d*20 for d in delivered]
        utilization = [d/30 for d in delivered]
        received = sum(delivered)
        met = min(40,opening+received)
        unmet = 40-met
        inventory = opening+received-met
        cost = sum(purchase)+sum(freight)+100+inventory
        cumulative['demand'] += 40
        cumulative['received'] += received
        cumulative['met'] += met
        cumulative['unmet'] += unmet
        cumulative['cost'] += cost
        assert abs(opening+received-met-inventory)<1e-8
        assert all(0<=d<=30+1e-8 for d in delivered)
        assert abs(sum(orders)-q)<1e-8
        assert abs(40+cumulative['received']-cumulative['met']-inventory)<1e-8
        caps = [0 if x else 30 for x in outage]
        rows = [
          [('对象','上期利用率','下单前已知状态'),('S1',fmt(previous_util[0]),'已知断供' if known[0] else ('恢复，可接单' if cycle==6 else '可接单')),('S2',fmt(previous_util[1]),'可接单')],
          [('对象','采购报价 p','到货单价 p + 20'), *[(f'S{i+1}',fmt(price[i]),fmt(landed[i])) for i in range(2)]],
          [('对象','订单份额','本期提交订单'), *[(f'S{i+1}',fmt(shares[i]*100)+'%',fmt(orders[i])) for i in range(2)],('M1','Q = max(0, 40 + 40 − '+fmt(opening)+')',fmt(q))],
          [('对象','订单后的实际状态','可用产能'),('S1','新断供，订单来不及重分' if cycle==2 else '持续断供' if outage[0] else '正常',str(caps[0])),('S2','正常','30')],
          [('供应商','总订单 → 可用产能','fill-ratio'), *[(f'S{i+1}',fmt(orders[i])+' → '+str(caps[i]),fmt(ratios[i])) for i in range(2)]],
          [('合同','实际交付','采购费 / 运输费'), *[(f'M1 → S{i+1}',fmt(delivered[i]),fmt(purchase[i])+' / '+fmt(freight[i])) for i in range(2)]],
          [('供应商','实际发货 / 正常产能','新利用率（供下期）'), *[(f'S{i+1}',fmt(delivered[i])+' / 30',fmt(utilization[i])) for i in range(2)]],
          [('项目','计算','结果'),('可用库存',fmt(opening)+' + '+fmt(received),fmt(opening+received)),('本期生产','min(40, '+fmt(opening+received)+')',fmt(met)),('本期缺口','40 − '+fmt(met),fmt(unmet)),('期末库存',fmt(opening+received)+' − '+fmt(met),fmt(inventory)),('本期支出',fmt(sum(purchase))+' + '+fmt(sum(freight))+' + 100 + '+fmt(inventory),fmt(cost))],
          [('对象','状态','显示'), *[(f'S{i+1}','断供' if outage[i] else '订单超过产能' if orders[i]>30 else '正常','红色' if outage[i] else '橙色' if orders[i]>30 else '青绿色') for i in range(2)]],
          [('对象','标签内容','含义'), *[(f'S{i+1}',('OUT · ' if outage[i] else '')+fmt(round(orders[i],1))+' → '+fmt(round(delivered[i],1)),'订单 → 发货') for i in range(2)],('M1',fmt(met)+' / 40','生产满足量 / 需求')],
          [('累计项目','结果','口径'),('需求 / 满足量',fmt(cumulative['demand'])+' / '+fmt(cumulative['met']),'每期累加'),('满足率',fmt(100*cumulative['met']/cumulative['demand'])+'%','累计满足量 / 累计需求'),('累计缺口',fmt(cumulative['unmet']),'历史缺口，不是积压订单'),('累计运营支出',fmt(cumulative['cost']),'四类费用之和'),('支出 / 单位满足量',fmt(cumulative['cost']/cumulative['met']),'不是采购单价')],
          [('变量','此前','完成后'),('ticks',str(cycle-1),str(cycle)),('inventory',fmt(opening)+'（本期期初）',fmt(inventory)+'（传给下期）'),('capacity-utilization','见步骤 1 的上期值','S1 '+fmt(utilization[0])+' / S2 '+fmt(utilization[1]))],
        ]
        notes = [
          'S1 的指定断供窗口是第 2–5 期。第 2 期此时尚未知，第 3、4、5 期已知，第 6 期到期恢复。',
          '例如 S2：100 × (1 + 0.20 × '+fmt(previous_util[1])+') = '+fmt(price[1])+'。已知断供的 S1 保留上次报价。',
          'M1 只有这两个既有伙伴。已知 S1 断供时订单全给 S2；本步没有预先裁剪到产能。',
          '本案例风险设为 0，只演示指定故障。正式模型还在这一步判断新的随机故障。',
          '本例仅有一个客户，供应商仍可能因补库订单大于 30 而限量；多客户时先求总订单再同比例配给。',
          '交付都发生在当前 cycle 内，没有在途库存或运输延迟；距离只改变费用。',
          '本期利用率刚被更新，但本期报价不再改变，价格反馈要等下一个 cycle。',
          ('本期缺口为 10。它记录为 lost demand；下一期 Q = 80，不会再加 10。' if cycle==5 else '关系维护费一直是 2 × 50 = 100；持有费按本期期末库存计算。'),
          '颜色更新不改变报价、合同、库存或任何经济结果。',
          '标签显示时四舍五入；模型内部继续保留小数。连线粗细来自订单份额，不是实际交付。',
          '累计统计只加一次。当期有初始库存缓冲时，即使到货下降，生产也可能仍然全部满足。',
          '期末库存、当期利用率、有效故障结束期等状态保留到下一期；合同与地理位置保持不变。',
        ]
        history.append(dict(cycle=cycle, opening=opening,q=q,price=price[:],shares=shares,orders=orders,delivered=delivered,ratios=ratios,received=received,met=met,unmet=unmet,ending=inventory,cost=cost,util=utilization[:],cumulative=cumulative.copy(),rows=rows,notes=notes))
    assert [h['ending'] for h in history] == [40,20,10,0,0,20,40]
    assert [h['unmet'] for h in history] == [0,0,0,0,10,0,0]
    return history

TRACE = make_trace()

def build_flow():
    content = '''<section id="refresh"><h2>先用 3 分钟把项目找回来</h2>
<p>我们的研究问题是：在<strong>共享产能有限、供应商会暂时断供</strong>的环境中，每家制造商固定合作 1、2、3 家供应商，如何改变<strong>需求满足率</strong>与<strong>运营支出</strong>？这里的 cycle 是一个离散采购／生产周期，没有校准成一天或一周。</p>
<div class="route"><div><span class="tag">供应商 Supplier</span><strong>报价、接受订单、限量交货</strong><p>每家价格和产能不同；可能完全停供。</p></div><div><span class="tag">制造商 Manufacturer</span><strong>补货、生产、保留库存</strong><p>需求固定，库存随周期改变。</p></div><div><span class="tag">合同 Contract</span><strong>连接谁、下多少、交多少</strong><p>从制造商指向供应商，伙伴固定，分单比例可变。</p></div><div><span class="tag">环境 Environment</span><strong>距离影响运费</strong><p>平面示意地图，没有道路或运输延迟。</p></div></div>
<p>默认有 5 家供应商和 10 家制造商。<code>supplier-count = 2</code> 意味着<strong>每家制造商有两个伙伴</strong>，共 20 条合同；不是整个网络只剩两家供应商。ABM 的关键在于：多个制造商会争用同一个供应商，个人“选便宜”的决定可能造成系统拥堵，结果由交互产生。</p>
'''+box('<strong>明天先讲这条主线：</strong>库存决定补多少 → 报价和已知可用性决定向谁下单 → 新断供与共享产能决定交多少 → 库存加到货决定生产多少 → 本期发货决定下一期报价。')+'''
<h3>哪些固定，哪些每期变化？</h3>'''+table(['初始化后固定','跨期状态','每期重算 / 累计'],[
('节点位置、基础价、正常产能、制造商需求、合同伙伴、费率','库存；利用率；当前报价；故障状态和结束期','本期订单、到货、产出、费用重算；cumulative-* 累加'),
('目标库存默认等于本制造商 1 期需求','已知故障的报价会保留，不一定来自紧邻上一期','上一期缺口只留作统计，不作为积压单进入下期')])+'''
<h3>复习路线</h3><p>时间紧时：读本节 → 点击下面的七期演示 → 熟悉“断供时序” → 练英文口述。需要回答实现细节时，再打开<a href="code-walkthrough.zh.html">完整代码讲解</a>。原指南适合找界面按钮和参数位置。</p></section>
<section id="setup"><h2>模拟开始前：初始化做了什么</h2>
<p><strong>初始化不是 cycle 1。</strong>完成 Replay 后 <code>ticks = 0</code>，有初始库存，但累计需求和累计产出仍为 0。</p>
<ol><li>读取并验证 14 个界面设置，错误时保留已有运行。</li><li>保存设置，清空旧状态，按人数配置地图大小，恢复参数。</li><li>设维护费 50、持有费 1、价格反馈系数 0.20、交互运费系数 3。</li><li>抽供应商基础价 80–120、正常产能为容量基准的 80%–120%；抽制造商固定需求和初始库存 40–80。</li><li>用地图种子放置实体。每家制造商按“基础报价 + 距离×运费系数”选最便宜的 k 家，并固定合同。</li><li>保存初始库存总量，清零账本，重置时钟。首次 Step 才处理 cycle 1。</li></ol>
<p>实际入口：'''+src('replay-setup')+' → '+src('initialize-scenario')+' → '+src('create-network')+'''。</p>
'''+box('<strong>两个种子：</strong><code>map-seed</code> 管地理位置；<code>scenario-seed</code> 管基础价格、产能、需求、初始库存及供应商／周期的潜在故障抽样。比较 1／2／3 个伙伴时，固定人口、其他参数和两个种子，再 Replay。价格和订单份额是内生结果，可以不同。')+'''
</section>
<section id="cycle"><h2>每个 cycle：严格按这个顺序</h2>
<p>下面 12 步对应 <code>go</code> 中的真实调用顺序。先统一下单，再统一配给，因此普通 <code>ask</code> 的随机执行顺序不会让先处理的制造商优先抢货。参数检查在这些步骤之前。</p>
'''+table(['顺序 / 函数','这一步做什么','输入 → 输出'],[(f'{i+1:02d} · '+src(name, 'tick（go 末尾）' if i==11 else None),desc,transition) for i,(name,title,desc,transition) in enumerate(STAGES)])+'''
<div class="formula">u(t−1) → p(t) → Q(t), order-share(t) → outage(t), fill-ratio(t) → delivery(t) → inventory(t), u(t) → p(t+1)</div>
<p>这里 <code>u</code> 是实际发货除正常产能。箭头表达因果顺序：本期订单不会倒过来修改本期已形成的报价。进入 cycle t 时 <code>ticks = t−1</code>，最后才增加为 t。</p></section>
<section id="demo"><h2>跟着一笔订单走完七个 cycle</h2>
<p>这是为了讲解而设定的<strong>微型案例</strong>，不是默认种子的实验结果：2 家供应商、1 家制造商；供应商基础价均 100、正常产能均 30；每条路线运费 20／单位；制造商需求 40、目标库存 40、初始库存 40；合同费每条 50、持有费每单位 1。</p>
<p><strong>S1 在第 2–5 期指定断供，随机风险为 0。</strong>第 2 期下单时未知，3、4、5 期已知，6 期恢复。数值由同一套公式计算，并已用 NetLogo 7.0.4 引擎的相同人工设定核对七期结果；显示到 4 位小数，内部保留精度。</p>
<div class="simulator" id="simulator"><div class="toolbar"><label for="cycle-select">选择周期 <select id="cycle-select"><option value="0">Cycle 1 · 正常采购</option><option value="1">Cycle 2 · 突然断供</option><option value="2">Cycle 3 · 已知断供</option><option value="3">Cycle 4 · 用完库存</option><option value="4">Cycle 5 · 出现缺口</option><option value="5">Cycle 6 · 恢复供应</option><option value="6">Cycle 7 · 补回库存</option></select></label><button id="restart" type="button">回到本期第 1 步</button></div>
<div class="steps" aria-label="本期步骤">'''+''.join(f'<button type="button" data-stage="{i}" aria-pressed="{str(i==0).lower()}">{i+1:02d} · {t}</button>' for i,(_,t,_,_) in enumerate(STAGES))+'''</div>
<div id="step-result" aria-live="polite" aria-atomic="true"></div><div class="toolbar"><button id="prev-step" type="button">上一步</button><button id="next-step" type="button" class="primary">下一步</button><a id="step-source" href="code-walkthrough.zh.html#proc-recover-suppliers">打开对应完整代码</a></div><p class="small">可直接点步骤；“下一步”在第 12 步后进入下一期。此处演示时序，不生成新的随机实验。</p></div>
<noscript><p>浏览器关闭了脚本。上方完整时序表和下方七期结果仍可阅读。</p></noscript>
<h3>七期结果放在一起看</h3>
'''+table(['Cycle','期初库存','希望补货','S1 / S2 到货','生产 / 缺口','期末库存','本期总支出'],[(str(h['cycle']),fmt(h['opening']),fmt(h['q']),fmt(h['delivered'][0])+' / '+fmt(h['delivered'][1]),fmt(h['met'])+' / '+fmt(h['unmet']),fmt(h['ending']),fmt(h['cost'])) for h in TRACE])+'''
<ol><li><strong>Cycle 2：</strong>库存从 40 降到 20，但生产仍满足 40。可见“到货少”不一定立刻“生产少”。</li><li><strong>Cycle 3：</strong>全部 60 单位订单改给 S2，但它只有 30 产能。分散风险不能凭空增加既有伙伴的产能。</li><li><strong>Cycle 4 → 5：</strong>第 4 期用 10 库存加 30 到货，恰好满足 40，库存归零；第 5 期只有 30 到货，因此首次出现 10 单位生产缺口。</li><li><strong>Cycle 6：</strong>S1 恢复时按上期零利用率报价 100，S2 按满产报价 120；Q = 80，按倒数到货成本分单约 43.0769 / 36.9231，两家都限量交 30。期末库存回到 20。</li><li><strong>Cycle 7：</strong>两家上期都满产，报价都为 120；Q = 60，均分后各交 30，期末库存回到 40。第 5 期的缺口 10 没有作为积压需求再次加到订单。</li></ol>
</section>'''
    content += '''<section id="equations"><h2>七条公式，沿着订单的方向记</h2>'''+table(['规则','公式','怎么解释'],[
('报价','pⱼ,t = baseⱼ × (1 + 0.20 × uⱼ,t−1)','只对已知可用者更新。u 是实际发货/正常产能，通常在 0–1 之间，所以最高加价 20%。'),
('补货','Qᵢ,t = max(0, Dᵢ + Tᵢ − Iᵢ,t−1)','D 是生产需求，T 是期末库存目标，I 是期初库存；不是只订 D。'),
('分单','cᵢⱼ,t = pⱼ,t + distanceᵢⱼ × freight；sᵢⱼ,t = (1/cᵢⱼ,t) / Σ(1/cᵢₖ,t)','分母只含可用的既有伙伴。有订单时成本低者份额大，每个可用伙伴都有正份额。'),
('配给','Oⱼ,t = Σᵢ Qᵢ,t sᵢⱼ,t；rⱼ,t = min(1, Cⱼ,t / Oⱼ,t)','断供时 r=0；正常无订单时 r=1；否则按共享产能配给。'),
('交货与生产','xᵢⱼ,t = Qᵢ,t sᵢⱼ,t rⱼ,t；Pᵢ,t = min(Dᵢ, Iᵢ,t−1 + Σⱼ xᵢⱼ,t)','先收到货，再生产；到货和产出可以不同。'),
('库存与缺口','Iᵢ,t = Iᵢ,t−1 + Σⱼ xᵢⱼ,t − Pᵢ,t；Uᵢ,t = Dᵢ − Pᵢ,t','库存传到下一期。缺口计入历史，但不转成下一期积压。'),
('成本','Costᵢ,t = Σⱼ xᵢⱼ,t pⱼ,t + Σⱼ xᵢⱼ,t freightᵢⱼ + 50kᵢ + Iᵢ,t','分别为采购、运输、合同维护、库存持有；不含收入或缺货罚金。')])+'''
<h3>为什么希望补货与实际提交仍可能不同？</h3><p>如果所有既有伙伴都不可用，制造商仍可能想补 80，但实际合同订单为 0。如果有可用伙伴，全部希望补货都会分出去，即使后来因产能不足只交一小部分。需要检查时，用 <code>order-quantity − sum [units-ordered] of my-out-contracts</code> 算出未提交量；精简版不再把它单独存成变量。未提交与提交后未交货仍是两种情况。</p>
<h3>共享产能的最小例子</h3><p>同一供应商产能 100，M1 订 80，M2 订 70。总订单 150，交付比例 100/150 = 2/3，因此分别收到 53.3333 和 46.6667。不是先给 M1 80 再给 M2 20；也不是一人 50。</p>
</section>
<section id="outages"><h2>最容易讲错：断供和价格的时点</h2>'''+table(['时点','本期下单时知道吗？','本期怎么处理？'],[
('指定故障刚开始 / 新随机故障','不知道。指定事件虽由实验者设好，制造商没有提前预知。','先下单，再设可用产能为 0；已下订单没有当期补救分配。'),
('故障持续的后续期','知道。recover-suppliers 保留有效故障。','不向它下单，已有合同仍保留；其他既有伙伴承担重新分配的订单。'),
('故障结束后的首期','下单前恢复。随机故障还可能再次发生。','恢复报价使用上期 0 利用率，因此回到基础价；可以重新接单。'),
('本期发货完成','此时才知道本期实际利用率。','只写 capacity-utilization，不再修改本期 unit-price。')])+'''
<div class="formula">指定故障 start = 2，duration = 4<br>有效期：2、3、4、5　｜　第 2 期为 surprise　｜　第 6 期开始前恢复</div>
<p>随机故障的结束期存为 <code>random-outage-through = current-cycle + duration − 1</code>，含结束的那个周期。随机风险 2% 表示符合条件的正常供应商在本周期新发生故障的概率，不表示任意时点只有 2% 的供应商停工。</p>
'''+box('<strong>指定故障与随机故障：</strong>旧随机故障可能跨入指定故障窗口，两者取 OR。指定故障或随机故障正在进行时，不再抽新的随机故障。不能简单把两种时长相加，也不能说风险 0 会关闭指定故障。')+'''
</section>
<section id="checks"><h2>怎样证明自己理解了模型</h2>
<p>先用守恒式检查实现，再用实验判断机制。下面是代码应满足的约束，浮点计算比较时允许小误差。</p>'''+table(['检查','等式或约束','为什么有用'],[
('订单去向','有可用伙伴时 Σ合同订单 = Qᵢ；否则为 0','未提交量可用 Qᵢ − Σ合同订单临时计算，不单独存储。'),
('货物守恒','Σ供应商发货 = Σ合同交付 = Σ制造商到货','排除漏货和重复记货。'),
('库存守恒','期初库存 + 到货 = 生产满足量 + 期末库存','解释为什么 receipts 不等于 production。'),
('累计库存','初始库存 + 累计到货 = 累计生产满足量 + 当前库存','检查跨周期状态是否丢失或重复。'),
('需求守恒','生产满足量 + 未满足需求 = 固定需求','确保缺口没有被当成本期产出。'),
('产能和价格边界','发货 ≤ 正常产能；0 ≤ 利用率 ≤ 1；base ≤ 报价 ≤ 1.2×base','价格上限只在默认 α=0.20 时为 1.2。'),
('费用守恒','总成本 = 采购 + 运输 + 维护 + 持有','不能拿总支出低直接解释成效率高。')])+'''
<h3>在 NetLogo 做一个可讲给考官听的演示</h3><ol><li>暂停，设置 5 家供应商、10 家制造商，两个种子固定；先让每家合作 2 家，随机风险为 0。</li><li>指定 S1 从第 3 期断供 2 期，Replay 后逐次 Step。S1 在 3、4 期停供，5 期恢复。</li><li>Inspect S1 的报价、利用率、订单、发货；Inspect 某个与 S1 相连的制造商及它的合同。</li><li>第 3 期看“已下订单但没交货”；第 4 期看“已知故障所以没给 S1 下单”；第 5 期看“恢复并按零利用率报价”。如果该制造商原本无需补货，它在第 3 期也可能没有订单，应据真实库存解释。</li><li>比较 k=1、2、3 时，每次改完都 Replay；不要在同一场运行中直接改 k 然后继续。</li></ol></section>
<section id="experiments"><h2>从每个 cycle 走到实验结论</h2>
<p>单个 cycle 是机制更新；<strong>一场 500-cycle 模拟是一个 replicate</strong>。同一情景下比较 k=1、2、3，再把 30 个情景的配对差做统计。不能把 500 个相邻 cycle 当作 500 个独立样本。</p>
<p>当前模型已补齐六组 BehaviorSpace 定义：风险、产能、库存目标、运费、价格反馈和费用。每种条件使用 30 个情景、每场 500 cycle。<a href="../experiment-results.html">已有六组实验报告</a>当时使用 NetLogo 后台引擎加 Java 批量运行器；费用组对已有轨迹重新计价。现在保存的费用组是逐组合重新运行以验证相同账本，不能把这些费用变体算成额外的独立情景。完整参数表和实验 XML 见<a href="code-walkthrough.zh.html#xml">代码讲解的界面与实验部分</a>。</p>
'''+table(['基准：风险 2%、运费 3','平均满足率','平均支出 / 单位满足量'],[('1 个伙伴','63.20%','140.59'),('2 个伙伴','84.00%','149.64'),('3 个伙伴','95.19%','157.46')])+'''
<p class="small">这些是已有报告中 30 个情景的逐场指标算术平均，不是本页教学例子的结果，也不是这次重新运行完整实验。金钱单位为抽象单位。</p>
<p>可以说：在测试条件下，更多伙伴提高平均满足率，也提高每单位满足需求的运营支出。不能说“三家永远最好”或“成本最低就利润最高”。风险为 0 时平均满足率仍分别约为 69.66%、90.79%、99.67%，说明一部分多源采购收益来自<strong>缓解集中采购的产能拥堵</strong>。</p>
'''+box('<strong>解释边界：</strong>这是合成参数、有限时域模型；没有经验校准、收益函数、缺货罚金、相关区域冲击、供应商替换或运输延迟。初始库存免费、终端库存不抵扣。更长期窗口的敏感性检查不能证明平稳性。')+'''
<p>资料版本提醒：<code>MODEL_PLAN.md</code> 记录渐进开发过程，早期参数和阶段状态不必等于现状；<code>report/report.tex</code> 目前仍是待填写模板。这里的流程以当前 <code>model.nlogox</code> 为准。</p></section>
<section id="talk"><h2>Viva 口述：先完整讲一遍</h2>
<p>先用中文理清思路，再练下面约 1 分钟出头的简单英文版。按六小段记：比较什么 → 固定伙伴 → 报价下单 → 断供配给 → 库存生产 → 成本与结论；细节等追问时展开。</p>
<h3>中文梳理版</h3><div class="spoken">我们的模型研究的是，在供应商产能有限且可能暂时断供的条件下，固定选择一家、两家或三家供应商，如何影响制造商的需求满足程度和运营支出。<br><br>初始化时，我们生成供应商的基础价格和产能、制造商的固定需求和初始库存，以及决定运费的地理位置。每个制造商按照初始到货单价选定伙伴，之后不再更换合同。<br><br>每个周期先处理到期恢复，再用上期实际利用率更新报价。制造商根据需求、目标库存和现有库存算补货量，避开已知断供的伙伴，并按当前到货单价的倒数分单。接着才揭示本期新的断供。供应商汇总所有订单，在产能不足时按比例配给。<br><br>供应商先把本期实际利用率存下来影响下一期价格。制造商再用库存加到货满足本期生产，剩余留作库存，不足部分记为丢失需求；同时记录采购、运输、关系维护和库存持有四类支出。最后更新全网累计指标和时钟。<br><br>我们固定外部情景比较采购策略。更多伙伴能分散断供风险，也能缓解拥堵，但会增加关系费并可能采购更贵的供给，因此研究的是服务与成本的权衡。</div>
<h3>Simple spoken version · 简单口语版</h3><div class="spoken" lang="en">Our model compares using one, two or three suppliers. We look at how much demand we meet and how much we spend.<br><br>Buyers choose partners by price plus delivery cost, and keep the same partners.<br><br>Each cycle, we check supply and update prices based on how busy suppliers were last cycle. Buyers order based on demand, current stock and target stock. Cheaper available partners get more orders.<br><br>New failures happen after ordering. If a supplier cannot fill all orders, it cuts each order by the same percentage.<br><br>Buyers use stock and deliveries to meet demand. Extra stock stays. Missed demand is not added to the next cycle.<br><br>Costs include buying, delivery, supplier fees and storage. We compare under the same conditions. More suppliers can reduce shortages, but may cost more.</div>
</section><section id="quiz"><h2>不看答案，回答这 12 个问题</h2>'''
    questions = [
('为什么需求 40，订单会是 80？','如果期初库存为 0，目标库存为 40，则 Q=max(0,40+40−0)=80，其中 40 用于当期需求，40 用于补回目标库存。'),
('第 2 期指定断供，为什么这期还有订单发给它？','模型让制造商只知道之前已经发生的断供。第 2 期的新事件在下单后才揭示；这是一项信息与时序假设。'),
('已知故障时会重新选择一家供应商吗？','不会。只是把订单改分到既有合同中的可用伙伴，合同网络不重连。'),
('同一供应商面对多个客户时，谁先拿货？','不分先后。订单全部提交后才汇总并确定统一比例；每条合同按自己的订单量乘这个比例。'),
('为什么利用率不是订单除产能？','价格反馈取决于实际生产。超额订单可能无法交付，订单/产能会超过 1；实际发货/正常产能被限制在 0–1。'),
('下单后发生故障，本期能再把订单转给别人吗？','不能。go 中 place-orders 只在 apply-new-outages 之前执行一次，没有本期二次采购。'),
('已知故障的报价为什么看起来没有更新？','update-supplier-prices 只更新可用供应商；停供者保留旧报价，恢复后按上期 0 发货得到基础价。'),
('没有收到货，为什么仍有成本？','既有合同仍收维护费；如果用完本期需求后仍有库存，也收期末持有费。采购和运输则为 0。'),
('第 5 期缺口 10，第 6 期要不要额外订这 10？','不要。它是 lost demand。第 6 期按当期需求和库存目标重新算 Q；教学例子是 40+40−0=80，不是 90。'),
('为什么固定 seed 并不让两种策略的价格完全一致？','种子固定外部属性与故障抽样。不同合同和订单影响实际利用率，因此内生价格、库存、分单和结果可以不同。'),
('更多供应商的优势全部来自抗断供吗？','不是。即使风险为 0，固定低成本网络也可能把订单集中到少数供应商，增加伙伴还可能缓解产能拥堵。'),
('为什么不能据此宣布最优采购策略？','没有收益、缺货罚金或综合目标，只有服务与运营支出的权衡；结论还依赖合成参数与模型假设。'),
    ]
    content += ''.join(qa(q,a) for q,a in questions)+'</section>'
    return content

FLOW_JS = r'''
const trace=TRACE_DATA;
const stages=STAGE_DATA;
let cycleIndex=0, stageIndex=0;
const safe=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function renderStep(){
 const h=trace[cycleIndex],s=stages[stageIndex],rows=h.rows[stageIndex];
 document.querySelector('#cycle-select').value=cycleIndex;
 document.querySelectorAll('[data-stage]').forEach(b=>b.setAttribute('aria-pressed',Number(b.dataset.stage)===stageIndex));
 const transition=s[3].split(' → ');
 document.querySelector('#step-result').innerHTML=`<p class="phase-count">Cycle ${h.cycle} · 步骤 ${stageIndex+1} / 12</p><h3 class="sim-heading">${safe(s[1])}</h3><p><code>${safe(stageIndex===11?'tick':s[0])}</code> · ${safe(s[2])}</p><div class="state-flow"><div class="state-box"><strong>读取</strong><span>${safe(transition[0])}</span></div><div class="state-arrow" aria-hidden="true">→</div><div class="state-box"><strong>写入 / 影响</strong><span>${safe(transition[1])}</span></div></div><div class="table-scroll"><table><thead><tr>${rows[0].map(x=>`<th scope="col">${safe(x)}</th>`).join('')}</tr></thead><tbody>${rows.slice(1).map(row=>`<tr>${row.map(x=>`<td>${safe(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p class="step-note">${safe(h.notes[stageIndex])}</p>`;
 document.querySelector('#step-source').href='code-walkthrough.zh.html#proc-'+s[0];
 document.querySelector('#prev-step').disabled=cycleIndex===0&&stageIndex===0;
 document.querySelector('#next-step').disabled=cycleIndex===trace.length-1&&stageIndex===11;
 document.querySelector('#next-step').textContent=stageIndex===11&&cycleIndex<trace.length-1?'进入下一 cycle':'下一步';
}
document.querySelectorAll('[data-stage]').forEach(b=>b.addEventListener('click',()=>{stageIndex=Number(b.dataset.stage);renderStep()}));
document.querySelector('#cycle-select').addEventListener('change',e=>{cycleIndex=Number(e.target.value);stageIndex=0;renderStep()});
document.querySelector('#restart').addEventListener('click',()=>{stageIndex=0;renderStep()});
document.querySelector('#next-step').addEventListener('click',()=>{if(stageIndex<11)stageIndex++;else if(cycleIndex<trace.length-1){cycleIndex++;stageIndex=0}renderStep()});
document.querySelector('#prev-step').addEventListener('click',()=>{if(stageIndex>0)stageIndex--;else if(cycleIndex>0){cycleIndex--;stageIndex=11}renderStep()});
renderStep();
'''.replace('TRACE_DATA',json.dumps(TRACE,ensure_ascii=False)).replace('STAGE_DATA',json.dumps(STAGES,ensure_ascii=False))

GROUPS = [
('parameters','A · 参数与启动',list(PROCS)[:7]),
('initialization','B · 初始化、地理与固定合同',list(PROCS)[7:22]),
('runtime','C · 每个 cycle 的核心逻辑',list(PROCS)[22:34]),
('display','D · 显示与累计账本',list(PROCS)[34:37]),
('reporters','E · 指标与界面 reporter',list(PROCS)[37:]),
]
assert sum(len(g[2]) for g in GROUPS)==47

def color_line(line):
    parts=re.split(r'("[^"\n]*"|;.*$)',line)
    result=[]
    for part in parts:
        safe=esc(part)
        if part.startswith(';'): result.append('<span class="comment">'+safe+'</span>')
        elif part.startswith('"'): result.append(safe)
        else: result.append(re.sub(r'(?<![\w-])(to-report|to|end|report|let|set|ask|ifelse-value|ifelse|if|foreach|with-local-randomness|random-seed|breed|globals|suppliers-own|manufacturers-own|contracts-own|directed-link-breed)(?![\w?-])',r'<span class="keyword">\1</span>',safe))
    return ''.join(result)

def source_block(start,end,opened=False):
    code=''.join(f'<span class="code-line" id="code-L{i}"><span class="ln" aria-hidden="true">{i}</span><span class="source-text">{color_line(LINES[i-1])}</span></span>' for i in range(start,end+1))
    return f'<details class="source"{ " open" if opened else ""}><summary>完整源码 · Code L{start}–{end} · 文件 L{start+2}–{end+2}</summary><pre aria-label="完整 NetLogo 源码，Code 行 {start} 至 {end}"><code>{code}</code></pre></details>'

VARIABLE_ROWS = [
('内部参数','capacity-setting；demand-min-setting；demand-max-setting','产能基准与需求抽样上下限，从 supplier-capacity/min-demand/max-demand 读取。'),
('内部参数','partner-count-setting；supplier-total-setting；manufacturer-total-setting','每家伙伴数，与全网供应商/制造商总数分开。'),
('内部参数','map-seed-setting；scenario-seed-setting','地理随机流与属性/故障随机流的输入。'),
('内部参数','outage-supplier-setting；outage-start-setting；outage-duration-setting','指定故障的 S 编号、首期、时长。'),
('内部参数','outage-risk-setting；duration-min-setting；duration-max-setting','新随机故障概率及持续期抽样范围。'),
('初始化状态','map-columns；settings-ready?；active-settings','网格列数；内部设置是否准备好；本次运行的界面参数快照。'),
('内部经济参数','transport-cost-per-distance；price-response；relationship-fee；holding-fee-per-unit','默认 3、0.20、50、1；运费可从实验初始化入口传入。'),
('实验参数','inventory-target-multiplier','期末库存目标 / 每期需求，默认 1；库存和费用实验取 0/1/2，不改变初始库存。New map / Replay 恢复为 1，没有新增界面输入。'),
('初始化记录','initial-inventory-total','全网初始库存，后续不重写，用于累计守恒检查。'),
('全网数量','period-demand；period-received；period-fulfilled；period-unmet','本期需求、收货、生产满足量、生产缺口。cumulative- 同后缀表示历史累加。'),
('全网费用','period-purchase-cost；period-transport-cost；period-relationship-cost；period-holding-cost；period-total-cost','本期采购、运输、维护、持有、总费用；cumulative- 同后缀表示历史累加。'),
('供应商固定属性','capacity；base-price','正常产能和基础价；在运行中不随故障或加价改写。'),
('供应商报价','unit-price；pricing-utilization；capacity-utilization','当前报价；生成当前报价所用的历史利用率；最近完成周期实际利用率。两种 utilization 的时间含义不同。'),
('供应商本期结果','orders-received；amount-shipped；fill-ratio；available-capacity','总订单；总发货；统一配给比例；本期实际可用产能。'),
('供应商故障','scheduled-outage?；random-outage?；random-outage-through；outage-active?','两种来源标记；随机故障含端点结束期；合并故障状态。'),
('合同路线与报价','route-distance；transport-rate；landed-unit-cost','固定距离；固定单位运费；本期报价+单位运费。'),
('合同订单与交付','order-share；units-ordered；units-delivered','相对于该制造商的份额；本期提交订单；本期实际交货。'),
('合同收费','purchase-charge；transport-charge','实际交货量分别乘报价与单位运费。'),
('制造商固定信息','manufacturer-id；demand；initial-inventory；inventory-target','显示编号；每期固定生产需求；初始库存记录；期末库存目标。'),
('制造商库存','inventory；inventory-at-start','inventory 跨期保留，周期结束后是期末库存；inventory-at-start 是本期下单时拍的快照。'),
('制造商下单','order-quantity','希望补货多少；实际提交量由合同上的 units-ordered 加总。'),
('制造商本期物流/生产','amount-received；production-met；unmet-demand','到货量；用库存+到货满足的生产需求；当期丢失需求。'),
('制造商费用','buyer-purchase-cost；buyer-transport-cost；buyer-relationship-cost；buyer-holding-cost','四类本期支出，供全网统计汇总；不保存没有下游用途的个人总额及个人累计副本。'),
]

def build_code():
    download_code='data:text/plain;base64,'+base64.b64encode(CODE.encode()).decode()
    download_xml='data:application/xml;base64,'+base64.b64encode(RAW.encode()).decode()
    content='''<section id="map"><h2>先看整份代码的地图</h2>
<p>这一份按<strong>完整过程</strong>讲解，不把逻辑剪成零散片段。所有 47 个过程／reporter 均有“执行者 → 读取 → 写入 → 逐句提示 → 易错点”，下面的源码块保留完整函数；文件开头的所有声明也完整收录。</p>
<p><strong>行号约定：</strong><code>Code L1</code> 是 NetLogo 的 Code 内容第一行；<code>model.nlogox</code> 的 XML 文件行号在此基础上加 2。第一行注释在文件 L3，<code>go</code> 位于 Code L'''+str(PROCS['go'][0])+'''（文件 L'''+str(PROCS['go'][0]+2)+'''）。</p>
<div class="toolbar"><a class="button" href="'''+download_code+'''" download="model-code-viva-snapshot.nls">下载完整逻辑源码</a><a class="button" href="'''+download_xml+'''" download="model-viva-snapshot.nlogox">下载完整模型快照</a><button type="button" data-print>打印全部讲解与代码</button></div>
<p class="small">页面内已嵌入这次核对的完整快照，离线也可下载。与另一份 HTML 放在同一目录，跨页定位才可用；单独打开仍能读完整正文。</p>
<h3>从哪里进入代码</h3><pre class="calltree">打开文件 → startup → reset-parameters
New map → setup → replay-setup
Replay ─────────→ replay-setup → initialize-scenario 3
BehaviorSpace ────────────────→ initialize-scenario freight-rate
                                   ├ configure-map / restore-settings
                                   ├ create-network
                                   │  ├ initialize-suppliers
                                   │  ├ initialize-manufacturers
                                   │  ├ generate-map → paint-regions
                                   │  └ establish-contracts → cheaper-supplier? → landed-cost-from
                                   └ reset-network-totals → reset-ticks
Step → go 一次；Run / Pause → 重复 go
           ├ 检查参数
           ├ 恢复 → 报价 → 下单 → 新故障 → 配给 → 交货
           ├ 记录供应商利用率 → 制造商生产/库存/费用
           └ 更新颜色/标签/累计指标 → tick</pre>
<p>代码分成 5 组：A 参数与启动；B 初始化；C cycle 机制；D 显示与全网统计；E 指标输出。建议先读 <a href="#proc-go">go</a>，再按它调用的顺序读 C 和 D，最后回头读 B 与 A。</p>
</section>
<section id="language"><h2>NetLogo 阅读钥匙：先问“现在是谁”</h2>'''+table(['写法','读法','本项目中的例子'],[
('<code>to / end</code>','命令过程，执行动作','go、place-orders'),
('<code>to-report / report</code>','reporter 计算并返回值','overall-service-level、cheaper-supplier?'),
('<code>ask manufacturers [...]</code>','当前执行者变为某个制造商','块内 inventory 是该制造商自己的库存。'),
('<code>ask eligible [...]</code>','内层执行者变为合同','[order-quantity] of end1 才能读取制造商希望补货量。'),
('<code>end1 / end2</code>','有向合同起点 / 终点','制造商 / 供应商，方向为订单关系，不是货物流向。'),
('<code>my-out-contracts / my-in-contracts</code>','自己的外出 / 进入合同','制造商用 out 找伙伴；供应商用 in 找所有客户。'),
('<code>[x] of agent</code>','读取别的主体的变量','[unit-price] of end2 读取供应商报价。'),
('<code>with [条件]</code>','筛选 agentset','排除已知停供的合同伙伴。'),
('<code>let / set</code>','新局部变量 / 改已有变量','let eligible 只存在局部；set inventory 改主体状态。'),
('<code>sort / foreach / -&gt;</code>','排序成列表 / 按列表遍历 / 匿名过程参数','foreach sort suppliers [source -&gt; ask source [...]] 固定抽样对应顺序。'),
('<code>ifelse / ifelse-value</code>','执行某分支 / 返回某分支的值','前者用于流程；后者可放在 set available-capacity 后。'),
('<code>with-local-randomness</code>','使用并隔离局部随机流','保证地图、属性和每个供应商周期的故障抽样不会互相消耗随机数。'),
('<code>myself</code>','触发当前 ask/of 等上下文的外层主体','paint-regions 中从候选中心量到待着色 patch 的距离。'),
('<code>ticks / tick</code>','已完成周期数 / 完成一周期后加 1','本期编号在循环内使用 ticks+1。')])+'''
<p>只有 <code>ask</code> 的执行者切换了，变量含义就可能随之改变。看一行代码时先确定上下文，再看变量来自自己还是 <code>of end1/end2</code>。本模型货物可分割，因此交付量和库存出现小数是预期行为。</p></section>
<section id="declarations"><h2>声明部分：谁保存哪些信息</h2>
<p><code>breed</code> 可以理解为“定义一类实体”。<code>breed [suppliers supplier]</code> 定义供应商类型：前面的复数名 suppliers 表示供应商集合，后面的单数名 supplier 用于指某个供应商。manufacturers / manufacturer 同理。声明类型还没有创建实体，后面的 <code>create-suppliers</code> 和 <code>create-manufacturers</code> 才真正生成它们。</p>
<p><code>directed-link-breed [contracts contract]</code> 定义“有方向的合同连线”类型。本模型用 <code>create-contract-to</code> 从制造商连向供应商，表示向谁下单；这个箭头不是货物流向。没有移动、路径规划或独立矿物粒子，货物由合同和主体的数值状态表示。</p>
<p>NetLogo 用分号 <code>;</code> 写行内注释：从分号到这一行末尾的说明不会执行。下方源码已给全部 76 个显式声明变量加上中文解释，并在临时变量和过程参数旁补了说明。<code>globals</code> 中的变量全网共用一份；<code>suppliers-own</code>、<code>manufacturers-own</code> 和 <code>contracts-own</code> 则是每个对应实体或合同各存一份；<code>let</code> 定义的临时变量只在所在作用域内使用。</p>
'''+table(['归属 / 分组','完整变量名或系列','用途与生命周期'],[(a,'<code>'+b.replace('；','</code>；<code>')+'</code>',c) for a,b,c in VARIABLE_ROWS])+'''
<p>界面输入变量不在 <code>globals</code> 中重复声明。全网 <code>period-*</code> 是最近完成一期；<code>cumulative-*</code> 是从初始化累计至今。供应商与制造商都有 received 字样，但 <code>orders-received</code> 是订单，<code>amount-received</code> 是货物。</p>'''+source_block(1,PROCS['startup'][0]-1)+'''</section>
<section id="finder"><h2>完整过程索引</h2><div class="searchbar"><label for="source-search">搜索函数名、变量或中文解释</label><div class="toolbar"><input id="source-search" type="search" placeholder="例如 inventory、断供、place-orders"><button id="clear-search" type="button">清空</button><span id="procedure-count" role="status" aria-live="polite">47 / 47 个过程</span></div><div class="toolbar"><button id="expand-all" type="button">展开所有源码</button><button id="collapse-all" type="button">收起所有源码</button></div><p class="small">搜索只筛选下面 47 个过程，不会删除内容。点击跨页代码链接会自动清空筛选并定位函数。</p></div><div class="group-index">'''+''.join(f'<a href="#{g[0]}">{g[1]}</a>' for g in GROUPS)+'''</div><p id="no-match" class="no-match" hidden>没有匹配过程。可以清空搜索，或试试“库存”“outage”“cost”。</p></section>'''
    names=list(PROCS)
    for group_id,group_title,group_names in GROUPS:
        content+=f'<section class="proc-group" id="{group_id}"><h2>{group_title}</h2><div class="group-index">'+''.join(f'<a href="#proc-{n}">{n}</a>' for n in group_names)+'</div>'
        for name in group_names:
            title,context,reads,writes,steps,pitfall=NOTES[name]
            start,end,_=PROCS[name]
            index=names.index(name)
            display_end=PROCS[names[index+1]][0]-1 if index+1<len(names) else len(LINES)
            content+=f'''<article class="proc" id="proc-{name}"><div class="signature">{index+1:02d} / 47 · {esc(context)} · Code L{start}–{end} · 文件 L{start+2}–{end+2}</div><h3><code>{name}</code><br>{title}</h3><div class="io"><div><b>读取</b>{esc(reads)}</div><div><b>写入 / 返回</b>{esc(writes)}</div></div><ol>'''+''.join(f'<li>{esc(s)}</li>' for s in steps)+f'</ol><p class="gotcha"><strong>讲解时别混淆：</strong>{esc(pitfall)}</p>'+source_block(start,display_end,name in ('go','place-orders'))+'</article>'
        content+='</section>'
    widgets=[]
    for w in MODEL.find('widgets'):
        if w.tag=='button': widgets.append((esc(w.get('display')),esc(w.text), 'Observer 命令；重复运行' if w.get('forever')=='true' else 'Observer 命令；单次'))
        elif w.tag=='monitor': widgets.append((esc(w.get('display')),'<code>'+esc(w.text)+'</code>','显示 reporter / 全局变量'))
    plots=[]
    for plot in MODEL.find('widgets').findall('plot'):
        for pen in plot.findall('pen'):
            plots.append((plot.get('display'),pen.get('display'),'<code>'+esc(pen.findtext('update'))+'</code>'))
    content+='''<section id="xml"><h2>Code 之外：界面和实验也是文件的一部分</h2>
<p><code>.nlogox</code> 是 XML 容器，包含 <code>code</code>、<code>widgets</code>、<code>info</code>、<code>turtleShapes</code>、<code>linkShapes</code>、<code>previewCommands</code> 和 <code>experiments</code>。上面覆盖所有模型过程；这一节补充写在界面和实验定义中的可执行内容。</p>
<h3>按钮与监视器实际调用</h3>'''+table(['界面标签','实际表达式','性质'],widgets)+'''
<h3>图表更新代码</h3>'''+table(['图表','笔 / 系列','完整 update 表达式'],plots)+'''
<p>Demand and production 在 ticks&gt;0 时画逐期需求与产出。费用图的 plot-level update 是 <code>clear-plot</code>，每期清掉旧柱子再画 Buy/Ship/Links/Stock。它们由 <code>tick</code> 更新图表触发，不是把经济逻辑再执行一次。图表 setup 块均为空。</p>
<h3>空间、图标和预览</h3><p>view 设置 <code>wrappingAllowedX="false"</code> 和 <code>wrappingAllowedY="false"</code>，所以世界不环绕；距离按有限平面计算。38 个 turtleShapes 定义包含许多 NetLogo 默认图标，但代码只给供应商用 box、制造商用 house。它们没有隐藏的经济机制。<code>info</code> 是说明文本。</p><p>预览命令完整内容为 <code>setup repeat 75 [ go ]</code>，供模型预览使用。它调用 New map 并运行 75 期，不是交互 Replay 自动执行 75 期。</p>
<h3>14 个界面输入的来源</h3>'''
    controls=[]
    for w in MODEL.find('widgets'):
        if w.tag in ('slider','input'):
            controls.append(('<code>'+esc(w.get('variable'))+'</code>',w.get('default') if w.tag=='slider' else esc(w.text),w.tag,('min '+w.get('min')+'；max '+w.get('max')+'；step '+w.get('step')) if w.tag=='slider' else '范围由 validate-settings 统一检查'))
    content+=table(['变量','保存的默认值','界面类型','界面范围 / 校验'],controls)
    content+='''<h3>六组 BehaviorSpace 实验</h3><p>情景种子 2026–2055 对应地图种子 1–30，实验 setup 用 <code>set map-seed scenario-seed - 2025</code> 配对。参数组合本身枚举了 30 个情景，因此 repetitions=1 不等于只做一个随机情景。每场 500 cycle，记录终点指标。</p>
'''+table(['实验','变化维度','固定条件与次数'],[
('sourcing-risk-comparison','k=1/2/3；风险=0/2/5%','运费 3；30 情景；3×3×30=270 场，每场 500 cycle。'),
('capacity-sensitivity','k=1/2/3；容量基准=60/80/100；风险=0/2%','30 情景；540 场。'),
('inventory-target-sensitivity','k=1/2/3；库存目标倍数=0/1/2；风险=0/2%','30 情景；540 场。'),
('transport-sensitivity','k=1/2/3；运费=2/3/4','风险 2%；30 情景；270 场。'),
('price-feedback-sensitivity','k=1/2/3；价格反馈=0/0.20/0.40；风险=0/2%','30 情景；540 场。'),
('accounting-fee-sensitivity-rerun','k=1/2/3；目标倍数=0/1/2；维护费=0/50/100；持有费=0/1/2','风险 2%；30 情景；2,430 场重新运行。')])+'''
<p>六组都固定人口 5×10、需求 30–50、随机时长 1–10、指定故障关闭。未变化的参数采用容量基准 100、目标倍数 1、运费 3、价格反馈 0.20、维护费 50、持有费 1。初始库存仍抽取 40–80，修改目标不会额外发放库存。界面暂时改人数不会改变保存的实验设置。</p>
<p><strong>新增四组的 setup 为什么多几行：</strong><code>initialize-scenario</code> 会 clear-all 并重置经济参数。setup 先用局部变量保存目标、价格反馈和费用，初始化后恢复，再把制造商的目标设为 demand × 倍数。目标赋值放在 <code>with-local-randomness</code> 中，不干扰模型随机流。运费直接作为初始化参数传入，确保在初始选商之前生效。</p>
<p>六组全跑共 4,590 场，其中前五组共 2,160 条记录，去掉跨组重叠后是 1,530 个不同参数／种子组合。原风险与运费两组仍共享 90 场基准，两者去重后为 450 场。不能把重叠基准或不同费用下的同一物理轨迹当成独立重复样本。</p>
<details class="source"><summary>完整实验 XML：全部参数、指标和运行设置</summary><pre><code>'''+esc(RAW[RAW.index('  <experiments>'):RAW.index('  </experiments>')+len('  </experiments>')])+'''</code></pre></details>
<p><strong>原报告与现在的区别：</strong>原六组研究由 NetLogo 后台引擎加 Java 运行器完成，当时只保存了风险和运费两个 BehaviorSpace 定义；其费用组对 270 条已有轨迹按九种费率重新计价，没有新增物理轨迹。现在补齐的费用实验会实际重跑 2,430 次以复现相同账本，速度较慢。报告中额外的拥堵观测、1,000-cycle 检查和配对统计仍由下载包中的观察层与分析脚本完成，不能只凭这些终点输出声称重新生成了整份报告。</p></section>
<section id="trace"><h2>跨函数追一遍：一个值是怎么走完系统的</h2>
<h3>库存从上一期走到下一期</h3><div class="formula">inventory（上期结余）<br>→ place-orders：inventory-at-start = inventory；Q = D + T − inventory<br>→ deliver-orders：每条合同产生 units-delivered<br>→ update-manufacturer-results：amount-received = Σ units-delivered<br>→ available = inventory-at-start + amount-received<br>→ production-met = min(demand, available)<br>→ inventory = available − production-met<br>→ 下一期 place-orders 再读这个 inventory</div>
<h3>本期的报价不会被本期订单反向修改</h3><div class="formula">record-supplier-results（t−1）：capacity-utilization<br>→ update-supplier-prices（t）：pricing-utilization → unit-price<br>→ 合同 landed-unit-cost → place-orders 的倒数成本份额<br>→ allocate-supply → deliver-orders<br>→ record-supplier-results（t）：写新 capacity-utilization<br>→ update-supplier-prices（t+1）：才形成下一期报价</div>
<h3>为什么清零位置不同？</h3><p><code>place-orders</code> 先把每条合同的订单和份额清零，因为没获得新订单的合同也必须归零。其他本期结果在后续过程里对全体对象覆盖重算，例如 deliver-orders 总会重新写每条合同的交货和费用；累计量则只能做加法，不能每期归零。</p>
<h3>没有写在代码里的机制，不能在 viva 中声称存在</h3><p>没有根据拥堵重新优化供应商组合、没有自动换伙伴、没有运输在途时间、没有需求季节性、没有供应商因收入再投资、没有区域相关故障、没有机器学习或均衡求解。订单倒数成本权重与上一期利用率加价是明确的行为规则；反馈可产生复杂结果，但不是最优策略求解器。</p>
</section><section id="review"><h2>代码追问练习</h2>'''
    for q,a in [
('考官指着 [order-quantity] of end1：为什么不能直接写 order-quantity？','这里已经进入 ask eligible，即合同上下文。order-quantity 属于制造商，因此要显式读取合同起点 end1。'),
('为什么 create-contract-to 的方向与货物运输方向相反？','连线代表采购/下单关系：制造商指向供应商；交货由合同记录数值，方向不会自动决定运输。'),
('为什么先设 transport-cost-per-distance 再 create-network？','初始伙伴排序已经依赖运费。先选商再改运费会把一个运费条件下的合同网络错误地用到另一个条件。'),
('为什么 update-supplier-prices 放在 record-supplier-results 前？','它必须读取上一期利用率。本期发货在后面记录，用于下一期报价，避免同一期循环依赖。'),
('settings-snapshot 为什么有用？','一方面防止 clear-all 丢掉待用的内部设置，另一方面确保 go 期间界面参数未改变。'),
('with-local-randomness 与固定 seed 是同一个作用吗？','固定 seed 使某段抽样可复现；局部随机流让这段抽样不污染外围随机状态。再通过每个供应商/周期的专用 seed，使外部故障不随采购策略变化。'),
('为什么故障时 fill-ratio=0，但正常零订单时 fill-ratio=1？','两者都产生零交付，但含义不同：前者完全不可供货，后者没有配给短缺且避免除零。'),
('unit-price 和 landed-unit-cost 有何区别？','前者只有供应商采购报价，后者加上合同路线的每单位运费；固定合同费、库存费均不在其中。'),
('为什么统计 reporter 返回 false，不返回 0？','在需求或满足量为 0 时比率未定义。返回 false 标记缺失，比返回一个可误解为真实结果的 0 更明确。界面包装再转 N/A。'),
('如果要加入“第二轮紧急采购”，从哪里改，为什么不是一行？','必须在新故障之后设计剩余订单、剩余产能、第二轮分配和计费规则，并明确是否重复交货；不能直接再调用 place-orders，因为它会清零和覆盖第一次的订单。这里只解释改动边界，当前模型没有这个机制。'),
    ]: content+=qa(q,a)
    content+='''<p>复习到这里，可以回到<a href="cycle-walkthrough.zh.html#demo">逐周期演示</a>，尝试每一步先说出将调用哪个过程，再看数值验证。</p></section>'''
    return content

CODE_JS = r'''
const articles=[...document.querySelectorAll('.proc')],search=document.querySelector('#source-search');
const searchable=articles.map(a=>a.textContent.toLowerCase());
function filter(){const q=search.value.trim().toLowerCase();let n=0;articles.forEach((a,i)=>{a.hidden=!searchable[i].includes(q);if(!a.hidden)n++});document.querySelector('#procedure-count').textContent=n+' / 47 个过程';document.querySelector('#no-match').hidden=n>0;document.querySelectorAll('.proc-group').forEach(g=>g.hidden=![...g.querySelectorAll('.proc')].some(a=>!a.hidden))}
search.addEventListener('input',filter);
document.querySelector('#clear-search').addEventListener('click',()=>{search.value='';filter();search.focus()});
document.querySelector('#expand-all').addEventListener('click',()=>document.querySelectorAll('details.source').forEach(d=>d.open=true));
document.querySelector('#collapse-all').addEventListener('click',()=>document.querySelectorAll('details.source').forEach(d=>d.open=false));
function reveal(){let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return}const el=document.getElementById(id);if(!el)return;const article=el.closest('.proc'),group=el.closest('.proc-group');if(article||group){search.value='';filter()}if(article)article.querySelector('details.source').open=true;const detail=el.closest('details');if(detail)detail.open=true;requestAnimationFrame(()=>el.scrollIntoView({block:'start'}))}
addEventListener('hashchange',reveal);reveal();filter();
'''

if __name__=='__main__':
    flow_toc=[('refresh','找回项目主线'),('setup','初始化'),('cycle','Cycle 的 12 步'),('demo','七期逐步演示'),('equations','七条核心公式'),('outages','断供与价格时点'),('checks','守恒与现场演示'),('experiments','实验与解释边界'),('talk','中英文口述'),('quiz','Viva 自测')]
    code_toc=[('map','代码地图与下载'),('language','NetLogo 阅读钥匙'),('declarations','全部变量声明'),('finder','过程搜索'),*[(g[0],g[1]) for g in GROUPS],('xml','界面与实验 XML'),('trace','跨函数追踪'),('review','代码追问练习')]
    (OUT/'cycle-walkthrough.zh.html').write_text(page('从初始化到每个 cycle','把一场模拟讲清楚：沿着订单、产能、库存和价格，逐步走完真实执行顺序。',flow_toc,build_flow(),FLOW_JS))
    (OUT/'code-walkthrough.zh.html').write_text(page('完整代码，从入口读到结果',f'逐个解释 47 个过程，保留全部 {len(LINES)} 行模型逻辑，并补齐界面与实验中的执行代码。',code_toc,build_code(),CODE_JS))
    print(json.dumps({'procedures':len(PROCS),'code_lines':len(LINES),'teaching_cycles':len(TRACE),'model_sha256':SHA,'files':['docs/cycle-walkthrough.zh.html','docs/code-walkthrough.zh.html']},ensure_ascii=False))
