import fs from 'fs';
const b=fs.readFileSync('hero.glb');const len=b.readUInt32LE(12);const j=JSON.parse(b.slice(20,20+len).toString());
console.log('meshes',j.meshes.map(m=>m.name+':'+m.primitives.length));
console.log('skins',j.skins?.map(s=>s.joints.length));
console.log('nodes',j.nodes.map((n,i)=>i+':'+n.name).join(' | '));
console.log('anims',j.animations?.map(a=>a.name));
console.log('materials',JSON.stringify(j.materials));
console.log('images',j.images?.map(i=>i.mimeType), 'accessor count verts', j.accessors[j.meshes[0].primitives[0].attributes.POSITION].count);
