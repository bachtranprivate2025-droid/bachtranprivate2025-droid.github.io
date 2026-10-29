import json, shutil, os
RUN="/home/claude/run85/"; D=RUN+"raw2810/"
for s,d in [("raw_add","raw_add2"),("raw2610_add","raw2610_add2")]:
    if os.path.exists(RUN+d): shutil.rmtree(RUN+d)
    shutil.copytree(RUN+s, RUN+d)
def app(path, lines):
    with open(path,"a",encoding="utf-8") as f:
        for l in lines: f.write(l.rstrip("\n")+"\n")
rl=lambda n:[l for l in open(D+n,encoding="utf-8") if l.strip()]
PX={}
for l in rl("px3.txt"):
    t,c,v,k=l.strip().split("|"); PX[t]=dict(cls=c.split(),vol=v.split(),k=[float(x) for x in k.split()])
FL={l.split("|")[0]:l.strip().split("|") for l in rl("f3.txt")}
Q=json.load(open(D+"qual3.json"))
INFO={"GIL":("Gilimex (XNK Bình Thạnh)","HOSE","3763","Hàng May mặc","TNG"),
"DLG":("Tập đoàn Đức Long Gia Lai","HOSE","2357","Xây dựng","CTD"),
"EVF":("Tài chính Tổng hợp Điện lực (EVNFinance)","HOSE","8773","Tài chính cá nhân (công ty tài chính)","TCB")}
NEWS={
"GIL":dict(n=8,score=-0.05,sent="negative",title="GIL thay TGĐ, ĐHCĐ bất thường; kiểm toán ngoại trừ vì vụ kiện Amazon, bị cắt margin",summary="20/10 TGĐ và trước đó kế toán trưởng từ nhiệm, bổ nhiệm TGĐ mới Hoàng Tiến Đạt; giải thể 2 công ty con để tái cấu trúc. Kiểm toán ngoại trừ BCTC bán niên 2026 do chưa trích lập ~800 tỷ tồn kho liên quan vụ kiện Amazon → HOSE cắt margin. 6T/2026 LNST 21 tỷ (cùng kỳ lỗ 68 tỷ). Mảng KCN (Gilimex Industrial Park) là câu chuyện dài hạn.",date="2026-10-27 16:39",source="vietstock / tinnhanhchungkhoan",direct=0.9),
"DLG":dict(n=0,score=0.0,sent="neutral",title="DLG không có tin mới; sự kiện gần nhất là BCTC quý 2/2026 (TCBS)",summary="FinLens không có tin riêng DLG trong 30 ngày; fallback TCBS (CBTT HOSE): chỉ có BCTC Q2/2026 (31/07) và thay đổi địa chỉ (25/08). Không có catalyst.",date="2026-08-25 00:00",source="TCBS",direct=0.2),
"EVF":dict(n=7,score=0.295,sent="positive",title="EVF lãi trước thuế 9T/2026 1.036 tỷ (+14,5%); chào bán riêng lẻ 85 triệu cp giá 13.500 đ cho 4 NĐT",summary="21/10: LNTT 9 tháng 1.035,8 tỷ (+14,5%), Q3 336,5 tỷ (+9,8%); tổng tài sản 96.197 tỷ (+15,8%). 15/10: chào bán riêng lẻ 85 triệu cp giá 13.500 đ (cao hơn thị giá ~11.800) cho Leadvisors, JVCF I, SSIAM, Daiwa-SSIAM. S&P xếp hạng B+, FiinRatings A; dự kiến phát hành 300 triệu USD trái phiếu quốc tế quý IV.",date="2026-10-21 16:37",source="nguoiduatin / vietstock",direct=0.8)}
new=json.load(open(RUN+"raw_add2/new.json"))
for t,(nm,ex,icb,ind,tm) in INFO.items():
    c0,c1,c5,c21,c63=PX[t]["k"]
    e=dict(t=t,name=nm,exchange=ex,icb=icb,industry=ind,tmpl=tm,price=round(c0*1000),c0=c0,c1=c1,c5=c5,c21=c21,c63=c63,
           f=Q[t]["f"],band=Q[t]["band"],caps=Q[t]["caps"],flags=Q[t]["flags"],news=NEWS[t],volume=float(PX[t]["vol"][1]))
    if t=="EVF": e["icbpx"]=[290.97,292.56,302.94,292.08]
    new[t]=e
json.dump(new,open(RUN+"raw_add2/new.json","w"),ensure_ascii=False)
R=RUN+"raw_add2/"; R6=RUN+"raw2610_add2/"
app(R+"tcbs_new.txt",rl("tcbs3.txt")); app(R+"fund_new.txt",rl("fund3.txt")); app(R+"insider_new.txt",rl("insider3.txt")); app(R+"cons_new.txt",rl("cons3.txt"))
app(R6+"flows.txt",["|".join(FL[t][:4]+[" ".join(str(x) for x in PX[t]["k"][:3])]) for t in INFO])
app(R6+"px.txt",[f"{t} {PX[t]['k'][3]} {PX[t]['k'][4]}" for t in INFO])
app(R6+"ssifa.txt",["GIL NONE","DLG NONE","EVF 45 38 0 56 2026-10-27"])
app(R6+"icbpx.txt",["8773 290.97 292.56 302.94 292.08"])
app(R6+"icbstr.txt",["8773 18 0.2769 40 2 2 -0.0191 -0.2763 -0.2122 -0.0403 -22"])
def cp_app(src,dst,lines):
    shutil.copy(RUN+src,RUN+dst); app(RUN+dst,lines)
cp_app("raw2710d/vol118.txt","raw2810/vol121.txt",[t+" "+" ".join(PX[t]["vol"][1:]) for t in INFO])
cp_app("raw2710d/f27_118.txt","raw2810/f27_121.txt",["|".join(FL[t][:4]+[PX[t]["vol"][0]]) for t in INFO])
cp_app("raw2710d/cls118.txt","raw2810/cls121.txt",[t+" "+" ".join(PX[t]["cls"]) for t in INFO])
L=json.load(open(RUN+"lists118.json"))
L={t:[("VN RVOL (28/10)" if x=="VN RVOL (27/10)" else x) for x in v] for t,v in L.items()}
for t in INFO: L[t]=["VN RVOL (28/10)"]
json.dump(L,open(RUN+"lists121.json","w"),ensure_ascii=False)
# conf map
M=json.load(open(RUN+"conf/map.json"))
for g in M["groups"]:
    if g["name"]=="May mặc": g["tickers"].append("GIL")
    if g["name"]=="Xây dựng · hạ tầng": g["tickers"].append("DLG")
M["groups"].append(dict(name="Tài chính tiêu dùng",tickers=["EVF"],etf=["XLF"],comm=[],note=""))
json.dump(M,open(RUN+"conf/map.json","w"),ensure_ascii=False,indent=1)
print(len(L))
