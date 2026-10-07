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
fin=sorted([(s['name'],max(EF[c] for c,a in ACTS.items() if a.codes.get('STN')==s['code']),s['prio']>0) for s in ST.values()],key=lambda x:x[1])
plt.figure(figsize=(7.5,4)); plt.barh([f[0] for f in fin],[(f[1]+1)/21.7 for f in fin],color=['#00778B' if f[2] else '#8DB9C2' for f in fin]); plt.xlabel('Station finish, months from NTP (approx.)'); plt.tight_layout(); plt.savefig('fin.png',dpi=160); plt.close()


def rng(codes):
    return min(ES[c] for c in codes), max(EF[c] for c in codes)
def M(i): return WORK[i]
def mon(i): return (WORK[i]-START).days/30.4375
# six-month Gantt for priority stations
def gantt6():
    rows=[('Mobilization (site, personnel, tools)',['PRJ-A1040'],'#8DB9C2'),
          ('Site access permits for surveys (all stations)',['PRJ-A1060'],'#00778B'),
          ('Survey and design - Riyadh (Thumamah)',['NRY-E1010','NRY-E1100'],'#3D3935'),('Survey and design - Makkah',['HMK-E1010','HMK-E1100'],'#3D3935'),
          ('Enabling works - Riyadh (Thumamah)',['NRY-X1010','NRY-X1020'],'#C8C9C7'),('Enabling works - Makkah',['HMK-X1010','HMK-X1020'],'#C8C9C7')]
    fig,ax=plt.subplots(figsize=(8.6,3.8))
    for i,(n,cs,col) in enumerate(rows):
        a,b=rng(cs); ax.barh(len(rows)-1-i,mon(b+1)-mon(a),left=mon(a),color=col,height=.55)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1],fontsize=8)
    ax.axvspan(0,2,color='#00778B',alpha=.07); ax.axvspan(2,6,color='#3D3935',alpha=.05); ax.axvspan(4,6,color='#C8C9C7',alpha=.35)
    ax.set_xlim(0,8); ax.set_xticks(range(0,9)); ax.set_xlabel('Months from NTP'); ax.grid(axis='x',alpha=.3)
    ax.text(1,len(rows)-.35,'Mobilization and survey permit',ha='center',fontsize=8); ax.text(4,len(rows)-.35,'Design (4 months)',ha='center',fontsize=8); ax.text(5,len(rows)-.75,'overlap: enabling works',ha='center',fontsize=7)
    ax.set_ylim(-.6,len(rows)+.1); plt.tight_layout(); plt.savefig('gantt6.png',dpi=160); plt.close()
gantt6()

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
        t.autofit=False
        for i,w in enumerate(widths): t.columns[i].width=Cm(w)
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    doc.add_paragraph()
def P(t,b=False): r=doc.add_paragraph().add_run(t); r.bold=b
def B(t): doc.add_paragraph(t,style='List Bullet')
sec=doc.sections[0]; hp=sec.header.paragraphs[0]; hp.text=PROJECT_NAME+' | '+REVISION; hp.runs[0].font.size=Pt(8)

tp=doc.add_paragraph(); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=tp.add_run("\n\n\nSaudi Arabia Railways (SAR)\n"+PROJECT_NAME+"\nContract with ETECHS"); r.bold=True; r.font.size=Pt(20); r.font.color.rgb=RGBColor(0,0x77,0x8B)
tp=doc.add_paragraph(); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER; tp.add_run('\nBaseline Programme Narrative\nFor SAR review and approval').font.size=Pt(15)
tp=doc.add_paragraph(); tp.alignment=WD_ALIGN_PARAGRAPH.CENTER
tp.add_run(f'\n\nProject {PROJECT_NO}  |  {REVISION}  |  Data date and NTP: {START.strftime("%d %B %Y")}  |  P6 file: 0580_Schedule_Baseline_Rev1.xer').font.size=Pt(10)
doc.add_page_break()

doc.add_heading('1. Purpose and basis of the programme',1)
P(f"This narrative describes the baseline programme ({REVISION}) of project {PROJECT_NAME}, covering 14 stations on three railways (North South Railway, East West Railway and Haramain High Speed Rail). It is delivered as a Primavera P6 24 XER file with {len(ACTS)} activities ({len(tasks)} tasks and {len(mil)} milestones) and {sum(len(v) for v in meta['pred_of'].values())} logic links. It runs from the Notice to Proceed milestone on {D(0)} to the contract completion milestone on {D(max(EF.values()))}.")
P('Source: the contract file only (conditions, Annex 2 scope of work, Annex 3 price table, Annex 4 clarifications, Annex 5 compliance table), plus the planning instructions of the Contractor in this revision. Durations, logic and station sequence are Contractor planning assumptions offered for SAR approval. They are not contract-stated, except the 36 month term, the payment milestones and the 21 day review period.')
doc.add_heading('2. Changes in this revision',1)
table([('First six months','Months 1-2 mobilization and the survey access permit (the permit takes two months); months 3-6 design (four months) which starts with the site survey. Milestones: mobilization and permits complete, design complete.'),
       ('Design rule','At every station: two months of mobilization and survey, then four months of design starting two months after the station mobilization starts; enabling works start in the last two months of design (two months of overlap). At the priority stations this is months 1-2, 3-6 and 5-6 of the project.'),
       ('Priority','Makkah and Riyadh (Thumamah) are Priority 1 and run works in parallel with design. Riyadh (Malaz) is Priority 2.'),
       ('Review period','Every SAR review of a submission is 21 days (15 working days). Survey approval was 5 days and is now 21 days.'),
       ('WBS','Stations are now level 3 of the WBS (project, EPC phase, station). Priority and railway are activity codes.'),
       ('Identity','Project number 0580 and the official name on every output. Programme phase added as an activity code.')],['Item','Change'],[3.5,12.5])
doc.add_heading('3. Key dates and milestones',1)
table([(c,ACTS[c].name,D(ES[c] if ACTS[c].typ=='TT_Mile' else EF[c])) for c in mil if c.startswith('PRJ')],['ID','Milestone','Date'],[3,10,3.5])
P('Contract completion is driven by logic: it is linked from NTP with a lag equal to the 36 month term and carries no date constraint. If the NTP date changes, every date moves with it.')
doc.add_heading('4. The first six months',1)
doc.add_picture('gantt6.png',width=Cm(16))
a1,b1=rng(['PRJ-A1010','PRJ-A1020','PRJ-A1030','PRJ-A1040','PRJ-A1050','PRJ-A1060'])
a2,b2=rng(['NRY-E1010','NRY-E1100','HMK-E1010','HMK-E1100']); a3,b3=rng(['NRY-X1010','NRY-X1020','HMK-X1010','HMK-X1020'])
table([('Mobilization and survey permit (months 1-2)',D(a1),D(b1),'Mobilization, initial baseline, and the two month site access permit for the surveys, applied for once for the whole project'),
       ('Design including survey (months 3-6)',D(a2),D(b2),'Site survey, concept, preliminary, detailed and IFC design with HCIS documents; each stage submitted and approved in 21 days'),
       ('Enabling works start (month 5)',D(a3),D(b3),'Site preparation, setting out, temporary works, cable routes, duct banks and plinths, in parallel with the last two months of design'),
       ],['Phase','Start','Finish','Content'],[4.5,2.6,2.6,6.3])
P('The survey needs a site access permit and the permit takes two months, so months 1 and 2 are mobilization and the permit (one project-level activity, PRJ-A1060, in the Mobilization branch of the WBS; there is no permit activity per station). The survey is the first part of design, so the survey and design start when the permit is granted and lasts four months in total, survey included. At the priority stations the two month window is held by milestone PRJ-M1150; the other stations start design in their wave, with the permit already in hand. Enabling works start two months before the end of design, so design and execution overlap by two months. No date constraint is used.')
doc.add_heading('5. Priority stations',1)
P('Priority 1: Makkah (Haramain) and Riyadh (Thumamah, North South Railway). Their permits are applied for first and their enabling and civil works run in parallel with design. Equipment is manufactured only after SAR approval of the engineering (milestone MS3), so no equipment is ordered before approval. Priority 2: Riyadh (Malaz, East West Railway), permitted in the same two months. The remaining stations follow in waves after the detailed baseline is approved, each with the same four month design.')
pr=[(s['name'],s['line'],{1:'Priority 1',2:'Priority 2',0:'Standard'}[s['prio']],D(ES[s['code']+'-E1010']),D(max(EF[c] for c,a in ACTS.items() if a.codes.get('STN')==s['code']))) for s in ST.values()]
table(pr,['Station','Railway','Priority','Design start','Station finish'],[5,2,2.5,3.2,3.2])
doc.add_heading('7. Review and approval periods',1)
P('All SAR reviews and approvals of submissions are 21 days. In a Sunday to Thursday calendar that is three working weeks, so each approval activity is 15 working days. This applies to the initial and detailed baseline programme, the survey, every design stage, HCIS documents, POC plan, as-built documents and the taking-over application. The POC inspection and approval, and the mock-up approval at Riyadh (Thumamah), are separate one month periods (22 working days) as instructed.')
ap=[c for c in tasks if ACTS[c].codes.get('SUBAPP')=='Approval']
P(f'{len(ap)} approval activities are loaded. Their durations: '+', '.join(f'{k} days x {v}' for k,v in sorted(collections.Counter(ACTS[c].dur for c in ap).items()))+' (working days).')
doc.add_heading('8. Calendar',1)
P('Single project calendar: Sunday to Thursday, 8 hours per day (08:00 to 12:00 and 13:00 to 17:00); Friday and Saturday are non-working. The contract defines a working day as a bank-open day, and dates falling on a non-working day move to the next working day. National holidays are calendar exceptions: Founding Day (22 Feb), National Day (23 Sep), Eid al-Fitr and Eid al-Adha.')
P('The Eid dates are estimates from the Islamic calendar. Confirm them against the official announcement before the baseline is submitted.',True)
table([(a.strftime('%d %b %Y'),b.strftime('%d %b %Y'),l) for a,b,l in HOLIDAYS],['From','To','Holiday'],[4,4,8])
doc.add_heading('9. Work breakdown structure',1)
cnt=collections.Counter(w['level'] for w in WBS.values())
P(f'The WBS follows EPC. Level 1 is the project ({PROJECT_NO}), level 2 the EPC phase (Engineering, Procurement, Construction, Commissioning and handover, plus Project management), level 3 the station, level 4 the design stage or work package (enabling works, civil, installation, POC), and level 5 the submittal, approval or area. There are {len(WBS)} nodes. The survey access permits sit under Project management and mobilization, in the Mobilization branch (one node per station). Levels 6 to 8 are not used because the contract gives no zone-level data; they can be added when it does.')
table(sorted(cnt.items()),['WBS level','Nodes'],[4,4])
doc.add_heading('10. Engineering stages',1)
P('Engineering is divided by recognised design stage: site survey (after the two month access permit), concept design, preliminary design, detailed design, issued for construction, HCIS submission and as-built. Within each stage there is a submittal and a 21 day SAR approval. Procurement is released after the engineering approval milestone (MS3).')
doc.add_heading('11. Logic and sequencing',1)
P('Relationships are mainly finish to start, with a few start to start and finish to finish links. There are no date constraints. Priority stations start first; the other stations follow in waves calibrated so the last station completes inside the 36 month term. The only activity without a predecessor is NTP, and the only activity without a successor is contract completion.')
doc.add_heading('12. Station finish dates',1)
doc.add_picture('fin.png',width=Cm(15.5))
doc.add_heading('13. Longest path and near-critical activities',1)
mn=min(fl[c] for c in tasks); crit=[c for c in tasks if fl[c]==mn]; near=[c for c in tasks if mn<fl[c]<=mn+20]
P(f'The contract completion milestone is held by the 36 month term, so no activity has zero float against it. The longest physical path finishes {mn} working days before the contract end date, and that margin is the project float. {len(crit)} tasks sit on this longest path and {len(near)} more are within 20 working days of it. The first 25 in date order are listed below.')
table([(c,ACTS[c].name,D(ES[c]),D(EF[c]),fl[c]) for c in sorted(near+crit,key=lambda c:ES[c])[:25]],['ID','Activity','Start','Finish','Float (working days)'],[3,7.5,2.8,2.8,2])
doc.add_heading('14. Resources and cost loading',1)
P('Every task carries two resources. Milestones carry none.')
table([('COST-SAR','Material','Contract cost quantity in SAR. Price 0. Total 62,000,000 SAR.'),('PROG-WT','Material','Progress value in SAR (progress share x 62,000,000). Price 1, so it carries the budget cost. All activities use Physical % complete.')],['Resource','Type','Use'],[3,3,10])
P('Because PROG-WT has price 1 and COST-SAR has price 0, the P6 budget, earned value, CPI and SPI are all in SAR on the fair EPC progress distribution. To view the contract payment-condition cost instead, swap the two prices (COST-SAR 1, PROG-WT 0). Never set both to 1.')
P("Cost comes from the contract: the Annex 3 station price multiplied by the clause 15 payment milestone, spread to activities by distribution keys. Mobilization (MS1, 20% of the total price) sits at project level. The activity-by-activity mapping and the invoices per month are in 0580_BOQ_Cost_Mapping.xlsx. Progress is a fair EPC distribution (Engineering 12, Procurement 40, Construction 33, Commissioning and handover 15 per station), weighted by each station's price share, plus 4% for project-level activities.")
table([(m,v[0],f'{v[1]*100:.0f}%') for m,v in MS.items()],['Milestone','Description','Share of price'],[3,9,3])
doc.add_heading('15. S-curve',1)
doc.add_picture('scurve.png',width=Cm(15.5))
P('Cost follows the contract payment milestones. Progress is smoother because it is distributed by effort. The two curves differ on purpose: cost is a payment profile, progress is physical.')
doc.add_heading('16. Activity codes',1)
P('Eleven global activity code types are loaded and every activity carries all of them: EPC phase, Area, Station, Railway, Discipline, Responsibility, Payment milestone, Design stage, Submittal or approval, Priority and Programme phase. The values are listed on the Activity_Codes sheet of the BOQ workbook.')
doc.add_heading('17. Changing the start date',1)
P('NTP is a start milestone with no constraint. To move the project, change the project Planned Start (Project > Details > Dates), then schedule with F9 using Retained Logic. All dates, including contract completion, move together. The holidays are fixed dates, so after a change review the calendar for the holidays that the new window crosses.')
doc.add_heading('18. Assumptions and exclusions',1)
for t in ['Durations and station order are Contractor planning assumptions.','Eid dates are estimates.','The 21 day SAR review is read as 21 calendar days, which is 15 working days in the Sunday to Thursday calendar. A longer review is an extension of time matter under the contract.','Priority 1 means Makkah and Riyadh (Thumamah). Riyadh (Malaz) is treated as Priority 2.','Mock-up approval: after the installation at Riyadh (Thumamah) is complete, SAR visits the site and approves the executed works (one month, 22 working days) so that the solution can be rolled out to the other stations. It is a predecessor of the SAT milestone (MS6) and the handover at that station only; it does not gate the installation of the other stations. Cost has no Annex 3 item and is carved from 3% of the testing milestone.','POC cost is carved from the design package of Riyadh (Thumamah) because Annex 3 has no POC item. The POC inspection system is mapped to access control and intercom (section A3).','Enabling and civil works start two months before the end of design at every station, before the engineering approval milestone, at the Contractor risk; equipment is not ordered before approval.','Site access, permits and railway possessions are assumed available. No possession restrictions are modelled.','The defects liability period and post-acceptance support are not in the programme.','Cost is a payment profile at BOQ value, excluding VAT.','The official project name is used as supplied. Please confirm its spelling before issue.','The file was checked structurally and with an independent forward pass; see the read-me for what was and was not tested in P6.']: B(t)
doc.add_heading('19. Risks to the programme',1)
table([('Eid dates differ from the estimate','Confirm before submission and reschedule'),('Long-lead equipment at Haramain stations (largest value)','Early procurement approval and FAT planning'),('SAR approval time above 21 days','Early submission and an approval log'),('POC not approved within one month','Early plan approval; consultant booked in advance'),('Enabling works before engineering approval','Limit to non-design-dependent work; confirm layouts at concept approval'),('Station access and railway possession','Coordinate during mobilization'),('Conflict between Annex 4 item 33 (fast-track) and Annex 5 on HCIS','Clarify with SAR before design submittals')],['Risk','Mitigation'],[8,8])
doc.add_heading('20. Submission checklist',1)
for t in ['Confirm the project name spelling and the Eid dates.','Open the XER in P6 24, schedule it, and compare dates with this narrative.','Confirm the priority order with SAR.','Check the cost mapping against the Annex 3 price table.','Submit the XER, narrative, BOQ mapping and read-me together.']: B(t)
doc.save(f'{OUT}/0580_Schedule_Narrative.docx'); print('ok',len(crit),len(near),D(max(EF.values())))
