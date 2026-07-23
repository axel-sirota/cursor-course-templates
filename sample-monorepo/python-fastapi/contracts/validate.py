"""
Contract validator for the sample monorepo.

Must run on stock python3 with zero pip installs (corporate lab machines),
so it does NOT import jsonschema. It implements exactly the subset the
contract schemas use: required fields, primitive types (string/number/object),
enum membership, and numeric minimum.

Usage: python3 contracts/validate.py <service-dir>
"""
import json
import sys
from pathlib import Path

CONTRACTS_DIR = Path(__file__).resolve().parent

TYPE_CHECKS = {
    "string": lambda value: isinstance(value, str),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "object": lambda value: isinstance(value, dict),
}


def schema_for(stem):
    """Map a fixture filename stem to (schema filename, definition name)."""
    if stem.startswith("payment_"):
        return "payment.schema.json", None
    if stem == "refund_request" or stem.startswith("refund_request_"):
        return "refund.schema.json", "RefundRequest"
    if stem == "refund_result" or stem.startswith("refund_result_"):
        return "refund.schema.json", "RefundResult"
    if stem.startswith("notification_"):
        return "notification.schema.json", None
    return None, None


def load_schema(name, definition):
    schema = json.loads((CONTRACTS_DIR / name).read_text())
    if definition is not None:
        schema = schema["definitions"][definition]
    return schema


def validate(instance, schema):
    """Return a list of violation messages; empty means the instance passes."""
    if not isinstance(instance, dict):
        return ["document is not an object"]

    errors = []
    for field in schema.get("required", []):
        if field not in instance:
            errors.append('field "%s" is required but missing' % field)

    for field, rules in schema.get("properties", {}).items():
        if field not in instance:
            continue
        value = instance[field]

        expected = rules.get("type")
        if expected in TYPE_CHECKS and not TYPE_CHECKS[expected](value):
            errors.append(
                'field "%s" value %s is not of type %s'
                % (field, json.dumps(value), expected)
            )
            continue

        if "enum" in rules and value not in rules["enum"]:
            errors.append(
                'field "%s" value "%s" not in enum [%s]'
                % (field, value, ", ".join(str(item) for item in rules["enum"]))
            )

        if "minimum" in rules and value < rules["minimum"]:
            errors.append(
                'field "%s" value %s is below minimum %s'
                % (field, value, rules["minimum"])
            )

    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: python3 validate.py <service-dir>", file=sys.stderr)
        return 2

    service_dir = Path(argv[1])
    fixtures_dir = service_dir / "fixtures"
    if not fixtures_dir.is_dir():
        print("FAIL %s: no fixtures/ directory found." % service_dir)
        return 1

    fixtures = sorted(fixtures_dir.glob("*.json"))
    if not fixtures:
        print("FAIL %s: no .json fixtures found." % fixtures_dir)
        return 1

    failed = False
    for fixture in fixtures:
        rel = fixture.relative_to(service_dir)
        schema_name, definition = schema_for(fixture.stem)
        if schema_name is None:
            print("SKIP %s: no schema matches this fixture name." % rel)
            continue

        try:
            instance = json.loads(fixture.read_text())
        except ValueError as exc:
            print("FAIL %s: invalid JSON (%s)." % (rel, exc))
            failed = True
            continue

        errors = validate(instance, load_schema(schema_name, definition))
        if errors:
            failed = True
            for error in errors:
                print("FAIL %s: %s." % (rel, error))
        else:
            print("PASS %s" % rel)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
