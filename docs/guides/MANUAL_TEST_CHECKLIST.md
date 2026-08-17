# NeuroScan Nepal — Manual Test Checklist

Use this checklist during dissertation manual testing (Chapter 6) and before viva rehearsal. Mark each item **Pass / Fail / N/A** and add notes.

**Tester:** ______________________  
**Date:** ______________________  
**Environment:** Windows / Chrome / `START_NEUROSCAN.bat`

---

## A. Authentication (6 tests)

| # | Test | Pass | Fail | Notes |
|---|------|:----:|:----:|-------|
| A1 | Login as radiologist (`radiologist@neuroscan.np`) redirects to dashboard | ☐ | ☐ | |
| A2 | Login as doctor redirects to doctor review | ☐ | ☐ | |
| A3 | Login as patient redirects to my records | ☐ | ☐ | |
| A4 | Invalid password shows error message | ☐ | ☐ | |
| A5 | Logout clears session and returns to login | ☐ | ☐ | |
| A6 | Unauthenticated access to `/upload` redirects to login | ☐ | ☐ | |

---

## B. Radiologist Workflow (8 tests)

| # | Test | Pass | Fail | Notes |
|---|------|:----:|:----:|-------|
| B1 | Home dashboard shows job statistics | ☐ | ☐ | |
| B2 | Upload page lists patients in dropdown | ☐ | ☐ | |
| B3 | Upload MRI creates job and redirects to processing | ☐ | ☐ | |
| B4 | All 8 pipeline stages show completion | ☐ | ☐ | |
| B5 | Results page shows label (normal/abnormal) | ☐ | ☐ | |
| B6 | Results page shows confidence > 0% | ☐ | ☐ | |
| B7 | Grad-CAM heatmap image displays | ☐ | ☐ | |
| B8 | Radiologist notes save successfully | ☐ | ☐ | |

---

## C. Doctor Workflow (4 tests)

| # | Test | Pass | Fail | Notes |
|---|------|:----:|:----:|-------|
| C1 | Doctor review lists completed scans | ☐ | ☐ | |
| C2 | AI result and radiologist notes visible | ☐ | ☐ | |
| C3 | Clinical recommendation submits successfully | ☐ | ☐ | |
| C4 | Doctor cannot access upload page | ☐ | ☐ | |

---

## D. Patient Workflow (3 tests)

| # | Test | Pass | Fail | Notes |
|---|------|:----:|:----:|-------|
| D1 | Patient unique ID displayed (NSN-PAT-XXXXXX) | ☐ | ☐ | |
| D2 | My records shows only patient's own scans | ☐ | ☐ | |
| D3 | Doctor recommendation visible on report | ☐ | ☐ | |

---

## E. RBAC Enforcement (5 tests)

| # | Test | Pass | Fail | Notes |
|---|------|:----:|:----:|-------|
| E1 | Doctor cannot upload (403 or UI blocked) | ☐ | ☐ | |
| E2 | Patient cannot access doctor review | ☐ | ☐ | |
| E3 | Patient cannot view other patients' jobs | ☐ | ☐ | |
| E4 | Radiologist cannot submit doctor review | ☐ | ☐ | |
| E5 | `/health` returns status ok without login | ☐ | ☐ | |

---

## F. UI and Display (4 tests)

| # | Test | Pass | Fail | Notes |
|---|------|:----:|:----:|-------|
| F1 | Model Info page shows 97.81% accuracy | ☐ | ☐ | |
| F2 | About page shows ethics disclaimer | ☐ | ☐ | |
| F3 | Backend offline banner appears when backend stopped | ☐ | ☐ | |
| F4 | Report files exist in `results/jobs/{id}/` | ☐ | ☐ | |

---

## Summary

| Section | Total | Passed | Failed |
|---------|-------|--------|--------|
| A Authentication | 6 | | |
| B Radiologist | 8 | | |
| C Doctor | 4 | | |
| D Patient | 3 | | |
| E RBAC | 5 | | |
| F UI | 4 | | |
| **Total** | **30** | | |

**Overall result:** ☐ All pass  ☐ Failures noted (describe below)

**Notes:**

---

*Attach screenshots of key pages for dissertation Chapter 6.*
