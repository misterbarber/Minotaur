import csv, json, glob, sys
sys.path.insert(0, '/home/claude/screen')
from classify import C, M, JUR, FRASER_NAMED

FX_AUD = {"AUD": 1.0, "CAD": 0.5308/0.5268, "USD": 0.7567/0.5268}  # to AUD, Pound Sterling Live 8-9 Oct 2026
TO_USD = {"AUD": 0.6962, "CAD": 0.7015, "USD": 1.0}

rows = []
for r in csv.DictReader(open('/home/claude/screen/raw.tsv'), delimiter='\t'):
    ccy = "AUD" if r['ex'] == "ASX" else "CAD"
    f = lambda k: float(r[k]) if r[k] not in ("", None) else None
    rows.append(dict(id=r['id'], ex=r['ex'], name=r['name'], ccy=ccy, price=f('price'), date=r['date'], mcap=f('mcap'),
                     shares=f('shares'), vol=f('vol'), lo=f('lo'), hi=f('hi'), note=r['note'], src="StockAnalysis quote page", npv=None))

# Minotaur 19 from the app's data store (refreshed 9 Oct 2026)
D = '/tmp/claude-0/-home-claude/d3f8bbc7-45b3-51c9-bb29-1cedb568c777/scratchpad/db2/stocks/'
for fn in glob.glob(D + '*.json'):
    d = json.load(open(fn)); d = d.get('data', d)
    mc = d['price'] * d['shares'] if d.get('shares') else d.get('mcap')
    w = d.get('w52') or [None, None]
    rows.append(dict(id=d['id'], ex=d['exchange'], name=d['name'], ccy=d['ccy'], price=d['price'], date=d['priceDate'], mcap=mc,
                     shares=d.get('shares'), vol=None, lo=w[0], hi=w[1], note="", src="Minotaur data store (refreshed 9 Oct 2026)",
                     npv=d.get('npv'), minotaur=True, stage_note=d.get('stageNote', '')))

out = []
for r in rows:
    i = r['id']
    if r.get('minotaur'):
        reg, stage, aq, cat, fund, note = M[i]
        metal = None
        conf = "H"
        d = json.load(open(D + i + '.json')); d = d.get('data', d)
        metal, country, project = d['metal'], d['country'], d['project']
    else:
        metal, country, reg, project, stage, aq, cat, fund, conf, note = C[i]
    r.update(metal=metal, country=country, region=reg, project=project, stage=stage, conf=conf, analyst=note)
    mcap_aud = r['mcap'] * FX_AUD[r['ccy']] if r['mcap'] else None
    r['mcap_aud'] = mcap_aud
    turn = r['vol'] * r['price'] * FX_AUD[r['ccy']] if r['vol'] else None
    r['turnover_aud'] = turn

    # ---- hard filters ----
    fails = []
    if i in ("MEI",): fails.append("Agreed takeover (Lynas scheme)")
    if i in ("MAUASX", "FOM"): fails.append("Acquired - delisted/inactive")
    if i == "ASMREE": fails.append("Being acquired (Energy Fuels)")
    if mcap_aud is not None and mcap_aud > 5000: fails.append("Above A$5bn ceiling")
    if mcap_aud is not None and mcap_aud < 30: fails.append("Below A$30m floor")
    if turn is not None and turn < 100000: fails.append("Turnover < A$100k (single-day volume)")
    r['fails'] = "; ".join(fails)
    flags = []
    if i in ("AGA",): flags.append("Proposed merger with Bunker Hill")
    if i in ("CNB",): flags.append("Evolution deal referenced by Morgans - verify")
    if conf == "L": flags.append("Low confidence - research before inclusion")
    r['flags'] = "; ".join(flags)

    # ---- scores ----
    jur = JUR.get(reg, 5)
    r['jur'] = jur
    r['jur_basis'] = "Fraser 2025 named rank" if reg in FRASER_NAMED else "Analyst tier"
    # valuation: P/NPV where a study NPV exists, else neutral 7
    val, pnav = 7, None
    n = r.get('npv')
    if n and n.get('value') and mcap_aud:
        pnav = (mcap_aud * TO_USD['AUD']) / (n['value'] * TO_USD.get(n['ccy'], 1))
        val = 15 if pnav < 0.2 else 13 if pnav < 0.35 else 11 if pnav < 0.5 else 9 if pnav < 0.75 else 6 if pnav < 1.0 else 4
    r['pnav'] = pnav; r['val'] = val
    # market signals: liquidity (0-5) + 52-week position (0-5)
    liq = 2 if turn is None else (5 if turn >= 5e6 else 4 if turn >= 1e6 else 3 if turn >= 2.5e5 else 2 if turn >= 1e5 else 0)
    pos = None
    if r['lo'] is not None and r['hi'] and r['hi'] > r['lo'] and r['price'] is not None:
        pos = max(0, min(1, (r['price'] - r['lo']) / (r['hi'] - r['lo'])))
    mom = 2 if pos is None else (5 if pos >= 0.66 else 3 if pos >= 0.33 else 1)
    r['pos52'] = pos
    r['mkt'] = liq + mom
    r['aq'], r['cat'], r['fund'] = aq, cat, fund
    r['score'] = aq + cat + val + fund + jur + r['mkt'] if not r['fails'] else None
    out.append(r)

json.dump(out, open('/home/claude/screen/scored.json', 'w'), indent=1, default=str)
elig = [r for r in out if r['score'] is not None]
print("total", len(out), "eligible", len(elig))
from collections import Counter
print(Counter(r['metal'] for r in elig))
print("excluded:", [(r['id'], r['fails']) for r in out if r['fails']])
