# One ADT^A01 From Pipe Text to Warehouse Row

Faiz Elahi - https://www.linkedin.com/in/faizilahi - https://pendataco.com - https://github.com/faizilahi

Portfolio interop walkthrough. Synthetic HL7v2 and FHIR R4 only. This is the closest fit in the set to a real-time health-data foundation pattern (streaming ADT ingest into a durable encounter row) without inventing an employer story.

## The message on the wire

```
MSH|^~\&|EPIC|HOSP|DEST|HOSP|20241112014500||ADT^A01|MSG00042|P|2.5
EVN|A01|20241112014500
PID|1||MRN77821^^^HOSP^MR||DOE^JANE^A||19840312|F|||123 MAIN ST^^BOSTON^MA^02108
PV1|1|I|ICU^201^1^HOSP||||ATTENDING^SMITH^ALAN^^^^^^^^^NPI|REF^LEE^SUE|||||||ENC-44021|||||||||||||||||||||||||20241112014500
```

## Segment map

| Segment | What we keep |
|---------|----------------|
| MSH | message type, timestamp, control id `MSG00042` |
| EVN | event `A01`, recorded time |
| PID | MRN `MRN77821`, name, DOB, sex |
| PV1 | patient class I, location ICU^201, encounter `ENC-44021`, admit dt |

## Parser path

`src/hl7_parse.py` splits on `\r` / `\n`, then fields on `|`, components on `^`. No external HL7 library - the point is to own the field offsets you will defend in code review.

## FHIR Patient + Encounter

The same ADT lands as FHIR R4 `Patient` and `Encounter` resources in `src/fhir_map.py`, then flattens to warehouse columns in `src/warehouse_row.py`.

## Run the walk

```bash
pip install -r requirements.txt
python scripts/generate_adt_batch.py
python scripts/run_adt_walk.py
pytest -q
```

The runner prints the warehouse row for `MSG00042` and batch load counts. Rows are synthetic and small enough for git.

---

Faiz Elahi - [LinkedIn](https://www.linkedin.com/in/faizilahi) - [pendataco.com](https://pendataco.com) - [GitHub](https://github.com/faizilahi)

