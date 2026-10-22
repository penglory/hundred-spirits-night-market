import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const g=JSON.parse(fs.readFileSync(path.join(root,'data/game.json'),'utf8'));
const jobs=JSON.parse(fs.readFileSync(path.join(root,'data/image-jobs.json'),'utf8'));
const assets=[];
function copy(source,target,meta){
 if(!fs.existsSync(source))return;
 fs.mkdirSync(path.dirname(target),{recursive:true});fs.copyFileSync(source,target);
 const png=fs.readFileSync(target);
 assets.push({...meta,file:path.relative(root,target).replaceAll('\\','/'),width:png.readUInt32BE(16),height:png.readUInt32BE(20),sha256:crypto.createHash('sha256').update(png).digest('hex'),bytes:png.length});
}
for(const j of jobs.filter(j=>['property','event','role','reference-card'].includes(j.kind))){
 const id=j.id.replace('_front','');
 for(const face of ['front','back']){
  const src=path.join(root,'assets/final',(face==='front'?j.id:j.backId)+'.png');
  copy(src,path.join(root,'output/cards',id+'_'+j.name+'_'+(face==='front'?'正面':'背面')+'.png'),{id,name:j.name,kind:j.kind,face,backKey:j.backId,copies:j.copies||1});
 }
}
for(const j of jobs.filter(j=>j.kind==='banknote'))copy(path.join(root,'assets/final',j.id+'.png'),path.join(root,'output/currency',j.amount+'_'+j.name+'_'+(j.face==='front'?'正面':'背面')+'.png'),{id:j.id,name:j.name,kind:j.kind,face:j.face,amount:j.amount,copies:j.copies});
for(const j of jobs.filter(j=>j.kind==='map-tile'))copy(path.join(root,'assets/final',j.id+'.png'),path.join(root,'output/map/分区',j.id+'.png'),{id:j.id,name:j.name,kind:'map-tile',face:'front',col:j.col,row:j.row});
const manifest={version:g.version,creationMethod:'卡片与纸币直接生成完整正反面。地图由16块包含格名和编号的完整生成分区拼接；所有图片均未后加名称、金额或规则。PDF仅拼放整张原图。',generatedCount:jobs.filter(j=>fs.existsSync(path.join(root,'assets/final',j.id+'.png'))).length,expectedUniqueImages:154,expectedPairedFiles:252,assets};
fs.writeFileSync(path.join(root,'data/asset-manifest.json'),JSON.stringify(manifest,null,2));
const e=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const fronts=assets.filter(a=>a.face==='front'&&!a.kind.startsWith('map'));
const entries=fronts.map(a=>{
 const back=assets.find(b=>b.face==='back'&&b.name===a.name);
 return '<figure data-kind="'+a.kind+'" data-name="'+e(a.name)+'"><a href="'+e(a.file)+'" target="_blank"><img loading="lazy" src="'+e(a.file)+'" data-front="'+e(a.file)+'" data-back="'+e(back?.file||a.file)+'" alt="'+e(a.name)+'"></a><figcaption><b>'+e(a.name)+'</b><span>'+e(a.id)+' · '+a.width+' × '+a.height+'</span></figcaption></figure>';
}).join('\n');
const html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>百妖夜市 · 成品图鉴</title><style>body{margin:0;background:#121c30;color:#f7eed9;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}header,main{max-width:1500px;margin:auto;padding:32px}h1{font-family:serif;font-size:48px;letter-spacing:.15em;margin:0;color:#edcb84}p{color:#c6c9ce}nav{display:flex;flex-wrap:wrap;gap:10px;align-items:center}input,select,button{font:inherit;padding:8px 14px;border:1px solid #5b6173;border-radius:4px;background:#202b40;color:#f7eed9}button{cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:24px}figure{margin:0}img{width:100%;display:block;object-fit:contain}figure[data-kind=banknote]{grid-column:span 2}figcaption{display:flex;justify-content:space-between;gap:10px;padding:8px 0}figcaption span{font-size:12px;color:#a9afbd}.map{max-width:1000px;margin:20px auto 50px}a{color:#edcb84}aside{border-left:3px solid #cfad69;padding:10px 18px;background:#1b263a;margin:20px 0}h2{font-weight:500}figure[hidden]{display:none}@media(max-width:620px){header,main{padding:18px}h1{font-size:34px}figure[data-kind=banknote]{grid-column:auto}}</style><header><h1>百妖夜市</h1><p>整张直接生成 · 32处地产 · 72种功能牌 · 6位商主 · 七种灵钱</p><aside>卡面文字与画面一次生成，没有后期补字。地产背面按八街复用，三类功能牌各共用一款背面，商主共用一款背面。每种纸币拥有独立正反面。原图尺寸以各卡下方标注为准。</aside><nav><input id="q" placeholder="查找名称" aria-label="查找名称"><select id="kind" aria-label="卡牌类型"><option value="">全部</option><option value="property">地产卡</option><option value="event">功能牌</option><option value="role">商主卡</option><option value="banknote">灵钱</option></select><button id="flip">显示背面</button><span id="count"></span></nav></header><main><h2>夜市全图</h2><div class="map"><a href="output/map/百妖夜市_地图原图.png" target="_blank"><img loading="lazy" src="output/map/百妖夜市_地图原图.png" alt="百妖夜市地图"></a></div><h2>成品正反面</h2><div class="grid">'+entries+'</div></main><script>const all=[...document.querySelectorAll("figure")],q=document.querySelector("#q"),k=document.querySelector("#kind");function filter(){let n=0;for(const f of all){f.hidden=!(f.dataset.name.includes(q.value.trim())&&(!k.value||f.dataset.kind===k.value));if(!f.hidden)n++}document.querySelector("#count").textContent=n+"款"}q.oninput=filter;k.onchange=filter;filter();let back=false;document.querySelector("#flip").onclick=()=>{back=!back;for(const f of all){const im=f.querySelector("img");im.src=back?im.dataset.back:im.dataset.front;f.querySelector("a").href=im.src}document.querySelector("#flip").textContent=back?"显示正面":"显示背面"};</script></html>';
fs.writeFileSync(path.join(root,'成品图鉴.html'),html.replaceAll('output/map/百妖夜市_地图原图.png','output/map/百妖夜市_完整地图.png'));
console.log(JSON.stringify({uniqueImages:manifest.generatedCount,pairedFiles:assets.length,gallery:'成品图鉴.html'}));
