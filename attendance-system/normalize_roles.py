import json

# Load members
with open('data/members.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Normalize roles
role_mapping = {
    'yuvak': 'Yuvak',
    'Yuvak': 'Yuvak',
    'sampark karyakar': 'Sampark Karyakar',
    'Sampark Karyakar': 'Sampark Karyakar',
    'karyakar': 'Karyakar',
    'Karyakar': 'Karyakar',
    'sanchalak': 'Sanchalak',
    'Sanchalak': 'Sanchalak',
    'sampark': 'Sampark',
    'Sampark': 'Sampark'
}

normalized_count = 0
for name, member in members.items():
    current_type = str(member.get('Type', '')).strip()
    if current_type in role_mapping:
        new_type = role_mapping[current_type]
        if member.get('Type') != new_type:
            member['Type'] = new_type
            normalized_count += 1

# Save normalized members
with open('data/members.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, indent=2, ensure_ascii=False)

print(f'✓ Normalized {normalized_count} member roles')
