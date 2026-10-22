import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const g=read('data/game.json');
assert.equal(g.properties.length,32);assert.equal(g.cards.length,72);assert.equal(g.roles.length,6);
assert.deepEqual(g.denominations,[100,200,500,1000,2000,5000,10000]);
assert.equal(g.cards.reduce((a,c)=>a+c.copies,0),96);
for(const rows of [g.properties,g.cards,g.roles,g.banknotes]){
 assert.equal(new Set(rows.map(r=>r.name)).size,rows.length);
 for(const r of rows)assert.equal([...r.name].length,4,r.name);
}
for(const s of g.streets){assert.equal([...s.name].length,2);assert.equal([...s.abilityName].length,4);assert.equal(g.properties.filter(p=>p.street===s.id).length,4);}
for(const p of g.properties){assert.equal(p.price/2,p.sale);for(const n of [p.price,p.upgrade,p.sale,p.upgrade/2,...p.rents])assert.equal(n%100,0);}
for(const c of g.cards){assert.equal([...c.type].length,3);assert.ok(c.effect);}
for(const r of g.roles)assert.equal([...r.skill].length,4);
assert.equal(g.map.length,48);assert.equal(g.map.filter(m=>m.id).length,32);
assert.equal(new Set(g.map.filter(m=>m.id).map(m=>m.id)).size,32);
assert.equal(g.map.filter(m=>!m.id).length,16);
assert.equal(5000+2*2000+2*1000+500+2*200+100,g.startingCash);
assert.equal(g.startingCash,12000);
const jobs=read('data/image-jobs.json');assert.equal(jobs.length,154);assert.equal(new Set(jobs.map(j=>j.id)).size,154);
const panels=jobs.filter(j=>j.kind==='map-tile');
assert.equal(panels.length,16);
assert.equal(new Set(panels.map(p=>p.col+','+p.row)).size,16);
assert.deepEqual(panels.flatMap(p=>p.cells.map(c=>c.index)).sort((a,b)=>a-b),Array.from({length:48},(_,i)=>i));
const generated=jobs.filter(j=>fs.existsSync(path.join(root,'assets/final',j.id+'.png')));
const report={data:'PASS',properties:32,cardTypes:72,physicalEventCards:96,roles:6,denominations:7,uniqueImagesExpected:154,uniqueImagesPresent:generated.length,missing:jobs.filter(j=>!generated.includes(j)).map(j=>j.id)};
const ocrPath=path.join(root,'data/ocr-results.json');
if(fs.existsSync(ocrPath)){
 const raw=read('data/ocr-results.json'),ocr=Array.isArray(raw)?raw:[raw];
 const normalize=s=>s.replace(/[\s，。、；：！？,.!?;:·“”"'\/（）()\-]/g,'');
 report.ocr=jobs.filter(j=>generated.includes(j)).map(j=>{
  const row=ocr.find(r=>r.id===j.id);if(!row)return {id:j.id,status:'not_scanned'};
  if(row.error)return {id:j.id,status:'ocr_error',error:row.error};
  const requirements=[];
  if(j.face==='front'&&j.kind!=='map')requirements.push(j.name);
  if(j.propertyId){const p=g.properties.find(p=>p.id===j.propertyId);requirements.push(String(p.price),String(p.upgrade),...p.rents.map(String),String(p.sale));}
  if(j.cardId){const c=g.cards.find(c=>c.id===j.cardId);requirements.push(c.type,c.timing,c.effect);}
  if(j.roleId){const r=g.roles.find(r=>r.id===j.roleId);requirements.push(r.skill,r.effect);}
  if(j.amount)requirements.push(String(j.amount),'游戏代币');
  if(j.streetId){const s=g.streets.find(s=>s.id===j.streetId);requirements.push(...s.names,s.abilityName,s.ability);}
  if(j.kind==='map-tile')requirements.push(...j.cells.map(m=>m.name));
  const text=normalize(row.text||'');
  const missing=requirements.filter(t=>!text.includes(normalize(t)));
  return {id:j.id,status:missing.length?'needs_visual_review':'ocr_match',missing,width:row.width,height:row.height};
 });
}
fs.writeFileSync(path.join(root,'data/validation.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,missing:report.missing.length,ocr:report.ocr?{match:report.ocr.filter(x=>x.status==='ocr_match').length,review:report.ocr.filter(x=>x.status!=='ocr_match').length}:undefined},null,2));
