# Experiment Run Templates

每个 Case、每种方法保存两份文件：

- `run.md`：实验日志。记录输入、时间、模型、原始输出、检索证据和人工修改。
- `assessment_output.md`：最终评估文本。记录该方法最后交付的风险评估，适合后续统一评分和写论文。

不要用人工修改后的文字覆盖原始模型输出。原始输出必须保留，修改后的版本写入 `assessment_output.md`。

Recommended structure:

```text
experiments/
├── 01_manual/
│   └── case_01/
│       ├── run.md
│       └── assessment_output.md
├── 02_llm_only/
│   └── case_01/
│       ├── run.md
│       └── assessment_output.md
└── 03_agentic_rag/
    └── case_01/
        ├── run.md
        └── assessment_output.md
```

Use:

- `01_manual_run_template.md` for Manual
- `02_llm_only_run_template.md` for LLM-only
- `03_agentic_rag_run_template.md` for Agentic RAG

These records are experiment logs. They are not intended to be copied verbatim into the thesis.

## Recommended order after finishing one assessment

1. 先复制对应的 `run` 模板，并填写时间、输入、原始结果和过程记录。
2. 将最终可接受的版本复制到 `assessment_output.md`；Manual 可以直接整理自己的评估，LLM-only 和 Agentic RAG 必须以人工审核后的版本为准。
3. 对照 `experiments/evaluation_rubric.md` 评分，并在 `run.md` 的 Post-Run Evaluation 中填写分数和理由。
4. 如果修改了原始结果，在 `run.md` 中写明改了什么以及为什么改。

## Result templates

After all three workflows for one case are complete, copy:

- `experiments/results/per_case_result_template.md` for the written comparison;
- `experiments/results/overall_results_template.csv` for the final dataset.

Scores are assigned to the initial assessment output. The reviewed output is
kept to show the correction effort and the final usable assessment.

For the first run, follow `experiments/HOW_TO_RUN_CASE_01.md`. CASE-01 working
files are already prepared in the three workflow folders.
