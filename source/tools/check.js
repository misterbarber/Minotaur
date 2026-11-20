const { chromium } = require('playwright'); const R=__dirname+'/..';
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'});
for (const [w,h,mob,scheme,tag] of [[1400,900,false,'light','desk-light'],[1400,900,false,'dark','desk-dark'],[390,844,true,'light','phone']]){
 const c=await b.newContext({viewport:{width:w,height:h},isMobile:mob,hasTouch:mob,colorScheme:scheme}); const p=await c.newPage(); const errs=[];
 p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.route('**/cdnjs.cloudflare.com/**',r=>r.fulfill({path:R+'/node_modules/leaflet/dist/leaflet.js',contentType:'application/javascript'}));
 await p.route('**/fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 await p.route('**/raw.githubusercontent.com/**',r=>r.fulfill({path:R+'/data.json',contentType:'application/json'}));
 await p.route('**/s3.tradingview.com/**',r=>r.fulfill({body:'',contentType:'application/javascript'}));
 await p.goto('file://'+R+'/site/index.html'); await p.waitForTimeout(1500);
 const pins=await p.$$eval('#globe path.leaflet-interactive',e=>e.length);
 const head=await p.evaluate(()=>({title:document.title,icons:[...document.head.querySelectorAll('link[rel*=icon]')].length,og:!!document.head.querySelector('meta[property="og:image"]'),bodyLinks:document.body.querySelectorAll('link,title,meta').length}));
 await p.screenshot({path:R+'/shots-'+tag+'.png'});
 await p.click('#tab-stocks'); await p.waitForTimeout(400);
 const rows=await p.$$eval('#list tr.row',e=>e.length);
 await p.click('#list tr.row'); await p.waitForTimeout(300);
 const det=await p.textContent('#detail h2').catch(()=>'?');
 await p.click('#tab-news'); await p.waitForTimeout(300); const news=await p.$$eval('#feed .item',e=>e.length);
 const hs=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 console.log(tag,JSON.stringify({errs,pins,rows,det,news,hscroll:hs,head})); await c.close();}
await b.close();})();
