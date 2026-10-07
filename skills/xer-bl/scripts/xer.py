from run_model import *
import io, datetime as dt

def d_start(i): return WORK[i].strftime('%Y-%m-%d') + ' 08:00'
def d_end(i): return WORK[i].strftime('%Y-%m-%d') + ' 17:00'

PROJ_ID = 1001
CLNDR_ID = 1
SHORT = PROJECT_NO

def clndr_data():
    def day(n, work):
        if not work: return f'(0||{n}()())'
        return f'(0||{n}()((0||0(s|08:00|f|12:00)())(0||1(s|13:00|f|17:00)())))'
    days = ''.join(day(i, i in (1, 2, 3, 4, 5)) for i in range(1, 8))
    serial = lambda d: (d - dt.date(1899, 12, 30)).days
    exc = ''
    n = 0
    for h in sorted(HOL):
        if h.weekday() in (4, 5): continue          # already non-working (Fri/Sat)
        exc += f'(0||{n}(d|{serial(h)})())'; n += 1
    return f'(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|Y)())(0||Exceptions()({exc}))))'

def esc(v):
    if v is None: return ''
    return str(v).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')

class Xer:
    def __init__(self): self.tables = []
    def table(self, name, fields, rows):
        self.tables.append((name, fields, rows))
    def dump(self, hdr):
        out = io.StringIO()
        out.write('\t'.join(hdr) + '\n')
        for name, fields, rows in self.tables:
            out.write(f'%T\t{name}\n')
            out.write('%F\t' + '\t'.join(fields) + '\n')
            for r in rows:
                assert len(r) == len(fields), (name, len(r), len(fields), r[:3])
                out.write('%R\t' + '\t'.join(esc(v) for v in r) + '\n')
        out.write('%E\n')
        return out.getvalue()

def build_xer(lag):
    order, pred_of, ES, EF, LS, LF, succ = finalize(lag)
    x = Xer()
    # currency + units
    x.table('CURRTYPE', ['curr_id', 'decimal_digit', 'curr_symbol', 'decimal_symbol', 'digit_group_symbol', 'pos_curr_fmt_type', 'neg_curr_fmt_type', 'curr_type', 'curr_short_name', 'group_digit_cnt', 'base_exch_rate'],
            [[1, 2, 'SAR', '.', ',', '#1.1', '(#1.1)', 'Saudi Riyal', 'SAR', 3, 1]])
    x.table('UMEASURE', ['unit_id', 'seq_num', 'unit_abbrev', 'unit_name'], [[1, 1, 'SAR', 'Saudi Riyal (cost units)'], [2, 2, 'pt', 'Progress point (0.001 percent of project)']])
    x.table('OBS', ['obs_id', 'parent_obs_id', 'seq_num', 'obs_name', 'obs_descr'], [[1, '', 1, 'SAR Security Program', 'ETECHS project team']])
    x.table('CALENDAR', ['clndr_id', 'default_flag', 'clndr_name', 'proj_id', 'base_clndr_id', 'last_chng_date', 'clndr_type', 'day_hr_cnt', 'week_hr_cnt', 'month_hr_cnt', 'year_hr_cnt', 'rsrc_private', 'clndr_data'],
            [[CLNDR_ID, 'Y', 'KSA Sun-Thu 8h (official holidays)', '', '', '2026-10-06 09:00', 'CA_Base', 8, 40, 172, 2080, 'N', clndr_data()]])
    last = max(EF.values())
    pf = ['proj_id', 'fy_start_month_num', 'rsrc_self_add_flag', 'allow_complete_flag', 'rsrc_multi_assign_flag', 'checkout_flag', 'project_flag', 'step_complete_flag', 'cost_qty_recalc_flag', 'batch_sum_flag',
          'name_sep_char', 'def_complete_pct_type', 'proj_short_name', 'acct_id', 'orig_proj_id', 'source_proj_id', 'base_type_id', 'clndr_id', 'sum_base_proj_id', 'task_code_base', 'task_code_step', 'priority_num',
          'wbs_max_sum_level', 'strgy_priority_num', 'last_checksum', 'critical_drtn_hr_cnt', 'def_cost_per_qty', 'last_recalc_date', 'plan_start_date', 'plan_end_date', 'scd_end_date', 'add_date', 'last_tasksum_date',
          'fcst_start_date', 'def_duration_type', 'task_code_prefix', 'guid', 'def_qty_type', 'add_by_name', 'web_local_root_path', 'proj_url', 'def_rate_type', 'add_act_remain_flag', 'act_this_per_link_flag',
          'def_task_type', 'act_pct_link_flag', 'critical_path_type', 'task_code_prefix_flag', 'def_rollup_dates_flag', 'rem_target_link_flag', 'reset_planned_flag', 'allow_neg_act_flag', 'sum_assign_level',
          'last_fin_dates_id', 'last_baseline_update_date', 'cr_external_key', 'apply_actuals_date', 'location_id', 'loaded_scope_level', 'export_flag', 'new_fin_dates_id', 'baselines_to_export',
          'baseline_names_to_export', 'next_data_date', 'close_period_flag', 'sum_refresh_date', 'trsrcsum_loaded']
    pv = dict(proj_id=PROJ_ID, fy_start_month_num=1, rsrc_self_add_flag='Y', allow_complete_flag='Y', rsrc_multi_assign_flag='Y', checkout_flag='N', project_flag='Y', step_complete_flag='N',
              cost_qty_recalc_flag='N', batch_sum_flag='Y', name_sep_char='.', def_complete_pct_type='CP_Phys', proj_short_name=SHORT, clndr_id=CLNDR_ID, task_code_base=1000, task_code_step=10,
              priority_num=10, wbs_max_sum_level=0, strgy_priority_num=100, critical_drtn_hr_cnt=0, def_cost_per_qty=0, last_recalc_date=d_start(0), plan_start_date=d_start(0),
              plan_end_date=d_end(last), scd_end_date=d_end(last), add_date='2026-10-06 09:00', def_duration_type='DT_FixedDrtn', guid='SARSEC00-0000-4000-8000-000000000001', def_qty_type='QT_Hour',
              add_by_name='admin', def_rate_type='COST_PER_QTY', add_act_remain_flag='N', act_this_per_link_flag='Y', def_task_type='TT_Task', act_pct_link_flag='Y', critical_path_type='CT_TotFloat',
              task_code_prefix_flag='N', def_rollup_dates_flag='N', rem_target_link_flag='Y', reset_planned_flag='N', allow_neg_act_flag='N', sum_assign_level='SL_Taskrsrc', loaded_scope_level=7,
              export_flag='Y', close_period_flag='Y')
    x.table('PROJECT', pf, [[pv.get(f, '') for f in pf]])
    # WBS
    wid = {}
    rows = []
    for i, (code, w) in enumerate(WBS.items()):
        wid[code] = 2000 + i
    for i, (code, w) in enumerate(WBS.items()):
        short = code.split('.')[-1] if w['parent'] else SHORT
        rows.append([wid[code], PROJ_ID, 1, (i + 1) * 10, 1, 'Y' if not w['parent'] else 'N', 'N', 'WS_Open', short, w['name'], wid[w['parent']] if w['parent'] else ''])
    x.table('PROJWBS', ['wbs_id', 'proj_id', 'obs_id', 'seq_num', 'est_wt', 'proj_node_flag', 'sum_data_flag', 'status_code', 'wbs_short_name', 'wbs_name', 'parent_wbs_id'], rows)
    # resources
    x.table('RSRC', ['rsrc_id', 'parent_rsrc_id', 'clndr_id', 'rsrc_seq_num', 'rsrc_name', 'rsrc_short_name', 'rsrc_title_name', 'def_qty_per_hr', 'cost_qty_type', 'ot_factor', 'active_flag', 'auto_compute_act_flag', 'def_cost_qty_link_flag', 'ot_flag',
                     'curr_id', 'unit_id', 'rsrc_type', 'load_tasks_flag', 'level_flag'],
            [[3001, '', CLNDR_ID, 1, 'Contract cost (BOQ x payment milestones)', 'COST-SAR', 'Contract cost quantity in SAR (price 0)', 1, 'QT_Hour', 0, 'Y', 'Y', 'Y', 'N', 1, 1, 'RT_Mat', 'N', 'N'],
             [3002, '', CLNDR_ID, 2, 'Progress weight (fair EPC distribution, SAR value)', 'PROG-WT', 'Progress value in SAR (price 1)', 1, 'QT_Hour', 0, 'Y', 'Y', 'N', 'N', 1, 1, 'RT_Mat', 'N', 'N']])
    x.table('RSRCRATE', ['rsrc_rate_id', 'rsrc_id', 'max_qty_per_hr', 'cost_per_qty', 'start_date', 'cost_per_qty2', 'cost_per_qty3', 'cost_per_qty4', 'cost_per_qty5'],
            [[3101, 3001, '', 0, '2026-01-01 00:00', 0, 0, 0, 0], [3102, 3002, 1000000, 1, '2026-01-01 00:00', 0, 0, 0, 0]])
    # activity code types
    CT = OrderedDict([('EPC', 'EPC phase'), ('AREA', 'Area'), ('STN', 'Station'), ('RAIL', 'Railway'), ('DISC', 'Discipline'), ('RESP', 'Responsibility'),
                      ('MST', 'Payment milestone'), ('STAGE', 'Design stage'), ('SUBAPP', 'Submittal or approval'), ('PRIO', 'Priority'), ('PHASE', 'Programme phase')])
    LABEL = {'EPC': {'MOB': 'Mobilization', 'ENG': 'Engineering', 'PRO': 'Procurement', 'CON': 'Construction', 'COM': 'Commissioning and handover', 'PMG': 'Project management', 'MS': 'Milestone'},
             'AREA': {'NSR': 'NSR', 'EWR': 'EWR', 'HHR': 'HHR', 'PRJ': 'Project level'},
             'RAIL': {'NSR': 'NSR', 'EWR': 'EWR', 'HHR': 'HHR', 'ALL': 'All railways'},
             'DISC': {'DOCS': 'Design documentation', 'CCTV': 'CCTV system', 'VMS': 'Video management and wall', 'ACC': 'Access control and intercom', 'UPSNET': 'UPS, network and cabinets', 'CIVIL': 'Civil works', 'TC': 'Testing, commissioning and handover', 'PM': 'Project management and logistics'},
             'RESP': {'ETECHS': 'ETECHS', 'SAR': 'SAR', 'SAR/HCIS': 'SAR and HCIS', 'Vendor': 'Vendor'},
             'MST': {'-': 'Not a payment milestone'} | {k: f'{k} {v[0]}' for k, v in MS.items()},
             'STAGE': {'-': 'Not a design stage', 'POC': 'Proof of concept', 'Survey': 'Site survey', 'Concept': 'Concept design', 'Preliminary': 'Preliminary design', 'Detailed': 'Detailed design', 'IFC': 'IFC and shop drawings', 'HCIS': 'HCIS documentation', 'As-built': 'As-built and O&M'},
             'SUBAPP': {'-': 'Not applicable', 'Submittal': 'Submittal', 'Approval': 'Approval'},
             'PRIO': {'Priority 1': 'Priority 1 - Makkah and Riyadh (Thumamah)', 'Priority 2': 'Priority 2 - Riyadh (Malaz)', 'Standard': 'Standard'},
             'PHASE': {'MOB': 'Mobilization and survey permit (months 1-2)', 'DES': 'Design including survey (months 3-6)', 'POC': 'Proof of concept - Riyadh (Thumamah)', 'ENA': 'Enabling works',
                       'PRO': 'Procurement and supply', 'CON': 'Construction and installation', 'COM': 'Testing, commissioning and handover', 'PMG': 'Project management and closeout', 'MS': 'Milestones'}}
    LABEL['STN'] = {'PRJ': 'Project level'} | {s['code']: f"{s['name']} ({s['line']})" for s in ST.values()}
    tid = {}; types = []; vals = []; vid = {}
    n_val = 0
    for ti, (k, nm) in enumerate(CT.items()):
        tid[k] = 4000 + ti
        types.append([tid[k], 40, ti + 1, nm, PROJ_ID, '', 'AS_Project'])
        for si, (vk, vl) in enumerate(LABEL[k].items()):
            n_val += 1; vid[(k, vk)] = 4100 + n_val
            vals.append([vid[(k, vk)], '', tid[k], vl, vk[:40], si + 1, '', 0])
    x.table('ACTVTYPE', ['actv_code_type_id', 'actv_short_len', 'seq_num', 'actv_code_type', 'proj_id', 'wbs_id', 'actv_code_type_scope'], types)
    x.table('ACTVCODE', ['actv_code_id', 'parent_actv_code_id', 'actv_code_type_id', 'actv_code_name', 'short_name', 'seq_num', 'color', 'total_assignments'], vals)
    # tasks
    tids = {code: 5000 + i for i, code in enumerate(ACTS)}
    rows = []; rr = []; ta = []; tp = []
    ff = {}
    for n in order:
        mn = 10**9
        for s_, t, lag_ in succ[n]:
            if t == 'FS': v = ES[s_] - (EF[n] + 1 + lag_)
            elif t == 'SS': v = ES[s_] - (ES[n] + lag_)
            elif t == 'FF': v = EF[s_] - (EF[n] + lag_)
            else: v = 0
            mn = min(mn, max(v, 0))
        ff[n] = 0 if mn >= 10**9 else mn
    tr = 0; k_ta = 0; k_tp = 0
    def lagv(l): return (lag[l[1]] if isinstance(l, tuple) else l)
    DEFAULTS = dict(EPC='PMG', AREA='PRJ', STN='PRJ', RAIL='ALL', DISC='PM', RESP='ETECHS', MST='-', STAGE='-', SUBAPP='-', PRIO='Standard')
    def phase_of(code, a):
        suf = code.split('-', 1)[1]
        if a.typ != 'TT_Task' and not suf.startswith('POC'): return 'MS'
        if code.startswith('PRJ-'): return 'MOB' if suf[0] == 'A' and suf < 'A2000' else ('PMG')
        if suf.startswith('POC'): return 'POC'
        if suf == 'E1005': return 'MOB'
        if suf[0] == 'E': return 'COM' if suf in ('E1130', 'E1140') else 'DES'
        return {'X': 'ENA', 'P': 'PRO', 'C': 'CON', 'T': 'COM'}[suf[0]]
    for code, a in ACTS.items():
        a.codes.setdefault('PHASE', phase_of(code, a))
        for kk, vv in DEFAULTS.items(): a.codes.setdefault(kk, vv)
        if a.codes['MST'] == '-' and a.cost_ms: a.codes['MST'] = a.cost_ms[0]
    for code, a in ACTS.items():
        dur = a.dur
        if a.typ == 'TT_Mile': es_d = ef_d = d_start(ES[code])
        elif a.typ == 'TT_FinMile': es_d = ef_d = d_end(EF[code])
        else: es_d, ef_d = d_start(ES[code]), d_end(EF[code])
        lsd = d_start(LS[code]) if a.typ != 'TT_FinMile' else d_end(LF[code])
        lfd = d_end(LF[code]) if a.typ != 'TT_Mile' else d_start(LS[code])
        tf = (LF[code] - EF[code]) * 8
        rows.append([tids[code], PROJ_ID, wid[a.wbs], CLNDR_ID, 0, 'N', 'CP_Phys', a.typ, 'DT_FixedDrtn', 'TK_NotStart', code, a.name,
                     tf, ff[code] * 8, dur * 8, dur * 8, es_d, ef_d, lsd, lfd, es_d, ef_d, es_d, ef_d, '', 'PRI_Normal'])
        if a.typ == 'TT_Task':
            for rid, qty, cst in ((3001, a.cost, 0), (3002, a.pts * 620, a.pts * 620)):
                k_ta += 1
                rr.append([6000 + k_ta, tids[code], PROJ_ID, 'Y', rid, 0, 0, qty, cst, qty, cst, es_d, ef_d, lsd, lfd, 'RT_Mat', 0 if rid == 3001 else 1])
        for p, t, l in pred_of[code]:
            k_tp += 1
            tp.append([8000 + k_tp, tids[code], tids[p], PROJ_ID, PROJ_ID, 'PR_' + t, l * 8])
        for ck, cv in a.codes.items():
            ta.append([tids[code], tid[ck], vid[(ck, cv)], PROJ_ID])
    x.table('TASK', ['task_id', 'proj_id', 'wbs_id', 'clndr_id', 'phys_complete_pct', 'rev_fdbk_flag', 'complete_pct_type', 'task_type', 'duration_type', 'status_code', 'task_code', 'task_name',
                     'total_float_hr_cnt', 'free_float_hr_cnt', 'remain_drtn_hr_cnt', 'target_drtn_hr_cnt', 'early_start_date', 'early_end_date', 'late_start_date', 'late_end_date',
                     'target_start_date', 'target_end_date', 'restart_date', 'reend_date', 'cstr_type', 'priority_type'], rows)
    x.table('TASKPRED', ['task_pred_id', 'task_id', 'pred_task_id', 'proj_id', 'pred_proj_id', 'pred_type', 'lag_hr_cnt'], tp)
    x.table('TASKRSRC', ['taskrsrc_id', 'task_id', 'proj_id', 'cost_qty_link_flag', 'rsrc_id', 'act_reg_qty', 'act_reg_cost', 'target_qty', 'target_cost', 'remain_qty', 'remain_cost',
                         'target_start_date', 'target_end_date', 'rem_late_start_date', 'rem_late_end_date', 'rsrc_type', 'cost_per_qty'], rr)
    x.table('TASKACTV', ['task_id', 'actv_code_type_id', 'actv_code_id', 'proj_id'], ta)
    hdr = ['ERMHDR', '24.12', '2026-10-06', 'Project', 'admin', 'ETECHS Planning', 'PMDB', 'Project Management', 'SAR']
    meta = dict(order=order, pred_of=pred_of, ES=ES, EF=EF, LS=LS, LF=LF, succ=succ, tids=tids, wid=wid, ff=ff, lag=lag)
    meta['LABEL'] = LABEL
    return x.dump(hdr), meta

if __name__ == '__main__':
    k, lag = solve()
    txt, meta = build_xer(lag)
    open('/tmp/w/test.xer', 'w', encoding='utf-8', newline='\n').write(txt)
    print(len(txt), txt.count('\n'))
    print(txt[:700])
