"""Retire used seed premises while keeping creative worlds reusable and varied."""
from collections import Counter
def template(row):return str(row.get('canonical_subject','')).startswith('creative-environment-')
def seed_anchor(row):
 source=row.get('source_selection');source=source if isinstance(source,dict) else {}
 value=source.get('canonical_subject')
 return value if value and not template(source) else None
def ordered(rows,history):
 scenarios=[]
 for row in history[-16:]:
  source=row.get('source_selection');source=source if isinstance(source,dict) else {}
  scenario=source.get('scenario')
  if scenario:scenarios.append(scenario)
 counts=Counter(scenarios);last=scenarios[-1] if scenarios else None
 return [r for _,r in sorted(enumerate(rows),key=lambda pair:(template(pair[1]),counts[pair[1].get('scenario')]+(3 if pair[1].get('scenario')==last else 0),pair[0]))]
