# KQKD quý: TCBS income statement (quý) + phản ứng giá 28/10 (TradingView)
import json
def g(a, b):
    if a is None or b is None or b <= 0: return None
    return (a - b) / b
def load(run):
    raw = json.load(open(run + "q3/tcbs_raw.json"))
    tv = json.load(open(run + "q3/tv2810.json")); vniW = tv["VNINDEX"][1]
    out = {}
    for t, rows in raw.items():
        bank = "netInterestIncome" in rows[0]
        Q = {}
        for x in rows:
            Q[(x["year"], x["quarter"])] = dict(
                rev=x.get("totalOperationIncome") if bank else x.get("revenue"),
                np=x.get("shareHolderIncome"), gy=x.get("yearShareHolderIncomeGrowth"))
        # lùi Q3/24, Q4/24 từ tăng trưởng YoY TCBS báo cho Q3/25, Q4/25
        for q in (3, 4):
            c = Q.get((2025, q))
            if c and c["gy"] is not None and c["np"] is not None and (2024, q) not in Q:
                Q[(2024, q)] = dict(rev=None, np=c["np"] / (1 + c["gy"]), gy=None)
        seq = [(2024, 3), (2024, 4), (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2026, 1), (2026, 2), (2026, 3)]
        q3 = (2026, 3) in Q
        L = 8 if q3 else 7
        def v(i, k): 
            x = Q.get(seq[i]); return None if x is None else x[k]
        n, nb, npq = v(L, "np"), v(L-4, "np"), v(L-1, "np")
        yoy, qoq = g(n, nb), g(n, npq)
        ryoy, rqoq = g(v(L, "rev"), v(L-4, "rev")), g(v(L, "rev"), v(L-1, "rev"))
        prev = g(npq, v(L-5, "np"))
        ttm = [v(i, "np") for i in range(L-3, L+1)]; ttmB = [v(i, "np") for i in range(L-7, L-3)]
        T = sum(ttm) if None not in ttm else None
        TB = sum(ttmB) if None not in ttmB else None
        tyoy = g(T, TB)
        accel = yoy is not None and prev is not None and yoy > prev
        turn = nb is not None and nb <= 0 and n is not None and n > 0
        if n is not None and n < 0: lab, ep = "🔴 Lỗ", -1
        elif yoy is not None and yoy <= -0.25: lab, ep = "🔴 Giảm mạnh", -1
        elif yoy is not None and yoy >= 0.25 and accel: lab, ep = "🟢 Tăng mạnh + tăng tốc", 1
        elif yoy is not None and yoy >= 0.25: lab, ep = "🟡 Tăng mạnh, chưa tăng tốc", 0
        elif turn: lab, ep = "🟡 Lãi trở lại (cùng kỳ lỗ)", 0
        else: lab, ep = "🟡 Trung tính", 0
        if nb is not None and nb > 0 and n is not None and n / nb >= 5: lab += " · nền cùng kỳ rất thấp"
        lb = lambda i: "Q%d/%02d" % (seq[i][1], seq[i][0] % 100)
        react = None
        if q3 and t in tv:
            d1, w = tv[t]; rel = round(w - vniW, 1)
            if yoy is not None and yoy >= 0.25 and (rel <= -5 or d1 <= -4): rk, rl = "sell", "⚠️ Lãi tăng nhưng giá bị bán theo tin"
            elif yoy is not None and yoy >= 0.25 and rel >= 2: rk, rl = "ok", "🟢 Giá xác nhận"
            elif ep == -1 and rel >= 2: rk, rl = "ignore", "🟡 Giá bỏ qua tin xấu"
            elif ep == -1 and rel <= -2: rk, rl = "down", "🔴 Giá phản ánh tin xấu"
            else: rk, rl = "flat", "⚪ Chưa phản ứng rõ"
            react = dict(d1=d1, w=w, rel=rel, k=rk, lbl=rl)
        adj = ep if q3 else 0
        out[t] = dict(q=lb(L), qp=lb(L-1), qb=lb(L-4), q3=q3, bank=bank, np=n, npB=nb, npQ=npq,
                      rev=v(L, "rev"), yoy=yoy, qoq=qoq, ryoy=ryoy, rqoq=rqoq, prev=prev,
                      ttm=T, ttmB=TB, tyoy=tyoy, accel=accel, ep=ep, lab=lab, adj=adj, react=react,
                      series=[v(i, "np") for i in range(L-4, L+1)], sq=[lb(i) for i in range(L-4, L+1)],
                      score=(2 if q3 else 0) + ep * 3 + (1 if accel else 0) + max(-2, min(2, yoy or 0)))
    return out, vniW
