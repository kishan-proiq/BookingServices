from pathlib import Path
from typing import List, Optional, Tuple

DEFAULT_LOG_PATH = Path("dummy_logs.log").resolve()

LEVELS = [
	"DEBUG",
	"INFO",
	"WARN",
	"ERROR",
	"CRITICAL",
]

def read_logs(
	path: Optional[str] = None,
	level: Optional[str] = None,
	query: Optional[str] = None,
	offset: int = 0,
	limit: int = 100,
) -> Tuple[List[str], int]:
	"""Read log lines from file with optional level and substring filtering.
	Returns (lines, total_count_before_pagination).
	"""
	log_path = Path(path).resolve() if path else DEFAULT_LOG_PATH
	if not log_path.exists():
		return [], 0

	with log_path.open("r", encoding="utf-8", errors="ignore") as fp:
		all_lines = [line.rstrip("\n") for line in fp]

	# Filter by level if provided (expects pattern like "[INFO]", "[ERROR]")
	filtered = all_lines
	if level:
		lvl = level.strip().upper()
		if lvl not in LEVELS:
			# Unknown level -> empty result for clarity
			return [], 0
		needle = f"[{lvl}]"
		filtered = [ln for ln in filtered if needle in ln]

	if query:
		q = query.lower()
		filtered = [ln for ln in filtered if q in ln.lower()]

	total = len(filtered)
	# Guard rails for pagination
	if offset < 0:
		offset = 0
	if limit <= 0:
		limit = 100

	return filtered[offset : offset + limit], total
