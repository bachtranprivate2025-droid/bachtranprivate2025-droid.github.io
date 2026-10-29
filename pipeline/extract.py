"""Gom kết quả tool (FinLens price_history, flows_top_net, TradingView batch) từ log phiên hiện tại
vào pipeline/inbox/<tag>.json — agent không phải chép lại số liệu bằng tay.

Dùng:  python3 pipeline/extract.py <tag> [đường_dẫn_log.jsonl]
Mặc định đọc file .jsonl mới nhất trong ~/.claude/projects/**/ (phiên đang chạy).
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else "pull"
if len(sys.argv) > 2:
    logs = [sys.argv[2]]
else:
    logs = sorted(glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True), key=os.path.getmtime)[-1:]

uses, res = {}, {}
def walk(x):
    if isinstance(x, dict):
        if x.get("type") == "tool_use" and "id" in x:
            uses[x["id"]] = (x.get("name") or "", x.get("input") or {})
        if x.get("type") == "tool_result" and "tool_use_id" in x:
            c = x.get("content")
            if isinstance(c, list):
                c = "".join(b.get("text", "") for b in c if isinstance(b, dict))
            res[x["tool_use_id"]] = c
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
for f in logs:
    for line in open(f, encoding="utf-8"):
        try: walk(json.loads(line))
        except Exception: pass

out = {"bars": {}, "flows": [], "tv": {}, "stockflow": {}, "dividends": []}
for i, (name, inp) in uses.items():
    if i not in res or not isinstance(res[i], str): continue
    try: d = json.loads(res[i])
    except Exception: continue
    if name.endswith("stocks_get_price_history") and d.get("bars"):
        m = out["bars"].setdefault(d["ticker"], {})
        for b in d["bars"]: m[b["date"]] = [b["close"], b["volume"]]
    elif name.endswith("flows_top_net") and "items" in d:
        out["flows"].append({"in": inp, "period_from": d.get("period_from"), "period_to": d.get("period_to"),
                             "items": [[x["ticker"], x["net_bil"]] for x in d["items"]]})
    elif name.endswith("flows_get_stock_flow") and d.get("series"):
        m = out["stockflow"].setdefault(d["ticker"], {})
        for x in d["series"]: m[x["date"]] = [x.get("foreign_net_bil") or 0.0, x.get("prop_net_bil") or 0.0]
    elif name.endswith("dividends_upcoming") and "items" in d:
        out["dividends"] += [dict(t=x["symbol"], ex=x["ex_date"], pay=x.get("pay_date"), kind=x["kind"], terms=x.get("terms"),
                                  yld=x.get("cash_yield_pct"), title=x.get("title"), src="FinLens", asof=d.get("as_of")) for x in d["items"]]
    elif name.endswith("get-symbol-data-batch") and isinstance(d.get("data"), dict):
        out["tv"].update(d["data"])
os.makedirs(os.path.join(HERE, "inbox"), exist_ok=True)
p = os.path.join(HERE, "inbox", tag + ".json")
json.dump(out, open(p, "w"), ensure_ascii=False)
print(f"{p}: {len(out['bars'])} mã có nến, {len(out['flows'])} lệnh flows, {len(out['tv'])} mã TradingView")
