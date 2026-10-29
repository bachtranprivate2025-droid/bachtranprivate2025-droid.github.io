C = [
("Hạng setup TA (cột đầu bảng)", [
 "<b>A+</b>: RS, DT, RV, CB đều 2/2 và NG ≥ 1",
 "<b>A</b>: RS, DT, RV đều 2/2 (CB, NG chưa đủ)",
 "<b>B</b>: 4 trụ chính ≥ 4/8 và RS ≥ 1 · <b>C</b>: còn lại",
 "<b>x/10</b> = 4 trụ chính (mỗi trụ 0–2) + NG (0–2)",
 "<b>⭐</b> = NG 2/2, ngành đồng thuận mạnh",
 "<b>Gần A, thiếu X</b> = hạng B thiếu đúng 1 trong RS / DT / RV",
 "⏳ Nền giá + nến H4 anh tự xác nhận trên chart"]),
("RS · sức mạnh giá", [
 "<b>2</b>: đường RS so VN30 trên MA20, thắng VN30 10 phiên, 3 tháng ≤ 15%, và RS rating ≥ 80 hoặc RS lập đỉnh 21 phiên",
 "<b>0</b>: 3 tháng đã tăng > 20% (chạy xa), hoặc dưới MA20 và thua VN30",
 "<b>1</b>: còn lại",
 "Cột RS vs VN30: xanh = vượt VN30, đỏ = thua; nhãn <i>RS đỉnh mới trước giá</i> là tín hiệu sớm"]),
("DT · dòng tiền 10 phiên", [
 "Chỉ tính <b>NN</b> (khối ngoại) + <b>TD</b> (tự doanh); không cộng tổ chức trong nước vì trùng số TD",
 "<b>2</b>: cả NN và TD mua ròng, hoặc ròng ≥ 0,3% GTGD 10 phiên mà bên còn lại chỉ âm nhẹ",
 "<b>0</b>: NN + TD bán ròng · <b>1</b>: còn lại"]),
("RV · RVOL (KL phiên ÷ TB 20 phiên)", [
 "<b>2</b>: nền 7 phiên trước < 0,8× rồi nổ ≥ 1,5× trong 3 phiên gần nhất (hoặc tích lũy: ≥ 3 phiên ≥ 1,5×, KL 5 phiên +15%, 3 tháng ≤ 15%, smart money mua)",
 "<b>0</b>: nổ ≥ 2× nhưng smart money bán đúng phiên đó, hoặc giá đã chạy > 20%",
 "Màu cột: <span class=\"lgc\" style=\"background:#5a5a5a\"></span>&lt; 1× · <span class=\"lgc\" style=\"background:var(--blue)\"></span>1–1,5× · <span class=\"lgc\" style=\"background:var(--yellow)\"></span>1,5–2× · <span class=\"lgc\" style=\"background:var(--green)\"></span>≥ 2×"]),
("CB · catalyst + cơ bản", [
 "<b>Điểm cơ bản</b> = trung bình F (FinLens, 0–100) và TCBS × 20",
 "<b>2</b>: điểm ≥ 65, F không bị cap, và có tin mạnh trong 30 ngày",
 "<b>1</b>: điểm tốt hoặc có tin tốt · <b>0</b>: tin xấu hoặc điểm yếu",
 "<b>KQKD quý</b> (chỉ mã đã ra Q3): <b>+1</b> khi LNST YoY ≥ 25% và tăng tốc so với YoY quý trước · <b>−1</b> khi giảm ≥ 25% hoặc lỗ",
 "⚠️ <i>Bán theo tin</i> = lãi tăng nhưng giá yếu hơn VNINDEX ≥ 5% trong tuần hoặc giảm ≥ 4% một phiên (chỉ cảnh báo)"]),
("NG · đồng thuận ngành", [
 "Tổng 4 nguồn: rotation ngành cấp 2 Fialda (−1/0/+1) + ngành ICB4 FinLens (🟢 +1 / 🟡 0 / 🔴 −1) + ETF Mỹ + hàng hóa",
 "Hàng hóa là chi phí đầu vào thì tính ngược (giá lên = bất lợi)",
 "<b>2</b>: tổng ≥ +2 và ngành cấp 2 không ngược · <b>0</b>: tổng ≤ −1 hoặc cấp 2 lẫn ICB4 cùng xấu · <b>1</b>: còn lại",
 "Pha rotation: 🟢 Dẫn dắt · 🔵 Cải thiện · 🟠 Suy yếu · 🔴 Tụt hậu; tiền vào / ra = động lượng ≥ +25 / ≤ −25"]),
("Thanh khoản · rổ chỉ số", [
 "<b>Tầng 1</b>: VN30, GTGD trung vị 20 phiên ≥ 50 tỷ, ổn định (CV ≤ 0,8)",
 "<b>Tầng 2</b>: VN100, ≥ 20 tỷ, ổn định · <b>Tầng 3</b>: ≥ 10 tỷ · <b>Tầng 4</b>: còn lại",
 "Cùng hạng setup thì tầng 1 → 4 xếp trước"]),
("Ký hiệu & viết tắt", [
 "🟢 tốt / thuận · 🟡 trung tính / chưa đủ · 🔴 xấu / ngược · ⚪ không có dữ liệu / không đáng kể · ⚠️ cần đọc kỹ",
 "<b>F</b>: chất lượng BCTC FinLens 0–100; <b>cap</b> = bị giới hạn trần do cờ đỏ (F = 0 là bị cap nặng)",
 "<b>TCBS</b>: General Rating 1–5 · <b>SSI FA</b>: 0–100, chỉ tham khảo",
 "<b>Quỹ GOM / XẢ</b>: số quỹ tăng vs giảm tỷ trọng · <b>Nội bộ</b>: mua / bán ròng 12 tháng > 10 tỷ",
 "<b>YoY</b> so cùng kỳ · <b>QoQ</b> so quý trước · <b>TTM</b> 4 quý cộng dồn"]),
]
LEGEND = ('<details class="legend" open><summary><b>Chú giải (legend)</b> <span class="note">· bấm để thu gọn</span></summary><div class="lgrid">'
          + "".join('<div class="lgcard"><div class="lgh">' + h + '</div><ul>' + "".join("<li>" + x + "</li>" for x in items) + "</ul></div>" for h, items in C)
          + "</div></details>")
LCSS = (".legend{margin:14px 0 6px;border:1px solid #333;border-radius:6px;background:#1b1b1b;padding:8px 12px}.legend summary{cursor:pointer;font-size:14px}"
        ".lgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;margin-top:8px}"
        ".lgcard{border:1px solid #2c2c2c;border-radius:5px;padding:8px 10px;background:#202020}.lgh{font-weight:700;margin-bottom:4px;color:#fff}"
        ".lgcard ul{margin:0;padding-left:16px;font-size:12px;line-height:1.45;color:#d6d6d6}.lgcard li{margin:2px 0}"
        ".lgc{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 3px -1px 0}")
assert "'" not in LEGEND and "\n" not in LEGEND
