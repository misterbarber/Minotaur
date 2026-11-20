const { chromium } = require('playwright'); const fs=require('fs'); const R=__dirname+'/..';
const topo=fs.readFileSync(R+'/vendor/countries-50m.json','utf8');
const tj=fs.readFileSync(R+'/vendor/topojson-client.min.js','utf8');
const data=JSON.parse(fs.readFileSync(R+'/data.json','utf8')); const fx=data.fx.toUSD;
const pins=data.stocks.filter(s=>s.lat!=null&&s.lon!=null).map(s=>({lat:s.lat,lon:s.lon,m:s.metal,usd:((s.shares&&s.price)?s.price*s.shares:(s.mcap||20))*(fx[s.ccy]||1)}));
const f=n=>'data:font/woff2;base64,'+fs.readFileSync(R+'/node_modules/@fontsource/'+n).toString('base64');
const html=`<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:BC;font-weight:700;src:url(${f('barlow-condensed/files/barlow-condensed-latin-700-normal.woff2')})}
@font-face{font-family:BC;font-weight:600;src:url(${f('barlow-condensed/files/barlow-condensed-latin-600-normal.woff2')})}
@font-face{font-family:PS;font-weight:400;src:url(${f('ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff2')})}
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#0E2033}
.hd{position:absolute;left:56px;top:36px;display:flex;align-items:center;gap:26px}
.hd h1{margin:0;font:700 92px/0.9 BC;letter-spacing:.06em;color:#F4F7F9}
.hd p{margin:10px 0 0;font:400 25px/1.25 PS;color:#B9C6D2}
.lg{position:absolute;right:56px;top:52px;display:flex;flex-direction:column;gap:9px;font:600 22px BC;letter-spacing:.08em;text-transform:uppercase;color:#DCE4EA}
.lg span{display:flex;align-items:center;gap:10px}.lg i{width:15px;height:15px;border-radius:50%;display:inline-block}
.rule{position:absolute;left:56px;right:56px;top:218px;height:3px;background:#D7AE55;opacity:.9}
svg.map{position:absolute;left:0;top:226px}
.ft{position:absolute;left:560px;bottom:28px;font:600 22px BC;letter-spacing:.1em;text-transform:uppercase;color:#D7AE55}
</style></head><body>
<div class="hd"><svg width="118" height="118" viewBox="0 0 40 40"><rect width="40" height="40" fill="#0E2033"/><path d="M6 6H34V34H6V10H30V30H10V14H26V26H14V18H22V22" fill="none" stroke="#D7AE55" stroke-width="2.4" stroke-linecap="square"/></svg>
<div><h1>MINOTAUR</h1><p>${data.stocks.length} gold, silver, copper &amp; rare-earth juniors<br>ASX · TSX · TSXV — stage, valuation, maps, news</p></div></div>
<div class="lg"><span><i style="background:#D7AE55"></i>Gold</span><span><i style="background:#A9B6C1"></i>Silver</span><span><i style="background:#DA8A5E"></i>Copper</span><span><i style="background:#A493DB"></i>Rare earths</span></div>
<div class="rule"></div><svg class="map" width="1200" height="404" id="m"></svg>
<div class="ft">invisory.uk/minotaur</div>
<script>${tj}
const W=${topo}, P=${JSON.stringify(pins)};
const k=1200/360, T0=76, B0=-58, H=404, ky=H/(T0-B0), X=l=>(l+180)*k, Y=a=>(T0-a)*ky;
const g=topojson.feature(W,W.objects.countries); let d="";
g.features.forEach(ft=>{const geo=ft.geometry; if(!geo) return; const polys=geo.type==="Polygon"?[geo.coordinates]:geo.coordinates;
 polys.forEach(p=>p.forEach(r=>{ if(r.some(c=>c[1]<-60)) return; let prev=null; r.forEach((c,i)=>{const jump=prev&&Math.abs(c[0]-prev[0])>180; d+=(i===0||jump?"M":"L")+X(c[0]).toFixed(1)+","+Y(c[1]).toFixed(1); prev=c;});}));});
const col={"Gold":"#D7AE55","Silver":"#A9B6C1","Copper":"#DA8A5E","Rare earths":"#A493DB"};
let s='<path d="'+d+'" fill="#1C3A57" stroke="#2F5375" stroke-width="0.8"/>';
P.sort((a,b)=>b.usd-a.usd).forEach(p=>{const r=Math.max(5,Math.min(14,2+3.2*Math.log10(Math.max(p.usd,5))));
 s+='<circle cx="'+X(p.lon)+'" cy="'+Y(p.lat)+'" r="'+(r+5)+'" fill="'+(col[p.m]||"#4DB8B2")+'" opacity=".18"/><circle cx="'+X(p.lon)+'" cy="'+Y(p.lat)+'" r="'+r+'" fill="'+(col[p.m]||"#4DB8B2")+'" stroke="#0E2033" stroke-width="1.5"/>';});
document.getElementById("m").innerHTML=s;</script></body></html>`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'}); const p=await b.newPage({viewport:{width:1200,height:630}});
 await p.setContent(html); await p.waitForTimeout(600); await p.screenshot({path:R+'/site/og-image.png'}); await b.close(); console.log('pins',pins.length);})();
