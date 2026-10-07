"""Core schedule model for the SAR Passengers' Security Checking programme.
Builds WBS, activities, logic, costs (contract payment milestones x BOQ station value) and progress weights,
then runs a calendar-aware CPM (Sun-Thu working week, KSA holidays) so every date is logic-driven.
"""
import json, math, datetime as dt
from collections import OrderedDict, defaultdict

PROJECT_NO = '0580'
PROJECT_NAME = '0580-Security Technology Salutation after eliminating Passenger Checking Roles'   # official name as supplied; confirm spelling
REVISION = 'Rev 1'
START = dt.date(2026, 11, 1)           # NTP milestone (editable in P6 by changing project planned start)
PO = 62_000_000
LINES = {'NSR': dict(name='North South Railway'), 'EWR': dict(name='East West Railway'), 'HHR': dict(name='Haramain High Speed Rail')}
SHARED = {'NSR': 487852 + 4387225 + 203241 + 394476 + 38716 + 483756,
          'EWR': 310926 + 2800750 + 203241 + 382873 + 67751 + 259632,
          'HHR': 1057094 + 9469993 + 203241 + 548785 + 67751 + 1375764}
SHARED_PARTS = {'NSR': dict(design=487852, pm=4387225, fat=203241, spares=394476, training=38716, cloud=483756),
                'EWR': dict(design=310926, pm=2800750, fat=203241, spares=382873, training=67751, cloud=259632),
                'HHR': dict(design=1057094, pm=9469993, fat=203241, spares=548785, training=67751, cloud=1375764)}
CODE = {'NSR-RYD': 'NRY', 'NSR-MAJ': 'NMJ', 'NSR-QAS': 'NQS', 'NSR-HAI': 'NHL', 'NSR-JOU': 'NJF', 'NSR-QUR': 'NQR',
        'EWR-RYD': 'ERY', 'EWR-DAM': 'EDM', 'EWR-HUF': 'EHF', 'EWR-ABQ': 'EAB',
        'HHR-JED': 'HJD', 'HHR-KAE': 'HKA', 'HHR-MAK': 'HMK', 'HHR-MAD': 'HMD'}

# ------------------------------------------------------------------ calendar
HOLIDAYS = [  # (start, end, label) inclusive; Sun-Thu working week handled separately. Eid dates are ESTIMATES.
    (dt.date(2027, 2, 22), dt.date(2027, 2, 22), 'Founding Day'),
    (dt.date(2027, 3, 7), dt.date(2027, 3, 11), 'Eid al-Fitr (estimated)'),
    (dt.date(2027, 5, 16), dt.date(2027, 5, 20), 'Eid al-Adha (estimated)'),
    (dt.date(2027, 9, 23), dt.date(2027, 9, 23), 'National Day'),
    (dt.date(2028, 2, 20), dt.date(2028, 2, 24), 'Eid al-Fitr (estimated)'),
    (dt.date(2028, 2, 22), dt.date(2028, 2, 22), 'Founding Day'),
    (dt.date(2028, 4, 30), dt.date(2028, 5, 4), 'Eid al-Adha (estimated)'),
    (dt.date(2028, 9, 23), dt.date(2028, 9, 23), 'National Day'),
    (dt.date(2029, 2, 11), dt.date(2029, 2, 15), 'Eid al-Fitr (estimated)'),
    (dt.date(2029, 2, 22), dt.date(2029, 2, 22), 'Founding Day'),
    (dt.date(2029, 4, 22), dt.date(2029, 4, 26), 'Eid al-Adha (estimated)'),
    (dt.date(2029, 9, 23), dt.date(2029, 9, 23), 'National Day'),
]
HOL = set()
for a, b, _ in HOLIDAYS:
    d = a
    while d <= b:
        HOL.add(d); d += dt.timedelta(days=1)

def is_work(d):
    return d.weekday() in (6, 0, 1, 2, 3) and d not in HOL     # Sun(6) Mon Tue Wed Thu

WORK = []
_d = START
while len(WORK) < 1600:
    if is_work(_d): WORK.append(_d)
    _d += dt.timedelta(days=1)
assert WORK[0] == START
TERM_END = dt.date(2029, 10, 31)       # 36 months from NTP
TERM_IDX = max(i for i, d in enumerate(WORK) if d <= TERM_END)

REVIEW_WD = 15          # SAR review of submissions: 21 calendar days = 3 working weeks (Sun-Thu) = 15 working days
DESIGN_TOTAL_WD = 79    # four months of design including the survey (working days), from design start to the last SAR approval
DESIGN_E = {}            # per-station design submittal chain (working days), calibrated so design spans four calendar months
def _add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12); return dt.date(d.year + y, m + 1, 1)
def _last_wd_before(d): return max(i for i, w in enumerate(WORK) if w < d)
def _first_wd_from(d): return min(i for i, w in enumerate(WORK) if w >= d)
M2_IDX = _last_wd_before(_add_months(START.replace(day=1), 2))     # end of month 2 (mobilization and site survey)
M6_IDX = _last_wd_before(_add_months(START.replace(day=1), 6))     # end of month 6 (design)
ENA_IDX = _first_wd_from(_add_months(START.replace(day=1), 4))     # start of month 5 = last two months of design

# ------------------------------------------------------------------ source data
SRC = json.load(open('/tmp/w/stations_sched.json'))
SEC = {}   # BOQ sections per station (Annex 3)
for s in SRC:
    SEC[s['id']] = dict(cctv=s['hw']['cctv'], vms=s['hw']['vms'], ac=s['hw']['ac'], ups=s['hw']['ups'], net=s['hw']['net'], civil=s['hw']['civil'])
LINE_HW = {l: sum(sum(SEC[s['id']].values()) for s in SRC if s['line'] == l) for l in LINES}
ST = OrderedDict()
PRIO = {'NSR-RYD': 1, 'HHR-MAK': 1, 'EWR-RYD': 2}   # 1 = Makkah and Riyadh (Thumamah), 2 = Riyadh (Malaz)
order = sorted(SRC, key=lambda s: ({1: 0, 2: 1}.get(PRIO.get(s['id'], 0), 2), s['start']))
for s in order:
    hw = sum(SEC[s['id']].values())
    share = hw / LINE_HW[s['line']]
    shared_alloc = {k: v * share for k, v in SHARED_PARTS[s['line']].items()}
    val = hw + sum(shared_alloc.values())
    civil_w = s['acts']['civil'][1] - s['acts']['civil'][0]
    inst_w = s['acts']['inst'][1] - s['acts']['inst'][0]
    inst_w = max(inst_w, 0)
    ST[s['id']] = dict(id=s['id'], name=s['name'], line=s['line'], ryd=s['ryd'], prio=PRIO.get(s['id'], 0), code=CODE[s['id']], cams=s['cams'], hw=SEC[s['id']],
                        hwtot=hw, shared=shared_alloc, val=val, start_w=s['start'], big=s['line'] == 'HHR',
                        civil_w=civil_w)
TOTAL = sum(s['val'] for s in ST.values())
assert abs(TOTAL - PO) < 5, TOTAL
for s in ST.values(): s['f'] = s['val'] / TOTAL
# fixed durations (working days) from the baseline assumptions
def stn_params(s):
    """Durations (working days) driven by the BOQ quantities of each station (Annex 3):
    cams = number of cameras, equipment SAR = CCTV + VMS + access control + UPS + network sections, civil SAR = civil section."""
    cams = s['cams']; h = s['hw']; eq = h['cctv'] + h['vms'] + h['ac'] + h['ups'] + h['net']; civ = h['civil']
    crews = 1 if cams < 150 else (2 if cams < 350 else 3)                 # installation crews scale with the camera count
    sv_ = max(8, round(5 + cams / 30))                                   # survey: 5 days set-up + 30 cameras per day walked and recorded
    E = DESIGN_TOTAL_WD - sv_ - REVIEW_WD                                # design is fixed at four months, survey included
    return dict(sv=sv_, E=E, appr=REVIEW_WD,
                proc=min(100, round(40 + eq / 100000)),                  # lead time: 40 days base + 1 day per SAR 100k of equipment
                ship=round(20 + eq / 250000),                            # shipping and customs: 20 days + 1 day per SAR 250k
                civil=round(20 + civ / 12000),                           # civil: 20 days + 1 day per SAR 12k of civil works (per crew)
                inst=round(15 + cams / (3 * crews)),                     # installation: 15 days + 3 cameras per crew-day
                sat=round(10 + cams / 30),                               # SAT: 10 days + 30 cameras per day
                train=10, trial=30, final=15)
for s in ST.values():
    s['p'] = stn_params(s)

# ------------------------------------------------------------------ payment milestones (contract clause 15)
MS = OrderedDict([
    ('MS1', ('Mobilization', 0.20)), ('MS2', ('Engineering submittal', 0.10)), ('MS3', ('SAR approval of engineering', 0.10)),
    ('MS4', ('Material delivery', 0.20)), ('MS5', ('Installation', 0.20)), ('MS6', ('Testing and commissioning (SAT)', 0.10)),
    ('MS7', ('Final acceptance and handover', 0.10))])

# progress weights (% of station progress), EPC phases: E 12, P 40, C 33, T&C/handover 15
PROG = OrderedDict()
PROG.update({'svS': 4, 'svA': 4, 'cnS': 4, 'cnA': 6, 'plS': 6, 'plA': 12 - 0, 'dtS': 0})  # placeholder replaced below

class Act:
    def __init__(s, code, name, wbs, dur, typ='TT_Task'):
        s.code, s.name, s.wbs, s.dur, s.typ = code, name, wbs, dur, typ
        s.preds = []       # (pred_code, type, lag)
        s.codes = {}
        s.cost_ms = None   # (milestone, weight)
        s.prog = 0.0       # progress weight, percent of whole project
        s.basis = ''
        s.boq = ''
        s.station = None

ACTS = OrderedDict()
WBS = OrderedDict()    # code -> dict(name, parent, level)

def wbs(code, name, parent=None):
    lvl = 1 if parent is None else WBS[parent]['level'] + 1
    WBS[code] = dict(code=code, name=name, parent=parent, level=lvl)
    return code

def act(code, name, wbs_code, dur, typ='TT_Task', preds=(), **codes):
    a = Act(code, name, wbs_code, dur, typ)
    a.preds = list(preds)
    a.codes = codes
    ACTS[code] = a
    return a

def hrs(n): return n * 8
