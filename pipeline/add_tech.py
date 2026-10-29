"""29/10: thêm 8 mã mới từ 4 watchlist TradingView, CHỈ phần kỹ thuật (giá, RVOL, RS vs VN30, NN/TD).
Cơ bản / tin / quỹ / nội bộ / CTCK để trống (NONE). Idempotent: bỏ qua mã đã có."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
ADD = {  # mã: (tên, sàn, ICB, ngành, mã mẫu ngành, nhãn list, icb khác mã mẫu?)
    "VTZ": ("Nhựa Việt Thành", "HNX", "1353", "Nhựa, cao su & sợi", "AAA", "VN RVOL (29/10)", False),
    "BVH": ("Tập đoàn Bảo Việt", "HOSE", "8575", "Bảo hiểm nhân thọ", "ABI", "VN RVOL (29/10)", True),
    "BCC": ("Xi măng Bỉm Sơn", "HNX", "2353", "Vật liệu xây dựng & Nội thất", "HT1", "VN RVOL (29/10)", False),
    "BCE": ("XD và GT Bình Dương", "HOSE", "2357", "Xây dựng", "CTD", "Stage 0-1 (W-D MA10)", False),
    "PXL": ("KCN Dầu khí Long Sơn", "UPCOM", "8633", "Bất động sản", "IDC", "Stage 0-1 (W-D MA10)", False),
    "PVT": ("Vận tải Dầu khí PVTrans", "HOSE", "2773", "Vận tải Thủy", "VOS", "Stage 1-2 (Emerging)", False),
    "GVR": ("Tập đoàn CN Cao su VN", "HOSE", "1353", "Nhựa, cao su & sợi", "DPR", "Stage 1-2 (Emerging)", False),
    "TVD": ("Than Vàng Danh", "HNX", "1771", "Khai thác Than", "NBC", "Stage 1-2 (Emerging)", False),
}
GROUP = {"VTZ": "Nhựa · bao bì", "BVH": "Bảo hiểm", "BCC": "VLXD · đá · xi măng · gạch", "BCE": "Xây dựng · hạ tầng",
         "PXL": "BĐS KCN", "PVT": "Vận tải biển", "GVR": "Cao su", "TVD": "Khoáng sản · than"}
L = json.load(open(H + "lists121.json"))
todo = [t for t in ADD if t not in L]
inbox = json.load(open(H + "inbox/2026-10-29_tech.json"))
new = json.load(open(H + "raw_add2/new.json"))
def app(path, lines):
    with open(H + path, "a", encoding="utf-8") as f:
        for l in lines: f.write(l + "\n")
for t in todo:
    nm, ex, icb, ind, tm, lab, icbnone = ADD[t]
    b = inbox["bars"][t]; ds = sorted(b, reverse=True); C = [b[d][0] for d in ds]; V = [b[d][1] for d in ds]
    new[t] = dict(t=t, name=nm, exchange=ex, icb=icb, industry=ind, tmpl=tm, price=round(C[0] * 1000),
                  c0=C[0], c1=C[1], c5=C[5], c21=C[21], c63=C[63], f=None, band="Chưa kéo", caps=[], flags=[],
                  news=dict(n=0, score=0.0, sent="neutral", title="Chỉ cập nhật kỹ thuật — chưa kéo tin/catalyst",
                            summary="Mã thêm 29/10 từ watchlist TradingView; anh yêu cầu chỉ phân tích kỹ thuật (giá, RVOL, RS vs VN30, NN/TD). F, TCBS, SSI, quỹ, nội bộ, giá mục tiêu CTCK, tin chưa kéo.",
                            date="2026-10-29", source="—", direct=0),
                  volume=float(V[0]), icbnone=icbnone, techOnly=True)
    sf = inbox["stockflow"][t]; FD = sorted(sf, reverse=True)[:10]
    nn = " ".join(str(sf[d][0]) for d in FD); td = " ".join(str(sf[d][1]) for d in FD)
    app("raw_add2/tcbs_new.txt", [t + " None None None None None None None"])
    app("raw_add2/fund_new.txt", [t + " NONE"])
    app("raw_add2/insider_new.txt", [t + "|NONE:-:chưa kéo"])
    app("raw_add2/cons_new.txt", [t + "|NONE"])
    app("raw2610_add2/ssifa.txt", [t + " NONE"])
    app("raw2610_add2/flows.txt", [f"{t}|Neutral|{nn}|{td}|{C[0]} {C[1]} {C[5]}"])
    app("raw2810/f27_121.txt", [f"{t}|Neutral|{nn}|{td}|{V[0]}"])
    app("raw2610_add2/px.txt", [f"{t} {C[21]} {C[63]}"])
    L[t] = [lab]
json.dump(new, open(H + "raw_add2/new.json", "w"), ensure_ascii=False)
json.dump(L, open(H + "lists121.json", "w"), ensure_ascii=False)
M = json.load(open(H + "conf/map.json"))
for g in M["groups"]:
    for t, gn in GROUP.items():
        if g["name"] == gn and t not in g["tickers"]: g["tickers"].append(t)
json.dump(M, open(H + "conf/map.json", "w"), ensure_ascii=False, indent=1)
EX = json.load(open(H + "conf/exchange.json"))
for t in ADD: EX[t] = ADD[t][1]
json.dump(EX, open(H + "conf/exchange.json", "w"))
TO = sorted(set(json.load(open(H + "conf/tech_only.json")) if os.path.exists(H + "conf/tech_only.json") else []) | set(ADD))
json.dump(TO, open(H + "conf/tech_only.json", "w"))
print("thêm", todo, "tổng", len(L))
