import json
NA=None
perf = [
 ["Bất động sản","8600",0.13,0.64,4.89,0.16,-2.60,45.55],
 ["Du lịch và Giải trí","5700",0.63,1.70,3.07,4.66,1.13,-7.73],
 ["Dầu khí","0500",-0.11,-0.93,1.84,-7.48,12.90,49.07],
 ["Bảo hiểm","8500",1.64,0.41,1.36,-4.69,-4.44,14.53],
 ["ĐT chứng khoán / phi CK","8900",0.00,NA,0.84,2.27,6.17,12.25],
 ["Tài nguyên cơ bản","1700",-0.09,0.67,0.69,8.78,0.90,6.71],
 ["Điện, nước & khí đốt","7500",-0.47,0.00,0.59,-2.14,2.35,9.86],
 ["Ngân hàng","8300",0.98,-0.86,0.47,-1.13,-1.67,-2.10],
 ["Truyền thông","5500",0.56,1.34,0.23,-1.37,-15.93,-34.02],
 ["Thực phẩm và đồ uống","3500",0.26,-0.52,-0.50,1.00,-2.38,2.58],
 ["Xây dựng và Vật liệu","2300",-0.03,-0.32,-0.63,1.55,-9.97,-12.70],
 ["Bán lẻ","5300",-0.19,-1.17,-0.84,1.95,-3.58,-0.61],
 ["Hàng cá nhân & Gia dụng","3700",0.43,0.29,-0.95,-6.97,-29.59,-26.81],
 ["Y tế","4500",-0.66,-0.65,-0.98,-1.25,-9.32,-10.58],
 ["Hóa chất","1300",0.08,-1.03,-1.05,-1.73,-6.95,0.50],
 ["Viễn thông","6500",-0.89,-1.09,-1.07,-4.21,-15.12,8.49],
 ["Hàng & Dịch vụ CN","2700",0.00,-2.23,-1.22,1.36,-3.14,-8.32],
 ["Dịch vụ tài chính","8700",-0.35,-2.66,-2.20,-2.66,-16.62,-23.55],
 ["Công nghệ thông tin","9500",-2.26,-4.86,-5.50,-14.29,-19.47,-39.79],
 ["Ô tô và phụ tùng","3300",-0.15,-1.05,-0.72,-2.75,-14.95,-30.07],
]
def pctile(vals):
    xs=[v for v in vals if v is not None]; n=len(xs)
    return [None if v is None else round(100*sum(1 for x in xs if x<v)/(n-1) + 100*(sum(1 for x in xs if x==v)-1)/(2*(n-1)),1) for v in vals]
cols={k:[r[i] for r in perf] for k,i in [("d1",2),("d3",3),("w1",4),("m1",5),("m6",6),("y1",7)]}
P={k:pctile(v) for k,v in cols.items()}
med={k:sorted(x for x in v if x is not None)[len([x for x in v if x is not None])//2] for k,v in cols.items()}
out=[]
for i,r in enumerate(perf):
    # Độ mạnh (trend): 1M 40% · 6M 40% · 1Y 20%
    strength=0.4*P["m1"][i]+0.4*P["m6"][i]+0.2*P["y1"][i]
    # Động lượng ngắn: 1W 70% + 3D 30% (3D thiếu → chỉ 1W)
    short=P["w1"][i] if P["d3"][i] is None else 0.7*P["w1"][i]+0.3*P["d3"][i]
    mom=short-P["m1"][i]          # thứ hạng ngắn hạn so với 1M: dương = tiền đang vào
    if strength>=50 and short>=50: ph="Dẫn dắt"
    elif strength>=50: ph="Suy yếu"
    elif short>=50: ph="Cải thiện"
    else: ph="Tụt hậu"
    out.append(dict(name=r[0],code=r[1],d1=r[2],d3=r[3],w1=r[4],m1=r[5],m6=r[6],y1=r[7],strength=round(strength,1),short=round(short,1),mom=round(mom,1),phase=ph))
out.sort(key=lambda x:-(x["strength"]+x["short"]))
for x in out: print(f'{x["code"]} {x["name"][:22]:22} str {x["strength"]:5.1f} short {x["short"]:5.1f} mom {x["mom"]:+6.1f} {x["phase"]}  1W {x["w1"]:+.2f} 1M {x["m1"]:+.2f} 6M {x["m6"]:+.2f}')
json.dump({"asof":"2026-10-28 ~14:45 (giữa phiên)","source":"Fialda chỉ số ngành ICB cấp 2, 3D từ TCBS","median":med,"rows":out},open("l2rot.json","w"),ensure_ascii=False,indent=1)
