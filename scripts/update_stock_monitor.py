#!/usr/bin/env python3
import json, urllib.request, datetime, time
from pathlib import Path
SYMBOLS={'SPY':'SPDR S&P 500 ETF Trust','VOO':'Vanguard S&P 500 ETF','QQQ':'Invesco QQQ Trust','QQQM':'Invesco NASDAQ 100 ETF','URTH':'iShares MSCI World ETF','AAPL':'Apple','MSFT':'Microsoft','NVDA':'NVIDIA','AMZN':'Amazon','GOOGL':'Alphabet Class A','META':'Meta Platforms','TSLA':'Tesla'}
UA={'User-Agent':'Mozilla/5.0 EverydayCompass/1.0'}
def get(ticker,range_,interval):
 u=f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={range_}&interval={interval}&events=history&includeAdjustedClose=true'
 req=urllib.request.Request(u,headers=UA)
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)['chart']['result'][0]
def n(v):return float(v) if v is not None else None
def main():
 out=[]
 for ticker,name in SYMBOLS.items():
  hist=get(ticker,'max','1d'); q=hist['indicators']['quote'][0]; ts=hist['timestamp']; highs=q['high']; closes=q['close']
  cutoff=int(datetime.datetime(2000,1,1,tzinfo=datetime.timezone.utc).timestamp()); ath=max(n(h) for t,h in zip(ts,highs) if t>=cutoff and h is not None)
  recent=get(ticker,'5d','1d'); meta=recent['meta']; rq=recent['indicators']['quote'][0]; rc=[n(x) for x in rq['close'] if x is not None]
  current=n(meta.get('regularMarketPrice')) or rc[-1]; prev=n(meta.get('chartPreviousClose') or meta.get('previousClose'))
  if prev is None and len(rc)>1:prev=rc[-2]
  prevprev=rc[-3] if len(rc)>=3 else None
  prevchg=((prev/prevprev)-1)*100 if prev and prevprev else None; currentchg=((current/prev)-1)*100 if current and prev else None; draw=((current/ath)-1)*100 if current and ath else None
  out.append({'ticker':ticker,'name':name,'prev_close':prev,'prev_day_pct_change':prevchg,'current_price':current,'current_pct_change':currentchg,'ath':ath,'drawdown_pct':draw})
  time.sleep(.15)
 payload={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),'source':'Yahoo Finance chart data','ath_since':'2000-01-01','instruments':out}
 p=Path(__file__).resolve().parents[1]/'data'/'stock-monitor.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(payload,indent=2)+'\n')
if __name__=='__main__':main()
