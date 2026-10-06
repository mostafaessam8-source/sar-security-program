from xer import *
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.chart import LineChart, Reference
import collections, os

OUT = '/home/user/sar-security-program/p6'
os.makedirs(OUT, exist_ok=True)

k, lag = solve()
txt, meta = build_xer(lag)
open(f'{OUT}/SAR_Security_Program_Baseline.xer', 'w', encoding='utf-8', newline='\n').write(txt)
ES, EF, LS, LF = meta['ES'], meta['EF'], meta['LS'], meta['LF']

BLUE = '00778B'; TINT = 'F2F8F9'; TINT2 = 'E6F1F4'; GRAY = 'C8C9C7'
HF = Font(name='Calibri', bold=True, color='FFFFFF', size=11); HFILL = PatternFill('solid', fgColor=BLUE)
BF = Font(name='Calibri', size=10); BOLD = Font(name='Calibri', size=10, bold=True)
thin = Side(style='thin', color=GRAY); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

def head(ws, row, titles, widths=None):
    for i, t in enumerate(titles, 1):
        c = ws.cell(row=row, column=i, value=t); c.font = HF; c.fill = HFILL; c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = BORDER
    if widths:
        for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w
    ws.row_dimensions[row].height = 32

def put(ws, row, vals, fmts=None, bold=False, fill=None):
    for i, v in enumerate(vals, 1):
        c = ws.cell(row=row, column=i, value=v); c.font = BOLD if bold else BF; c.border = BORDER
        if fmts and fmts.get(i): c.number_format = fmts[i]
        if fill: c.fill = PatternFill('solid', fgColor=fill)

EPCN = {'ENG': 'Engineering', 'PRO': 'Procurement', 'CON': 'Construction', 'COM': 'Commissioning and handover', 'PMG': 'Project management', 'MS': 'Milestone'}
def wcode(a): return a.wbs
wb = openpyxl.Workbook()

# ---------------------------------------------------------------- Station BOQ
ws = wb.active; ws.title = 'Station_BOQ'
ws['A1'] = 'Annex 3 price table: BOQ value by station (SAR, excluding VAT)'; ws['A1'].font = Font(name='Calibri', bold=True, size=14, color=BLUE)
ws['A2'] = 'A1-A6 are priced per station. Shared packages (design, PM, FAT, spares, training, cloud) are priced per railway and allocated to stations pro rata to A1-A6 hardware value.'; ws['A2'].font = BF
hd = ['Station', 'Railway', 'A1 CCTV', 'A2 Video mgmt and wall', 'A3 Access and intercom', 'A4 UPS', 'A5 Poles, cabinets, network', 'A6 Civil works', 'Hardware subtotal', 'Design and engineering', 'Project management', 'FAT', 'Commissioning spares', 'Training', 'Cloud (12 mo)', 'Shared total', 'Station value', 'Share of price']
head(ws, 4, hd, [24, 9] + [14] * 14 + [15, 11])
r0 = 5
for i, s in enumerate(ST.values()):
    r = r0 + i; h = s['hw']; sh = s['shared']
    put(ws, r, [f"{s['name']} ({s['code']})", s['line'], h['cctv'], h['vms'], h['ac'], h['ups'], h['net'], h['civil'], f'=SUM(C{r}:H{r})',
                sh['design'], sh['pm'], sh['fat'], sh['spares'], sh['training'], sh['cloud'], f'=SUM(J{r}:O{r})', f'=I{r}+P{r}', f'=Q{r}/Q${r0+14}'],
        {j: '#,##0' for j in range(3, 18)} | {18: '0.00%'})
rt = r0 + 14
put(ws, rt, ['Total', ''] + [f'=SUM({L(j)}{r0}:{L(j)}{rt-1})' for j in range(3, 18)] + [f'=SUM(R{r0}:R{rt-1})'], {j: '#,##0' for j in range(3, 18)} | {18: '0.00%'}, bold=True, fill=TINT2)
ws.cell(row=rt + 2, column=1, value='Contract price (Annex 3)').font = BOLD; ws.cell(row=rt + 2, column=3, value=PO).number_format = '#,##0'
ws.cell(row=rt + 3, column=1, value='Difference (should be zero within SAR 5)').font = BOLD; ws.cell(row=rt + 3, column=3, value=f'=Q{rt}-C{rt+2}').number_format = '#,##0.00'
ws.freeze_panes = 'C5'
STROW = {s['code']: r0 + i for i, s in enumerate(ST.values())}

# ---------------------------------------------------------------- Payment milestones
wp = wb.create_sheet('Payment_Milestones')
wp['A1'] = 'Contract clause 15 payment milestones applied to each station price'; wp['A1'].font = Font(name='Calibri', bold=True, size=14, color=BLUE)
wp['A2'] = 'MS1 Mobilization is 20% of the TOTAL price. MS2 to MS7 are prorated per station on the station share of the price.'; wp['A2'].font = BF
head(wp, 4, ['Milestone', 'Description', 'Share of price', 'Amount (SAR)'], [12, 36, 14, 18])
for i, (kk, (nm, pct_)) in enumerate(MS.items()):
    put(wp, 5 + i, [kk, nm, pct_, f'=C{5+i}*{PO}'], {3: '0%', 4: '#,##0'})
put(wp, 12, ['Total', '', '=SUM(C5:C11)', '=SUM(D5:D11)'], {3: '0%', 4: '#,##0'}, bold=True, fill=TINT2)
head(wp, 15, ['Station', 'Station share'] + [f'{kk} amount' for kk in list(MS)[1:]] + ['Stations total MS2-MS7'], [26, 14] + [16] * 7)
for i, s in enumerate(ST.values()):
    r = 16 + i
    put(wp, r, [f"{s['name']} ({s['code']})", f"=Station_BOQ!R{STROW[s['code']]}"] + [f'=$B{r}*{PO}*$C${5+j}' for j in range(1, 7)] + [f'=SUM(C{r}:H{r})'], {2: '0.00%'} | {j: '#,##0' for j in range(3, 10)})
put(wp, 30, ['Total', '=SUM(B16:B29)'] + [f'=SUM({L(j)}16:{L(j)}29)' for j in range(3, 10)], {2: '0.00%'} | {j: '#,##0' for j in range(3, 10)}, bold=True, fill=TINT2)
wp['A32'] = 'Check: MS1 + stations MS2-MS7 = total price'; wp['A32'].font = BOLD; wp['D32'] = '=D5+I30'; wp['D32'].number_format = '#,##0'

# ---------------------------------------------------------------- BOQ mapping (activities)
wm = wb.create_sheet('BOQ_Mapping')
wm['A1'] = 'Activity cost mapping: how each activity cost was distributed from the BOQ'; wm['A1'].font = Font(name='Calibri', bold=True, size=14, color=BLUE)
wm['A2'] = 'Cost = milestone amount (contract payment condition x station share of the BOQ) x distribution key. Column K recomputes it with formulas; column L is the whole-riyal value loaded in P6.'; wm['A2'].font = BF
cols = ['Activity ID', 'Activity name', 'WBS', 'EPC phase', 'Station', 'Payment milestone', 'Milestone %', 'Station price share', 'Milestone amount (SAR)', 'Distribution key', 'Cost recomputed', 'Cost in P6 (SAR)', 'Difference', 'Distribution basis', 'Primary BOQ source', 'Progress points', 'Progress % of project', 'Start', 'Finish', 'Duration (work days)']
head(wm, 4, cols, [13, 62, 22, 14, 10, 12, 10, 11, 15, 11, 15, 15, 10, 70, 58, 11, 11, 12, 12, 10])
r = 5
for code, a in ACTS.items():
    if a.typ != 'TT_Task': continue
    ms = a.cost_ms[0] if a.cost_ms else ''
    stc = a.codes.get('STN', 'PRJ')
    if ms == 'MS1':
        share = None; mamt = f"=Payment_Milestones!D5"; pctv = MS['MS1'][1]
    elif ms:
        share = f"=Station_BOQ!R{STROW[stc]}"; pctv = MS[ms][1]; mamt = f'=G{r}*{PO}*H{r}'
    else:
        share = None; mamt = 0; pctv = 0
    key = a.cost_ms[1] if a.cost_ms else 0
    rec = f'=ROUND(I{r}*J{r},0)' if ms else 0
    put(wm, r, [code, a.name, a.wbs, EPCN.get(a.codes.get('EPC'), ''), stc, ms, pctv, share, mamt, key, rec, a.cost, f'=L{r}-K{r}', a.basis or 'No payment milestone attached (administrative approval or review step)', a.boq or '-', a.pts, f'=P{r}/1000', WORK[ES[code]], WORK[EF[code]], a.dur],
        {7: '0%', 8: '0.00%', 9: '#,##0', 10: '0.0000', 11: '#,##0', 12: '#,##0', 13: '#,##0', 16: '#,##0', 17: '0.000', 18: 'dd-mmm-yy', 19: 'dd-mmm-yy'})
    r += 1
last_map = r - 1
put(wm, r, ['Total', '', '', '', '', '', '', '', '', '', f'=SUM(K5:K{last_map})', f'=SUM(L5:L{last_map})', f'=SUM(M5:M{last_map})', '', '', f'=SUM(P5:P{last_map})', f'=SUM(Q5:Q{last_map})', '', '', ''], {11: '#,##0', 12: '#,##0', 13: '#,##0', 16: '#,##0', 17: '0.000'}, bold=True, fill=TINT2)
wm.freeze_panes = 'C5'; wm.auto_filter.ref = f'A4:T{last_map}'

# ---------------------------------------------------------------- Distribution keys
wk = wb.create_sheet('Distribution_Keys')
wk['A1'] = 'Distribution keys (cost within each payment milestone, and progress weights)'; wk['A1'].font = Font(name='Calibri', bold=True, size=14, color=BLUE)
head(wk, 3, ['Milestone', 'Activity template', 'Key', 'Basis'], [12, 60, 12, 90])
tmpl = [('MS2', 'Survey, concept, preliminary, detailed, IFC, HCIS submittals', '5 / 10 / 20 / 40 / 20 / 5 %', 'Design effort split by stage; the railway design and engineering package sits inside the station price'),
        ('MS3', 'Approval activities of the same six stages', '5 / 10 / 20 / 40 / 20 / 5 %', 'Mirror of the submittal key (SAR review windows of 21 days)'),
        ('MS4', 'Manufacture CCTV, VMS, access control, UPS and network', '75% split by BOQ section share', 'A1, A2, A3 and A4+A5 shares of the station equipment value'),
        ('MS4', 'FAT / shipping and customs / delivery and receiving', '5 / 15 / 5 %', 'Fixed keys; spares and logistics sit inside delivery'),
        ('MS5', 'Civil trenches and duct banks / poles and foundations', '55 / 45 % of the A6 share', 'A6 civil works share of station hardware'),
        ('MS5', 'Install cabinets / cabling / CCTV / VMS / access control', '20 / 30 / 25 / 15 / 10 % of (1 - A6 share)', 'Installation is included in the unit prices (Annex 3 works included)'),
        ('MS6', 'Pre-commissioning / SAT', '40 / 60 %', 'Fixed keys'),
        ('MS7', 'As-built submittal / approval / training / trial operation / handover', '15 / 5 / 15 / 35 / 30 %', 'Fixed keys'),
        ('MS1', 'Performance security / initial baseline / site establishment / mobilization submittals', '15 / 10 / 45 / 30 %', 'Project level, 20% of the total price')]
for i, t in enumerate(tmpl): put(wk, 4 + i, list(t))
head(wk, 15, ['EPC phase', 'Component', 'Weight (% of station progress)', 'Basis'])
pw = [('Engineering', 'Survey 8, concept 10, preliminary 18, detailed 30, IFC 18, HCIS 6, as-built 10 (of 12%); each stage split submittal / approval by duration', 12, 'Typical EPC effort weighting for design'),
      ('Procurement', 'Manufacture 24 (split by BOQ package share), FAT 4, shipping 8, delivery 4', 40, 'Procurement carries the largest share of a supply-led security contract'),
      ('Construction', 'Trenches 8, poles 6, cabinets 3, cabling 6, CCTV 5, VMS 3, access 2', 33, 'Site works'),
      ('Commissioning and handover', 'Pre-commissioning 3, SAT 4, training 2, trial operation 3, handover 3', 15, 'Testing, trial and acceptance')]
for i, t in enumerate(pw): put(wk, 16 + i, list(t))
put(wk, 20, ['Total stations', '', '=SUM(C16:C19)', 'Station weights sum to 100%'], None, bold=True, fill=TINT2)
put(wk, 22, ['Project level', 'Mobilization and baseline 2.7% and closeout pack 1.3% of the whole project', 4, 'Stations carry 96% of the project, each station weighted by its BOQ price share'])

# ---------------------------------------------------------------- S-curve data
months = collections.OrderedDict()
def mkey(d): return (d.year, d.month)
cost_m = collections.Counter(); prog_m = collections.Counter(); inv_m = collections.Counter()
for code, a in ACTS.items():
    if a.typ != 'TT_Task' or a.dur == 0: continue
    for i in range(ES[code], EF[code] + 1):
        cost_m[mkey(WORK[i])] += a.cost / a.dur; prog_m[mkey(WORK[i])] += a.pts / a.dur
keys = sorted(set(cost_m) | set(prog_m))
cum_c = 0; cum_p = 0; sc_rows = []
for kk in keys:
    cum_c += cost_m[kk]; cum_p += prog_m[kk]
    sc_rows.append((dt.date(kk[0], kk[1], 1), cost_m[kk], cum_c, cum_c / PO, prog_m[kk] / 1000.0, cum_p / 1000.0))
wsc = wb.create_sheet('S_Curve')
wsc['A1'] = 'S-curve: cost (contract payment conditions) against progress (fair EPC distribution), spread linearly over each activity'; wsc['A1'].font = Font(name='Calibri', bold=True, size=14, color=BLUE)
head(wsc, 3, ['Month', 'Cost in month (SAR)', 'Cumulative cost (SAR)', 'Cumulative cost %', 'Progress in month %', 'Cumulative progress %'], [12, 18, 18, 14, 16, 16])
for i, rw in enumerate(sc_rows):
    r = 4 + i
    put(wsc, r, [rw[0], rw[1], f'=SUM(B$4:B{r})', f'=C{r}/{PO}', rw[4] / 100.0, f'=SUM(E$4:E{r})'], {1: 'mmm-yy', 2: '#,##0', 3: '#,##0', 4: '0.0%', 5: '0.00%', 6: '0.0%'})
n = len(sc_rows)
ch = LineChart(); ch.title = 'Cumulative cost % and progress %'; ch.height = 9; ch.width = 22
ch.add_data(Reference(wsc, min_col=4, min_row=3, max_row=3 + n), titles_from_data=True); ch.add_data(Reference(wsc, min_col=6, min_row=3, max_row=3 + n), titles_from_data=True)
ch.set_categories(Reference(wsc, min_col=1, min_row=4, max_row=3 + n)); ch.y_axis.number_format = '0%'; ch.y_axis.scaling.max = 1.0
wsc.add_chart(ch, 'H4')

# ---------------------------------------------------------------- Resources
wr = wb.create_sheet('Resources')
head(wr, 1, ['Resource ID', 'Name', 'Type', 'Unit', 'Price per unit', 'Meaning', 'How P6 uses it'], [12, 44, 12, 8, 12, 70, 80])
put(wr, 2, ['COST-SAR', 'Contract cost (BOQ x payment milestones)', 'Material', 'SAR', 0, 'Contract cost of the activity in SAR from the payment conditions applied to the BOQ station value (column L of BOQ_Mapping)', 'Quantity carrier. Price 0, so it adds no budget cost. Set the price to 1 (and PROG-WT to 0) to see the contract-condition cost curve instead.'])
put(wr, 3, ['PROG-WT', 'Progress weight (fair EPC distribution, SAR value)', 'Material', 'SAR', 1, 'Progress share x SAR 62,000,000 (100,000 points x SAR 620). Fair EPC distribution (see Distribution_Keys)', 'Price 1, so budgeted cost = progress value in SAR. Activity % complete type is Physical, so earned value = physical % x this budget, and the cost and schedule performance indexes are measured in SAR on the progress distribution.'])

# ---------------------------------------------------------------- Codes, WBS, relationships
wc = wb.create_sheet('Activity_Codes')
head(wc, 1, ['Code type', 'Code value', 'Description', 'Activities'], [18, 14, 44, 12])
cnt = collections.Counter();
for a in ACTS.values():
    for kk2, vv in a.codes.items(): cnt[(kk2, vv)] += 1
CTN = {'EPC': 'EPC phase', 'AREA': 'Area', 'STN': 'Station', 'RAIL': 'Railway', 'DISC': 'Discipline', 'RESP': 'Responsibility', 'MST': 'Payment milestone', 'STAGE': 'Design stage', 'SUBAPP': 'Submittal or approval', 'PRIO': 'Priority'}
rr_ = 2
for (kk2, vv), c in sorted(cnt.items()):
    put(wc, rr_, [CTN[kk2], vv, '', c]); rr_ += 1
ww = wb.create_sheet('WBS')
head(ww, 1, ['WBS code', 'Name', 'Level', 'Parent'], [30, 70, 8, 30])
for i, (code, w) in enumerate(WBS.items()): put(ww, 2 + i, [code, w['name'], w['level'], w['parent'] or ''])
wl = wb.create_sheet('Relationships')
head(wl, 1, ['Predecessor', 'Successor', 'Type', 'Lag (work days)'], [14, 14, 8, 14])
rr_ = 2
for n_ in meta['order']:
    for p, t, lg in meta['pred_of'][n_]: put(wl, rr_, [p, n_, t, lg]); rr_ += 1

# ---------------------------------------------------------------- Summary first sheet
wsu = wb.create_sheet('Summary', 0)
wsu['A1'] = 'SAR Passengers Security Checking: baseline schedule, cost loading and BOQ mapping'; wsu['A1'].font = Font(name='Calibri', bold=True, size=15, color=BLUE)
lines = [('Source of cost', 'Draft contract with ETECHS (22 Jan 2024): Annex 3 price table (Revised-02) and clause 15 payment milestones'),
         ('Contract price', PO), ('Project start (NTP milestone)', START), ('Contract term end (36 months)', TERM_END),
         ('Activities', len([1 for a in ACTS.values()])), ('Tasks (2 resources each)', len([1 for a in ACTS.values() if a.typ == "TT_Task"])), ('Milestones', len([1 for a in ACTS.values() if a.typ != "TT_Task"])),
         ('Cost loaded in P6 (SAR)', f'=BOQ_Mapping!L{last_map+1}'), ('Difference to contract price', f'=B9-B3'), ('Progress points loaded', f'=BOQ_Mapping!P{last_map+1}'),
         ('Working calendar', 'Sunday to Thursday, 8 hours; KSA official holidays; Eid dates are estimates to be updated'), ('How to read', 'Station_BOQ gives the BOQ value of each station; Payment_Milestones applies the contract payment conditions; BOQ_Mapping shows each activity cost; Distribution_Keys explains the keys; S_Curve shows cost against progress.')]
for i, (a_, b_) in enumerate(lines):
    wsu.cell(row=3 + i, column=1, value=a_).font = BOLD; c = wsu.cell(row=3 + i, column=2, value=b_); c.font = BF
    if isinstance(b_, (int,)) and a_ == 'Contract price': c.number_format = '#,##0'
    if isinstance(b_, dt.date): c.number_format = 'dd-mmm-yyyy'
wsu['B10'].number_format = '#,##0'; wsu['B11'].number_format = '#,##0'; wsu['B12'].number_format = '#,##0'
wsu.column_dimensions['A'].width = 34; wsu.column_dimensions['B'].width = 120
for w_ in wb.worksheets:
    w_.sheet_view.showGridLines = False
wb.save(f'{OUT}/SAR_BOQ_Cost_Mapping.xlsx')
print('xlsx saved; mapping rows', last_map - 4, 'S-curve months', n)
