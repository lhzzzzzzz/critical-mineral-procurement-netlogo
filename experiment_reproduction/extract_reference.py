"""从原 HTML 的内嵌 ZIP 提取历史对照；这些文件只用于验证，不参与新结果计算。"""
from pathlib import Path
from html.parser import HTMLParser
import argparse
import base64
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parent


class EmbeddedZip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.active = dict(attrs).get("id") == "zip-data"

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.chunks.append(data)


def extract(report, output):
    parser = EmbeddedZip()
    parser.feed(report.read_text(encoding="utf-8"))
    if not parser.chunks:
        raise ValueError("HTML 中没有 zip-data，不能假定历史参考结果存在。")
    payload = base64.b64decode("".join(parser.chunks), validate=True)
    output.mkdir(parents=True, exist_ok=True)
    # 白名单提取，不执行历史包中的任何程序，也不接受包内路径。
    names = ["results-500.csv", "summary.json", "manifest.json", "model.nlogox", "analyze.py", "README.txt"]
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for name in names:
            (output / name).write_bytes(archive.read(name))
    provenance = {
        "source_html": str(report.resolve()),
        "html_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        "embedded_zip_sha256": hashlib.sha256(payload).hexdigest(),
        "purpose": "Historical reference only; never used to fill new simulation data.",
        "files": {n: hashlib.sha256((output / n).read_bytes()).hexdigest() for n in names},
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(f"Historical reference: {output}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, default=ROOT.parent / "experiment-results.html")
    p.add_argument("--output", type=Path, default=ROOT / "reference")
    args = p.parse_args()
    extract(args.report, args.output)
