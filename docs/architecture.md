# Architecture — HL7 / FHIR Interop Lab

Pipeline: synthetic HL7 file → `hl7_parser.adt_from_message` → `fhir_builder.adt_to_fhir_bundle` → JSON on disk → `fhir_to_adt` → `adt_to_hl7` for round-trip comparison. Validation checks structural Bundle requirements only (not full FHIR validator).
