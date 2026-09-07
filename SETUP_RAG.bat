@echo off
title NeuroScan RAG Setup
cd /d "%~dp0"
echo Installing LangChain, FAISS, sentence-transformers, reportlab ...
py -3.11 -m pip install langchain langchain-community langchain-core faiss-cpu sentence-transformers reportlab transformers
echo.
echo Building FAISS index from medical_kb.json (53+ documents) ...
py -3.11 scripts\build_rag_index.py
echo.
echo Done. Restart NeuroScan with START_NEUROSCAN.bat
pause
