/* global React */
const { useState } = React;

const C = {
  canvas:'#0c1e35', frame:'#274a79', ink:'#fff', ink2:'#e6ecf5', ink3:'#9aa8bd',
  rule:'#cfd6e6',
  lox:'#9fd3ff', lox2:'#9cd0ff', lh2:'#ffd39f', intertank:'#89ffa8',
  intertank2:'#b6ffb6', halo:'#caa9ff', engineFill:'#1f6aa8', engineStroke:'#9cd0ff',
  mono:"'JetBrains Mono', ui-monospace, Menlo, monospace",
  sans:"'Inter','Noto Sans KR',system-ui,sans-serif",
};

function Frame({ title, subtitle, width=700, height=520, children }) {
  return (
    <div style={{background:C.canvas,color:C.ink,width,fontFamily:C.sans,padding:0}}>
      <div style={{border:`2px solid ${C.frame}`,padding:16,minHeight:height-4,position:'relative'}}>
        {title && (
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline',marginBottom:10}}>
            <div style={{fontSize:14,color:C.ink}}>{title}</div>
            {subtitle && <div style={{fontFamily:C.mono,fontSize:11,color:C.lox}}>{subtitle}</div>}
          </div>
        )}
        {children}
      </div>
    </div>
  );
}

function LaneChip({ color=C.lox, children }) {
  return (
    <span style={{fontFamily:C.mono,fontSize:11,letterSpacing:'0.12em',textTransform:'uppercase',color}}>
      {children}
    </span>
  );
}

// Tank rendered as an SVG <g>. Callers place via wrapping <svg> + transform.
function Tank({ x=0, y=0, w=120, h=200, color=C.lox, label='LOX', radius=26, stroke=1.3 }) {
  const r = radius;
  const d = `M ${x} ${y+r} A ${r} ${r} 0 0 1 ${x+r} ${y} L ${x+w-r} ${y} A ${r} ${r} 0 0 1 ${x+w} ${y+r} L ${x+w} ${y+h-r} A ${r} ${r} 0 0 1 ${x+w-r} ${y+h} L ${x+r} ${y+h} A ${r} ${r} 0 0 1 ${x} ${y+h-r} Z`;
  return (
    <g>
      <path d={d} fill="none" stroke={color} strokeWidth={stroke}/>
      <text x={x+6} y={y+16} fill={color} fontSize={11} fontFamily={C.mono}>{label}</text>
    </g>
  );
}

function Interstage({ x=0, y=0, w=120, color=C.intertank, dashes='8 4', label='INTERTANK' }) {
  return (
    <g>
      <rect x={x} y={y} width={w} height={10} fill="none" stroke={color} strokeWidth={1.2} strokeDasharray={dashes}/>
      {label && <text x={x+w+12} y={y+10} fill={color} fontSize={11} fontFamily={C.mono}>{label}</text>}
    </g>
  );
}

function EngineRow({ cx=60, y=120, count=5, size=18, gap=22, fill=C.engineFill, stroke=C.engineStroke, label }) {
  const total = (count-1)*gap;
  const start = cx - total/2;
  const tris = [];
  for (let i=0;i<count;i++){
    const x = start + i*gap;
    tris.push(<path key={i} d={`M ${x} ${y} L ${x-size/2} ${y+size*1.2} L ${x+size/2} ${y+size*1.2} Z`} fill={fill} stroke={stroke} strokeWidth={1} opacity={0.9}/>);
  }
  return (
    <g>
      {tris}
      {label && <text x={cx} y={y+size*1.2+14} fill={stroke} fontSize={11} fontFamily={C.mono} textAnchor="middle">{label}</text>}
    </g>
  );
}

function DimLadder({ x=24, y1=40, y2=260, label='42.1 m' }) {
  return (
    <g>
      <line x1={x} y1={y1} x2={x} y2={y2} stroke={C.ink} strokeWidth={1}/>
      <line x1={x-6} y1={y1} x2={x+6} y2={y1} stroke={C.ink} strokeWidth={1}/>
      <line x1={x-6} y1={y2} x2={x+6} y2={y2} stroke={C.ink} strokeWidth={1}/>
      <text x={x-10} y={(y1+y2)/2} fill={C.ink} fontSize={11} fontFamily={C.mono} textAnchor="end" dominantBaseline="middle">{label}</text>
    </g>
  );
}

function Legend({ x=0, y=0, width=240, items=[] }) {
  const h = 24 + items.length*18;
  return (
    <g transform={`translate(${x},${y})`}>
      <rect x={0} y={0} width={width} height={h} fill="none" stroke={C.ink} strokeWidth={1}/>
      {items.map((it,i)=>(
        <g key={i} transform={`translate(12, ${10 + i*18})`}>
          <rect x={0} y={0} width={16} height={10} fill="none" stroke={it.color} strokeWidth={2}/>
          <text x={24} y={9} fill={it.color} fontSize={11} fontFamily={C.mono}>{it.label}</text>
        </g>
      ))}
    </g>
  );
}

function Stage({ x=0, y=0, w=120, h=220, label='S‑IC', diameter='Ø33 ft' }) {
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} fill="none" stroke={C.ink} strokeWidth={1.6}/>
      <text x={x + w/2} y={y+h+22} fill={C.lox} fontSize={12} fontFamily={C.mono} textAnchor="middle">{label}</text>
      <text x={x + w/2} y={y+h+36} fill={C.lox} fontSize={11} fontFamily={C.mono} textAnchor="middle">{diameter}</text>
    </g>
  );
}

function PartTreeBlock({ tree }) {
  const json = JSON.stringify(tree, null, 2);
  return (
    <pre style={{background:'#0a1a2e',border:`1px solid ${C.frame}`,padding:14,color:C.ink2,
      fontFamily:C.mono,fontSize:12,margin:0,overflow:'auto'}}>
      <span style={{color:C.ink3}}>{'```part_tree'}</span>{'\n'+json+'\n'}<span style={{color:C.ink3}}>{'```'}</span>
    </pre>
  );
}

function Button({ children, variant='default', ...rest }) {
  const border = variant==='primary'?C.lox:variant==='go'?C.intertank:variant==='warn'?C.lh2:C.ink;
  const color = border;
  return (
    <button {...rest} style={{fontFamily:C.mono,fontSize:12,textTransform:'uppercase',letterSpacing:'0.08em',
      padding:'8px 14px',background:'transparent',color,border:`1px solid ${border}`,borderRadius:2,cursor:'pointer'}}>
      {children}
    </button>
  );
}

Object.assign(window, { Frame, Tank, Interstage, EngineRow, DimLadder, Legend, Stage, PartTreeBlock, LaneChip, Button, BP_COLORS:C });
