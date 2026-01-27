# AADS Wiki (Current)

Version: 1.1 (draft)
Last updated: 2026-01-25

This wiki reflects the current hardware split:
- Jetson: backend, AI, sensors, storage
- Raspberry Pi: dashboard UI and Arduino bridge
- PC: development and training

---

## Philosophy

When satellites fail, we survive.
The system is built to operate offline with local inference and local data.

---

## The Digital Crew

- Vakten: vision and threat detection
- Navi: conversational assistant
- Navigator: NAVTEX and route intelligence
- Legen: medical triage
- Psykologen: mental health support
- Ingenioren: diagnostics and maintenance

---

## System Architecture (Current)

Jetson
- FastAPI backend
- AI modules and models
- Databases and storage

Raspberry Pi
- UI dashboard (non-HTML recommended)
- Arduino analog-to-digital bridge
- Data forwarding to Jetson

PC
- Full stack development and training

---

## Hardware Notes

- Jetson is the edge AI system and sensor hub
- Raspberry Pi offloads UI workload from Jetson
- Arduino provides analog signal capture; Pi handles conversion and transport

---

## Deployment Summary

- Jetson runs the backend stack
- Pi runs UI + bridge services
- PC runs the dev/training stack

---

This document replaces the v1.0 wiki stored in:
- docs/old_versions/v1.0/AADS_WIKI_v1.0.md
