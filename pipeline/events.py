"""Nhịp tuần: lịch sự kiện (cổ tức/quyền) -> conf/events.json.
python3 pipeline/events.py pipeline/inbox/<tag>.json
Nguồn: FinLens dividends_upcoming (symbols = danh sách báo cáo, days_ahead=120) + bổ sung tay ở EXTRA
(FinLens dividends chưa có, lấy từ tin FinLens news_search event_type=dividend)."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)) + "/"
IN = json.load(open(sys.argv[1]))
EXTRA = [  # cập nhật tay mỗi tuần từ tin; xóa khi FinLens đã có
    dict(t="VNM", ex="2026-11-10", pay="2026-11-26", kind="cash", terms="2.500đ/CP", yld=4.33, title="Tạm ứng cổ tức đợt 1/2026 bằng tiền 25% (ĐKCC 11/11)", src="Tin Vietstock 29/10"),
    dict(t="GVR", ex=None, pay="2026-12-10", kind="cash", terms="400đ/CP", yld=1.25, title="Cổ tức năm 2025 bằng tiền 4% (chưa rõ ngày chốt)", src="Tin Vietstock 28/10"),
]
seen, items = set(), []
for x in IN.get("dividends", []) + EXTRA:
    k = (x["t"], x["ex"], x["title"])
    if k in seen: continue
    seen.add(k); items.append({k2: v for k2, v in x.items() if k2 != "asof"})
asof = max([x.get("asof") or "" for x in IN.get("dividends", [])] or [""])
json.dump({"asof": asof, "items": items}, open(H + "conf/events.json", "w"), ensure_ascii=False, indent=1)
print(asof, len(items), sorted({x["t"] for x in items}))
