from xer import *
import collections, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
OUT='/home/user/sar-security-program/p6'
k, lag = solve(); txt, meta = build_xer(lag)
ES,EF,LS=meta['ES'],meta['EF'],meta['LS']
fl={c:LS[c]-ES[c] for c in ACTS}
D=lambda i: WORK[i].strftime('%d %b %Y')
tasks=[c for c,a in ACTS.items() if a.typ=='TT_Task']; mil=[c for c,a in ACTS.items() if a.typ!='TT_Task']
cm=collections.Counter(); pm=collections.Counter()
for c in tasks:
    a=ACTS[c]
    for i in range(ES[c],EF[c]+1): cm[(WORK[i].year,WORK[i].month)]+=a.cost/a.dur; pm[(WORK[i].year,WORK[i].month)]+=a.pts/a.dur
ks=sorted(cm); cc=cp=0; X=[];YC=[];YP=[]
for i,kk in enumerate(ks): cc+=cm[kk]; cp+=pm[kk]; X.append(i+1); YC.append(cc/PO*100); YP.append(cp/1000)
plt.figure(figsize=(7.5,3.6)); plt.plot(X,YC,color='#00778B',lw=2,label='Cumulative cost %'); plt.plot(X,YP,color='#E2A400',lw=2,ls='--',label='Cumulative progress %')
plt.xlabel('Month from NTP'); plt.ylabel('%'); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig('scurve.png',dpi=160); plt.close()
fin=sorted([(s['name'],max(EF[c] for c,a in ACTS.items() if a.codes.get('STN')==s['code']),s['ryd']) for s in ST.values()],key=lambda x:x[1])
plt.figure(figsize=(7.5,4)); plt.barh([f[0] for f in fin],[(f[1]+1)/21.7 for f in fin],color=['#00778B' if f[2] else '#8DB9C2' for f in fin]); plt.xlabel('Station finish, months from NTP (approx.)'); plt.tight_layout(); plt.savefig('fin.png',dpi=160); plt.close()

doc=Document(); doc.styles['Normal'].font.name='Calibri'; doc.styles['Normal'].font.size=Pt(10.5)
for s in doc.sections: s.left_margin=s.right_margin=Cm(2.2)
for n in ('Heading 1','Heading 2'): doc.styles[n].font.color.rgb=RGBColor(0,0x77,0x8B); doc.styles[n].font.name='Calibri'
def shade(cell,color):
    sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),color); cell._tc.get_or_add_tcPr().append(sh)
def table(rows,hdr,widths=None):
    t=doc.add_table(rows=1,cols=len(hdr)); t.style='Table Grid'
    for i,h in enumerate(hdr):
        c=t.rows[0].cells[i]; c.text=''; r=c.paragraphs[0].add_run(h); r.bold=True; r.font.size=Pt(9.5); r.font.color.rgb=RGBColor(255,255,255); shade(c,'00778B')
    for row in rows:
        cs=t.add_row().cells
        for i,v in enumerate(row): cs[i].text=''; cs[i].paragraphs[0].add_run(str(v)).font.size=Pt(9.5)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    doc.add_paragraph()
def P(t,b=False): r=doc.add_paragraph().add_run(t); r.bold=b
def B(t): doc.add_paragraph(t,style='List Bullet')

tp=doc.add_paragraph(); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=tp.add_run("\n\n\nSaudi Arabia Railways (SAR)\nPassengers' Security Checking Systems\nContract with ETECHS"); r.bold=True; r.font.size=Pt(20); r.font.color.rgb=RGBColor(0,0x77,0x8B)
tp=doc.add_paragraph(); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER; tp.add_run('\nBaseline Programme Narrative\nFor SAR review and approval').font.size=Pt(15)
tp=doc.add_paragraph(); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER
tp.add_run(f'\n\nRevision 0 (initial baseline)  |  Data date and NTP: {START.strftime("%d %B %Y")}  |  P6 file: SAR_Security_Program_Baseline.xer').font.size=Pt(10)
doc.add_page_break()

doc.add_heading('1. Purpose and basis of the programme',1)
P(f"This narrative describes the initial baseline programme for the Passengers' Security Checking Systems at 14 stations on three railways (North South Railway, East West Railway and Haramain High Speed Rail). It is delivered as a Primavera P6 24 XER file with {len(ACTS)} activities ({len(tasks)} tasks and {len(mil)} milestones) and 855 logic links. It runs from the Notice to Proceed milestone on {D(0)} to the contract completion milestone on {D(max(EF.values()))}.")
P('Source: the contract file only (conditions, Annex 2 scope of work, Annex 3 price table, Annex 4 clarifications, Annex 5 compliance table). Durations, logic and station sequence are Contractor planning assumptions offered for SAR approval. They are not contract-stated, except the 36 month term, the payment milestones and the review period.')
doc.add_heading('2. Key dates and milestones',1)
table([(c,ACTS[c].name,D(ES[c] if ACTS[c].typ=='TT_Mile' else EF[c]),fl[c]) for c in mil if c.startswith('PRJ')],['ID','Milestone','Date','Float (working days)'],[3,8,3.5,3])
P('Contract completion is driven by logic: it is linked from NTP with a lag equal to the 36 month term and carries no date constraint. If the NTP date changes, every date moves with it.')
doc.add_heading('3. Calendar',1)
P('Single project calendar: Sunday to Thursday, 8 hours per day (08:00 to 12:00 and 13:00 to 17:00); Friday and Saturday are non-working. The contract defines a working day as a bank-open day, and dates falling on a non-working day move to the next working day. National holidays are calendar exceptions: Founding Day (22 Feb), National Day (23 Sep), Eid al-Fitr and Eid al-Adha.')
P('The Eid dates are estimates from the Islamic calendar. Confirm them against the official announcement before the baseline is submitted.',True)
table([(a.strftime('%d %b %Y'),b.strftime('%d %b %Y'),l) for a,b,l in HOLIDAYS],['From','To','Holiday'],[4,4,8])
doc.add_heading('4. Work breakdown structure',1)
cnt=collections.Counter(w['level'] for w in WBS.values())
P(f'The WBS follows EPC: Engineering, Procurement, Construction, and Commissioning and handover, with Project management and milestones at project level. It has {len(WBS)} nodes over {max(cnt)} levels: project, railway, station, EPC phase, design stage or work package, and area. Levels 7 and 8 were not needed because the contract gives no zone-level data; they can be added when zone data is available.')
table(sorted(cnt.items()),['WBS level','Nodes'],[4,4])
doc.add_heading('5. Engineering stages',1)
P('Engineering is divided by recognised design stage: site survey, concept design, preliminary design, detailed design, issued for construction, HCIS submission and as-built. Within each stage every area has a submittal and a SAR approval activity. Approval durations reflect the SAR review period. Procurement does not start before approval of the related design.')
doc.add_heading('6. Logic and sequencing',1)
P('Relationships are mainly finish to start, with a few start to start and finish to finish links. There are no date constraints. Riyadh stations have priority: they start first and have shorter procurement lead times. The other stations follow in waves, and the wave offsets were calibrated so that the last station completes inside the 36 month term. The only activity without a predecessor is NTP, and the only activity without a successor is contract completion.')
doc.add_heading('7. Station finish dates',1)
doc.add_picture('fin.png',width=Cm(15.5))
table([(n,D(e),'Yes' if r_ else '') for n,e,r_ in fin],['Station','Station finish','Riyadh priority'],[8,4,3])
doc.add_heading('8. Critical and near-critical activities',1)
mn=min(fl[c] for c in tasks); crit=[c for c in tasks if fl[c]==mn]; near=[c for c in tasks if mn<fl[c]<=mn+20]
P(f'The contract completion milestone is held by the 36 month term, so no activity has zero float against it. The longest physical path finishes {mn} working days before the contract end date, and that margin is the project float. {len(crit)} tasks sit on this longest path ({mn} working days of float) and {len(near)} more are within 20 working days of it. The first 25 in date order are listed below.')
table([(c,ACTS[c].name,D(ES[c]),D(EF[c]),fl[c]) for c in sorted(near+crit,key=lambda c:ES[c])[:25]],['ID','Activity','Start','Finish','Float (working days)'],[3,7.5,2.8,2.8,2])
doc.add_heading('9. Resources and cost loading',1)
P('Every task carries two resources. Milestones carry none.')
table([('COST-SAR','Material','Contract cost quantity in SAR. Price 0. Total 62,000,000 SAR.'),('PROG-WT','Material','Progress value in SAR (progress share x 62,000,000). Price 1, so it carries the budget cost. All activities use Physical % complete.')],['Resource','Type','Use'],[3,3,10])
P('Because PROG-WT has price 1 and COST-SAR has price 0, the P6 budget, earned value, CPI and SPI are all in SAR on the fair EPC progress distribution. To view the contract payment-condition cost instead, swap the two prices (COST-SAR 1, PROG-WT 0).')
P("Cost comes from the contract: the Annex 3 station price multiplied by the clause 15 payment milestone, spread to activities by distribution keys. Mobilization (MS1, 20% of the total price) sits at project level. The activity-by-activity mapping is in SAR_BOQ_Cost_Mapping.xlsx. Progress is a fair EPC distribution (Engineering 12, Procurement 40, Construction 33, Commissioning and handover 15 per station), weighted by each station's price share, plus 4% for project-level activities.")
table([(m,v[0],f'{v[1]*100:.0f}%') for m,v in MS.items()],['Milestone','Description','Share of price'],[3,9,3])
doc.add_heading('10. S-curve',1)
doc.add_picture('scurve.png',width=Cm(15.5))
P('Cost follows the contract payment milestones. Progress is smoother because it is distributed by effort. The two curves differ on purpose: cost is a payment profile, progress is physical.')
doc.add_heading('11. Activity codes',1)
P('Ten global activity code types are loaded and every activity carries all of them: EPC phase, Area, Station, Railway, Discipline, Responsibility, Payment milestone, Design stage, Submittal or approval, and Priority. The values are listed on the Activity_Codes sheet of the BOQ workbook.')
doc.add_heading('12. Changing the start date',1)
P('NTP is a start milestone with no constraint. To move the project, change the project Planned Start (Project > Details > Dates), then schedule with F9 using Retained Logic. All dates, including contract completion, move together. The holidays are fixed dates, so after a change review the calendar for the holidays that the new window crosses.')
doc.add_heading('13. Assumptions and exclusions',1)
for t in ['Durations and station order are Contractor planning assumptions.','Eid dates are estimates.','The SAR review period is taken as 21 days; longer approval is an extension of time matter under the contract.','Site access, permits and railway possessions are assumed available. No possession restrictions are modelled.','The defects liability period and post-acceptance support are not in the programme.','Cost is a payment profile at BOQ value, excluding VAT.','The file was checked structurally and with an independent forward pass. The author has not opened it in P6 (see the read-me).']: B(t)
doc.add_heading('14. Risks to the programme',1)
table([('Eid dates differ from the estimate','Confirm before submission and reschedule'),('Long-lead equipment at Haramain stations (largest value)','Early procurement approval and FAT planning'),('SAR approval time above the review period','Early submission and an approval log'),('Station access and railway possession','Coordinate during mobilization'),('Conflict between Annex 4 item 33 (fast-track) and Annex 5 on HCIS','Clarify with SAR before design submittals')],['Risk','Mitigation'],[8,8])
doc.add_heading('15. Submission checklist',1)
for t in ['Confirm the Eid dates and update the calendar.','Open the XER in P6 24, schedule it, and compare dates with this narrative.','Confirm the station order with SAR.','Check the cost mapping against the Annex 3 price table.','Submit the XER, narrative, BOQ mapping and read-me together.']: B(t)
doc.save(f'{OUT}/SAR_Schedule_Narrative.docx'); print('ok',len(crit),len(near),D(max(EF.values())))
