const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('console',m=>console.log('PAGE',m.text()));p.on('pageerror',e=>console.log('ERR',e));
 await p.goto('file://'+__dirname+'/tw.html');await p.evaluate(()=>window.ready);
 fs.writeFileSync(__dirname+'/clicks.json',JSON.stringify(await p.evaluate(()=>window.CLICKS)));
 const out=process.argv[3]||'frames';fs.mkdirSync(out,{recursive:true});
 const times=process.argv[2]&&process.argv[2]!=='all'?process.argv[2].split(',').map(Number):[...Array(Math.round(21.6*30)).keys()].map(i=>i/30);
 for(let i=0;i<times.length;i++){
  const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',0.95)},times[i]);
  fs.writeFileSync(`${out}/${String(i).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64'));
 }
 await b.close();
})();
