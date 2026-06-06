import subprocess
import sys
from pathlib import Path


def test_typescript_export_generates_file() -> None:
    schemas_root = Path(__file__).resolve().parents[3] / "packages" / "schemas"
    script = schemas_root / "scripts" / "export_typescript.py"
    out = schemas_root / "generated" / "types.ts"

    subprocess.run(
        [sys.executable, str(script)],
        check=True,
        cwd=str(schemas_root),
    )
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "export type RunStatus" in content
    assert "export type JobTargetStatus" in content
