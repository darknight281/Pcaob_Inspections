"""Helpers for classifying PCAOB quality-control (Part II) criticisms.

Modules
-------
config       Paths and taxonomy loading.
extract      PDF text extraction, QC-section detection, unit segmentation.
rules        Dictionary (regex) classifier for criticism units and firm responses.
llm          Claude prompt, JSON schema, and output validation for the LLM coder.
diagnostics  Reliability, co-occurrence, lexical, and unsupervised-structure checks.
"""
