/* TopNav — shared header for all Blueprint NPU pages.
   Renders a server health pill + page tabs. Drop this once per page:
     <div id="topnav"></div>
     <script type="text/babel" src="TopNav.jsx"></script>
   Then call: window.BPMountTopNav('Setup'|'Minimal'|'SelfLoop'|'End_to_End'|'Output'|'Errors'|'Home')
*/

const BP_PAGES = [
  { k:'README',     href:'README.html',      label:'README',  group:'_' },
  { k:'Dashboard',  href:'Dashboard.html',   label:'Dashboard', group:'_' },
  { k:'Method',     href:'Method.html',      label:'Method',  group:'_' },
  { k:'Learning',   href:'Learning.html',    label:'Learning',group:'_' },
  // STRUCTURE
  { k:'Assembly',   href:'Assembly.html',    label:'Assembly',group:'STRUCTURE' },
  { k:'Joints',     href:'Joints.html',      label:'Joints',  group:'STRUCTURE' },
  { k:'Mass',       href:'Mass.html',        label:'Mass',    group:'STRUCTURE' },
  // MATERIAL
  { k:'Materials',  href:'Materials.html',   label:'Material',group:'MATERIAL' },
  { k:'PrintQueue', href:'PrintQueue.html',  label:'Queue',   group:'MATERIAL' },
  { k:'Inspection', href:'Inspection.html',  label:'Inspect', group:'MATERIAL' },
  { k:'Supply',     href:'Supply.html',      label:'Supply',  group:'MATERIAL' },
  // ANALYSIS
  { k:'Loads',      href:'Loads.html',       label:'Loads',   group:'ANALYSIS' },
  { k:'Thermal',    href:'Thermal.html',     label:'Thermal', group:'ANALYSIS' },
  { k:'Test',       href:'Test.html',        label:'Test',    group:'ANALYSIS' },
  { k:'FMEA',       href:'FMEA.html',        label:'FMEA',    group:'ANALYSIS' },
  // OPS
  { k:'Lineage',    href:'Lineage.html',     label:'Lineage', group:'OPS' },
  { k:'Ops',        href:'Ops.html',         label:'Ops',     group:'OPS' },
  { k:'ECN',        href:'ECN.html',         label:'ECN',     group:'OPS' },
  { k:'ICD',        href:'ICD.html',         label:'ICD',     group:'OPS' },
  // PROGRAM
  { k:'Schedule',   href:'Schedule.html',    label:'Schedule',group:'PROGRAM' },
  { k:'Risk',       href:'Risk.html',        label:'Risk',    group:'PROGRAM' },
];

const BP_C = {
  canvas:'#0c1e35', frame:'#274a79', ink:'#fff', ink2:'#e6ecf5', ink3:'#9aa8bd',
  lox:'#9fd3ff', inter:'#89ffa8', risk:'#ff9fb5', lh2:'#ffd39f',
  mono:"'JetBrains Mono',ui-monospace,Menlo,monospace",
  sans:"'Inter','Noto Sans KR',system-ui,sans-serif",
};

function BPHealth(){
  const [state,setState] = React.useState('checking'); // checking | online | offline
  const [info,setInfo] = React.useState('');

  React.useEffect(()=>{
    let dead=false;
    const ping = ()=>{
      const ctrl = new AbortController();
      const t = setTimeout(()=>ctrl.abort(), 2000);
      fetch('http://127.0.0.1:11434/api/tags', { signal:ctrl.signal })
        .then(r=>r.json())
        .then(data=>{
          if(dead) return;
          const models = (data.models||[]);
          const count = models.length;
          const first = count>0 ? models[0].name : 'no models';
          setState('online');
          setInfo(count===1 ? first : count>1 ? `${first} +${count-1}` : 'no models pulled');
        })
        .catch(()=>{ if(!dead){ setState('offline'); setInfo(''); } })
        .finally(()=>clearTimeout(t));
    };
    ping();
    const id = setInterval(ping, 6000);
    return ()=>{ dead=true; clearInterval(id); };
  },[]);

  const map = {
    checking: { c:BP_C.ink3,  dot:BP_C.ink3,  t:'connecting…' },
    online:   { c:BP_C.inter, dot:BP_C.inter, t:`ollama online · ${info}` },
    offline:  { c:BP_C.risk,  dot:BP_C.risk,  t:'ollama offline · start C:\\Ollama-IPEX\\start-ollama.bat' },
  }[state];

  return (
    <a href="Errors.html" style={{display:'inline-flex',alignItems:'center',gap:8,textDecoration:'none',padding:'5px 10px',border:`1px solid ${map.c}`,fontFamily:BP_C.mono,fontSize:10.5,color:map.c,letterSpacing:'.06em'}}>
      <span style={{width:6,height:6,borderRadius:'50%',background:map.dot,boxShadow:`0 0 8px ${map.dot}`,animation:state==='checking'?'bp-pulse 1s infinite':'none'}}/>
      <span>127.0.0.1:11434 · {map.t}</span>
    </a>
  );
}

function BPTopNav({ active }){
  return (
    <div style={{position:'sticky',top:0,zIndex:50,background:'rgba(12,30,53,0.92)',backdropFilter:'blur(8px)',borderBottom:`1px solid ${BP_C.frame}`}}>
      <style>{`@keyframes bp-pulse{0%,100%{opacity:.4}50%{opacity:1}}`}</style>
      <div style={{maxWidth:1200,margin:'0 auto',padding:'10px 24px',display:'flex',alignItems:'center',gap:18}}>
        <a href="index.html" style={{display:'flex',alignItems:'center',gap:8,textDecoration:'none'}}>
          <span style={{width:18,height:18,border:`1.5px solid ${BP_C.lox}`,position:'relative'}}>
            <span style={{position:'absolute',inset:3,border:`1px solid ${BP_C.lox}`}}/>
          </span>
          <span style={{fontFamily:BP_C.mono,fontSize:11,color:BP_C.ink,letterSpacing:'.14em'}}>BLUEPRINT · NPU</span>
        </a>
        <nav className="bp-topnav-scroll" style={{display:'flex',gap:2,marginLeft:8,flex:1,overflowX:'auto',scrollbarWidth:'none'}}>
          <style>{`.bp-topnav-scroll::-webkit-scrollbar{display:none}`}</style>
          {BP_PAGES.map((p,i)=>{
            const on = p.k===active;
            const prev = BP_PAGES[i-1];
            const showSep = prev && prev.group && p.group && prev.group !== p.group;
            return (
              <React.Fragment key={p.k}>
                {showSep && <span style={{width:1,background:BP_C.frame,margin:'2px 6px',flexShrink:0}}/>}
                <a href={p.href} style={{
                  fontFamily:BP_C.mono,fontSize:10.5,letterSpacing:'.04em',
                  padding:'5px 9px',textDecoration:'none',whiteSpace:'nowrap',
                  color: on?BP_C.canvas:BP_C.ink2,
                  background: on?BP_C.lox:'transparent',
                  border:`1px solid ${on?BP_C.lox:'transparent'}`,
                }}>{p.label}</a>
              </React.Fragment>
            );
          })}
        </nav>
        <BPHealth/>
      </div>
    </div>
  );
}

window.BPMountTopNav = function(active){
  const root = document.getElementById('topnav');
  if(!root) return;
  ReactDOM.createRoot(root).render(<BPTopNav active={active}/>);
};
