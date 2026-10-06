from model import *

def solve(buffer_days=20):
    surveys, accepted = build()
    # pass 1: find detailed-baseline-approved day
    wave0 = {sid: 0 for sid in ST}
    order, pred_of, ES, EF = cpm(wave0)
    t_db = EF['PRJ-M2100']
    best = None
    for k100 in range(50, 200):
        k = k100 / 100.0
        lag = {}
        for sid, s in ST.items():
            if s['ryd']: lag[sid] = 0; continue
            D = rnd_(s['start_w'] * 5 * k)
            lag[sid] = max(0, D - (t_db + 1))
        order, pred_of, ES, EF = cpm(lag)
        fin = EF['PRJ-C1010']
        if fin <= TERM_IDX - buffer_days: best = (k, lag)
        else: break
    return best

def rnd_(x): return int(x + 0.5)

def finalize(lag):
    order, pred_of, ES, EF = cpm(lag)
    end_idx = TERM_IDX
    LS, LF, succ = backward(order, pred_of, ES, EF, end_idx)
    # costs (whole SAR) per (station, milestone) with residual to the largest key
    amounts = {}
    for sid, s in ST.items():
        c = s['code']
        for ms in ('MS2', 'MS3', 'MS4', 'MS5', 'MS6', 'MS7'):
            members = [(a.code, a.cost_ms[1]) for a in ACTS.values() if a.station == sid and a.cost_ms and a.cost_ms[0] == ms]
            M = MS[ms][1] * PO * s['f']
            raw = {code: M * w for code, w in members}
            ints = {code: int(v + 0.5) for code, v in raw.items()}
            amounts.update(ints)
            amounts[('M', sid, ms)] = M
    prj_members = [(a.code, a.cost_ms[1]) for a in ACTS.values() if a.cost_ms and a.cost_ms[0] == 'MS1']
    for code, w in prj_members: amounts[code] = int(MS['MS1'][1] * PO * w + 0.5)
    cost = {k: v for k, v in amounts.items() if isinstance(k, str)}
    diff = PO - sum(cost.values())
    # spread the rounding residual one riyal at a time on the largest activities
    big = sorted(cost, key=lambda k: -cost[k])
    i = 0
    while diff != 0:
        cost[big[i % 50]] += 1 if diff > 0 else -1
        diff += -1 if diff > 0 else 1; i += 1
    for code in ACTS: ACTS[code].cost = cost.get(code, 0)
    # progress points: whole project = 100,000 (0.001%)
    raw = {code: ACTS[code].prog * 1000.0 for code in ACTS}
    pts = {code: int(v + 0.5) for code, v in raw.items()}
    d = 100000 - sum(pts.values())
    bigp = sorted(pts, key=lambda k: -pts[k]); i = 0
    while d != 0:
        pts[bigp[i % 40]] += 1 if d > 0 else -1; d += -1 if d > 0 else 1; i += 1
    for code in ACTS: ACTS[code].pts = pts[code]
    return order, pred_of, ES, EF, LS, LF, succ

if __name__ == '__main__':
    k, lag = solve()
    print('stretch', k)
    order, pred_of, ES, EF, LS, LF, succ = finalize(lag)
    print('activities', len(ACTS), 'tasks', sum(1 for a in ACTS.values() if a.typ == 'TT_Task'), 'milestones', sum(1 for a in ACTS.values() if a.typ != 'TT_Task'))
    print('project finish idx', max(EF.values()), WORK[max(EF.values())], 'term end', WORK[TERM_IDX])
    print('NTP', WORK[ES['PRJ-M0000']], 'baseline approved', WORK[EF['PRJ-M2100']])
    for sid, s in ST.items():
        c = s['code']; print(sid, 'start', WORK[ES[f'{c}-E1010']], 'accepted', WORK[EF[f'{c}-T3100']], 'TF', LF[f'{c}-T3100'] - EF[f'{c}-T3100'])
    print('cost total', sum(a.cost for a in ACTS.values()), 'pts', sum(a.pts for a in ACTS.values()))
    print('min dur', min(a.dur for a in ACTS.values() if a.typ == 'TT_Task'))
    print('closeout', WORK[ES['PRJ-C1010']], WORK[EF['PRJ-C1010']], 'completion', WORK[EF['PRJ-MX99']])
    import collections
    print(collections.Counter(w['level'] for w in WBS.values()), len(WBS))
