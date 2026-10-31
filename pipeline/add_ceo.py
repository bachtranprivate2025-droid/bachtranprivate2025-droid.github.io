"""31/10: thêm CEO (HNX, BĐS) theo yêu cầu anh — CHỈ kỹ thuật (giá, RVOL, RS vs VN30, NN/TD). Idempotent."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
cl = [11.1,11.1,11.3,11.5,11.6,11.5,11.5,11.6,11,10.9,11,11,10.7,10.5,10.4,10.3,9.9,10.2,10.5,10.3,10.5,10.8,10.8,10.9,11,11.2,11.5,11.6,11.7,11.6,11.5,11.8,11.5,11.8,11.6,11.9,12.6,12.6,12.8,12.9,13.2,12.9,13,13.4,13.6,13.3,13.3,12.6,11.6,11.7,11.9,12.1,12,11.9,12.3,12.2,12.2,11.7,11.8,12,12,12,11.4,11.7]
dts = ["10-30","10-29","10-28","10-27","10-26","10-23","10-22","10-21","10-20","10-19","10-16","10-15","10-14","10-13","10-12","10-09","10-08","10-07","10-06","10-05","10-02","10-01","09-30","09-29","09-28","09-25","09-24","09-23","09-22","09-21","09-18","09-17","09-16","09-15","09-14","09-11","09-10","09-09","09-08","09-07","09-04","09-03","08-28","08-27","08-26","08-25","08-24","08-21","08-20","08-19","08-18","08-17","08-14","08-13","08-12","08-11","08-10","08-07","08-06","08-05","08-04","08-03","07-31","07-30"]
vol = [5257300,3312400,8147400,3985100,8640500,6458300,8335000,12861900,6213800,7751100,5206800,10337900,4844700,5058900,6119300,11741100,4882700,3956000,11083800,4872500,4994000,3841300,3873700,5789400,9240000,5961500,3897700,2911900,3342700,4464600,7565000,4735800,4080900,3842700,5249700,9135600,2515900,3680900,3162800,4343800,6408400,5876300,6583200,4742300,8414500,10009900,20634800,10612800,2210200,4420600,3382000,5761800,7600600,6050800,3670600,5320800,6788800,4158300,3005500,8181900,4470700,8161800,4518200,8364300]
assert len(cl)==len(dts)==len(vol)==64
nn = [4.54,1.34,0.01,-0.21,-1.6,0.02,-17.97,1.58,-17.3,-17.65]; td = [0,0,0,0.24,0,0,0,0,0,0]
bars = {"2026-"+d: (c, v) for d, c, v in zip(dts, cl, vol)}
t = "CEO"
L = json.load(open(H+"lists121.json"))
if t in L: raise SystemExit("CEO đã có")
ST = json.load(open(H+"store/daily.json")); D = ST["dates"]; vs = ST.setdefault("volSrc", {})
ST["close"][t] = {}; ST["vol"][t] = {}; vs[t] = {}
for d, (c, v) in bars.items():
    if d in D: ST["close"][t][d] = c; ST["vol"][t][d] = float(v); vs[t][d] = "finlens"
ST["nn"][t] = {}; ST["td"][t] = {}
for i, d in enumerate(sorted(["2026-"+x for x in dts[:10]], reverse=True)):
    ST["nn"][t][d] = nn[i]; ST["td"][t][d] = td[i]
ST["tv"]["perf"][t] = {"w": (cl[0]/cl[5]-1)*100, "m1": (cl[0]/cl[22]-1)*100, "m3": (cl[0]/cl[63]-1)*100, "m6": None, "close": cl[0]*1000, "vol": vol[0]}
json.dump(ST, open(H+"store/daily.json", "w"))
new = json.load(open(H+"raw_add2/new.json"))
new[t] = dict(t=t, name="Tập đoàn CEO", exchange="HNX", icb="8633", industry="Bất động sản", tmpl="PDR", price=round(cl[0]*1000),
              c0=cl[0], c1=cl[1], c5=cl[5], c21=cl[21], c63=cl[63], f=None, band="Chưa kéo", caps=[], flags=[],
              news=dict(n=0, score=0.0, sent="neutral", title="Chỉ cập nhật kỹ thuật — chưa kéo tin/catalyst",
                        summary="Mã anh thêm 31/10 (NN mua ròng 30/10). Chỉ có kỹ thuật; F, TCBS, SSI, quỹ, nội bộ, CTCK, tin chưa kéo.",
                        date="2026-10-30", source="—", direct=0), volume=float(vol[0]), icbnone=False, techOnly=True)
json.dump(new, open(H+"raw_add2/new.json", "w"), ensure_ascii=False)
def app(p, l):
    open(H+p, "a", encoding="utf-8").write(l+"\n")
nns = " ".join(map(str, nn)); tds = " ".join(map(str, td))
app("raw_add2/tcbs_new.txt", t+" None None None None None None None"); app("raw_add2/fund_new.txt", t+" NONE")
app("raw_add2/insider_new.txt", t+"|NONE:-:chưa kéo"); app("raw_add2/cons_new.txt", t+"|NONE"); app("raw2610_add2/ssifa.txt", t+" NONE")
app("raw2610_add2/flows.txt", f"{t}|Neutral|{nns}|{tds}|{cl[0]} {cl[1]} {cl[5]}")
app("raw2810/f27_121.txt", f"{t}|Neutral|{nns}|{tds}|{vol[0]}"); app("raw2610_add2/px.txt", f"{t} {cl[21]} {cl[63]}")
L[t] = ["Bổ sung (anh thêm)"]; json.dump(L, open(H+"lists121.json", "w"), ensure_ascii=False)
M = json.load(open(H+"conf/map.json"))
for g in M["groups"]:
    if g["name"] == "BĐS dân cư" and t not in g["tickers"]: g["tickers"].append(t)
json.dump(M, open(H+"conf/map.json", "w"), ensure_ascii=False, indent=1)
print("OK", len(L))
