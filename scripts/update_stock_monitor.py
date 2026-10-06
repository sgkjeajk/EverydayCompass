#!/usr/bin/env python3
import json,urllib.request,datetime,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];UA={'User-Agent':'Mozilla/5.0 EverydayCompass/1.0'}
def get(t,r,i):
 req=urllib.request.Request(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?range={r}&interval={i}&events=history&includeAdjustedClose=true',headers=UA)
 with urllib.request.urlopen(req,timeout=25) as x:return json.load(x)['chart']['result'][0]
def n(v):return float(v) if v is not None else None
def main():
 cfg=json.loads((ROOT/'data/stock-tickers.json').read_text())['instruments'];out=[]
 for x in cfg:
  if x.get('enabled',True) is False:continue
  t=x['ticker'];hist=get(t,'max','1d');q=hist['indicators']['quote'][0];cut=int(datetime.datetime(2000,1,1,tzinfo=datetime.timezone.utc).timestamp());ath=max(n(h) for ts,h in zip(hist['timestamp'],q['high']) if ts>=cut and h is not None)
  recent=get(t,'5d','1d');m=recent['meta'];rc=[n(v) for v in recent['indicators']['quote'][0]['close'] if v is not None];cur=n(m.get('regularMarketPrice')) or rc[-1];prev=n(m.get('chartPreviousClose') or m.get('previousClose')) or (rc[-2] if len(rc)>1 else None);pp=rc[-3] if len(rc)>=3 else None
  out.append({**x,'prev_close':prev,'prev_day_pct_change':((prev/pp)-1)*100 if prev and pp else None,'current_price':cur,'current_pct_change':((cur/prev)-1)*100 if cur and prev else None,'ath':ath,'drawdown_pct':((cur/ath)-1)*100 if cur and ath else None});time.sleep(.15)
 (ROOT/'data/stock-monitor.json').write_text(json.dumps({'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),'source':'Yahoo Finance chart data','ath_since':'2000-01-01','instruments':out},indent=2)+'\n')
if __name__=='__main__':main()
