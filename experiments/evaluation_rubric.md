# Evaluation

Use the reference review to score all three methods. The same researcher may
prepare the reference and score the outputs; this is reported as a limitation.

## Decisions

Each existing provision receives one label:

- `Supported`: the provision materially supports the stated control;
- `Partially supported`: it supports only part of the statement or depends on
  an unstated condition;
- `Unsupported`: it does not materially support the statement;
- `Unable to determine`: the available context or legal source is insufficient.

Compound mappings must be split before scoring. Article ranges and references to
annexes are reviewed as separate provisions where they express separate legal
requirements.

## Measures

### Existing mapping accuracy

The share of existing provision decisions that match the reference decision.
Report the counts as well as the percentage.

### Missing mapping precision and recall

Use these only when the reference review identifies a reasonably stable set of
material omissions. A long list of remotely relevant articles is not rewarded.

### Evidence errors

Count a citation as an error when the cited location does not exist, cannot be
verified, or does not support the stated reason. Describe the error briefly.

### Unsupported claims

Count material legal or applicability claims that are not supported by the item
or the cited official text. Repeated wording of the same error counts once.

### Time

For Manual, record total review time. For each AI method, record execution time,
human review time and their sum. The main efficiency comparison uses total time
to reach an acceptable review.

## Result table

Keep one row per item and method:

```text
item_id
framework
method
existing_mapping_correct
existing_mapping_total
missing_mapping_true_positive
missing_mapping_proposed
missing_mapping_reference_total
evidence_errors
unsupported_claims
execution_time_min
human_review_time_min
total_time_min
short_note
```

Do not calculate a combined quality score. Applicability handling and challenge
usefulness should first be discussed in short notes; add an ordinal score only
if the pilot shows that it can be applied consistently.
