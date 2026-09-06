# 实验操作指南

## 1. 只需要认识这些文件

```text
experiments/
├── data/
│   ├── items.csv
│   └── pilot_items.csv
├── outputs/
│   ├── manual/
│   ├── llm_only/
│   └── agentic_rag/
└── results/
    └── item_results.csv
```

- `data/items.csv`：三种方法共同使用的 40 条输入。
- `data/pilot_items.csv`：从 40 条中抽出的四条流程检查数据。
- `outputs/manual/`：你以后慢慢填写的人工结果。
- `outputs/`：程序真实产生的 AI 回答。当前 DORA 已完成，AI Act 尚未完成。
- `results/item_results.csv`：最后计算准确率、时间和论文图表的数据表。

## 2. 三种方法

- `Manual`：你查官方法律并填写人工判断。
- `LLM-only`：模型直接判断，不提供 RAG 法律文本。
- `Agentic RAG`：程序先从 Regulatory RAG 检索，再让同一模型判断。

LLM-only 和 Agentic RAG 使用 `.env` 中相同的 `PRIVATE_AI_MODEL`。三种方法检查相同的
输入，并使用相同的条款判断和条目总结字段。

## 3. 环境检查

```bash
cd /Users/dada/Developer/italy_proj/ai-cyber-risk-thesis
conda activate compliance-agent
python -m pip install -r requirements.txt
python -m unittest discover -s agent/tests -v
```

`.env` 不得提交。DORA RAG 工程位于：

```text
/Users/dada/Developer/italy_proj/regulatory-rag
```

## 4. 当前已经完成的内容

20 条 DORA 已经分别运行一次 LLM-only 和 Agentic RAG。正常查看时只打开：

```text
experiments/outputs/llm_only/provision_checks.csv
experiments/outputs/llm_only/item_summary.csv
experiments/outputs/agentic_rag/provision_checks.csv
experiments/outputs/agentic_rag/item_summary.csv
```

每条的原始回答、参数和 RAG 证据在相应的 `records/` 中。不要手工修改原始回答。

`experiments/results/item_results.csv` 已经写入 DORA AI 运行的实际执行时间和实际提出的遗漏数量。
需要人工判断才能确定的准确率、证据错误、无依据声明和人工修正时间保持为空。

## 5. Manual 怎么做

你不需要一次完成，可以每次做几条。使用：

```text
experiments/outputs/manual/provision_checks.csv
experiments/outputs/manual/item_summary.csv
experiments/outputs/manual/timing.csv
```

每条的操作：

1. 在 `timing.csv` 记录开始时间。
2. 只查官方法律文本，不打开该条对应的 AI 输出。
3. 在 `provision_checks.csv` 判断每个现有条款是 `Supported`、
   `Partially supported`、`Unsupported` 或 `Unable to determine`。
4. 填写简短原因、官方来源和支持段落。
5. 在 `item_summary.csv` 填写总体判断和真正重要的遗漏条款。
6. 在 `timing.csv` 填写结束时间和总分钟数。

Manual 可以晚于 AI 程序运行。关键不是运行顺序，而是人工核验时不要参考对应 AI 答案。

## 6. 唯一尚缺的工程部分：AI Act RAG

不要修改现有 DORA corpus。需要在独立 RAG 工程中加入官方英文 Regulation (EU)
2024/1689，并建立包含 DORA 和 AI Act 的论文 profile。

建议标识：

```text
document_id: EU-2024-1689
CELEX: 32024R1689
ELI: http://data.europa.eu/eli/reg/2024/1689/oj
parser_profile: eurlex_oj_html
```

官方入口：`https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng`。

在 Regulatory RAG 工程中：

1. 下载并核对 EUR-Lex Official Journal 英文 PDF。
2. 运行 `inventory_regulatory_corpus.py`，保存页数和 SHA-256。
3. 在 documents catalog 中添加 AI Act 文档记录。
4. 复制 DORA profile，建立 DORA + AI Act 的组合 profile。
5. 运行 corpus validation、HTML/PDF 构建和 vector index 构建。
6. 人工抽查 Articles 5、9–15、17、19–20、25–27、72–73。
7. 在本工程 `.env` 设置：

```text
REGULATORY_RAG_PROFILE=/absolute/path/to/thesis-dora-ai-act-en.json
```

该工程不能由这里直接修改；完成后再运行 AI Act 的两种方法。

## 7. 补齐 AI Act 输出

LLM-only：

```bash
python -m agent.batch \
  --method llm-only \
  --input experiments/data/items.csv \
  --framework "EU AI Act" \
  --output experiments/outputs/llm_only \
  --resume
```

Agentic RAG：

```bash
python -m agent.batch \
  --method agentic-rag \
  --input experiments/data/items.csv \
  --framework "EU AI Act" \
  --output experiments/outputs/agentic_rag \
  --resume
```

完成后把客观运行数据同步到评分表：

```bash
python scripts/update_results.py
```

`--resume` 只跳过已有完整记录的条目，因此不会重新调用已经完成的 DORA。

## 8. 最后评分

以核验后的 Manual 为参考，在 `experiments/results/item_results.csv` 补充：

- AI 条款判断与 Manual 相同的数量；
- 遗漏条款的 true positive 和 Manual 参考总数；
- 证据错误和无依据声明数量；
- 人工修正时间；
- 总时间和必要的简短说明。

空白表示尚未测量；`0` 表示已经检查且实际为零。不要用 `0` 代表缺失数据。如果后来
修正 Manual 判断，要对两种 AI 方法重新评分，但不需要重新调用模型。

## 9. 论文表格和图表

当前三张论文表格框架在 `thesis_outputs/tables/`。数据完整后运行：

```bash
python scripts/build_thesis_outputs.py
```

程序将在 `thesis_outputs/generated/` 生成 3 张结果表和 6 张 SVG 图。图的数值全部来自
`experiments/results/item_results.csv`。可以自己重画样式，但不要手工修改图中的数据。

## 10. 最后检查

- [x] 20 条 DORA 的 LLM-only 已运行。
- [x] 20 条 DORA 的 Agentic RAG 已运行并保存证据。
- [x] 120 行评分表已建立并写入现有客观数据。
- [x] Manual 工作表已建立。
- [ ] AI Act 已加入 RAG。
- [ ] 20 条 AI Act 的两种 AI 方法已运行。
- [ ] Manual 和人工修正时间已填写。
- [ ] 最终评分、论文表格和图表已生成。
