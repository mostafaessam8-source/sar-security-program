import re, sys, datetime as dt, collections

def parse(path):
    raw = open(path, encoding='utf-8').read().split('\n')
    hdr = raw[0].split('\t'); T = {}; cur = None
    for ln in raw[1:]:
        if ln.startswith('%T'): cur = ln.split('\t')[1]; T[cur] = dict(f=None, r=[])
        elif ln.startswith('%F'): T[cur]['f'] = ln.split('\t')[1:]
        elif ln.startswith('%R'):
            v = ln.split('\t')[1:]; assert len(v) == len(T[cur]['f']), (cur, len(v), len(T[cur]['f']))
            T[cur]['r'].append(dict(zip(T[cur]['f'], v)))
        elif ln.startswith('%E'): T['_end'] = True
    return hdr, T

def calendar_from_xer(T):
    data = T['CALENDAR']['r'][0]['clndr_data']
    exc = set(dt.date(1899, 12, 30) + dt.timedelta(days=int(x)) for x in re.findall(r'd\|(\d+)', data))
    dow = {}
    for m in re.finditer(r'\(0\|\|(\d)\(\)(\(\(|\(\))', data):
        pass
    working = []
    for m in re.finditer(r'\(0\|\|([1-7])\(\)(\(\(0\|\|0\(s\||\(\))', data):
        pass
    # day n working if its entry contains time spans
    parts = re.findall(r'\(0\|\|([1-7])\(\)(\(\(0\|\|0\(s\|08:00\|f\|12:00\)\(\)\)\(0\|\|1\(s\|13:00\|f\|17:00\)\(\)\)\)|\(\))\)', data)
    wd = {int(n): ('s|' in body) for n, body in parts}
    return wd, exc

def run(path):
    hdr, T = parse(path)
    errs = []
    ok = lambda c, m: (errs.append(m) if not c else None)
    ok(hdr[0] == 'ERMHDR' and hdr[1].startswith('24'), 'header')
    ok(T.get('_end'), 'missing %E')
    for t, d in T.items():
        if t == '_end': continue
        pk = d['f'][0]
        if t in ('TASKPRED',): pk = d['f'][0]
        if t not in ('TASKACTV',):
            ids = [r[pk] for r in d['r']]
            ok(len(ids) == len(set(ids)), f'duplicate PK in {t}')
    wbs = {r['wbs_id']: r for r in T['PROJWBS']['r']}
    roots = [r for r in wbs.values() if not r['parent_wbs_id']]
    ok(len(roots) == 1, 'WBS root count')
    for r in wbs.values(): ok(not r['parent_wbs_id'] or r['parent_wbs_id'] in wbs, 'WBS parent missing')
    def level(w):
        n = 1
        while wbs[w]['parent_wbs_id']: w = wbs[w]['parent_wbs_id']; n += 1
        return n
    maxlvl = max(level(w) for w in wbs)
    tasks = {r['task_id']: r for r in T['TASK']['r']}
    codes = [r['task_code'] for r in T['TASK']['r']]
    ok(len(codes) == len(set(codes)), 'duplicate activity IDs'); ok(all(len(c) <= 20 for c in codes), 'task_code > 20 chars')
    for r in tasks.values(): ok(r['wbs_id'] in wbs, 'task wbs missing')
    # resources
    tr = collections.defaultdict(list)
    for r in T['TASKRSRC']['r']:
        ok(r['task_id'] in tasks, 'taskrsrc task'); tr[r['task_id']].append(r)
    cost = sum(float(r['target_cost']) for r in T['TASKRSRC']['r'] if r['rsrc_id'] == '3002')
    pts = sum(float(r['target_qty']) for r in T['TASKRSRC']['r'] if r['rsrc_id'] == '3001')
    for tid_, r in tasks.items():
        if r['task_type'] == 'TT_Task': ok(sorted(x['rsrc_id'] for x in tr[tid_]) == ['3001', '3002'], f'resources on {r["task_code"]}')
        else: ok(tid_ not in tr, f'milestone with resources {r["task_code"]}')
        if r['task_type'] == 'TT_Task': ok(int(r['target_drtn_hr_cnt']) >= 8, f'duration < 1 day {r["task_code"]}')
    # preds
    preds = collections.defaultdict(list); succs = collections.defaultdict(list); seen = set()
    for r in T['TASKPRED']['r']:
        ok(r['task_id'] in tasks and r['pred_task_id'] in tasks, 'pred ids'); ok(r['task_id'] != r['pred_task_id'], 'self link')
        key = (r['task_id'], r['pred_task_id'], r['pred_type']); ok(key not in seen, 'duplicate relationship'); seen.add(key)
        preds[r['task_id']].append((r['pred_task_id'], r['pred_type'][3:], int(r['lag_hr_cnt']) // 8)); succs[r['pred_task_id']].append(r['task_id'])
    open_start = [tasks[t]['task_code'] for t in tasks if not preds[t]]
    open_end = [tasks[t]['task_code'] for t in tasks if not succs[t]]
    # actv
    types = {r['actv_code_type_id'] for r in T['ACTVTYPE']['r']}; vals = {r['actv_code_id']: r for r in T['ACTVCODE']['r']}
    for r in T['TASKACTV']['r']:
        ok(r['task_id'] in tasks and r['actv_code_id'] in vals and vals[r['actv_code_id']]['actv_code_type_id'] == r['actv_code_type_id'], 'taskactv')
    cnt_codes = collections.Counter(r['task_id'] for r in T['TASKACTV']['r'])
    ok(all(cnt_codes[t] == len(types) for t in tasks), 'every activity must carry all activity-code types')
    # independent forward pass from XER data with the XER calendar
    wd, exc = calendar_from_xer(T)
    ok(wd == {1: True, 2: True, 3: True, 4: True, 5: True, 6: False, 7: False}, f'calendar parse {wd}')
    start = dt.datetime.strptime(T['PROJECT']['r'][0]['plan_start_date'], '%Y-%m-%d %H:%M').date()
    WORK = []; d = start
    while len(WORK) < 1600:
        if (d.weekday() in (6, 0, 1, 2, 3)) and d not in exc: WORK.append(d)
        d += dt.timedelta(days=1)
    idx = {w: i for i, w in enumerate(WORK)}
    order = []; seen_ = set(); stk = set()
    def visit(n):
        if n in seen_: return
        assert n not in stk, 'cycle'
        stk.add(n)
        for p, _, _ in preds[n]: visit(p)
        stk.discard(n); seen_.add(n); order.append(n)
    for n in tasks: visit(n)
    ES = {}; EF = {}
    for n in order:
        r = tasks[n]; dur = int(r['target_drtn_hr_cnt']) // 8
        es = 0 if not preds[n] else -10**9
        for p, t, lag in preds[n]:
            if t == 'FS': es = max(es, EF[p] + 1 + lag)
            elif t == 'SS': es = max(es, ES[p] + lag)
            elif t == 'FF': es = max(es, EF[p] + lag - dur + 1)
        ES[n] = max(es, 0); EF[n] = ES[n] + dur - 1
    mism = 0
    for n, r in tasks.items():
        typ = r['task_type']
        if typ == 'TT_FinMile': got = r['early_end_date'][:10]; exp = WORK[EF[n]].isoformat()
        elif typ == 'TT_Mile': got = r['early_start_date'][:10]; exp = WORK[ES[n]].isoformat()
        else: got = (r['early_start_date'][:10], r['early_end_date'][:10]); exp = (WORK[ES[n]].isoformat(), WORK[EF[n]].isoformat())
        if got != exp: mism += 1
    ok(mism == 0, f'{mism} activities whose dates differ from an independent forward pass')
    finish = WORK[max(EF.values())]
    return dict(errs=errs, activities=len(tasks), tasks=sum(1 for r in tasks.values() if r['task_type'] == 'TT_Task'), milestones=sum(1 for r in tasks.values() if r['task_type'] != 'TT_Task'),
                rels=len(T['TASKPRED']['r']), wbs=len(wbs), maxlvl=maxlvl, cost=cost, pts=pts, open_start=open_start, open_end=open_end, finish=str(finish), mism=mism,
                types=len(types), holidays=len(exc))

if __name__ == '__main__':
    r = run(sys.argv[1]);
    for k, v in r.items(): print(k, v)
