"""In 3 lô symbol TradingView (50 mã/lô) cho danh sách hiện tại."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)) + "/"
EX = json.load(open(H + "conf/exchange.json"))
s = [EX[t] + ":" + t for t in sorted(json.load(open(H + "lists121.json")))]
s += ["HOSE:VNINDEX", "HOSE:VN30"]
for i in range(0, len(s), 50):
    print(json.dumps(s[i:i + 50]))
