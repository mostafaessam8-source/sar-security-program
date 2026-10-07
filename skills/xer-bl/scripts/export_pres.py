"""Export the Rev 1 model to JSON for the interactive offline presentation."""
from xer import *
import json, collections
k, lag = solve(); txt, meta = build_xer(lag)
ES, EF, LS, LF = meta['ES'], meta['EF'], meta['LS'], meta['LF']
iso = lambda i: WORK[i].isoformat()
mi = lambda i: (WORK[i].year - START.year) * 12 + WORK[i].month - START.month      # 0-based month index from NTP month
NM = 36
def clean(a):
    suf = ' - ' + a.name.split(' - ')[-1] if ' - ' in a.name else ''
    return a.name[:-len(suf)] if suf and a.station else a.name
acts = []
for code, a in ACTS.items():
    t = 'T' if a.typ == 'TT_Task' else ('F' if a.typ == 'TT_FinMile' else 'M')
    d0 = iso(ES[code]) if t != 'F' else iso(EF[code]); d1 = iso(EF[code]) if t != 'M' else iso(ES[code])
    acts.append(dict(id=code, n=clean(a), t=t, stn=a.codes.get('STN', 'PRJ'), ep=a.codes.get('EPC'), ph=a.codes.get('PHASE'), sg=a.codes.get('STAGE'), sa=a.codes.get('SUBAPP'),
                     rs=a.codes.get('RESP'), ms=a.codes.get('MST'), pr=[f"{p_} {t_}{('+'+str(l_)) if l_ else ''}" for p_, t_, l_ in meta['pred_of'][code]], s=d0, f=d1, d=a.dur, c=a.cost, p=a.pts * 620, fl=LS[code] - ES[code]))
D0 = json.load(open('/tmp/claude-0/-home-user/0d8cf00c-df50-59d0-89bb-befade0f854d/scratchpad/deck/data.json'))
stations = []
STNMAP = {s['code']: s for s in ST.values()}
ev_suf = {'MS2': 'E1200', 'MS3': 'E1210', 'MS4': 'P1100', 'MS5': 'C2100', 'MS6': 'T1100', 'MS7': 'T3100'}
def curve(codes, key):
    arr = [0.0] * NM
    for c in codes:
        a = ACTS[c]
        if a.typ != 'TT_Task' or a.dur == 0: continue
        v = a.cost if key == 'c' else a.pts * 620
        for i in range(ES[c], EF[c] + 1): arr[min(NM - 1, mi(i))] += v / a.dur
    return [round(x) for x in arr]
inv_events = []
for sid, s in ST.items():
    code = s['code']; mine = [c for c, a in ACTS.items() if a.codes.get('STN') == code]
    ph = {}
    for p_ in ('MOB', 'DES', 'POC', 'ENA', 'PRO', 'CON', 'COM'):
        cs = [c for c in mine if ACTS[c].codes.get('PHASE') == p_ and ACTS[c].typ == 'TT_Task']
        if cs: ph[p_] = [iso(min(ES[c] for c in cs)), iso(max(EF[c] for c in cs))]
    invs = []
    for ms, suf in ev_suf.items():
        c = f'{code}-{suf}'; amt = round(PO * MS[ms][1] * s['f'])
        invs.append(dict(ms=ms, n=MS[ms][0], d=iso(ES[c] if ACTS[c].typ == 'TT_Mile' else EF[c]), a=amt)); inv_events.append((code, s['line'], ms, invs[-1]['d'], amt))
    stations.append(dict(id=sid, code=code, name=s['name'], line=s['line'], prio=s['prio'], val=round(s['val']), share=s['f'], cams=s['cams'], ph=ph, inv=invs,
                         hw=s['hw'], sh={k:round(v) for k,v in s['shared'].items()}, camt=D0['camSt'][sid], start=iso(min(ES[c] for c in mine)), end=iso(max(EF[c] for c in mine)), cost=sum(ACTS[c].cost for c in mine), prog=sum(ACTS[c].pts for c in mine) * 620,
                         cc=curve(mine, 'c'), pc=curve(mine, 'p')))
prj = [c for c, a in ACTS.items() if a.codes.get('STN', 'PRJ') == 'PRJ']
prj_ph = {'MOB': [iso(ES['PRJ-A1010']), iso(EF['PRJ-M1150'])]}
inv_events.append(('PRJ', 'ALL', 'MS1', iso(EF['PRJ-M1100']), round(PO * MS['MS1'][1])))
# rounding residual: each payment milestone adds up to its exact contract amount
for ms_, v_ in MS.items():
    tgt = round(PO * v_[1]); idx = [i for i, e in enumerate(inv_events) if e[2] == ms_]
    diff = tgt - sum(inv_events[i][4] for i in idx)
    if diff and ms_ != 'MS1':
        bi = max(idx, key=lambda i: inv_events[i][4]); e = inv_events[bi]; inv_events[bi] = (e[0], e[1], e[2], e[3], e[4] + diff)
for st_ in stations:
    for iv in st_['inv']:
        for e in inv_events:
            if e[0] == st_['code'] and e[2] == iv['ms']: iv['a'] = e[4]
# monthly invoices
months = []
for m in range(NM):
    y, mm = divmod(START.month - 1 + m, 12); months.append(f'{START.year + y}-{mm + 1:02d}')
inv_m = {ms: [0] * NM for ms in MS}
for code, line, ms, d, amt in inv_events:
    dd = dt.date.fromisoformat(d); idx = (dd.year - START.year) * 12 + dd.month - START.month; inv_m[ms][min(NM - 1, idx)] += amt
stages_ap = collections.Counter(ACTS[c].dur for c in ACTS if ACTS[c].codes.get('SUBAPP') == 'Approval' and ACTS[c].typ == 'TT_Task')
D = json.load(open('/tmp/claude-0/-home-user/0d8cf00c-df50-59d0-89bb-befade0f854d/scratchpad/deck/data.json'))
out = dict(
    meta=dict(no=PROJECT_NO, name=PROJECT_NAME, rev=REVISION, ntp=START.isoformat(), end=TERM_END.isoformat(), po=PO, acts=len(ACTS), tasks=sum(1 for a in ACTS.values() if a.typ == 'TT_Task'),
              ms=sum(1 for a in ACTS.values() if a.typ != 'TT_Task'), finish=iso(max(EF.values())), review_wd=REVIEW_WD, cams=D['cams'], camT=D['camT'], camLine=D['camLine'], catPriced=D['catPriced'],
              m2=iso(M2_IDX), m6=iso(M6_IDX), ena=iso(ENA_IDX), approvals=dict(stages_ap)),
    months=months, acts=acts, stations=stations, inv_m=inv_m, ms_def={k_: dict(n=v[0], p=v[1]) for k_, v in MS.items()},
    prj=dict(cc=curve(prj, 'c'), pc=curve(prj, 'p')),
    key=dict(m1100=iso(EF['PRJ-M1100']), m1150=iso(EF['PRJ-M1150']), m2100=iso(EF['PRJ-M2100']), m1250=iso(EF['PRJ-M1250']), mx99=iso(EF['PRJ-MX99']), poc=iso(EF['NRY-POC4100'])),
    events=[dict(c=e[0], l=e[1], ms=e[2], d=e[3], a=e[4]) for e in inv_events],
    line_val={l: round(sum(s_['val'] for s_ in ST.values() if s_['line']==l)) for l in ('NSR','EWR','HHR')},
    holidays=[[a.isoformat(), b.isoformat(), l] for a, b, l in HOLIDAYS])
json.dump(out, open('pres_data.json', 'w'), separators=(',', ':'))
print('ok', len(json.dumps(out)) // 1024, 'KB', out['key'], sum(inv_m['MS1']), sum(sum(v) for v in inv_m.values()))
tot = [0] * NM
for v in inv_m.values():
    for i, x in enumerate(v): tot[i] += x
print([round(x / 1e6, 1) for x in tot])
print('station cost sum + MS1', sum(s['cost'] for s in stations) + sum(ACTS[c].cost for c in prj))
