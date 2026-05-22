import sys
sys.path.insert(0, '/home/ubuntu/tutor-miniprogram/backend')
from app.models import Base

tables = sorted(Base.metadata.tables.keys())
print(f"All models OK: {len(tables)} tables")
for t in tables:
    print(f"  - {t}")
