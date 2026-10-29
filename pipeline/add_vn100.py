"""29/10: VN30 + VN100 là danh mục MẶC ĐỊNH của báo cáo. Thêm các mã còn thiếu (chỉ kỹ thuật) và gắn nhãn VN30/VN100
cho mọi mã thuộc rổ. Chạy lại an toàn (bỏ qua mã đã có). Khi rổ VN100 đổi (kỳ review), sửa conf/idx.json rồi chạy lại."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
IDX = json.load(open(H + "conf/idx.json")); V30 = IDX["VN30"].split(); V100 = IDX["VN100"].split()
# mã: (tên, ICB, ngành, mã mẫu ngành, nhóm ngành trong conf/map.json, icb khác mã mẫu?)
INFO = {
 "BID": ("BIDV", "8355", "Ngân hàng", "TCB", "Ngân hàng", False),
 "LPB": ("LPBank", "8355", "Ngân hàng", "TCB", "Ngân hàng", False),
 "MBB": ("MBBank", "8355", "Ngân hàng", "TCB", "Ngân hàng", False),
 "SHB": ("SHB", "8355", "Ngân hàng", "TCB", "Ngân hàng", False),
 "SSB": ("SeABank", "8355", "Ngân hàng", "TCB", "Ngân hàng", False),
 "STB": ("Sacombank", "8355", "Ngân hàng", "TCB", "Ngân hàng", False),
 "BMP": ("Nhựa Bình Minh", "2353", "Vật liệu xây dựng & Nội thất", "NTP", "Nhựa · bao bì", False),
 "BSR": ("Lọc Hoá dầu Việt Nam", "0533", "Sản xuất và Khai thác dầu khí", "PVD", "Dầu khí", True),
 "PLX": ("Petrolimex", "0533", "Sản xuất và Khai thác dầu khí", "PVD", "Dầu khí", True),
 "CMG": ("Tập đoàn Công nghệ CMC", "9533", "Dịch vụ Máy tính", "YEG", "Công nghệ thông tin", True),
 "FPT": ("FPT Corp", "9537", "Phần mềm", "YEG", "Công nghệ thông tin", True),
 "CTR": ("Công trình Viettel", "2357", "Xây dựng", "CTD", "Xây dựng · hạ tầng", False),
 "HHV": ("Hạ tầng Giao thông Đèo Cả", "2357", "Xây dựng", "CTD", "Xây dựng · hạ tầng", False),
 "PC1": ("Tập đoàn PC1", "2357", "Xây dựng", "CTD", "Xây dựng · hạ tầng", False),
 "DPM": ("Đạm Phú Mỹ", "1357", "Sản phẩm hóa dầu, Nông dược & Hóa chất khác", "DCM", "Hóa chất · phân bón", False),
 "DSE": ("Chứng khoán DNSE", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "FTS": ("Chứng khoán FPT", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "SSI": ("Chứng khoán SSI", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "VCI": ("Chứng khoán Vietcap", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "VCK": ("Chứng khoán VPS", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "VIX": ("Chứng khoán VIX", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "VND": ("Chứng khoán VNDIRECT", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "VPX": ("Chứng khoán VPBank", "8777", "Môi giới chứng khoán", "HCM", "Chứng khoán", False),
 "DXG": ("Bluemarq Group (Đất Xanh)", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "KDH": ("Nhà Khang Điền", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "KOS": ("KOSY", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "NLG": ("Nam Long", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "NVL": ("Novaland", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "TAL": ("BĐS Taseco", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "VHM": ("Vinhomes", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "VPI": ("Văn Phú - Invest", "8633", "Bất động sản", "PDR", "BĐS dân cư", False),
 "SIP": ("Đầu tư Sài Gòn VRG", "8633", "Bất động sản", "IDC", "BĐS KCN", False),
 "GEX": ("Tập đoàn Gelex", "2737", "Thiết bị điện", "GEE", "Thiết bị điện · điện tử", False),
 "HDG": ("Tập đoàn Hà Đô", "7535", "Sản xuất & Phân phối Điện", "NT2", "Điện", False),
 "POW": ("PV Power", "7535", "Sản xuất & Phân phối Điện", "NT2", "Điện", False),
 "REE": ("Cơ Điện Lạnh REE", "7535", "Sản xuất & Phân phối Điện", "NT2", "Điện", False),
 "HPG": ("Hòa Phát", "1757", "Thép và sản phẩm thép", "HSG", "Thép", False),
 "KDC": ("Tập đoàn KIDO", "3577", "Thực phẩm", "MCH", "Thực phẩm · tiêu dùng", False),
 "PAN": ("Tập đoàn PAN", "3577", "Thực phẩm", "MCH", "Thực phẩm · tiêu dùng", False),
 "SBT": ("TTC AgriS (Mía đường TTC Biên Hòa)", "3577", "Thực phẩm", "MCH", "Thực phẩm · tiêu dùng", False),
 "PNJ": ("Vàng bạc Đá quý Phú Nhuận", "3767", "Hàng cá nhân", "LIX", "Trang sức · bán lẻ", False),
 "SAB": ("SABECO", "3533", "Sản xuất bia", "VNM", "Bia · đồ uống", True),
 "VHC": ("Vĩnh Hoàn", "3573", "Nuôi trồng nông & hải sản", "ANV", "Thủy sản · nông nghiệp", False),
 "PHR": ("Cao su Phước Hòa", "1353", "Nhựa, cao su & sợi", "DPR", "Cao su", False),
}
NEWG = {"Công nghệ thông tin": dict(etf=["XLK"], comm=[], note="XLK = Technology Select Sector SPDR"),
        "Trang sức · bán lẻ": dict(etf=["XRT"], comm=[], note=""),
        "Bia · đồ uống": dict(etf=["XLP"], comm=[], note="")}
L = json.load(open(H + "lists121.json"))
todo = [t for t in INFO if t not in L]
inbox = json.load(open(H + "inbox/2026-10-29_vn100.json"))
new = json.load(open(H + "raw_add2/new.json"))
def app(path, lines):
    with open(H + path, "a", encoding="utf-8") as f:
        for l in lines: f.write(l + "\n")
tv = {k.split(":")[1]: v for k, v in inbox["tv"].items()}
for t in todo:
    nm, icb, ind, tm, grp, icbnone = INFO[t]
    b = inbox["bars"][t]; ds = sorted(b, reverse=True); C = [b[d][0] for d in ds]; V = [b[d][1] for d in ds]
    p = tv[t]; c21 = C[0] / (1 + p["Perf.1M"] / 100); c63 = C[0] / (1 + p["Perf.3M"] / 100)
    new[t] = dict(t=t, name=nm, exchange="HOSE", icb=icb, industry=ind, tmpl=tm, price=round(C[0] * 1000),
                  c0=C[0], c1=C[1], c5=C[5], c21=c21, c63=c63, f=None, band="Chưa kéo", caps=[], flags=[],
                  news=dict(n=0, score=0.0, sent="neutral", title="Chỉ cập nhật kỹ thuật — chưa kéo tin/catalyst",
                            summary="Mã thuộc rổ VN30/VN100 (danh mục mặc định), thêm 29/10 chỉ phần kỹ thuật (giá, RVOL, RS vs VN30, NN/TD). F, TCBS, SSI, quỹ, nội bộ, giá mục tiêu CTCK, tin sẽ kéo ở nhịp tuần.",
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
    app("raw2610_add2/px.txt", [f"{t} {c21} {c63}"])
    L[t] = []
# nhãn rổ chỉ số cho mọi mã thuộc rổ (kể cả mã đã có)
for t in V100:
    if t not in L: continue
    lab = "VN30" if t in V30 else "VN100"
    L[t] = [x for x in L[t] if x not in ("VN30", "VN100")] + [lab]
json.dump(new, open(H + "raw_add2/new.json", "w"), ensure_ascii=False)
json.dump(L, open(H + "lists121.json", "w"), ensure_ascii=False)
M = json.load(open(H + "conf/map.json"))
names = {g["name"] for g in M["groups"]}
for gn, g in NEWG.items():
    if gn not in names: M["groups"].append(dict(name=gn, tickers=[], **g))
for g in M["groups"]:
    for t, v in INFO.items():
        if g["name"] == v[4] and t not in g["tickers"]: g["tickers"].append(t)
json.dump(M, open(H + "conf/map.json", "w"), ensure_ascii=False, indent=1)
EX = json.load(open(H + "conf/exchange.json"))
for t in INFO: EX[t] = "HOSE"
json.dump(EX, open(H + "conf/exchange.json", "w"))
SY = json.load(open(H + "conf/syms.json"))
if "XLK" not in SY["ex"]: SY["ex"]["XLK"] = "AMEX"; SY["syms"].append("AMEX:XLK")
json.dump(SY, open(H + "conf/syms.json", "w"), ensure_ascii=False)
TO = sorted(set(json.load(open(H + "conf/tech_only.json"))) | set(INFO))
json.dump(TO, open(H + "conf/tech_only.json", "w"))
print("thêm", len(todo), "mã; tổng", len(L), "; VN30 có", sum(1 for v in L.values() if "VN30" in v), "; VN100 (ngoài VN30)", sum(1 for v in L.values() if "VN100" in v))
