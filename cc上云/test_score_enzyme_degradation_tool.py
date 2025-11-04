"""
测试 ScoreEnzymeDegradationTool 的基本功能。
"""

from __future__ import annotations

import json

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

module_path = PROJECT_ROOT / "core" / "tools" / "design" / "score_enzyme_degradation_tool.py"
spec = importlib.util.spec_from_file_location("score_enzyme_degradation_tool", module_path)
if spec is None or spec.loader is None:
    raise ImportError(f"未找到模块: {module_path}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

ScoreEnzymeDegradationTool = module.ScoreEnzymeDegradationTool


def main() -> None:
    pollutant = "O=C(C1=CC=CC=C1C(=O)OCCCC)OCCCC"
    sequence = (
        "MTRKNVLLIVVDQWRADFIPHLMRAEGREPFLKTPNLDRLCREGLTFRNHVTTCVPCGPARASLLTGLYLMNHRAVQNT"
        "VPLDQRHLNLGKALRAIGYDPALIGYTTTTPDPRTTSARDPRFTVLGDIMDGFRSVGAFEPNMEGYFGWVAQNGFELPE"
        "NREDIWLPEGEHSVPGATDKPSRIPKEFSDSTFFTERALTYLKGRDGKPFFLHLGYYRPHPPFVASAPYHAMYKAEDMP"
        "APIRAENPDAEAAQHPLMKHYIDHIRRGSFFHGAEGSGATLDEGEIRQMRATYCGLITEIDDCLGRVFAYLDETGQWDD"
        "TLIIFTSDHGEQLGDHHLLGKIGYNAESFRIPLVIKDAGQNRHAGQIEEGFSESIDVMPTILEWLGGETPRACDGRSLL"
        "PFLAEGKPSDWRTELHYEFDFRDVFYDQPQNSVQLSQDDCSLCVIEDENYKYVHFAALPPLFFDLKADPHEFSNLAGDP"
        "AYAALVRDYAQKALSWRLSHADRTLTHYRSSPQGLTTRNH"
    )

    tool = ScoreEnzymeDegradationTool()
    result = tool._run(
        pollutant_smiles=pollutant,
        enzyme_sequences=[sequence],
        reference_kcat=None,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
