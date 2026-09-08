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
- `outputs/`：程序真实产生的 AI 回答。已有 DORA 结果是旧的嵌入式 RAG 运行记录。
- `results/item_results.csv`：最后计算准确率、时间和论文图表的数据表。

## 2. 三种方法

- `Manual`：你查官方法律并填写人工判断。
- `LLM-only`：模型直接判断，不提供 RAG 法律文本。
- `Agentic RAG`：程序先从 Regulatory RAG 检索，再让同一模型判断。

LLM-only 和 Agentic RAG 使用 `.env` 中相同的 `PRIVATE_AI_MODEL`。三种方法检查相同的
输入，并使用相同的条款判断和条目总结字段。

## 3. 环境检查

```bash
cd /Users/moni/Developer/ai-cyber-risk-thesis
conda activate compliance-agent
python -m pip install -r requirements.txt
python -m unittest discover -s agent/tests -v
```

`.env` 不得提交。Agentic RAG 只通过只读 HTTP API 访问 Regulatory RAG：

```text
REGULATORY_RAG_API_URL=http://127.0.0.1:8080
REGULATORY_RAG_API_KEY=仅在服务要求 Bearer 认证时填写
REGULATORY_RAG_MODE=hybrid
REGULATORY_RAG_TOP_K=8
```

可以复制仓库中的 `.env.example` 后填写；不要把真实密钥提交到 Git。

论文工程不得 import `regulatory_rag`，也不得读取 RAG 工程的 data、release 或 indexes。
程序启动时会检查 `GET /health` 和 `GET /api/v1/status`；任一检查失败即停止。

## 4. 当前已经完成的内容

20 条 DORA 已经分别运行一次 LLM-only 和旧版嵌入式 Agentic RAG。正常查看时只打开：

```text
experiments/outputs/llm_only/provision_checks.csv
experiments/outputs/llm_only/item_summary.csv
experiments/outputs/agentic_rag/provision_checks.csv
experiments/outputs/agentic_rag/item_summary.csv
```

每条的原始回答、参数和 RAG 证据在相应的 `records/` 中。不要手工修改原始回答。
正式 HTTP 实验不要在旧目录中使用 `--resume`，否则会静默混合两种 provider。应使用新的
输出目录完整运行 40 条 Agentic RAG，验收后再决定是否归档旧目录。

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
   `Partially supported`、`Unsupported` 或 `Unable to determine`，并使用
   `EXPERIMENT_DESIGN.md` 中的统一判定边界。
4. 填写简短原因、官方来源和支持段落。
5. 在 `item_summary.csv` 填写总体判断和真正重要的遗漏条款。
6. 在 `timing.csv` 填写结束时间和总分钟数。

Manual 可以晚于 AI 程序运行。关键不是运行顺序，而是人工核验时不要参考对应 AI 答案。

## 6. Regulatory RAG HTTP 边界

本工程保留的 `experiments/data/ai_act_legal_text.json` 只是早期流程准备数据，不再作为
正式或临时检索后端。论文工程不实现 BM25、Vector、RRF、Parser 或法规切片。

每个现有条款验证调用：

```text
POST /api/v1/retrieve
query_mode=direct
query=规范法规引用，例如 AI Act Article 9
timeout=30 seconds
```

Direct 是 API 查询模式，不是绕过 Parser。规范引用由 Regulatory RAG 自己的法规引用
Parser 解析；控制陈述不会混入这条定位查询，而是在随后由模型结合返回证据进行判断。

每个条目的遗漏条款检索调用：

```text
POST /api/v1/retrieve
query_mode=planned
timeout=120 seconds
```

AI Act 请求固定 scope 为 framework `ai_act`、document ID `EU-2024-1689`；DORA 请求按
每条 mapping 的 instrument 固定 document ID。空结果记录为 `empty`，不会扩大 scope。
服务错误、Planner 不可用或非 JSON 响应会明确终止运行。返回的 evidence ID、document ID、
正文、条款位置、官方 URL、rank、score，以及 Planned 的 plan 和逐 claim coverage 都写入
运行记录。

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
  --output experiments/outputs/agentic_rag_http
```

这条命令对 40 条输入使用同一个 HTTP provider。若只做 AI Act 流程检查，可以临时添加
`--framework "EU AI Act"`，但最终比较应在新的输出目录运行全部 40 条。

完成后把客观运行数据同步到评分表：

```bash
python scripts/update_results.py \
  --agentic-rag-output experiments/outputs/agentic_rag_http
```

`--resume` 只用于继续同一个 HTTP 批次，不要用它把 HTTP 结果写入旧的嵌入式结果目录。

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
- [x] 20 条 DORA 的旧版嵌入式 Agentic RAG 已运行并保存证据。
- [x] 120 行评分表已建立并写入现有客观数据。
- [x] Manual 工作表已建立。
- [x] Regulatory RAG HTTP 健康检查、状态和 Planner 已联通。
- [x] 40 条 HTTP Agentic RAG 已在独立输出目录运行。
- [x] 20 条 AI Act 的两种 AI 方法已运行。
- [ ] Manual 和人工修正时间已填写。
- [ ] 最终评分、论文表格和图表已生成。
