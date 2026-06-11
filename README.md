# Agent Eval Lab

一个从零搭建的最小可用 **Agent 评测（Eval）** 项目：会用工具的 Agent → 轨迹记录 → 三类评测 → 轨迹回放器。
作为转 Agent Eval 方向的求职作品，完整路线见 [PLAN.md](./PLAN.md)。

## 目录结构

```
agent-eval-lab/
├── README.md            # 本文件
├── PLAN.md              # 三周每日落地清单（边做边勾）
├── .env.example         # provider 配置模板（DeepSeek/Qwen/OpenAI/Claude）
├── requirements.txt     # Python 依赖
├── src/
│   ├── config.py        # 读 .env、建 client、成本估算（全局复用）
│   └── hello_llm.py     # Day 1：第一个 API 调用
└── data/                # 轨迹 jsonl 产物（git 忽略）
```

## 快速开始

### 1. 创建虚拟环境并装依赖

```bash
# 方式 A：uv（推荐，快）
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# 方式 B：传统 venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 provider

```bash
cp .env.example .env
# 编辑 .env，从示例里选一组（国内推荐 DeepSeek），填入你的 API key
```

### 3. 跑通 Day 1

```bash
python -m src.hello_llm
```

看到模型回复 + 本次 token 消耗 + 估算成本，即 Day 1 完成。
（未配置 .env 时会得到一条中文提示，告诉你缺哪个变量 —— 这是预期行为。）

## 核心架构

当前只有一层关键抽象：`src/config.py` 是整个项目**唯一**读 `.env`、建 client 的地方，其他模块统一复用，绝不自己建客户端。

- **统一入口 `get_client()`**：任何要调 LLM 的模块都从这里拿 `(client, settings)`。所有 provider（DeepSeek / Qwen / OpenAI / Claude）都走 OpenAI 兼容接口，换 provider 只动 `.env`，业务代码零改动 —— 这正是后面横向评测多个模型所需的能力。
- **成本估算 `estimate_cost()`**：按价格表算单次调用花费（未登记的模型按 0 估算，输入价取缓存未命中的上限），建立「每次调用都在花钱」的体感，是后面成本指标的起点。
- **工程防御**：所有请求带 60s 超时；缺必填变量时 `load_settings()` 打印中文提示并退出（预期行为，非报错）。

后续按 [PLAN.md](./PLAN.md) 推进 —— 轨迹结构与 JSONL 落盘（第 1 周）、三类评测与指标（第 2 周）、回放器前端（第 3 周）—— 但「provider 抽象集中在 `config.py`」这条边界始终不变。

## 设计原则

- **第一个 Agent 手写循环，不用 LangChain**：做 Eval 必须看清轨迹里每一步怎么产生的。
- **provider 可替换**：评测的本质之一就是横向对比不同模型，所以从第一天起就把 provider 抽象到 `.env`。
- **每天有"完成标志"**：Eval 的精神是可验证，先拿它要求项目本身。
