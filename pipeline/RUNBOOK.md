# Pipeline báo cáo VN W-D-H4 — sổ tay chạy

Mọi lệnh chạy từ gốc repo `bachtranprivate2025-droid.github.io`. Kết quả cuối: `index.html` (GitHub Pages).

## Ba nhịp cập nhật

| Nhịp | Khi nào | Kéo gì | Số lệnh tool (≈130 mã) |
|---|---|---|---|
| Hằng ngày | Thứ 2–6, sau 18h30 | Giá, KL/RVOL, RS vs VN30, khối ngoại, tự doanh, quote ETF/hàng hóa | TradingView 4 · FinLens flows 12 · FinLens nến cho mã RVOL ≥ 1,4× (thường 10–40) |
| Hàng tuần | Thứ 6 sau phiên (hoặc cuối tuần) | F/cờ đỏ BCTC, TCBS rating, SSI FA, quỹ, nội bộ, giá mục tiêu CTCK, tin/catalyst, RS rating, ngành ICB4, Fialda rotation | như bản đầy đủ cũ |
| Theo quý | Mùa BCTC: tháng 1, 4, 7, 10 + nửa đầu tháng kế tiếp | KQKD quý (TCBS income statement) | chỉ mã chưa có số quý mới |

## Nhịp hằng ngày (prompt cho scheduled task)

1. `git pull`.
2. TradingView `mcp-tv-get-symbol-data-batch`, columns `["close","volume","Perf.W","Perf.1M","Perf.3M","Perf.6M"]`,
   3 lệnh × 50 mã. Danh sách `EXCHANGE:TICKER` in bằng: `python3 pipeline/symbols.py` (lô cuối có thêm `HOSE:VNINDEX`, `HOSE:VN30`).
3. TradingView batch ETF/hàng hóa: symbols = `conf/syms.json["syms"]`, columns `["close","SMA20","SMA50","Perf.1M","change","description"]` (1 lệnh).
4. FinLens `flows_top_net` days=1 limit=30: flow_type foreign và proprietary × direction buy/sell × exchange HOSE/HNX/UPCOM (12 lệnh).
   Nếu note báo tự doanh "CHƯA gồm phiên" hôm nay thì vẫn chạy tiếp — báo cáo ghi rõ TD tới phiên trước.
5. `python3 pipeline/extract.py <YYYY-MM-DD>` rồi `python3 pipeline/ingest.py pipeline/inbox/<YYYY-MM-DD>.json`.
6. Dòng "CẦN KIỂM KL FinLens" liệt kê mã → gọi FinLens `stocks_get_price_history` ticker=<mã> limit=2 cho từng mã
   (KL TradingView gồm thỏa thuận; FinLens là KL khớp lệnh). Sau đó chạy lại bước 5 với tag `<YYYY-MM-DD>b`.
7. `python3 pipeline/build.py && cp pipeline/out/report.html index.html`.
8. Kiểm: mở bằng Playwright, không lỗi JS; commit "Cập nhật ngày <dd/mm>" và push.
9. Báo anh: số mã A+/A/gần A, mã đổi hạng, mã RVOL nổ, ghi chú nếu TD chưa có phiên mới.

## Nhịp hàng tuần

Chạy lại các bước kéo đầy đủ như bản 26–28/10 (signals_screen RS, quality_scan F, TCBS getGeneralRating, SSI FA,
fund_stock_ownership, insider, research consensus, news, market_sector_strength + chỉ số ngành ICB4, Fialda L2 qua browser),
ghi vào các file `raw_add2/`, `raw2610_add2/`, `fialda/l2rot.json`, rồi sửa ngày trong `conf/weekly.json`.

Lịch sự kiện (cột KQKD): FinLens `dividends_upcoming` symbols = toàn bộ `lists121.json`, days_ahead=120, limit=50 (1 lệnh) +
FinLens `news_search` event_type=dividend, news_type=company_specific, days=14, limit=50 để bắt mã FinLens dividends còn thiếu
(thêm tay vào `EXTRA` trong `events.py`, xóa khi FinLens đã có). Chạy `extract.py <tag>` rồi `events.py pipeline/inbox/<tag>.json`.
Hạn BCTC quý sửa trong `conf/weekly.json` → `bctc` khi sang mùa mới.
Sau đó chạy nhịp hằng ngày.

## Nhịp quý

Trong mùa BCTC: TCBS `getIncomeStatementForBank/NonBank` cho mã chưa có quý mới → `q3/tcbs_raw.json`; sửa `earn` trong `conf/weekly.json`.

## Thêm mã mới

Thêm vào `lists121.json` + các file tuần (như stage4 cũ). Cho store: FinLens `stocks_get_price_history` limit=40 +
`flows_get_stock_flow` days=10, rồi extract/ingest (ingest tự nhận nến lịch sử của mã mới).

## Giới hạn đã biết

- flows_top_net chỉ trả top 30 mỗi chiều mỗi sàn; mã ngoài top coi như ≈ 0 (sai số nhỏ hơn mã thứ 30, thường < 3 tỷ HOSE).
- Mã không qua kiểm FinLens dùng KL TradingView (có thể gồm thỏa thuận nhỏ).
- 1M/3M theo Perf TradingView (tháng lịch), không đúng 21/63 phiên.
- So sánh mã với ngành ICB4 (1D/1W) để trống khi số ngành là bản tuần.
