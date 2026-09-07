/** Simple UI copy for NeuroScan Nepal */

export const BRAND = {
  name: 'NeuroScan Nepal',
  namePart1: 'NeuroScan',
  namePart2: 'Nepal',
  tagline: 'Brain MRI screening support for Nepal',
  subtitle: 'Grande International Hospital · MRI screening',
  institution: 'Final Year Project · Birmingham City University · 2026',
}

export const LOGIN_PANEL = {
  tagline: 'AI-assisted screening. Clinician-led decisions.',
  mission:
    'NeuroScan Nepal uses deep learning and explainable AI to support brain MRI screening and clinical review in resource-limited healthcare settings in Nepal.',
  nepalTitle: 'Designed for resource-limited healthcare settings in Nepal.',
  nepalSupport:
    'Supporting faster access to AI-assisted MRI screening where specialist neurological expertise may be limited.',
  features: [
    {
      number: '01',
      title: 'AI-Assisted Screening',
      description:
        'Analyse brain MRI scans and identify patterns associated with common brain abnormalities.',
    },
    {
      number: '02',
      title: 'Explainable Results',
      description:
        "Grad-CAM visualisations highlight the image regions influencing the model's prediction.",
    },
    {
      number: '03',
      title: 'Clinical Workflow',
      description:
        'Share findings, review AI results, and provide recommendations through a role-based workflow.',
    },
  ],
  workflowTitle: 'How NeuroScan works',
  workflow: [
    { step: 'Upload', hint: 'MRI scan' },
    { step: 'Analyse', hint: 'AI-assisted screening' },
    { step: 'Explain', hint: 'Grad-CAM visualisation' },
    { step: 'Review', hint: 'Clinical decision support' },
  ],
  badges: [
    { label: 'AI-ASSISTED', accent: 'cyan' },
    { label: 'EXPLAINABLE', accent: 'blue' },
    { label: 'CLINICIAN-REVIEWED', accent: 'green' },
  ],
}

export const LOGIN = {
  formTitle: 'Sign in',
  formHint: 'Access your clinical workspace.',
  demoTitle: 'Development access',
  demoSubtitle: 'Quick-access roles for testing and demonstration.',
  registerPrompt: 'New patient?',
  registerLink: 'Register',
}

export const PAGES = {
  home: {
    eyebrow: 'Radiologist',
    title: 'Dashboard',
    description: 'Upload scans, track jobs, and review results.',
  },
  upload: {
    eyebrow: 'Radiologist',
    title: 'Upload MRI',
    description: 'Select a patient and upload their brain MRI scan.',
  },
  processing: {
    eyebrow: 'Pipeline',
    title: 'Processing',
    description: 'Live status of the 8-stage analysis pipeline.',
  },
  results: {
    eyebrow: 'Results',
    title: 'Analysis results',
    description: 'Review AI output and add your recommendation.',
  },
  doctorReview: {
    eyebrow: 'Doctor',
    title: 'MRI review',
    description: 'Review scans and submit your clinical recommendation.',
  },
  patientPortal: {
    eyebrow: 'Patient',
    title: 'My records',
    description: 'View your MRI, AI report, and doctor’s notes.',
  },
  modelInfo: {
    eyebrow: 'Model',
    title: 'Model information',
    description: 'Architecture, training data, and performance metrics.',
  },
  about: {
    eyebrow: 'About',
    title: 'About NeuroScan Nepal',
    description: 'AI-assisted brain MRI screening — final year research project.',
  },
  register: {
    eyebrow: 'Patient',
    title: 'Register',
    description: 'Create your patient account to access your records.',
  },
}

export const ABOUT = {
  aim: 'NeuroScan Nepal helps screen brain MRI scans for normal vs abnormal findings. It includes CNN detection, Grad-CAM explainability, medical guidance, a bilingual chatbot, and hospital referrals. This is a research prototype — not a certified medical device.',
}

export const FOOTER = {
  left: 'NeuroScan Nepal · AI-assisted screening prototype',
  right: 'Final Year Project · Birmingham City University · 2026',
}
