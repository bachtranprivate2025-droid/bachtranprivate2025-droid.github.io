import json, sys, copy, statistics

import os, datetime
RUN = os.path.dirname(os.path.abspath(__file__)) + "/"
RAW = RUN + "raw_add2/"
SRC = RUN + "template/VN_3_PORTFOLIOS_2026-10-23.html"
OUT = RUN + "out/report.html"
R26 = RUN + "raw2610_add2/"

src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
PRE = '<script id="report-data" type="application/json">'
assert lines[111].startswith(PRE)

base = json.load(open(RUN + "base_data.json"))
BASE = {r["t"]: r for r in base["rows"]}
LISTS = json.load(open(RUN + "lists121.json"))
FLOW_DATES = ["2026-10-27", "2026-10-26", "2026-10-23", "2026-10-22", "2026-10-21",
              "2026-10-20", "2026-10-19", "2026-10-16", "2026-10-15", "2026-10-14"]
WIN = "2025-10-25"  # cửa sổ 12 tháng cho giao dịch nội bộ

def vn(x, d=0):
    return f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
def sgn(x, d=0):
    return ("+" if x > 0 else "−" if x < 0 else "") + vn(x, d)
def dmy(iso):
    y, m, dd = iso.split("-"); return f"{dd}/{m}/{y}"
def iso_from_dmy2(s):
    dd, m, yy = s.split("/"); return f"20{yy}-{m}-{dd}"
def num(s):
    return None if s in ("null", "None") else float(s)

# ---------- load raw ----------
def rd(name):  # file gốc 85 mã + file *_new (8 mã RVOL TEST vni)
    import os
    out = list(open(RAW + name + ".txt", encoding="utf-8"))
    if os.path.exists(RAW + name + "_new.txt"):
        out += list(open(RAW + name + "_new.txt", encoding="utf-8"))
    return [l for l in out if l.strip()]
RS_OLD = {}
for fn in ("rs_1.txt", "rs_2.txt", "rs_3.txt"):
    for l in open(RAW + fn):
        t, a, b, c, d, v = l.split()
        RS_OLD[t] = dict(rs=num(a), breadth=num(b), leader=num(c), mom=num(d), avgval=float(v))
RS = {}
for l in open(R26 + "rs.txt"):
    t, a, b, c, d, v = l.split()
    RS[t] = dict(rs=num(a), breadth=num(b), leader=num(c), mom=num(d), avgval=float(v))
RS["C4G"] = RS_OLD["C4G"]  # 27/10 signals_screen không trả C4G: giữ RS 23/10
PX = {}
for l in open(R26 + "px.txt"):
    t, a, b = l.split(); PX[t] = (float(a), float(b))
ICBPX = {}
for l in open(R26 + "icbpx.txt"):
    k, *v = l.split(); ICBPX[k] = [num(x) for x in v]
ICBBAD = {}
for l in open(R26 + "icbbad.txt"):
    k, *v = l.split(); ICBBAD[k] = set(v)
ICBSTR = {}
for l in open(R26 + "icbstr.txt"):
    k, *v = l.split(); v = [num(x) for x in v]
    ICBSTR[k] = dict(sector_rs=v[0], sector_rs_score=v[1], breadth_rs=v[2], breadth_n_stocks=v[3], n_stocks=v[4],
                     r12=v[5], r6=v[6], r3=v[7], r1=v[8], divergence=v[9], asof="2026-10-27")
SSI = {}
for l in open(R26 + "ssifa.txt"):
    p = l.split()
    SSI[p[0]] = None if p[1] == "NONE" else dict(fa=float(p[1]), eff=float(p[2]), pro=float(p[3]), biz=float(p[4]), date=p[5])
def ssi_view(t):
    x = SSI.get(t)
    if not x or not x["fa"]:
        return None
    fa = x["fa"]; stale = x["date"] < "2026-09-01"
    icon = "⚠️" if stale else ("🟢" if fa >= 70 else "🟡" if fa >= 40 else "🔴")
    if stale:
        line = "Thành phần không dùng được (bản cũ)"
    else:
        f = lambda v: "–" if v <= 0 else vn(v)
        line = f"KQKD {f(x['biz'])} · HQ {f(x['eff'])} · TV {f(x['pro'])}"
    last = ("Bản cũ " + dmy(x["date"]) + ", SSI chưa chấm lại") if stale else ("SSI chấm " + dmy(x["date"]))
    return dict(head=f"{icon} {vn(fa)}/100", line=line, last=last)
PROXY = {}
for l in open(R26 + "proxy.txt"):
    k, a, b = l.split(); PROXY[k] = round((float(b) / float(a) - 1) * 100, 2)

FLOW = {}
for l in open(R26 + "flows.txt", encoding="utf-8"):
    if not l.strip(): continue
    t, sig, f, p, c = l.strip().split("|")
    f = [float(x) for x in f.split()]; p = [float(x) for x in p.split()]
    FLOW[t] = dict(signal=sig, nn=f, td=p, smart=[round(a + b, 2) for a, b in zip(f, p)], closes=[float(x) for x in c.split()])

for l in open(RUN + "raw2810/f27_121.txt", encoding="utf-8"):
    t, sig, f, p, _v = l.strip().split("|")
    f = [float(x) for x in f.split()]; p = [float(x) for x in p.split()]
    FLOW[t].update(signal=sig, nn=f, td=p, smart=[round(a + b, 2) for a, b in zip(f, p)])


# ======== NHỊP HẰNG NGÀY: giá, KL/RVOL, NN/TD lấy từ store/daily.json ========
ST = json.load(open(RUN + "store/daily.json"))
SD = ST["dates"]; ASOF = SD[-1]; NN_ASOF = ST["nnAsof"]; TD_ASOF = ST["tdAsof"]
WK = json.load(open(RUN + "conf/weekly.json"))          # mốc các nhóm cập nhật tuần / quý
FD10 = [d for d in SD if d <= NN_ASOF][-10:][::-1]
FLOW_DATES = FD10
dm = lambda iso: iso[8:10] + "/" + iso[5:7]
for t in FLOW:
    c = ST["close"][t]
    nn_ = [round(ST["nn"][t].get(d, 0.0), 2) for d in FD10]
    td_ = [round(ST["td"][t].get(d, 0.0), 2) for d in FD10]   # phiên TD chưa có số = 0
    FLOW[t].update(nn=nn_, td=td_, smart=[round(a + b, 2) for a, b in zip(nn_, td_)],
                   closes=[c[SD[-1]], c[SD[-2]], c[SD[-6]]])
    pf = ST["tv"]["perf"].get(t) or {}
    c0 = c[SD[-1]]
    PX[t] = (c0 / (1 + pf["m1"] / 100) if pf.get("m1") is not None else PX[t][0],
             c0 / (1 + pf["m3"] / 100) if pf.get("m3") is not None else PX[t][1])

TC = {}
for l in rd("tcbs"):
    t, *v = l.split()
    keys = ["stockRating", "valuation", "financialHealth", "businessModel", "businessOperation", "rsRating", "taScore"]
    TC[t] = {k: num(x) for k, x in zip(keys, v)}

FUND = {}
for l in rd("fund"):
    p = l.split()
    FUND[p[0]] = None if p[1] == "NONE" else dict(trend=p[1].replace("_", " "), add=int(p[2]), trim=int(p[3]),
                                                n=int(p[4]), pct=float(p[5]), asof=p[6])

CONS = {}
for l in rd("cons"):
    p = l.rstrip("\n").split("|")
    if p[1] == "NONE":
        CONS[p[0]] = None; continue
    d, rt, lt = p[3].split(":")
    CONS[p[0]] = dict(price=float(p[1]), targets=[float(x) for x in p[2].split(",")],
                      latest=(d, rt, None if lt == "-" else float(lt)), dist=p[4],
                      note=p[5] if len(p) > 5 else "")

INS = {}
for l in rd("insider"):
    p = l.rstrip("\n").split("|")
    t = p[0]
    if p[1].startswith("NONE"):
        _, d, kind = p[1].split(":")
        INS[t] = dict(deals=[], last=(d, kind), more=False)
        continue
    deals = []
    for item in p[1].split(";"):
        d, q, pr = item.split(":")
        deals.append((iso_from_dmy2(d), float(q), float(pr)))
    INS[t] = dict(deals=[x for x in deals if x[0] >= WIN], last=None, more=len(p) > 2 and p[2] == "MORE")

SCL = json.load(open(RAW + "scl.json")); SCL["tmpl"] = "VGC"
NEW = json.load(open(RAW + "new.json")); NEW["SCL"] = SCL

# ---------- views ----------
def fund_view(t):
    f = FUND[t]
    if not f:
        return dict(head="⚪ Không có quỹ", line="FinLens không có quỹ nào nắm", asof="")
    stale = f["asof"] < "2026-01-01"
    tr = f["trend"] or "ĐI NGANG"
    icon = "⚠️" if stale else ("🟢" if tr == "GOM" else "🔴" if tr == "XẢ" else "⚪")
    return dict(head=f"{icon} {tr}", line=f"{f['add']} tăng / {f['trim']} giảm · {f['n']} quỹ · {vn(f['pct'], 2)}% CP",
                asof=f"Kỳ {dmy(f['asof'])}" + (" · dữ liệu cũ" if stale else ""))

def insider_view(t):
    x = INS[t]
    if not x["deals"]:
        if x["last"]:
            return dict(head="⚪ Không có GD", line="12 tháng qua không có giao dịch",
                        last=f"Gần nhất {x['last'][0]} ({x['last'][1]})")
        return dict(head="⚪ Không có GD", line="12 tháng qua không có giao dịch", last="")
    deals = x["deals"]
    nb = sum(1 for d in deals if d[1] > 0); ns = sum(1 for d in deals if d[1] < 0)
    sh = sum(d[1] for d in deals); bil = sum(d[1] * d[2] for d in deals) / 1e9
    big = max(abs(d[1] * d[2]) for d in deals) / 1e9
    icon, lab = ("🟢", "Mua ròng") if bil > 10 else ("🔴", "Bán ròng") if bil < -10 else ("⚪", "Không đáng kể")
    last = f"{nb} mua / {ns} bán · gần nhất {dmy(max(d[0] for d in deals))}"
    if big > 500:
        last += " · ⚠️ có GD >500 tỷ, có thể là chuyển nhượng/phát hành, xem CBTT"
    if x["more"]:
        last += " · có thể còn GD chưa lấy hết"
    return dict(head=f"{icon} {lab}", line=f"{sgn(sh / 1e6, 2)} tr CP · ≈{sgn(bil, 0)} tỷ", last=last)

CONS1M = {}
for l in rd("cons1m"):
    t, items = l.strip().split("|")
    CONS1M[t] = [(d, rt, float(v)) for d, rt, v in (x.split(":") for x in items.split(";"))]

def cons_view(t):
    # Chỉ dùng báo cáo có giá mục tiêu trong 30 ngày (25/09–25/10/2026); không có thì bỏ trống
    deals = CONS1M.get(t)
    if not deals or not CONS.get(t):
        return None
    price = CONS[t]["price"]
    fixed = any(v < 1000 for _, _, v in deals)
    tg = sorted(v * 1000 if v < 1000 else v for _, _, v in deals)
    med = statistics.median(tg)
    up = (med / price - 1) * 100
    icon = "🟢" if up >= 20 else "🟡" if up >= 10 else "🔴"
    d, rt, lt = deals[0]; lt = lt * 1000 if lt < 1000 else lt
    lu = (lt / price - 1) * 100
    last = f"Mới nhất {dmy(d)[:5]}: {rt} {vn(lt)} ({sgn(lu, 1)}%)"
    if len(tg) == 1: last += " · chỉ 1 BC"
    if fixed: last += " · đã sửa lỗi đơn vị nguồn"
    if t == "GMD": last += " · bỏ 91.800 (07/10) có vẻ chưa quy đổi sau chia tách"
    rng = f" · {vn(tg[0])}–{vn(tg[-1])}" if len(tg) > 1 else ""
    return dict(head=f"{icon} {sgn(up, 1)}%", line=f"Trung vị {vn(med)} · {len(tg)} BC 30 ngày{rng}", last=last)

def cons_view_old(t):
    c = CONS[t]
    if not c:
        return dict(head="⚪ NO DATA", line="FinLens chưa có khuyến nghị CTCK", last="")
    fx = lambda v: v * 1000 if v is not None and v < 1000 else v
    fixed = any(v < 1000 for v in c["targets"]) or (c["latest"][2] is not None and c["latest"][2] < 1000)
    tg = sorted(fx(v) for v in c["targets"])
    med = statistics.median(tg)
    up = (med / c["price"] - 1) * 100
    icon = "🟢" if up >= 20 else "🟡" if up >= 10 else "🔴"
    d, rt, lt = c["latest"]; lt = fx(lt)
    rt = "không ghi" if rt in ("NULL", "") else rt
    if d < WIN:
        icon = "⚪"; last = f"BC mới nhất {dmy(d)}, cũ hơn 12 tháng"
    elif lt:
        lu = (lt / c["price"] - 1) * 100
        last = f"Mới nhất {dmy(d)[:5]}: {rt} {vn(lt)} ({sgn(lu, 1)}%)"
        if up - lu > 10:
            icon = "⚠️"; last += " · thấp hơn trung vị"
    else:
        last = f"Mới nhất {dmy(d)[:5]}: {rt}, không có giá"
    if fixed: last += " · đã sửa lỗi đơn vị nguồn"
    if c["note"]: last += " · " + c["note"]
    return dict(head=f"{icon} {sgn(up, 1)}%", line=f"Trung vị {vn(med)} · {len(tg)} BC · {vn(tg[0])}–{vn(tg[-1])}", last=last)

def tcbs_cmp(f, caps, tc):
    r = tc["stockRating"]; fh = tc["financialHealth"]
    hint = " TC mạnh." if fh is not None and fh >= 4.5 else " TC yếu." if fh is not None and fh <= 2 else ""
    if r is None:
        return dict(status="⚪", text="TCBS không có rating.")
    if f is None:
        return dict(status="⚪", text=f"Không có F, TCBS {vn(r, 1)}." + hint)
    if f == 0:
        if r >= 3: return dict(status="🟡", text=f"Lệch: F = 0 (cap) nhưng TCBS {vn(r, 1)}." + hint)
        if r < 2.5: return dict(status="🔴", text=f"Cùng yếu: F = 0, TCBS {vn(r, 1)}." + hint)
        return dict(status="🟡", text=f"F = 0 (cap), TCBS trung tính {vn(r, 1)}." + hint)
    fs = f / 20
    if abs(fs - r) < 0.5:
        st = "🟢" if fs >= 3 and r >= 3 else "🔴" if fs < 2.5 and r < 2.5 else "🟡"
        return dict(status=st, text=f"Khớp F (≈{vn(fs, 1)}/5)." + hint)
    hi = "F cao hơn" if fs > r else "TCBS cao hơn"
    return dict(status="🟡", text=f"Lệch: F ≈{vn(fs, 1)}/5 vs TCBS {vn(r, 1)}, {hi}." + hint)

# ---------- rows ----------
TICKERS = sorted(LISTS)
TECH_ONLY = set(json.load(open(RUN + "conf/tech_only.json"))) if os.path.exists(RUN + "conf/tech_only.json") else set() 
TECH_ONLY &= set(LISTS)
LABS = sorted({x for v in LISTS.values() for x in v} - {"Stage 2-2", "Stage 1-2 (Emerging)", "Stage 0-1 (W-D MA10)"})
ratings = {t: TC[t]["stockRating"] for t in TICKERS}
def tc_rank(t):
    r = ratings[t]
    return None if r is None else 1 + sum(1 for x in ratings.values() if x is not None and x > r)

def make_new(t):
    s = NEW[t]; _tm = s["tmpl"]
    while _tm not in BASE and _tm in NEW: _tm = NEW[_tm]["tmpl"]   # mã mẫu cũng là mã mới: lần về mã gốc
    tmpl = copy.deepcopy(BASE[_tm])  # mã mới: mượn dữ liệu ngành ICB4 của mã cùng ngành
    pct = lambda a, b: (a / b - 1) * 100
    tmpl.update({
        "t": t, "exchange": s["exchange"], "industry": s["industry"], "icb": s["icb"],
        "price": s["price"], "chg": pct(s["c0"], s["c1"]), "pe": None, "volume": s["volume"],
        "f": s["f"], "band": s["band"], "reliability": "High", "flags": s["flags"],
        "newsN": s["news"]["n"], "newsScore": s["news"]["score"], "newsSent": s["news"]["sent"],
        "title": s["news"]["title"], "summary": s["news"]["summary"], "newsDate": s["news"]["date"],
        "source": s["news"]["source"], "directStrength": s["news"]["direct"],
        "r1": pct(s["c0"], s["c1"]), "r5": pct(s["c0"], s["c5"]), "r21": pct(s["c0"], s["c21"]), "r63": pct(s["c0"], s["c63"]),
        "quality": {"f": s["f"], "caps": s.get("caps", []), "years": ["2025", "2024", "2023", "2022", "2021"], "reliability": "High"},
        "caps": s.get("caps", []), "score": 0, "alloc": 0,
    })
    sg = tmpl.get("sig") or {}
    sg.update({"exchange": s["exchange"], "close": s["c0"], "chg_1m_pct": round(pct(s["c0"], s["c21"]), 2)})
    tmpl["sig"] = sg
    tmpl.pop("excludedCatalyst", None)
    if s.get("icbpx"):  # ICB4 không có mã mẫu: tính lại hiệu suất ngành thật, bỏ icbStrength của mã mẫu
        i0, i1, i5, i21 = s["icbpx"]
        sd = lambda a, b: None if (a is None or b is None) else pct(a, b)
        sec = {"d1": sd(i0, i1), "w1": sd(i0, i5), "m1": sd(i0, i21)}
        bm = tmpl.get("icbBenchmark")
        if bm:
            bm["sector"] = sec
            bm["relative"] = {k: (None if sec[k] is None else sec[k] - bm["index"][k]) for k in ("d1", "w1", "m1")}
        tmpl["icbComparison"]["sector"] = {"d1": sec["d1"], "w1": sec["w1"]}
        tmpl["icbStrength"] = None
    if s.get("icbnone"):  # ICB4 không có mã mẫu cùng ngành và chưa kéo chỉ số ngành: không mượn số ngành
        tmpl["icbStrength"] = None
        if tmpl.get("icbBenchmark"):
            tmpl["icbBenchmark"]["sector"] = {"d1": None, "w1": None, "m1": None}
            tmpl["icbBenchmark"]["relative"] = {"d1": None, "w1": None, "m1": None}
    st = tmpl.get("icbComparison")
    if st:
        st["stock"] = {"d1": pct(s["c0"], s["c1"]), "w1": pct(s["c0"], s["c5"])}
        st["relative"] = {k: (None if st["sector"][k] is None else st["stock"][k] - st["sector"][k]) for k in ("d1", "w1")}
    return tmpl

VNI = ICBPX["VNINDEX"]
def refresh(r, t):
    pct = lambda a, b: None if (a is None or b is None) else (a / b - 1) * 100
    c0, c1, c5 = FLOW[t]["closes"]; c21, c63 = PX[t]
    old = r.get("price")
    r["price"] = round(c0 * 1000)
    if r.get("pe") and old: r["pe"] = r["pe"] * r["price"] / old
    r["r1"] = pct(c0, c1); r["chg"] = r["r1"]; r["r5"] = pct(c0, c5); r["r21"] = pct(c0, c21); r["r63"] = pct(c0, c63)
    if r.get("sig"):
        r["sig"]["close"] = c0; r["sig"]["chg_1m_pct"] = round(r["r21"], 2)
    if CONS.get(t): CONS[t]["price"] = r["price"]
    code = r["icb"]; ip = ICBPX.get(code); bad = ICBBAD.get(code, set())
    if ip:
        i0, i1, i5, i21 = ip
        sec = {"d1": pct(i0, i1), "w1": pct(i0, i5), "m1": pct(i0, i21)}
        for k in bad: sec[k] = None
    else:
        sec = {"d1": None, "w1": None, "m1": None}
    idx = {"d1": pct(VNI[0], VNI[1]), "w1": pct(VNI[0], VNI[2]), "m1": pct(VNI[0], VNI[3])}
    r["icbBenchmark"] = {"benchmark": "VNINDEX", "asof": "2026-10-26",
                         "baseDates": {"d1": "2026-10-23", "w1": "2026-10-19", "m1": "2026-09-25"},
                         "sector": sec, "index": idx,
                         "relative": {k: (None if sec[k] is None else sec[k] - idx[k]) for k in sec}}
    stock = {"d1": r["r1"], "w1": r["r5"]}
    same = ASOF == WK["icb"]
    r["icbComparison"] = {"asof": ASOF, "dayBase": SD[-2], "weekBase": SD[-6], "sectorAsof": WK["icb"],
                          "stock": stock, "sector": {"d1": sec["d1"], "w1": sec["w1"]},
                          "relative": {k: (None if (sec[k] is None or not same) else stock[k] - sec[k]) for k in ("d1", "w1")}}
    st = ICBSTR.get(code)
    if st:
        base = r.get("icbStrength") or {"icb_code": code, "name": r["industry"], "level": 4}
        base.update(st); r["icbStrength"] = base
    elif r.get("icbStrength"):
        r["icbStrength"]["asof"] = r["icbStrength"].get("asof", "2026-10-23")
    for key in ("sectorProxy", "commodityProxy", "proxy"):
        lst = r.get(key) or []
        r[key] = [[p[0], p[1], PROXY.get(p[0], p[2])] for p in lst]
    sp = dict((p[0].split(":")[1], p[2]) for p in r["sectorProxy"])
    if r.get("sector") in sp and isinstance(sp[r["sector"]], (int, float)):
        r["sectorChange"] = sp[r["sector"]]

rows = []
for t in TICKERS:
    r = make_new(t) if t in NEW else copy.deepcopy(BASE[t])
    r["lists"] = LISTS[t]
    fl = FLOW[t]
    r.update({"foreign": round(sum(fl["nn"]), 2), "prop": round(sum(fl["td"]), 2), "smart": round(sum(fl["smart"]), 2),
              "series": fl["smart"], "seriesNN": fl["nn"], "seriesTD": fl["td"], "signal": fl["signal"], "flowAsof": NN_ASOF, "tdAsof": TD_ASOF})
    rs = RS.get(t)
    if rs:
        r.update({"rs": rs["rs"], "breadth": rs["breadth"], "leader": rs["leader"], "mom": rs["mom"]})
    elif t in NEW:  # mã mới không có trong signals_screen: không mượn RS của mã mẫu
        r.update({"rs": None, "breadth": None, "leader": None, "mom": None})
    sig = r.get("sig") or {}
    sig.update({"ticker": t, "signal_date": "2026-10-27" if t != "C4G" else "2026-10-23", "rs_rating": r["rs"], "industry_rs": r["breadth"],
                "rs_vs_industry": r["leader"], "sector_rs": r["mom"]})
    if rs: sig["avg_value_bil"] = rs["avgval"]
    elif t == "EVG": sig["avg_value_bil"] = 2.86  # 28,63 tỷ / 10 phiên (FinLens flows)
    r["sig"] = sig if rs else None  # không có trong signals_screen thì không tính vào coverage
    refresh(r, t)
    r["tcbs"] = TC[t]; r["tcbsRank"] = tc_rank(t); r["tcbsCmp"] = tcbs_cmp(r["f"], r["caps"], TC[t])
    r["fundView"] = fund_view(t); r["insiderView"] = insider_view(t); r["consView"] = cons_view(t); r["ssiView"] = ssi_view(t)
    if t in TECH_ONLY:  # mã chỉ cập nhật kỹ thuật
        na = dict(head="⚪ Chưa kéo", line="Mã chỉ cập nhật kỹ thuật", last="")
        r["fundView"] = dict(na, asof=""); r["insiderView"] = na; r["consView"] = None; r["ssiView"] = None
        r["techOnly"] = True
    rows.append(r)

meta = copy.deepcopy(base["meta"]); meta["reportDate"] = ASOF; meta["revisionDate"] = datetime.date.today().isoformat(); meta["tdAsof"] = TD_ASOF; meta["weekly"] = WK; meta["flowDates"] = FLOW_DATES
data = {"rows": rows, "counts": {"rows": len(rows)}, "unique": len(rows),
        "overlap": sum(1 for v in LISTS.values() if len(v) > 1), "meta": meta}
for k in base:
    if k not in data: data[k] = base[k]
meta["icbPerformance"].update({"asof": "2026-10-26", "dayBase": "2026-10-23", "weekBase": "2026-10-19",
    "method": "1D = C26/C23 - 1; 1W = C26/C19 - 1; delta = stock return minus sector return in percentage points"})
meta["icbStrength"]["asof"] = "2026-10-27"
meta["icbBenchmark"].update({"asof": "2026-10-26", "baseDates": {"d1": "2026-10-23", "w1": "2026-10-19", "m1": "2026-09-25"},
    "indexCloses": [{"date": "2026-10-26", "close": VNI[0]}, {"date": "2026-10-23", "close": VNI[1]},
                    {"date": "2026-10-19", "close": VNI[2]}, {"date": "2026-09-25", "close": VNI[3]}]})

# ---- RVOL (FinLens stocks_get_price_history, 14/09–26/10/2026) ----
SDD = SD[::-1]
VOL = {t: [ST["vol"][t][d] for d in SDD[:32]] for t in TICKERS}
assert all(len(v) == 32 for v in VOL.values())
for r in rows:
    v = VOL[r["t"]]
    rv = []
    for d in range(10):
        base = sum(v[d+1:d+21]) / 20
        rv.append(round(v[d] / base, 3) if base > 0 else None)
    a5 = sum(rv[:5]) / 5; b5 = sum(rv[5:]) / 5; m10 = sum(rv) / 10
    sd = (sum((x - m10) ** 2 for x in rv) / 10) ** 0.5
    r["rvol"] = rv
    r["rvolStats"] = {"today": rv[0], "avg10": round(m10, 3), "avg5": round(a5, 3), "prev5": round(b5, 3),
                      "delta": round((a5 / b5 - 1) * 100, 1) if b5 else None, "sd": round(sd, 3),
                      "hi15": sum(1 for x in rv if x >= 1.5), "hi2": sum(1 for x in rv if x >= 2),
                      "vol": v[0], "sma20": round(sum(v[1:21]) / 20)}
    r["volume"] = int(v[0])
    r["rvolToday"] = rv[0]; r["rvolAvg10"] = round(m10, 3); r["rvolDelta"] = r["rvolStats"]["delta"]; r["rvolHi15"] = r["rvolStats"]["hi15"]

# ---- RS vs VN30 (FinLens price history, 21 phiên gần nhất tới @D0@/2026) ----
CLS = {t: [ST["close"][t][d] for d in SDD[:21]] for t in TICKERS + ["VN30"]}
V30 = CLS["VN30"]
for r in rows:
    c = CLS[r["t"]]
    rl = [c[i] / V30[i] for i in range(21)]           # RS line, mới nhất trước
    idx = [round((rl[d] / rl[10] - 1) * 100, 2) for d in range(10)]   # % vượt VN30 so với 13/10
    sret = [round((c[d] / c[d+1] - 1) * 100, 2) for d in range(10)]
    vret = [round((V30[d] / V30[d+1] - 1) * 100, 2) for d in range(10)]
    diff = [round(a - b, 2) for a, b in zip(sret, vret)]
    ma20 = sum(rl[:20]) / 20
    rshigh = rl[0] >= max(rl) - 1e-12
    phigh = c[0] >= max(c) - 1e-9
    wins = sum(1 for x in diff if x > 0)
    if rshigh and not phigh: tag = "RS đỉnh mới trước giá"
    elif rshigh: tag = "RS đỉnh mới 21 phiên"
    elif rl[0] < ma20 and idx[0] < -3: tag = "RS gãy"
    else: tag = ""
    r["rs30"] = {"idx": idx, "diff": diff, "sret": sret, "vret": vret, "today": diff[0], "r10": idx[0],
                 "aboveMa": rl[0] > ma20, "maGap": round((rl[0] / ma20 - 1) * 100, 2), "wins": wins, "tag": tag}
    r["rs30_10"] = idx[0]; r["rs30_1"] = diff[0]; r["rs30_wins"] = wins
    vv = VOL[r["t"]]
    r["val10"] = round(sum(vv[d] * c[d] for d in range(10)) / 1e6, 2)  # tỷ đồng, 14/10–27/10 (KL × giá đóng cửa)


# ---- Đồng thuận ngành (VN ICB4 + ETF Mỹ + hàng hóa) & thanh khoản / rổ chỉ số (28/10) ----
import statistics as _S
CONF = json.load(open(RUN + "conf/map.json"))["groups"]
QT = json.load(open(RUN + "conf/quotes2.json")); QQ = QT["q"]; SPY1M = QT["spy1m"]
EXM = json.load(open(RUN + "conf/syms.json"))["ex"]
fullsym = lambda k: k if ":" in k else EXM[k] + ":" + k
COMMS = {"HRC1!", "HE1!", "SB1!", "CT1!", "NG1!", "NCF1!", "HG1!", "BRN1!", "UFV1!", "TF1!"}
NAMES = {"HRC1!": "Thép HRC", "HE1!": "Heo hơi", "SB1!": "Đường", "CT1!": "Bông", "NG1!": "Khí", "NCF1!": "Than", "HG1!": "Đồng",
         "BRN1!": "Brent", "UFV1!": "Urê", "TF1!": "Cao su"}
OVR = {"GEE": ("GRID", None), "NAG": ("XLY", "HG1!"), "PVD": ("OIH", "BRN1!"), "GAS": ("XLE", "BRN1!"), "NT2": ("XLU", "NG1!"),
       "QTP": ("XLU", None), "HAH": ("BOAT", None), "VOS": ("BDRY", None), "VJC": ("JETS", "-BRN1!"), "ACV": ("JETS", None),
       "CVN": ("IHI", None), "MSR": ("REMX", None), "NBC": ("XME", "NCF1!"), "VPL": ("PEJ", None), "YEG": ("XLC", None),
       "PLC": ("XLE", "BRN1!")}
NO_ETF_SCORE = {"BĐS dân cư", "BĐS KCN"}
GMAP = {}
for g in CONF:
    for t in g["tickers"]:
        GMAP[t] = g
def qstate(k, role="etf"):
    inv = k.startswith("-"); fs = fullsym(k.lstrip("-")); short = fs.split(":")[-1]
    c, a, b, m, d1, desc = QQ[fs]; bench = 0 if (short in COMMS or role == "peer") else SPY1M
    up = c > a and c > b and m > bench; dn = c < a and c < b and m < bench
    st = ("g" if dn else "r" if up else "y") if inv else ("g" if up else "r" if dn else "y")
    return dict(sym=short, full=fs, name=NAMES.get(short, short), desc=desc, st=st, m1=m, d1=d1, inv=inv, role=role)
L2DATA = json.load(open(RUN + "fialda/l2rot.json")); L2ROT = {x["code"]: x for x in L2DATA["rows"]}
IDX = json.load(open(RUN + "conf/idx.json")); V30 = set(IDX["VN30"].split()); V100 = set(IDX["VN100"].split())
for r in rows:
    t = r["t"]; g = GMAP[t]
    etf, com = OVR.get(t, (g["etf"][0] if g["etf"] else None, g["comm"][0] if g["comm"] else None))
    # VN ICB4
    st4 = r.get("icbStrength") or {}; srs = st4.get("sector_rs"); rel = ((r.get("icbBenchmark") or {}).get("relative") or {})
    w1, m1 = rel.get("w1"), rel.get("m1")
    beat = w1 is not None and m1 is not None and w1 > 0 and m1 > 0
    lose = all(x is None or x < 0 for x in (w1, m1)) and not (w1 is None and m1 is None)
    if (srs is not None and srs >= 60) or beat: vst = "g"
    elif srs is not None and srs < 40 and (lose or (w1 is None and m1 is None and srs < 30)): vst = "r"
    else: vst = "y"
    vn = dict(st=vst, srs=srs, w1=w1, m1=m1)
    e = qstate(etf) if etf else None
    cm = qstate(com) if com else None
    groups = [vn["st"]] + ([e["st"]] if (e and g["name"] not in NO_ETF_SCORE) else []) + ([cm["st"]] if cm else [])
    # Rotation ngành cấp 2 (Fialda, 28/10 giữa phiên) — điểm −1/0/+1
    l2 = L2ROT.get(r["icb"][:2] + "00")
    if l2:
        ph, mo = l2["phase"], l2["mom"]
        if ph == "Dẫn dắt": l2pt = 0 if mo <= -25 else 1
        elif ph == "Cải thiện": l2pt = 1 if mo >= 25 else 0
        elif ph == "Suy yếu": l2pt = -1 if mo <= -25 else 0
        else: l2pt = 0 if mo >= 25 else -1
        flow = "tiền đang vào" if mo >= 25 else "tiền đang ra" if mo <= -25 else ""
        l2v = dict(code=l2["code"], name=l2["name"], phase=ph, mom=mo, strength=l2["strength"], short=l2["short"], pt=l2pt, flow=flow, w1=l2["w1"], m1=l2["m1"], m6=l2["m6"])
    else:
        l2pt = 0; l2v = None
    ptmap = {"g": 1, "y": 0, "r": -1}
    pts = [l2pt, ptmap[vst]] + ([ptmap[e["st"]]] if (e and g["name"] not in NO_ETF_SCORE) else []) + ([ptmap[cm["st"]]] if cm else [])
    S = sum(pts)
    if S >= 2 and l2pt >= 0: ng = 2
    elif S <= -1 or (l2pt == -1 and vst == "r"): ng = 0
    else: ng = 1
    r["conf5"] = dict(ng=ng, S=S, l2=l2v, vn=vn, etf=e, com=cm, group=g["name"], etfRef=g["name"] in NO_ETF_SCORE)
    seen = set(); refs = []
    def addref(k, role):
        fs = fullsym(k.lstrip("-"))
        if fs in seen: return
        seen.add(fs); x = qstate(k, role); x["main"] = (k == etf or k == com); refs.append(x)
    if etf: addref(etf, "etf")
    for k in g["etf"]: addref(k, "etf")
    if com: addref(com, "comm")
    for k in g["comm"]: addref(k, "comm")
    for k in g.get("peers", []): addref(k, "peer")
    r["globalRefs"] = refs
    # thanh khoản 20 phiên (KL × giá đóng cửa) + rổ chỉ số
    vv = VOL[t]; c = CLS[t]
    val = [vv[d] * c[d] / 1e6 for d in range(20)]
    mean = _S.mean(val); med = _S.median(val); cv = _S.pstdev(val) / mean if mean else 9
    idx = "VN30" if t in V30 else "VN100" if t in V100 else ""
    stable = cv <= 0.8
    if idx == "VN30" and med >= 50 and stable: tier = 1
    elif idx and med >= 20 and stable: tier = 2
    elif med >= 10: tier = 3
    else: tier = 4
    r["liq"] = dict(tier=tier, idx=idx, med=round(med, 1), mean=round(mean, 1), cv=round(cv, 2), stable=stable)
    r["liqTier"] = tier; r["liqScore"] = (5 - tier) * 10000 + round(med, 1)

sys.path.insert(0, RUN + "q3"); import earn as _earn
EARN, VNIW = _earn.load(RUN)
for r in rows:
    e = EARN.get(r["t"])
    if e: r["earn"] = e; r["earnScore"] = round(e["score"], 3)
    else: r["earnScore"] = -99

# ---- Lịch sự kiện: cổ tức / quyền (FinLens dividends_upcoming + tin) + hạn BCTC quý ----
import datetime as _dt
EVJ = json.load(open(RUN + "conf/events.json")) if os.path.exists(RUN + "conf/events.json") else {"items": [], "asof": ""}
BC = WK.get("bctc", {})
_d = lambda x: _dt.date.fromisoformat(x)
KIND = {"cash": ("evCash", "Cổ tức tiền"), "stock": ("evStock", "Cổ tức CP"), "rights": ("evRights", "Quyền mua (pha loãng)")}
EVTOP = []
for r in rows:
    ev = []
    for x in sorted((x for x in EVJ["items"] if x["t"] == r["t"]), key=lambda x: x["ex"] or "9"):
        c, lab = KIND.get(x["kind"], ("evCash", x["kind"]))
        x = dict(x, terms=(x.get("terms") or "").replace("thưởng CP ", ""))
        import re as _re
        _rd = _re.search(r"(đợt \d+/\d{4}|năm \d{4})", x.get("title") or "")
        txt = lab + (" " + _rd.group(1) if _rd else "") + " " + (x["terms"] or "") + (" (" + f"{x['yld']:.2f}".replace(".", ",") + "%)" if x.get("yld") else "")
        if not x["ex"]:
            when = "chưa rõ ngày GDKHQ"
        else:
            n = (_d(x["ex"]) - _d(ASOF)).days
            when = (f"GDKHQ hôm nay {dm(x['ex'])} — giá tham chiếu đã điều chỉnh" if n == 0 else f"GDKHQ {dm(x['ex'])} (còn {n} ngày)" if n > 0 else f"đã GDKHQ {dm(x['ex'])}")
        pay = (" · trả " + dmy(x["pay"])) if x.get("pay") else ""
        ev.append({"c": c, "t": "📅 " + when + ": " + txt + pay, "src": x.get("src", ""), "title": x.get("title", "")})
        if x["ex"] and 0 <= (_d(x["ex"]) - _d(ASOF)).days <= 30 or not x["ex"]:
            EVTOP.append({"t": r["t"], "ex": x["ex"], "s": (dm(x["ex"]) if x["ex"] else "chưa rõ ngày") + " " + lab + " " + (x["terms"] or "")})
    E = r.get("earn")
    if BC:
        if E and E.get("q3"):
            ev.append({"c": "evBctc", "t": "✅ BCTC " + BC["q"] + ": đã có số (TCBS)", "src": "", "title": ""})
        else:
            nr = (_d(BC["rieng"]) - _d(ASOF)).days; nh = (_d(BC["hopnhat"]) - _d(ASOF)).days
            ev.append({"c": "evBctc", "t": "⏳ BCTC " + BC["q"] + ": hạn " + dm(BC["rieng"]) + (f" (còn {nr} ngày)" if nr >= 0 else " (đã quá)") + " riêng lẻ · " + dm(BC["hopnhat"]) + (f" (còn {nh} ngày)" if nh >= 0 else " (đã quá)") + " hợp nhất", "src": "", "title": ""})
    r["events"] = ev
_m = {}
for x in EVTOP:
    k = (x["t"], x["s"])
    if k in _m: _m[k]["n"] += 1
    else: _m[k] = dict(x, n=1)
EVTOP = [dict(x, s=x["s"] + (f" ×{x['n']} đợt" if x["n"] > 1 else "")) for x in _m.values()]
EVTOP.sort(key=lambda x: x["ex"] or "9")
data["eventsMeta"] = {"asof": EVJ.get("asof"), "top": EVTOP, "next": BC.get("next", "")}

data["earnMeta"] = dict(asof="2026-10-28", vniW=VNIW, n=len(rows), out=sum(1 for r in rows if r.get("earn", {}).get("q3")))
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
lines[111] = PRE + blob + "</script>"
html = "\n".join(lines)


dmy4 = lambda iso: iso[8:10] + "/" + iso[5:7] + "/" + iso[:4]
NOTES = ("Nhịp cập nhật: HẰNG NGÀY (sau 18h30) kéo giá, khối lượng/RVOL, RS vs VN30, khối ngoại, tự doanh và quote ETF/hàng hóa theo lô — TradingView 3 lệnh cho cả danh sách (50 mã/lệnh), FinLens flows_top_net 12 lệnh (NN, TD × mua/bán × 3 sàn, top 30 mỗi chiều; mã ngoài top coi như ≈ 0), FinLens price history chỉ cho các mã RVOL ≥ 1,4× để lấy KL khớp lệnh (KL TradingView gồm cả thỏa thuận). "
         "HÀNG TUẦN (thứ Sáu): F/cờ đỏ BCTC, TCBS rating, SSI FA, quỹ, nội bộ, giá mục tiêu CTCK, catalyst/tin, RS rating FinLens, sức mạnh và hiệu suất ngành ICB4, rotation ngành cấp 2 Fialda — bản hiện tại chốt " + dmy4(WK["fund"]) + " (ngành ICB4 " + dmy4(WK["icb"]) + ", Fialda " + dmy4(WK["fialda"]) + "). "
         "THEO QUÝ: KQKD quý chỉ kéo trong mùa BCTC (tháng 1, 4, 7, 10 và nửa đầu tháng kế tiếp), mỗi lần chỉ các mã chưa có số quý mới; bản hiện tại " + WK["earn"] + ". "
         "Phiên " + dmy4(ASOF) + ": khối ngoại chốt " + dmy4(NN_ASOF) + ", tự doanh chốt " + dmy4(TD_ASOF) + (" (FinLens chưa có số tự doanh phiên mới nhất, tạm tính 0)" if TD_ASOF < NN_ASOF else "") + ". "
         + ("Giá đã điều chỉnh theo sự kiện quyền: " + ", ".join(f"{k} ×{v}" for k, v in ST.get("adj", {}).items()) + ". " if ST.get("adj") else "")
         + "So sánh mã với ngành ICB4 (1D/1W) để trống khi số ngành khác mốc với giá. 1M/3M lấy Perf TradingView (theo tháng lịch).")

def rep(old, new, count=1):
    global html
    n = html.count(old)
    assert n == count, f"expected {count} got {n}: {old[:80]}"
    html = html.replace(old, new)

rep("<title>VN W-D-H4 — 3 danh mục 23/10/2026</title>", "<title>VN W-D-H4 — "+str(len(rows))+" mã @D0Y@</title>")
rep("<b>Snapshot 23/10/2026 · sửa bố cục và phương pháp 24/10/2026</b>", "<b>Giá, KL/RVOL, RS vs VN30, khối ngoại chốt phiên @D0Y@ · tự doanh tới phiên @TD@ · nhóm tuần chốt @WK@ · BCTC quý: @Q@</b>")
rep("Giá/hiệu suất và signals: 23/10. NN/TD: 09/10–22/10 giữ từ bản gốc. F: FinLens annual 5 năm, đã kiểm tra lại và khớp bản 23/10; kỳ cụ thể trong tooltip. Sector/ETF dùng snapshot TradingView đã lưu, chưa đồng bộ giờ đóng cửa giữa các thị trường.",
    NOTES)
rep("3. Bảng phân tích 85 mã", "3. Bảng phân tích "+str(len(rows))+" mã")
rep(" Tin Duyên Hà gán cho DHC đã loại khỏi catalyst.", " Tin Duyên Hà gán cho DHC đã loại khỏi catalyst. SCL: tin Vietstock 18/10 về KQKD quý 3. EVG, DDV, GEL, CTS, SHI: FinLens không có tin 30 ngày, catalyst lấy fallback TCBS (CBTT sàn), điểm tin để trung tính.")
rep('rows.filter(r=>["IDC","ACV","NT2","TCB","HAH","AAS"].includes(r.t))', "rows.filter(r=>r.alloc)")
rep("Báo cáo nghiên cứu 23/10/2026 · chỉnh sửa 24/10/2026 · giữ đủ 85 mã của ba Stage list.",
    "Báo cáo dữ liệu phiên @D0Y@ · "+str(len(rows))+" mã: 3 Stage list + VN RVOL + RVOL TEST vni + RVOL 25/10 + mã anh thêm.")
rep("09/10 → 22/10 · 10 phiên", "@F9@ → @NN@ · 10 phiên")
rep("Nhóm F tốt nhưng catalyst hoặc dòng tiền chưa xác nhận tiếp tục ở Watchlist.",
    "'+rows.filter(r=>r.f===0).length+' mã có F = 0 do FinLens áp cap; điểm cơ bản đã lấy trung bình với TCBS để không loại mã quá sớm, nhưng các mã này vẫn cần đọc BCTC trước khi giải ngân.")

RS_DEF = r'''
const rs30Cell=r=>{const s=r.rs30;if(!s)return '<td class="rs30"></td>';
const pts=s.idx.slice().reverse(),W=168,H=50,lo=Math.min(0,...pts),hi=Math.max(0,...pts),span=Math.max(hi-lo,2),x=i=>(i*(W-8)/9+4),y=v=>H-4-((v-lo)/span)*(H-8);
const up=s.r10>=0,cls=up?"rsUp":"rsDn";
const path=pts.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' ');
const area=path+' L'+x(9).toFixed(1)+' '+y(0).toFixed(1)+' L'+x(0).toFixed(1)+' '+y(0).toFixed(1)+' Z';
const dots=pts.map((v,i)=>{const k=9-i,d=(DATA.meta.flowDates[k]||"").split("-").reverse().slice(0,2).join("/");const t=r.t+' · '+d+' · RS cộng dồn '+(v>0?'+':'')+num(v,2)+'% so VN30 · phiên: mã '+(s.sret[k]>0?'+':'')+num(s.sret[k],2)+'% / VN30 '+(s.vret[k]>0?'+':'')+num(s.vret[k],2)+'%';return '<circle class="'+(s.diff[k]>0?'rsW':'rsL')+'" cx="'+x(i).toFixed(1)+'" cy="'+y(v).toFixed(1)+'" r="'+(i===9?3.2:2.2)+'"><title>'+esc(t)+'</title></circle>';}).join("");
const svg='<svg class="rssvg" viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="'+esc('RS so VN30 10 phiên '+r.t)+'"><line class="rs0" x1="0" x2="'+W+'" y1="'+y(0).toFixed(1)+'" y2="'+y(0).toFixed(1)+'"/><path class="'+cls+'A" d="'+area+'"/><path class="'+cls+'" d="'+path+'"/>'+dots+'</svg>';
const sg=v=>(v>0?'+':v<0?'−':'')+num(Math.abs(v),2)+'%';
return '<td class="rs30" title="'+esc('RS so VN30 = giá đóng cửa mã / VN30 (FinLens). Đường = % vượt/thua VN30 cộng dồn từ @RS0@; chấm xanh = phiên mã mạnh hơn VN30, chấm đỏ = yếu hơn. MA20 tính trên đường RS 20 phiên.')+'">'+svg+'<div class="flowline"><span class="'+(up?"up":"down")+'">'+sg(s.r10)+'</span> <span class="note">10 phiên</span></div><div class="note">@D0@: <span class="'+(s.today>0?"up":s.today<0?"down":"flat")+'">'+sg(s.today)+'</span> · thắng '+s.wins+'/10 phiên</div><div class="note">RS '+(s.aboveMa?'trên':'dưới')+' MA20 ('+sg(s.maGap)+')</div>'+(s.tag?'<div class="rvtag '+(s.tag==="RS gãy"?"rsTagBad":"rsTagGood")+'">'+esc(s.tag)+'</div>':'')+'</td>';};
'''
RV_DEF = r'''
const rvolCell=r=>{const a=r.rvol,s=r.rvolStats;if(!a)return '<td class="rvol"></td>';
const W=168,H=50,bw=12,gap=4.8,mx=Math.max(2.5,...a),y=v=>H-2-(Math.min(v,mx)/mx)*(H-6);
const bars=a.map((v,i)=>({v,i})).reverse().map(({v,i},j)=>{const d=DATA.meta.flowDates[i]||"";const cls=v>=2?"rv3":v>=1.5?"rv2":v>=1?"rv1":"rv0";const t=r.t+' · '+d.split("-").reverse().slice(0,2).join("/")+' · RVOL '+num(v,2)+'×';return '<rect class="'+cls+'" x="'+(j*(bw+gap)+1).toFixed(1)+'" y="'+y(v).toFixed(1)+'" width="'+bw+'" height="'+(H-2-y(v)).toFixed(1)+'" rx="1"><title>'+esc(t)+'</title></rect>';}).join("");
const ln=(v,c)=>'<line class="'+c+'" x1="0" x2="'+W+'" y1="'+y(v).toFixed(1)+'" y2="'+y(v).toFixed(1)+'"/>';
const svg='<svg class="rvsvg" viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img" aria-label="'+esc('RVOL 10 phiên '+r.t)+'">'+ln(1,"ref1")+ln(1.5,"ref15")+bars+'</svg>';
const tc=s.today>=2?"rv3t":s.today>=1.5?"rv2t":s.today>=1?"rv1t":"muted";
const dl=s.delta==null?"–":(s.delta>0?"+":"")+num(s.delta,0)+'%';
let tag="";if(s.today>=2)tag="Bùng nổ phiên cuối";else if(s.hi15>=3&&s.delta>15)tag="Thanh khoản tăng dần";else if(s.delta>=30)tag="Đang tăng";else if(s.avg10<.7)tag="Cạn thanh khoản";else if(s.delta<=-30)tag="Hạ nhiệt";
return '<td class="rvol" title="'+esc('RVOL = KL phiên / TB KL 20 phiên trước đó (FinLens khớp lệnh; TradingView nếu chưa kiểm). KL @D0@: '+Math.round(s.vol).toLocaleString("vi-VN")+' · SMA20: '+Math.round(s.sma20).toLocaleString("vi-VN"))+'">'+svg+'<div class="flowline"><span class="'+tc+'">'+num(s.today,2)+'×</span> <span class="note">@D0@</span></div><div class="note">TB10 '+num(s.avg10,2)+'× · Δ5 phiên <span class="'+(s.delta>0?"up":s.delta<0?"down":"flat")+'">'+dl+'</span></div><div class="note">σ '+num(s.sd,2)+' · '+s.hi15+' phiên ≥1,5×'+(s.hi2?' ('+s.hi2+' ≥2×)':'')+'</div>'+(tag?'<div class="rvtag">'+esc(tag)+'</div>':'')+'</td>';};
'''
TCBS_DEF = r'''const tcbsCell=r=>{const t=r.tcbs,c=r.tcbsCmp;if(!t||t.stockRating==null)return '<div class="note">TCBS: NO DATA</div>';const cls=t.stockRating>=3?"good":t.stockRating>=2?"mid":"bad";return '<span class="fscore '+cls+'" tabindex="0" title="'+esc('TCBS General Rating 23/10/2026, thang 1–5. Hạng '+r.tcbsRank+'/'+rows.length)+'">'+num(t.stockRating,1)+'</span><div class="note">Hạng '+r.tcbsRank+'/'+rows.length+'</div><div class="note">ĐG '+num(t.valuation,1)+' · TC '+num(t.financialHealth,1)+' · MH '+num(t.businessModel,1)+' · VH '+num(t.businessOperation,1)+' · RS '+num(t.rsRating,1)+' · TA '+num(t.taScore,1)+'</div><div class="cmp-note"><b>'+esc(c.status)+'</b> '+esc(c.text)+'</div>';};
'''
EXTRA_DEF = r'''const xcell=(v,title)=>!v?'<td class="center xcol"></td>':'<td class="center xcol" title="'+esc(title)+'"><div class="xhead">'+esc(v.head)+'</div><div class="note">'+esc(v.line)+'</div>'+(v.last||v.asof?'<div class="note">'+esc(v.last||v.asof)+'</div>':'')+'</td>';
const extraCells=r=>xcell(r.ssiView,'SSI Research điểm cơ bản (FA) thang 100: KQKD = kết quả kinh doanh, HQ = hiệu quả, TV = triển vọng ngành; – = SSI để trống (vd ngân hàng không có KQKD). Trống ô = SSI không chấm mã này. Chỉ tham khảo, không vào điểm xếp hạng')+xcell(r.fundView,'FinLens fund_stock_ownership: GOM/XẢ theo số quỹ tăng/giảm tỷ trọng so với kỳ trước')+xcell(r.insiderView,'TCBS getInsiderDealing: giao dịch người nội bộ và cổ đông lớn 12 tháng (từ 25/10/2025)')+xcell(r.consView,'FinLens research_get_analyst_consensus: upside theo giá mục tiêu trung vị so với giá 26/10/2026');
'''
rep("const tr=(r,i)=>{", TCBS_DEF + EXTRA_DEF + RV_DEF + RS_DEF + "const tr=(r,i)=>{")
rep('<td class="center">\'+fbadge(r)+\'</td><td class="center">\'+badge(r.rs)+\'</td>',
    '<td class="center">\'+fbadge(r)+\'</td><td class="center">\'+tcbsCell(r)+\'</td>\'+extraCells(r)+\'<td class="center">\'+badge(r.rs)+\'</td>')
rep("<th>F · FinLens</th><th>RS mã</th>", "<th>F · FinLens</th><th>TCBS · xếp hạng &amp; so sánh</th><th>SSI FA</th><th>Quỹ gom / xả</th><th>Nội bộ &amp; CĐ lớn 12T</th><th>Giá mục tiêu CTCK</th><th>RS mã</th>")
rep("Proxy thiếu quote được ghi NO QUOTE.",
    "Proxy thiếu quote được ghi NO QUOTE. TCBS: General Rating 23/10 (stockRating, định giá, tài chính, mô hình kinh doanh, vận hành, rsRating, taScore; thang 1–5). TCBS stockRating ×20 được lấy trung bình với F để ra điểm cơ bản dùng cho xếp hạng và allocation; F FinLens quy về thang 1–5 để đối chiếu, lệch dưới 0.5 là khớp. Quỹ: FinLens fund_stock_ownership, GOM/XẢ theo số quỹ tăng/giảm tỷ trọng; kỳ trước 2026 bị đánh dấu dữ liệu cũ. Nội bộ: TCBS getInsiderDealing 12 tháng, dấu theo khối lượng (+ mua, − bán), bỏ dòng khối lượng 0; ròng trên ±10 tỷ mới tính là mua/bán ròng; GD đơn lẻ trên 500 tỷ được gắn ⚠️. Giá mục tiêu: FinLens research_get_analyst_consensus, chỉ dùng báo cáo có giá mục tiêu trong 30 ngày (25/09–25/10/2026); không có báo cáo nào trong 30 ngày thì để trống; upside = trung vị so với giá 26/10; giá nhỏ hơn 1.000 được coi là lỗi đơn vị và nhân 1.000. SSI FA: SSI Research research_list_fa_rating, bản chấm 26/10/2026, thang 100 (KQKD, hiệu quả, triển vọng ngành); ô trống = SSI không chấm; bản cũ 19/04 được gắn ⚠️. Bốn cột Quỹ, Nội bộ, Giá mục tiêu, SSI FA chỉ để tham khảo, không đổi điểm xếp hạng hay allocation. Smart money = NN + TD; không cộng nhóm tổ chức trong nước của FinLens vì trùng số với TD.")
rep("Catalyst mạnh vẫn cần dòng tiền và điều kiện kỹ thuật xác nhận trong bảng.",
    "Catalyst mạnh vẫn cần dòng tiền xác nhận trong bảng. Cột TCBS đối chiếu với F FinLens: mã nào lệch hoặc mâu thuẫn cần đọc BCTC trước khi tin catalyst.")

rep("r.rankScore =", "const tcN=r.tcbs&&r.tcbs.stockRating!=null?r.tcbs.stockRating*20:null; r.fCombo=r.f!=null&&tcN!=null?(r.f+tcN)/2:(r.f??tcN??0); r.rankScore =")
rep("""(r.caps.length?'<div class="note">Có cap</div>':"");""", """(r.caps.length?'<div class="note">Có cap</div>':"")+'<div class="note" title="Trung bình F FinLens và TCBS ×20">Điểm chấm '+num(r.fCombo,1)+'</div>';""")
rep(".35*(r.f??0)+.15*(r.catScore??0)+.25*(r.flowScore??0)+.15*(r.techScore??0)+.10*(r.confluence??0)",
    ".40*r.fCombo+.20*(r.catScore??0)+.30*(r.flowScore??0)+.10*(r.confluence??0)")
rep(".30*(r.f??0)+.20*(r.catScore??0)+.20*(r.flowScore??0)+.15*(r.techScore??0)+.15*r.confluenceScore",
    ".35*r.fCombo+.25*(r.catScore??0)+.25*(r.flowScore??0)+.15*r.confluenceScore")
rep("35% F + 15% catalyst + 25% dòng tiền + 15% kỹ thuật + 10% sector", "40% điểm cơ bản (TB F và TCBS×20) + 20% catalyst + 30% dòng tiền + 10% sector")
rep("Điểm xác nhận = 35% F + 15% catalyst + 25% dòng tiền + 15% kỹ thuật FinLens + 10% sector.",
    "Điểm xác nhận = 40% điểm cơ bản + 20% catalyst + 30% dòng tiền + 10% sector. Điểm cơ bản = trung bình F FinLens (0–100) và TCBS stockRating ×20 (thang 1–5 quy về 0–100); thiếu một nguồn thì dùng nguồn còn lại. Tiêu chí kỹ thuật (RS mã, Leader, Momentum) đã bỏ khỏi chấm điểm từ 25/10/2026; các cột RS vẫn hiển thị để tham khảo.")
rep("30% F, 20% catalyst, 20% dòng tiền, 15% kỹ thuật và 15% confluence", "35% điểm cơ bản (TB F và TCBS×20), 25% catalyst, 25% dòng tiền và 15% confluence")
rep("</style>", ".cmp-note{margin-top:4px;font-size:12px;line-height:1.35}\n.xcol{min-width:150px;max-width:190px}\n.xhead{font-weight:700;margin-bottom:3px}\n</style>")

rep('coverage+"/85"', 'coverage+"/"+rows.length')
rep('["Quote snapshot","85/85"]', '["Quote snapshot",rows.length+"/"+rows.length]')
rep('["F / NN-TD","85/85"]', '["F / NN-TD",rows.length+"/"+rows.length]')
rep("Báo cáo 3 danh mục · 23/10/2026</h1>", "Báo cáo 4 watchlist · @D0Y@</h1>")
rep("Stage 0-1 (W-D MA10) — 85 mã unique, 19 mã giao nhau.", "Stage 0-1 (W-D MA10) · " + " · ".join(LABS) + " — "+str(len(rows))+" mã unique, "+str(data["overlap"])+" mã nằm ở từ 2 list trở lên." + (" " + str(len(TECH_ONLY)) + " mã chỉ cập nhật kỹ thuật (" + ", ".join(sorted(TECH_ONLY)) + "): F, TCBS, SSI, quỹ, nội bộ, CTCK, tin để trống." if TECH_ONLY else ""))
rep("nếu có trong ba Stage list.", "nếu có trong 4 watchlist.")
rep("(85-coverage)", "(rows.length-coverage)")
rep('85/85 mã</span>', str(len(rows))+"/"+str(len(rows))+' mã</span>')
rep("cho cả 85 mã", "cho cả "+str(len(rows))+" mã")
rep('selected.length+"/85 mã"', 'selected.length+"/"+rows.length+" mã"')
rep("<option>Stage 0-1 (W-D MA10)</option></select>", "<option>Stage 0-1 (W-D MA10)</option>" + "".join("<option>" + x + "</option>" for x in LABS) + "</select>")
rep("FinLens · chốt 23/10/2026<br>1D so 22/10 · 1W so 16/10", "FinLens · chốt 26/10/2026<br>1D so 23/10 · 1W so 19/10")
rep("Chốt 23/10 · so 22/10, 16/10, 24/09/2026", "Chốt 26/10 · so 23/10, 19/10, 25/09/2026")
rep("cùng ngày: 23/10 so 22/10 và 16/10;", "cùng ngày: 26/10 so 23/10 và 19/10;")
rep("cùng ngày 23/10/2026, so với 22/10 (Daily), 16/10 (W, 5 phiên), 24/09 (M, 21 phiên)", "cùng ngày 26/10/2026, so với 23/10 (Daily), 19/10 (W, 5 phiên), 25/09 (M, 21 phiên)")

rep("""money(r,"prop","seriesTD","TD")+'""", """money(r,"prop","seriesTD","TD")+rvolCell(r)+rs30Cell(r)+'""")
rep('<th class="money">Dòng tiền TD 10 phiên</th>', '<th class="money">Dòng tiền TD 10 phiên</th><th class="rvol rvsort" id="rvolHead" tabindex="0" title="Bấm để sắp xếp theo RVOL: phiên cuối → TB10 → Δ5 phiên → về mặc định">Relative RVOL 10 phiên <span id="rvolArrow">⇅</span></th><th class="rs30 rvsort" id="rsHead" tabindex="0" title="Bấm để sắp xếp: RS 10 phiên → RS phiên @D0@ → số phiên thắng VN30 → về mặc định">RS vs VN30 10 phiên <span id="rsArrow">⇅</span></th>')
rep('<option value="prop">TD mua ròng</option></select>', '<option value="prop">TD mua ròng</option><option value="smart">Smart money (NN + TD)</option><option value="rvolToday">RVOL phiên @D0@ cao → thấp</option><option value="rvolAvg10">RVOL TB10 cao → thấp</option><option value="rvolDelta">RVOL Δ5 phiên tăng mạnh nhất</option><option value="rvolHi15">Số phiên RVOL ≥1,5×</option><option value="rs30_10">RS vs VN30 10 phiên mạnh nhất</option><option value="rs30_1">RS vs VN30 phiên @D0@</option><option value="rs30_wins">Số phiên thắng VN30</option></select>')
rep('document.querySelector("#sort").addEventListener("change",render);', 'document.querySelector("#sort").addEventListener("change",()=>{rvArrow();render();});\n  const RVS=["rvolToday","rvolAvg10","rvolDelta"],RVL={rvolToday:"↓ phiên cuối",rvolAvg10:"↓ TB10",rvolDelta:"↓ Δ5"};\n  function rvArrow(){const v=document.querySelector("#sort").value,a=document.querySelector("#rvolArrow"),b=document.querySelector("#rsArrow");if(a)a.textContent=RVL[v]||(v==="rvolHi15"?"↓ số phiên ≥1,5×":"⇅");if(b)b.textContent=RSL[v]||"⇅";}\n  const RSS=["rs30_10","rs30_1","rs30_wins"],RSL={rs30_10:"↓ 10 phiên",rs30_1:"↓ @D0@",rs30_wins:"↓ số phiên thắng"};\n  function rsCycle(){const s=document.querySelector("#sort"),i=RSS.indexOf(s.value);s.value=i<0?RSS[0]:(i===RSS.length-1?"rankScore":RSS[i+1]);rvArrow();render();}\n  const rsh=document.querySelector("#rsHead");if(rsh){rsh.addEventListener("click",rsCycle);rsh.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();rsCycle();}});}\n  function rvCycle(){const s=document.querySelector("#sort"),i=RVS.indexOf(s.value);s.value=i<0?RVS[0]:(i===RVS.length-1?"rankScore":RVS[i+1]);rvArrow();render();}\n  const rvh=document.querySelector("#rvolHead");if(rvh){rvh.addEventListener("click",rvCycle);rvh.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();rvCycle();}});}')
rep("</style>", ".rvol{min-width:190px}.rs30{min-width:190px}.rssvg{display:block;overflow:visible}.rssvg circle{cursor:help}.rs0{stroke:#bbb;stroke-dasharray:3 3;stroke-width:1}.rsUp{fill:none;stroke:var(--green);stroke-width:1.8}.rsDn{fill:none;stroke:var(--red);stroke-width:1.8}.rsUpA{fill:var(--green);opacity:.12}.rsDnA{fill:var(--red);opacity:.12}.rsW{fill:var(--green)}.rsL{fill:var(--red)}#rsArrow{color:var(--yellow);font-weight:400;margin-left:4px}.rsTagGood{background:#1d3a2a;color:#9fe3b9}.rsTagBad{background:#3a1d24;color:#f0a5b5}.rvsort{cursor:pointer;user-select:none}.rvsort:hover,.rvsort:focus{color:#fff;background:#303030}#rvolArrow{color:var(--yellow);font-weight:400;margin-left:4px}.rvsvg{display:block;overflow:visible}.rvsvg rect{cursor:help}.rv0{fill:#5a5a5a}.rv1{fill:var(--blue)}.rv2{fill:var(--yellow)}.rv3{fill:var(--green)}.ref1{stroke:#bbb;stroke-dasharray:3 3;stroke-width:1}.ref15{stroke:var(--yellow);stroke-dasharray:1 3;stroke-width:1;opacity:.7}.rv1t{color:var(--blue)}.rv2t{color:var(--yellow)}.rv3t{color:var(--green)}.rvtag{display:inline-block;margin-top:4px;font-size:11px;padding:1px 6px;border-radius:3px;background:#2a2a2a;color:#ddd}\n</style>")
rep("Smart money = NN + TD; không cộng nhóm tổ chức trong nước của FinLens vì trùng số với TD.",
    "Smart money = NN + TD; không cộng nhóm tổ chức trong nước của FinLens vì trùng số với TD. Relative RVOL: khối lượng khớp từng phiên (FinLens stocks_get_price_history) chia trung bình khối lượng 20 phiên liền trước, không tính phiên đó; 10 cột từ @F9@ (trái) đến @D0@ (phải); vạch đứt trắng = 1×, vạch chấm vàng = 1,5×; cột xám dưới 1×, xanh 1–1,5×, vàng 1,5–2×, xanh lá từ 2×. Số đi kèm: RVOL phiên cuối, TB10 = trung bình 10 phiên, Δ5 phiên = TB RVOL 5 phiên gần nhất so với 5 phiên trước đó, σ = độ lệch chuẩn RVOL 10 phiên (càng cao càng giật cục), số phiên từ 1,5×. Nhãn: Bùng nổ phiên cuối (≥2×), Thanh khoản tăng dần (≥3 phiên từ 1,5× và Δ5 trên +15%), Đang tăng (Δ5 từ +30%), Hạ nhiệt (Δ5 từ −30%), Cạn thanh khoản (TB10 dưới 0,7×). RVOL chỉ tham khảo, không vào điểm xếp hạng hay allocation. RS vs VN30: đường RS = giá đóng cửa mã chia VN30 (FinLens stocks_get_price_history, 21 phiên gần nhất tới @D0@); mini chart là % vượt/thua VN30 cộng dồn từ @RS0@ đến @D0@, chấm xanh = phiên mã tăng hơn VN30, chấm đỏ = kém hơn. Số đi kèm: RS 10 phiên, chênh lệch phiên cuối, số phiên thắng VN30, vị trí đường RS so với MA20 của chính nó. Nhãn: RS đỉnh mới trước giá (đường RS lập đỉnh 21 phiên khi giá chưa lập đỉnh), RS đỉnh mới 21 phiên, RS gãy (dưới MA20 và thua VN30 quá 3% trong 10 phiên). Giá cùng mốc với các cột giá/hiệu suất. RS vs VN30 chỉ tham khảo, chưa vào điểm xếp hạng/allocation nhưng là trụ gác cổng của Hạng setup TA. Hạng setup TA (@D0Y@): 4 trụ, mỗi trụ 0–2 điểm. RS (gác cổng): 2 = đường RS trên MA20, thắng VN30 10 phiên, 3M ≤ 15%, RS rating ≥ 80 hoặc RS lập đỉnh 21 phiên; 0 = 3M > 20% hoặc RS dưới MA20 và thua VN30. Dòng tiền: 2 = NN và TD cùng mua ròng 10 phiên, phiên cuối không bán mạnh; 1 = tổng dương hoặc chưa có tổ chức; 0 = tổng bán ròng. RVOL: 2 = cạn (TB10 < 0,8×) rồi nổ ≥ 1,5× hoặc tăng dần (≥ 3 phiên ≥ 1,5×, Δ5 > +15%, chưa chạy xa, dòng tiền dương); 0 = nổ ≥ 2× khi smart money bán hoặc giá đã chạy xa. Catalyst + Cơ bản: 2 = điểm cơ bản ≥ 65 không cap và catalyst tích cực mạnh trong 30 ngày; 1 = chỉ một trong hai (hoặc cơ bản 50–65 + catalyst mạnh); 0 = còn lại hoặc tin tiêu cực. Hạng: A+ = 8/8, A ≥ 6 và RS = 2, B 4–5 và RS ≥ 1, C còn lại. Nền giá và nến H4 anh tự xác nhận trên chart.")

SETUP_JS = r'''if(!window.__rotSort){window.__rotSort=1;const go=th=>{const t=th.closest("table"),b=t.tBodies[0],c=+th.dataset.c,txt=c===0,cur=th.dataset.s||"",st=txt?(cur===""?"a":cur==="a"?"d":""):(cur===""?"d":cur==="d"?"a":"");t.querySelectorAll("th.rsrt").forEach(h=>{h.dataset.s="";h.querySelector(".sar").textContent="⇅";});th.dataset.s=st;th.querySelector(".sar").textContent=st==="d"?"↓":st==="a"?"↑":"⇅";const R=[...b.rows];R.sort((x,y)=>{if(!st)return x.dataset.i-y.dataset.i;const a=x.cells[c].dataset.v,z=y.cells[c].dataset.v;if(a===""&&z!=="")return 1;if(z===""&&a!=="")return -1;const na=parseFloat(a),nz=parseFloat(z);const r=(isNaN(na)||isNaN(nz))?String(a).localeCompare(String(z),"vi"):na-nz;return st==="d"?-r:r;});R.forEach(r=>b.appendChild(r));};document.addEventListener("click",e=>{const th=e.target.closest&&e.target.closest("th.rsrt");if(th)go(th);});document.addEventListener("keydown",e=>{const th=e.target.closest&&e.target.closest("th.rsrt");if(th&&(e.key==="Enter"||e.key===" ")){e.preventDefault();go(th);}});}
const pct=x=>x==null?"–":x>=9?"gấp "+num(x+1,0)+" lần":(x>=0?"+":"−")+num(Math.abs(x*100),0)+"%";
const bn=x=>x==null?"–":num(x,0);
const evHtml=r=>(r.events&&r.events.length)?'<div class="evbox"><div class="evh">Lịch sự kiện</div>'+r.events.map(e=>'<div class="ev '+e.c+'"'+(e.title||e.src?' title="'+esc((e.title||'')+(e.src?' · nguồn '+e.src:''))+'"':'')+'>'+esc(e.t)+'</div>').join('')+'</div>':'';
const earnCell=r=>{const E=r.earn;if(!E)return '<td class="earn"><div class="note">TCBS: không có số quý</div>'+evHtml(r)+'</td>';
 const st=E.q3?'<span class="etag eOut">Đã ra Q3/26</span>':'<span class="etag eWait">⏳ Chưa ra Q3 · số '+E.q+'</span>';
 const s=E.series||[],mx=Math.max(1,...s.map(x=>Math.abs(x||0))),W=120,H=34,bw=W/s.length-4;
 const bars=s.map((x,i)=>{const h=Math.max(1,Math.abs(x||0)/mx*(H/2-2)),y=(x||0)>=0?H/2-h:H/2;return '<rect x="'+(i*(bw+4))+'" y="'+y+'" width="'+bw+'" height="'+h+'" class="'+((x||0)<0?'eNeg':i===s.length-1?'eLast':'eBar')+'"><title>'+E.sq[i]+': LNST '+bn(x)+' tỷ</title></rect>';}).join("");
 const rv=E.bank?"TN hoạt động":"DT";
 return '<td class="earn">'+st+'<div class="elab">'+esc(E.lab)+(E.q3&&E.adj?' <b class="'+(E.adj>0?'up':'down')+'">CB '+(E.adj>0?'+1':'−1')+'</b>':'')+'</div>'+
 '<svg class="esvg" width="'+W+'" height="'+H+'"><line x1="0" x2="'+W+'" y1="'+H/2+'" y2="'+H/2+'" class="rs0"/>'+bars+'</svg>'+
 '<div class="note">LNST '+E.q+': <b>'+bn(E.np)+' tỷ</b> · YoY <b class="'+((E.yoy||0)>=0?'up':'down')+'">'+pct(E.yoy)+'</b> · QoQ '+pct(E.qoq)+'</div>'+
 '<div class="note">'+rv+': '+bn(E.rev)+' tỷ · YoY '+pct(E.ryoy)+' · QoQ '+pct(E.rqoq)+'</div>'+
 '<div class="note">TTM 4 quý: '+bn(E.ttm)+' tỷ · YoY '+pct(E.tyoy)+'</div>'+
 '<div class="note">Tăng tốc: '+(E.accel?'<b class="up">có</b>':'không')+' ('+E.qp+' '+pct(E.prev)+' → '+E.q+' '+pct(E.yoy)+')</div>'+
 (E.react?'<div class="note">'+esc(E.react.lbl)+' · 1W '+(E.react.w>0?'+':'')+num(E.react.w,1)+'% (VNINDEX +'+num(DATA.earnMeta.vniW,1)+'%) · 28/10 '+num(E.react.d1,1)+'%</div>':'')+evHtml(r)+'</td>';};
const earnSummary=()=>{const R=rows.filter(r=>r.earn),out=R.filter(r=>r.earn.q3),wait=R.length-out.length;
 const up=out.filter(r=>r.earn.adj===1).sort((a,b)=>b.earnScore-a.earnScore),dn=out.filter(r=>r.earn.adj===-1).sort((a,b)=>(a.earn.yoy??-9)-(b.earn.yoy??-9)),sell=out.filter(r=>r.earn.react&&r.earn.react.k==="sell"),strongNoAcc=out.filter(r=>r.earn.ep===0&&(r.earn.yoy||0)>=0.25);
 const L=(a,f)=>a.length?a.map(f).join(" · "):'<span class="note">chưa có mã</span>';
 const wq=R.filter(r=>!r.earn.q3&&r.earn.ep===1).sort((a,b)=>b.earnScore-a.earnScore);
 return '<div class="allocation setupbox"><b>Mùa BCTC quý 3/2026</b> <span class="note">(TCBS, chốt 28/10: '+out.length+'/'+R.length+' mã đã có số Q3, '+wait+' mã chưa ra. Hạn nộp BCTC quý: 30 ngày sau quý (30/10), công ty mẹ có công ty con được 45 ngày (14/11). CB +1 khi LNST Q3 YoY ≥ 25% và tăng tốc so với YoY quý 2; CB −1 khi LNST giảm ≥ 25% YoY hoặc lỗ. Chỉ áp cho mã đã ra Q3. Phản ứng giá = hiệu suất 1 tuần so với VNINDEX và phiên 28/10, chỉ để tham khảo.)</span>'+
 '<div style="margin:4px 0">🟢 <b>CB +1</b>: '+L(up,r=>'<b>'+r.t+'</b> <span class="note">'+pct(r.earn.yoy)+'</span>')+'</div>'+
 '<div style="margin:4px 0">🟡 <b>Tăng mạnh nhưng chậm lại</b>: '+L(strongNoAcc,r=>'<b>'+r.t+'</b> <span class="note">'+pct(r.earn.prev)+' → '+pct(r.earn.yoy)+'</span>')+'</div>'+
 '<div style="margin:4px 0">⚠️ <b>Bán theo tin</b>: '+L(sell,r=>'<b>'+r.t+'</b> <span class="note">LNST '+pct(r.earn.yoy)+', 1W '+(r.earn.react.w>0?'+':'')+num(r.earn.react.w,1)+'%</span>')+'</div>'+
 '<div style="margin:4px 0">🔴 <b>CB −1</b>: '+L(dn,r=>'<b>'+r.t+'</b> <span class="note">'+(r.earn.np<0?'lỗ':pct(r.earn.yoy))+'</span>')+'</div>'+
 '<div class="note" style="margin:4px 0">⏳ Chưa ra Q3 nhưng Q2 tăng mạnh + tăng tốc (theo dõi khi công bố): '+L(wq,r=>'<b>'+r.t+'</b>')+'</div>'+(()=>{const M=DATA.eventsMeta||{},T=M.top||[];return '<div style="margin:4px 0">📅 <b>Cổ tức / quyền 30 ngày tới</b> <span class="note">(FinLens dividends + tin, chốt '+(M.asof||'').split('-').reverse().slice(0,2).join('/')+'; mua TRƯỚC ngày GDKHQ mới được hưởng, ngày GDKHQ giá tham chiếu điều chỉnh giảm)</span>: '+(T.length?T.map(x=>'<b>'+x.t+'</b> <span class="note">'+esc(x.s)+'</span>').join(' · '):'<span class="note">không có</span>')+'</div><div class="note">'+esc(M.next||'')+'</div>';})()+'</div>';};
function setupGrade(r){
  const s=r.rs30||{},v=r.rvolStats||{},r63=r.r63??0,nn=r.foreign??0,td=r.prop??0,sum=nn+td,last=((r.seriesNN||[])[0]||0)+((r.seriesTD||[])[0]||0),miss=[];
  let RS;
  if(r63>20){RS=0;miss.push("RS: đã chạy "+num(r63,1)+"% trong 3 tháng (>20%)");}
  else if(!s.aboveMa&&s.r10<0){RS=0;miss.push("RS: dưới MA20 và thua VN30 "+num(s.r10,1)+"%");}
  else if(s.aboveMa&&s.r10>0&&r63<=15&&((r.rs??0)>=80||/đỉnh mới/.test(s.tag||""))){RS=2;}
  else{RS=1;const m=[];if(!s.aboveMa)m.push("RS dưới MA20");if(!(s.r10>0))m.push("thua VN30 10 phiên");if(r63>15)m.push("3M +"+num(r63,1)+"% (>15%)");if(!((r.rs??0)>=80||/đỉnh mới/.test(s.tag||"")))m.push("RS rating "+(r.rs??"–")+" <80, RS chưa lập đỉnh");miss.push("RS: "+m.join(", "));}
  let FL;
  const val=r.val10||0,netPct=val>0?sum/val*100:0,pos=Math.max(nn,td),neg=Math.min(nn,td),okLast=last>-0.1*Math.abs(sum);
  const bothBuy=nn>0.5&&td>0.5&&okLast,strongNet=sum>0.5&&netPct>=0.3&&neg>=-0.25*pos&&okLast;
  r.flowNetPct=Math.round(netPct*100)/100;
  if(bothBuy||strongNet)FL=2;
  else if(sum>0.5||Math.abs(sum)<=0.5){FL=1;miss.push("Dòng tiền: "+(Math.abs(sum)<=0.5?"chưa có tổ chức tham gia":(nn<=0.5?"NN chưa mua ròng":"TD chưa mua ròng"))+(nn>0.5&&td>0.5?" (phiên @NN@ bán mạnh)":"")+(sum>0.5?" · ròng "+num(netPct,2)+"% GTGD 10 phiên":""));}
  else{FL=0;miss.push("Dòng tiền: NN+TD bán ròng "+num(sum,1)+" tỷ");}
  const rvA=r.rvol||[],baseA=rvA.slice(3,10).filter(x=>x!=null),baseAvg=baseA.length?baseA.reduce((a,b)=>a+b,0)/baseA.length:9;
  let pk=0;for(let d=1;d<3;d++)if((rvA[d]||0)>(rvA[pk]||0))pk=d;
  const pop=rvA[pk]||0,popDay=["@D0@","@D1@","@D2@"][pk],popSmart=((r.seriesNN||[])[pk]||0)+((r.seriesTD||[])[pk]||0);
  const dryPop=baseAvg<0.8&&pop>=1.5,build=v.hi15>=3&&v.delta>15&&r63<=15&&sum>0;
  r.rvPop={pk,pop,day:popDay,base:Math.round(baseAvg*100)/100};
  let RV;
  if(pop>=2&&(popSmart<0||r63>20)){RV=0;miss.push("RVOL: nổ "+num(pop,2)+"× phiên "+popDay+" nhưng "+(popSmart<0?"smart money bán phiên đó":"giá đã chạy xa"));}
  else if(dryPop||build)RV=2;
  else{RV=1;miss.push("RVOL: chưa có cạn rồi nổ trong 3 phiên (đỉnh "+num(pop,2)+"× phiên "+popDay+", nền 7 phiên trước "+num(baseAvg,2)+"×)");}
  const fc=r.fCombo??0,good=fc>=65&&!(r.caps&&r.caps.length),mid=fc>=50,fresh=!!r.newsDate&&r.newsDate>="2026-09-27",bad=!!r.title&&r.newsSent==="negative",strong=!bad&&fresh&&(r.catScore??0)>=70;
  let CF;
  if(bad){CF=0;miss.push("Catalyst xấu: "+(r.title||""));}
  else if(good&&strong)CF=2;
  else if(good||(mid&&strong)){CF=1;miss.push(good?"Catalyst: chưa có tin mạnh trong 30 ngày":"Cơ bản: điểm "+num(fc,1)+" (<65)"+((r.caps&&r.caps.length)?" / F có cap":""));}
  else{CF=0;miss.push("Cơ bản: điểm "+num(fc,1)+(strong?"":", catalyst yếu"));}
  const E=r.earn;if(E&&E.q3){if(E.adj===1&&CF<2){CF++;miss.push("CB +1 nhờ KQKD "+E.q+": LNST "+pct(E.yoy)+" YoY, tăng tốc từ "+pct(E.prev)+" quý trước");}else if(E.adj===-1&&CF>0){CF--;miss.push("CB −1 vì KQKD "+E.q+": "+E.lab.replace(/^\S+ /,"")+(E.yoy!=null?" ("+pct(E.yoy)+" YoY)":""));}else if(E.adj===-1)miss.push("KQKD "+E.q+": "+E.lab.replace(/^\S+ /,""));if(E.react&&E.react.k==="sell")miss.push("⚠️ KQKD tốt nhưng giá bị bán theo tin (1W "+num(E.react.w,1)+"% vs VNINDEX, phiên 28/10 "+num(E.react.d1,1)+"%)");}
  const cf5=r.conf5||{},NG=cf5.ng??1,core=RS+FL+RV+CF,tot=core+NG,ta3=RS===2&&RV===2&&FL===2,grade=(ta3&&CF===2&&NG>=1)?"A+":ta3?"A":(core>=4&&RS>=1)?"B":"C",gr={"A+":4,A:3,B:2,C:1}[grade];
  if(NG===0)miss.push("Ngành: rotation cấp 2 / ICB4 / ETF / hàng hóa đang ngược chiều"+(ta3&&CF===2?" (chặn A+)":""));else if(NG===1)miss.push("Ngành: đồng thuận chưa đủ (tổng "+(cf5.S>=0?"+":"")+cf5.S+", cần ≥ +2 và ngành cấp 2 không ngược)");
  const L=r.liq||{tier:4},liqB={1:200,2:200,3:100,4:0}[L.tier]||0;
  const near=grade==="B"&&[RS,RV,FL].filter(x=>x===2).length===2?["RS","RVOL","Dòng tiền"][[RS,RV,FL].indexOf([RS,RV,FL].find(x=>x!==2))]:null;
  r.setup={RS,FL,RV,CF,NG,tot,grade,miss,near,star:NG===2};r.setupScore=gr*1000+liqB+tot*10+(s.r10||0)/10;
}
rows.forEach(setupGrade);
const _st={g:"🟢",y:"🟡",r:"🔴"};
const _ph={"Dẫn dắt":"🟢","Cải thiện":"🔵","Suy yếu":"🟠","Tụt hậu":"🔴"};
const confLine=r=>{const c=r.conf5;if(!c)return '';const v=c.vn,a=[];if(c.l2)a.push(_ph[c.l2.phase]+' Ngành C2 '+c.l2.phase+(c.l2.flow?' · '+c.l2.flow:''));a.push(_st[v.st]+' VN'+(v.srs!=null?' RS '+num(v.srs,0):''));if(c.etf)a.push(_st[c.etf.st]+' '+c.etf.sym+' '+(c.etf.m1>=0?'+':'')+num(c.etf.m1,1)+'%'+(c.etfRef?' (tham khảo)':''));if(c.com)a.push(_st[c.com.st]+' '+c.com.name+' '+(c.com.m1>=0?'+':'')+num(c.com.m1,1)+'%'+(c.com.inv?' (chi phí)':''));return '<div class="note">Ngành: '+a.join(' · ')+'</div>';};
const liqLine=r=>{const l=r.liq;if(!l)return '';const ic={1:"🟢",2:"🟢",3:"🟡",4:"⚠️"}[l.tier];return '<div class="note">'+ic+' '+(l.idx||'Ngoài VN100')+' · GTGD TB20 '+num(l.med,1)+' tỷ'+(l.stable?'':' · biến động mạnh')+'</div>';};
const globalRefs=r=>{const a=r.globalRefs||[];if(!a.length)return '';const ic={g:"🟢",y:"🟡",r:"🔴"},lab={etf:"ETF Mỹ",comm:"hàng hóa",peer:"cùng ngành quốc tế"};
return '<div style="margin-top:4px"><b>Quốc tế cùng ngành (TradingView):</b></div>'+a.map(x=>'<div>'+ic[x.st]+' <a href="https://www.tradingview.com/chart/?symbol='+encodeURIComponent(x.full)+'" target="_blank" rel="noopener"><code>'+esc(x.full)+'</code></a> '+esc(x.desc)+' <span class="'+tone(x.d1)+'">'+sign(x.d1,2)+'%</span> <span class="note">· 1M '+sign(x.m1,1)+'% · '+lab[x.role]+(x.inv?' (chi phí, giảm là tốt)':'')+(x.main?' · tính điểm NG':'')+'</span></div>').join('')+(r.conf5&&r.conf5.etfRef?'<div class="note">BĐS: ETF Mỹ chỉ tham khảo, không tính điểm</div>':'');};
const setupCell=r=>{const g=r.setup;if(!g)return '<td class="setup"></td>';const p=(k,v)=>'<span class="sp sp'+v+'" title="'+k+'">'+k+' '+v+'</span>';
return '<td class="setup"><div class="sgrade sg'+g.grade.replace("+","p")+'">'+g.grade+'</div><div class="note">'+g.tot+'/10 điểm'+(g.star?' ⭐':'')+(g.near?' · <b class="up">gần A, thiếu '+g.near+'</b>':'')+'</div><div class="spills">'+p("RS",g.RS)+p("DT",g.FL)+p("RV",g.RV)+p("CB",g.CF)+p("NG",g.NG)+'</div>'+confLine(r)+liqLine(r)+(g.miss.length?'<ul class="smiss">'+g.miss.map(m=>'<li>'+esc(m)+'</li>').join("")+'</ul>':'<div class="note up">Đủ 4 trụ</div>')+'<div class="note">⏳ Xác nhận nền + nến H4 trên chart</div></td>';};
const setupSummary=()=>{const by=g=>rows.filter(r=>r.setup&&r.setup.grade===g).sort((a,b)=>b.setupScore-a.setupScore);const line=(g,list)=>'<div style="margin:4px 0"><span class="sgrade sg'+g.replace("+","p")+'">'+g+'</span>'+(list.length?list.map(r=>'<b>'+r.t+'</b> <span class="note">'+r.setup.tot+'/10'+(r.setup.star?' ⭐':'')+'</span>'+(r.liq&&r.liq.idx?' <span class="note">'+r.liq.idx+'</span>':'')).join(' · '):'<span class="note">chưa có mã</span>')+'</div>';return '<div class="allocation setupbox"><b>Setup TA phiên @D0@</b> <span class="note">(4 trụ: RS vs VN30 + RS rating + 3M · dòng tiền NN+TD (2 điểm khi cả hai mua, hoặc ròng ≥ 0,3% GTGD 10 phiên mà bên còn lại chỉ âm nhẹ) · RVOL (nổ ≥ 1,5× trong 3 phiên gần nhất sau nền cạn) · Catalyst + Cơ bản; A+ = RS + RVOL + NN/TD + Catalyst/Cơ bản đều 2/2 và ngành không ngược chiều (NG ≥ 1) · A = RS + RVOL + NN/TD đều 2/2 · B ≥ 4/8 (4 trụ chính) và RS ≥ 1 · ⭐ = đồng thuận ngành 2/2 (VN ICB4 + ETF Mỹ + hàng hóa) · trong cùng hạng ưu tiên VN30 → VN100 thanh khoản ổn định → ngoài rổ; nền + nến H4 anh tự xác nhận)</span>'+line("A+",by("A+"))+line("A",by("A"))+line("B",by("B"))+(()=>{const nr=by("B").filter(r=>r.setup.near);return '<div class="note" style="margin:4px 0">Gần A (thiếu đúng 1 trụ TA): '+(nr.length?nr.map(r=>'<b>'+r.t+'</b> thiếu '+r.setup.near).join(' · '):'chưa có mã')+'</div>';})()+'<div class="note">'+by("C").length+' mã hạng C (không đạt).</div></div>';};
'''
rep("const allocated=rows.reduce(", SETUP_JS + "  const allocated=rows.reduce(")
rep('<th class="sticky-ticker">Mã / Sector</th>', '<th class="sticky-ticker">Mã / Sector</th><th class="setup">Hạng setup TA</th>')
rep("""'</td><td class="fund">'+cat(r)""", """'</td>'+setupCell(r)+'<td class="fund">'+cat(r)""")
rep('<select id="sort"><option value="rankScore">Ưu tiên tổng hợp</option>', '<select id="sort"><option value="rankScore">Ưu tiên tổng hợp</option><option value="setupScore">Hạng setup TA (A+ → C, ưu tiên VN30/VN100)</option><option value="liqScore">Thanh khoản / rổ chỉ số (VN30 → VN100 → ngoài rổ)</option>')
rep("""1. Tóm tắt điều hành</h2><div class="summary">'+cards.map(c=>'<div class="card"><span class="note">'+c[0]+'</span><b>'+c[1]+'</b></div>').join("")+'</div>'+""",
    """1. Tóm tắt điều hành</h2><div class="summary">'+cards.map(c=>'<div class="card"><span class="note">'+c[0]+'</span><b>'+c[1]+'</b></div>').join("")+'</div>'+setupSummary()+""")
rep("</style>", ".setup{min-width:210px;max-width:250px}.sgrade{display:inline-block;font-size:20px;font-weight:800;padding:2px 10px;border-radius:5px;margin-bottom:3px}.sgAp{background:#1f6e45;color:#fff}.sgA{background:#2f8f5c;color:#fff}.sgB{background:#7a5c14;color:#fff}.sgC{background:#3a3a3a;color:#bbb}.spills{display:flex;gap:4px;flex-wrap:wrap;margin:4px 0}.sp{font-size:11px;padding:1px 5px;border-radius:3px}.sp2{background:#1d3a2a;color:#9fe3b9}.sp1{background:#3a321d;color:#ead08a}.sp0{background:#3a1d24;color:#f0a5b5}.smiss{margin:4px 0 0 14px;padding:0;font-size:11px;color:#c9c9c9;line-height:1.35}.setupbox .sgrade{font-size:13px;padding:1px 7px;margin-right:6px}\\n</style>")

ROT_HTML = '<div class="allocation setupbox" style="margin:10px 0"><b>Rotation ngành cấp 2 (Fialda, chốt phiên 28/10)</b> <span class="note">Độ mạnh = thứ hạng 1M 40% + 6M 40% + 1Y 20% · Ngắn hạn = thứ hạng 1W 70% + 3D 30% · Động lượng = ngắn hạn − thứ hạng 1M (≥ +25 tiền đang vào, ≤ −25 tiền đang ra) · Ô màu Độ mạnh / Ngắn hạn: đỏ = yếu nhất nhóm → xanh = mạnh nhất nhóm · Bấm tiêu đề cột để sắp xếp (bấm lần nữa đảo chiều, lần ba về mặc định)</span><div style="overflow-x:auto"><table class="rotT" style="min-width:640px"><thead><tr><th class="rsrt" data-c="0" tabindex="0">Ngành C2 <span class="sar">⇅</span></th><th class="rsrt" data-c="1" tabindex="0">Pha <span class="sar">⇅</span></th><th class="rsrt" data-c="2" tabindex="0">Độ mạnh <span class="sar">⇅</span></th><th class="rsrt" data-c="3" tabindex="0">Ngắn hạn <span class="sar">⇅</span></th><th class="rsrt" data-c="4" tabindex="0">Động lượng <span class="sar">⇅</span></th><th class="rsrt" data-c="5" tabindex="0">1D <span class="sar">⇅</span></th><th class="rsrt" data-c="6" tabindex="0">3D <span class="sar">⇅</span></th><th class="rsrt" data-c="7" tabindex="0">1W <span class="sar">⇅</span></th><th class="rsrt" data-c="8" tabindex="0">1M <span class="sar">⇅</span></th><th class="rsrt" data-c="9" tabindex="0">6M <span class="sar">⇅</span></th><th class="rsrt" data-c="10" tabindex="0">Điểm NG <span class="sar">⇅</span></th><th>Mã trong báo cáo</th></tr></thead><tbody>'
_vnf = lambda x, d=0: f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
_icon = {"Dẫn dắt": "🟢", "Cải thiện": "🔵", "Suy yếu": "🟠", "Tụt hậu": "🔴"}
for x in L2DATA["rows"]:
    mo = x["mom"]
    if x["phase"] == "Dẫn dắt": pt = 0 if mo <= -25 else 1
    elif x["phase"] == "Cải thiện": pt = 1 if mo >= 25 else 0
    elif x["phase"] == "Suy yếu": pt = -1 if mo <= -25 else 0
    else: pt = 0 if mo >= 25 else -1
    tks = sorted(r2["t"] for r2 in rows if r2["icb"][:2] + "00" == x["code"])
    fl = " · tiền vào" if mo >= 25 else " · tiền ra" if mo <= -25 else ""
    sg = lambda v: ("+" if v > 0 else "−" if v < 0 else "") + _vnf(abs(v), 2) + "%"
    _pc = {"Dẫn dắt": "phL", "Cải thiện": "phI", "Suy yếu": "phW", "Tụt hậu": "phG"}[x["phase"]]
    _ht = lambda v: "ht%d" % min(4, int(v // 20))
    _pv = lambda v: ("rpos" if v > 0 else "rneg" if v < 0 else "rz") + (" rb" if abs(v) >= 3 else "")
    _mc = "mIn" if mo >= 25 else "mOut" if mo <= -25 else "mMid"
    _nc = {1: "ngP", 0: "ngZ", -1: "ngN"}[pt]
    _fl = '<span class="flw fIn">tiền vào</span>' if mo >= 25 else '<span class="flw fOut">tiền ra</span>' if mo <= -25 else ""
    mo = 0 if abs(mo) < 0.5 else mo
    _d3 = '<td data-v="" class="rz">–</td>' if x["d3"] is None else f'<td data-v="{x["d3"]}" class="{_pv(x["d3"])}">{sg(x["d3"])}</td>'
    _ms = ("+" if mo > 0 else "") + (_vnf(mo) if mo >= 0 else "−" + _vnf(-mo))
    _ri = {"Dẫn dắt": 4, "Cải thiện": 3, "Suy yếu": 2, "Tụt hậu": 1}[x["phase"]]
    _i = globals().get("_rotI", 0); globals()["_rotI"] = _i + 1
    ROT_HTML += (f'<tr class="rr {_pc}r" data-i="{_i}"><td data-v="{x["name"]}"><b>{x["name"]}</b> <span class="note">{x["code"]}</span></td>'
                 f'<td data-v="{_ri * 1000 + x["strength"] + x["short"]}"><span class="ph {_pc}">{x["phase"]}</span>{_fl}</td>'
                 f'<td data-v="{x["strength"]}" class="hc {_ht(x["strength"])}">{_vnf(x["strength"])}</td><td data-v="{x["short"]}" class="hc {_ht(x["short"])}">{_vnf(x["short"])}</td>'
                 f'<td data-v="{mo}"><span class="mo {_mc}">{_ms}</span></td>'
                 f'<td data-v="{x["d1"]}" class="{_pv(x["d1"])}">{sg(x["d1"])}</td>{_d3}<td data-v="{x["w1"]}" class="{_pv(x["w1"])}">{sg(x["w1"])}</td><td data-v="{x["m1"]}" class="{_pv(x["m1"])}">{sg(x["m1"])}</td><td data-v="{x["m6"]}" class="{_pv(x["m6"])}">{sg(x["m6"])}</td>'
                 f'<td data-v="{pt}"><span class="ngp {_nc}">{"+" if pt > 0 else ""}{pt}</span></td><td class="tks">{", ".join(tks) or "–"}</td></tr>')
ROT_HTML += '</tbody></table></div><div class="note">NG (trụ 5) = tổng điểm: rotation cấp 2 (−1/0/+1) + ngành ICB4 FinLens (🟢+1/🟡0/🔴−1) + ETF Mỹ + hàng hóa. NG 2 khi tổng ≥ +2 và ngành cấp 2 không ngược; NG 0 khi tổng ≤ −1 hoặc cả cấp 2 lẫn ICB4 cùng xấu; còn lại NG 1. Dữ liệu Fialda chốt phiên 28/10 (đã đối chiếu lại sau giờ đóng cửa); 1D = 0,00% là ngành đứng yên thật trong phiên. Các cột khác của báo cáo chốt 26–27/10.</div></div>'
rep("2. Market / sector / ETF confluence</h2>", "2. Market / sector / ETF confluence</h2>" + ROT_HTML.replace("\\", "\\\\"))
rep("""TradingView sector / ETF:</b></div>'+refs(r.sectorProxy,"sector/ETF")+'</td>'""", """TradingView sector / ETF:</b></div>'+refs((r.sectorProxy||[]).filter(p=>/^(HOSE|HNX|UPCOM):/.test(p[0])),"sector VN")+globalRefs(r)+'</td>'""")
rep("</style>", ".rotT td{vertical-align:middle}.rr td:first-child{border-left:4px solid transparent}.phLr td:first-child{border-left-color:#2fb36b}.phIr td:first-child{border-left-color:#4a8fe0}.phWr td:first-child{border-left-color:#e8923a}.phGr td:first-child{border-left-color:#e0475b}.ph{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:700}.phL{background:#1d4a32;color:#8ff0b5}.phI{background:#1d3352;color:#9cc6ff}.phW{background:#4d3216;color:#ffc27a}.phG{background:#4d1d26;color:#ff9aa8}.flw{display:inline-block;margin-left:5px;font-size:11px;padding:1px 6px;border-radius:3px}.fIn{background:#14402a;color:#7ee2a6}.fOut{background:#45181f;color:#ff8f9e}.hc{text-align:center;font-weight:700;color:#fff}.ht0{background:#5c2029}.ht1{background:#4a2e22}.ht2{background:#3a3626}.ht3{background:#24452f}.ht4{background:#1d5a37}.rpos{color:#5fd48f}.rneg{color:#ff7a8a}.rz{color:#aaa}.rb{font-weight:700}.mo{display:inline-block;min-width:38px;text-align:center;padding:1px 6px;border-radius:3px;font-weight:700}.mIn{background:#1d5a37;color:#c9ffdd}.mOut{background:#5c2029;color:#ffd0d6}.mMid{color:#bbb}.ngp{display:inline-block;min-width:26px;text-align:center;padding:1px 6px;border-radius:3px;font-weight:800}.ngP{background:#2f8f5c;color:#fff}.ngZ{background:#6b5a1f;color:#fff}.ngN{background:#a8364a;color:#fff}.tks{font-size:12px;color:#ddd}.rsrt{cursor:pointer;user-select:none;white-space:nowrap}.rsrt:hover,.rsrt:focus{color:#fff;background:#303030}.rsrt[data-s=d] .sar,.rsrt[data-s=a] .sar{color:var(--yellow)}.sar{color:#777;font-weight:400}\n</style>")
rep('<th class="setup">Hạng setup TA</th>', '<th class="setup">Hạng setup TA</th><th class="earn">KQKD quý</th>')
rep("+setupCell(r)+", "+setupCell(r)+earnCell(r)+")
rep('<option value="liqScore">', '<option value="earnScore">KQKD quý (đã ra Q3, tăng mạnh + tăng tốc trước)</option><option value="liqScore">')
rep("+setupSummary()+", "+setupSummary()+earnSummary()+")
rep("</style>", ".evbox{margin-top:6px;padding-top:5px;border-top:1px dashed #444}.evh{font-size:11px;color:#aaa;margin-bottom:2px}.ev{font-size:11.5px;line-height:1.35;margin:1px 0}.evCash{color:#9fe3b9}.evStock{color:#f3d58a}.evRights{color:#f5a3a3}.evBctc{color:#bbb}th.earn,td.earn{min-width:230px;width:230px}.etag{display:inline-block;font-size:11px;padding:1px 6px;border-radius:3px;margin-bottom:3px}.eOut{background:#1d3a2a;color:#9fe3b9}.eWait{background:#2a2a2a;color:#bbb}.elab{font-size:12px;margin:2px 0}.esvg{display:block;margin:3px 0}.eBar{fill:#5a7fa8}.eLast{fill:var(--yellow)}.eNeg{fill:var(--red)}\n</style>")
sys.path.insert(0, RUN + "q3"); import legend as _lg
rep("<h2>3. Bảng phân tích ", _lg.LEGEND + "<h2>3. Bảng phân tích ")
rep("</style>", _lg.LCSS + "\n</style>")

dmy4 = lambda iso: iso[8:10] + "/" + iso[5:7] + "/" + iso[:4]
for k, v in {"@D0Y@": dmy4(ASOF), "@D0@": dm(SD[-1]), "@D1@": dm(SD[-2]), "@D2@": dm(SD[-3]), "@NN@": dm(NN_ASOF),
             "@TD@": dm(TD_ASOF), "@F9@": dm(FD10[-1]), "@RS0@": dm(SD[-11]), "@WK@": dm(WK["fund"]), "@Q@": WK["earn"]}.items():
    html = html.replace(k, v)
os.makedirs(RUN + "out", exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html)
json.dump(data, open(RUN + "out/data.json", "w"), ensure_ascii=False)
print("written", OUT, len(html), "rows", len(rows))
