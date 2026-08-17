"""Generate NeuroScan Nepal 32-week supervisor journal (Mahara format)."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "submission" / "NeuroScan_Nepal_Weekly_Journal_32_Weeks_Updated.docx"

WEEKS = [
    {
        "week": 1,
        "activity": (
            "Set up my Mahara journal on the BCU ePortfolio system and read the project handbook to "
            "understand the assessment structure, submission deadlines, and expectations. Attended the "
            "first project tutorial and met with my supervisor to discuss project ideas. Confirmed the "
            "project topic: an AI-powered brain abnormality detection and advisory system for Nepal, "
            "named NeuroScan Nepal. Began initial discussions on using anonymised brain MRI scans from "
            "Grande International Hospital, Kathmandu as the primary clinical dataset for the project."
        ),
        "issues": (
            "The initial scope felt broad. My supervisor advised focusing the detection task on binary "
            "classification (normal vs abnormal) rather than multi-class tumour type classification, "
            "which narrowed the scope to something achievable within the timeline. Access to the Grande "
            "Hospital dataset would require ethics approval and confirmed anonymisation procedures."
        ),
        "actions": [
            "Read foundational literature on deep learning and medical image classification",
            "Draft an initial problem statement based on Nepal's healthcare context",
            "Contact Grande International Hospital regarding anonymised MRI brain scan data access",
            "Identify ethics requirements for using hospital-sourced clinical imaging data",
        ],
    },
    {
        "week": 2,
        "activity": (
            "Conducted a structured literature review on CNN-based brain MRI classification and "
            "explainable AI methods such as Grad-CAM. Collected and summarised five academic papers "
            "and two industry case studies. Drafted functional requirements for upload, classification, "
            "reporting, and user roles (radiologist, doctor, patient). Confirmed Grande International "
            "Hospital, Kathmandu as the primary data source for anonymised brain MRI scans, giving the "
            "project direct relevance to the Nepalese healthcare setting."
        ),
        "issues": (
            "Hospital datasets require strict ethics and anonymisation unlike public Kaggle datasets. "
            "Supervisor recommended documenting Grande Hospital data governance clearly in the proposal "
            "and keeping a supplementary public dataset only as backup if hospital access was delayed."
        ),
        "actions": [
            "Complete literature review draft with comparison table",
            "Finalise functional and non-functional requirements",
            "Document Grande International Hospital dataset access plan and data fields available",
            "Draft data handling protocol for anonymised MRI scans from Grande Hospital",
        ],
    },
    {
        "week": 3,
        "activity": (
            "Designed the high-level system architecture for NeuroScan Nepal: React frontend, FastAPI "
            "backend, and PyTorch ML pipeline. Created flowcharts for the eight-stage processing pipeline "
            "(upload, preprocessing, detection, Grad-CAM, RAG advisory, chatbot, hospital finder, report "
            "export). Selected the technology stack and documented rationale for each choice. Built a "
            "32-week Gantt chart for supervisor review."
        ),
        "issues": (
            "Deciding between a single monolithic app vs separate frontend/backend caused some delay. "
            "Supervisor supported a decoupled architecture to demonstrate full-stack skills and easier "
            "testing."
        ),
        "actions": [
            "Refine architecture diagrams for the interim report",
            "Define folder structure and naming conventions for the repository",
            "Begin ethics and data handling section for Grande Hospital MRI dataset",
            "Plan data/raw/ folder structure for normal and abnormal classes from Grande Hospital",
        ],
    },
    {
        "week": 4,
        "activity": (
            "Completed the formal project proposal including problem statement, objectives, methodology, "
            "and evaluation plan. Wrote the ethics and data privacy section covering anonymised Grande "
            "International Hospital MRI scans, patient identifier removal, and prototype disclaimers. "
            "Set up the Git repository with .gitignore for models, uploads, logs, and the Grande Hospital "
            "dataset (stored locally in data/raw/, not committed). Submitted the proposal and presented "
            "a brief overview to my supervisor."
        ),
        "issues": (
            "Ethics form required clarification on hospital-sourced patient data. Confirmed that only "
            "anonymised MRI scans approved by Grande International Hospital and BCU ethics procedures "
            "would be used, with no patient names or identifiers stored in the system."
        ),
        "actions": [
            "Await proposal feedback and revise if needed",
            "Set up Python virtual environment and install core dependencies",
            "Receive and inspect the Grande International Hospital MRI dataset",
            "Organise scans into data/raw/normal and data/raw/abnormal folders",
        ],
    },
    {
        "week": 5,
        "activity": (
            "Configured the development environment on Windows: Python 3.11, PyTorch, FastAPI, Node.js, "
            "and React with Vite. Created requirements.txt, requirements-cnn.txt, and a README with "
            "step-by-step setup instructions. Verified PyTorch installation and ran a small tensor "
            "operation test. Initialized the frontend with Tailwind CSS."
        ),
        "issues": (
            "PyTorch installation required a specific Python version (3.11). Documented the exact "
            "commands to avoid setup issues during viva demonstration."
        ),
        "actions": [
            "Explore Grande International Hospital dataset structure and class balance",
            "Create train/validation/test split script for data/raw/ folders",
            "Visualise sample normal and abnormal Grande Hospital MRI images for the logbook",
        ],
    },
    {
        "week": 6,
        "activity": (
            "Received and explored the Grande International Hospital brain MRI dataset (~1,600 anonymised "
            "scans). Organised images into data/raw/normal and data/raw/abnormal directories. Analysed "
            "class distribution and documented image dimensions, formats, and quality variation from the "
            "Grande Hospital scans. Created train/validation/test splits and saved split statistics. "
            "Produced sample visualisations comparing normal and abnormal cases for the interim report."
        ),
        "issues": (
            "Grande Hospital dataset contained mixed image sizes and colour/grayscale formats across "
            "different scanner exports. Planned a standardisation step in preprocessing to handle this "
            "consistently before CNN training."
        ),
        "actions": [
            "Implement image loading for JPEG, PNG, and NIfTI formats",
            "Implement CLAHE contrast enhancement",
            "Design low-contrast quality check for unreliable scans",
        ],
    },
    {
        "week": 7,
        "activity": (
            "Implemented the preprocessing module (preprocessing.py): scan loading via nibabel and Pillow, "
            "CLAHE enhancement, resize to 128×128 grayscale, and low-contrast quality flagging. Ran "
            "before/after CLAHE comparisons on ten sample images. Wrote unit tests in "
            "test_preprocessing_pipeline.py and all tests passed."
        ),
        "issues": (
            "Some scans had very low dynamic range, triggering false low-quality flags. Adjusted "
            "percentile-based threshold after reviewing edge cases with supervisor guidance."
        ),
        "actions": [
            "Design Baseline CNN architecture for binary classification",
            "Document layer structure and parameter count",
            "Prepare training script skeleton",
        ],
    },
    {
        "week": 8,
        "activity": (
            "Designed and implemented the Baseline CNN model (cnn_baseline.py) with convolutional blocks, "
            "pooling, and a two-class output layer (normal/abnormal). Documented architecture decisions "
            "and total trainable parameters. Created a model summary diagram for the technical report."
        ),
        "issues": (
            "Initial model was slightly too deep for the dataset size. Reduced complexity to reduce "
            "overfitting risk on limited training samples."
        ),
        "actions": [
            "Implement training loop with CrossEntropy loss and Adam optimiser",
            "Configure checkpoint saving to models/cnn_baseline.pth",
            "Run first training experiment and log results",
        ],
    },
    {
        "week": 9,
        "activity": (
            "Built the training pipeline (train_cnn.py) with batch loading from the Grande International "
            "Hospital dataset (data/raw/normal and data/raw/abnormal), loss computation, and validation "
            "accuracy tracking. Ran multiple training epochs and logged loss curves. Saved model "
            "checkpoints. Monitored training on CPU/GPU and recorded epoch duration for the logbook."
        ),
        "issues": (
            "Training was slow on CPU. Used smaller batch size and fewer epochs for iteration, planning "
            "a longer final training run overnight."
        ),
        "actions": [
            "Complete full training run to convergence",
            "Evaluate model on validation set",
            "Generate confusion matrix and classification metrics",
        ],
    },
    {
        "week": 10,
        "activity": (
            "Evaluated the trained CNN on the Grande International Hospital validation and test sets "
            "using evaluate.py. Achieved 97.81% validation accuracy on the Grande Hospital "
            "MRI dataset (~1,600 scans). Generated confusion matrix, precision, recall, and F1 scores. "
            "Saved evaluation report to results/cnn_baseline_report.txt. Compared results with published "
            "baseline figures from literature."
        ),
        "issues": (
            "Minor class imbalance in the Grande Hospital dataset caused slightly lower recall on abnormal "
            "cases. Noted as a limitation and possible future improvement (class weighting or data "
            "augmentation)."
        ),
        "actions": [
            "Implement single-scan prediction script (predict.py)",
            "Test inference on held-out sample images",
            "Begin Grad-CAM explainability module",
        ],
    },
    {
        "week": 11,
        "activity": (
            "Implemented predict.py for single MRI inference: load model weights, preprocess scan, "
            "return label and confidence score. Tested on ten manual samples with expected outcomes. "
            "Wrote test_predict.py; all assertions passed. Documented inference latency per scan."
        ),
        "issues": (
            "Confidence scores were miscalibrated on low-quality inputs. Integrated the preprocessing "
            "quality flag so downstream stages can warn the user."
        ),
        "actions": [
            "Implement Grad-CAM heatmap generation and overlay",
            "Save explainability images alongside predictions",
            "Test Grad-CAM on both normal and abnormal cases",
        ],
    },
    {
        "week": 12,
        "activity": (
            "Implemented Grad-CAM explainability (04_gradcam.py): backward pass on the predicted class, "
            "heatmap generation, and overlay on the original scan. Saved outputs to gradcam.png per job. "
            "Compared heatmaps for normal vs abnormal cases and included figures in the logbook."
        ),
        "issues": (
            "Heatmap resolution did not always align with display size. Added resize step so overlay "
            "matches the preprocessed image dimensions."
        ),
        "actions": [
            "Build medical knowledge base for RAG-style advisory text",
            "Write normal and abnormal advisory templates",
            "Link advisory output to model confidence in pipeline",
        ],
    },
    {
        "week": 13,
        "activity": (
            "Created the RAG advisory module with a structured medical knowledge base (MEDICAL_KB) for "
            "normal and abnormal outcomes. Generated advisory text including further investigation "
            "recommendations for abnormal scans. Added prototype disclaimer stating output is not "
            "clinical advice. Integrated advisory stage into pipeline.py."
        ),
        "issues": (
            "Rule-based RAG is limited compared to a live retrieval system. Supervisor accepted this "
            "for the prototype scope but recommended describing upgrade path in the final report."
        ),
        "actions": [
            "Implement bilingual chatbot responses (English and Nepali)",
            "Create Nepal hospital recommendation list",
            "Wire chatbot and hospital finder into the pipeline",
        ],
    },
    {
        "week": 14,
        "activity": (
            "Implemented bilingual chatbot guidance (English/Nepali) and a hospital finder listing "
            "neurology centres in Nepal, including Grande International Hospital (Kathmandu), Tribhuvan "
            "University Teaching Hospital, and Nepal Mediciti. Configured hospital list to expand for "
            "abnormal results. Tested output formatting for patient-facing display."
        ),
        "issues": (
            "Nepali translations were prototype-level. Noted need for review by a native speaker before "
            "any real deployment."
        ),
        "actions": [
            "Integrate all eight pipeline stages into pipeline.py",
            "Implement JSON, TXT, and HTML report export",
            "Run end-to-end test on five sample scans",
        ],
    },
    {
        "week": 15,
        "activity": (
            "Completed end-to-end pipeline integration in pipeline.py: all eight stages run sequentially "
            "with stage callbacks for progress tracking. Implemented report export (report.json, report.txt, "
            "report.html) under results/jobs/{job_id}/. Successfully processed five test scans from upload "
            "to final report."
        ),
        "issues": (
            "One NIfTI sample failed due to unexpected dimensions. Added fallback to mean intensity "
            "projection for multi-slice volumes."
        ),
        "actions": [
            "Add structured logging to neuroscan.log",
            "Run integration test on 25 images",
            "Document average pipeline duration and failure rate",
        ],
    },
    {
        "week": 16,
        "activity": (
            "Set up structured logging (logging_config.py) with INFO-level pipeline traces. Ran "
            "integration_test_25.py across 25 Grande International Hospital MRI scans and recorded "
            "accuracy, confidence, and processing time. Fixed two stage-logging bugs found during batch "
            "testing. Saved test evidence for the interim demonstration."
        ),
        "issues": (
            "Two scans failed preprocessing due to corrupt files. Added clearer error messages and "
            "failed job status in the job store."
        ),
        "actions": [
            "Create FastAPI backend skeleton with /health endpoint",
            "Configure CORS and upload directory",
            "Plan REST API endpoints for upload and job status",
        ],
    },
    {
        "week": 17,
        "activity": (
            "Built the FastAPI backend (backend.py) with health check and pipeline steps endpoints. "
            "Configured CORS for the React frontend. Created uploads/ and results/jobs/ directories. "
            "Tested endpoints with curl and confirmed JSON responses."
        ),
        "issues": (
            "Had to ensure src/ was on PYTHONPATH for pipeline imports when running uvicorn from "
            "project root. Documented startup command in README."
        ),
        "actions": [
            "Implement POST /upload with background pipeline thread",
            "Implement jobs.json persistence with thread-safe updates",
            "Implement GET /jobs and GET /jobs/{id}",
        ],
    },
    {
        "week": 18,
        "activity": (
            "Implemented file upload API: save scan to uploads/, create job record, spawn daemon thread "
            "for process_job(). Built jobs.json job store with status, stages, and result fields. "
            "Implemented list and detail endpoints. Verified upload-to-completion flow via API calls."
        ),
        "issues": (
            "Concurrent uploads required a lock on jobs.json to prevent corruption. Added threading.RLock "
            "around all job read/write operations."
        ),
        "actions": [
            "Improve error handling for missing PyTorch/pipeline",
            "Add HTTP request logging middleware",
            "Document API in README and test with Postman",
        ],
    },
    {
        "week": 19,
        "activity": (
            "Hardened backend error handling for pipeline unavailable, upload failures, and job failures. "
            "Added request logging middleware writing to neuroscan.log. Tested concurrent uploads and "
            "documented API behaviour. Reviewed OpenAPI docs at /docs."
        ),
        "issues": (
            "Large file uploads occasionally timed out on slow disk. Increased client timeout guidance in "
            "frontend documentation."
        ),
        "actions": [
            "Fix confidence score display mismatch (score vs confidence field)",
            "Create shared frontend utility for job result parsing",
            "Begin React frontend pages for upload and results",
        ],
    },
    {
        "week": 20,
        "activity": (
            "Identified and fixed confidence score bug: jobs.json stored result.score but the UI read "
            "result.confidence, showing 0%. Created jobResult.js utility to read score with confidence "
            "fallback. Updated Upload, Processing, and Results pages. Regression-tested against existing "
            "jobs in jobs.json."
        ),
        "issues": (
            "Older jobs in jobs.json had minimal result objects (score only). UI now handles both full "
            "and legacy result formats gracefully."
        ),
        "actions": [
            "Set up React app with routing and Tailwind styling",
            "Build Upload page with file picker and progress bar",
            "Build Processing page with live stage polling",
        ],
    },
    {
        "week": 21,
        "activity": (
            "Initialized React frontend with Vite, React Router, and Tailwind CSS. Created routes for "
            "Home, Upload, Processing, Results, Model Info, and About. Built reusable components: Header, "
            "Footer, PageHeader, StatusBadge, and BackendStatus. Configured API_BASE and pipeline step "
            "definitions in config.js."
        ),
        "issues": (
            "Vite CJS deprecation warning appeared but did not block development. Tracked for future "
            "Vite config update."
        ),
        "actions": [
            "Complete Upload page with XHR progress and job polling",
            "Complete Processing page with eight-stage breakdown",
            "Build Results page with RAG advisory and hospital list",
        ],
    },
    {
        "week": 22,
        "activity": (
            "Completed Upload page with MRI preview, upload progress, and two-second job polling. Built "
            "Processing page showing real-time pipeline stage status with progress bar. Connected frontend "
            "to backend APIs. Tested full upload-to-processing flow in the browser."
        ),
        "issues": (
            "Polling continued after job completion until page navigation. Added completion message and "
            "links to Results page."
        ),
        "actions": [
            "Build Home dashboard with job statistics",
            "Build Results page with classification and reports section",
            "Add Model Info and About pages",
        ],
    },
    {
        "week": 23,
        "activity": (
            "Built Results page displaying classification, confidence, probabilities, RAG advisory, "
            "bilingual chatbot text, hospital recommendations, and report paths. Created Home dashboard "
            "with total/running/completed job counts and recent activity list. Added Model Info page with "
            "dataset and architecture summary."
        ),
        "issues": (
            "Report download paths were server filesystem paths, not direct downloads. Documented as "
            "known limitation; files accessible on server under results/jobs/."
        ),
        "actions": [
            "Polish UI styling and responsive layout",
            "Conduct informal peer review of the interface",
            "Update prototype.html for standalone demonstrations",
        ],
    },
    {
        "week": 24,
        "activity": (
            "Refined UI with consistent card layout, gradient result headers, and status badges. Improved "
            "mobile navigation in Header. Conducted peer review with two classmates; incorporated feedback "
            "on clearer status messages and empty states. Updated colour scheme for clinical readability."
        ),
        "issues": (
            "Peers found the Processing page technical for non-technical users. Added plain-language stage "
            "labels alongside technical step keys."
        ),
        "actions": [
            "Enhance prototype.html with sample cases and live upload",
            "Run full frontend-backend integration test checklist",
            "Prepare interim demonstration for supervisor",
        ],
    },
    {
        "week": 25,
        "activity": (
            "Updated prototype.html with normal/abnormal sample cases, carousel navigation, and live upload "
            "integration. Demonstrated quick comparison between static samples and real API-driven analysis. "
            "Prepared a five-minute demo script for presentations."
        ),
        "issues": (
            "Prototype page initially failed after backend auth was added (401 error). Logged fix for "
            "following week when RBAC is implemented."
        ),
        "actions": [
            "Complete end-to-end integration testing",
            "Fix remaining UI bugs from test checklist",
            "Plan role-based access control for clinical workflow",
        ],
    },
    {
        "week": 26,
        "activity": (
            "Executed full integration test checklist: upload JPEG/PNG scans, monitor all eight pipeline "
            "stages, verify results display and jobs.json persistence. Fixed CORS and timeout issues. "
            "Documented known limitations in README. Demonstrated working system to supervisor at interim "
            "checkpoint."
        ),
        "issues": (
            "Supervisor requested role separation (radiologist, doctor, patient) for a more realistic "
            "clinical workflow. Scoped RBAC implementation for weeks 27–29."
        ),
        "actions": [
            "Design authentication system with JWT and SQLite",
            "Define role permissions matrix",
            "Implement login and registration pages",
        ],
    },
    {
        "week": 27,
        "activity": (
            "Implemented authentication module (src/auth.py) with SQLite user store, bcrypt password "
            "hashing, and JWT tokens. Created three roles: radiologist, doctor, and patient. Auto-generated "
            "unique patient IDs (NSN-PAT-000001). Built Login and Register pages with AuthContext and "
            "ProtectedRoute guards. Seeded demo accounts for testing."
        ),
        "issues": (
            "passlib/bcrypt compatibility issue on Windows required switching to bcrypt library directly. "
            "Documented fix in requirements.txt."
        ),
        "actions": [
            "Protect API endpoints with role-based access",
            "Build Doctor Review page for MRI viewing and recommendations",
            "Build Patient Portal (My Records) for report access",
        ],
    },
    {
        "week": 28,
        "activity": (
            "Implemented role-based API filtering: radiologists see all jobs, doctors see completed scans, "
            "patients see only their own records. Built Doctor Review page with MRI image viewer, AI summary, "
            "and recommendation form. Built Patient Portal showing MRI, AI report, and doctor recommendation. "
            "Radiologist upload now requires patient assignment."
        ),
        "issues": (
            "MRI images could not load in img tags without auth headers. Implemented blob fetch with "
            "Authorization for secure image display."
        ),
        "actions": [
            "Add radiologist investigation recommendation field on Results page",
            "Fix prototype.html authentication for demo uploads",
            "Test complete clinical workflow across all three roles",
        ],
    },
    {
        "week": 29,
        "activity": (
            "Added radiologist notes feature: investigation recommendation and optional notes for the "
            "doctor on the Results page (POST /jobs/{id}/radiologist-notes). Doctor and patient views now "
            "show radiologist recommendations. Fixed prototype.html 401 errors with auto-login and patient "
            "selection. Ran full workflow test: patient register → radiologist upload → radiologist notes "
            "→ doctor review → patient view."
        ),
        "issues": (
            "Legacy jobs without patient_user_id do not appear in patient portal. Documented that only "
            "new uploads after RBAC are linked to patients."
        ),
        "actions": [
            "Run system-wide testing on 25+ scans with all roles",
            "Measure and document average pipeline processing time",
            "Begin final report and user documentation",
        ],
    },
    {
        "week": 30,
        "activity": (
            "Conducted system testing across all roles: verified login permissions, job isolation, and "
            "recommendation handoff chain. Re-ran integration test on 25 Grande Hospital MRI scans; "
            "recorded accuracy and average processing time (~10–30 seconds per scan). Tested backend "
            "offline behaviour and frontend error messages. Compiled test report with pass/fail summary."
        ),
        "issues": (
            "One scan failed due to corrupt PNG header. Failure handling correctly marked job as failed "
            "with error message visible in UI."
        ),
        "actions": [
            "Complete README with install, run, and demo account instructions",
            "Write user manual sections for each role",
            "Draft evaluation and discussion chapters for final report",
        ],
    },
    {
        "week": 31,
        "activity": (
            "Finalised project documentation: README, user manual for radiologist/doctor/patient workflows, "
            "and API overview. Documented the Grande International Hospital dataset (~1,600 anonymised MRI "
            "scans) as the primary training and evaluation data source. Prepared architecture diagrams, "
            "pipeline flowchart, and RBAC matrix for the technical report. Wrote evaluation section "
            "covering accuracy metrics on the Grande Hospital dataset, usability observations, and "
            "system limitations. Rehearsed ten-minute viva demonstration with all three roles."
        ),
        "issues": (
            "Report word count required trimming in the literature review section. Supervisor advised "
            "moving detailed API documentation to an appendix."
        ),
        "actions": [
            "Final proofread of report and logbook",
            "Prepare presentation slides for viva",
            "Package code, report, and logbook for submission",
        ],
    },
    {
        "week": 32,
        "activity": (
            "Completed final review of codebase, report, and Mahara logbook entries. Prepared viva "
            "presentation slides covering problem statement, methodology, demo, evaluation, and future "
            "work. Rehearsed live demonstration: patient registration, radiologist upload and notes, "
            "doctor recommendation, patient report view. Submitted final project package to BCU ePortfolio "
            "and module submission point."
        ),
        "issues": (
            "Minor slide formatting issues resolved before submission. Reflected on project outcomes: "
            "achieved binary classification pipeline, explainability, clinical workflow, and role-based "
            "access within the planned timeline."
        ),
        "actions": [
            "Attend viva voce examination",
            "Archive Git repository with final release tag",
            "Write post-project reflection on skills gained and future improvements",
        ],
    },
]


def add_section(doc, heading, body, bullet_items=None):
    p = doc.add_paragraph()
    run = p.add_run(heading)
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

    doc.add_paragraph(body)

    if bullet_items:
        for item in bullet_items:
            bp = doc.add_paragraph(item, style="List Bullet")
            for run in bp.runs:
                run.font.size = Pt(10)


def build():
    doc = Document()

    # Title
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("NeuroScan Nepal\nWeekly Project Journal\n")
    r.bold = True
    r.font.size = Pt(22)
    r.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s = sub.add_run("BCU ePortfolio / Mahara Logbook Format — 32 Weeks\n\n")
    s.font.size = Pt(12)

    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line in [
        "Student Name: _________________________________",
        "Student ID: ___________________________________",
        "Supervisor: ___________________________________",
        "Module: Final Year Project",
        "Project: AI-Powered Brain MRI Screening for Nepal",
    ]:
        info.add_run(line + "\n").font.size = Pt(11)

    doc.add_page_break()

    # Instructions
    doc.add_heading("How to Use This Journal", level=1)
    doc.add_paragraph(
        "Primary dataset: Grande International Hospital, Kathmandu — approximately 1,600 anonymised "
        "brain MRI scans organised into normal and abnormal classes (data/raw/normal, data/raw/abnormal). "
        "All patient identifiers removed per ethics approval. Dataset not committed to Git."
    )

    doc.add_paragraph(
        "Copy each week's entry into your Mahara journal on the BCU ePortfolio system. "
        "Personalise activities where needed, attach screenshots as evidence, and record "
        "actual supervisor feedback when meetings take place."
    )
    doc.add_page_break()

    for entry in WEEKS:
        doc.add_heading(f"Week {entry['week']}", level=1)

        add_section(doc, "Activity This Week", entry["activity"])
        doc.add_paragraph()
        add_section(doc, "Key Issues / Supervisor Notes", entry["issues"])
        doc.add_paragraph()
        add_section(doc, "Action Plan for Next Week", "", entry["actions"])

        if entry["week"] < 32:
            doc.add_paragraph()
            sep = doc.add_paragraph("—" * 50)
            sep.runs[0].font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

    doc.save(OUTPUT)
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    build()
