# 📦 Docker‑policy – AADS/NAVI

Denne policyen definerer hvordan Docker‑images, containere og runtime‑miljø skal bygges og driftes i dette prosjektet.  
Ops‑01 (Runtime, Docker & Deployment Overseer) håndhever disse reglene.

---

## 1. Images

- Bruk **små, stabile base‑images** (alpine/slim der det er fornuftig).
- Unngå unødvendige verktøy og pakker.
- Rydd opp etter `apt`/`apk` (ingen cache, ingen midlertidige filer).
- Lås versjoner der det er kritisk (forutsigbarhet > “latest”).

---

## 2. Lagdeling

- Installer avhengigheter før applikasjonskode for bedre caching.
- Unngå å endre filer unødvendig i tidlige lag.
- Del opp Dockerfile i logiske steg (deps, build, runtime).

---

## 3. Secrets & konfig

- **Ingen secrets i Dockerfile.**
- Bruk miljøvariabler, secrets‑store eller mountede filer.
- Konfigurasjon skal være runtime‑styrt, ikke hardkodet.

---

## 4. Runtime

- Containere skal ha:
  - Fornuftig `HEALTHCHECK`
  - Fornuftig `restart`‑policy (f.eks. `on-failure` eller `always` der det gir mening)
- Prosesser skal ikke kjøre som root hvis det kan unngås.
- Logg til stdout/stderr, ikke til tilfeldige filer.

---

## 5. Logging & observability

- Logg strukturert der det er mulig (JSON eller konsistent format).
- Logg feil med nok kontekst til å feilsøke.
- Ikke spam loggene med støy.

---

## 6. Ressurser

- Vurder `limits` og `requests` der det er relevant (Kubernetes / orkestrering).
- Unngå minnelekkasjer, uendelige loops og ukontrollert ressursbruk.

---

## 7. Review

Ved endringer i Dockerfiles, compose‑filer eller runtime‑konfig:

- Ops‑01 skal vurdere:
  - Stabilitet
  - Sikkerhet
  - Ressursbruk
  - Observability

Hvis noe er uklart, skal det dokumenteres i PR‑beskrivelsen.