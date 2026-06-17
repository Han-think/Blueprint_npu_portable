/* global React */
const { useState } = React;

const GW = {
  canvas:'#0c1e35', canvas2:'#0a1a2e', frame:'#274a79',
  ink:'#fff', ink2:'#e6ecf5', ink3:'#9aa8bd',
  lox:'#9fd3ff', lh2:'#ffd39f', intertank:'#89ffa8', halo:'#caa9ff',
  mono:"'JetBrains Mono', ui-monospace, Menlo, monospace",
  sans:"'Inter','Noto Sans KR',system-ui,sans-serif",
};

function Chip({ children, color=GW.lox }) {
  return <span style={{fontFamily:GW.mono,fontSize:11,letterSpacing:'0.12em',textTransform:'uppercase',color}}>{children}</span>;
}

function Field({ label, children }) {
  return (
    <label style={{display:'block'}}>
      <div style={{fontFamily:GW.mono,fontSize:11,color:GW.ink3,letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:4}}>{label}</div>
      {children}
    </label>
  );
}

function TextInput({ value, onChange, mono=true, ...rest }) {
  return <input value={value} onChange={e=>onChange&&onChange(e.target.value)} style={{
    width:'100%',fontFamily:mono?GW.mono:GW.sans,fontSize:12,background:GW.canvas2,color:GW.ink,
    border:`1px solid ${GW.frame}`,padding:'8px 10px',borderRadius:2,outline:'none'}} {...rest}/>;
}
function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={e=>onChange&&onChange(e.target.value)} style={{
      width:'100%',fontFamily:GW.mono,fontSize:12,background:GW.canvas2,color:GW.ink,
      border:`1px solid ${GW.frame}`,padding:'8px 10px',borderRadius:2,outline:'none'}}>
      {options.map(o=><option key={o} value={o}>{o}</option>)}
    </select>
  );
}
function Slider({ min=16, max=512, step=16, value, onChange, label }) {
  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',fontFamily:GW.mono,fontSize:11,color:GW.ink3,marginBottom:4}}>
        <span style={{letterSpacing:'0.08em',textTransform:'uppercase'}}>{label}</span>
        <span style={{color:GW.lox}}>{value}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={e=>onChange&&onChange(+e.target.value)} style={{width:'100%',accentColor:GW.lox}}/>
    </div>
  );
}
function Check({ checked, onChange, children }) {
  return (
    <label style={{display:'flex',alignItems:'center',gap:8,cursor:'pointer'}}>
      <input type="checkbox" checked={checked} onChange={e=>onChange&&onChange(e.target.checked)} style={{accentColor:GW.lox}}/>
      <span style={{fontFamily:GW.mono,fontSize:11,letterSpacing:'0.08em',textTransform:'uppercase',color:GW.ink2}}>{children}</span>
    </label>
  );
}

function Btn({ children, variant='default', onClick, style }) {
  const border = variant==='primary'?GW.lox:variant==='go'?GW.intertank:variant==='warn'?GW.lh2:GW.ink;
  return (
    <button onClick={onClick} style={{fontFamily:GW.mono,fontSize:12,textTransform:'uppercase',letterSpacing:'0.08em',
      padding:'10px 16px',background:'transparent',color:border,border:`1px solid ${border}`,borderRadius:2,cursor:'pointer',...style}}>
      {children}
    </button>
  );
}

function Accordion({ title, open:initOpen=false, children }) {
  const [open,setOpen]=useState(initOpen);
  return (
    <div style={{border:`1px solid ${GW.frame}`,borderRadius:2,marginBottom:10}}>
      <button onClick={()=>setOpen(!open)} style={{width:'100%',textAlign:'left',background:'transparent',
        border:0,padding:'10px 14px',color:GW.ink,fontFamily:GW.mono,fontSize:12,letterSpacing:'0.08em',
        textTransform:'uppercase',cursor:'pointer',display:'flex',justifyContent:'space-between'}}>
        <span>{title}</span>
        <span style={{color:GW.lox}}>{open?'−':'+'}</span>
      </button>
      {open && <div style={{padding:'0 14px 14px'}}>{children}</div>}
    </div>
  );
}

function Tabs({ tabs, active, onChange }) {
  return (
    <div style={{display:'flex',borderBottom:`1px solid ${GW.frame}`,marginBottom:14}}>
      {tabs.map(t=>(
        <button key={t} onClick={()=>onChange(t)} style={{
          background:'transparent',border:0,borderBottom:`2px solid ${active===t?GW.lox:'transparent'}`,
          padding:'10px 16px',color:active===t?GW.ink:GW.ink3,fontFamily:GW.mono,fontSize:12,
          textTransform:'uppercase',letterSpacing:'0.08em',cursor:'pointer'}}>
          {t}
        </button>
      ))}
    </div>
  );
}

Object.assign(window, { GW, Chip, Field, TextInput, Select, Slider, Check, Btn, Accordion, Tabs });
