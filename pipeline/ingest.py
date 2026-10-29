"""Nạp số liệu kéo trong ngày (inbox/<tag>.json do extract.py tạo) vào store/daily.json.

python3 pipeline/ingest.py pipeline/inbox/<tag>.json

- TradingView batch: giá đóng cửa, KL (gồm thỏa thuận), Perf W/1M/3M/6M, quote ETF/hàng hóa.
- FinLens flows_top_net (days=1): khối ngoại phiên mới nhất; tự doanh phiên mà nguồn đã chốt.
- FinLens price_history: KL khớp lệnh (ưu tiên hơn TradingView) + phát hiện giá đã điều chỉnh.
Chạy lại nhiều lần với cùng inbox không sao (ghi đè cùng ngày).
In ra danh sách mã cần kiểm KL bằng FinLens (RVOL theo TradingView ≥ 1,4×).
"""
import json, os, sys, statistics
H = os.path.dirname(os.path.abspath(__file__)) + "/"
ST = json.load(open(H + "store/daily.json"))
T = sorted(json.load(open(H + "lists121.json")))
IN = json.load(open(sys.argv[1]))
SYMS = json.load(open(H + "conf/syms.json"))
tvt = {k.split(":")[1]: v for k, v in IN["tv"].items()}

fl = [f for f in IN["flows"] if f["in"].get("days", 5) == 1]
nn_to = [f["period_to"] for f in fl if f["in"]["flow_type"] == "foreign"]
asof = max(nn_to) if nn_to else (sys.argv[2] if len(sys.argv) > 2 else None)
assert asof, "không xác định được phiên: cần flows foreign days=1 hoặc truyền ngày"
dates = ST["dates"]
if asof not in dates:
    assert asof > dates[-1], f"phiên {asof} cũ hơn store"
    dates.append(asof)
vs = ST.setdefault("volSrc", {})

# 1) TradingView
for t in T + ["VN30", "VNINDEX"]:
    v = tvt.get(t)
    if not v: continue
    k = 1 if t in ("VN30", "VNINDEX") else 1000
    ST["close"].setdefault(t, {})[asof] = v["close"] / k
    if t in T and vs.get(t, {}).get(asof) != "finlens":
        ST["vol"].setdefault(t, {})[asof] = float(v["volume"]); vs.setdefault(t, {})[asof] = "tv"
    ST["tv"]["perf"][t] = {"w": v.get("Perf.W"), "m1": v.get("Perf.1M"), "m3": v.get("Perf.3M"), "m6": v.get("Perf.6M"),
                           "close": v.get("close"), "vol": v.get("volume")}
if tvt: ST["tv"]["asof"] = asof

# 2) FinLens nến: KL khớp lệnh + điều chỉnh giá
for t, bars in IN["bars"].items():
    if t not in ST["close"]: ST["close"][t] = {}
    old = ST["close"][t]
    ref = [d for d in sorted(bars) if d in old and d < asof and vs.get(t, {}).get(d) != "tv"]
    if ref:
        d = ref[-1]; ratio = bars[d][0] / old[d]
        if abs(ratio - 1) > 0.003:
            for x in list(old):
                if x not in bars: old[x] *= ratio
            for x in list(ST["vol"].get(t, {})):
                if x not in bars: ST["vol"][t][x] /= ratio
            ST.setdefault("adj", {})[t] = round(ST.get("adj", {}).get(t, 1) * ratio, 4)
            print(f"⚠️ {t}: FinLens điều chỉnh giá ×{ratio:.4f}, đã co giãn lịch sử")
    for d, (c, v) in bars.items():
        if d in dates or d == asof:
            old[d] = c
            if t in T:
                ST["vol"].setdefault(t, {})[d] = float(v); vs.setdefault(t, {})[d] = "finlens"

# 3) Dòng tiền
for f in fl:
    ft, d = f["in"]["flow_type"], f["period_to"]
    key = {"foreign": "nn", "proprietary": "td"}.get(ft)
    if not key: continue
    for t in T: ST[key].setdefault(t, {}).setdefault(d, 0.0)   # ngoài top 30 ≈ 0
    for tk, v in f["items"]:
        if tk in ST[key]: ST[key][tk][d] = v
    if key == "nn": ST["nnAsof"] = max(ST["nnAsof"], d)
    else: ST["tdAsof"] = max(ST["tdAsof"], d)

# 4) Quote ETF / hàng hóa -> conf/quotes2.json
q = {k: [v["close"], v.get("SMA20"), v.get("SMA50"), v.get("Perf.1M"), v.get("change"), v.get("description")]
     for k, v in IN["tv"].items() if k in SYMS["syms"] and "SMA20" in v}
if q:
    json.dump({"asof": f"TradingView tối {asof} (ETF Mỹ/EU chốt phiên trước giờ VN)", "spy1m": q.get("AMEX:SPY", [0, 0, 0, 0])[3], "q": q},
              open(H + "conf/quotes2.json", "w"), ensure_ascii=False)

# 5) Kiểm tra + cắt store
miss = [t for t in T if asof not in ST["close"].get(t, {})]
need = []
for t in T:
    v = ST["vol"].get(t, {})
    prev = [v[d] for d in dates[-21:-1] if d in v]
    if asof in v and len(prev) == 20 and vs.get(t, {}).get(asof) != "finlens":
        rv = v[asof] / statistics.mean(prev)
        if rv >= 1.4: need.append((t, round(rv, 2)))
ST["dates"] = dates[-90:]
json.dump(ST, open(H + "store/daily.json", "w"))
print(f"phiên {asof}: NN tới {ST['nnAsof']}, TD tới {ST['tdAsof']}, thiếu giá {miss or 'không'}")
print("CẦN KIỂM KL FinLens (limit=2):", " ".join(t for t, _ in need) or "không", need)
