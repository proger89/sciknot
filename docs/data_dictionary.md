# Data Dictionary

## `experiments_seed.csv`

- `experiment_id` - stable fact row id.
- `material` - canonical object such as `Комсомольский рудный массив`.
- `process` - measurement, modeling, forecast, or planning activity.
- `property_name` - measured or assessed property.
- `value` - normalized value or `missing`.
- `trend` - `increase`, `stable`, `unknown`, etc.
- `source_document_id` - stable document id from `documents_seed.csv`.
- `source_quote` - short quote/title fragment used as evidence.
- `confidence` - 0..1 confidence for the curated fact.

## Answer bundle

The UI displays `summary`, `experiment_rows`, `evidence`, `gaps`, `confidence`, `data_insufficient`, and a bounded `subgraph`.

