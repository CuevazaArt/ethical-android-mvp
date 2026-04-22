import os
import glob
import re
from refactor_modules import DOMAINS, get_target_domain

file_map = {}
for domain, files in DOMAINS.items():
    for f in files:
        file_map[f] = domain

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))

for pyfile in glob.glob(os.path.join(REPO_ROOT, 'src/modules/**/*.py'), recursive=True):
    with open(pyfile, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content
    def replacer(match):
        mod = match.group(1)
        domain = get_target_domain(mod)
        if domain:
            return f'from src.modules.{domain}.{mod} import'
        print(f'Unmapped relative import: {mod} in {pyfile}')
        return match.group(0)
    new_content = re.sub(r'^from \.([a-zA-Z0-9_]+) import', replacer, new_content, flags=re.MULTILINE)
    if new_content != content:
        with open(pyfile, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {pyfile}')
