const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
(async()=>{
 const b=await chromium.launch({args:['--disable-web-security']});const p=await b.newPage({viewport:{width:2160,height:3840}});
 p.on('console',m=>console.log('PAGE',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('http://127.0.0.1:8765/tw.html');await p.evaluate(()=>window.ready);
 const mode=process.argv[2];
 if(mode==='meta'){fs.writeFileSync('meta.json',JSON.stringify(await p.evaluate(()=>({keys:KEYS,dings:DINGS}))));}
 else if(mode==='preview'){const ts=process.argv[3].split(',').map(Number);
   for(const t of ts){const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.8)},t);
     fs.writeFileSync(`prev_${t}.jpg`,Buffer.from(d.split(',')[1],'base64'));}}
 else { // full render piped to ffmpeg
   const N=Math.round(31.0*30);
   const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','slow','-crf','15','-pix_fmt','yuv420p','-profile:v','high','-level','5.2','video.mp4'],{stdio:['pipe','inherit','inherit']});
   for(let i=0;i<N;i++){const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.96)},i/30);
     const buf=Buffer.from(d.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
     if(i%60==0)console.log('frame',i);}
   ff.stdin.end();await new Promise(r=>ff.on('close',r));}
 await b.close();
})();
