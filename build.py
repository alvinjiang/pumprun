#!/usr/bin/env python3
"""Build defihodler web client from data files + templates."""
import json, base64, os, subprocess, re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "design", "data")
WEB = os.path.join(ROOT, "web")

def load_data():
    with open(os.path.join(DATA, "basket_returns.bin"), "rb") as f:
        basket_b64 = base64.b64encode(f.read()).decode()
    with open(os.path.join(DATA, "btcusdt.json")) as f:
        btc = json.dumps([[d["t"], float(d["c"])] for d in json.load(f)])
    with open(os.path.join(DATA, "index.json")) as f:
        coins = json.dumps(json.load(f))
    return basket_b64, btc, coins

def build_html():
    basket_b64, btc_data, coin_data = load_data()
    
    js = f"""var BTC={btc_data};
var BASKET=new Float32Array(Uint8Array.from(atob("{basket_b64}"),function(c){{return c.charCodeAt(0)}}).buffer);
var BTC_PRICE={{}},DATES=[];
for(var i=0;i<BTC.length;i++){{var d=new Date(BTC[i][0]),day=d.toISOString().slice(0,10);BTC_PRICE[day]=BTC[i][1];DATES.push(day)}}
var WIN=365,START=10000,DPS=8;var API=(function(){{var m=document.querySelector('meta[name="api-base"]');if(m&&m.content){{var u=m.content;while(u[u.length-1]==="/")u=u.slice(0,-1);return u}}return location.protocol.indexOf("http")===0?location.origin:""}})();
var FP=DATES.indexOf("2017-08-17"),MX=DATES.length-WIN-1;
var SEASONS=[{{name:"ICO Summer",s:"2017-01-01",e:"2017-12-31"}},{{name:"Crypto Winter",s:"2018-01-01",e:"2019-03-31"}},{{name:"Crypto Spring",s:"2019-04-01",e:"2019-09-30"}},{{name:"COVID Crash",s:"2020-03-01",e:"2020-04-30"}},{{name:"DeFi Summer",s:"2020-06-01",e:"2020-09-30"}},{{name:"Institutional Wave",s:"2020-10-01",e:"2021-03-31"}},{{name:"NFT Mania",s:"2021-01-01",e:"2021-04-30"}},{{name:"China Ban & Recovery",s:"2021-05-01",e:"2021-09-30"}},{{name:"Metaverse Rotation",s:"2021-10-01",e:"2022-01-31"}},{{name:"LUNA Collapse",s:"2022-05-01",e:"2022-06-30"}},{{name:"Crypto Winter II",s:"2022-06-01",e:"2023-01-31"}},{{name:"Banking Crisis",s:"2023-03-01",e:"2023-04-30"}},{{name:"ETF Era",s:"2024-01-01",e:"2024-06-30"}},{{name:"Meme Coin Spring",s:"2024-03-01",e:"2024-05-31"}},{{name:"Post-Halving Rally",s:"2024-10-01",e:"2025-01-31"}},{{name:"Quiet Bull",s:"2025-01-01",e:"2026-07-15"}}];
var TIERS=[[0,"Beef or Shrimp Ramen?"],[40,"Order yourself a 2010 Bitcoin Pizza."],[100,"You'll want a cold wallet for all that Bitcoin!"],[500,"Rimowa or Rama Works, depending on how active you are."],[1000,"Aeron or Embody?"],[5000,"Antminer or RTX GPU?"],[10000,"A decent APE NFT."],[20000,"Pepsi or Batman?"],[40000,"Fly your friends private for a Vegas whale experience."],[60000,"You'd still need to trade that Daytona in for a Royal Oak."],[100000,"Tesla for your BTC?"],[250000,"If only you had an allocation from RM..."],[350000,"Now Lambo."],[500000,"Not the U.S. Constitution \\u2014 you're a little short of the 2021 $43.2M price."]];
var G={{s:0,i:0,inBasket:true,running:false,phase:"count",done:false,screen:"lobby",btcQty:0,trades:0,speed:1,pos:new Uint8Array(WIN),altCum:0}};
var raf=null,acc=0,lt=0,btcS=[],altS=[],youS=[];"""

    js += """
function fmt$(v){return'$'+Math.round(v).toLocaleString()}
function ord(n){var s=['th','st','nd','rd'],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0])}
var EVENTS=[{date:"2017-09-04",text:"China bans ICOs, shuts exchanges"},{date:"2018-01-15",text:"Crypto crash begins — BTC from $19K to $6K"},{date:"2018-11-15",text:"Bitcoin Cash hash war (BCH vs BSV)"},{date:"2019-04-02",text:"Bitcoin surges past $5K — crypto spring"},{date:"2019-06-18",text:"Facebook announces Libra"},{date:"2020-03-12",text:"COVID crash — BTC to $3,800 in 24h"},{date:"2020-05-11",text:"Bitcoin Halving #3 (12.5 → 6.25 BTC)"},{date:"2020-08-15",text:"DeFi Summer peaks — yield farming mania"},{date:"2020-12-16",text:"BTC breaks $20K — institutional wave"},{date:"2021-02-08",text:"Tesla buys $1.5B Bitcoin"},{date:"2021-03-11",text:"Beeple NFT sells for $69.3M"},{date:"2021-04-14",text:"Coinbase IPO — BTC at $64K ATH"},{date:"2021-05-19",text:"China bans mining; Elon tweets; BTC crashes 40%"},{date:"2021-09-07",text:"El Salvador adopts BTC as legal tender"},{date:"2021-10-19",text:"ProShares BTC futures ETF (BITO) launches"},{date:"2021-11-10",text:"BTC ATH #2 at $67,500"},{date:"2022-05-09",text:"Terra/LUNA collapse — $40B erased"},{date:"2022-06-13",text:"3AC insolvent, Celsius halts withdrawals"},{date:"2022-09-15",text:"Ethereum Merge — PoW to PoS"},{date:"2022-11-11",text:"FTX collapses — $8B hole, SBF arrested"},{date:"2023-03-10",text:"Silvergate, SVB, Signature collapse — bank run"},{date:"2023-06-05",text:"SEC sues Binance & Coinbase"},{date:"2024-01-10",text:"BTC spot ETFs approved by SEC"},{date:"2024-03-15",text:"Meme coin spring: WIF, PEPE, BONK"},{date:"2024-04-19",text:"Bitcoin Halving #4 (6.25 → 3.125 BTC)"},{date:"2024-05-23",text:"Ethereum spot ETFs approved"},{date:"2024-11-06",text:"BTC breaks $100K post-election"},{date:"2025-01-20",text:"BTC ATH #3 above $110K"},{date:"2025-03-15",text:"US Strategic Bitcoin Reserve announced"},{date:"2025-10-15",text:"Crypto market cap exceeds $5 trillion"},{date:"2026-02-21",text:"Bybit hacked — $1.5B largest crypto theft"}];
function fmtPct(v){return(v>=0?'+':'')+v.toFixed(2)+'%'}

function showScreen(id){
  G.screen=id;
  document.querySelectorAll('.screen').forEach(function(s){s.classList.remove('on')});
  document.getElementById('scr-'+id).classList.add('on');
  if(id==='lobby') loadLobbyData();
}
function startGame(forcedS){
  var s=Number.isInteger(forcedS)?forcedS:FP+Math.floor(Math.random()*(MX-FP));
  if(s<FP)s=FP;if(s>MX)s=MX;
  G.s=s;G.i=0;G.inBasket=true;G.running=false;G.done=false;G.phase="count";
  G.trades=0;G.pos=new Uint8Array(WIN);G.altCum=0;
  G.btcQty=START/BTC_PRICE[DATES[G.s]];
  btcS=[0];altS=[0];youS=[0];
  showScreen('game');
  updateUI();drawChart();drawDayBar();
  var ov=document.getElementById('countdown'),num=document.getElementById('count-num');
  ov.style.display='flex';var c=3;num.textContent='3';
  var timer=setInterval(function(){
    c--;if(c>0){num.textContent=String(c)}
    else{clearInterval(timer);num.textContent='0';
      setTimeout(function(){ov.style.display='none';G.phase='live';G.running=true;lt=0;acc=0;raf=requestAnimationFrame(loop)},400)}
  },1000);
}

function step(){
  var date=DATES[G.s+G.i],ret=BASKET[G.s+G.i];
  if(G.inBasket&&!isNaN(ret))G.btcQty*=Math.exp(ret);
  G.pos[G.i]=G.inBasket?1:0;
  btcS.push((BTC_PRICE[date]/BTC_PRICE[DATES[G.s]]-1)*100);
  G.altCum+=(!isNaN(ret)?ret:0);
  altS.push((Math.exp(G.altCum)*BTC_PRICE[date]/BTC_PRICE[DATES[G.s]]-1)*100);
  var cr=0;for(var j=0;j<=G.i;j++){if(G.pos[j]===1){var r=BASKET[G.s+j];if(!isNaN(r))cr+=r}}
  youS.push((Math.exp(cr)*BTC_PRICE[date]/BTC_PRICE[DATES[G.s]]-1)*100);
  G.i++;if(G.i>=WIN)finishGame();
}

function loop(ts){
  if(!G.running)return;if(!lt)lt=ts;
  acc+=(ts-lt)/1000*DPS*G.speed;lt=ts;
  var n=Math.floor(acc);acc-=n;
  while(n-->0&&G.running&&!G.done)step();
  updateUI();drawChart();drawDayBar();
  if(!G.done)raf=requestAnimationFrame(loop);
}

var cv=document.getElementById('chart'),cx=cv.getContext('2d');
var yLo=-25,yHi=25;
function drawChart(){
  var W=cv.parentElement.clientWidth*2,H=1600;cv.width=W;cv.height=H;var dpr=2;
  cx.clearRect(0,0,W,H);if(btcS.length<2)return;
  // Compute range from CURRENT visible data only (not future projection)
  var allV=btcS.concat(altS).concat(youS);
  var dMn=Math.min.apply(null,allV),dMx=Math.max.apply(null,allV);
  // Expand range when any line approaches the edge (within 10% of range)
  var edge=yHi-yLo,loEdge=yLo+edge*.1,hiEdge=yHi-edge*.1;
  if(dMx>hiEdge)yHi=dMx+edge*.15;
  if(dMn<loEdge)yLo=dMn-edge*.15;
  var yMn=yLo,yMx=yHi;
  var pad={t:16*dpr,b:20*dpr,l:52*dpr,r:16*dpr};
  var pw=W-pad.l-pad.r,ph=H-pad.t-pad.b;
  var Yf=function(v){return pad.t+ph-((v-yMn)/(yMx-yMn))*ph};

  // Position background bands
  var bs=0,st=G.pos[0]===1;
  for(var si=1;si<=G.i;si++){
    if(si===G.i||G.pos[si]!==(st?1:0)){
      cx.fillStyle=st?'rgba(0,188,0,.08)':'rgba(193,7,6,.08)';
      cx.fillRect(pad.l+pw*bs/WIN,pad.t,pw*(si-bs)/WIN,ph);
      bs=si;if(si<G.i)st=G.pos[si]===1;
    }
  }
  // Future grey
  if(G.i<WIN){cx.fillStyle='rgba(255,255,255,.012)';cx.fillRect(pad.l+pw*G.i/WIN,pad.t,pw*(WIN-G.i)/WIN,ph)}
  // Grid
  cx.strokeStyle='#111116';cx.lineWidth=1;
  for(var i2=0;i2<=5;i2++){cx.beginPath();cx.moveTo(pad.l,pad.t+ph*i2/5);cx.lineTo(W-pad.r,pad.t+ph*i2/5);cx.stroke()}
  for(var i3=0;i3<=12;i3++){cx.beginPath();cx.moveTo(pad.l+pw*i3/12,pad.t);cx.lineTo(pad.l+pw*i3/12,H-pad.b);cx.stroke()}
  // Baseline
  var zy=Yf(0);
  cx.strokeStyle='rgba(255,255,255,.07)';cx.setLineDash([3*dpr,8*dpr]);
  cx.beginPath();cx.moveTo(pad.l,zy);cx.lineTo(W-pad.r,zy);cx.stroke();cx.setLineDash([]);
  // Y labels
  cx.font=(12*dpr)+"px 'SF Mono',monospace";cx.fillStyle='#6a7290';cx.textAlign='right';
  var yst=Math.max(5,Math.ceil((yMx-yMn)/6/5)*5);
  for(var pct=Math.ceil(yMn/yst)*yst;pct<=yMx;pct+=yst)cx.fillText((pct>0?'+':'')+pct+'%',pad.l-4*dpr,Yf(pct)+3*dpr);
  // BTC line (red)
  cx.strokeStyle='rgba(193,7,6,.75)';cx.lineWidth=2*dpr;
  cx.beginPath();for(var i4=0;i4<btcS.length;i4++){var x=pad.l+pw*i4/WIN,y=Yf(btcS[i4]);if(i4===0)cx.moveTo(x,y);else cx.lineTo(x,y)}cx.stroke();
  // Future BTC dashed
  if(G.i<WIN&&!G.done){cx.strokeStyle='rgba(193,7,6,.15)';cx.lineWidth=1.5*dpr;cx.setLineDash([4*dpr,8*dpr]);cx.beginPath();var fst=false;for(var i5=G.i;i5<WIN&&G.s+i5<DATES.length;i5++){var v2=(BTC_PRICE[DATES[G.s+i5]]/BTC_PRICE[DATES[G.s]]-1)*100;var x2=pad.l+pw*i5/WIN,y2=Yf(v2);if(!fst){cx.moveTo(x2,y2);fst=true}else cx.lineTo(x2,y2)}cx.stroke();cx.setLineDash([])}
  // ALT line (green)
  cx.strokeStyle='rgba(0,188,0,.85)';cx.lineWidth=2*dpr;
  cx.beginPath();for(var i6=0;i6<altS.length;i6++){var xa=pad.l+pw*i6/WIN,ya=Yf(altS[i6]);if(i6===0)cx.moveTo(xa,ya);else cx.lineTo(xa,ya)}cx.stroke();
  // YOU line (yellow)
  cx.strokeStyle='rgba(252,255,0,.7)';cx.lineWidth=2*dpr;
  cx.beginPath();for(var i7=0;i7<youS.length;i7++){var xy=pad.l+pw*i7/WIN,yy=Yf(youS[i7]);if(i7===0)cx.moveTo(xy,yy);else cx.lineTo(xy,yy)}cx.stroke();
  // Day marker
  if(G.i>0&&G.i<WIN){var curX=pad.l+pw*G.i/WIN;cx.strokeStyle='rgba(255,255,255,.1)';cx.lineWidth=.5*dpr;cx.beginPath();cx.moveTo(curX,pad.t);cx.lineTo(curX,H-pad.b);cx.stroke()}
}

function drawDayBar(){
  document.getElementById('day-label').textContent=G.i;
  document.getElementById('day-bar-fill').style.width=(G.i/WIN*100)+'%';
}

function updateUI(){
  var date=G.i>0?DATES[G.s+G.i-1]:DATES[G.s];
  var btcNow=BTC_PRICE[date]||BTC_PRICE[DATES[G.s]];
  var btcStart=BTC_PRICE[DATES[G.s]];
  var youD=G.i===0?START:G.btcQty*btcNow;
  var badD=G.i===0?START:START*btcNow/btcStart;
  var delta=youD-badD,ahead=delta>=0;
  var totalPnL=Math.round(youD-START);
  var dailyPnl=0;if(G.i>1){var pb=BTC_PRICE[DATES[G.s+G.i-2]];if(pb&&btcNow)dailyPnl=(btcNow/pb-1)*100}
  
  // You box
  document.getElementById('you-val').textContent=fmt$(youD);
  document.getElementById('you-val').className='f-val'+(ahead?' up':' dn');
  document.getElementById('you-sub').innerHTML=(totalPnL>=0?'+':'-')+'$'+Math.abs(totalPnL).toLocaleString()+' &middot; '+G.trades+' trades';
  
  // VS box
  document.getElementById('vs-num').textContent=(delta>=0?'+':'-')+'$'+Math.abs(Math.round(delta)).toLocaleString();
  document.getElementById('vs-num').className='vs-num'+(ahead?' ahead':' behind');
  
  // Badger box
  document.getElementById('badger-val').textContent=fmt$(badD);
  document.getElementById('badger-sub').textContent=(dailyPnl>=0?'+':'')+dailyPnl.toFixed(2)+'% today';
  
  // Position banner
  var bn=document.getElementById('pos-banner'),tg=document.getElementById('toggle-btn');
  if(G.inBasket){
    bn.className='pos-banner fomo';
    bn.innerHTML='<div class=\"pos-main\"><span>FOMO</span></div><span class=\"pos-desc\">Altcoin Bags Full</span>';
    tg.className='toggle hodl';tg.innerHTML='HODL &middot; SWITCH TO BITCOIN';
  }else{
    bn.className='pos-banner safu';
    bn.innerHTML='<div class=\"pos-main\"><span>SAFU</span></div><span class=\"pos-desc\">Hodling Only Bitcoin</span>';
    tg.className='toggle yolo';tg.innerHTML='YOLO &middot; SWITCH TO ALTCOINS';
  }
  
}

function runBananaTest(callback){
  var blocks=[],cur=0,inB=false;
  for(var i=0;i<WIN;i++){
    if(G.pos[i]===1){inB=true;cur++}
    else{if(inB){blocks.push(cur);inB=false;cur=0}}
  }
  if(inB)blocks.push(cur);
  if(blocks.length===0){callback(null);return}
  var totalB=blocks.reduce(function(a,b){return a+b},0);
  var totalH=WIN-totalB,startIdx=G.s,btcStart=BTC_PRICE[DATES[startIdx]];
  var youDollarsFinal=G.btcQty*BTC_PRICE[DATES[G.s+WIN-1]];
  var N=1000,worse=0,m=0;
  function chunk(){
    var end=Math.min(m+50,N);
    for(;m<end;m++){
      var shuf=blocks.slice();
      for(var i=shuf.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=shuf[i];shuf[i]=shuf[j];shuf[j]=t}
      var cuts=new Array(shuf.length+1);for(var i=0;i<=shuf.length;i++)cuts[i]=Math.floor(Math.random()*(totalH+1));
      cuts.sort(function(a,b){return a-b});
      var btcQ=START/btcStart,day=startIdx;
      for(var b=0;b<shuf.length;b++){
        day+=cuts[b+1]-cuts[b];
        for(var d=0;d<shuf[b];d++){var r=BASKET[day+d];if(!isNaN(r))btcQ*=Math.exp(r)}
        day+=shuf[b];
      }
      if(btcQ*BTC_PRICE[DATES[startIdx+WIN-1]]<=youDollarsFinal)worse++;
    }
    if(m>=N)callback(Math.round(worse/N*100));
    else setTimeout(chunk,1);
  }
  chunk();
}

function finishGame(){
  G.done=true;G.running=false;cancelAnimationFrame(raf);updateUI();drawChart();drawDayBar();var be=BTC_PRICE[DATES[G.s+WIN-1]];var youDollarsFinal=G.btcQty*be;
  var bs=BTC_PRICE[DATES[G.s]];
  var youD=G.btcQty*be,badD=START*be/bs;
  var rel=youD/badD-1;
  var inBt=G.pos.reduce(function(a,b){return a+b},0);
  var pctIn=Math.round(inBt/WIN*100);
  
  // Unwinnable check
  var unw=false;
  if(rel<-0.01){unw=true;for(var ui=0;ui<WIN;ui++){var cr2=0;for(var uj=0;uj<=ui;uj++){var rr=BASKET[G.s+uj];if(!isNaN(rr))cr2+=rr}if(Math.exp(cr2)*BTC_PRICE[DATES[G.s+ui]]/bs>BTC_PRICE[DATES[G.s+ui]]/bs){unw=false;break}}}
  
  var verdict,stampClass;
  if(G.trades===0&&inBt===0){verdict='HODLER';stampClass='hodler'}
  else if(rel>0.02){verdict='LUCKY APE';stampClass='lucky'}
  else if(rel>-0.01){verdict='LUCKY APE';stampClass='lucky'}
  else if(unw&&rel>-0.01){verdict='HODLER';stampClass='hodler'}
  else{verdict='HONEY BADGER WINS';stampClass='badger'}
  
  // Seasons
  var ws=new Date(DATES[G.s]),we=new Date(DATES[G.s+WIN-1]),snames=[];
  for(var si=0;si<SEASONS.length;si++){var ss=new Date(SEASONS[si].s),se=new Date(SEASONS[si].e);if(ws<=se&&we>=ss)snames.push(SEASONS[si].name)}
  var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fdt(ds){var dt=new Date(ds);return MON[dt.getUTCMonth()]+' '+dt.getUTCDate()+', '+dt.getUTCFullYear()}
  
  document.getElementById('sdt').textContent=DATES[G.s]+' UTC';
  document.getElementById('sst').textContent=verdict;
  document.getElementById('sst').className='stamp '+stampClass;
  document.getElementById('sds').textContent=fdt(DATES[G.s])+' \\u2192 '+fdt(DATES[G.s+WIN-1]);
  document.getElementById('sss').textContent=snames.length>0?'You traded through the '+snames.join(', '):'';
  document.getElementById('str').textContent=G.trades;
  document.getElementById('sti').textContent=pctIn+'%';
  document.getElementById('sps').textContent='\\u2014';
  
  var oel=document.getElementById('sout');
  if(rel>0.01){oel.innerHTML='You beat the Bitcoin HODLER by <span class=\"win\">'+fmt$(Math.round(youD-badD))+'</span>'}
  else if(unw&&rel>-0.01){oel.innerHTML='This window was unwinnable. <span class=\"win\">Matching the badger counts as a win.</span>'}
  else{oel.innerHTML=\"You'd have been better off by <span class='lose'>\"+fmt$(Math.round(badD-youD))+\"</span> just HODLing Bitcoin\"}
  
  document.getElementById('sya').textContent=fmt$(Math.round(youD));
  var yp=(youD/START-1)*100;
  document.getElementById('syp').textContent=(yp>=0?'+':'')+yp.toFixed(1)+'%';
  document.getElementById('syp').className='pct'+(yp>0.1?' up':yp<-0.1?' dn':' eq');
  
  document.getElementById('sba').textContent=fmt$(Math.round(badD));
  var bp=(badD/START-1)*100;
  document.getElementById('sbp').textContent=(bp>=0?'+':'')+bp.toFixed(1)+'%';
  document.getElementById('sbp').className='pct'+(bp>0.1?' up':bp<-0.1?' dn':' eq');
  
  var tier=TIERS[0][1];for(var ti=0;ti<TIERS.length;ti++){if(youD>=TIERS[ti][0])tier=TIERS[ti][1]}
  if(unw&&rel>-0.01)tier='At least you survived. The badger is still watching.';
  document.getElementById('stier').textContent=tier;
  // Notable events
  var evs=[],ws2=new Date(DATES[G.s]),we2=new Date(DATES[G.s+WIN-1]);
  for(var ei=0;ei<EVENTS.length;ei++){var ed=new Date(EVENTS[ei].date);if(ed>=ws2&&ed<=we2)evs.push(EVENTS[ei])}
  var ebox=document.getElementById('sum-events-box'),elist=document.getElementById('sum-events-list'),etitle=document.getElementById('sum-events-title');
  if(evs.length>0){ebox.style.display='block';var ec=Math.min(evs.length,8);etitle.textContent=ec+' notable event'+(ec>1?'s':'')+' during this period'+(evs.length>8?' (showing '+ec+' of '+evs.length+')':'');elist.innerHTML='';for(var ej=0;ej<ec;ej++){var erow=document.createElement('div');erow.className='event-row';erow.textContent=evs[ej].date.slice(0,7)+' \u2014 '+evs[ej].text;elist.appendChild(erow)}}

  else{ebox.style.display='none'}
  document.getElementById('summary-overlay').classList.add('on');
  var ht=document.querySelector('.header').getBoundingClientRect().top,tb=document.getElementById('toggle-btn').getBoundingClientRect().bottom,ch=document.querySelector('.summary-card').offsetHeight;document.getElementById('summary-overlay').style.paddingTop=Math.max(0,(ht+tb)/2-ch/2)+'px';
  
  // POST to server
  setTimeout(function(){runBananaTest(function(bp){var pct=bp||50;document.getElementById('sps').textContent=pct===-1?'\u2014':ord(pct);var stampEl=document.getElementById('sst');if(rel>0.02&&pct>=90){stampEl.textContent='DEGEN';stampEl.className='stamp degen'}if(API){try{var payload=JSON.stringify({i:crypto.randomUUID?crypto.randomUUID():String(Date.now()),s:G.s,p:pct,r:rel,t:G.pos.reduce(function(a,p,i){if(i===0||p!==G.pos[i-1])a.push(i);return a},[]),d:Math.round(youD-badD),final:Math.round(youD)});fetch(API+'/pump/run',{method:'POST',body:payload,keepalive:true,headers:{'X-Api-Key':(document.querySelector('meta[name=api-key]')||{}).content||''}}).then(function(r){return r.json()}).then(function(d){if(d&&d.tierText)document.getElementById('stier').textContent=d.tierText}).catch(function(){})}catch(e){}}})},150)
}

function doToggle(){if(G.done)return;G.inBasket=!G.inBasket;if(G.phase==='live'&&G.running)G.trades++;updateUI()}

function loadLobbyData(){
  if(!API)return;
  fetch(API+'/pump/ledger').then(function(r){return r.json()}).then(function(d){
    document.getElementById('lg-games').textContent=(d.games||0).toLocaleString();
    document.getElementById('lg-badger').textContent=(d.badger_wins||0).toLocaleString();
    fetch(API+'/pump/recent?n=100').then(function(r2){return r2.json()}).then(function(d2){
      if(d2&&d2.games&&d2.games.length){
        var rets=[];
        for(var i=0;i<d2.games.length;i++){var rr=d2.games[i].r;if(typeof rr==='number')rets.push(rr)}
        rets.sort(function(a,b){return a-b});
        if(rets.length>0){
          var med=rets[Math.floor(rets.length/2)];
          document.getElementById('lg-median').textContent=(med>=0?'+':'')+(med*100).toFixed(1)+'%';
          document.getElementById('lg-best').textContent=(rets[rets.length-1]>=0?'+':'')+(rets[rets.length-1]*100).toFixed(1)+'%';
        }
      }
    }).catch(function(){});
  }).catch(function(){});
  fetch(API+'/pump/recent?n=20').then(function(r){return r.json()}).then(function(d){
    var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var tbody=document.getElementById('recent-tbody');
    var tape=document.getElementById('tape'),h='';
    if(!d||!d.games||!d.games.length){
      tbody.innerHTML='<tr><td colspan="5" class="mid">No games played yet. Be the first.</td></tr>';
      tape.innerHTML='No games played yet. Be the first.';return;
    }
    tbody.innerHTML='';
    for(var i=0;i<d.games.length;i++){
      var g=d.games[i],ret=g.r||0,vc='',v='BADGER',tvc='b';
      if(ret>0.02&&g.p>=90){vc='vb-d';v='DEGEN';tvc='d'}
      else if(ret>0.01){vc='vb-l';v='LUCKY APE';tvc='l'}
      else if(ret>-0.01){vc='vb-h';v='HODLER';tvc='h'}
      else{vc='vb-b';v='BADGER WINS';tvc='b'}
      var vs=parseInt(g.s),ve=vs+364,ds=new Date(DATES[vs]),de=new Date(DATES[ve]||DATES[DATES.length-1]);
      var wStr=MON[ds.getUTCMonth()]+' '+ds.getUTCFullYear()+'\u2192'+MON[de.getUTCMonth()]+' '+de.getUTCFullYear();
      var ws2=new Date(DATES[vs]),we2=new Date(DATES[ve]||DATES[DATES.length-1]),snames=[];
      for(var si=0;si<SEASONS.length;si++){var ss=new Date(SEASONS[si].s),se=new Date(SEASONS[si].e);if(ws2<=se&&we2>=ss)snames.push(SEASONS[si].name)}
      var seasonStr=snames.length>0?snames.slice(0,3).join(', '):'\u2014';
      var retPct=(ret>=0?'+':'')+(ret*100).toFixed(1)+'%',retClass=ret>0.01?'up':ret<-0.01?'dn':'mid';
      if(i>=d.games.length-8){
        var tr=document.createElement('tr');
        tr.innerHTML='<td><span class="vbadge '+vc+'">'+v+'</span></td><td class="mid">'+wStr+'</td><td class="'+retClass+'">'+retPct+'</td><td class="mid">'+(g.t?g.t.length:0)+'</td><td class="mid">'+seasonStr+'</td>';
        tbody.appendChild(tr);
      }
      var up=ret>=0,relPct2=(ret*100).toFixed(0),wStr2=MON[ds.getUTCMonth()]+String(ds.getUTCFullYear()).slice(2)+'\u2192'+MON[de.getUTCMonth()]+String(de.getUTCFullYear()).slice(2);
      h+='<span class="ti"><span class="vb '+tvc+'">'+(tvc==='d'?'DEGEN':tvc==='l'?'LUCKY APE':tvc==='h'?'HODLER':'BADGER WINS')+'</span> '+wStr2+' '+(tvc==='h'?'<span class="mid">matched badger</span>':'<span class="'+(up?'up':'dn')+'">'+(up?'+':'')+relPct2+'% vs badger</span>')+'</span>';
    }
    tape.innerHTML=h+h;
  }).catch(function(){});
}

// Event handlers
document.getElementById('toggle-btn').addEventListener('click',doToggle);
document.addEventListener('keydown',function(e){if(e.code==='Space'){e.preventDefault();if(G.screen==='game')doToggle()}if(e.code==='KeyP'&&G.phase==='live'&&!G.done){G.running=!G.running;if(!G.running){G._pp=G.inBasket}else{if(G.inBasket!==G._pp)G.trades++;lt=0;raf=requestAnimationFrame(loop)}document.getElementById('pause-btn').textContent=G.running?'\u23f8':'\u25b6'}});
document.querySelectorAll('.spd-btn').forEach(function(b){b.addEventListener('click',function(){G.speed=parseFloat(b.dataset.s);document.querySelectorAll('.spd-btn').forEach(function(x){x.classList.toggle('on',x===b)})})});
document.getElementById('btn-again').addEventListener('click',function(){document.getElementById('summary-overlay').classList.remove('on');startGame()});
document.getElementById('pause-btn').addEventListener('click',function(){if(G.phase!=='live'||G.done)return;G.running=!G.running;if(!G.running){G._pp=G.inBasket}else{if(G.inBasket!==G._pp)G.trades++;lt=0;raf=requestAnimationFrame(loop)}this.textContent=G.running?'\u23f8':'\u25b6'});
document.getElementById('meth-close').addEventListener('click',function(){document.getElementById('meth-overlay').classList.remove('on')});
document.addEventListener('keydown',function(e){if(e.key==='Escape')document.getElementById('meth-overlay').classList.remove('on')});
document.getElementById('meth-overlay').addEventListener('click',function(e){if(e.target===this)this.classList.remove('on')});

function copyShareLink(){
  var url=location.origin+location.pathname;
  var cb=document.getElementById('btn-copy');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(url).then(function(){
      cb.textContent='LINK COPIED!';cb.style.background='rgba(252,255,0,.15)';
      setTimeout(function(){cb.textContent='SHARE';cb.style.background=''},1800);
    }).catch(function(){fallbackCopy(url,cb,'SHARE')});
  }else{fallbackCopy(url,cb,'SHARE')}
}
function fallbackCopy(url,cb,label){
  var ta=document.createElement('textarea');ta.value=url;ta.style.position='fixed';ta.style.left='-9999px';
  document.body.appendChild(ta);ta.select();
  try{document.execCommand('copy')}catch(e){}
  document.body.removeChild(ta);
  cb.textContent='LINK COPIED!';cb.style.background='rgba(252,255,0,.15)';
  setTimeout(function(){cb.textContent=label||'CHALLENGE A FRIEND';cb.style.background=''},1800);
}
function copyChallengeLink(){
  var url=location.origin+location.pathname+'?t='+G.s;
  var cb=document.getElementById('btn-challenge');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(url).then(function(){
      cb.textContent='LINK COPIED!';cb.style.background='rgba(252,255,0,.15)';
      setTimeout(function(){cb.textContent='CHALLENGE A FRIEND';cb.style.background=''},1800);
    }).catch(function(){fallbackCopy(url,cb,'CHALLENGE A FRIEND')});
  }else{fallbackCopy(url,cb,'CHALLENGE A FRIEND')}
}
document.getElementById('btn-lobby').addEventListener('click',function(){document.getElementById('summary-overlay').classList.remove('on');showScreen('lobby')});
function dailyChallengeDay(){
  var d=new Date(),s=d.toISOString().slice(0,10),h=0;
  for(var i=0;i<s.length;i++){h=((h<<5)-h)+s.charCodeAt(i);h|=0}
  return FP+Math.abs(h)%(MX-FP);
}
window.addEventListener('resize',function(){if(G.screen==='game'){drawChart();drawDayBar()}});

// Init
var params=new URLSearchParams(location.search);var challengeS=parseInt(params.get('s'),10);var challengeT=parseInt(params.get('t'),10);
if(Number.isInteger(challengeS)){startGame(challengeS)}
else if(Number.isInteger(challengeT)){
  showScreen('lobby');
  var btn=document.getElementById('btn-play');
  btn.textContent='YOU\\u2019VE BEEN CHALLENGED!';
  btn.className='btn-play challenged';
  btn.setAttribute('onclick','startGame('+challengeT+')');
}else{
  showScreen('lobby');
  document.getElementById('btn-play').setAttribute('onclick','startGame()');
}
document.getElementById('btn-daily').addEventListener('click',function(){startGame(dailyChallengeDay())});"""

    html = build_html_template(js)
    
    # Verify JS syntax
    js_only = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if js_only:
        with open("/tmp/check.js", "w") as f:
            f.write(js_only.group(1))
        r = subprocess.run(["node", "--check", "/tmp/check.js"], capture_output=True, text=True)
        if r.returncode != 0:
            print("JS SYNTAX ERROR:", r.stderr[:500])
            return
    
    with open(os.path.join(WEB, "index.html"), "w") as f:
        f.write(html)
    
    size = os.path.getsize(os.path.join(WEB, "index.html"))
    print(f"Built: {size:,} bytes ({size/1024:.0f} KB) — JS OK")

def build_html_template(js):
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="api-base" content="https://api.gridrun.net">
<meta name="api-key" content="immadegen">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><rect width='16' height='16' fill='%23000' rx='2'/><rect x='6' y='1' width='1' height='14' fill='%2300bc00'/><rect x='4' y='4' width='5' height='8' fill='%2300bc00' rx='0.5'/></svg>">
<title>DEGEN|TERMINAL</title>
<style>
body{background:var(--bg);color:var(--bright);font-family:'SF Mono','Monaco','Menlo','Consolas',monospace;font-size:15px;-webkit-font-smoothing:antialiased;min-height:100vh;overflow-x:hidden}
:root{--bg:#000;--panel:#0d0d10;--panel2:#111114;--border:#1c1c20;--border2:#242428;--dim:#5c5c60;--mid:#8a8a8e;--bright:#c8c8cc;--green:#00bc00;--red:#c10706;--yellow:#fcff00;--purple:#3c425b;--green-bg:#041604;--red-bg:#160404}
*{margin:0;padding:0;box-sizing:border-box}
body::before{content:'';display:block;height:2px;background:linear-gradient(90deg,#1a1a2e 0%,var(--purple) 30%,#5a6080 50%,var(--purple) 70%,#1a1a2e 100%)}
.screen{display:none}.screen.on{display:flex;flex-direction:column}
#scr-lobby.on{display:block}
.app{max-width:920px;margin:0 auto;padding:12px 20px 24px}

/* === LOBBY === */
.tape-wrap{border-bottom:1px solid var(--border);padding:5px 0;background:var(--panel);white-space:nowrap;font-size:12px}
.tape{display:inline-block;animation:tape 30s linear infinite;padding-left:20px}
.tape span{margin-right:28px;color:var(--dim)}
.tape .vb{font-size:11px;font-weight:700;letter-spacing:.06em;padding:1px 5px;border:1px solid}
.tape .vb.d{color:var(--green);border-color:rgba(0,188,0,.3)}
.tape .vb.b{color:var(--red);border-color:rgba(193,7,6,.3)}
.tape .vb.l{color:var(--yellow);border-color:rgba(252,255,0,.3)}
.tape .vb.h{color:var(--mid);border-color:var(--border)}
.tape .up{color:var(--green)}.tape .dn{color:var(--red)}.tape .mid{color:var(--mid)}
@keyframes tape{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.hero{position:relative;padding:44px 20px 40px;text-align:center}
.hero-chips{display:flex;justify-content:center;gap:10px;margin-bottom:20px}
.chip{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 14px;border:1px solid}
.chip.ape{color:var(--green);border-color:rgba(0,188,0,.3);background:rgba(0,188,0,.04)}
.chip.vs{color:var(--dim);border-color:var(--border);font-size:11px;padding:5px 10px}
.chip.badger{color:var(--red);border-color:rgba(193,7,6,.3);background:rgba(193,7,6,.04)}
.hero-title{font-size:38px;font-weight:700;letter-spacing:.04em;line-height:1.1;margin-bottom:8px}
.hero-title .g{color:var(--green)}
.hero-tag{font-size:11px;letter-spacing:.2em;color:var(--dim);text-transform:uppercase;margin-bottom:10px}
.hero-copy{font-size:14px;color:var(--mid);line-height:1.7;max-width:400px;margin:0 auto 26px}
.hero-copy strong{color:var(--bright)}
.cta-row{display:flex;justify-content:center;gap:10px}
.btn-play{background:var(--green);color:#000;border:none;font-family:inherit;font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:13px 0;width:280px;text-align:center;cursor:pointer}
.btn-play:hover{background:#00d400}
.btn-play.challenged{background:var(--yellow);color:#000;font-size:13px}
.btn-daily{background:transparent;color:var(--mid);border:1px solid var(--border);font-family:inherit;font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:13px 0;width:280px;text-align:center;cursor:pointer;box-sizing:border-box}
.btn-daily:hover{border-color:var(--mid);color:var(--bright)}
.content{max-width:920px;margin:0 auto;padding:24px 20px;border-top:1px solid var(--border)}
.sec-head{font-size:10px;letter-spacing:.18em;color:var(--dim);text-transform:uppercase;margin-bottom:10px;padding-bottom:7px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between}
.live{color:var(--green);display:flex;align-items:center;gap:5px}
.ldot{width:5px;height:5px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.gstats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);border:1px solid var(--border);margin-bottom:24px}
.gs{background:var(--panel);padding:14px 16px;text-align:center}
.gs .n{font-size:26px;font-weight:700;color:var(--bright);margin-bottom:3px;line-height:1}
.gs .n.red{color:var(--red)}.gs .n.yellow{color:var(--yellow)}.gs .n.green{color:var(--green)}
.gs .l{font-size:10px;letter-spacing:.12em;color:var(--dim);text-transform:uppercase}
.rtable{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px}
.rtable th{font-size:10px;letter-spacing:.14em;color:var(--dim);text-transform:uppercase;text-align:left;padding:5px 8px;border-bottom:1px solid var(--border);font-weight:400}
.rtable td{padding:8px 8px;border-bottom:1px solid rgba(255,255,255,.03)}
.rtable tr:hover td{background:rgba(255,255,255,.012)}
.vbadge{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:2px 6px;border:1px solid}
.vb-d{color:var(--green);border-color:rgba(0,188,0,.3)}
.vb-b{color:var(--red);border-color:rgba(193,7,6,.3)}
.vb-l{color:var(--yellow);border-color:rgba(252,255,0,.3)}
.vb-h{color:var(--mid);border-color:var(--border)}
td.up{color:var(--green)}td.dn{color:var(--red)}td.mid{color:var(--mid)}
.lore{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:24px}
.lore-card{border:1px solid var(--border);background:var(--panel);padding:16px}
.lore-icon{font-size:28px;margin-bottom:8px}
.lore-title{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;color:var(--bright)}
.lore-body{font-size:12px;color:var(--dim);line-height:1.65}
.lore-stat{font-size:16px;font-weight:700;margin-top:8px}
.lore-stat.red{color:var(--red)}.lore-stat.green{color:var(--green)}
.footer{border-top:1px solid var(--border);padding:11px 0;display:flex;justify-content:space-between;font-size:10px;letter-spacing:.1em;color:var(--dim);text-transform:uppercase}

/* === GAME (matches kiro v2-path-a) === */
.header{border:1px solid var(--border);background:var(--panel);padding:9px 14px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}
.logo-name{font-size:14px;font-weight:700;letter-spacing:.06em}
.logo-name .g{color:var(--green)}
.logo-sub{font-size:9px;letter-spacing:.14em;color:var(--dim);text-transform:uppercase}
.duel{display:grid;grid-template-columns:1fr 100px 1fr;gap:6px;margin-bottom:8px}
.fighter{border:1px solid var(--border);background:var(--panel);padding:10px 14px}
.fighter.you{border-color:rgba(0,188,0,.2)}
.fighter.badger{border-color:rgba(193,7,6,.15);text-align:right}
.f-name{font-size:10px;font-weight:700;letter-spacing:.08em;color:var(--yellow);text-transform:uppercase;margin-bottom:5px}
.f-val{font-size:30px;font-weight:700;line-height:1;letter-spacing:-.01em}
.fighter.you .f-val{color:var(--green)}.fighter.you .f-val.dn{color:var(--red)}
.fighter.badger .f-val{color:var(--mid)}
.f-sub{font-size:10px;color:var(--dim);margin-top:3px}
.f-sub .up{color:var(--green)}.f-sub .dn{color:var(--red)}
.vs-col{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}
.vs-num{font-size:22px;font-weight:700;padding:2px 7px;border:1px solid}
.vs-num.ahead{color:var(--green);border-color:rgba(0,188,0,.3)}
.vs-num.behind{color:var(--red);border-color:rgba(193,7,6,.3)}
.pos-banner{border:1px solid;padding:8px 14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;font-weight:700;letter-spacing:.04em}
.pos-banner.fomo{background:var(--red-bg);border-color:rgba(193,7,6,.4);color:var(--red)}
.pos-banner.safu{background:var(--green-bg);border-color:rgba(0,188,0,.4);color:var(--green)}
canvas{width:100%;height:800px;display:block}
.pos-main{display:flex;align-items:center;gap:12px;font-size:16px}
.pos-desc{font-size:14px;letter-spacing:.04em;color:var(--mid);text-transform:uppercase;font-weight:400}
.chart-wrap{border:1px solid var(--border);background:#000;position:relative;margin-bottom:5px}
.countdown{position:absolute;inset:0;background:rgba(0,0,0,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:10;display:none}
.c-lbl{font-size:9px;letter-spacing:.18em;color:var(--dim);text-transform:uppercase;margin-bottom:12px}
.c-num{font-size:80px;font-weight:700;color:var(--bright);line-height:1}
.c-sub{font-size:12px;color:var(--mid);text-align:center;max-width:340px;line-height:1.5;margin-top:12px}
.meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;font-size:14px}
.legend{display:flex;gap:14px;color:var(--dim)}
.li{display:flex;align-items:center;gap:5px}
.day-bar-wrap{display:flex;align-items:center;margin-bottom:10px;padding-left:52px;padding-right:16px;position:relative}
.sw{width:18px;height:2px;display:inline-block}
.sw-g{background:var(--green)}.sw-y{background:var(--yellow);opacity:.8}.sw-r{background:var(--red)}
.spd{display:flex;gap:2px}
.spd-btn{background:var(--purple);border:1px solid rgba(255,255,255,.07);color:var(--mid);font-family:inherit;font-size:14px;padding:3px 12px;cursor:pointer;text-transform:uppercase;letter-spacing:.06em}
.spd-btn.on{color:var(--bright);border-color:rgba(255,255,255,.18);background:#4a5270}
.pause-btn{background:var(--purple);border:1px solid rgba(255,255,255,.07);color:var(--mid);font-family:inherit;font-size:14px;padding:3px 10px;cursor:pointer;margin-right:6px;min-width:40px;text-align:center}
.day-bar-label{position:absolute;left:0;width:52px;font-size:12px;letter-spacing:.08em;color:#6a7290;text-transform:uppercase;text-align:center;white-space:nowrap}
.toggle{width:100%;padding:45px;font-family:inherit;font-size:22px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;border:1px solid;display:flex;justify-content:center;align-items:center;gap:12px}
.day-bar{flex:1;height:4px;background:#1a1a20}
.day-bar-fill{height:4px;background:linear-gradient(90deg,#4a5270,#6a7290,#8a92b0);width:0%}
.toggle.hodl{background:var(--green-bg);border-color:var(--green);color:var(--green)}
.toggle.yolo{background:var(--red-bg);border-color:var(--red);color:var(--red)}

.summary-overlay.on{display:flex;justify-content:center;align-items:flex-start;background:rgba(0,0,0,.65)}
.summary-overlay{position:fixed;inset:0;display:none;z-index:100}
.summary-card{width:420px;max-height:92vh;overflow-y:auto;background:#0a0a0c;border:1px solid #1c1c20;border-radius:24px;padding:14px 22px 26px;display:flex;flex-direction:column;gap:14px}
.sum-top-row{display:flex;justify-content:space-between;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
.sum-top-row .verdict-label{color:var(--bright)}.sum-top-row .datetime{color:var(--dim)}
.sum-verdict-box{border:1px solid #1c1c20;border-radius:8px;background:#111114;padding:24px 16px;text-align:center}
.sum-verdict-box .stamp{font-size:30px;font-weight:600;letter-spacing:.03em;text-transform:uppercase}
.sum-verdict-box .stamp.degen{color:var(--green)}.sum-verdict-box .stamp.lucky{color:#8a6d10}
.sum-verdict-box .stamp.hodler{color:var(--green)}.sum-verdict-box .stamp.badger{color:var(--red)}
.sum-verdict-box .window-dates{font-size:12px;color:var(--dim);margin-top:8px}
.sum-verdict-box .season-tag{font-size:11px;color:var(--mid);margin-top:6px;font-style:italic}
.sum-stat-row{display:flex;gap:8px}
.sum-stat{flex:1;border:1px solid #1c1c20;border-radius:6px;background:#111114;padding:12px 8px;text-align:center;display:flex;flex-direction:column;justify-content:center;gap:4px}
.sum-stat .num{font-size:22px;font-weight:600;color:var(--bright)}
.sum-stat .label{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim)}
.sum-outcome-box{border:1px solid #1c1c20;border-radius:8px;background:#111114;padding:16px}
.sum-outcome-box .outcome{font-size:13px;color:var(--mid);margin-bottom:14px;line-height:1.5}
.sum-outcome-box .outcome .win{color:var(--green)}.sum-outcome-box .outcome .lose{color:var(--red)}
.sum-player-row{display:flex;justify-content:space-between;align-items:baseline;padding:8px 0;border-top:1px solid rgba(255,255,255,.04)}
.sum-player-row .who{font-size:15px;font-weight:600;color:var(--bright)}
.sum-player-row .amount{font-size:15px;font-weight:600;color:var(--bright)}
.sum-player-row .pct{font-size:12px;margin-left:6px}
.sum-player-row .pct.up{color:var(--green)}.sum-player-row .pct.dn{color:var(--red)}.sum-player-row .pct.eq{color:var(--yellow)}
.sum-player-row .buy{font-size:12px;color:var(--dim);font-style:italic;margin-top:2px}
.sum-btn-row{display:flex;gap:10px;margin-top:4px}
.sum-btn{flex:1;padding:12px;font-family:inherit;font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;text-align:center;cursor:pointer;border:1px solid #1c1c20;background:#111114;color:var(--mid);border-radius:6px}
.sum-btn.primary{color:var(--bright);border-color:#2a2a30}
.challenge-btn{width:100%!important;flex:none!important;color:var(--yellow)!important;border-color:rgba(252,255,0,.3)!important}
.sum-events-box{border:1px solid #1c1c20;border-radius:8px;background:#111114;padding:14px 16px}
.events-title{font-size:11px;color:var(--dim);letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px}
.event-row{font-size:12px;color:var(--mid);padding:4px 0;border-top:1px solid rgba(255,255,255,.03)}
.meth-overlay{position:fixed;inset:0;background:rgba(0,0,0,.65);display:none;justify-content:center;align-items:flex-start;z-index:200;padding:40px 20px 40px;overflow-y:auto}
.meth-overlay.on{display:flex}
.meth-card{width:100%;max-width:680px;background:#0a0a0c;border:1px solid #1c1c20;border-radius:16px;padding:10px 36px 28px;position:relative;color:var(--mid);font-size:13px;line-height:1.75}
.meth-card h2{font-size:16px;font-weight:700;color:var(--bright);letter-spacing:.06em;margin:28px 0 10px;text-transform:uppercase}
.meth-card h2:first-child{margin-top:0}
.meth-card hr{border:none;border-top:1px solid var(--border);margin:16px 0}
.meth-card p{margin-bottom:12px}
.meth-card em{color:var(--dim)}
.meth-card a{color:var(--green);text-decoration:none}
.meth-close{position:absolute;top:14px;right:18px;background:none;border:none;color:var(--dim);font-family:inherit;font-size:18px;cursor:pointer;line-height:1}
.meth-close:hover{color:var(--bright)}
.meth-footer{text-align:center;font-size:11px;color:var(--dim);margin-top:28px;padding-top:18px;border-top:1px solid var(--border)}
</style>
</head>
<body>
<!-- === LOBBY === -->
<div class="screen on" id="scr-lobby">
<div class="tape-wrap"><div class="tape" id="tape">Loading recent games...</div></div>

<div class="hero">
  <div class="hero-chips">
    <div class="chip ape">⚡ Token Degen</div>
    <div class="chip vs">VS</div>
    <div class="chip badger">🦡 Bitcoin HODLer</div>
  </div>
  <div class="hero-title">DEGEN<span class="g">TERMINAL</span></div>
  <div class="hero-tag">No Fees · No Spread · No Mercy · 2017–2026</div>
  <div class="hero-copy">
    $10,000. 365 days. One button.<br>
    <strong>HODL Bitcoin</strong> or <strong>YOLO the top‑5 most volatile alts.</strong><br>
    The honey badger bought BTC on day one and never looked back.<br>
    Beat it. Prove you're a DEGEN, not just lucky.
  </div>
  <div class="cta-row">
    <button class="btn-play" id="btn-play">▶ PLAY NOW</button>
    <button class="btn-daily" id="btn-daily">⊞ DAILY CHALLENGE</button>
  </div>
</div>

<div class="content">
  <div class="sec-head"><span>Global Statistics</span><span class="live"><span class="ldot"></span>Live</span></div>
  <div class="gstats">
    <div class="gs"><div class="n" id="lg-games">—</div><div class="l">Games Played</div></div>
    <div class="gs"><div class="n red" id="lg-badger">—</div><div class="l">Badger Wins</div></div>
    <div class="gs"><div class="n yellow" id="lg-median">—</div><div class="l">Median vs Badger</div></div>
    <div class="gs"><div class="n green" id="lg-best">—</div><div class="l">Best Degen vs Badger</div></div>
  </div>

  <div class="sec-head"><span>Recent Results</span></div>
  <table class="rtable">
    <thead><tr><th>VERDICT</th><th>WINDOW</th><th>VS BADGER</th><th>TRADES</th><th>SEASON</th></tr></thead>
    <tbody id="recent-tbody">
      <tr><td colspan="5" class="mid">Loading...</td></tr>
    </tbody>
  </table>

  <div class="sec-head"><span>The Lore</span></div>
  <div class="lore">
    <div class="lore-card">
      <div class="lore-icon">🦍</div>
      <div class="lore-title">Token Degen (You)</div>
      <div class="lore-body">Always switching, always convinced this time is different. The basket is wild — top 5 most volatile alts rebalanced daily. DOGE, PEPE, ENJ. The coins you forgot you held.</div>
      <div class="lore-stat red">Wins 28% of the time</div>
    </div>
    <div class="lore-card">
      <div class="lore-icon">🦡</div>
      <div class="lore-title">The Bitcoin HODLer</div>
      <div class="lore-body">Bought BTC on day one and never looked back. Not interested in your thesis, doesn't care about use cases, and a depeg doesn't matter when it values everything in sats.</div>
      <div class="lore-stat green">Wins 72% of the time</div>
    </div>
  </div>

  <div class="footer">
    <span>Market Data: 2017–2026 · 54 coins · Daily resolution · <a href="#" onclick="document.getElementById('meth-overlay').classList.add('on');return false" style="color:var(--bright);text-decoration:none">METHODOLOGY &amp; CREDITS</a></span>
    <span>You Trade, The Badger Waits. Guess who wins?</span>
  </div>
</div>
</div>
</div>


<!-- === METHODOLOGY MODAL === -->
<div class="meth-overlay" id="meth-overlay">
<div class="meth-card">
<button class="meth-close" id="meth-close">&times;</button>
<h2>METHODOLOGY &amp; CREDITS</h2>
<hr>
<h2>Real Data</h2>
<p>Market data is sourced from Binance, without which we wouldn't have a liquid token ecosystem. The constraints that come from this choice are realistic and practical. Because crypto has no daily closing price (it's a 24/7 market), we pick a fixed time every day to source a single daily price. The dataset starts in mid-2017, when Binance was founded. Although Bitcoin was already trading at around USD 2,000 by then, there were not many alternative coins (fewer still which were not Bitcoin forks or clones). The altcoin market really only grew after Binance (in an attempt to get a lead over earlier competitors like Bittrex with stricter listing rules) quickly started listing every coin it could find. The choice to use Binance data was grounded in easy access to reliable market data and its role in shaping the ecosystem but it also means we miss the truly degen stuff like the Solana meme coins. It turns out anyway that such short-lived tokens would have to be excluded to make the game playable.</p>
<h2>The Alt Basket</h2>
<p>Our degen altcoin basket is made up of the Top 5 (for at least the prior 2 weeks) volatile (30-day rolling annual stddev) altcoins equally weighted. The chart ticks on daily prices so having a 14-day minimum filters out coins that may otherwise show as blips rather than a trend on a 365 day chart. This results in about +/- 50 coins that stay in the basket for an average of 7 days (after the 14-day filter) as of this writing.</p>
<p>The trading window is 1 year, which for crypto is 365 trading days. This was selected to give a good balance of playtime at 1x speed (about 45s), cover sufficient crypto events/seasons and also happily covers both the time horizon between trading and investing, and typical crypto holding periods. It probably comes as no surprise that as the window lengthens the proportion of Badger wins goes up — from about 60% at 90 days to 80% at 2 years (according to our banana casino).</p>
<h2>Fees, Spread and Slippage</h2>
<p>No fees, spread, slippage. These are the things that will kill you in real life trading, which don't matter as much to a long term single-asset HODLer. It's in your favour that we don't model it here.</p>
<h2>Calculation</h2>
<p>Both portfolios start with $10,000 worth of Bitcoin on day 1, at day 1 BTC/USD prices.</p>
<p>The badger holds this BTC and converts it back at the end of the 365 days at day 365 BTC/USD prices. It does not trade at all during the period, not even BTC/USD.</p>
<p>The player's (your) portfolio starts in the altcoin (aka Degen) basket, unless you toggle out to hold BTC during the countdown before Day 1. Then it starts same as the badger. Whenever you toggle, the full value of your holdings are converted into the other side at market prices. This means you'll want to be on the side of the higher line, and optimally switch when the gap is the biggest and about to move in the opposite direction. The yellow line represents your current performance.</p>
<h2>Chart</h2>
<p>The green line represents the performance of the altcoin basket, red line for BTC performance. The yellow line represents your performance, so ideally you'll want to keep that above both red and green. When you first start the game it may not be easy to see 3 lines, as the yellow line will initially follow either the green or red line (depending on if you toggled HODL/YOLO during the countdown).</p>
<p>The day bar represents how far you are in the game. There is no option for other time periods. You can speed it up using the speed controls if you feel it's going nowhere, or slow it down for more precise timing. You can also Pause and toggle during the Pause — the game is less about market timing than predicting the future, and if you wanted an edge on predictability just keep replaying the same game.</p>
<h2>Inspiration</h2>
<p>In parts of my personal and professional life I've been asked to consider the value (or my opinion) of trading shitcoins. At those times I often wished there was a simple resource explaining how HODLing BTC long term is a "better" strategy than degen ape-ing into coins. (Unless you're a professional, which I occasionally was, but if you are you wouldn't be asking me.) The point being that, yes there may be alpha that traders work hard to capture; if you want 2-min advice, try this game!</p>
<p>When I recently stumbled upon the absolutely fantastic <a href="https://beatthecouch.com/" target="_blank">Beat The Couch</a>, I realised that it was exactly what I was looking for, except applied to crypto trading (rather than market timing). I want to give credit to their biggest innovation — the monkey simulator, that runs 1000 rounds using the same parameters you played to give you an idea if you're really good or just lucky. Run a monkey simulator on your real-life trades to align for a quick ego/skill alignment.</p>
<h2>Gratitude</h2>
<p>Besides the couch at Beat the Couch, I'm also very grateful to <a href="https://fyra.sh" target="_blank">fyra</a> for hosting this on their CDN. The stats tracking backend is a small self-hosted worker hosted by the <a href="https://gridrun.net" target="_blank">GRIDRUN</a> team.</p>
<p>Thanks also to you for playing, giving <a href="mailto:degen@gridrun.net">feedback</a> or sharing the link. Hope you had fun and remember when asking a professional trader for tips — yes we're secretive but it's actually not that we don't want to share, it's just that... it's not that simple.</p>
<p>I leave you with a note from my AI coding partner:<br><em>Interesting... BTC is down ~34% of the time, up ~66% of the time over 365-day windows. The badger wins 70.2% of the time, but BTC itself only wins 65.6% — meaning the basket underperforms BTC even when BTC is up, and gets crushed when BTC is down.</em></p>
<div class="meth-footer">Copyright &copy; 2026, All Rights Reserved.</div>
</div>
</div>
<!-- === GAME === -->
<div class="screen" id="scr-game">
<div class="app">
  <div class="header">
    <div class="logo-name">DEGEN<span class="g">TERMINAL</span></div>
    <div class="logo-sub">No Fees · No Spread · No Mercy</div>
  </div>
  <div class="duel">
    <div class="fighter you">
      <div class="f-name">You</div>
      <div class="f-val" id="you-val">$10,000</div>
      <div class="f-sub" id="you-sub">$0 · 0 trades</div>
    </div>
    <div class="vs-col">
      <div class="vs-num ahead" id="vs-num">$0</div>
    </div>
    <div class="fighter badger">
      <div class="f-name">Honey Badger</div>
      <div class="f-val" id="badger-val">$10,000</div>
      <div class="f-sub" id="badger-sub">0.00% today</div>
    </div>
  </div>
  <div class="pos-banner fomo" id="pos-banner">
    <div class="pos-main"><span>FOMO</span></div><span class="pos-desc">Altcoin Bags Full</span>
  </div>
  <div class="chart-wrap">
    <div class="countdown" id="countdown">
      <div class="c-lbl">The next block confirms in...</div>
      <div class="c-num" id="count-num">3</div>
      <div class="c-sub">You start in the token basket. Switch during the countdown to start HODLing Bitcoin.</div>
    </div>
    <canvas id="chart"></canvas>
  </div>
  <div class="day-bar-wrap">
    <div class="day-bar-label" id="day-label">0</div>
    <div class="day-bar"><div class="day-bar-fill" id="day-bar-fill"></div></div>
  </div>
  <div class="meta">
    <div class="legend">
      <div class="li"><span class="sw sw-g"></span>Alts</div>
      <div class="li"><span class="sw sw-y"></span>You</div>
      <div class="li"><span class="sw sw-r"></span>BTC</div>
    </div>
    <div class="spd">
      <button class="pause-btn" id="pause-btn">⏸</button>
      <button class="spd-btn" data-s="0.5">0.5×</button>
      <button class="spd-btn on" data-s="1">1×</button>
      <button class="spd-btn" data-s="2">2×</button>
      <button class="spd-btn" data-s="4">4×</button>
    </div>
  </div>
  <button class="toggle hodl" id="toggle-btn">HODL · SWITCH TO BITCOIN</button>
</div>

<!-- === SUMMARY === -->
<div class="summary-overlay" id="summary-overlay">
  <div class="summary-card">
    <div class="sum-top-row"><span class="verdict-label">DEGEN OR HODLER?</span><span class="datetime" id="sdt">—</span></div>
    <div class="sum-verdict-box">
      <div class="stamp" id="sst">—</div>
      <div class="window-dates" id="sds">—</div>
      <div class="season-tag" id="sss">—</div>
    </div>
    <div class="sum-stat-row">
      <div class="sum-stat"><div class="num" id="str">0</div><div class="label">TRADES</div></div>
      <div class="sum-stat"><div class="num" id="sti">0%</div><div class="label">TIME IN ALTS</div></div>
      <div class="sum-stat"><div class="num" id="sps">—</div><div class="label">% VS APES</div></div>
    </div>
    <div class="sum-outcome-box">
      <div class="outcome" id="sout">—</div>
      <div class="sum-player-row"><span class="who">YOU</span><span><span class="amount" id="sya">$0</span><span class="pct" id="syp">0%</span></span></div>
      <div class="sum-player-row"><span class="who">HONEY BADGER</span><span><span class="amount" id="sba">$0</span><span class="pct" id="sbp">0%</span></span></div>
      <div class="sum-player-row" style="border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;text-align:center;font-size:12px;color:var(--mid)">How ya gonna spend it?</div>
      <div class="sum-player-row" style="border-top:0;padding-top:0"><span class="buy" id="stier">—</span></div>
    </div>
    <div class="sum-events-box" id="sum-events-box" style="display:none">
      <div class="events-title" id="sum-events-title"></div>
      <div id="sum-events-list"></div>
    </div>
    <div class="sum-btn-row" >
      <div class="sum-btn challenge-btn" id="btn-challenge" onclick="copyChallengeLink()">CHALLENGE A FRIEND</div>
    </div>
    <div class="sum-btn-row">
      <div class="sum-btn primary" id="btn-copy" onclick="copyShareLink()">SHARE</div>
      <div class="sum-btn" id="btn-again">PLAY AGAIN</div>
    </div>
    <div class="sum-btn-row" style="margin-top:0">
      <div class="sum-btn" id="btn-lobby" style="flex:0.35;margin:0 auto;padding:7px;font-size:10px">BACK TO LOBBY</div>
    </div>
  </div>
</div>

<script>""" + js + """</script>
</body>
</html>"""

if __name__ == "__main__":
    build_html()
