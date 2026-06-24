import os

base = r'c:\Users\adity\Desktop\Finanacial Intelligence platform'

all_files = [os.path.join(base, 'Dashboard_Overview.py')]
for rel in os.listdir(os.path.join(base, 'pages')):
    if rel.endswith('.py'):
        all_files.append(os.path.join(base, 'pages', rel))

for p in all_files:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content.replace("use_container_width=True", "width='stretch'")
    new_content = new_content.replace("use_container_width=False", "width='content'")
    if new_content != content:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Fixed:', os.path.basename(p))
    else:
        print('No change:', os.path.basename(p))
