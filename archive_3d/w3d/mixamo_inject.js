(async()=>{
const GLB='https://pikaso.cdnpk.net/private/production/6098850697/hero-rigged.glb?token=exp=1795478400~hmac=c8cf549c22c22d01edde03bda8c8168edb02fcca24bfa0dadfff03a00a757c8d';
const TEX='https://pikaso.cdnpk.net/private/production/6098850852/3896354863.jpg?token=exp=1795478400~hmac=f3259d9d334e02e9f69226890198b1c74d25d82861bb44ab3889f69b08bc23ba';
const buf=await (await fetch(GLB)).arrayBuffer();const tex=new Uint8Array(await (await fetch(TEX)).arrayBuffer());
const dv=new DataView(buf);const jl=dv.getUint32(12,true);const j=JSON.parse(new TextDecoder().decode(new Uint8Array(buf,20,jl)));const B=20+jl+8;
const NC={SCALAR:1,VEC2:2,VEC3:3,VEC4:4};
function acc(i){const a=j.accessors[i],bv=j.bufferViews[a.bufferView];const off=B+(bv.byteOffset||0)+(a.byteOffset||0);const n=a.count*NC[a.type];
 if(a.componentType===5126)return new Float32Array(buf.slice(off,off+n*4));if(a.componentType===5125)return new Uint32Array(buf.slice(off,off+n*4));if(a.componentType===5123)return new Uint16Array(buf.slice(off,off+n*2));}
const pr=j.meshes[0].primitives[0];const P=acc(pr.attributes.POSITION),N=acc(pr.attributes.NORMAL),T=acc(pr.attributes.TEXCOORD_0),I=acc(pr.indices);
const L=['mtllib hero.mtl','o hero'];const nv=P.length/3;
for(let i=0;i<nv;i++){const x=P[i*3],y=P[i*3+1],z=P[i*3+2];L.push(`v ${(-z*170).toFixed(4)} ${(y*170).toFixed(4)} ${(x*170).toFixed(4)}`);}
for(let i=0;i<nv;i++)L.push(`vt ${T[i*2].toFixed(6)} ${(1-T[i*2+1]).toFixed(6)}`);
for(let i=0;i<nv;i++){const x=N[i*3],y=N[i*3+1],z=N[i*3+2];L.push(`vn ${(-z).toFixed(4)} ${y.toFixed(4)} ${x.toFixed(4)}`);}
L.push('usemtl skin');for(let t=0;t<I.length;t+=3){const a=I[t]+1,b=I[t+1]+1,c=I[t+2]+1;L.push(`f ${a}/${a}/${a} ${b}/${b}/${b} ${c}/${c}/${c}`);}
const enc=new TextEncoder();const files=[['hero.obj',enc.encode(L.join('\n'))],['hero.mtl',enc.encode('newmtl skin\nKd 1 1 1\nmap_Kd hero_tex.jpg\n')],['hero_tex.jpg',tex]];
const crcT=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;crcT[n]=c>>>0;}
const crc=d=>{let c=0xFFFFFFFF;for(let i=0;i<d.length;i++)c=crcT[(c^d[i])&255]^(c>>>8);return (c^0xFFFFFFFF)>>>0;};
const parts=[],cen=[];let off=0;
for(const [name,data] of files){const nm=enc.encode(name);const c=crc(data);
 const h=new DataView(new ArrayBuffer(30));h.setUint32(0,0x04034b50,true);h.setUint16(4,20,true);h.setUint32(14,c,true);h.setUint32(18,data.length,true);h.setUint32(22,data.length,true);h.setUint16(26,nm.length,true);
 parts.push(new Uint8Array(h.buffer),nm,data);
 const ch=new DataView(new ArrayBuffer(46));ch.setUint32(0,0x02014b50,true);ch.setUint16(4,20,true);ch.setUint16(6,20,true);ch.setUint32(16,c,true);ch.setUint32(20,data.length,true);ch.setUint32(24,data.length,true);ch.setUint16(28,nm.length,true);ch.setUint32(42,off,true);
 cen.push(new Uint8Array(ch.buffer),nm);off+=30+nm.length+data.length;}
const cenSize=cen.reduce((s,a)=>s+a.length,0);const e=new DataView(new ArrayBuffer(22));e.setUint32(0,0x06054b50,true);e.setUint16(8,files.length,true);e.setUint16(10,files.length,true);e.setUint32(12,cenSize,true);e.setUint32(16,off,true);
window.__heroZip=new File([...parts,...cen,new Uint8Array(e.buffer)],'hero.zip',{type:'application/zip'});
return 'zip ready '+window.__heroZip.size;
})()
