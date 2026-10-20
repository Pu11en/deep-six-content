// D6-6c917b49743b, 27.20–40.55. Style C. Absolute narration time.
// Illustrative rooms and scales, not a measured nest or physiological model.
import {
  W, H, C, Path2D, createCanvas, rng, clamp, lerp, eOut, eIO, eBack,
  prog, makeFibres, cut, polyPath, smoothPath, ovalPath, capsulePath,
  bandPath, withCamera, placeAnt, walkPhase, tuft, drawLarva, drawEgg,
  drawPupa, createCaptions, mix,
} from './paper-kit.mjs';
import { createNest, CHAMBERS } from './nest-world.mjs';

const START = 27.2;
const END = 40.55;
const TAU = Math.PI * 2;
const SHOTS = [27.2,28.26,29.28,30.08,31.15,32.06,32.99,33.8,34.64,35.9,37.02,37.62,38.3,38.98,39.66,40.55];
const BACK = polyPath([[-1800,-1800],[3000,-1800],[3000,3800],[-1800,3800]]);
const CLOUD = smoothPath([[-190,40],[-180,-20],[-130,-35],[-115,-100],[-35,-115],[15,-75],[80,-95],[135,-45],[180,-38],[210,30],[170,68],[-140,65]]);
const DROP = new Path2D('M0 -30 C-7 -15 -18 0 -15 10 C-10 29 14 27 17 10 C20 0 6 -17 0 -30 Z');

function antennae(t, seed=0, lift=0) {
  return [[lift + .10*Math.sin(t*8+seed), .08*Math.sin(t*6+seed)],
    [lift + .09*Math.sin(t*7+seed+1), .1*Math.cos(t*5+seed)]];
}

export function createScene(config, timing) {
  const texture = makeFibres(config.seed ?? 20261019);
  const nest = createNest(texture, 7);
  const captions = createCaptions(timing.words, timing.caption_groups, { texture, centerY: config.caption_center_y ?? 1420 });
  const random = rng(1207);
  const pebbles = Array.from({length:75},()=>({x:-500+random()*2100,y:180+random()*2080,r:5+random()*17,a:random()*3,color:[C.soilPale,C.soilDark,'#C58B62'][Math.floor(random()*3)]}));
  const rain = Array.from({length:42},(_,i)=>({x:-220+i*39,phase:random(),speed:.85+random()*.6}));
  const weatherDome = smoothPath([[230,768],[260,733],[290,692],[325,648],[375,603],[420,567],[475,541],[535,525],[588,539],[640,561],[687,597],[735,638],[779,690],[815,742],[850,768]]);
  const strata = [
    [bandPath(-1800,3000,220,3800,15,41),C.soil],
    [bandPath(-1800,3000,1110,3800,12,42),'#9B674C'],
    [bandPath(-1800,3000,1530,3800,15,43),'#805443'],
  ];
  const cavern = smoothPath([[-230,1040],[-200,580],[-50,320],[260,270],[700,285],[1100,400],[1280,780],[1200,1045],[800,1110],[200,1090]]);
  const cavernInner = smoothPath([[-200,1025],[-160,610],[0,370],[280,320],[700,335],[1070,445],[1210,780],[1150,1030],[800,1060],[200,1050]]);
  const nurseryFloor = bandPath(-1800,3000,1045,3800,5,44);
  const rampFloor = polyPath([[-1800,2112],[3000,-192],[3000,3800],[-1800,3800]]);
  const rampRim = polyPath([[-1800,2112],[3000,-192],[3000,-167],[-1800,2137]]);
  const soilCells = [];
  for (let row=0;row<7;row++) for(let col=0;col<10;col++) {
    const x=-430+col*194+(row%2)*92, y=280+row*190;
    const points=Array.from({length:8},(_,i)=>{
      const a=i*TAU/8, r=.85+random()*.18;
      return [x+Math.cos(a)*117*r,y+Math.sin(a)*109*r];
    });
    soilCells.push({path:polyPath(points),x,y,color:['#805643','#A47452','#916148','#BD8A62'][Math.floor(random()*4)]});
  }

  // Cache the invariant paper set, keeping moving pieces and camera transforms live.
  const nursery = createCanvas(1800,2700);
  const nctx = nursery.getContext('2d');
  nctx.translate(360,260);
  cut(nctx,BACK,C.soil,texture,0);
  for(const [p,c] of strata) cut(nctx,p,c,texture,8);
  for(const p of pebbles) cut(nctx,ovalPath(p.x,p.y,p.r,p.r*.6,p.a),p.color,texture,2);
  cut(nctx,cavern,C.tunnel,texture,14);
  cut(nctx,cavernInner,'#D8BD91',texture,6);
  cut(nctx,smoothPath([[-200,1020],[0,910],[350,940],[720,900],[1180,1000],[1200,1120],[-200,1120]]),'#C59D70',texture,5);
  cut(nctx,nurseryFloor,C.soil,texture,9);
  for(let i=0;i<17;i++) cut(nctx,ovalPath(-80+i*80,1090+(i%3)*28,9+(i%4)*3,6),i%2?C.soilPale:C.soilDark,texture,2);

  function base(ctx,color=C.soil) { cut(ctx,BACK,color,texture,0); }
  function earth(ctx) {
    for(const [p,c] of strata) cut(ctx,p,c,texture,8);
    for(const p of pebbles) cut(ctx,ovalPath(p.x,p.y,p.r,p.r*.6,p.a),p.color,texture,2);
  }
  function room(ctx) { ctx.drawImage(nursery,-360,-260); }
  function dust(ctx,t,amount=1) {
    for(let i=0;i<12;i++) {
      const x=80+((i*173+t*22)%930), y=380+((i*127-t*32+5000)%550);
      ctx.save(); ctx.globalAlpha=.24*amount;
      cut(ctx,ovalPath(x,y,2+i%3,1.8),C.cream,texture,0); ctx.restore();
    }
  }
  function brood(ctx,t,large=true) {
    if(large) {
      cut(ctx,bandPath(-220,1280,914,960,4,91),C.soilPale,texture,7);
      drawLarva(ctx,texture,330,730,2.75,-.18,Math.sin(t*5)+.15*Math.sin(Math.PI*prog(t,27.54,27.88)));
      drawPupa(ctx,texture,730,870,.53,-.05,.6);
      for(let i=0;i<5;i++) drawEgg(ctx,texture,625+(i%3)*47,1015-Math.floor(i/3)*51,28,.25+i*.24);
    } else {
      cut(ctx,bandPath(-220,1280,745,800,4,92),C.soilPale,texture,7);
      drawLarva(ctx,texture,260,625,1.7,-.18,Math.sin(t*5));
      drawPupa(ctx,texture,715,704,.46,.02,.6);
      for(let i=0;i<4;i++) drawEgg(ctx,texture,405+i*34,724,21,.7);
    }
  }
  function nurse(ctx,t,x,y,s,dist,carry=null,rotation=0,look=0) {
    placeAnt(ctx,texture,x,y,s,{walk:1,phase:walkPhase(dist,s),carry,
      antennae:antennae(t,2,-.12-look),head:look*.22,mand:carry?.14:0}, {faceRight:true,rotation});
  }
  function chamberOccupants(ctx,t,ids=['M1','M2','M3']) {
    ids.forEach((id,i)=>{
      const c=CHAMBERS[id], distance=(t-START)*9;
      // Brood on the left, worker on the right; no intersecting bodies.
      drawLarva(ctx,texture,c.x-c.rx*.48,c.y+4,.21,-.25,Math.sin(t*5+i));
      drawEgg(ctx,texture,c.x-c.rx*.73,c.y+8,4.8,.3);
      const x=c.x+c.rx*.35+3*Math.sin(t*2+i);
      placeAnt(ctx,texture,x,c.y+c.ry*.65,.085,{walk:0,antennae:antennae(t,i),head:.03*Math.sin(t*5+i)});
    });
  }
  function cutaway(ctx,t,cam,state={}) {
    withCamera(ctx,cam,()=>{
      nest.draw(ctx,t,{mound:1,traffic:0,surfaceAnts:0,...state});
      chamberOccupants(ctx,t,state.ids??['M1','M2','M3']);
    });
  }
  function clouds(ctx,t,cold,part=0) {
    [[180,375,1.1],[620,330,1.3],[1040,385,.9]].forEach(([x,y,s],i)=>{
      ctx.save();ctx.translate(x+Math.sin(t*.9+i)*25+(i<1?-1:1)*part*650,y);
      ctx.scale(s,s);cut(ctx,CLOUD,mix('#D5DFDE','#8998A6',cold),texture,10);ctx.restore();
    });
  }
  function weather(ctx,t,wet,k) {
    base(ctx,'#BFCFD0');
    const cam=wet?{x:560+32*k,y:770+18*k,zoom:1.25+.11*k}:{x:530-22*k,y:740+28*k,zoom:1.13+.12*k};
    withCamera(ctx,cam,()=>{
      // Surface set only: the earth cover conceals the illustrative tunnels.
      nest.draw(ctx,t,{mound:1,traffic:0,tunnelsDraw:0,cold:1,wind:.7,rain:0});
      cut(ctx,weatherDome,C.soil,texture,12);
      ctx.save();ctx.clip(weatherDome);
      cut(ctx,smoothPath([[580,526],[690,580],[790,690],[850,780],[630,780],[640,650]]),'#94603F',texture,0);
      cut(ctx,smoothPath([[310,708],[395,604],[491,549],[550,549],[450,619],[365,726]]),'#CD966A',texture,0);
      for(let i=0;i<16;i++) cut(ctx,ovalPath(280+i*34,710-(i%3)*44,7+(i%3)*3,5),i%2?C.soilLight:C.soilDark,texture,2);
      ctx.restore();
      clouds(ctx,t,wet?1:eOut(prog(t,31.34,31.55)));
      if(wet) {
        for(const d of rain) {
          const u=((t-32.06)*1.7*d.speed+d.phase)%1;
          const y=420+u*335,x=d.x-u*65;
          cut(ctx,capsulePath([x,y],[x-10,y+29],3.8,3.2),C.water,texture,1);
        }
        for(const [x,r] of [[120,68],[890,76],[1040,50]]) {
          const spread=.8+.2*eOut(prog(t,32.06,32.34));
          cut(ctx,ovalPath(x,764,r*spread,10),C.water,texture,2);
          const phase=((t-32.22)*3+x*.017)%1;
          for(let i=0;i<3;i++) cut(ctx,ovalPath(x+(i-1)*18*(.4+phase),752-Math.sin(phase*Math.PI)*26,3,7),C.water,texture,1);
        }
      }
    });
  }
  function galleries(ctx,t,k) {
    base(ctx);withCamera(ctx,{x:510+70*k,y:1010-20*k,zoom:1+.055*k},()=>{
      earth(ctx);
      for(let row=0;row<2;row++) {
        const y=650+row*350;
        cut(ctx,smoothPath([[-400,y+20],[-260,y-195],[20,y-230],[450,y-215],[1100,y-225],[1350,y+20]]),C.tunnel,texture,10);
        cut(ctx,bandPath(-1800,3000,y, y+75,5,70+row),C.soilPale,texture,5);
        for(let col=0;col<3;col++) {
          const dist=(t-32.99)*74, x=200+col*275+dist;
          nurse(ctx,t+row,x,y,.29,dist,row===0&&col===0?'larva':null);
        }
      }
      dust(ctx,t);
    });
  }
  function ramp(ctx,t,k) {
    base(ctx);withCamera(ctx,{x:490+78*k,y:975-55*k,zoom:1.06+.08*k},()=>{
      earth(ctx);
      cut(ctx,polyPath([[-1800,1650],[3000,-654],[3000,-180],[-1800,2124]]),C.tunnel,texture,10);
      cut(ctx,polyPath([[-1800,1750],[3000,-554],[3000,-180],[-1800,2124]]),'#CDB183',texture,4);
      cut(ctx,rampFloor,C.soil,texture,12);cut(ctx,rampRim,C.soilPale,texture,4);
      const x=410+190*k,y=1248-x*.48;
      nurse(ctx,t,x,y,.82,190*k*Math.hypot(1,.48),'larva',-Math.atan(.48));
      for(let i=0;i<10;i++) cut(ctx,ovalPath(70+i*135,1300-(70+i*135)*.48,11,6,-.35),i%2?C.soilDark:C.soilPale,texture,2);
      dust(ctx,t);
    });
  }
  function sun(ctx,t,x,y,r) {
    ctx.save();ctx.translate(x,y);ctx.rotate(t*.64);
    for(let i=0;i<14;i++) {
      const a=i*TAU/14, rr=r*(i%2?1.6:1.85)*(1+.04*Math.sin(t*6+i));
      cut(ctx,polyPath([[Math.cos(a-.1)*r*1.03,Math.sin(a-.1)*r*1.03],[Math.cos(a)*rr,Math.sin(a)*rr],[Math.cos(a+.1)*r*1.03,Math.sin(a+.1)*r*1.03]]),i%2?C.sunRay:C.sunRay2,texture,4);
    }
    ctx.restore();cut(ctx,ovalPath(x,y,r,r),C.sun,texture,9);cut(ctx,ovalPath(x-r*.14,y-r*.15,r*.7,r*.66),C.sunHi,texture,1);
  }
  function wetSoil(ctx,t,top=250,bottom=1450) {
    ctx.save();ctx.beginPath();ctx.rect(-1500,top,4000,bottom-top);ctx.clip();
    cut(ctx,BACK,'#6F9EAF',texture,0);
    for(const c of soilCells) {
      ctx.save();ctx.translate(c.x,c.y);ctx.scale(.97+.015*Math.sin(t*2+c.y),.98);ctx.translate(-c.x,-c.y);
      cut(ctx,c.path,c.color,texture,8);
      cut(ctx,ovalPath(c.x-20,c.y-15,19,11,-.3),mix(c.color,C.soilPale,.4),texture,1);ctx.restore();
    }
    for(let i=0;i<12;i++) {
      const x=100+i*77+11*Math.sin(t*3+i), y=top+30+((t*70+i*89)%(bottom-top-60));
      ctx.save();ctx.globalAlpha=.6;cut(ctx,capsulePath([x,y],[x+4,y+18],2,3),'#C5E5EC',texture,1);ctx.restore();
    }
    ctx.restore();
  }
  function separation(ctx,t,k,closing=false) {
    base(ctx,'#D6E4DC');
    const z=closing?lerp(1.03,.94,k):lerp(1.1,.98,k);
    withCamera(ctx,{x:530+(closing?-15:20)*k,y:940+20*k,zoom:z},()=>{
      const dome=smoothPath([[-200,620],[120,620],[240,480],[390,385],[510,355],[650,390],[790,510],[870,620],[1400,620],[1400,2700],[-200,2700]]);
      cut(ctx,dome,C.soil,texture,12);
      cut(ctx,bandPath(-1500,2500,940,2800,9,81),C.soilDark,texture,7);
      wetSoil(ctx,t,1030,1580);
      cut(ctx,bandPath(-1500,2500,1250,2800,7,82),'#92634C',texture,5);
      // A real soil band separates the upper room from water-filled pores.
      cut(ctx,ovalPath(500,730,355,155),C.tunnel,texture,9);
      cut(ctx,ovalPath(500,740,325,125),'#CEAC7B',texture,4);
      cut(ctx,bandPath(160,840,825,865,4,83),C.soilPale,texture,4);
      drawLarva(ctx,texture,295,775,.69,-.15,Math.sin(t*5));
      drawLarva(ctx,texture,390,780,.61,.2,Math.sin(t*5+1));
      for(let i=0;i<4;i++) drawEgg(ctx,texture,470+(i%2)*25,805-Math.floor(i/2)*27,15,.6);
      const dist=(t-38.3)*16;
      placeAnt(ctx,texture,670+7*Math.sin(t),825,.32,{walk:0,antennae:antennae(t),head:.06*Math.sin(t*5)});
      for(const [x,y,r] of [[220,940,16],[440,970,13],[610,930,20],[790,965,13],[520,480,12],[650,510,9]]) cut(ctx,ovalPath(x,y,r,r*.6),C.soilPale,texture,2);
      for(const x of [70,115,920,990]) tuft(ctx,texture,x,612,74,Math.round(x),[C.grass,C.grassMid],.07*Math.sin(t*3+x));
      clouds(ctx,t,.1,1);
    });
  }

  function drawWorld(ctx,t) {
    const i=Math.max(0,Math.min(14,SHOTS.findIndex((s,j)=>j<15&&t>=s&&t<SHOTS[j+1])));
    const k=prog(t,SHOTS[i],SHOTS[i+1]);
    base(ctx);
    if(i===0) {
      withCamera(ctx,{x:540-35*k,y:990-15*k,zoom:1.06-.08*k},()=>{room(ctx);brood(ctx,t);dust(ctx,t);});
    } else if(i===1) {
      withCamera(ctx,{x:530+35*k,y:990,zoom:.93+.09*k},()=>{
        room(ctx);brood(ctx,t,false);
        nurse(ctx,t,480+95*k,1045,.75,95*k,null,0,.25*eOut(prog(t,28.74,28.98)));dust(ctx,t);
      });
    } else if(i===2) {
      cutaway(ctx,t,{x:530+10*k,y:930+75*k,zoom:1.04+.09*k,dy:-120},{cold:prog(t,29.62,30.08)*.8,rain:.5,rainFall:0,ids:['M1','M2','M3','U1','C1']});
    } else if(i===3) {
      withCamera(ctx,{x:515+55*k,y:1040-12*k,zoom:1.04+.08*k},()=>{
        room(ctx);nurse(ctx,t,450+125*k,1045,1.02,125*k,'larva');dust(ctx,t);
      });
    } else if(i===4||i===5) {
      weather(ctx,t,i===5,k);
    } else if(i===6) {
      galleries(ctx,t,k);
    } else if(i===7) {
      ramp(ctx,t,k);
    } else if(i===8) {
      cutaway(ctx,t,{x:515+45*k,y:717+25*k,zoom:2.2-.38*k,dy:-200},{cold:.8});
    } else if(i===9) {
      cutaway(ctx,t,{x:520-20*k,y:650-45*k,zoom:1.32+.11*k,dy:-130},{cold:.7,rain:1,rainFall:0,cloudsPart:.35+.65*eOut(prog(t,36.24,37.02))});
    } else if(i===10) {
      cutaway(ctx,t,{x:530+18*k,y:635+24*k,zoom:1.34+.09*k,dy:-140},{cold:.2});
      withCamera(ctx,{x:530+18*k,y:635+24*k,zoom:1.34+.09*k,dy:-140},()=>{
        ctx.save();ctx.globalAlpha=.25;cut(ctx,polyPath([[655,340],[725,340],[670,590],[390,590]]),'#FFE8A3',texture,0);ctx.restore();
        sun(ctx,t,695,320,90);
      });
    } else if(i===11) {
      withCamera(ctx,{x:530+65*k,y:1010-20*k,zoom:1.12+.06*k},()=>{
        room(ctx);nurse(ctx,t,445+75*k,1045,1.06,75*k,'larva');dust(ctx,t);
      });
    } else if(i===12) {
      separation(ctx,t,k);
    } else if(i===13) {
      withCamera(ctx,{x:520+85*k,y:945+75*k,zoom:1.26+.08*k},()=>{earth(ctx);wetSoil(ctx,t,250,1450);});
    } else {
      separation(ctx,t,k,true);
    }
  }

  return {
    duration:config.duration_seconds??(END-START), blurWindows:[], drawWorld,
    drawOverlay:captions,
    draw(ctx,t) { drawWorld(ctx,t);captions(ctx,t); },
  };
}
