# 实验操作指南

这份指南按实际执行顺序写。正式实验开始前重新读一次即可，不需要另外设计流程。

## 1. 先记住三个方法

- `Manual`：自己查官方法律文本并填写结果，是核验后的评分基线。
- `LLM-only`：调用与 Agent 相同的模型，但不给模型 RAG 证据，也不联网搜索。
- `Agentic RAG`：程序先从 Regulatory RAG 检索证据，再让同一模型判断。

三种方法使用完全相同的输入条目和输出字段。系统只辅助复核，不代替最终法律判断。

## 2. 一次性环境准备

在终端执行：

```bash
cd /Users/dada/Developer/italy_proj/ai-cyber-risk-thesis
conda activate compliance-agent
python -m pip install -r requirements.txt
python -m unittest discover -s agent/tests -v
```

`.env` 保存模型和 RAG 配置，不要提交或复制到实验结果里。需要的变量见
`.env.example`。LLM-only 和 Agent 都读取 `PRIVATE_AI_MODEL`，因此不会因为手动打开
另一个聊天产品而换成不同模型。

当前本机的 RAG 配置应至少包含：

```text
REGULATORY_RAG_ROOT=/Users/dada/Developer/italy_proj/regulatory-rag
REGULATORY_RAG_MODE=hybrid
REGULATORY_RAG_TOP_K=10
```

AI Act 组合 profile 建好后，再增加下一节所列的 `REGULATORY_RAG_PROFILE`。

## 3. 唯一还缺的外部工作：AI Act RAG

不要修改当前 DORA profile。应在只读的独立工程
`/Users/dada/Developer/italy_proj/regulatory-rag` 中新建一个论文专用的 DORA + AI Act
组合 profile，例如：

```text
data/regulations/catalog/corpora/thesis-dora-ai-act-en.json
```

AI Act 主法规使用 EUR-Lex 发布的官方英文 Regulation (EU) 2024/1689，建议稳定标识
为：

```text
document_id: EU-2024-1689
CELEX: 32024R1689
ELI: http://data.europa.eu/eli/reg/2024/1689/oj
parser_profile: eurlex_oj_html
```

官方入口：`https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng`。

在 RAG 工程中的具体操作是：

1. 从 EUR-Lex 下载 Official Journal 英文 PDF，先放入
   `data/regulations/incoming/`，人工确认法规编号、语言和来源。
2. 将确认后的原始文件移动到类似
   `data/regulations/official/eu/eurlex/ai_act/base_acts/` 的目录。不要重新保存或修改
   原始文件。
3. 运行 inventory，取得文件大小、页数和 SHA-256：

```bash
python scripts/inventory_regulatory_corpus.py \
  --root data/regulations/official/eu/eurlex/ai_act
```

4. 在 `data/regulations/catalog/documents.json` 添加 AI Act 的人工复核记录，并提升
   catalog version。原有 profile 的 `expected_catalog_version` 也要同步。
5. 复制 DORA profile 为新的论文 profile，使用新的 `corpus_id`、版本号和独立的
   snapshot/processed 路径；保留需要的 DORA document IDs，再加入
   `EU-2024-1689`。首次构建时暂不填写 `processed_corpus`。
6. 使用新 profile 验证、下载 HTML 并生成 chunks：

```bash
python scripts/validate_regulatory_corpus.py --profile PATH_TO_NEW_PROFILE
python scripts/fetch_eurlex_html.py --document-id EU-2024-1689 --profile PATH_TO_NEW_PROFILE
python scripts/build_eurlex_corpus.py --profile PATH_TO_NEW_PROFILE
python scripts/build_pdf_corpus.py --profile PATH_TO_NEW_PROFILE
python scripts/validate_regulatory_corpus.py --profile PATH_TO_NEW_PROFILE
```

7. 将最后一次 validation 输出的 `chunk_count` 和 `chunk_set_hash` 写入新 profile 的
   `processed_corpus`，再次验证，然后构建 vector index：

```bash
python scripts/validate_regulatory_corpus.py --profile PATH_TO_NEW_PROFILE
python scripts/build_vector_index.py --profile PATH_TO_NEW_PROFILE
```

8. 至少人工检查实验会用到的 Articles 5、9–15、17、19–20、25–27、72–73 是否能
   检索，并核对返回文本和条款定位。
9. 回到本工程，在 `.env` 中设置：

```text
REGULATORY_RAG_PROFILE=/absolute/path/to/thesis-dora-ai-act-en.json
```

这部分只能在 Regulatory RAG 工程修改。本工程不应复制第二份法规语料。

## 4. 正式实验前的开发检查

先使用 DORA-15 检查 LLM-only。输出路径必须是一个尚不存在的新目录：

```bash
python -m agent.llm_only \
  --input experiments/datasets/pilot_items.csv \
  --item DORA-15 \
  --output /tmp/dora15-llm-only-dev
```

再检查 Agentic RAG：

```bash
python -m agent.main \
  --input experiments/datasets/pilot_items.csv \
  --item DORA-15 \
  --evidence rag \
  --output /tmp/dora15-agent-dev
```

没有 `--experiment-run` 的输出会明确标为 development，不能放入论文结果。

## 5. Pilot 的执行顺序

Pilot 固定使用 TC05、TC20、DORA-15、DORA-18。必须先做 Manual，再看 AI 输出，避免
AI 答案影响人工基线。

### 5.1 Manual

对每一条：

1. 开始计时。
2. 只查官方法律文本。
3. 拆开检查每个现有引用。
4. 只记录真正重要的遗漏条款。
5. 填写 `experiments/templates/mapping_reviews.csv` 和
   `experiments/templates/item_reviews.csv`。
6. 记录结束时间和官方来源。
7. 再次核对法律文本；核对后的 Manual 结果就是评分基线。

### 5.2 LLM-only

四条一次运行：

```bash
python -m agent.batch \
  --method llm-only \
  --input experiments/datasets/pilot_items.csv \
  --output experiments/runs/pilot_dev/llm_only
```

程序会保存每条的第一次模型回答和生成时间。然后记录人工修正时间，不要重新生成一个
“更好看”的回答替换第一次回答。

### 5.3 Agentic RAG

AI Act corpus 可用后运行：

```bash
python -m agent.batch \
  --method agentic-rag \
  --input experiments/datasets/pilot_items.csv \
  --output experiments/runs/pilot_dev/agentic_rag
```

检查每条的 `evidence.json`、`raw_response.json`、`mapping_reviews.csv` 和
`item_reviews.csv`，并记录人工修正时间。

如果 Agent 使用了唯一一次自动修正重试，目录还会出现 `raw_attempts.json`，其中保留
第一次和修正后的回答。不要删除第一次失败的记录。

## 6. Pilot 后冻结规则

Pilot 只用来发现明显问题，例如引用拆分错误、RAG 找不到正确条款、输出难以评分或
计时方式无法执行。不要为了让 Agent 得分更高反复调整。

修正必要问题后，固定：

- 40 条输入数据；
- 两个 prompt 文件；
- `PRIVATE_AI_MODEL`；
- RAG profile、corpus version 和 index version；
- 判断标签和计时规则；
- Git commit。

同时将论文 RAG profile 的 `corpus_status` 改为 `frozen`，填写不早于
`as_of_date` 的 `frozen_at`，并再次通过 corpus validation。

Pilot 的开发输出不能直接计入结果。冻结后，用 `--experiment-run` 重新执行四条。

## 7. 正式运行 40 条

每种 AI 方法每条运行一次。固定模型的 temperature 已在程序中设置为 0。

```bash
python -m agent.batch \
  --method llm-only \
  --input experiments/datasets/items.csv \
  --output experiments/runs/main_v1/llm_only \
  --experiment-run

python -m agent.batch \
  --method agentic-rag \
  --input experiments/datasets/items.csv \
  --output experiments/runs/main_v1/agentic_rag \
  --experiment-run
```

Manual 仍应在查看对应 AI 输出前完成。总计是 40 条 × 3 种方法，即 120 个方法—条目
组合，不需要人为扩展成更多实验。

## 8. 最后评分

以核验后的 Manual 为基线，将每条、每种方法汇总到
`experiments/results/item_results.csv`。比较：

- 完成并修正到可接受结果的总时间；
- 现有引用判断准确率；
- 重要遗漏引用的 precision/recall；
- 证据引用错误；
- 无依据的法律或适用性判断；
- 人工修正时间。

如果后来发现 Manual 基线有错，记录修改原因，并按修正后的基线重新计算三个方法的
相关结果。不要为了得到更好的结论删除失败条目。

## 9. 完成检查表

- [ ] AI Act 已进入论文专用的组合 RAG profile。
- [ ] AI Act 和 DORA 条款检索均已人工抽查。
- [ ] 四条 pilot 的 Manual、LLM-only、Agentic RAG 均完成。
- [ ] 根据 pilot 只修正了明确的流程问题。
- [ ] 数据、模型、prompt、corpus 和代码版本已冻结。
- [ ] 四条 pilot 已按冻结版本重新运行。
- [ ] 40 条主实验已完成。
- [ ] 人工修正时间和评分结果已填写。
- [ ] 错误和局限没有被隐藏。
