import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const g=JSON.parse(fs.readFileSync(path.join(root,'data/game.json'),'utf8'));
const jobs=JSON.parse(fs.readFileSync(path.join(root,'data/image-jobs.json'),'utf8')).filter(j=>!j.kind.startsWith('map'));
const positions=[[0,0],[1,0],[2,0],[3,0],[3,1],[3,2],[3,3],[2,3],[1,3],[0,3],[0,2],[0,1]];
const common='One COMPLETE FINISHED SQUARE TILE of an illustrated Chinese fantasy board game called 百妖夜市. Square 1:1, highest native resolution available, 2048x2048 or greater if supported. This tile will be joined edge-to-edge to other whole finished tiles. All Chinese names and numbers must be generated INSIDE this image; NO later text will be added. Exquisite refined watercolor and gouache storybook illustration, midnight indigo, warm gold lanterns, friendly yokai spirits, rich fine architecture, ornate thin gold outer frame. Flat overhead game component, not a photographed object. No perspective distortion of printed cells, no white outer margins, no shadows, no English, no gibberish. All printed Chinese must match supplied text exactly. Use generous clear ivory areas behind text and very readable dark Chinese characters. ';
const layouts={
0:'The path bends from the BOTTOM LEFT edge toward the TOP RIGHT edge. EXACTLY FOUR track cells. Cell 0 at lower-left immediately below cell 1; cells 1, 2, 3 form a left-to-right row along the top edge. Connect 0 upward to 1 then right to 2 then right to 3. Other area is decorative market artwork. Do not create a fifth cell.',
3:'The path bends from the TOP LEFT edge toward the BOTTOM RIGHT edge. EXACTLY FOUR track cells: cells 0, 1, 2 in a left-to-right row along the top edge, cell 3 immediately below cell 2 at right. Connect 0 to 1 to 2 then downward to 3. Other area decorative. No fifth cell.',
6:'The path bends from TOP RIGHT edge toward BOTTOM LEFT edge. EXACTLY FOUR track cells: cell 0 upper-right immediately above cell 1; cells 1, 2, 3 run right-to-left along bottom edge. Connect downward then left. Other area decorative. No fifth cell.',
9:'The path bends from BOTTOM RIGHT edge toward TOP LEFT edge. EXACTLY FOUR track cells: cells 0, 1, 2 run right-to-left along bottom edge; cell 3 immediately above cell 2 at left. Connect left then upward. Other area decorative. No fifth cell.'
};
for(let k=0;k<12;k++){
 const [col,row]=positions[k],cells=g.map.slice(k*4,k*4+4);
 let layout=layouts[k];
 if(!layout)layout=k<3?'EXACTLY FOUR equal-size track cells in a LEFT-TO-RIGHT row along the TOP edge, joined by clockwise arrows. Lower area is decorative street panorama.':k<6?'EXACTLY FOUR equal-size track cells in a TOP-TO-BOTTOM column along the RIGHT edge, joined by clockwise arrows. Left area is decorative street panorama.':k<9?'EXACTLY FOUR equal-size track cells in a RIGHT-TO-LEFT row along the BOTTOM edge, joined by clockwise arrows. Upper area is decorative street panorama.':'EXACTLY FOUR equal-size track cells in a BOTTOM-TO-TOP column along the LEFT edge, joined by clockwise arrows. Right area is decorative street panorama.';
 const instructions=cells.map((c,i)=>'Local cell '+i+' must contain EXACT number "'+c.index+'" and EXACT name "'+c.name+'", each printed ONCE.').join(' ');
 const subjects=cells.map(c=>c.name).join('、');
 jobs.push({id:'map_tile_'+String(k+1).padStart(2,'0'),kind:'map-tile',name:'地图分区'+(k+1),face:'front',col,row,cells,prompt:common+layout+' The words "cell" and local cell indices are instructions, NOT text to print. '+instructions+' Draw miniature illustrations matching these four places: '+subjects+'. Only the supplied FOUR global indices and FOUR Chinese names may appear as text. No other numbers, labels, titles, captions or extra cells. Make cells distinct and numbered in the exact traversal order. Use midnight-blue and warm-gold connecting streets to align with neighboring tiles. Large legible Chinese text, decorative corners must not look like additional track cells.'});
}
const centers=[
 [1,1,'百妖夜市','A magnificent moonlit fox perfume district and tanuki food district overlooking a small canal, lanterns and friendly spirits. One large beautifully readable golden title 百妖夜市. No track cells.'],
 [2,1,'月圆开市','A luminous full moon above an ivory paper lantern district and violet silk district, arched canal bridge, paper cranes. One clear small poetic title 月圆开市. No track cells.'],
 [1,2,'百妖争金','An emerald jade curiosity street and sapphire mirror theatre around a reflecting pond, charming shoppers. One clear small poetic title 百妖争金. No track cells.'],
 [2,2,'灯火长明','Crimson wine taverns and turquoise dragon canal inns, magical trading boats and gold lantern reflections. One clear small poetic title 灯火长明. No track cells.']
];
centers.forEach(([col,row,name,desc],i)=>jobs.push({id:'map_tile_'+(13+i),kind:'map-tile',name,face:'front',col,row,cells:[],prompt:common+'Complete decorative inner map tile. '+desc+' All paths lead naturally toward the center of a large fantasy market. Soft scenic borders, thin gold line at outer edge. The only text is "'+name+'".'}));
fs.writeFileSync(path.join(root,'data/image-jobs.json'),JSON.stringify(jobs,null,2));
fs.writeFileSync(path.join(root,'data/map-tiles.json'),JSON.stringify(jobs.filter(j=>j.kind==='map-tile'),null,2));
console.log(jobs.length+' total images, 16 complete map panels');
