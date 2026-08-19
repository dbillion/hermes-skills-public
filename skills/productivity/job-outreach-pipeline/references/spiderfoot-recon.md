# SpiderFoot Recon — verified commands (v4.0.0, docker compose)

## Start the stack
```
cd /home/deeone/spiderfoot
docker compose up -d --build
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/   # expect 200
```

## Control via sfcli.py (NOT the `scan` verb — use `start`)
```
MODS="sfp_dnsresolve,sfp_dns,sfp_certspotter,sfp_censys,sfp_builtwith,sfp_arin,sfp_bingsearch,sfp_circllu,sfp_dnsneighbor,sfp_threatcrowd,sfp_dnsdumpster,sfp_sublist3r,sfp_subdomain_takeover,sfp_webcontent"
echo "start infios.com -m $MODS -n Infios-Recon" | python3 sfcli.py -s http://127.0.0.1:5001
echo "scaninfo 4E5E4544" | python3 sfcli.py -s http://127.0.0.1:5001   # poll RUNNING/FINISHED
echo "export 4E5E4544"  | python3 sfcli.py -s http://127.0.0.1:5001   # full JSON dump
```

## Result parsing (company email is in RAW_RIR_DATA, not a clean EMAILADDR event)
```python
import json,re
data=json.load(open('/tmp/scan.json'))
emails={m.group(0).lower() for r in data
         for m in [re.search(r'[\w.%+-]+@([\w.-]+)', r['data'])] if m and 'infios.com' in r['data']}
```
Corporate emails from ARIN WHOIS (public RIR) are ACCEPTABLE. Personal scrapes are NOT.

## Scope rule
Company domain only. Never target a person. `sfp_arin` yields the registrant's corporate email
from the public RIR record — that is the intended, safe output.
