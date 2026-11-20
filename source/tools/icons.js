const { chromium } = require('playwright'); const fs=require('fs'); const R=__dirname+'/..';
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'}); const svg=fs.readFileSync(R+'/icon.svg','utf8');
for (const [n,name] of [[16,'favicon-16.png'],[180,'apple-touch-icon.png']]){ const p=await b.newPage({viewport:{width:n,height:n}});
 await p.setContent(`<html><body style="margin:0;background:#0E2033">${svg.replace('<svg ','<svg width="'+n+'" height="'+n+'" ')}</body></html>`);
 await p.screenshot({path:R+'/site/'+name}); await p.close();}
await b.close();})();
