"""Đồng bộ danh mục báo cáo = 4 watchlist TradingView (conf/watchlists.json) + VN30/VN100 (conf/idx.json)
+ mã anh tự thêm ("Bổ sung (anh thêm)"). Xóa mọi nhãn/mã khác. Mã mới chỉ thêm phần kỹ thuật.

Cách chạy (nhịp tuần hoặc khi anh đổi watchlist):
  1. TradingView mcp-watchlist-get-watchlist cho 4 id trong conf/watchlists.json → sửa danh sách mã trong file.
  2. Mã mới: FinLens stocks_get_profile + stocks_get_price_history limit=34 + flows_get_stock_flow days=11,
     TradingView batch (close, volume, Perf.*) → điền NEWINFO bên dưới (ICB, mã mẫu, nhóm ngành).
  3. python3 pipeline/extract.py <tag>; python3 pipeline/sync_lists.py pipeline/inbox/<tag>.json; ingest; build.
"""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)) + "/"
W = json.load(open(H + "conf/watchlists.json"))
IDX = json.load(open(H + "conf/idx.json")); V30 = set(IDX["VN30"].split()); V100 = set(IDX["VN100"].split())
WL = ["Stage 2-2", "Stage 1-2 (Emerging)", "Stage 0-1 (W-D MA10)", "VN RVOL"]
MAN = "Bổ sung (anh thêm)"
# mã mới: (tên, sàn, ICB, ngành, mã mẫu, nhóm ngành, icb khác mã mẫu?)
NEWINFO = {
 "HHS": ("Đầu tư DV Hoàng Huy", "HOSE", "3353", "Sản xuất ô tô", "GEE", "Ô tô · cơ khí", True),
 "SBG": ("Cơ khí Công nghệ cao Siba", "HOSE", "2727", "Công nghiệp phức hợp", "GEE", "Ô tô · cơ khí", True),
 "VC3": ("Tập đoàn Nam Mê Kông", "HNX", "8637", "Tư vấn, môi giới BĐS", "DXS", "BĐS dân cư", False),
 "LSG": ("BĐS Sài Gòn Vina", "UPCOM", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "VCR": ("Du lịch ITC (Vinacapital Resort)", "UPCOM", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "VGR": ("Cảng xanh VIP", "UPCOM", "2777", "Kho bãi, hậu cần", "VSC", "Cảng · logistics", False),
 "DMX": ("Đầu tư Điện Máy Xanh", "HOSE", "5373", "Bán lẻ phức hợp", "FRT", "Bán lẻ · phân phối", True),
 "HNG": ("Nông nghiệp Quốc tế HAGL", "UPCOM", "3573", "Nuôi trồng nông & hải sản", "ANV", "Thủy sản · nông nghiệp", False),
 "DBD": ("Bidiphar", "HOSE", "4577", "Dược phẩm", "DCL", "Dược · y tế", False),
 "SAM": ("SAM Holdings", "HOSE", "9578", "Thiết bị viễn thông", "YEG", "Công nghệ thông tin", True),
 "RYG": ("Hoàng Gia (gạch ốp lát)", "HOSE", "2353", "Vật liệu xây dựng & Nội thất", "HT1", "VLXD · đá · xi măng · gạch", False),
 "TLD": ("Đô thị Thăng Long (gỗ, ván ép)", "HOSE", "2353", "Vật liệu xây dựng & Nội thất", "HT1", "VLXD · đá · xi măng · gạch", False),
}
NEWG = {"Ô tô · cơ khí": dict(etf=["XLY"], comm=[], note="")}
L0 = json.load(open(H + "lists121.json"))
man = {t for t, v in L0.items() if MAN in v}
L = {}
for lab in WL:
    for t in W[lab].split(): L.setdefault(t, []).append(lab)
for t in V100: L.setdefault(t, []).append("VN30" if t in V30 else "VN100")
for t in man: L.setdefault(t, []).append(MAN)
todo = [t for t in L if t not in L0]
miss = [t for t in todo if t not in NEWINFO]
assert not miss, f"thiếu NEWINFO cho {miss}"
if todo:
    IN = json.load(open(sys.argv[1]))
    ST = json.load(open(H + "store/daily.json")); asof = ST["dates"][-1]
    new = json.load(open(H + "raw_add2/new.json")); tv = {k.split(":")[1]: v for k, v in IN["tv"].items()}
    def app(path, lines):
        with open(H + path, "a", encoding="utf-8") as f:
            for l in lines: f.write(l + "\n")
    for t in todo:
        nm, ex, icb, ind, tm, grp, icbnone = NEWINFO[t]
        b = {d: v for d, v in IN["bars"][t].items() if d <= asof}
        ds = sorted(b, reverse=True); C = [b[d][0] for d in ds]; V = [b[d][1] for d in ds]
        p = tv[t]; c21 = C[0] / (1 + p["Perf.1M"] / 100); c63 = C[0] / (1 + p["Perf.3M"] / 100)
        new[t] = dict(t=t, name=nm, exchange=ex, icb=icb, industry=ind, tmpl=tm, price=round(C[0] * 1000),
                      c0=C[0], c1=C[1], c5=C[5], c21=c21, c63=c63, f=None, band="Chưa kéo", caps=[], flags=[],
                      news=dict(n=0, score=0.0, sent="neutral", title="Chỉ cập nhật kỹ thuật — chưa kéo tin/catalyst",
                                summary="Mã mới trong watchlist TradingView, thêm phần kỹ thuật (giá, RVOL, RS vs VN30, NN/TD). Cơ bản, tin kéo ở nhịp tuần.",
                                date=asof, source="—", direct=0),
                      volume=float(V[0]), icbnone=icbnone, techOnly=True)
        sf = {d: v for d, v in IN["stockflow"][t].items() if d <= asof}; FD = sorted(sf, reverse=True)[:10]
        nn = " ".join(str(sf[d][0]) for d in FD); td = " ".join(str(sf[d][1]) for d in FD)
        app("raw_add2/tcbs_new.txt", [t + " None None None None None None None"])
        app("raw_add2/fund_new.txt", [t + " NONE"])
        app("raw_add2/insider_new.txt", [t + "|NONE:-:chưa kéo"])
        app("raw_add2/cons_new.txt", [t + "|NONE"])
        app("raw2610_add2/ssifa.txt", [t + " NONE"])
        app("raw2610_add2/flows.txt", [f"{t}|Neutral|{nn}|{td}|{C[0]} {C[1]} {C[5]}"])
        app("raw2810/f27_121.txt", [f"{t}|Neutral|{nn}|{td}|{V[0]}"])
        app("raw2610_add2/px.txt", [f"{t} {c21} {c63}"])
    json.dump(new, open(H + "raw_add2/new.json", "w"), ensure_ascii=False)
    M = json.load(open(H + "conf/map.json")); names = {g["name"] for g in M["groups"]}
    for gn, g in NEWG.items():
        if gn not in names: M["groups"].append(dict(name=gn, tickers=[], **g))
    for g in M["groups"]:
        for t in todo:
            if g["name"] == NEWINFO[t][5] and t not in g["tickers"]: g["tickers"].append(t)
    json.dump(M, open(H + "conf/map.json", "w"), ensure_ascii=False, indent=1)
    EX = json.load(open(H + "conf/exchange.json"))
    for t in todo: EX[t] = NEWINFO[t][1]
    json.dump(EX, open(H + "conf/exchange.json", "w"))
    TO = sorted(set(json.load(open(H + "conf/tech_only.json"))) | set(todo))
    json.dump(TO, open(H + "conf/tech_only.json", "w"))
json.dump(L, open(H + "lists121.json", "w"), ensure_ascii=False)
rem = sorted(set(L0) - set(L))
print(f"{len(L)} mã · thêm {len(todo)}: {' '.join(todo)} · bỏ {len(rem)}: {' '.join(rem)}")
from collections import Counter; print(Counter(x for v in L.values() for x in v))
