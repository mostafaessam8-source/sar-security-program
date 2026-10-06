from model_base import *
import copy

def rnd(x): return int(x + 0.5)

def build(k_stretch=1.0, buffer_days=20):
    ACTS.clear(); WBS.clear()
    wbs('SAR-SEC', 'SAR Passengers Security Checking - HHR, EWR, NSR (14 stations)')
    EP = {'PM': 'Project Management and Mobilization', 'ENG': 'Engineering', 'PRO': 'Procurement', 'CON': 'Construction', 'COM': 'Commissioning and Handover'}
    for c, n in EP.items(): wbs(c, n, 'SAR-SEC')
    wbs('PM.MOB', 'Mobilization and baseline programme', 'PM'); wbs('PM.MST', 'Contract milestones', 'PM'); wbs('PM.CLO', 'Closeout', 'PM')
    AREAS = OrderedDict([('RYD', 'Riyadh priority stations (NSR + EWR)'), ('NSR', 'NSR - North South Railway'), ('EWR', 'EWR - East West Railway'), ('HHR', 'HHR - Haramain High Speed Rail')])
    for ep in ('ENG', 'PRO', 'CON', 'COM'):
        for a, n in AREAS.items(): wbs(f'{ep}.{a}', n, ep)

    def area_of(s): return 'RYD' if s['ryd'] else s['line']

    CODEBASE = {}
    # ---------------------------------------------------------------- project level
    pm = 'PM.MOB'
    A0 = act('PRJ-M0000', 'Notice to Proceed - project start (1 Nov 2026, editable)', 'PM.MST', 0, 'TT_Mile', EPC='MS', AREA='PRJ', STN='PRJ', RAIL='ALL', DISC='PM', RESP='SAR', MST='-', STAGE='-', SUBAPP='-', PRIO='Standard')
    def prj(code, name, w, dur, preds, typ='TT_Task', **kw):
        base = dict(EPC='PMG', AREA='PRJ', STN='PRJ', RAIL='ALL', DISC='PM', RESP='ETECHS', MST='-', STAGE='-', SUBAPP='-', PRIO='Standard'); base.update(kw)
        a = act(code, name, w, dur, typ, preds, **base); return a
    prj('PRJ-A1010', 'Performance security, insurance and key personnel approval', pm, 10, [('PRJ-M0000', 'FS', 0)], MST='MS1')
    prj('PRJ-A1020', 'Initial baseline programme (Primavera) covering mobilization and survey', pm, 7, [('PRJ-M0000', 'FS', 0)], MST='MS1')
    prj('PRJ-A1030', 'SAR review and approval of initial baseline', pm, 15, [('PRJ-A1020', 'FS', 0)], RESP='SAR', SUBAPP='Approval', MST='MS1')
    prj('PRJ-A1040', 'Mobilization: site establishment, offices, personnel and tools', pm, 25, [('PRJ-M0000', 'FS', 5)], MST='MS1')
    prj('PRJ-A1050', 'Mobilization submittals: QC programme and ITP, HSE, security, procurement and shipping plan', pm, 20, [('PRJ-M0000', 'FS', 5)], SUBAPP='Submittal', MST='MS1')
    prj('PRJ-M1100', 'MS1 Mobilization complete (payment milestone 20%)', 'PM.MST', 0, [('PRJ-A1010', 'FS', 0), ('PRJ-A1030', 'FS', 0), ('PRJ-A1040', 'FS', 0), ('PRJ-A1050', 'FS', 0)], 'TT_FinMile', EPC='MS', MST='MS1', RESP='SAR')
    prj('PRJ-A2010', 'Detailed baseline programme (within 21 days after survey)', pm, 15, [], SUBAPP='Submittal')
    prj('PRJ-A2020', 'SAR review and approval of detailed baseline', pm, 15, [('PRJ-A2010', 'FS', 0)], RESP='SAR', SUBAPP='Approval')
    prj('PRJ-M2100', 'Detailed baseline programme approved', 'PM.MST', 0, [('PRJ-A2020', 'FS', 0)], 'TT_FinMile', EPC='MS', RESP='SAR')
    prj('PRJ-C1010', 'Contract closeout pack and handover documentation', 'PM.CLO', 10, [], EPC='PMG', SUBAPP='Submittal')
    prj('PRJ-MX99', 'Contract completion - end of 36-month term', 'PM.MST', 0, [('PRJ-C1010', 'FS', 0), ('PRJ-M0000', 'FS', TERM_IDX + 1)], 'TT_FinMile', EPC='MS', RESP='SAR')

    # cost / progress keys for project level
    MOB_KEY = {'PRJ-A1010': 15, 'PRJ-A1020': 10, 'PRJ-A1040': 45, 'PRJ-A1050': 30}
    PRJ_PROG = {'PRJ-A1010': 0.4, 'PRJ-A1020': 0.2, 'PRJ-A1030': 0.2, 'PRJ-A1040': 0.8, 'PRJ-A1050': 0.6, 'PRJ-A2010': 0.3, 'PRJ-A2020': 0.2, 'PRJ-C1010': 1.3}
    for c, w in MOB_KEY.items():
        ACTS[c].cost_ms = ('MS1', w / 100.0); ACTS[c].basis = f'MS1 Mobilization 20% of the total price (SAR {0.20*PO:,.0f}) x key {w}%'
        ACTS[c].boq = 'Contract price (62,000,000) x 20% mobilization payment (contract clause 15)'
    for c, w in PRJ_PROG.items(): ACTS[c].prog = w

    # ---------------------------------------------------------------- station level
    dbase_dur_days = None
    surveys = []; accepted = []
    for sid, s in ST.items():
        c = s['code']; p = s['p']; E = p['E']; S = p['sat']; I = p['inst']; C = p['civil']
        area = area_of(s); name = s['name']
        for ep in ('ENG', 'PRO', 'CON', 'COM'):
            wbs(f'{ep}.{area}.{c}', f'{name} ({s["line"]})', f'{ep}.{area}')
        eng = f'ENG.{area}.{c}'; pro = f'PRO.{area}.{c}'; con = f'CON.{area}.{c}'; com = f'COM.{area}.{c}'
        stages = [('SRV', 'Site survey and as-found verification'), ('CNC', 'Concept design'), ('PRE', 'Preliminary (schematic) design'),
                  ('DET', 'Detailed design'), ('IFC', 'IFC and shop drawings'), ('HCS', 'HCIS documentation (Stage 3 and 4)'), ('ASB', 'As-built and O&M documentation')]
        for sc, sn in stages:
            wbs(f'{eng}.{sc}', sn, eng); wbs(f'{eng}.{sc}.SUB', 'Submittal', f'{eng}.{sc}'); wbs(f'{eng}.{sc}.APR', 'Approval', f'{eng}.{sc}')
        for pc, pn in [('CCT', 'CCTV system'), ('VMS', 'Video management and video wall'), ('ACC', 'Access control and intercom'), ('UPN', 'UPS, network and cabinets'), ('LOG', 'FAT and logistics')]:
            wbs(f'{pro}.{pc}', pn, pro)
        wbs(f'{con}.CIV', 'Civil works', con); wbs(f'{con}.INS', 'Installation', con)
        wbs(f'{com}.TST', 'Testing and commissioning', com); wbs(f'{com}.TRN', 'Training', com); wbs(f'{com}.TOA', 'Trial operation and acceptance', com)
        base = dict(AREA=area, STN=c, RAIL=s['line'], PRIO='Riyadh priority' if s['ryd'] else 'Standard')

        def A(n, nm, w, dur, preds, typ='TT_Task', **kw):
            code = f'{c}-{n}'
            d = dict(base); d.update(kw)
            a = act(code, f'{nm} - {name}', w, dur, typ, [(f'{c}-{p_}' if not p_.startswith('PRJ') else p_, t, l) for p_, t, l in preds], **d)
            a.station = sid
            return a
        c1 = rnd(0.15 * E); p1 = rnd(0.25 * E); d1 = rnd(0.40 * E); i1 = E - (c1 + p1 + d1); L = rnd(0.15 * E); h1 = E - (c1 + p1 + L)
        ENGK = dict(EPC='ENG', DISC='DOCS')
        A('E1010', 'Survey: submittal of site survey and as-found report', f'{eng}.SRV.SUB', p['sv'], [], RESP='ETECHS', STAGE='Survey', SUBAPP='Submittal', **ENGK)
        A('E1020', 'Survey: SAR approval of survey report', f'{eng}.SRV.APR', 5, [('E1010', 'FS', 0)], RESP='SAR', STAGE='Survey', SUBAPP='Approval', **ENGK)
        A('E1030', 'Concept design: submittal', f'{eng}.CNC.SUB', c1, [('E1010', 'FS', 0)], RESP='ETECHS', STAGE='Concept', SUBAPP='Submittal', **ENGK)
        A('E1040', 'Concept design: SAR review and approval', f'{eng}.CNC.APR', p['appr'], [('E1030', 'FS', 0)], RESP='SAR', STAGE='Concept', SUBAPP='Approval', **ENGK)
        A('E1050', 'Preliminary design: submittal', f'{eng}.PRE.SUB', p1, [('E1030', 'FS', 0)], RESP='ETECHS', STAGE='Preliminary', SUBAPP='Submittal', **ENGK)
        A('E1060', 'Preliminary design: SAR review and approval', f'{eng}.PRE.APR', p['appr'], [('E1050', 'FS', 0)], RESP='SAR', STAGE='Preliminary', SUBAPP='Approval', **ENGK)
        A('E1070', 'Detailed design: submittal (drawings, BOQ, data sheets)', f'{eng}.DET.SUB', d1, [('E1050', 'FS', 0)], RESP='ETECHS', STAGE='Detailed', SUBAPP='Submittal', **ENGK)
        A('E1080', 'Detailed design: SAR review and approval', f'{eng}.DET.APR', p['appr'], [('E1070', 'FS', 0)], RESP='SAR', STAGE='Detailed', SUBAPP='Approval', **ENGK)
        A('E1090', 'IFC and shop drawings: submittal', f'{eng}.IFC.SUB', i1, [('E1070', 'FS', 0)], RESP='ETECHS', STAGE='IFC', SUBAPP='Submittal', **ENGK)
        A('E1100', 'IFC and shop drawings: SAR approval and release', f'{eng}.IFC.APR', p['appr'], [('E1090', 'FS', 0)], RESP='SAR', STAGE='IFC', SUBAPP='Approval', **ENGK)
        A('E1110', 'HCIS Stage 3 and 4 documents: preparation', f'{eng}.HCS.SUB', h1, [('E1050', 'FS', L), ('E1090', 'FF', 0)], RESP='ETECHS', STAGE='HCIS', SUBAPP='Submittal', **ENGK)
        A('E1120', 'HCIS Stage 3 and 4 documents: SAR final review and HCIS submission', f'{eng}.HCS.APR', p['appr'], [('E1110', 'FS', 0)], RESP='SAR/HCIS', STAGE='HCIS', SUBAPP='Approval', **ENGK)
        A('E1130', 'As-built and O&M documentation: submittal', f'{eng}.ASB.SUB', S + 15, [(f'C2100', 'FS', 0)], RESP='ETECHS', STAGE='As-built', SUBAPP='Submittal', **ENGK)
        A('E1140', 'As-built and O&M documentation: SAR review and approval', f'{eng}.ASB.APR', p['appr'], [('E1130', 'FS', 0)], RESP='SAR', STAGE='As-built', SUBAPP='Approval', **ENGK)
        A('E1200', 'MS2 Engineering submittal complete (10%)', eng, 0, [('E1090', 'FS', 0), ('E1110', 'FS', 0)], 'TT_FinMile', EPC='MS', DISC='DOCS', RESP='ETECHS', STAGE='-', SUBAPP='-', MST='MS2')
        A('E1210', 'MS3 Engineering approved by SAR (10%)', eng, 0, [('E1020', 'FS', 0), ('E1040', 'FS', 0), ('E1060', 'FS', 0), ('E1080', 'FS', 0), ('E1100', 'FS', 0), ('E1120', 'FS', 0), ('E1200', 'FS', 0)], 'TT_FinMile', EPC='MS', DISC='DOCS', RESP='SAR', STAGE='-', SUBAPP='-', MST='MS3')
        # procurement
        PK = dict(EPC='PRO', STAGE='-', SUBAPP='-')
        man = p['proc'] - 10
        A('P1010', 'Manufacture CCTV cameras and analytics', f'{pro}.CCT', man, [('E1210', 'FS', 0)], DISC='CCTV', RESP='Vendor', **PK)
        A('P1020', 'Manufacture video management servers, storage and video wall', f'{pro}.VMS', man, [('E1210', 'FS', 0)], DISC='VMS', RESP='Vendor', **PK)
        A('P1030', 'Manufacture access control and intercom equipment', f'{pro}.ACC', man, [('E1210', 'FS', 0)], DISC='ACC', RESP='Vendor', **PK)
        A('P1040', 'Manufacture UPS, network switches and field cabinets', f'{pro}.UPN', man, [('E1210', 'FS', 0)], DISC='UPSNET', RESP='Vendor', **PK)
        A('P1050', 'Factory acceptance test at vendor premises', f'{pro}.LOG', 10, [('P1010', 'FS', 0), ('P1020', 'FS', 0), ('P1030', 'FS', 0), ('P1040', 'FS', 0)], DISC='PM', RESP='ETECHS', **PK)
        A('P1060', 'Shipping and customs clearance', f'{pro}.LOG', p['ship'] - 5, [('P1050', 'FS', 0)], DISC='PM', RESP='Vendor', **PK)
        A('P1070', 'Delivery to station and receiving inspection', f'{pro}.LOG', 5, [('P1060', 'FS', 0)], DISC='PM', RESP='ETECHS', **PK)
        A('P1100', 'MS4 Material delivered (20%)', pro, 0, [('P1070', 'FS', 0)], 'TT_FinMile', EPC='MS', DISC='PM', RESP='ETECHS', STAGE='-', SUBAPP='-', MST='MS4')
        # construction
        CK = dict(EPC='CON', STAGE='-', SUBAPP='-', RESP='ETECHS')
        A('C1010', 'Civil: platform trenches and duct banks', f'{con}.CIV', rnd(0.70 * C), [('E1210', 'FS', 0)], DISC='CIVIL', **CK)
        A('C1020', 'Civil: camera and ALPR pole foundations and poles', f'{con}.CIV', rnd(0.55 * C), [('C1010', 'SS', rnd(0.45 * C))], DISC='CIVIL', **CK)
        A('C2010', 'Install UPS, network switches and field cabinets', f'{con}.INS', rnd(0.30 * I), [('P1100', 'FS', 0)], DISC='UPSNET', **CK)
        A('C2020', 'Cabling and termination (power, fibre, data)', f'{con}.INS', rnd(0.50 * I), [('C2010', 'SS', rnd(0.10 * I)), ('C1010', 'SS', math.ceil(C / 2))], DISC='CCTV', **CK)
        A('C2030', 'Install and aim CCTV cameras', f'{con}.INS', rnd(0.40 * I), [('C2020', 'FS', 0), ('C1020', 'FS', 0)], DISC='CCTV', **CK)
        A('C2040', 'Install video management, video wall and control-room equipment', f'{con}.INS', rnd(0.35 * I), [('C2010', 'FS', 0)], DISC='VMS', **CK)
        A('C2050', 'Install access control and intercom', f'{con}.INS', rnd(0.30 * I), [('C2010', 'FS', rnd(0.10 * I))], DISC='ACC', **CK)
        A('C2100', 'MS5 Installation complete (20%)', con, 0, [('C2020', 'FS', 0), ('C2030', 'FS', 0), ('C2040', 'FS', 0), ('C2050', 'FS', 0), ('C1020', 'FS', 0)], 'TT_FinMile', EPC='MS', DISC='PM', RESP='ETECHS', STAGE='-', SUBAPP='-', MST='MS5')
        # commissioning
        TK = dict(EPC='COM', STAGE='-', SUBAPP='-')
        pre = rnd(0.4 * S)
        A('T1010', 'Pre-commissioning and loop checks', f'{com}.TST', pre, [('C2100', 'FS', 0)], DISC='TC', RESP='ETECHS', **TK)
        A('T1020', 'Site acceptance test (SAT) and commissioning', f'{com}.TST', S - pre, [('T1010', 'FS', 0)], DISC='TC', RESP='ETECHS', **TK)
        A('T1100', 'MS6 SAT complete (10%)', com, 0, [('T1020', 'FS', 0)], 'TT_FinMile', EPC='MS', DISC='TC', RESP='SAR', STAGE='-', SUBAPP='-', MST='MS6')
        A('T2010', 'Operator and maintenance training', f'{com}.TRN', p['train'], [('T1020', 'FS', 0)], DISC='TC', RESP='ETECHS', **TK)
        A('T2020', 'Trial operation (maximum 45 days)', f'{com}.TOA', p['trial'], [('T1020', 'FS', 0)], DISC='TC', RESP='SAR', **TK)
        A('T3010', 'Taking-over application, SAR review and handover', f'{com}.TOA', p['final'], [('T1100', 'FS', 0), ('T2010', 'FS', 0), ('T2020', 'FS', 0), ('E1140', 'FS', 0)], DISC='TC', RESP='SAR', **TK)
        A('T3100', 'MS7 Station accepted - final acceptance and handover (10%)', com, 0, [('T3010', 'FS', 0)], 'TT_FinMile', EPC='MS', DISC='TC', RESP='SAR', STAGE='-', SUBAPP='-', MST='MS7')
        ACTS[f'{c}-T3100'].codes['MST'] = 'MS7'
        surveys.append(f'{c}-E1010'); accepted.append(f'{c}-T3100')
        ST[sid]['_c'] = c
        # milestone cost + progress keys
        f = s['f']; Mamt = lambda k_: MS[k_][1] * PO * f
        H5 = sum(s['hw'][x] for x in ('cctv', 'vms', 'ac', 'ups', 'net')); H6 = H5 + s['hw']['civil']; a6 = s['hw']['civil'] / H6
        pk = {'P1010': s['hw']['cctv'] / H5, 'P1020': s['hw']['vms'] / H5, 'P1030': s['hw']['ac'] / H5, 'P1040': (s['hw']['ups'] + s['hw']['net']) / H5}
        design_key = {'E1010': 5, 'E1030': 10, 'E1050': 20, 'E1070': 40, 'E1090': 20, 'E1110': 5}
        appr_key = {'E1020': 5, 'E1040': 10, 'E1060': 20, 'E1080': 40, 'E1100': 20, 'E1120': 5}
        KEYS = []
        for n, w in design_key.items(): KEYS.append((n, 'MS2', w / 100.0, f'Design stage key {w}% of the engineering-submittal milestone', 'Annex 3 Design and engineering package (railway) allocated by station hardware share'))
        for n, w in appr_key.items(): KEYS.append((n, 'MS3', w / 100.0, f'Design stage key {w}% of the SAR-approval milestone', 'Annex 3 Design and engineering package (railway) allocated by station hardware share'))
        names_pk = {'P1010': ('A1 CCTV system', s['hw']['cctv']), 'P1020': ('A2 Video management and wall', s['hw']['vms']), 'P1030': ('A3 Access control and intercom', s['hw']['ac']), 'P1040': ('A4 UPS + A5 poles, cabinets and network', s['hw']['ups'] + s['hw']['net'])}
        for n, share in pk.items(): KEYS.append((n, 'MS4', 0.75 * share, f'BOQ section share {share*100:.1f}% of station equipment x 75% (manufacture)', f'Annex 3 {names_pk[n][0]} (SAR {names_pk[n][1]:,.0f})'))
        KEYS += [('P1050', 'MS4', 0.05, 'Fixed key 5% (FAT)', 'Annex 3 Factory acceptance test (railway), allocated by hardware share'),
                 ('P1060', 'MS4', 0.15, 'Fixed key 15% (shipping and customs)', 'Annex 3 equipment sections A1-A5 (logistics share)'),
                 ('P1070', 'MS4', 0.05, 'Fixed key 5% (delivery, receiving) incl. commissioning spares', 'Annex 3 Commissioning spares (railway), allocated by hardware share')]
        KEYS += [('C1010', 'MS5', 0.55 * a6, f'BOQ civil share {a6*100:.1f}% x 55% (trenches and duct banks)', f'Annex 3 A6 Civil works (SAR {s["hw"]["civil"]:,.0f})'),
                 ('C1020', 'MS5', 0.45 * a6, f'BOQ civil share {a6*100:.1f}% x 45% (poles)', f'Annex 3 A6 Civil works (SAR {s["hw"]["civil"]:,.0f})')]
        for n, w in {'C2010': 0.20, 'C2020': 0.30, 'C2030': 0.25, 'C2040': 0.15, 'C2050': 0.10}.items():
            KEYS.append((n, 'MS5', (1 - a6) * w, f'Installation key {int(w*100)}% x (1 - civil share {a6*100:.1f}%)', 'Annex 3 equipment sections A1-A5 (installation share)'))
        KEYS += [('T1010', 'MS6', 0.40, 'Fixed key 40% of SAT milestone', 'Annex 3 equipment sections A1-A5 (testing share)'), ('T1020', 'MS6', 0.60, 'Fixed key 60% of SAT milestone', 'Annex 3 equipment sections A1-A5 (testing share)'),
                 ('E1130', 'MS7', 0.15, 'Fixed key 15% of final-acceptance milestone', 'Annex 3 documentation and training share'), ('E1140', 'MS7', 0.05, 'Fixed key 5%', 'Annex 3 documentation share'),
                 ('T2010', 'MS7', 0.15, 'Fixed key 15%', 'Annex 3 Training (railway), allocated by hardware share'), ('T2020', 'MS7', 0.35, 'Fixed key 35%', 'Annex 3 equipment sections A1-A5 (trial operation share)'),
                 ('T3010', 'MS7', 0.30, 'Fixed key 30%', 'Annex 3 equipment sections A1-A5 (handover share)')]
        for n, ms, w, basis, boq in KEYS:
            a = ACTS[f'{c}-{n}']; a.cost_ms = (ms, w); a.basis = f'{ms} {MS[ms][0]} {MS[ms][1]*100:.0f}% x station price share {f*100:.2f}% | {basis}'; a.boq = boq
        for ms in ('MS2', 'MS3', 'MS4', 'MS5', 'MS6', 'MS7'):
            tot = sum(w for n, m, w, _, _ in KEYS if m == ms); assert abs(tot - 1) < 1e-9, (sid, ms, tot)
        # progress (percent of the whole project)
        stn_pct = 96.0 * f
        E_stage = {'SRV': (8, 'E1010', 'E1020'), 'CNC': (10, 'E1030', 'E1040'), 'PRE': (18, 'E1050', 'E1060'), 'DET': (30, 'E1070', 'E1080'), 'IFC': (18, 'E1090', 'E1100'), 'HCS': (6, 'E1110', 'E1120'), 'ASB': (10, 'E1130', 'E1140')}
        for sc, (w, sub, apr) in E_stage.items():
            tot_w = 12.0 * w / 100.0
            ds, da = ACTS[f'{c}-{sub}'].dur, ACTS[f'{c}-{apr}'].dur
            ACTS[f'{c}-{sub}'].prog = stn_pct * tot_w / 100.0 * ds / (ds + da); ACTS[f'{c}-{apr}'].prog = stn_pct * tot_w / 100.0 * da / (ds + da)
        for n, share in pk.items(): ACTS[f'{c}-{n}'].prog = stn_pct * 24.0 / 100.0 * share
        for n, w in {'P1050': 4, 'P1060': 8, 'P1070': 4, 'C1010': 8, 'C1020': 6, 'C2010': 3, 'C2020': 6, 'C2030': 5, 'C2040': 3, 'C2050': 2, 'T1010': 3, 'T1020': 4, 'T2010': 2, 'T2020': 3, 'T3010': 3}.items():
            ACTS[f'{c}-{n}'].prog = stn_pct * w / 100.0
        # wave start link
        if s['ryd']:
            ACTS[f'{c}-E1010'].preds.append(('PRJ-M1100', 'FS', 0 if sid == 'NSR-RYD' else 10))
        else:
            ACTS[f'{c}-E1010'].preds.append(('PRJ-M2100', 'FS', ('WAVE', sid)))
    # detailed baseline after both Riyadh surveys; closeout after all acceptances
    ACTS['PRJ-A2010'].preds = [(f'{ST["NSR-RYD"]["code"]}-E1010', 'FS', 0), (f'{ST["EWR-RYD"]["code"]}-E1010', 'FS', 0)]
    ACTS['PRJ-C1010'].preds = [(a, 'FS', 0) for a in accepted]
    return surveys, accepted

# ------------------------------------------------------------------ CPM
def cpm(wave_lag):
    order = []; seen = set(); temp = set()
    pred_of = {k: [(p, t, (wave_lag[l[1]] if isinstance(l, tuple) else l)) for p, t, l in a.preds] for k, a in ACTS.items()}
    def visit(n):
        if n in seen: return
        assert n not in temp, f'cycle at {n}'
        temp.add(n)
        for p, _, _ in pred_of[n]: visit(p)
        temp.discard(n); seen.add(n); order.append(n)
    for n in ACTS: visit(n)
    ES = {}; EF = {}
    for n in order:
        a = ACTS[n]; dur = a.dur; es = 0 if not pred_of[n] else -10**9
        for p, t, lag in pred_of[n]:
            if t == 'FS': es = max(es, EF[p] + 1 + lag)
            elif t == 'SS': es = max(es, ES[p] + lag)
            elif t == 'FF': es = max(es, EF[p] + lag - dur + 1)
            elif t == 'SF': es = max(es, ES[p] + lag - dur + 1)
        if es < 0: es = 0
        ES[n] = es; EF[n] = es + dur - 1
    return order, pred_of, ES, EF

def backward(order, pred_of, ES, EF, end_idx):
    succ = defaultdict(list)
    for n in order:
        for p, t, lag in pred_of[n]: succ[p].append((n, t, lag))
    LS = {}; LF = {}
    for n in reversed(order):
        a = ACTS[n]; lf = 10**9
        for s_, t, lag in succ[n]:
            if t == 'FS': lf = min(lf, LS[s_] - 1 - lag)
            elif t == 'SS': lf = min(lf, LS[s_] - lag + a.dur - 1)
            elif t == 'FF': lf = min(lf, LF[s_] - lag)
            elif t == 'SF': lf = min(lf, LF[s_] - lag + a.dur - 1)
        if lf >= 10**9: lf = end_idx
        LF[n] = lf; LS[n] = lf - a.dur + 1
    return LS, LF, succ
