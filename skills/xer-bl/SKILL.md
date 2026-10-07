---
name: xer-bl
description: Build a baseline (BL) schedule submittal for Primavera P6 24 as an XER file plus BOQ cost mapping workbook, programme narrative (Word) and import read-me. Use when asked to deliver a schedule as XER, a baseline programme for approval, a P6 import file, or "XER BL". Arabic triggers: "جدول زمني XER", "بيزلاين بريمافيرا", "BL submittal".
---

# XER BL: baseline schedule submittal for P6 24

Deliver five files together: `<No>_Schedule_Baseline_Rev<n>.xer`, `<No>_BOQ_Cost_Mapping.xlsx`, `<No>_Schedule_Narrative.docx`, `<No>_README_P6_Import.md` and the interactive offline presentation `<No>_Interactive_Presentation_Rev<n>.html`. Project number and the official project name (verbatim as supplied, flag doubtful spelling) go on every output: file names, XER project ID and root WBS, workbook summary, narrative cover and header, presentation, site header. Reference implementation (SAR security programme) is in `scripts/` (model_base, model, run_model, xer, validate, out_xlsx, out_docx). Reuse the structure, replace the data.

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
12. **BOQ mapping workbook** (formula-based, totals reconcile to the contract price): Station_BOQ, Payment_Milestones, BOQ_Mapping (**first two columns are BOQ ID and BOQ Description** for every activity: contract price-table section codes such as A1 to A6; shared packages get derived IDs SH-xx; multi-section shares like A1-A5; '-' with an explanation for activities without BOQ cost; then per activity: milestone, %, station share, key, recomputed cost vs loaded cost, basis text), Distribution_Keys, S_Curve (cost and progress), **Invoicing_Monthly** (mandatory, see below), Resources, Activity_Codes, WBS, Relationships.
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

## Reusing the scripts (`scripts/`)
- `model_base.py` data, calendar, holidays, price table, payment milestones. Replace the contract data (stations, BOQ sections, shared packages, MS %, term, NTP date). It reads a station schedule JSON (path is hard-coded: change it).
- `model.py` builds WBS, activities, logic, cost keys and progress weights. `run_model.py` solves the wave stretch factor and integer-allocates cost and progress (progress amount in SAR = points x price/100,000). `xer.py` writes the XER. `validate.py` re-reads the XER and checks it independently. `out_xlsx.py` writes the workbook (BOQ_Mapping with BOQ ID and Description first, Invoicing_Monthly, S_Curve...). `out_docx.py` writes the narrative.
- Run order: `python3 out_xlsx.py` (also writes the XER), `python3 out_docx.py`, `python3 validate.py <xer>`. Output folder is hard-coded to `/home/user/<repo>/p6`: change it.
- Validator expectations: errs empty, activities = tasks + milestones, open_start only NTP, open_end only completion milestone, mism 0, cost total = progress total = contract price.

## Delivery
- Commit the four files to the project repo (`p6/`) with the Co-Authored-By and Claude-Session trailers, push to the branch the user named, then send all four files to the user (SendUserFile).
- The final message states plainly: what was validated, that it was not opened in P6 if so, assumptions (durations, Eid), what is excluded.

## Lessons from the SAR baseline (keep)
- Only the contract the user declares final is a source; never reuse another project's numbers.
- Both resource prices 1 doubles the total; the first import into a database fixes resource prices and types, so tell the user to delete old resources before re-importing.
- The workbook Summary check cell must reference the right cells (cost loaded minus contract price); recalc the workbook to catch `#VALUE!`.
- Keep the price table section codes (A1 to A6) as BOQ IDs; label derived IDs as derived.
- Invoices follow payment milestones, not cost spread: Invoicing_Monthly is separate from the S_Curve sheet and the two will differ.

## Change log
- v1 baseline method: two resources, EPC WBS, design stages with submittal/approval, logic-driven completion, NTP milestone.
- v2: Physical % complete; both resources Material in SAR with price switch; full PROJECT table for import.
- v4 (Rev 1): six-month plan with overlap, priority tiers, POC, 21-day reviews, station-level WBS, PHASE code, project number/name on all outputs, interactive offline presentation.
- v3: Invoicing_Monthly detailed sheet; BOQ ID and BOQ Description as the first two columns of BOQ_Mapping.

## Rev 1 additions (project 0580)
- **Survey permit (user rule)**: the site survey needs an access permit that takes two months (activity E1005, 45 working days, phase MOB, SAR); the survey belongs to DESIGN (phase DES), so the 4 months of design include the survey and start when the permit ends. Design total = survey + design chain + last review = 79 working days (`DESIGN_TOTAL_WD`). The POC starts at design start and must finish before design complete.
- **Design rule for EVERY station (user restated)**: two months mobilization and survey, design lasts four months and starts two months after the station mobilization starts (priority stations: after milestone PRJ-M1150; others: survey start + 43 working days), enabling works start two months before design ends (overlap of two months, SS design start + 40 to 42 working days); manufacture still waits for MS3. Recalibrate the wave stretch factor after any such change.
- **First-six-months structure**: months 1-2 mobilization and site survey, months 3-6 design for the priority stations, enabling works starting at the start of month 5 (overlap of the last two design months). Drive it with logic, not dates: project milestones (mobilization and survey complete, design complete) linked from NTP with working-day lags computed from the calendar (`M2_IDX`, `M6_IDX`, `ENA_IDX` in `model_base.py`); tune the priority design submittal chain (`DESIGN_E_P1`) so design ends with month 6.
- **WBS**: level 1 project, level 2 EPC phase, level 3 station, level 4 stage/package, level 5 submittal-approval/area. Priority and railway are activity codes, not WBS levels.
- **Priority tiers** (`PRIO` in model_base): tier 1 starts surveys at once, carries the four-month design and runs enabling/civil works in parallel with design (equipment still released only after SAR approval, MS3); tier 2 shorter design; others in waves. Wave search skips priority stations.
- **POC pattern** (Riyadh Thumamah): plan submittal, 21-day approval, network test bed, CCTV and inspection/access-control demonstration, integrated test, report, consultant inspection, approval (one month in total), POC-approved milestone as predecessor of MS3. No Annex 3 POC item: carve 15% of the station MS2/MS3 buckets and 10% of the station engineering progress weight, and say so.
- **Review period**: every SAR review is 21 days = 15 working days in a Sun-Thu calendar (`REVIEW_WD`); survey approval and taking-over included.
- **Enabling works** (X1010, X1020) carved from the civil share of MS5; priority stations start them in month 5, others after MS3.
- **Activity code `PHASE`** (programme phase) is derived in `xer.py` (`phase_of`) and used by the presentation Gantt colours.
- **Presentation look rule**: the interactive presentation must keep the look of the SAR PowerPoint the user supplies (fixed 16:9 canvas 1280x720, logo top-left, breadcrumb and page number top-right, parallelogram title, KPI cards, bottom rule with circle, track-stripe cover and teal Thank You slide, same slide order and layouts); new slides use the same grammar. Every card, KPI, row, bar, table row and chart element opens a detail drawer. Port coordinates from the pptxgenjs build (inches x 96 = px). Render the user's pptx to PNG first (soffice to pdf, pdftoppm) and compare.
- **Schedule in ONE page**: the user does not want the schedule scattered over several slides. Put the whole programme on a single dynamic page (all activities, all WBS levels, 36 months) with: WBS tree you expand level by level (L1 to L5, activities), group by WBS or by package and station, quick views (first six months, priority, POC, SAR reviews, milestones, longest path), professional filters (railway, priority, stations, EPC phase, programme phase, responsible, type, float, months range and zoom, search), date or cost columns, progress curves per station and payments views on the same filters, CSV export. Other slides only summarise and link into this page.
- **Management audience rule**: for high management keep the deck short (about 7 slides: cover, scope, plan highlights, one schedule page, cash flow, dashboard, closing), a few words per card, no internal 'to confirm' lists on slides (put assumptions in a neutral 'Key assumptions' drawer), detail only behind clicks (price tables, contract terms, activity lists). Default schedule view = Level 2 package bars in the SAR look, ordered by start date; filters and level controls sit behind a 'Filters and levels' toggle.
- **Summary detail by default**: when a package or station is expanded, show a few grouped rows (Site survey, Concept, Preliminary, Detailed, IFC, HCIS, POC, As-built; Manufacture, FAT/shipping/delivery; Enabling works, Civil, Installation; SAT, Training and trial, Handover; one Milestones row of diamonds) instead of every activity; the raw activity list is one click away (group row drawer, or Detail: All activities).
- **Interactive offline presentation**: `export_pres.py` writes `pres_data.json` from the same model (activities, per-station monthly cost and time progress, invoices); `build_pres.py` inlines data, Chart.js and logos into `pres_template.html`. Slides: cover, scope x3, first six months, priorities and POC, review periods, Level 2, Level 3 by station (activities and milestones, monthly progress with CSV, payment milestones), cash flow, dashboard with month slider, closing. Test with headless Chromium (no console errors, click through stations, tabs, drawers, dashboard filters).
- **Site button**: a Presentation button next to Publish downloads the presentation from a base64 payload embedded in both the hosted page and the offline copy.
- The presentation, XER, workbook and narrative must come from the same model run; never leave an older revision in another deliverable without saying so.
