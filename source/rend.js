const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+__dirname+'/typo.html');await p.evaluate(()=>window.ready);
 const times=process.argv[2]?process.argv[2].split(',').map(Number):[...Array(327).keys()].map(i=>i/30);
 fs.mkdirSync(process.argv[3]||'ov',{recursive:true});
 for(let i=0;i<times.length;i++){
  const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/png')},times[i]);
  fs.writeFileSync(`${process.argv[3]||'ov'}/${String(i).padStart(4,'0')}.png`,Buffer.from(d.split(',')[1],'base64'));
 }
 await b.close();
})();
