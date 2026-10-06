# SAR Passengers' Security Checking Systems: P6 baseline package

## Files
| File | Content |
|---|---|
| SAR_Security_Program_Baseline.xer | Primavera P6 24 schedule: 558 activities (470 tasks, 88 milestones), 855 relationships, 515 WBS nodes (6 levels), 10 activity code types, 2 resources |
| SAR_BOQ_Cost_Mapping.xlsx | Cost mapping from the BOQ to each activity, payment milestones, distribution keys, S-curve, resources, codes, WBS, relationships |
| SAR_Schedule_Narrative.docx | Programme narrative for submission |

## Import into P6 24
1. File > Import > choose Primavera PM (XER). Select the file.
2. Import as a new project. Choose the EPS node. Map the currencies, resources and calendar (create new).
3. Open the project. Check: Activities, WBS (EPC), Activity Codes, Resources.
4. Schedule (F9): Retained Logic, Make open-ended activities critical off. Do not set the data date earlier than the start.

## Structure
- WBS: Project > Railway > Station > EPC phase (Engineering, Procurement, Construction, Commissioning and handover) > design stage / package > area.
- Activity codes: EPC phase, Area, Station, Railway, Discipline, Responsibility, Payment milestone, Design stage, Submittal or approval, Priority.
- Resources (each task has both; milestones have none):
  - PROG-WT (Material, price 1): progress value in SAR = progress share x 62,000,000. It carries the budget, so earned value, CPI and SPI are in SAR on the fair EPC progress distribution.
  - COST-SAR (Material, price 0): contract-condition cost quantity in SAR (total 62,000,000). To see the payment-condition cost curve instead, set COST-SAR price to 1 and PROG-WT to 0.
  - Activity % complete type is Physical for every activity, so enter physical % per activity.
- Calendar: Sunday to Thursday, 8 h/day, with KSA holidays.

## Change the project start (1 Nov 2026)
NTP (PRJ-M0000) is a start milestone with no constraint. Change Project > Details > Dates > Planned Start, then F9. Everything, including contract completion (linked by a 36 month lag), moves. Holidays are fixed dates, so review the calendar afterwards.

## Check before you submit
- Eid dates in the calendar are ESTIMATES. Update them to the announced dates.
- Durations, logic and station order are planning assumptions, not contract text.
- Not tested inside P6: the XER passed structural checks (keys, references, resources, codes, calendar) and an independent forward pass that matched every date, but it was never opened in P6. Import it into a test project first and compare the finish (31 Oct 2029) and total cost (62,000,000).
- Not included: defects liability period and post-acceptance support.

## Cost or progress view (price switch)
Both resources carry the same kind of quantity (SAR) on every activity, so the price decides what the budget shows:
- Progress view: PROG-WT Standard Rate 1, COST-SAR 0 (as delivered).
- Cost view: COST-SAR Standard Rate 1, PROG-WT 0.
Change it in Resources > Units & Prices, then F9. Never set both to 1 (the project total doubles to 124,000,000).
If you re-import into a database that already has COST-SAR / PROG-WT, P6 keeps the old rates and types: delete the old project and the two resources first, or set the rates by hand.
