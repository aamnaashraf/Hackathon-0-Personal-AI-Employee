import time
import json
from pathlib import Path

# Test the orchestrator logic manually
vault_path = Path("E:/hackathon 0/Hackathon-0-FTE-s-/AI_Employee_Vault")

watcher_dirs = [
    vault_path / 'Watchers' / 'Gmail',
    vault_path / 'Watchers' / 'WhatsApp',
    vault_path / 'Watchers' / 'LinkedIn',
    vault_path / 'Watchers' / 'File_System',
    vault_path / 'Drop_Folder'
]

all_items = []
for watcher_dir in watcher_dirs:
    if watcher_dir.exists():
        items = list(watcher_dir.glob('*.md'))
        all_items.extend(items)
        print(f"Found {len(items)} items in {watcher_dir}")

print(f"\nTotal items found: {len(all_items)}")
for item in all_items:
    print(f"  - {item} (parent: {item.parent.name})")

# Check which items would be moved
needs_action = vault_path / 'Needs_Action'
needs_action.mkdir(exist_ok=True)

for item in all_items:
    if item.parent.name not in ['Needs_Action', 'Done', 'Approved', 'Rejected', 'Pending_Approval']:
        print(f"\nWOULD MOVE: {item.name} from {item.parent.name} to Needs_Action")
        target_path = needs_action / item.name
        print(f"  Target: {target_path}")