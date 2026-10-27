/** Local-only review player; deliberately serves only the two named film outputs. */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const allowed=new Map([
 ['/draft.mp4','HYDROOVERITY_M10_DRAFT_540P.mp4'],
 ['/master.mp4','HYDROOVERITY_M10_MASTER_1080P.mp4'],
]);
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://127.0.0.1');
 if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405).end();return;}
 if(url.pathname==='/'){
  const master=fs.existsSync(path.join(root,'renders',allowed.get('/master.mp4')));
  const media=master?'/master.mp4':'/draft.mp4';
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Content-Security-Policy':"default-src 'self'; style-src 'unsafe-inline'; media-src 'self'; frame-ancestors 'none'"});
  res.end(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>HYDROOVERITY · M10 film review</title><style>body{margin:0;background:#071623;color:#f5fafd;font:18px system-ui}main{max-width:1200px;margin:36px auto;padding:0 24px}h1{letter-spacing:-1px}p{color:#b6cbd5;line-height:1.5}video{width:100%;background:#000;border:1px solid #315364}a{color:#36c6e9}strong{color:#f5b64a}</style><main><h1>HYDROOVERITY · M10</h1><p>${master?'1080p production render':'540p timing draft'} · Team TARK · SIH26254</p><video controls preload="metadata" src="${media}" aria-label="HYDROOVERITY narrated engineering film"></video><p><strong>Owner review copy.</strong> Digital design and simulations, not physically validated hardware. Separate authentic synthetic software tests are labeled. Captions and listening review remain provisional until documented in the production QA.</p><p><a href="${media}" download>Download this MP4</a></p></main></html>`);return;
 }
 const filename=allowed.get(url.pathname);
 if(!filename){res.writeHead(404).end();return;}
 const file=path.join(root,'renders',filename);
 if(!fs.existsSync(file)){res.writeHead(404).end('Render not complete');return;}
 const size=fs.statSync(file).size;
 let start=0,end=size-1,status=200;
 if(req.headers.range){
  const m=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);
  if(!m){res.writeHead(416,{'Content-Range':`bytes */${size}`}).end();return;}
  start=Number(m[1]);end=m[2]?Number(m[2]):end;
  if(start>end||start>=size||end>=size){res.writeHead(416,{'Content-Range':`bytes */${size}`}).end();return;}
  status=206;
 }
 res.writeHead(status,{'Content-Type':'video/mp4','Accept-Ranges':'bytes','Content-Length':end-start+1,...(status===206?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});
 if(req.method==='HEAD'){res.end();return;}
 fs.createReadStream(file,{start,end}).pipe(res);
});
server.listen(3101,'127.0.0.1',()=>console.log('M10 owner review: http://127.0.0.1:3101'));
