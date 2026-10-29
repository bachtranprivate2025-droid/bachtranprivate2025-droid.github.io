import json,sys
d=json.load(open(sys.argv[1]))["data"]
out={k:[v["close"],v["SMA20"],v["SMA50"],v["Perf.1M"],v["change"],v["description"]] for k,v in d.items()}
json.dump({"asof":"TradingView trưa 28/10/2026 (phiên Mỹ/EU chốt 27/10, châu Á trong phiên 28/10)","spy1m":out["AMEX:SPY"][3],"q":out},open(sys.argv[2],"w"),ensure_ascii=False)
print(len(out))
