"""Kéo catalyst: gom kết quả FinLens news_get_for_stock từ log phiên hiện tại → raw_add2/new.json (news của các mã mới/chỉ kỹ thuật).
Chạy:  python3 pipeline/news_ingest.py [log.jsonl]   (mặc định: log mới nhất trong ~/.claude/projects)"""
import glob, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)) + "/"
log = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True), key=os.path.getmtime)[-1]
uses, res = {}, {}
def walk(x):
    if isinstance(x, dict):
        if x.get("type") == "tool_use" and "id" in x: uses[x["id"]] = x.get("name") or ""
        if x.get("type") == "tool_result" and "tool_use_id" in x:
            c = x.get("content")
            if isinstance(c, list): c = "".join(b.get("text", "") for b in c if isinstance(b, dict))
            res[x["tool_use_id"]] = c
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
for l in open(log, encoding="utf-8"):
    try: walk(json.loads(l))
    except Exception: pass
got = {}
for i, nm in uses.items():
    if nm.endswith("news_get_for_stock") and isinstance(res.get(i), str):
        try: d = json.loads(res[i])
        except Exception: continue
        if d.get("ticker") and "sentiment" in d: got[d["ticker"]] = d
new = json.load(open(H + "raw_add2/new.json")); TO = set(json.load(open(H + "conf/tech_only.json")))
done = []
for t, d in got.items():
    if t not in new: continue
    s = d["sentiment"]; n = s["n_articles"]; items = d.get("items") or []
    if n == 0 or not items:
        new[t]["news"] = dict(n=0, score=0.0, sent="neutral", title="Không có tin riêng của mã trong 30 ngày",
                              summary="FinLens không ghi nhận bài nào riêng cho mã trong 30 ngày gần nhất (kéo 31/10). Chưa có catalyst.",
                              date="2026-10-31", source="—", direct=0)
        done.append(t); continue
    best = max(items, key=lambda x: (x.get("importance", 0), x["published_at"]))
    w = s.get("weighted_score") or 0
    sent = "positive" if w >= 0.15 else "negative" if w <= -0.15 else "neutral"
    rel = next((x["relevance"] for x in best.get("tickers", []) if x["symbol"] == t), 0.7)
    summ = best["summary"]
    if len(summ) > 420: summ = summ[:417].rsplit(" ", 1)[0] + "…"
    summ += f" {n} tin/30 ngày: {s['n_positive']} tích cực, {s['n_negative']} tiêu cực."
    new[t]["news"] = dict(n=n, score=round(w, 3), sent=sent, title=best["title"], summary=summ,
                          date=best["published_at"], source=best["source"], direct=rel)
    done.append(t)
json.dump(new, open(H + "raw_add2/new.json", "w"), ensure_ascii=False)
print(len(done), "mã có catalyst mới:", " ".join(sorted(done)))
print("chưa có kết quả:", " ".join(sorted(t for t in TO if t in new and t not in got)))
