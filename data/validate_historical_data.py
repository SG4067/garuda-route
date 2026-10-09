"""Validate normalized historical data and confirm CSV/JSON parity."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from openpyxl import load_workbook

from process_workbook import (
    DEFAULT_WORKBOOK,
    FIELDS,
    VERIFIED_SOURCE_CHECKS,
    normalize_duration,
    source_text,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "processed" / "historical_waterlogging.csv"
JSON_PATH = ROOT / "data" / "processed" / "historical_waterlogging.json"
SCHEMA_PATH = ROOT / "data" / "schemas" / "historical_waterlogging.schema.json"
SAMPLE_PATH = ROOT / "data" / "sample" / "sample_roads.json"

NUMBER_FIELDS = {
    "latitude", "longitude", "rainfall_amount_mm", "rainfall_duration_minutes",
    "rainfall_intensity_mm_hr", "confidence",
}
INTEGER_FIELDS = {"source_excel_row"}
BOOLEAN_FIELDS = {"rainfall_is_road_specific", "is_priority_location"}
ARRAY_FIELDS = {"review_flags"}
NULLABLE_FIELDS = {
    "road_id", "road_name", "location_name", "latitude", "longitude",
    "event_date", "event_date_start", "event_date_end", "rainfall_amount_mm",
    "rainfall_duration_minutes", "rainfall_intensity_mm_hr", "severity", "description", "confidence",
}


def fail(message: str) -> None:
    raise SystemExit(f"VALIDATION FAILED: {message}")


def parse_csv_cell(field: str, value: str):
    if field in ARRAY_FIELDS:
        return json.loads(value)
    if field in BOOLEAN_FIELDS:
        if value not in {"true", "false"}:
            fail(f"invalid boolean in CSV {field}: {value!r}")
        return value == "true"
    if field in INTEGER_FIELDS:
        return int(value)
    if field in NUMBER_FIELDS:
        return None if value == "" else float(value)
    if field == "source_rainfall_amount_raw":
        if value == "":
            return None
        if value.strip().upper() == "UNKNOWN":
            return value
        try:
            number = float(value)
            return int(number) if number.is_integer() else number
        except ValueError:
            return value
    if field in NULLABLE_FIELDS and value == "":
        return None
    return value


def check_source_preservation(records: list[dict]) -> None:
    book = load_workbook(DEFAULT_WORKBOOK, read_only=True, data_only=True)
    sheet = book["Citywide incidents"]
    for record in records:
        row_number = record["source_excel_row"]
        source = [cell.value for cell in sheet[row_number]]
        source_values = {
            "source_city_raw": source[0],
            "source_location_raw": source[1],
            "source_event_date_raw": source[2],
            "source_rainfall_amount_raw": source[3],
            "source_rainfall_scope_raw": source[4],
            "source_duration_raw": source[5],
            "source_severity_context_raw": source[6],
            "source_evidence_note_raw": source[7],
            "source_priority_label_raw": source[8],
            "source_url": source[9],
        }
        for field, original in source_values.items():
            actual = record[field]
            if isinstance(original, float) and isinstance(actual, (float, int)):
                if float(original) != float(actual):
                    fail(f"source value changed at row {row_number}, field {field}")
            elif source_text(original) != source_text(actual):
                fail(f"source value changed at row {row_number}, field {field}")

        original_rain = source[3]
        if not isinstance(original_rain, (int, float)) or isinstance(original_rain, bool):
            if record["rainfall_amount_mm"] is not None:
                fail(f"unknown/non-numeric rainfall became a number at source row {row_number}")
        elif record["rainfall_amount_mm"] != original_rain:
            fail(f"rainfall amount differs from source at row {row_number}")

        expected_duration, _ = normalize_duration(source_text(source[5]))
        if "1953011-2022-05-23" in record["source_url"]:
            # Direct article review found no rainfall duration; preserve the
            # source workbook wording, but do not normalize it as evidence.
            expected_duration = None
        if record["rainfall_duration_minutes"] != expected_duration:
            fail(f"duration normalization differs from rule at source row {row_number}")
    book.close()


def main() -> None:
    csv_rows: list[dict] = []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            fail("CSV column names/order do not match the normalizer contract")
        csv_rows = [{field: parse_csv_cell(field, row[field]) for field in FIELDS} for row in reader]

    with JSON_PATH.open(encoding="utf-8") as stream:
        records = json.load(stream)
    if not isinstance(records, list):
        fail("historical JSON root must be an array")
    if len(csv_rows) != len(records):
        fail(f"CSV has {len(csv_rows)} rows but JSON has {len(records)} records")
    if csv_rows != records:
        for index, (csv_record, json_record) in enumerate(zip(csv_rows, records), start=1):
            if csv_record != json_record:
                fail(f"CSV/JSON mismatch at record {index}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = [error for record in records for error in validator.iter_errors(record)]
    if schema_errors:
        fail("schema error: " + "; ".join(f"{e.json_path}: {e.message}" for e in schema_errors[:10]))

    record_ids = [record["record_id"] for record in records]
    if len(record_ids) != len(set(record_ids)):
        fail("record_id values are not unique")
    for record in records:
        expected_status = "VERIFIED" if record["record_id"] in VERIFIED_SOURCE_CHECKS else "REQUIRES_REVIEW"
        if record["evidence_status"] != expected_status:
            fail(f"unexpected evidence status for {record['record_id']}")
        latitude, longitude = record["latitude"], record["longitude"]
        if (latitude is None) != (longitude is None):
            fail(f"only one coordinate is present in {record['record_id']}")
        for field in ("rainfall_amount_mm", "rainfall_duration_minutes", "rainfall_intensity_mm_hr"):
            value = record[field]
            if value is not None and value < 0:
                fail(f"negative {field} in {record['record_id']}")
        if not record["source_url"] or not record["source_name"] or not record["source_record_id"]:
            fail(f"source provenance missing in {record['record_id']}")
        if record["rainfall_is_road_specific"]:
            fail(f"workbook rainfall was incorrectly assigned to a road in {record['record_id']}")
        if record["threshold_status"] != "UNKNOWN" or record["threshold_assessment"] != "INSUFFICIENT EVIDENCE FOR THRESHOLD":
            fail(f"unsupported threshold status in {record['record_id']}")

    check_source_preservation(records)

    exact_keys = [(r["city"], r["event_date_raw"], r["location_name"], r["source_url"]) for r in records]
    if len(exact_keys) != len(set(exact_keys)):
        fail("duplicate full source records found; investigate before removing")
    overlap = defaultdict(list)
    for record in records:
        overlap[(record["city"], record["event_date_raw"], record["location_name"])].append(record)
    overlap_groups = [rows for rows in overlap.values() if len(rows) > 1]
    if any(not all("OVERLAPPING_SOURCE_REPORTS_SAME_LOCATION_DATE" in row["review_flags"] for row in group) for group in overlap_groups):
        fail("overlapping location/date records were not flagged")

    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    if sample.get("data_classification") != "SYNTHETIC_TEST_DATA" or not sample.get("roads"):
        fail("sample records are not clearly labelled and separated")
    historical_ids = {record["road_id"] for record in records if record["road_id"]}
    for road in sample["roads"]:
        if road["road_id"] in historical_ids:
            fail("sample road ID overlaps historical records")
        if road["threshold_minutes"] is not None or road["threshold_status"] != "UNKNOWN":
            fail("sample file contains an unsupported numeric threshold")

    city_counts = Counter(record["city"] for record in records)
    rainfall_count = sum(record["rainfall_amount_mm"] is not None for record in records)
    duration_count = sum(record["rainfall_duration_minutes"] is not None for record in records)
    event_count = len({record["event_id"] for record in records})
    duration_event_count = len({record["event_id"] for record in records if record["rainfall_duration_minutes"] is not None})
    unique_locations = len({(record["city"], (record["location_name"] or "").casefold()) for record in records})
    print(json.dumps({
        "result": "PASS",
        "csv_records": len(csv_rows),
        "json_records": len(records),
        "schema_valid_records": len(records),
        "unique_record_ids": len(set(record_ids)),
        "event_groups": event_count,
        "unique_city_location_pairs": unique_locations,
        "rows_by_city": dict(city_counts),
        "rows_with_contextual_rainfall_amount": rainfall_count,
        "rows_with_normalized_duration": duration_count,
        "event_groups_with_normalized_duration": duration_event_count,
        "rows_with_event_context_severity_text": sum(record["severity"] is not None for record in records),
        "rows_with_standardized_road_specific_severity": sum(record["severity_scope"] == "LOCATION_SPECIFIC" for record in records),
        "rows_with_road_specific_rainfall": sum(record["rainfall_is_road_specific"] for record in records),
        "rows_with_numeric_rainfall_intensity": sum(record["rainfall_intensity_mm_hr"] is not None for record in records),
        "rows_with_source_provenance": len(records),
        "verified_event_location_claims": sum(record["evidence_status"] == "VERIFIED" for record in records),
        "records_requiring_review": sum(record["evidence_status"] == "REQUIRES_REVIEW" for record in records),
        "exact_duplicate_records": 0,
        "overlapping_location_date_groups_retained": len(overlap_groups),
        "sample_data_separate_and_unthresholded": True,
        "threshold_eligible_records": 0,
        "coordinate_pairs_present": sum(record["latitude"] is not None for record in records),
    }, indent=2))


if __name__ == "__main__":
    main()
