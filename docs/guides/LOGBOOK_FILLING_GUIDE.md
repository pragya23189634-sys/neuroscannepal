# Mahara Logbook — Filling Guide (Phase 4)

Use this guide to copy your 32-week project record into BCU Mahara. Source material is in:

- `NeuroScan_Nepal_Weekly_Journal_32_Weeks_Updated.docx` (if generated)
- `scripts/generate_weekly_journal_doc.py` (regenerate journal)

Run:
```powershell
py -3.11 scripts/generate_weekly_journal_doc.py
py -3.11 scripts/generate_logbook_doc.py
```

---

## How to fill each Mahara weekly entry

For **each week (1–32)**, create one Mahara journal entry with:

| Mahara field | What to write |
|--------------|---------------|
| **Title** | `Week X — [Topic]` (see table below) |
| **Date** | Actual week date range |
| **Activity** | Copy "Activity" paragraph from weekly journal doc |
| **Issues / challenges** | Copy "Issues" paragraph |
| **Actions / next steps** | Copy bullet list from "Actions" |
| **Hours** | Estimate honestly (typically 8–15 hrs/week) |
| **Evidence** | Attach screenshot, code commit, or report snippet |

---

## Week-by-week titles (quick reference)

| Week | Title |
|------|-------|
| 1 | Project setup & topic confirmation |
| 2 | Literature review & requirements |
| 3 | System architecture design |
| 4 | Project proposal submission |
| 5 | Ethics & dataset planning |
| 6 | Dataset receipt & exploration |
| 7 | Preprocessing pipeline |
| 8 | Preprocessing tests & QC |
| 9 | CNN model design |
| 10 | Model training phase 1 |
| 11 | Inference module |
| 12 | Grad-CAM explainability |
| 13 | RAG advisory module |
| 14 | Chatbot & hospital finder |
| 15 | Pipeline integration |
| 16 | Batch testing & logging |
| 17 | FastAPI backend setup |
| 18 | Upload & job management |
| 19 | Backend hardening |
| 20 | React frontend setup |
| 21 | Upload & processing pages |
| 22 | Results & model info pages |
| 23 | Frontend polish |
| 24 | Integration testing |
| 25 | Bug fixes & confidence display |
| 26 | Model retraining & tuning |
| 27 | Authentication & RBAC design |
| 28 | RBAC implementation |
| 29 | Doctor review & patient portal |
| 30 | Performance testing |
| 31 | Dissertation writing |
| 32 | Final submission prep |

---

## Evidence to attach (by phase)

| Phase | Weeks | Attach |
|-------|-------|--------|
| Research | 1–4 | Proposal PDF, literature table |
| Data & ML | 5–11 | Preprocessing report, training curves, `cnn_baseline_report.txt` |
| Pipeline | 12–16 | Grad-CAM sample, pipeline log screenshot |
| Backend | 17–19 | API health screenshot, `backend.py` snippet |
| Frontend | 20–23 | Dashboard screenshots |
| Integration | 24–26 | `test_25_results.json`, integration test output |
| RBAC | 27–29 | Login screenshots (3 roles), doctor review screenshot |
| Submission | 30–32 | Dissertation draft, viva script, manual checklist |

---

## Supervisor comments

Leave the **Supervisor Comments** field blank in Mahara — your supervisor fills this during review meetings.

---

## Checklist before Mahara submission

- [ ] All 32 weekly entries created
- [ ] Each entry has date, hours, activity, and reflection
- [ ] At least one piece of evidence attached per month
- [ ] Weeks 26–29 mention RBAC and 97.81% accuracy
- [ ] Week 32 mentions final dissertation and viva prep
- [ ] Supervisor has reviewed and commented on key entries

---

*This guide completes Phase 4 logbook documentation. You must manually enter entries into Mahara — they cannot be auto-uploaded.*
