import json
Q={ # close, sma20, sma50, perf1M (TradingView 27/10)
"KBE":(66.06,64.03,66.09,1.74),"XLF":(55.88,54.87,56.0,2.30),"CBOE:PAVE":(52.96,53.05,53.86,-0.69),"IAI":(178.16,177.05,184.25,-1.81),
"BDRY":(12.57,13.34,14.58,-18.75),"CBOE:IYT":(82.16,80.04,81.83,3.84),"JETS":(27.02,26.98,28.04,-5.89),"BOAT":(52.12,52.47,51.31,1.52),
"XRT":(87.31,85.24,85.18,6.13),"XLB":(51.78,50.15,50.98,4.02),"XLP":(87.15,84.86,84.47,7.05),"KIE":(62.46,61.23,61.98,4.38),
"XPH":(63.96,63.37,67.10,-3.96),"XLV":(179.18,173.3,171.6,5.44),"XLU":(42.85,41.44,41.81,8.73),"XLE":(68.21,66.11,64.61,10.16),
"OIH":(408.87,387.73,401.69,4.17),"GRID":(167.05,174.09,176.96,-6.72),"REMX":(54.2,57.62,66.97,-18.55),"XLY":(115.45,112.55,113.33,4.32),
"IHI":(54.53,52.77,53.08,6.28),"PEJ":(65.37,64.05,64.35,5.23),"XLC":(103.58,109.76,111.28,-8.71),"MOO":(80.83,81.41,83.70,-3.37),
"CBOE:ITB":(90.35,86.75,90.05,2.21),"SLX":(101.55,102.47,105.48,-2.84),"XLK":(189.49,192.57,189.55,-3.09),"XME":(100.5,102.43,109.53,-6.96),
"VNQ":(92.39,90.88,93.49,0.92),"WOOD":(65.86,66.35,69.16,-4.97),
"HRC1!":(1342,1283.85,1247.16,8.66),"HE1!":(62.03,67.42,74.15,-11.74),"SB1!":(19.2,20.26,18.80,9.71),"CT1!":(78.05,80.0,83.63,-5.28),
"NG1!":(3.058,3.018,2.959,-2.86),"NCF1!":(153,152.44,148.0,4.08),"HG1!":(6.643,6.603,6.626,-1.84),"BRN1!":(111.21,106.86,101.38,12.77),
"UFV1!":(436.5,434.28,435.39,-4.49),"TF1!":(253.8,256.81,243.03,-0.51)}
SPY1M=0.11
COMM={"HRC1!","HE1!","SB1!","CT1!","NG1!","NCF1!","HG1!","BRN1!","UFV1!","TF1!"}
def st(k,inv=False):
    c,a,b,m=Q[k]; bench=0 if k in COMM else SPY1M
    if inv:
        if c<a and c<b and m<0: return "🟢"
        if c>a and c>b and m>0: return "🔴"
        return "🟡"
    if c>a and c>b and m>bench: return "🟢"
    if c<a and c<b and m<bench: return "🔴"
    return "🟡"
# nhóm: (tên, mã, ETF Mỹ, hàng hóa, ghi chú)
G=[
("Ngân hàng","ABB ACB CTG EIB HDB KLB MSB NAB NVB OCB TCB TPB VAB VIB VPB",["KBE","XLF"],[],""),
("Chứng khoán","AAS BSI CTS HCM ORS TCX VDS",["IAI"],[],""),
("Bảo hiểm","ABI BMI",["KIE"],[],""),
("BĐS dân cư","DIG HDC HTN LDG PDR QCG TCH VIC VRE DXS SJS",["CBOE:ITB","VNQ"],[],"Tương quan yếu, chủ yếu xét ngành VN"),
("BĐS KCN","BCM IDC IJC KBC SZC",["CBOE:IYT"],[],"KCN ăn theo FDI/chuỗi cung ứng; ETF chỉ tham khảo"),
("Xây dựng · hạ tầng","C4G CDC CII CTD CTI DPG EVG HID VC7 HUT TV2 GEL",["CBOE:PAVE"],["-HRC1!"],"HUT trước đây ghép nhầm bông → đổi PAVE"),
("Thép","HSG NKG VGS SHI",["XLB","SLX"],["HRC1!"],"Quặng sắt giảm = biên lợi nhuận tốt hơn"),
("VLXD · đá · xi măng · gạch","DGT HDA HT1 KSB SCL VGC",["XLB","CBOE:PAVE"],["-NCF1!"],"Than là chi phí đầu vào xi măng (tăng = bất lợi)"),
("Hóa chất · phân bón","CSV DCM LAS DDV",["XLB"],["UFV1!"],"Urê cho DCM; DAP CBOT ít giao dịch nên không dùng"),
("Dầu nhờn · hóa dầu","PLC",["XLE"],["BRN1!"],""),
("Nhựa · bao bì","AAA APH",["XLB"],["-BRN1!"],"Hạt nhựa theo giá dầu (chi phí đầu vào)"),
("Cao su","DPR HII TRC",["XLB"],["TF1!"],"Cao su SGX TSR20"),
("Giấy","DHC HHP",["XLB","WOOD"],[],""),
("Dầu khí","PVD GAS",["XLE","OIH"],["BRN1!","NG1!"],"PVD dùng OIH; GAS dùng XLE + Brent + khí"),
("Vận tải dầu · khí","PVP",["BOAT"],["BRN1!"],""),
("Điện","NT2 QTP",["XLU"],["NG1!","NCF1!"],"NT2 theo khí, QTP theo than"),
("Thiết bị điện · điện tử","GEE NAG",["GRID","XLY"],["HG1!"],"GEE dùng GRID; NAG dùng XLY"),
("Cảng · logistics","DXP GMD PHP VSC MHC",["CBOE:IYT","BOAT"],[],""),
("Vận tải biển","HAH VOS",["BOAT","BDRY"],[],"HAH container (BOAT), VOS hàng rời (BDRY)"),
("Hàng không · sân bay","VJC ACV",["JETS"],["-BRN1!"],"Dầu tăng là bất lợi cho VJC"),
("Chuyển phát","VTP",["CBOE:IYT"],[],""),
("Bán lẻ · phân phối","MWG FRT DGW PET PSD",["XRT","XLY"],[],"DGW/PSD có thể thêm XLK"),
("Thực phẩm · tiêu dùng","MCH MSN LIX TLG",["XLP"],[],""),
("Đường","QNS",["XLP"],["SB1!"],""),
("Thủy sản · nông nghiệp","ANV CMX IDI HAG",["MOO"],[],"Cá tra không có hợp đồng tương lai"),
("Chăn nuôi heo","DBC BAF",["MOO"],["HE1!"],""),
("May mặc","TNG VGT",["XRT"],["-CT1!"],"Bông là chi phí đầu vào"),
("Dược · y tế","DCL FIT TNH CVN",["XLV","XPH","IHI"],[],"CVN dùng IHI"),
("Khoáng sản · than","MSR NBC",["REMX","XME"],["NCF1!"],"MSR dùng REMX; NBC dùng than Newcastle"),
("Máy móc · ô tô","VEA",["XLY"],[],""),
("Giải trí · truyền thông","VPL YEG",["PEJ","XLC"],[],"VPL dùng PEJ; YEG dùng XLC"),
]
d=json.load(open("/home/claude/run85/data118_2710.json"))
allT={r["t"] for r in d["rows"]}
seen=[t for g in G for t in g[1].split()]
print("missing",sorted(allT-set(seen)),"extra",sorted(set(seen)-allT),"dup",[t for t in seen if seen.count(t)>1])
lines=["| Nhóm | Mã | ETF Mỹ | Hàng hóa | Ghi chú |","|---|---|---|---|---|"]
nm=lambda k:k.split(":")[-1]
def fmt(k):
    inv=k.startswith("-"); k=k.lstrip("-")
    return (f"{st(k,inv)} {nm(k)} {Q[k][3]:+.1f}%"+(" (chi phí, giảm là tốt)" if inv else "")).replace(".",",").replace("+-","−").replace("-","−")
for n,t,e,c,note in G:
    lines.append(f"| {n} | {t.replace(' ', ', ')} | {' · '.join(fmt(k) for k in e) or '–'} | {' · '.join(fmt(k) for k in c) or '–'} | {note} |")
open("table.md","w").write("\n".join(lines))
json.dump({"groups":[dict(name=n,tickers=t.split(),etf=e,comm=c,note=note) for n,t,e,c,note in G]},open("map.json","w"),ensure_ascii=False,indent=1)
print("\n".join(lines))
