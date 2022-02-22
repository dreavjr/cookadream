import os
from pathlib import Path

root = str(Path(__file__).parent.resolve()) + '/macOS/app/Cook-a-Dream/Cook-a-Dream.app/Contents/Resources/app_packages'

dependencies = set()

with open('cookadream_profile_stats.txt', 'rt', encoding='utf-8') as stats_file:
    stats = stats_file.readlines()
    stats = stats[7:]
    for s in stats:
        try:
            path = s[46:].split(':')[0]
        except IndexError:
            break
        if not path.strip():
            continue
        if path[0] != '/':
            continue
        path = Path(path)
        if not path.is_dir():
            path = path.parent
        relative = os.path.relpath(path, start=root)
        if relative.startswith('..'):
            continue
        dependencies.add(relative)

dependencies = sorted(dependencies)
for d in dependencies:
    print(d)

