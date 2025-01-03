from shutil import rmtree, make_archive
from pathlib import Path
from et import copy_with_exceptions, read_json
from os import remove
from json import dump

version = read_json('.version.json')
old_version = version.copy()
match input('New version(M, m, P, B): ').strip():
    case 'M':
        version['major'] = version['major'] + 1
    case 'm':
        version['minor'] = version['minor'] + 1
    case 'P':
        version['patch'] = version['patch'] + 1
    case 'B':
        version['build'] = version['build'] + 1

with open('.version.json', 'w') as f:
    dump(version, f, indent=4)

version = f'{version['major']}.{version['minor']}.{version['patch']}-Beta.{version['build']}'
old_version = f'{old_version['major']}.{old_version['minor']}.{old_version['patch']}-Beta.{old_version['build']}'

if Path(f'Snake game {old_version}.zip').exists():
    remove(f'Snake game {old_version}.zip')
copy_with_exceptions('.','archive' , ['__pycache__', '.venv', '.vscode', '.colors.txt', '.save.json', 'packer.py', 'settings.json', 'archive'])
make_archive(f'Snake game {version}', 'zip', root_dir='./archive')
rmtree('archive')

print(f'New version ready for release: {version}')