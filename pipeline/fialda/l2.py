import json
NA=None
perf = [
 ["Bất động sản","8600",0.12,NA,0.08,1.15,0.29,50.46],
 ["Du lịch và Giải trí","5700",-0.31,NA,2.12,5.73,0.47,-7.30],
 ["Dầu khí","0500",-0.21,NA,-4.53,-9.16,7.26,40.39],
 ["Bảo hiểm","8500",-0.13,NA,-0.33,-6.10,-5.24,12.46],
 ["ĐT chứng khoán / phi CK","8900",0.00,NA,0.84,2.27,6.17,12.25],
 ["Tài nguyên cơ bản","1700",-2.20,NA,-0.92,5.91,-1.19,4.05],
 ["Điện, nước & khí đốt","7500",0.46,NA,-0.32,-2.79,1.64,9.26],
 ["Ngân hàng","8300",-1.69,NA,-2.99,-3.05,-3.61,-4.66],
 ["Truyền thông","5500",-0.07,NA,-1.93,-3.92,-16.39,-36.84],
 ["Thực phẩm và đồ uống","3500",-1.26,NA,-2.99,-1.60,-4.29,-1.99],
 ["Xây dựng và Vật liệu","2300",-0.15,NA,-1.93,-0.43,-11.58,-14.74],
 ["Bán lẻ","5300",-1.01,NA,-1.82,0.30,-4.17,-2.38],
 ["Hàng cá nhân & Gia dụng","3700",-1.89,NA,-3.12,-7.55,-31.97,-29.59],
 ["Y tế","4500",-0.03,NA,-0.14,-0.76,-10.45,-10.24],
 ["Hóa chất","1300",-2.13,NA,-2.59,-4.92,-10.46,-3.14],
 ["Viễn thông","6500",-1.73,NA,-2.90,-6.22,-15.88,-0.05],
 ["Hàng & Dịch vụ CN","2700",-2.43,NA,-4.81,-3.37,-5.53,-11.77],
 ["Dịch vụ tài chính","8700",-1.42,NA,-4.50,-4.49,-18.18,-23.90],
 ["Công nghệ thông tin","9500",-0.21,NA,-7.15,-15.44,-22.45,-41.63],
 ["Ô tô và phụ tùng","3300",-0.47,NA,-0.94,-2.54,-14.54,-29.31],
]
def pctile(vals):
    xs=[v for v in vals if v is not None]; n=len(xs)
    return [None if v is None else round(100*sum(1 for x in xs if x<v)/(n-1) + 100*(sum(1 for x in xs if x==v)-1)/(2*(n-1)),1) for v in vals]
cols={k:[r[i] for r in perf] for k,i in [("d1",2),("d3",3),("w1",4),("m1",5),("m6",6),("y1",7)]}
P={k:pctile(v) for k,v in cols.items()}
med={k:(sorted(x for x in v if x is not None)[len([x for x in v if x is not None])//2] if any(x is not None for x in v) else None) for k,v in cols.items()}
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
json.dump({"asof":"2026-10-30 (chốt phiên)","source":"Fialda chỉ số ngành ICB cấp 2; 3D chưa có (TCBS mất kết nối), ngắn hạn = 1W","median":med,"rows":out},open("l2rot.json","w"),ensure_ascii=False,indent=1)
