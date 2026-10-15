from pathlib import Path
import json,csv,math,statistics as st,hashlib
P=Path(__file__).resolve().parent
T=2.045229642132703
raw=[json.loads(l) for l in (P/'results.jsonl').read_text().splitlines()]
manifest=json.loads((P/'manifest.json').read_text());byid={r['id']:r for r in raw}
assert len(byid)==len(raw)==len(manifest['design'])
keys=['k','risk','capacity','target','freight','alpha']
checks=[]

def stat(a):
    m=st.mean(a);h=T*st.stdev(a)/math.sqrt(len(a)) if len(a)>1 else 0
    return {'mean':m,'lo':m-h,'hi':m+h,'sd':st.stdev(a) if len(a)>1 else 0,'n':len(a)}

def enrich(d):
    return dict(d,service=100*d['met']/d['demand'],unit_cost=d['cost']/d['met'],avg_stock=d['stock_sum']/d['cycles'],avg_unused=d['unused_sum']/d['cycles'],available_util=100*d['received']/d['available_sum'],capacity_ratio=d['normal_capacity']/d['demand_per_cycle'],out_pct=100*d['out_supplier_cycles']/(5*d['cycles']),buyer_short_pct=100*d['buyer_shortage_cycles']/(10*d['cycles']))

rows=[];windows=[]
for p in manifest['design']:
    r=byid[p['id']];r.update(p)
    for s in r['snapshots']:
        assert abs(s['initial_stock']+s['received']-s['met']-s['terminal_stock'])<1e-5
        assert abs(s['cost']-sum(s[t] for t in ['purchase','transport','links_cost','holding']))<1e-5
        assert abs(s['links_cost']-50*10*r['k']*s['cycles'])<1e-5
        assert abs(s['holding']-s['stock_sum'])<1e-5
        assert abs(s['available_sum']-s['received']-s['unused_sum'])<1e-5
    if r['kind']=='core':
        s=next(s for s in r['snapshots'] if s['cycles']==500)
        rows.append(dict(p,**enrich(s)))
        if p['cycles']==1000:
            cumul={int(s['cycles']):s for s in r['snapshots']}
            for start,end in [(1,100),(101,500),(501,1000)]:
                right=cumul[end];left=cumul.get(start-1)
                flows=['demand','met','unmet','received','purchase','transport','links_cost','holding','cost','stock_sum','available_sum','unused_sum','congested_supplier_cycles','out_supplier_cycles','shortage_cycles','buyer_shortage_cycles']
                d=right.copy()
                for f in flows:d[f]=right[f]-(left[f] if left else 0)
                d['cycles']=end-start+1;d['initial_stock']=left['terminal_stock'] if left else right['initial_stock']
                windows.append(dict(p,**enrich(d),window=f'{start}-{end}'))
checks.append('All snapshots: inventory, cost, fixed fees, holding fees and available-capacity conservation.')
# Exogenous environment/shocks are identical across strategy, freight, target and feedback.
ref={}
for p in manifest['design']:
    if p['kind']!='core':continue
    r=byid[p['id']];key=(p['seed'],p['risk'],p['capacity'])
    env=r['environment'];signature=(env,r['out_path'][:500])
    if key in ref: assert ref[key]==signature,(p['id'],'exogenous pairing')
    else:ref[key]=signature
checks.append('Exact environment and 500-cycle supplier outage paths match all treatments at each seed/risk/capacity.')
# Alpha cannot change single-partner physical delivery. Compare independently rerun cases.
for risk in (0,2):
    for seed in range(2026,2056):
        cases=[r for r in rows if r['k']==1 and r['risk']==risk and r['seed']==seed and r['capacity']==100 and r['target']==1 and r['freight']==3]
        for f in ['met','received','terminal_stock','stock_sum']:
            vals=[r[f] for r in cases];assert max(vals)-min(vals)<1e-6
checks.append('Single-partner trajectories invariant under alpha=0,0.2,0.4 for both risks (60 paired scenarios).')
metrics=['service','unit_cost','cost','met','unmet','received','avg_stock','terminal_stock','initial_stock','avg_unused','available_util','capacity_ratio','out_pct','buyer_short_pct','used_suppliers','largest_customer_group','purchase','transport','links_cost','holding']
groups=[]
for key in sorted(set(tuple(r[f] for f in keys) for r in rows)):
    rs=[r for r in rows if tuple(r[f] for f in keys)==key]
    assert len(rs)==30
    groups.append(dict(zip(keys,key),families=rs[0]['families'],stats={m:stat([r[m] for r in rs]) for m in metrics}))

def select(**p):
    default=dict(k=1,risk=2,capacity=100,target=1,freight=3,alpha=.2);default.update(p)
    return sorted([r for r in rows if all(r[k]==v for k,v in default.items())],key=lambda r:r['seed'])

def paired(a,b):
    assert len(a)==len(b)==30 and [r['seed'] for r in a]==[r['seed'] for r in b]
    return {m:stat([y[m]-x[m] for x,y in zip(a,b)]) for m in ['service','unit_cost','cost','met','avg_stock','avg_unused']}
pairs={}
for k in (1,2,3):
    for risk in (0,2):
        for target in (1,2):pairs[f'inventory-risk{risk}-k{k}-{target}minus0']=paired(select(k=k,risk=risk,target=0),select(k=k,risk=risk,target=target))
        for alpha in (.2,.4):pairs[f'alpha-risk{risk}-k{k}-{alpha}minus0']=paired(select(k=k,risk=risk,alpha=0),select(k=k,risk=risk,alpha=alpha))
    pairs[f'inventory-risk2-k{k}-2minus1']=paired(select(k=k,target=1),select(k=k,target=2))
    pairs[f'risk-k{k}-2minus0']=paired(select(k=k,risk=0),select(k=k,risk=2))
    pairs[f'freight-k{k}-4minus2']=paired(select(k=k,freight=2),select(k=k,freight=4))
for a,b in [(1,2),(2,3),(1,3)]:pairs[f'baseline-k{b}minus{a}']=paired(select(k=a),select(k=b))
wg=[]
for k in (1,2,3):
    for window in ('1-100','101-500','501-1000'):
        rs=[r for r in windows if r['k']==k and r['window']==window]
        wg.append(dict(k=k,window=window,stats={m:stat([r[m] for r in rs]) for m in metrics}))
fees=[]
for F in (0,50,100):
    for H in (0,1,2):
        for target in (0,1,2):
            for k in (1,2,3):
                rs=select(k=k,target=target)
                unit=[(r['purchase']+r['transport']+F*r['links']*500+H*r['stock_sum'])/r['met'] for r in rs]
                fees.append(dict(F=F,H=H,target=target,k=k,unit_cost=stat(unit),service=stat([r['service'] for r in rs]),avg_stock=stat([r['avg_stock'] for r in rs])))
checks.append('Fee grid: 2,430 revaluations of 270 existing trajectories, never treated as new replicates.')
# Controlled outage trajectories; compare with the same strategy's no-outage path.
demos=[]
for k in (1,2,3):
    control=byid[f'D{k}_0']
    for duration in (0,2,10):
        r=byid[f'D{k}_{duration}'];trace=r['trace'];last=r['snapshots'][-1]
        extra=sum(a[2]-b[2] for a,b in zip(control['trace'][100:],trace[100:]))
        recover=None
        if duration:
            for idx in range(100+duration,196):
                if all(trace[j][2]>=control['trace'][j][2]-1e-6 for j in range(idx,idx+5)):
                    recover=idx+1;break
        demos.append(dict(k=k,duration=duration,trace=trace,extra_unmet_101_200=extra,recovery_cycle=recover,service=100*last['met']/last['demand']))
summary=dict(groups=groups,pairs=pairs,windows=wg,fees=fees,demos=demos,checks=checks,manifest={k:v for k,v in manifest.items() if k!='design'})
(P/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
fields=['id','seed','map']+keys+['cycles']+[k for k in rows[0] if k not in ['id','seed','map']+keys+['cycles','families','kind','outage_supplier','outage_duration']]
with (P/'results-500.csv').open('w') as f:
    w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
(P/'analysis_checks.txt').write_text('\n'.join(checks))
for g in groups:
    print(' '.join(f'{k}={g[k]}' for k in keys), 'service %.3f unit %.3f stock %.2f unused %.2f'%tuple(g['stats'][m]['mean'] for m in ['service','unit_cost','avg_stock','avg_unused']))
print('PAIRS',json.dumps({k:{m:{s:round(x,4) for s,x in v[m].items()} for m in ['service','unit_cost']} for k,v in pairs.items()},indent=2))
print('WINDOWS',[(g['k'],g['window'],round(g['stats']['service']['mean'],3),round(g['stats']['unit_cost']['mean'],3)) for g in wg])
print('DEMO',[(d['k'],d['duration'],d['extra_unmet_101_200'],d['recovery_cycle']) for d in demos])
print('ALL CHECKS PASSED',len(rows),'rows; ',len(groups),'conditions')
