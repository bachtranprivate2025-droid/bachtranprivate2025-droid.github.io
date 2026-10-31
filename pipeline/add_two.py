"""31/10: thêm IDC (HNX, BĐS KCN) + HVN (HOSE, hàng không) — mã NN+TD mua ròng 10 phiên. Chỉ kỹ thuật. Idempotent."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
B = json.load(open("/tmp/idc_hvn.json"))
INFO = {"IDC": ("IDICO", "HNX", "8633", "Bất động sản", "IDC", "BĐS KCN", False,
                [3.92,7.62,15.24,3.47,18.21,6.49,18.66,-7.6,12.11,-0.09], [0,0,0,-0.28,0,0,-1.87,0.28,-0.29,-0.1]),
        "HVN": ("Vietnam Airlines", "HOSE", "5751", "Dịch vụ hàng không", "VJC", "Hàng không · sân bay", False,
                [-1.79,-0.72,-1.87,8.33,-1.09,1.78,1.72,1.97,13.57,15.1], [0,0,0,0,0,0,0,0,-13.59,-11.18])}
L = json.load(open(H+"lists121.json")); ST = json.load(open(H+"store/daily.json")); D = ST["dates"]; vs = ST.setdefault("volSrc", {})
new = json.load(open(H+"raw_add2/new.json")); M = json.load(open(H+"conf/map.json"))
def app(p, l): open(H+p, "a", encoding="utf-8").write(l+"\n")
for t, (nm, ex, icb, ind, tm, grp, inone, nn, td) in INFO.items():
    if t in L: continue
    bars = sorted(B[t]["bars"], key=lambda b: b["date"], reverse=True)
    cl = [b["close"] for b in bars]; vol = [b["volume"] for b in bars]
    ST["close"][t] = {}; ST["vol"][t] = {}; vs[t] = {}
    for b in bars:
        if b["date"] in D: ST["close"][t][b["date"]] = b["close"]; ST["vol"][t][b["date"]] = float(b["volume"]); vs[t][b["date"]] = "finlens"
    ds = [b["date"] for b in bars][:10]
    ST["nn"][t] = dict(zip(ds, nn)); ST["td"][t] = dict(zip(ds, td))
    ST["tv"]["perf"][t] = {"w": (cl[0]/cl[5]-1)*100, "m1": (cl[0]/cl[21]-1)*100, "m3": (cl[0]/cl[63]-1)*100, "m6": None, "close": cl[0]*1000, "vol": vol[0]}
    new[t] = dict(t=t, name=nm, exchange=ex, icb=icb, industry=ind, tmpl=tm, price=round(cl[0]*1000), c0=cl[0], c1=cl[1], c5=cl[5], c21=cl[21], c63=cl[63],
                  f=None, band="Chưa kéo", caps=[], flags=[], news=dict(n=0, score=0.0, sent="neutral", title="Chỉ cập nhật kỹ thuật — chưa kéo tin/catalyst",
                  summary="Mã thêm 31/10 (NN+TD mua ròng 10 phiên). Chỉ có kỹ thuật; F, TCBS, SSI, quỹ, nội bộ, CTCK, tin chưa kéo.", date="2026-10-30", source="—", direct=0),
                  volume=float(vol[0]), icbnone=inone, techOnly=True)
    nns = " ".join(map(str, nn)); tds = " ".join(map(str, td))
    app("raw_add2/tcbs_new.txt", t+" None None None None None None None"); app("raw_add2/fund_new.txt", t+" NONE")
    app("raw_add2/insider_new.txt", t+"|NONE:-:chưa kéo"); app("raw_add2/cons_new.txt", t+"|NONE"); app("raw2610_add2/ssifa.txt", t+" NONE")
    app("raw2610_add2/flows.txt", f"{t}|Neutral|{nns}|{tds}|{cl[0]} {cl[1]} {cl[5]}")
    app("raw2810/f27_121.txt", f"{t}|Neutral|{nns}|{tds}|{vol[0]}"); app("raw2610_add2/px.txt", f"{t} {cl[21]} {cl[63]}")
    L[t] = ["Bổ sung (anh thêm)"]
    for g in M["groups"]:
        if g["name"] == grp and t not in g["tickers"]: g["tickers"].append(t)
json.dump(ST, open(H+"store/daily.json", "w")); json.dump(new, open(H+"raw_add2/new.json", "w"), ensure_ascii=False)
json.dump(L, open(H+"lists121.json", "w"), ensure_ascii=False); json.dump(M, open(H+"conf/map.json", "w"), ensure_ascii=False, indent=1)
print("OK", len(L))
