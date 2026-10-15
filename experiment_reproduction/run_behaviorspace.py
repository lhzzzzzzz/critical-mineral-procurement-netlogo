"""用真正的 BehaviorSpace 导出六份 Table CSV；仅在本目录模型副本中增加观测。"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
EXPERIMENTS = {
    "01_risk": "sourcing-risk-comparison",
    "02_capacity": "capacity-sensitivity",
    "03_inventory": "inventory-target-sensitivity",
    "04_transport": "transport-sensitivity",
    "05_price_feedback": "price-feedback-sensitivity",
    "06_fees": "accounting-fee-sensitivity-rerun",
}
OBSERVATION_GLOBALS = """
  repro-stock-sum repro-available-sum repro-unused-sum repro-out-sum
  repro-buyer-short-sum repro-congested-sum repro-shortage-cycles
"""
OBSERVATION_CODE = """

;; Observation only: the original go procedure and all decisions are unchanged.
to reproduction-step
  go
  with-local-randomness [
    set repro-stock-sum repro-stock-sum + total-inventory
    set repro-available-sum repro-available-sum + sum [available-capacity] of suppliers
    set repro-unused-sum repro-unused-sum + sum [available-capacity - amount-shipped] of suppliers
    set repro-out-sum repro-out-sum + count suppliers with [outage-active?]
    set repro-buyer-short-sum repro-buyer-short-sum + count manufacturers with [unmet-demand > 0.000001]
    set repro-congested-sum repro-congested-sum + count suppliers with [not outage-active? and orders-received > capacity + 0.000001]
    if period-unmet > 0.000001 [set repro-shortage-cycles repro-shortage-cycles + 1]
    if abs (initial-inventory-total + cumulative-received - cumulative-fulfilled - total-inventory) > 0.00001 [error "Reproduction: stock conservation"]
    if abs (period-total-cost - period-purchase-cost - period-transport-cost - period-relationship-cost - period-holding-cost) > 0.00001 [error "Reproduction: cost conservation"]
    if any? suppliers with [amount-shipped > available-capacity + 0.000001 or amount-shipped < -0.000001] [error "Reproduction: capacity"]
    if any? suppliers with [unit-price < base-price - 0.000001 or unit-price > base-price * (1 + price-response) + 0.000001] [error "Reproduction: price bounds"]
  ]
end
"""
EXTRA_METRICS = [
    "repro-stock-sum", "repro-available-sum", "repro-unused-sum", "repro-out-sum",
    "repro-buyer-short-sum", "repro-congested-sum", "repro-shortage-cycles",
    "sum [capacity] of suppliers", "sum [demand] of manufacturers", "count contracts",
    "count suppliers with [any? my-in-contracts]", "max [count my-in-contracts] of suppliers",
]


def prepare_model(source, directory, observe=True):
    """保存确切来源和观测副本。原始源码只追加变量/记录过程，不重写 go。"""
    original = source.read_text(encoding="utf-8")
    tree = ET.fromstring(original)
    if len(tree.findall("experiments/experiment")) != 6:
        raise ValueError("需要含六组已保存实验的模型。")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "source.nlogox").write_text(original, encoding="utf-8")
    if not observe:
        return directory / "source.nlogox"
    code = tree.findtext("code")
    observed = code.replace("globals [", "globals [" + OBSERVATION_GLOBALS, 1) + OBSERVATION_CODE
    text = original.replace(code, observed, 1)
    for exp in tree.find("experiments"):
        exp.find("go").text = "reproduction-step"
        for metric in EXTRA_METRICS:
            ET.SubElement(exp.find("metrics"), "metric").text = metric
    a, b = text.index("  <experiments>"), text.index("  </experiments>") + len("  </experiments>")
    text = text[:a] + "  " + ET.tostring(tree.find("experiments"), encoding="unicode") + text[b:]
    dest = directory / "observed.nlogox"
    dest.write_text(text, encoding="utf-8")
    return dest


def find_java(explicit=None):
    if explicit:
        return explicit
    if os.environ.get("JAVA_HOME"):
        return str(Path(os.environ["JAVA_HOME"]) / "bin/java")
    installed = sorted((Path.home() / "Library/Java/JavaVirtualMachines").glob("*/Contents/Home/bin/java"))
    return str(installed[-1]) if installed else shutil.which("java")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, default=ROOT.parent / "model.nlogox")
    p.add_argument("--netlogo", type=Path, default=Path(os.environ.get("NETLOGO_HOME", "/Applications/NetLogo 7.0.4")))
    p.add_argument("--java", default=None)
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--only", nargs="+", choices=list(EXPERIMENTS), default=list(EXPERIMENTS))
    p.add_argument("--plain", action="store_true", help="原样模型；CSV 不含额外观测。")
    p.add_argument("--output", type=Path, default=ROOT / "raw")
    args = p.parse_args()
    java = find_java(args.java)
    if not java or not (args.netlogo / "app/netlogo-7.0.4.jar").exists():
        raise SystemExit("请通过 --java 和 --netlogo 指定 Java 与 NetLogo 7.0.4 安装。")
    if args.threads < 1:
        raise SystemExit("--threads 必须为正整数。")
    args.output.mkdir(parents=True, exist_ok=True)
    model = prepare_model(args.model, args.output.parent / "models", not args.plain)
    metadata = {"source_model": str(args.model.resolve()), "source_sha256": hashlib.sha256(args.model.read_bytes()).hexdigest(),
                "run_model": str(model.resolve()), "run_model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
                "observation_only": not args.plain, "threads": args.threads, "runs": []}
    for short, name in EXPERIMENTS.items():
        if short not in args.only:
            continue
        out = args.output / f"{short}.csv"
        partial = args.output / f"{short}.partial.csv"
        log = args.output / f"{short}.log"
        cmd = [java, "-Xmx1024m", "-Djava.awt.headless=true", "-Dfile.encoding=UTF-8", "-cp", str(args.netlogo / "app/*"),
               "org.nlogo.headless.Main", "--model", str(model), "--experiment", name, "--table", str(partial), "--threads", str(args.threads)]
        start = time.monotonic()
        print(f"Running {name} ...", flush=True)
        with log.open("w", encoding="utf-8") as stream:
            result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(f"运行失败：{log}；未把不完整 CSV 当作成功输出。")
        # NetLogo 个别运行报错也可能正常退出，因此分析器还会检查网格、结束步数和守恒。
        with partial.open(newline="", encoding="utf-8-sig") as stream:
            data = list(csv.reader(stream))
        head = next(i for i, row in enumerate(data) if row and row[0] == "[run number]")
        count = sum(bool(row) for row in data[head + 1:])
        partial.replace(out)
        record = {"experiment": name, "csv": out.name, "rows": count, "seconds": round(time.monotonic() - start, 3),
                  "sha256": hashlib.sha256(out.read_bytes()).hexdigest(), "command": cmd}
        metadata["runs"].append(record)
        (args.output / "run_manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(f"Finished {short}: {count} rows in {record['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
