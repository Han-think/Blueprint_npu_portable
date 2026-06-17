/* TopNav — Blueprint XPU 공유 헤더
   사용법:
     <div id="topnav"></div>
     <script type="text/babel" src="TopNav.jsx"></script>
     window.BPMountTopNav('Design'|'Model'|'Learning'|'Dashboard'|'Home'|...)
*/

// ── 생산 항목 (상단 크게) ─────────────────────────────────────
const BP_PRIMARY = [
  { k:'Design',    href:'Minimal.html',   label:'설계·생성',  icon:'◈' },
  // Model 탭 제거: 서버·모델 선택은 설계·생성 페이지 좌측 패널의 드롭다운으로 이동
  { k:'Learning',  href:'Learning.html',  label:'학습',       icon:'◎' },
  { k:'Dashboard', href:'Dashboard.html', label:'대시보드',   icon:'▤'  },
];

// 참고문서 탭 숨김 (BP_DOCS 데이터는 보존 — 복원 시 이 플래그만 켜면 됨)
const BP_SHOW_DOCS = false;

// ── 참고 문서 (하단 스크롤, 그룹) ────────────────────────────
const BP_DOCS = [
  // STRUCTURE
  { k:'Assembly',   href:'Assembly.html',   label:'Assembly',  group:'STRUCTURE' },
  { k:'Joints',     href:'Joints.html',     label:'Joints',    group:'STRUCTURE' },
  { k:'Mass',       href:'Mass.html',       label:'Mass',      group:'STRUCTURE' },
  // MATERIAL
  { k:'Materials',  href:'Materials.html',  label:'Material',  group:'MATERIAL' },
  { k:'PrintQueue', href:'PrintQueue.html', label:'Queue',     group:'MATERIAL' },
  { k:'Inspection', href:'Inspection.html', label:'Inspect',   group:'MATERIAL' },
  { k:'Supply',     href:'Supply.html',     label:'Supply',    group:'MATERIAL' },
  // ANALYSIS
  { k:'Loads',      href:'Loads.html',      label:'Loads',     group:'ANALYSIS' },
  { k:'Thermal',    href:'Thermal.html',    label:'Thermal',   group:'ANALYSIS' },
  { k:'CFD',        href:'CFD.html',        label:'CFD',       group:'ANALYSIS' },
  { k:'Test',       href:'Test.html',       label:'Test',      group:'ANALYSIS' },
  { k:'FMEA',       href:'FMEA.html',       label:'FMEA',      group:'ANALYSIS' },
  // OPS
  { k:'Lineage',    href:'Lineage.html',    label:'Lineage',   group:'OPS' },
  { k:'Ops',        href:'Ops.html',        label:'Ops',       group:'OPS' },
  { k:'ECN',        href:'ECN.html',        label:'ECN',       group:'OPS' },
  { k:'ICD',        href:'ICD.html',        label:'ICD',       group:'OPS' },
  // PROGRAM
  { k:'Schedule',   href:'Schedule.html',   label:'Schedule',  group:'PROGRAM' },
  { k:'Risk',       href:'Risk.html',       label:'Risk',      group:'PROGRAM' },
  { k:'FMEA2',      href:'FMEA.html',       label:'FMEA',      group:'PROGRAM' },
  // ETC
  { k:'Method',     href:'Method.html',     label:'Method',    group:'ETC' },
  { k:'Compare',    href:'Compare.html',    label:'Compare',   group:'ETC' },
  { k:'Output',     href:'Output.html',     label:'Output',    group:'ETC' },
];

const BP_C = {
  canvas:'#0c1e35', canvas2:'#0a1a2e', frame:'#274a79',
  ink:'#fff', ink2:'#e6ecf5', ink3:'#9aa8bd',
  lox:'#9fd3ff', inter:'#89ffa8', risk:'#ff9fb5', lh2:'#ffd39f', halo:'#caa9ff',
  mono:"'JetBrains Mono',ui-monospace,Menlo,monospace",
  sans:"'Inter','Noto Sans KR',system-ui,sans-serif",
};

// ── Ollama 헬스 pill ─────────────────────────────────────────
function BPHealth() {
  const [state, setState] = React.useState('checking');
  const [info,  setInfo]  = React.useState('');

  React.useEffect(() => {
    let dead = false;
    const ping = async () => {
      // LM Studio(주력) 먼저, 안 되면 Ollama(폴백) 확인
      try {
        const r = await fetch('http://127.0.0.1:1234/v1/models', { signal: AbortSignal.timeout(2000) });
        const data = await r.json();
        if (dead) return;
        const ms = data.data || [];
        setState('online');
        setInfo(`LM Studio · ${ms.length ? (ms[0].id.length > 28 ? ms[0].id.slice(0, 28) + '…' : ms[0].id) : 'no models'}`);
        return;
      } catch {}
      try {
        const r = await fetch('http://127.0.0.1:11434/api/tags', { signal: AbortSignal.timeout(2000) });
        const data = await r.json();
        if (dead) return;
        const ms = data.models || [];
        setState('online');
        setInfo(`Ollama · ${ms.length ? ms[0].name : 'no models'}`);
        return;
      } catch {}
      if (!dead) { setState('offline'); setInfo(''); }
    };
    ping();
    const id = setInterval(ping, 6000);
    return () => { dead = true; clearInterval(id); };
  }, []);

  const map = {
    checking: { c: BP_C.ink3, dot: BP_C.ink3,  t: 'connecting…' },
    online:   { c: BP_C.inter, dot: BP_C.inter, t: info },
    offline:  { c: BP_C.risk,  dot: BP_C.risk,  t: 'no local server' },
  }[state];

  return (
    <a href="Minimal.html"
      style={{ display:'inline-flex', alignItems:'center', gap:6, textDecoration:'none',
               padding:'4px 10px', border:`1px solid ${map.c}`,
               fontFamily:BP_C.mono, fontSize:10, color:map.c, letterSpacing:'.05em',
               whiteSpace:'nowrap', flexShrink:0 }}>
      <span style={{ width:6, height:6, borderRadius:'50%', background:map.dot,
                     boxShadow:`0 0 7px ${map.dot}`,
                     animation: state==='checking' ? 'bp-pulse 1s infinite' : 'none' }}/>
      {map.t}
    </a>
  );
}

// ── 메인 TopNav ──────────────────────────────────────────────
function BPTopNav({ active }) {
  const [docsOpen, setDocsOpen] = React.useState(false);

  // docs에서 현재 페이지인지
  const activeInDocs = BP_DOCS.some(p => p.k === active);

  return (
    <div style={{ position:'sticky', top:0, zIndex:50,
                  background:'rgba(10,26,46,0.97)', backdropFilter:'blur(10px)',
                  borderBottom:`1px solid ${BP_C.frame}` }}>
      <style>{`
        @keyframes bp-pulse{0%,100%{opacity:.3}50%{opacity:1}}
        .bp-docs-scroll::-webkit-scrollbar{height:3px;}
        .bp-docs-scroll::-webkit-scrollbar-thumb{background:${BP_C.frame};}
        .bp-pri-btn:hover{background:rgba(159,211,255,0.08)!important;}
      `}</style>

      {/* ── 상단: 로고 + 생산 항목 + 헬스 ── */}
      <div style={{ maxWidth:1280, margin:'0 auto', padding:'0 20px',
                    display:'flex', alignItems:'stretch', gap:0, height:48 }}>

        {/* 로고 */}
        <a href="index.html"
          style={{ display:'flex', alignItems:'center', gap:8, textDecoration:'none',
                   paddingRight:20, borderRight:`1px solid ${BP_C.frame}`, flexShrink:0 }}>
          <span style={{ width:16, height:16, border:`1.5px solid ${BP_C.lox}`, position:'relative', flexShrink:0 }}>
            <span style={{ position:'absolute', inset:3, border:`1px solid ${BP_C.lox}` }}/>
          </span>
          <span style={{ fontFamily:BP_C.mono, fontSize:11, color:BP_C.ink,
                         letterSpacing:'.12em', whiteSpace:'nowrap' }}>BLUEPRINT</span>
        </a>

        {/* 생산 항목 */}
        <div style={{ display:'flex', alignItems:'stretch', flex:1 }}>
          {BP_PRIMARY.map(p => {
            const on = p.k === active;
            return (
              <a key={p.k} href={p.href} className="bp-pri-btn"
                style={{ display:'flex', alignItems:'center', gap:6, padding:'0 18px',
                         textDecoration:'none', borderRight:`1px solid ${BP_C.frame}`,
                         background: on ? 'rgba(159,211,255,0.1)' : 'transparent',
                         borderBottom: on ? `2px solid ${BP_C.lox}` : '2px solid transparent',
                         transition:'background .1s' }}>
                <span style={{ fontFamily:BP_C.mono, fontSize:13, color: on ? BP_C.lox : BP_C.ink3 }}>
                  {p.icon}
                </span>
                <span style={{ fontFamily:BP_C.sans, fontSize:13, fontWeight: on ? 600 : 400,
                               color: on ? BP_C.lox : BP_C.ink2, whiteSpace:'nowrap' }}>
                  {p.label}
                </span>
              </a>
            );
          })}

          {/* 참고문서 토글 */}
          {BP_SHOW_DOCS && <button onClick={() => setDocsOpen(v => !v)}
            style={{ display:'flex', alignItems:'center', gap:5, padding:'0 14px',
                     background: (docsOpen || activeInDocs) ? 'rgba(154,168,189,0.1)' : 'transparent',
                     border:'none', borderRight:`1px solid ${BP_C.frame}`,
                     borderBottom: activeInDocs ? `2px solid ${BP_C.ink3}` : '2px solid transparent',
                     cursor:'pointer', color: BP_C.ink3, fontFamily:BP_C.sans,
                     fontSize:13, whiteSpace:'nowrap' }}>
            <span style={{ fontFamily:BP_C.mono, fontSize:10 }}>≡</span>
            참고문서
            <span style={{ fontFamily:BP_C.mono, fontSize:9, marginLeft:2 }}>
              {docsOpen ? '▲' : '▼'}
            </span>
          </button>}
        </div>

        {/* 헬스 pill */}
        <div style={{ display:'flex', alignItems:'center', paddingLeft:14, flexShrink:0 }}>
          <BPHealth/>
        </div>
      </div>

      {/* ── 하단: 참고문서 드롭다운 ── */}
      {BP_SHOW_DOCS && docsOpen && (
        <div style={{ borderTop:`1px solid ${BP_C.frame}`, background:'rgba(10,26,46,0.98)',
                      padding:'8px 20px' }}>
          <div className="bp-docs-scroll"
            style={{ display:'flex', gap:0, overflowX:'auto', alignItems:'center',
                     scrollbarWidth:'thin' }}>
            {BP_DOCS.filter((p,i,arr) => {
              // FMEA2 중복 제거
              if(p.k === 'FMEA2') return false;
              return true;
            }).map((p, i, arr) => {
              const on = p.k === active;
              const prev = arr[i - 1];
              const showSep = prev && prev.group !== p.group;
              return (
                <React.Fragment key={p.k}>
                  {showSep && (
                    <span style={{ width:1, height:16, background:BP_C.frame,
                                   margin:'0 6px', flexShrink:0 }}/>
                  )}
                  {showSep && (
                    <span style={{ fontFamily:BP_C.mono, fontSize:8, color:BP_C.ink3,
                                   letterSpacing:'.1em', marginRight:4, flexShrink:0 }}>
                      {p.group}
                    </span>
                  )}
                  <a href={p.href}
                    style={{ fontFamily:BP_C.mono, fontSize:10.5, letterSpacing:'.03em',
                             padding:'4px 8px', textDecoration:'none', whiteSpace:'nowrap',
                             color: on ? BP_C.canvas : BP_C.ink3,
                             background: on ? BP_C.ink3 : 'transparent',
                             borderRadius:2, flexShrink:0 }}>
                    {p.label}
                  </a>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

window.BPMountTopNav = function(active) {
  const root = document.getElementById('topnav');
  if (!root) return;
  ReactDOM.createRoot(root).render(<BPTopNav active={active}/>);
};
