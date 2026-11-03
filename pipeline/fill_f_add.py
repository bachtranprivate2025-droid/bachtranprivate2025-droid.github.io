"""Gộp kết quả quality_scan vào conf/fill_f.json. Dùng: python3 fill_f_add.py 'T|f|band|caps;caps|flag;flag;flag'"""
import json, sys, os
P = os.path.dirname(os.path.abspath(__file__)) + "/conf/fill_f.json"
D = json.load(open(P)) if os.path.exists(P) else {}
for l in sys.stdin.read().strip().splitlines():
    t, f, band, caps, fl = l.split("|")
    D[t] = dict(f=float(f), band=band, caps=[c for c in caps.split(";") if c], flags=[x for x in fl.split(";") if x])
json.dump(D, open(P, "w"), ensure_ascii=False, indent=0); print(len(D))
