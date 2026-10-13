# Netlify static + Function + Service Account write — verified

## Deploy (CLI crashes on top-level-await bug under bun/Node here)
- Pin build in netlify.toml: `[build] command = "echo 'static site, no build'"` (prevents interactive framework prompt).
- Set env WITHOUT `--scope functions` (use `All` context): `netlify env:set GOOGLE_SA_JSON "$(cat sa-key.json)"`.
- Deploy: `netlify deploy --prod --functions functions`.

## Service Account (write to Sheets from Function)
1. `gcloud iam service-accounts create jobfit-board-sa --display-name="..." --project=<proj>`
2. `gcloud iam service-accounts keys create sa-key.json --iam-account=<sa>@<proj>.iam.gserviceaccount.com`
3. Share Sheet: `gws drive permissions create --params '{"fileId":<ID>}' --json '{"type":"user","role":"writer","emailAddress":"<sa>"}'`
4. Set `GOOGLE_SA_JSON` Netlify env = contents of sa-key.json. Keep key out of repo + web dir (.gitignore; move to ~/.hermes/secrets).

## Function write pattern (Node, RS256 JWT)
- `getToken()`: build JWT with SA `client_email`+`private_key`, POST oauth2.googleapis.com/token, get access_token.
- Write cell: `PUT https://sheets.googleapis.com/v4/spreadsheets/{ID}/values/{range}?valueInputOption=RAW` with `Authorization: Bearer {tok}`.
- gviz public CSV read (no key): `https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=Tab`
