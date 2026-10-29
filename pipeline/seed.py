"""Một lần: dựng store/daily.json từ dữ liệu cũ (chốt 27/10) + inbox backfill 28–29/10."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
T = sorted(json.load(open(H + "lists121.json")))

# ngày giao dịch: nến TCM (70 phiên tới 28/10) + 29/10
raw = json.load(open(H + "inbox/seed_raw2810b.json"))
k = [k for k in raw["TCM"] if "price" in k][0]
bars = raw["TCM"][k]; bars = json.loads(bars) if isinstance(bars, str) else bars
dates = sorted(b["date"] for b in bars["bars"])
dates = [d for d in dates if d <= "2026-10-27"]
i27 = len(dates) - 1

close, vol, nn, td = {}, {}, {}, {}
for l in open(H + "raw2810/cls121.txt"):           # 21 giá, mới nhất trước, chốt 27/10
    p = l.split(); v = [float(x) for x in p[1:]]
    close[p[0]] = {dates[i27 - j]: x for j, x in enumerate(v)}
V27 = {}
for l in open(H + "raw2710b/vpend.txt"):
    t, x = l.split(); V27[t] = float(x)
FD = ["2026-10-27", "2026-10-26", "2026-10-23", "2026-10-22", "2026-10-21",
      "2026-10-20", "2026-10-19", "2026-10-16", "2026-10-15", "2026-10-14"]
for l in open(H + "raw2810/f27_121.txt"):
    t, sig, f, p, v = l.strip().split("|")
    if v != "-": V27[t] = float(v)
    nn[t] = dict(zip(FD, map(float, f.split()))); td[t] = dict(zip(FD, map(float, p.split())))
for l in open(H + "raw2810/vol121.txt"):           # 31 KL, mới nhất trước, chốt 26/10
    p = l.split(); v = [float(x) for x in p[1:]]
    vol[p[0]] = {dates[i27 - 1 - j]: x for j, x in enumerate(v)}
    vol[p[0]]["2026-10-27"] = V27[p[0]]

bf = json.load(open(H + "inbox/2026-10-29_backfill.json"))
new_dates = ["2026-10-28", "2026-10-29"]
dates += new_dates
adj = {}
for t in T + ["VN30", "VNINDEX"]:
    b = bf["bars"][t]
    if t == "VNINDEX":
        close[t] = {d: v[0] for d, v in b.items()}; continue
    c27 = b["2026-10-27"][0]
    ratio = c27 / close[t]["2026-10-27"]
    if abs(ratio - 1) > 0.003:                       # FinLens đã điều chỉnh giá (cổ tức/chia tách): co giãn lịch sử
        adj[t] = round(ratio, 4)
        close[t] = {d: x * ratio for d, x in close[t].items()}
        if t in vol: vol[t] = {d: x / ratio for d, x in vol[t].items()}
    for d in new_dates:
        close[t][d] = b[d][0]
        if t in vol: vol[t][d] = float(b[d][1])

# dòng tiền 28–29/10 từ flows_top_net (top 30 mỗi sàn mỗi chiều; mã ngoài top coi như ≈ 0)
def table(ft, days):
    m = {}
    for f in bf["flows"]:
        if f["in"]["flow_type"] == ft and f["in"].get("days") == days:
            for tk, v in f["items"]: m[tk] = v
    return m
f1, f2 = table("foreign", 1), table("foreign", 2)
p1 = table("proprietary", 1)
for t in T:
    nn[t]["2026-10-29"] = f1.get(t, 0.0)
    nn[t]["2026-10-28"] = round(f2.get(t, 0.0) - f1.get(t, 0.0), 2)
    td[t]["2026-10-28"] = p1.get(t, 0.0)

store = {"dates": dates, "close": close, "vol": vol, "nn": nn, "td": td,
         "nnAsof": "2026-10-29", "tdAsof": "2026-10-28", "volSrc": {},
         "tv": {"asof": "2026-10-29", "perf": {}}, "adj": adj}
for sym, v in bf["tv"].items():
    t = sym.split(":")[1]
    if t in T or t in ("VN30", "VNINDEX"):
        store["tv"]["perf"][t] = {"w": v.get("Perf.W"), "m1": v.get("Perf.1M"), "m3": v.get("Perf.3M"), "m6": v.get("Perf.6M"),
                                  "close": v.get("close"), "vol": v.get("volume")}
json.dump(store, open(H + "store/daily.json", "w"))
print(len(dates), dates[-5:], "điều chỉnh:", adj)
