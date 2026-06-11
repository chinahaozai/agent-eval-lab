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

## 设计原则

- **第一个 Agent 手写循环，不用 LangChain**：做 Eval 必须看清轨迹里每一步怎么产生的。
- **provider 可替换**：评测的本质之一就是横向对比不同模型，所以从第一天起就把 provider 抽象到 `.env`。
- **每天有"完成标志"**：Eval 的精神是可验证，先拿它要求项目本身。
