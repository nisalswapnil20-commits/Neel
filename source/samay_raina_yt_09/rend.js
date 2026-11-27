// usage: node rend.js [comma-separated times] [outdir]
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('console',m=>console.log('page:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/typo.html');await p.evaluate(()=>window.ready);
 fs.writeFileSync(__dirname+'/events.json',JSON.stringify(await p.evaluate(()=>window.EVENTS)));
 const times=process.argv[2]?process.argv[2].split(',').map(Number):[...Array(786).keys()].map(i=>i/30);
 const dir=process.argv[3]||'ov'; fs.mkdirSync(dir,{recursive:true});
 for(let i=0;i<times.length;i++){
  const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/png')},times[i]);
  fs.writeFileSync(`${dir}/${String(i).padStart(4,'0')}.png`,Buffer.from(d.split(',')[1],'base64'));
 }
 await b.close();
})();
