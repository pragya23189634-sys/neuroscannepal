Frontend setup and run instructions

1. Install dependencies (in the frontend folder):
   - cd NeuroScan_Nepal\frontend
   - npm install

2. Run in development mode:
   - npm run dev
   - The dev server runs at http://localhost:3000

3. Build for production:
   - npm run build
   - Preview with: npm run preview

Notes:
- This SPA expects the backend API at http://127.0.0.1:8000 (same machine). Update fetch endpoints in code when integrating.
- Tailwind must be built by PostCSS (npm install will handle dev deps).
