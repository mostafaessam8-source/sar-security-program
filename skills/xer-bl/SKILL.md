---
name: xer-bl
description: Build a baseline (BL) schedule submittal for Primavera P6 24 as an XER file plus BOQ cost mapping workbook, programme narrative (Word) and import read-me. Use when asked to deliver a schedule as XER, a baseline programme for approval, a P6 import file, or "XER BL". Arabic triggers: "جدول زمني XER", "بيزلاين بريمافيرا", "BL submittal".
---

# XER BL: baseline schedule submittal for P6 24

Deliver four files together: `<Project>_Baseline.xer`, `<Project>_BOQ_Cost_Mapping.xlsx`, `<Project>_Schedule_Narrative.docx`, `README_P6_Import.md`. Reference implementation (SAR security programme) is in `scripts/` (model_base, model, run_model, xer, validate, out_xlsx, out_docx). Reuse the structure, replace the data.

## Principles (fixed by the user, keep for every project)
1. **Single source**: use only the contract file the user names as final. Never mix other projects' files.
2. **Roles**: act as planning engineer. Everything must be defensible for submission and approval.
3. **WBS = EPC**: Project > Railway/Package > Station/Area > EPC phase (Engineering, Procurement, Construction, Commissioning and handover) > stage/package > area. Go to level 8 only if the contract gives data for it; otherwise stop and say so.
4. **Engineering by recognised design stages** (survey, concept, preliminary, detailed, IFC, authority/HCIS-type submission, as-built); inside each stage per area: **Submittal** and **Approval** activities.
5. **No tiny activities**: minimum 1 working day (8 h). Milestones are zero duration.
6. **Logic**: FS mainly, SS/FF only with reason, lags in working time. No date constraints. Priority areas first (waves). Only the NTP has no predecessor and only the completion milestone has no successor; add predecessors to approval/MS milestones so nothing is open-ended.
7. **Start milestone**: NTP/start as a Start Milestone at the agreed date (default 1 Nov of the planning year), no constraint, so changing the project Planned Start moves everything. Contract completion is a finish milestone driven by logic (FS from NTP with lag = contract term), not a date.
8. **Calendar**: one calendar, Sun-Thu, 8 h, official KSA holidays as exceptions. Eid dates are estimates: always flag them for confirmation. The contract's working-day definition decides how non-working dates roll.
9. **Two resources on every task** (none on milestones), both **Material type, quantity in SAR** so the price switch works:
   - `COST-SAR`: activity cost from the contract payment conditions (price list x payment-milestone %, distributed by keys).
   - `PROG-WT`: progress value = fair EPC progress distribution x contract price (100,000 points x price/100,000 per point).
   - Delivered default: PROG-WT price 1, COST-SAR price 0. User switches view by setting one to 1 and the other 0. **Never both 1** (total doubles). Both sum to the contract price exactly (allocate rounding residual to the largest activities).
10. **% complete type = Physical for all activities** and as project default (`CP_Phys`).
11. **Activity codes**: global/project codes, all activities carry every code type: EPC phase, Area, Station, Railway/Package, Discipline, Responsibility, Payment milestone, Design stage, Submittal or approval, Priority.
12. **BOQ mapping workbook** (formula-based, totals reconcile to the contract price): Station_BOQ, Payment_Milestones, BOQ_Mapping (per activity: milestone, %, station share, key, recomputed cost vs loaded cost, basis text), Distribution_Keys, S_Curve (cost and progress), **Invoicing_Monthly** (mandatory, see below), Resources, Activity_Codes, WBS, Relationships.
    - **Invoicing_Monthly (detailed invoiced per month)**: (a) one row per invoice event = each payment milestone x station, with invoice month, milestone date from the programme, milestone, description, station, line, trigger activity ID and name, amount (formula linked to Payment_Milestones), cumulative SAR and %; total row and a check cell = 0 against the contract price. (b) monthly matrix over the whole contract term: columns per payment milestone, invoiced in month, cumulative SAR, cumulative %, with a cumulative-% chart. (c) monthly matrix by station (project-level mobilization as its own column). Use SUMIFS over the detail table so everything recalculates. Invoice month = month the trigger milestone activity is achieved; state that payment terms after invoicing are not modelled unless the contract gives them.
    - After writing the workbook recalculate it (LibreOffice Calc headless, install libreoffice-calc if missing) and confirm no `#` errors and all check cells = 0.
13. **Narrative (Word)**: basis and sources, key dates, calendar and holidays, WBS, engineering stages, logic and priority waves, station finish dates, longest/near-critical path (float is measured against the term-driven completion, say so), resources and cost loading, S-curve, activity codes, how to change the start date, assumptions and exclusions, risks, submission checklist.
14. **README**: import steps (File > Import > XER, new project, schedule with Retained Logic), structure, how to change start, cost/progress price switch, warning that existing resources keep old prices on re-import (delete old project and resources first), Eid estimates, what was not tested.

## XER technical rules (learned in P6 24 import tests)
- Header: `ERMHDR 24.12 <date> Project admin <user> <db> Project Management <currency>`; tables CURRTYPE, UMEASURE, OBS, CALENDAR, PROJECT, PROJWBS, RSRC, RSRCRATE, ACTVTYPE, ACTVCODE, TASK, TASKPRED, TASKRSRC, TASKACTV, end `%E`.
- **PROJECT must carry the full field set** (acct_id, guid, export_flag=Y, plan_start/plan_end/scd_end, loaded_scope_level, etc.). A thin PROJECT table made P6's Import Project Options grid empty.
- Durations in hours (8 per day). Task types TT_Task / TT_Mile / TT_FinMile; DT_FixedDrtn; lags in hours; PR_FS / PR_SS / PR_FF.
- Calendar data in P6 nested-paren format; holiday exceptions as Excel serial days.
- Activity IDs max 20 chars, unique. Unique primary keys, valid foreign keys.
- P6 shows Nonlabor/time-based units in days in the UI (hours/8). That is display only.
- Resources already in the database are reused on import with their old rates: say so every time.

## Workflow
1. Read the contract; extract price table, payment milestones, term, review periods, working-day definition, scope per area.
2. Build the model (WBS, activities, logic, cost keys, progress weights) and run the own CPM; calibrate wave offsets so the last area finishes within the term (search a stretch factor).
3. Write XER, then run `validate.py`: errors empty, 2 resources per task, no milestone resources, open ends only the completion milestone, every activity has all codes, independent forward pass `mism = 0`, cost total = progress total = contract price.
4. Produce xlsx, docx, README. Copy to the repo `p6/` folder, commit, push to main.
5. Report honestly: validated structurally and by an independent CPM; if not opened in P6 here, say so; list assumptions (durations are planning assumptions, Eid estimates, exclusions like DLP).
