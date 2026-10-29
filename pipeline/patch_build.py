"""Một lần: chuyển build2810q3.py thành build.py chạy theo store hằng ngày (đã chạy, giữ lại để tra)."""
import re
P = "/home/claude/bachtranprivate2025-droid.github.io/pipeline/build.py"
s = open(P, encoding="utf-8").read()
def sub(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:90]); s = s.replace(old, new)

sub('RUN = "/home/claude/run85/"', 'import os, datetime\nRUN = os.path.dirname(os.path.abspath(__file__)) + "/"')
sub('SRC = "/tmp/claude-0/-home-claude/a2c511d1-6981-5396-8518-8d161b3b1a1b/scratchpad/template_unzip/VN_3_PORTFOLIOS_2026-10-23.html"',
    'SRC = RUN + "template/VN_3_PORTFOLIOS_2026-10-23.html"')
sub('OUT = RUN + "VN_WDH4_129MA_2026-10-29.html"', 'OUT = RUN + "out/report.html"')

DAILY = r'''
# ======== NHỊP HẰNG NGÀY: giá, KL/RVOL, NN/TD lấy từ store/daily.json ========
ST = json.load(open(RUN + "store/daily.json"))
SD = ST["dates"]; ASOF = SD[-1]; NN_ASOF = ST["nnAsof"]; TD_ASOF = ST["tdAsof"]
WK = json.load(open(RUN + "conf/weekly.json"))          # mốc các nhóm cập nhật tuần / quý
FD10 = [d for d in SD if d <= NN_ASOF][-10:][::-1]
FLOW_DATES = FD10
dm = lambda iso: iso[8:10] + "/" + iso[5:7]
for t in FLOW:
    c = ST["close"][t]
    nn_ = [round(ST["nn"][t].get(d, 0.0), 2) for d in FD10]
    td_ = [round(ST["td"][t].get(d, 0.0), 2) for d in FD10]   # phiên TD chưa có số = 0
    FLOW[t].update(nn=nn_, td=td_, smart=[round(a + b, 2) for a, b in zip(nn_, td_)],
                   closes=[c[SD[-1]], c[SD[-2]], c[SD[-6]]])
    pf = ST["tv"]["perf"].get(t) or {}
    c0 = c[SD[-1]]
    PX[t] = (c0 / (1 + pf["m1"] / 100) if pf.get("m1") is not None else PX[t][0],
             c0 / (1 + pf["m3"] / 100) if pf.get("m3") is not None else PX[t][1])
'''
sub("TC = {}\nfor l in rd(\"tcbs\"):", DAILY + "\nTC = {}\nfor l in rd(\"tcbs\"):")

# so sánh mã với ngành: ngành ICB4 là số tuần, khác mốc với giá hằng ngày -> bỏ chênh lệch
sub('''    r["icbComparison"] = {"asof": "2026-10-26", "dayBase": "2026-10-23", "weekBase": "2026-10-19",
                          "stock": stock, "sector": {"d1": sec["d1"], "w1": sec["w1"]},
                          "relative": {k: (None if sec[k] is None else stock[k] - sec[k]) for k in ("d1", "w1")}}''',
    '''    same = ASOF == WK["icb"]
    r["icbComparison"] = {"asof": ASOF, "dayBase": SD[-2], "weekBase": SD[-6], "sectorAsof": WK["icb"],
                          "stock": stock, "sector": {"d1": sec["d1"], "w1": sec["w1"]},
                          "relative": {k: (None if (sec[k] is None or not same) else stock[k] - sec[k]) for k in ("d1", "w1")}}''')
sub('"signal": fl["signal"], "flowAsof": "2026-10-27"})', '"signal": fl["signal"], "flowAsof": NN_ASOF, "tdAsof": TD_ASOF})')
sub('meta["reportDate"] = "2026-10-26"; meta["revisionDate"] = "2026-10-27"',
    'meta["reportDate"] = ASOF; meta["revisionDate"] = datetime.date.today().isoformat(); meta["tdAsof"] = TD_ASOF; meta["weekly"] = WK')

# RVOL + RS vs VN30 từ store
old_vol = s[s.index("VOL = {}\nfor l in open(RUN + \"raw2810/vol121.txt\"):"):s.index("assert all(len(v) == 32 for v in VOL.values())")]
s = s.replace(old_vol, '''SDD = SD[::-1]
VOL = {t: [ST["vol"][t][d] for d in SDD[:32]] for t in TICKERS}
''')
sub('''CLS = {}
for l in open(RUN + "raw2810/cls121.txt"):
    p = l.split(); CLS[p[0]] = [float(x) for x in p[1:]]''',
    '''CLS = {t: [ST["close"][t][d] for d in SDD[:21]] for t in TICKERS + ["VN30"]}''')

# ---- nhãn ngày trong HTML/JS: dùng token, thay ở cuối ----
sub('"<title>VN W-D-H4 — 121 mã 27/10/2026</title>"', '"<title>VN W-D-H4 — "+str(len(rows))+" mã @D0Y@</title>"')
sub('"<b>Giá & cơ bản chốt phiên 26/10/2026 · NN/TD + RVOL chốt phiên 27/10/2026 (cập nhật tối 27/10)</b>"',
    '"<b>Giá, KL/RVOL, RS vs VN30, khối ngoại chốt phiên @D0Y@ · tự doanh tới phiên @TD@ · nhóm tuần chốt @WK@ · BCTC quý: @Q@</b>"')
i0 = s.index('    "Tối 27/10: thêm cột RS vs VN30 10 phiên')
i1 = s.index('nên không vào allocation.")', i0) + len('nên không vào allocation.")')
s = s[:i0] + '    NOTES)' + s[i1:]
sub('''    "Báo cáo nghiên cứu dữ liệu phiên 26/10/2026 (NN/TD + RVOL phiên 27/10) · cập nhật tối 27/10/2026 theo template v2 · đủ 121 mã: 3 Stage list + VN RVOL (bản 28/10, 21 mã) + RVOL TEST vni (bản 26/10) + RVOL 25/10 + 7 mã anh thêm 27/10 (LDG, VC7, QCG, CTI, NAG, CMX, CII).")''',
    '''    "Báo cáo dữ liệu phiên @D0Y@ · "+str(len(rows))+" mã: 3 Stage list + VN RVOL + RVOL TEST vni + RVOL 25/10 + mã anh thêm.")''')
sub('rep("09/10 → 22/10 · 10 phiên", "14/10 → 27/10 · 10 phiên")', 'rep("09/10 → 22/10 · 10 phiên", "@F9@ → @NN@ · 10 phiên")')
sub("cộng dồn từ 13/10; chấm xanh", "cộng dồn từ @RS0@; chấm xanh")
sub("'</span> <span class=\"note\">10 phiên</span></div><div class=\"note\">27/10: <span", "'</span> <span class=\"note\">10 phiên</span></div><div class=\"note\">@D0@: <span")
sub("(FinLens). KL 27/10: '", "(FinLens khớp lệnh; TradingView nếu chưa kiểm). KL @D0@: '")
sub("'×</span> <span class=\"note\">27/10</span></div>", "'×</span> <span class=\"note\">@D0@</span></div>")
sub("Báo cáo 4 watchlist · 26/10/2026</h1>", "Báo cáo 4 watchlist · @D0Y@</h1>")
sub('RVOL phiên 27/10 cao → thấp', 'RVOL phiên @D0@ cao → thấp')
sub('RS vs VN30 phiên 27/10</option>', 'RS vs VN30 phiên @D0@</option>')
sub('RS phiên 27/10 → số phiên thắng', 'RS phiên @D0@ → số phiên thắng')
sub('rs30_1:"↓ 27/10"', 'rs30_1:"↓ @D0@"')
sub('" (phiên 27/10 bán mạnh)"', '" (phiên @NN@ bán mạnh)"')
sub('popDay=["27/10","26/10","23/10"][pk]', 'popDay=["@D0@","@D1@","@D2@"][pk]')
sub("<b>Setup TA phiên 27/10</b>", "<b>Setup TA phiên @D0@</b>")
for a, b in [("Số đi kèm: RVOL phiên 26/10", "Số đi kèm: RVOL phiên cuối"),
             ("10 cột từ 14/10 (trái) đến 27/10 (phải)", "10 cột từ @F9@ (trái) đến @D0@ (phải)"),
             ("21 phiên 29/09–27/10", "21 phiên gần nhất tới @D0@"),
             ("từ 13/10 đến 27/10", "từ @RS0@ đến @D0@"),
             ("chênh lệch phiên 27/10", "chênh lệch phiên cuối"),
             ("Giá trong cột này chốt 27/10, khác giá/hiệu suất ở các cột khác (chốt 26/10).", "Giá cùng mốc với các cột giá/hiệu suất."),
             ("Hạng setup TA (27/10/2026)", "Hạng setup TA (@D0Y@)")]:
    sub(a, b, 2 if a == "21 phiên 29/09–27/10" else 1)

NOTES = r'''
dmy4 = lambda iso: iso[8:10] + "/" + iso[5:7] + "/" + iso[:4]
NOTES = ("Nhịp cập nhật: HẰNG NGÀY (sau 18h30) kéo giá, khối lượng/RVOL, RS vs VN30, khối ngoại, tự doanh và quote ETF/hàng hóa theo lô — TradingView 3 lệnh cho cả danh sách (50 mã/lệnh), FinLens flows_top_net 12 lệnh (NN, TD × mua/bán × 3 sàn, top 30 mỗi chiều; mã ngoài top coi như ≈ 0), FinLens price history chỉ cho các mã RVOL ≥ 1,4× để lấy KL khớp lệnh (KL TradingView gồm cả thỏa thuận). "
         "HÀNG TUẦN (thứ Sáu): F/cờ đỏ BCTC, TCBS rating, SSI FA, quỹ, nội bộ, giá mục tiêu CTCK, catalyst/tin, RS rating FinLens, sức mạnh và hiệu suất ngành ICB4, rotation ngành cấp 2 Fialda — bản hiện tại chốt " + dmy4(WK["fund"]) + " (ngành ICB4 " + dmy4(WK["icb"]) + ", Fialda " + dmy4(WK["fialda"]) + "). "
         "THEO QUÝ: KQKD quý chỉ kéo trong mùa BCTC (tháng 1, 4, 7, 10 và nửa đầu tháng kế tiếp), mỗi lần chỉ các mã chưa có số quý mới; bản hiện tại " + WK["earn"] + ". "
         "Phiên " + dmy4(ASOF) + ": khối ngoại chốt " + dmy4(NN_ASOF) + ", tự doanh chốt " + dmy4(TD_ASOF) + (" (FinLens chưa có số tự doanh phiên mới nhất, tạm tính 0)" if TD_ASOF < NN_ASOF else "") + ". "
         + ("Giá đã điều chỉnh theo sự kiện quyền: " + ", ".join(f"{k} ×{v}" for k, v in ST.get("adj", {}).items()) + ". " if ST.get("adj") else "")
         + "So sánh mã với ngành ICB4 (1D/1W) để trống khi số ngành khác mốc với giá. 1M/3M lấy Perf TradingView (theo tháng lịch).")
'''
sub("def rep(old, new, count=1):", NOTES + "\ndef rep(old, new, count=1):")

TOK = r'''
dmy4 = lambda iso: iso[8:10] + "/" + iso[5:7] + "/" + iso[:4]
for k, v in {"@D0Y@": dmy4(ASOF), "@D0@": dm(SD[-1]), "@D1@": dm(SD[-2]), "@D2@": dm(SD[-3]), "@NN@": dm(NN_ASOF),
             "@TD@": dm(TD_ASOF), "@F9@": dm(FD10[-1]), "@RS0@": dm(SD[-11]), "@WK@": dm(WK["fund"]), "@Q@": WK["earn"]}.items():
    html = html.replace(k, v)
os.makedirs(RUN + "out", exist_ok=True)
'''
sub('open(OUT, "w", encoding="utf-8").write(html)', TOK + 'open(OUT, "w", encoding="utf-8").write(html)')
sub('json.dump(data, open(RUN + "data121_2710.json", "w"), ensure_ascii=False)', 'json.dump(data, open(RUN + "out/data.json", "w"), ensure_ascii=False)')
open(P, "w", encoding="utf-8").write(s)
print("ok")
