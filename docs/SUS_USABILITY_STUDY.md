# NeuroScan Nepal — SUS Usability Study

Print this file or share with participants. See `docs/SUS_USABILITY_STUDY.md` for full instructions.

---

## Participant information sheet

**Project:** NeuroScan Nepal — AI-assisted brain MRI screening (research prototype)  
**Researcher:** Pragya Gajurel (23189634), BSc Computer and Data Science, BCU / Sunway College Kathmandu  
**Contact:** gajurelpragya@gmail.com

### What is this study?

You are invited to test a student-built web application that demonstrates how AI might assist brain MRI screening in Nepal. The system is **not a real medical device** and must not be used for diagnosis.

### What will you do?

- Spend about **15 minutes** using the application
- Complete **4 short tasks** (login, upload, review, patient view)
- Fill in a **10-question usability questionnaire** (5 minutes)

### Do I have to take part?

No. Participation is voluntary. You may stop at any time without giving a reason.

### Will my data be kept confidential?

Yes. We record only an anonymous ID (P1, P2, …), your SUS scores, and brief notes. No name or email is required.

### Risks

Minimal. You are testing a local web app on a student laptop. No real patient data is used.

---

## Consent form

- [ ] I have read the information sheet  
- [ ] I understand this is a research prototype, not a medical tool  
- [ ] I agree to take part voluntarily  
- [ ] I am aged 18 or over  

**Participant ID:** P___ (filled by researcher)  
**Date:** _______________  
**Signature:** _______________

---

## Task script (researcher reads to participant)

1. **Start app** — Researcher opens http://127.0.0.1:3000/login  
2. **Task 1 — Radiologist:** Login as radiologist, upload one MRI scan, wait for processing to finish  
3. **Task 2 — Results:** Open the results page; say whether the label and confidence are understandable  
4. **Task 3 — Doctor:** Logout, login as doctor, submit a one-sentence clinical recommendation  
5. **Task 4 — Patient:** Logout, login as patient, open My Records and read the report  

**Demo accounts:**

| Role | Email | Password |
|------|-------|----------|
| Radiologist | radiologist@neuroscan.np | radiologist123 |
| Doctor | doctor@neuroscan.np | doctor123 |
| Patient | patient@neuroscan.np | patient123 |

---

## SUS questionnaire

**Instructions:** Rate each statement from **1** (strongly disagree) to **5** (strongly agree).

| # | Statement | 1 | 2 | 3 | 4 | 5 |
|---|-----------|---|---|---|---|---|
| 1 | I think I would like to use this system frequently | | | | | |
| 2 | I found the system unnecessarily complex | | | | | |
| 3 | I thought the system was easy to use | | | | | |
| 4 | I think I would need support to use this system | | | | | |
| 5 | I found the various functions well integrated | | | | | |
| 6 | I thought there was too much inconsistency | | | | | |
| 7 | I would imagine most people would learn quickly | | | | | |
| 8 | I found the system very cumbersome | | | | | |
| 9 | I felt very confident using the system | | | | | |
| 10 | I needed to learn a lot before I could get going | | | | | |

**Optional comments:** _______________________________________________

---

## Scoring (researcher only)

For each item, convert response to 0–4:
- Items **1, 3, 5, 7, 9:** score = response − 1  
- Items **2, 4, 6, 8, 10:** score = 5 − response  

**SUS score = (sum of 10 scores) × 2.5** → result out of **100**

| SUS range | Interpretation |
|-----------|----------------|
| &lt; 50 | Poor |
| 50–68 | Below average |
| 68–80 | Good |
| &gt; 80 | Excellent |

Run `py -3.11 scripts/calculate_sus.py` after filling `docs/SUS_RESULTS_TEMPLATE.csv`.

---

## Results record

| Participant | Date | SUS /100 | Task issues noted |
|-------------|------|----------|-------------------|
| P1 | | | |
| P2 | | | |
| P3 | | | |
| P4 | | | |
| P5 | | | |
| **Mean** | | | |
| **Std dev** | | | |

**Paste into dissertation Chapter 7:**

> Five peers (P1–P5) completed a System Usability Scale evaluation after a 15-minute guided session. Mean SUS score was **[X]/100** (SD = [Y]), indicating **[acceptable/good/excellent]** usability for a research prototype.
