import json
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent
REPO_ROOT = SEED_DIR.parents[2]
PACKAGE_PATH = SEED_DIR / "package.json"
DATASET_PATH = SEED_DIR / "thinking.jsonl"
SCHEMA_PATH = REPO_ROOT / "00_contract" / "schema_v6.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_design_package():
    package = load_json(PACKAGE_PATH)
    bp = package["schema_v6_blueprint"]

    require(package["target"]["vehicle_id"] == "arm_6dof", "target vehicle must be arm_6dof")
    require(package["primary_metric"]["name"] == "assembly_serviceability_efficiency", "primary metric mismatch")
    require(len(package["existing_bom"]) >= 9, "existing BOM must contain at least 9 groups")
    require(len(package["redesigned_bom"]) >= 5, "redesigned BOM must contain at least 5 groups")
    require(package["assembly_delta"]["redesigned_steps"] < package["assembly_delta"]["baseline_steps"], "assembly steps must be reduced")
    require(len(package["assembly_delta"]["retained_service_access_points"]) >= 6, "at least 6 service access points required")

    print_part_ids = {item["part_id"] for item in package["print_strategy"]}
    redesigned_ids = {item["id"] for item in package["redesigned_bom"]}
    require(redesigned_ids.issubset(print_part_ids), "every redesigned BOM group needs print strategy")

    verify_text = " ".join(v["check"] for v in bp["verify"]).lower()
    for keyword in ["j1-j6", "cable", "tool flange", "joint cartridge"]:
        require(keyword in verify_text, f"verify must include {keyword} access/check")

    risk_text = " ".join(r["desc"] for r in bp["risk"]).lower()
    require("over-integration" in risk_text, "over-integration risk required")
    require("axis alignment" in risk_text, "axis alignment risk required")

    required_bp_fields = load_json(SCHEMA_PATH)["required"]
    for field in required_bp_fields:
        require(field in bp, f"schema_v6 blueprint missing field: {field}")

    require(bp["version"] == "bp-npu-r6", "schema_v6 blueprint version mismatch")
    require(bp["brief"]["constraints"]["process"] == "FDM", "process must be FDM")
    require(len(bp["geometry_ops"]) >= 12, "geometry_ops should contain later-STL intent")
    return package


def validate_dataset():
    rows = []
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            rows.append(row)
            require(row["schema"] == "blueprint_design_thinking_example_v1", f"line {line_no}: schema mismatch")
            require(row["target"] == "arm_6dof", f"line {line_no}: target mismatch")
            require(row["metric"] == "assembly_serviceability_efficiency", f"line {line_no}: metric mismatch")
            require("existing_structure" in row["input"], f"line {line_no}: missing existing_structure")
            require("classification" in row["reasoning"], f"line {line_no}: missing reasoning classification")
            require("proposal" in row["output"], f"line {line_no}: missing output proposal")
            require("verification" in row["output"], f"line {line_no}: missing output verification")

    require(20 <= len(rows) <= 110, f"dataset should contain 20-110 examples, found {len(rows)}")
    classes = {row["reasoning"]["classification"] for row in rows}
    require("fail_over_integration" in classes, "dataset must include over-integration failure examples")
    require("integrate_with_guardrail" in classes, "dataset must include guarded integration examples")

    dataset_text = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows).lower()
    for keyword in ["j1", "j2", "j3", "j5", "j6", "cable", "tool", "axis"]:
        require(keyword in dataset_text, f"dataset must cover {keyword}")
    return rows


def main():
    package = validate_design_package()
    rows = validate_dataset()
    print("Robot arm redesign V1 validation OK")
    print(f"- existing BOM groups: {len(package['existing_bom'])}")
    print(f"- redesigned BOM groups: {len(package['redesigned_bom'])}")
    print(f"- assembly steps: {package['assembly_delta']['baseline_steps']} -> {package['assembly_delta']['redesigned_steps']}")
    print(f"- service access points: {len(package['assembly_delta']['retained_service_access_points'])}")
    print(f"- design-thinking examples: {len(rows)}")


if __name__ == "__main__":
    main()

