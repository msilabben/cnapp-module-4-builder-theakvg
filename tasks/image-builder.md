# Workshop - modul 4: software supply chain security 


Krav: 
- GitHub bruker
- (Valgfritt) IDE
    - Oppgavene som krever kodeendring, kan enten gjøres lokalt på din maskin, eller bruke GitHub Desktop.

### Oppsett
1. Gi GitHub brukernavnet til fasilitator, slik at dere kan bli invitert til organisasjonen. 
2. Godkjenn invitasjonen
3. Gå til [msilabben](https://github.com/msilabben)


Si ifra til fasilitator hvis dere møter på problemer. 


## Oppgaver

### Forke M4 repo
1. Gå til msilabben og fork repoet som heter: cnapp-module-4-builder
2. Velg msilabben som miljø 
3. Gå til "Actions" og godta at workflows får lov til å kjøre. 
4. Velg "pull-request" på høyre side og manuaelt sett igang workflowen. Vent til den har kjørt ferdig. 
5. Velg "publish" på høyre side, og manuelt sett igang workflowen. 
6. Gå til organisasjonssiden "msilabben", og velg "packages" i menyen på toppen. Ser du de tilhørende imagene du publiserte?

### Verifiser signatur
1. Åpne et nytt codespace ved å gå til hjemmeområdet til ditt M4 repository, klikk på "Code", deretter "Create new codespace on main"
2. Log in på GHCR med docker cli
```bash
gh auth token | docker login ghcr.io --username $(gh api user -q ".login") --password-stdin
```
3. Hent ned og verifiser SBoM
```bash
cosign verify-attestation \
  --certificate-identity "https://github.com/msilabben/<your repository name>/.github/workflows/push-main.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  --type spdxjson \
  --output json ghcr.io/msilabben/cnapp-module-4-builder/trivy:0.71.1 2>/dev/null | jq > result.json
```
4. Ta et minutt til å reflektere: hva er det vi ser i result.json?
5. Dekod payload og inspiser innholdet
```bash
jq -r '.payload' result.json | base64 -d > payload.json
```
6. Hva er det 'subject' og 'predicate' forteller oss i payload.json?

### Oppdate M2 pipelines med ny kilde
1. Gå til msilabben og fork repoet som heter: cnapp-module-2-application ("Copy the main branch only" skal være avslått)
2. Velg msilabben som miljø. 
3. Gå til "actions" og godta at workflows får lov til å kjøre. 
4. Gi M2 tilgang til de bygde pakkene ved å gå til 'msilabben > packages > <din pakke> > package settings > add repository > velg din M2'
5. Åpne et codespace på branch "use-own-images", ved å gå til https://github.com/msilabben/<ditt M2 repo>/tree/fix/use-own-images > "Code" > "create workspace on fix/use-own-images"
6. Åpne filen `.github/workflows/pull-request.yml` og rediger følgende til å passe ditt repo og dine publiserte pakker:
- COSIGN_CERTIFICATE_IDENTITY
- SEMGREP_IMAGE
- TRIVY_IMAGE
- CONFTEST_IMAGE
7. Commit endringene og push
8. Åpne en PR og verifiser at denne blir grønn

### Lag OPA policy 
1. Gå til codespace for M2.
2. Gå til ".github/workflows/pull-request.yml" og lokaliser opa-jobben. 
3. Gå til "policy/semgrep.rego" og se på semgrep regelen. 
4. Med inspirasjon fra semgrep, prøv å lag en OPA-regel som kun tillater images fra msilabben sin ghcr, med pull-request workflowen som inputet. (Lag en ny .rego fil, oppdater pull-request.yml med regelen, og sett inputet til å være .github/workflow/pull-request.yml)
