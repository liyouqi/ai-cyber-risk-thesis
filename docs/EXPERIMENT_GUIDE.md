# 实验操作指南

## 文件

```text
experiments/
├── data/
│   ├── items.csv
│   └── gold_standard.csv
├── outputs/
│   ├── manual/
│   ├── llm_only/
│   └── agentic_rag_http/
└── results/
    └── item_results.csv
```

- `items.csv`：三种方法共同使用的 40 条输入。
- `gold_standard.csv`：独立专家 Gold，只由最后评分脚本读取。
- 每个方法的 `item_summary.csv`：40 个 item-level 回答。
- `item_results.csv`：根据 Gold 计算出的 120 行结果。

## 统一任务

每种方法判断现有 mapping 作为整体是否充分覆盖 control，只输出 `Yes`
或 `No`。无法确认充分覆盖时输出 `No`。如果存在能实质修复缺口的重要
条款，同时记录 missing mapping；没有明确条款时保持为空。

## Manual

Manual 只填写：

```text
experiments/outputs/manual/item_summary.csv
```

表中只保留四列：`item_id`、`coverage`、`missing_mapping`，以及事后估算
的 `time_min`。没有同期保存的人工定性笔记，因此不报告
review note，也不要求人工填写 AI 输出里的 evidence excerpt、
applicability note 或 challenge comment。

Manual 不打开 Gold 或 AI 输出。`missing_mapping` 使用分号分隔的
`document_id::provision`，例如：

```text
EU-2022-2554::Article 11(6)(b)
```

只有人工记录明确指出能修复缺口的具体条款时才填写；仅判断覆盖不足但
没有明确补充条款时保持为空。

## AI 运行

`.env` 配置 LLM 和 Regulatory RAG：

```text
REGULATORY_RAG_API_URL=http://127.0.0.1:8080
REGULATORY_RAG_MODE=hybrid
REGULATORY_RAG_TOP_K=8
```

LLM-only：

```bash
python -m agent.batch \
  --method llm-only \
  --input experiments/data/items.csv \
  --output experiments/outputs/llm_only
```

Agentic RAG：

```bash
python -m agent.batch \
  --method agentic-rag \
  --input experiments/data/items.csv \
  --output experiments/outputs/agentic_rag_http
```

Agentic RAG 对现有引用使用 Direct，对缺失条款搜索使用 Planned。论文工程
只调用 RAG 的 HTTP API，不 import RAG 包，也不读取其数据或索引目录。

## 评分与图表

先建立空结果表：

```bash
python scripts/prepare_result_table.py
```

三种方法完成后评分：

```bash
python scripts/update_results.py
```

评分后生成论文表格与图表：

```bash
python scripts/build_thesis_outputs.py
```

旧 prompt 或旧评价标准产生的输出不能与本轮结果混合。
