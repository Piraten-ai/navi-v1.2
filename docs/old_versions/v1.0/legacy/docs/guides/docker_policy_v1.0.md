**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# ðŸ“¦ Dockerâ€‘policy â€“ AADS/NAVI

Denne policyen definerer hvordan Dockerâ€‘images, containere og runtimeâ€‘miljÃ¸ skal bygges og driftes i dette prosjektet.  
Opsâ€‘01 (Runtime, Docker & Deployment Overseer) hÃ¥ndhever disse reglene.

---

## 1. Images

- Bruk **smÃ¥, stabile baseâ€‘images** (alpine/slim der det er fornuftig).
- UnngÃ¥ unÃ¸dvendige verktÃ¸y og pakker.
- Rydd opp etter `apt`/`apk` (ingen cache, ingen midlertidige filer).
- LÃ¥s versjoner der det er kritisk (forutsigbarhet > â€œlatestâ€).

---

## 2. Lagdeling

- Installer avhengigheter fÃ¸r applikasjonskode for bedre caching.
- UnngÃ¥ Ã¥ endre filer unÃ¸dvendig i tidlige lag.
- Del opp Dockerfile i logiske steg (deps, build, runtime).

---

## 3. Secrets & konfig

- **Ingen secrets i Dockerfile.**
- Bruk miljÃ¸variabler, secretsâ€‘store eller mountede filer.
- Konfigurasjon skal vÃ¦re runtimeâ€‘styrt, ikke hardkodet.

---

## 4. Runtime

- Containere skal ha:
  - Fornuftig `HEALTHCHECK`
  - Fornuftig `restart`â€‘policy (f.eks. `on-failure` eller `always` der det gir mening)
- Prosesser skal ikke kjÃ¸re som root hvis det kan unngÃ¥s.
- Logg til stdout/stderr, ikke til tilfeldige filer.

---

## 5. Logging & observability

- Logg strukturert der det er mulig (JSON eller konsistent format).
- Logg feil med nok kontekst til Ã¥ feilsÃ¸ke.
- Ikke spam loggene med stÃ¸y.

---

## 6. Ressurser

- Vurder `limits` og `requests` der det er relevant (Kubernetes / orkestrering).
- UnngÃ¥ minnelekkasjer, uendelige loops og ukontrollert ressursbruk.

---

## 7. Review

Ved endringer i Dockerfiles, composeâ€‘filer eller runtimeâ€‘konfig:

- Opsâ€‘01 skal vurdere:
  - Stabilitet
  - Sikkerhet
  - Ressursbruk
  - Observability

Hvis noe er uklart, skal det dokumenteres i PRâ€‘beskrivelsen.
