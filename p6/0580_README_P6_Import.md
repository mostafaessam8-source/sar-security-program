# 0580-Security Technology Salutation after eliminating Passenger Checking Roles: P6 baseline package (Rev 1)

## Files
| File | Content |
|---|---|
| 0580_Schedule_Baseline_Rev1.xer | Primavera P6 24 schedule: 598 activities (507 tasks, 91 milestones), 913 relationships, 519 WBS nodes (5 levels), 11 activity code types, 2 resources |
| 0580_BOQ_Cost_Mapping.xlsx | Cost mapping from the BOQ to each activity, payment milestones, invoices per month, distribution keys, S-curve, resources, codes, WBS, relationships |
| 0580_Schedule_Narrative.docx | Programme narrative for submission |
| ../presentation/0580_Interactive_Presentation_Rev1.html | Interactive offline presentation and dashboard (open in any browser) |

## What changed in Rev 1
- Survey permit and design rule, every station: the site survey needs an access permit that takes two months (activity E1005, 45 working days, months 1-2 at the priority stations; WBS Project management and mobilization > Mobilization > one node per station, EPC code Project management). The survey is the first part of design, so design (survey, concept, preliminary, detailed, IFC, HCIS) starts when the permit is granted and lasts four months in total (79 working days to the last SAR approval). Enabling works start two months before the end of design (two months of overlap). At the priority stations: permit 1 Nov to 31 Dec 2026, design 3 Jan to 29 Apr 2027, enabling works from 1 Mar 2027 (milestones PRJ-M1150 and PRJ-M1250). Other stations apply the same rule from their own start; permit processing takes 2% of the MS2 bucket (no Annex 3 item).
- Priority 1: Makkah and Riyadh (Thumamah). Priority 2: Riyadh (Malaz). Priority 1 works run in parallel with design.
- POC at Riyadh (Thumamah): CCTV, inspection and access control, network; one month (22 working days) for consultant inspection and approval. POC approval is a predecessor of MS3 at that station.
- Every SAR review is 21 days = 15 working days (survey approval was 5 days), except the POC inspection and approval and the mock-up approval, which are one month (22 working days).
- Mock-up approval (NRY-T1030, milestone NRY-T1130): after the installation at Riyadh (Thumamah), SAR visits the site and approves the executed works so the solution can be rolled out to the other stations. It precedes the SAT milestone (MS6) and handover at that station only; it does not hold back the installation of other stations. Cost is carved from 3% of that station's MS6 bucket (no Annex 3 item).
- WBS: level 1 project, level 2 EPC phase, level 3 station, level 4 design stage or work package, level 5 submittal/approval or area.
- New activity code type Programme phase (mobilization and survey, design, POC, enabling works, procurement, construction, commissioning).
- Project number 0580 and the official name on every output.

## Import into P6 24
1. File > Import > Primavera PM (XER). Select the file. Import as a new project (project ID 0580), choose the EPS node.
2. If COST-SAR / PROG-WT already exist in the database from Rev 0, P6 keeps their old prices and types. Delete the old project and the two resources first, or set the prices by hand (see below).
3. Schedule (F9): Retained Logic, open-ended activities not critical.

## Resources (each task has both; milestones have none)
- PROG-WT (Material, price 1): progress value in SAR = progress share x 62,000,000. It carries the budget, so earned value, CPI and SPI are in SAR on the fair EPC progress distribution.
- COST-SAR (Material, price 0): contract-condition cost quantity in SAR (total 62,000,000).
- Cost view: set COST-SAR to 1 and PROG-WT to 0 (Resources > Units & Prices), then F9. Never set both to 1 (the project total doubles).
- Activity % complete type is Physical for every activity.

## Change the project start (1 Nov 2026)
NTP (PRJ-M0000) is a start milestone with no constraint. Change Project > Details > Dates > Planned Start, then F9. Everything, including the month 2 and month 6 milestones and contract completion (36 month lag), moves. Holidays are fixed dates, so review the calendar afterwards.

## Check before you submit
- The project name is used exactly as supplied ("Salutation"); please confirm the spelling.
- Eid dates in the calendar are ESTIMATES.
- Durations, logic, station order and the priority tiers are planning assumptions, not contract text. The 21 day review is read as 15 working days.
- POC cost has no Annex 3 item and is carved from 15% of the Riyadh (Thumamah) design milestones (MS2 and MS3).
- Not tested inside P6 by the author: the XER passed structural checks (keys, references, resources, codes, calendar) and an independent forward pass that matched every date. Import it into a test project first and compare the finish (31 Oct 2029) and total cost (62,000,000).
- The website tabs Schedule and S-curve still show the Rev 0 plan; the presentation and this package are Rev 1.
- Not included: defects liability period and post-acceptance support.
