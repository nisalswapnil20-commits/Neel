const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const caps=JSON.parse(fs.readFileSync('../caps2.json','utf8'));
const TITLES=JSON.parse(process.env.ONLY||'null')||[['hook',0.15,3.0],['clock',8.35,10.34],['london',92.0,95.5],['rankdown',116.6,119.72],['rankup',135.8,139.22],['vs',139.3,142.88],['mp',155.6,157.6],['gold',169.25,173.22],['end',173.22,175.94]];
(async()=>{
 const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:2160,height:700}});
 await p.goto('file://'+path.resolve('overlay.html')); await p.evaluate(()=>document.fonts.ready);
 await p.waitForTimeout(500);
 fs.mkdirSync('cap',{recursive:true});
 if(process.env.ONLY){} else {
 let list=[];let idx=0;let tcur=0;
 const blank='cap/blank.png'; await p.evaluate(()=>setCap([],0)); await p.screenshot({path:blank,omitBackground:true});
 const push=(f,until)=>{ if(until-tcur>0.0005){list.push([f,until-tcur]);tcur=until;} };
 for(const c of caps){
   const st=c.t[0]; if(st>=173.22) break;
   push(blank,st);
   for(let n=1;n<=c.words.length;n++){
     const until = n<c.words.length ? c.t[n] : Math.min(c.end,173.22);
     const f=`cap/c${String(idx++).padStart(4,'0')}.png`;
     await p.evaluate(([w,n])=>setCap(w,n),[c.words,n]); await p.screenshot({path:f,omitBackground:true});
     push(f,until);
   }
 }
 push(blank,175.94);
 fs.writeFileSync('caps.txt', list.map(([f,d])=>`file '${f}'\nduration ${d.toFixed(4)}`).join('\n')+`\nfile '${blank}'\n`);
 console.log('caption states',idx);}
 // titles
 await p.setViewportSize({width:2160,height:3840});
 for(const [name,s,e] of TITLES){
   fs.mkdirSync('t_'+name,{recursive:true});
   await p.evaluate(n=>setTitle(n),name);
   const nf=Math.round((e-s)*30);
   for(let i=0;i<nf;i++){
     let ms=i/30*1000; const out=(e-s)*1000-ms;
     await p.evaluate(m=>seek(m),ms);
     const op = (name=='end')?1:Math.min(1,out/300);   // fade out last 0.3s
     await p.evaluate(o=>{document.getElementById('title').style.opacity=o},op);
     await p.screenshot({path:`t_${name}/${String(i).padStart(4,'0')}.png`,omitBackground:true});
   }
   await p.evaluate(()=>{document.getElementById('title').style.opacity=1});
   console.log(name,nf);
 }
 await b.close();
})();
