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
  updateUI();drawChart();drawStrip();
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
  updateUI();drawChart();drawStrip();
  if(!G.done)raf=requestAnimationFrame(loop);
}

var cv=document.getElementById('chart'),cx=cv.getContext('2d');
var yLo=-25,yHi=25;
function drawChart(){
  var W=cv.parentElement.clientWidth*2,H=1200;cv.width=W;cv.height=H;var dpr=2;
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
  cx.font=(8*dpr)+"px 'SF Mono',monospace";cx.fillStyle='#5c5c60';cx.textAlign='right';
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

function drawStrip(){
  var strip=document.getElementById('strip');strip.innerHTML='';
  var s=0,cur=G.pos[0]||0;
  for(var i=1;i<=G.i;i++){
    if(i===G.i||G.pos[i]!==cur){
      var seg=document.createElement('div');
      seg.className='sg'+(cur===1?' sg-g':' sg-r');
      seg.style.width=((i-s)/WIN*100)+'%';strip.appendChild(seg);
      s=i;if(i<G.i)cur=G.pos[i];
    }
  }
  if(G.i<WIN&&!G.done){var sf=document.createElement('div');sf.className='sg sf';sf.style.width=((WIN-G.i)/WIN*100)+'%';strip.appendChild(sf)}
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
    bn.innerHTML='<div class=\"pos-main\"><span>FOMO</span><span class=\"pos-desc\">Altcoin Bags Full</span></div>';
    tg.className='toggle hodl';tg.innerHTML='HODL &middot; SWITCH TO BITCOIN';
  }else{
    bn.className='pos-banner safu';
    bn.innerHTML='<div class=\"pos-main\"><span>SAFU</span><span class=\"pos-desc\">Hodling Only Bitcoin</span></div>';
    tg.className='toggle yolo';tg.innerHTML='YOLO &middot; SWITCH TO ALTCOINS';
  }
  
  document.getElementById('day-label').textContent='DAY '+G.i;
  document.getElementById('prog-fill').style.width=(G.i/WIN*100)+'%';
}

function finishGame(){
  G.done=true;G.running=false;cancelAnimationFrame(raf);updateUI();drawChart();drawStrip();
  var bs=BTC_PRICE[DATES[G.s]],be=BTC_PRICE[DATES[G.s+WIN-1]];
  var youD=G.btcQty*be,badD=START*be/bs;
  var rel=youD/badD-1;
  var inBt=G.pos.reduce(function(a,b){return a+b},0);
  var pctIn=Math.round(inBt/WIN*100);
  
  // Unwinnable check
  var unw=false;
  if(rel<-0.01){unw=true;for(var ui=0;ui<WIN;ui++){var cr2=0;for(var uj=0;uj<=ui;uj++){var rr=BASKET[G.s+uj];if(!isNaN(rr))cr2+=rr}if(Math.exp(cr2)*BTC_PRICE[DATES[G.s+ui]]/bs>BTC_PRICE[DATES[G.s+ui]]/bs){unw=false;break}}}
  
  var verdict,stampClass;
  if(G.trades===0&&inBt===0){verdict='HODLER';stampClass='hodler'}
  else if(rel>0.02){verdict='DEGEN';stampClass='degen'}
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
  if(evs.length>0){ebox.style.display='block';etitle.textContent=evs.length+' notable event'+(evs.length>1?'s':'')+' during this period';elist.innerHTML='';for(var ej=0;ej<evs.length;ej++){var erow=document.createElement('div');erow.className='event-row';erow.textContent=evs[ej].date.slice(0,7)+' \u2014 '+evs[ej].text;elist.appendChild(erow)}}
  else{ebox.style.display='none'}
  
  document.getElementById('summary-overlay').classList.add('on');
  
  // POST to server
  if(API){try{var payload=JSON.stringify({i:crypto.randomUUID?crypto.randomUUID():String(Date.now()),s:G.s,p:50,r:rel,t:G.pos.reduce(function(a,p,i){if(i===0||p!==G.pos[i-1])a.push(i);return a},[]),d:Math.round(youD-badD),final:Math.round(youD)});fetch(API+'/api/run',{method:'POST',body:payload,keepalive:true,headers:{'X-Api-Key':(document.querySelector('meta[name=api-key]')||{}).content||''}}).then(function(r){return r.json()}).then(function(d){if(d&&d.tierText)document.getElementById('stier').textContent=d.tierText}).catch(function(){})}catch(e){}}else{console.log('no API base, skipping server post')}
}

function doToggle(){if(G.done)return;G.inBasket=!G.inBasket;if(G.phase==='live')G.trades++;updateUI()}

function loadLobbyData(){
  if(!API)return;
  fetch(API+'/api/ledger').then(function(r){return r.json()}).then(function(d){
    document.getElementById('lg-games').textContent=(d.games||0).toLocaleString();
    document.getElementById('lg-badger').textContent=(d.badger_wins||0).toLocaleString();
    document.getElementById('lg-degen').textContent=(d.degen_wins||0).toLocaleString();
    document.getElementById('lg-lucky').textContent=(d.lucky_wins||0).toLocaleString();
    document.getElementById('lg-don').textContent='$'+Math.round(d.donated||0).toLocaleString();
  }).catch(function(){});
  fetch(API+'/api/recent').then(function(r){return r.json()}).then(function(d){
    var el=document.getElementById('recent-feed');el.innerHTML='';
    if(!d||!d.games)return;
    for(var i=0;i<d.games.length;i++){
      var g=d.games[i],v=g.verdict||'unknown';
      var row=document.createElement('div');row.className='rrow';
      row.innerHTML='<span class=\"rv '+(v==='degen'?'rv-dg':v==='lucky ape'?'rv-lk':'rv-bg')+'\">'+v.toUpperCase()+'</span><span class=\"rt\">'+ (g.trades||0)+' trades</span><span class=\"rr\">'+(g.rel>=0?'+':'')+(g.rel*100).toFixed(1)+'%</span>';
      el.appendChild(row);
    }
  }).catch(function(){});
  fetch(API+'/api/tape').then(function(r){return r.json()}).then(function(d){
    var el=document.getElementById('tape');if(!d||!d.coins)return;
    var h='';for(var i=0;i<d.coins.length;i++){var c=d.coins[i];h+='<span><b>'+c.sym+'</b> '+c.price.toLocaleString()+' <span class=\"'+(c.change24h>=0?'up':'dn')+'\">'+(c.change24h>=0?'+':'')+c.change24h.toFixed(2)+'%</span></span> \\u00B7 '}
    el.innerHTML=h+h;
  }).catch(function(){});
}

// Event handlers
document.getElementById('toggle-btn').addEventListener('click',doToggle);
document.addEventListener('keydown',function(e){if(e.code==='Space'){e.preventDefault();if(G.screen==='game')doToggle()}if(e.code==='KeyP'&&G.phase==='live'&&!G.done){G.running=!G.running;if(G.running){lt=0;raf=requestAnimationFrame(loop)}}});
document.querySelectorAll('.spd-btn').forEach(function(b){b.addEventListener('click',function(){G.speed=parseFloat(b.dataset.s);document.querySelectorAll('.spd-btn').forEach(function(x){x.classList.toggle('on',x===b)})})});
document.getElementById('btn-again').addEventListener('click',function(){document.getElementById('summary-overlay').classList.remove('on');startGame()});

function copyChallengeLink(){
  var url=location.origin+location.pathname+'?t='+G.s;
  var cb=document.getElementById('btn-challenge');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(url).then(function(){
      cb.textContent='LINK COPIED!';cb.style.background='rgba(252,255,0,.15)';
      setTimeout(function(){cb.textContent='CHALLENGE A FRIEND';cb.style.background=''},1800);
    }).catch(function(){fallbackCopy(url,cb)});
  }else{fallbackCopy(url,cb)}
}
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
window.addEventListener('resize',function(){if(G.screen==='game'){drawChart();drawStrip()}});

// Init
var params=new URLSearchParams(location.search);var challengeS=parseInt(params.get('s'),10);var challengeT=parseInt(params.get('t'),10);
if(Number.isInteger(challengeS)){startGame(challengeS)}else if(Number.isInteger(challengeT)){showScreen('lobby');document.getElementById('challenge-box').style.display='block';document.getElementById('btn-play').setAttribute('onclick','startGame('+challengeT+')')}else{showScreen('lobby');document.getElementById('btn-play').setAttribute('onclick','startGame()')}"""

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
<meta name="api-base" content="https://api.gridrun.net:8090">
<meta name="api-key" content="immadegen">
<title>defihodler</title>
<style>
:root{--bg:#000;--panel:#0d0d10;--panel2:#111114;--border:#1c1c20;--border2:#242428;--dim:#5c5c60;--mid:#8a8a8e;--bright:#c8c8cc;--green:#00bc00;--red:#c10706;--yellow:#fcff00;--purple:#3c425b;--green-bg:#041604;--red-bg:#160404}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--bright);font-family:'SF Mono','Monaco','Menlo','Consolas',monospace;font-size:13px;-webkit-font-smoothing:antialiased;padding-top:30px}
/* accent bar removed — tape is now the top element */
.screen{display:none}.screen.on{display:flex;flex-direction:column}
#scr-lobby.on{display:block}
.app{max-width:920px;margin:0 auto;padding:12px 20px 24px}

/* === LOBBY === */
.lobby-header{border:1px solid var(--border);background:var(--panel);padding:16px 20px;margin-bottom:14px;text-align:center}
.lobby-header h1{font-size:20px;font-weight:700;letter-spacing:.06em;margin-bottom:4px}
.lobby-header h1 .g{color:var(--green)}
.lobby-header .sub{font-size:13px;letter-spacing:.14em;color:var(--dim);text-transform:uppercase}
.tape-wrap{position:fixed;top:0;left:0;right:0;z-index:50;border-bottom:1px solid var(--border);background:var(--panel);overflow:hidden;height:28px;display:flex;align-items:center}
.tape{display:inline-block;white-space:nowrap;animation:tape 30s linear infinite;font-size:12px;padding-left:20px}
.tape span{margin-right:28px;color:var(--dim)}
.tape .vb{font-size:11px;font-weight:700;letter-spacing:.06em;padding:1px 5px;border:1px solid}
.tape .vb.d{color:var(--green);border-color:rgba(0,188,0,.3)}
.tape .vb.b{color:var(--red);border-color:rgba(193,7,6,.3)}
.tape .vb.l{color:var(--yellow);border-color:rgba(252,255,0,.3)}
.tape .vb.h{color:var(--green);border-color:rgba(0,188,0,.2)}
.tape .up{color:var(--green)}.tape .dn{color:var(--red)}
@keyframes tape{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.hero{display:flex;gap:14px;margin-bottom:18px}
.hero-btn{flex:1;border:1px solid;padding:18px 16px 14px;text-align:center;cursor:pointer;transition:.1s}
.hero-btn:hover{opacity:.9}
.hero-btn.green{background:var(--green-bg);border-color:rgba(0,188,0,.4);color:var(--green)}
.hero-btn.red{background:var(--red-bg);border-color:rgba(193,7,6,.4);color:var(--red)}
.hero-btn .hb-name{font-size:18px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;margin-bottom:4px}
.hero-btn .hb-desc{font-size:14px;color:var(--dim);line-height:1.4}
.hero-btn .hb-play{font-size:15px;font-weight:600;margin-top:10px;letter-spacing:.08em;text-transform:uppercase}
.challenge-box{border:1px solid rgba(252,255,0,.2);background:var(--panel);padding:14px 20px;margin-bottom:14px;text-align:center}
.challenge-title{font-size:15px;font-weight:700;color:var(--yellow);text-transform:uppercase;letter-spacing:.04em}
.challenge-sub{font-size:12px;color:var(--mid);margin-top:4px}
.howto{border:1px solid var(--border);background:var(--panel);padding:16px 20px;margin-bottom:18px;text-align:center}
.howto h2{font-size:15px;font-weight:700;letter-spacing:.1em;color:var(--dim);text-transform:uppercase;margin-bottom:12px}
.howto-steps{display:flex;gap:10px}
.howto-step{flex:1;text-align:center}
.howto-step .n{font-size:24px;font-weight:700;color:var(--purple);margin-bottom:4px}
.howto-step .t{font-size:14px;color:var(--mid);line-height:1.4}
.ledger-box{border:1px solid var(--border);background:var(--panel);padding:14px 16px;margin-bottom:12px}
.ledger-box h2{font-size:14px;font-weight:700;letter-spacing:.14em;color:var(--dim);text-transform:uppercase;margin-bottom:10px}
.lgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.lstat{text-align:center}.lstat .lv{font-size:22px;font-weight:700}.lstat .lk{font-size:12px;letter-spacing:.08em;color:var(--dim);text-transform:uppercase}
.lstat.lg .lv{color:var(--green)}.lstat.lr .lv{color:var(--red)}.lstat.ly .lv{color:var(--yellow)}
.recent-box{border:1px solid var(--border);background:var(--panel);padding:14px 16px;margin-bottom:12px}
.recent-box h2{font-size:14px;font-weight:700;letter-spacing:.14em;color:var(--dim);text-transform:uppercase;margin-bottom:10px}
.rfeed{max-height:180px;overflow-y:auto}
.rrow{display:flex;align-items:center;gap:10px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.02);font-size:14px}
.rv{padding:1px 6px;font-weight:600;font-size:13px;letter-spacing:.06em;text-transform:uppercase;border:1px solid}
.rv-dg{color:var(--green);border-color:rgba(0,188,0,.3)}
.rv-lk{color:var(--yellow);border-color:rgba(252,255,0,.3)}
.rv-bg{color:var(--red);border-color:rgba(193,7,6,.3)}
.rt{color:var(--mid)}.rr{color:var(--dim);margin-left:auto}
.footer-row{text-align:center;font-size:13px;color:var(--dim);padding:10px 0}
.footer-row a{color:var(--mid);text-decoration:none}

/* === GAME (matches kiro v2-path-a) === */
.header{border:1px solid var(--border);background:var(--panel);padding:9px 14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}
.logo-name{font-size:14px;font-weight:700;letter-spacing:.06em}
.logo-name .g{color:var(--green)}
.logo-sub{font-size:9px;letter-spacing:.14em;color:var(--dim);text-transform:uppercase}
.duel{display:grid;grid-template-columns:1fr 100px 1fr;gap:6px;margin-bottom:7px}
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
.pos-banner{border:1px solid;padding:8px 14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;font-weight:700;letter-spacing:.04em}
.pos-banner.fomo{background:var(--red-bg);border-color:rgba(193,7,6,.4);color:var(--red)}
.pos-banner.safu{background:var(--green-bg);border-color:rgba(0,188,0,.4);color:var(--green)}
.pos-main{display:flex;align-items:center;gap:12px;font-size:14px}
.pos-desc{font-size:9px;letter-spacing:.12em;color:var(--mid);text-transform:uppercase;font-weight:400}
.chart-wrap{border:1px solid var(--border);background:#000;position:relative;margin-bottom:5px}
canvas{width:100%;height:600px;display:block}
.countdown{position:absolute;inset:0;background:rgba(0,0,0,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:10;display:none}
.c-lbl{font-size:9px;letter-spacing:.18em;color:var(--dim);text-transform:uppercase;margin-bottom:12px}
.c-num{font-size:80px;font-weight:700;color:var(--bright);line-height:1}
.c-sub{font-size:12px;color:var(--mid);text-align:center;max-width:340px;line-height:1.5;margin-top:12px}
.strip{height:4px;display:flex;margin-bottom:7px}
.sg-g{background:var(--green);opacity:.55}.sg-r{background:var(--red);opacity:.2}.sf{background:rgba(255,255,255,.04)}
.meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-size:9px}
.legend{display:flex;gap:14px;color:var(--dim)}
.li{display:flex;align-items:center;gap:5px}
.sw{width:18px;height:2px;display:inline-block}
.sw-g{background:var(--green)}.sw-y{background:var(--yellow);opacity:.8}.sw-r{background:var(--red)}
.prog-wrap{display:flex;align-items:center;gap:8px;letter-spacing:.1em;color:var(--dim);text-transform:uppercase}
.prog{flex:1;height:6px;background:#1a1a20;min-width:180px;border:1px solid var(--border)}
.prog-fill{height:100%;background:linear-gradient(90deg,#4a5270,#6a7290,#8a92b0);border-right:1px solid rgba(255,255,255,.1)}
.ctrl{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.ctrl-lbl{font-size:8px;letter-spacing:.14em;color:var(--dim);text-transform:uppercase}
.spd{display:flex;gap:2px}
.spd-btn{background:var(--purple);border:1px solid rgba(255,255,255,.07);color:var(--dim);font-family:inherit;font-size:9px;padding:3px 9px;cursor:pointer;text-transform:uppercase;letter-spacing:.06em}
.spd-btn.on{color:var(--bright);border-color:rgba(255,255,255,.18);background:#4a5270}
.kbd{margin-left:auto;font-size:8px;letter-spacing:.1em;color:var(--dim);text-transform:uppercase}
.toggle{width:100%;padding:15px;font-family:inherit;font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;border:1px solid;display:flex;justify-content:center;align-items:center;gap:12px}
.toggle.hodl{background:var(--green-bg);border-color:var(--green);color:var(--green)}
.toggle.yolo{background:var(--red-bg);border-color:var(--red);color:var(--red)}

/* === SUMMARY === */
.summary-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;justify-content:center;align-items:center;z-index:100}
.summary-overlay.on{display:flex;align-items:flex-start;padding-top:160px}
.summary-card{width:420px;max-height:92vh;overflow-y:auto;background:#0a0a0c;border:1px solid #1c1c20;border-radius:24px;padding:14px 22px 32px;display:flex;flex-direction:column;gap:14px}
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
</style>
</head>
<body>
<!-- === LOBBY === -->
<div class="screen on" id="scr-lobby">
<div class="app">
  <div class="lobby-header">
    <h1>DEGEN<span class="g">TERMINAL</span></h1>
    <div class="sub">The ape trades. The badger waits. Guess who wins.</div>
  </div>
  <div class="tape-wrap"><div class="tape" id="tape">Loading recent games...</div></div>
  <div class="hero">
    <div class="hero-btn green" id="btn-play">
      <div class="hb-name">Token Degen</div>
      <div class="hb-desc">YOLO into the 5 most volatile altcoins. One click to ape in, one click to hide in BTC.</div>
      <div class="hb-play">PLAY</div>
    </div>
  </div>
  <div class="challenge-box" id="challenge-box" style="display:none">
    <div class="challenge-title">You've been challenged!</div>
    <div class="challenge-sub">Play the same period as your friend and see if you can do better!</div>
  </div>
  <div class="howto">
    <h2>How It Works</h2>
    <div class="howto-steps">
      <div class="howto-step"><div class="n">1</div><div class="t">$10,000 in BTC.<br>A random 365-day window from 2017–2026.</div></div>
      <div class="howto-step"><div class="n">2</div><div class="t">One button: HODL BTC or YOLO into a basket of top tokens.</div></div>
      <div class="howto-step"><div class="n">3</div><div class="t">The badger bought BTC<br>and never looked back. Beat it.</div></div>
    </div>
  </div>
  <div class="ledger-box">
    <h2>Global Ledger · All returns are vs the Honey Badger (BTC HODL)</h2>
    <div class="lgrid">
      <div class="lstat"><div class="lv" id="lg-games">—</div><div class="lk">Games</div></div>
      <div class="lstat lr"><div class="lv" id="lg-badger">—</div><div class="lk">Badger Wins</div></div>
      <div class="lstat ly"><div class="lv" id="lg-lucky">—</div><div class="lk">Lucky Apes</div></div>
      <div class="lstat lg"><div class="lv" id="lg-degen">—</div><div class="lk">Degens</div></div>
      <div class="lstat lr"><div class="lv" id="lg-don">—</div><div class="lk">Donated</div></div>
    </div>
  </div>
  <div class="recent-box">
    <h2>Recent Results</h2>
    <div class="rfeed" id="recent-feed"><div class="rrow"><span style="color:var(--dim)">Loading...</span></div></div>
  </div>
  <div class="footer-row">
    <a href="#" onclick="document.getElementById('meth-modal').classList.add('on');return false">Methodology</a> · Built with historical Binance data 2017–2026 · Not financial advice
  </div>
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
    <div class="pos-main"><span>FOMO</span><span class="pos-desc">Altcoin Bags Full</span></div>
  </div>
  <div class="chart-wrap">
    <div class="countdown" id="countdown">
      <div class="c-lbl">The next block confirms in...</div>
      <div class="c-num" id="count-num">3</div>
      <div class="c-sub">You start in the token basket. Switch during the countdown to start HODLing Bitcoin.</div>
    </div>
    <canvas id="chart"></canvas>
  </div>
  <div class="strip" id="strip"></div>
  <div class="meta">
    <div class="legend">
      <div class="li"><span class="sw sw-g"></span>Alts</div>
      <div class="li"><span class="sw sw-y"></span>You</div>
      <div class="li"><span class="sw sw-r"></span>BTC</div>
    </div>
    <div class="prog-wrap">
      <span id="day-label">DAY 0</span>
      <div class="prog"><div class="prog-fill" id="prog-fill" style="width:0%"></div></div>
      <span>365</span>
    </div>
  </div>
  <div class="ctrl">
    <span class="ctrl-lbl">SPEED</span>
    <div class="spd">
      <button class="spd-btn" data-s="0.5">0.5×</button>
      <button class="spd-btn on" data-s="1">1×</button>
      <button class="spd-btn" data-s="2">2×</button>
      <button class="spd-btn" data-s="4">4×</button>
    </div>
    <span class="kbd">SPACE: TOGGLE · P: PAUSE</span>
  </div>
  <button class="toggle hodl" id="toggle-btn">HODL · SWITCH TO BITCOIN</button>
</div>
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
