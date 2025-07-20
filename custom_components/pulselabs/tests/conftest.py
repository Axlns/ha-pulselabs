import sys
from pathlib import Path

# tests/ → pulselabs/ → custom_components/ → config/  (3 уровня вверх)
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))