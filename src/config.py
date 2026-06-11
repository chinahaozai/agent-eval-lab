"""集中管理 LLM provider 配置与客户端创建。

为什么独立成一个文件：
- 整个项目只在这里读环境变量、建 client，其他模块统一复用 get_client()。
- provider 通过 .env 切换（DeepSeek / Qwen / OpenAI / Claude 都提供 OpenAI 兼容接口），
  业务代码一行都不用改 —— 这正是后面评测多个模型时需要的能力。
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

# 加载项目根目录的 .env（若不存在则静默跳过，由 load_settings 给出友好提示）。
load_dotenv()

# 单次请求超时（秒）。对外部 API 调用必须设超时，避免脚本无限挂起。
REQUEST_TIMEOUT_SECONDS = 60

# 各模型每百万 token 的价格，仅用于成本估算（单位与所选 provider 的账单一致）。
# 价格会变动，以各家官网为准；未在此登记的模型，成本按 0 估算。
#
# 关于 DeepSeek 的输入价：官方区分「缓存命中 / 缓存未命中」两档，差距极大
# （v4-flash 命中仅 0.02 元、未命中 1 元 —— 差 50 倍）。这里的 input 一律取
# 「缓存未命中」价，即成本上限；实际账单因命中缓存通常更低。精确区分缓存命中的
# 成本核算留到评测周（做成本指标时）再处理。
PRICE_PER_1M_TOKENS: dict[str, dict[str, float]] = {
    # ── DeepSeek（人民币/百万 token）。deepseek-chat / deepseek-reasoner 是旧名，
    #    2026-07-24 弃用，分别对应 v4-flash 的非思考 / 思考模式，价格与 v4-flash 相同。
    "deepseek-v4-flash": {"input": 1.0, "output": 2.0},   # 输入缓存命中价仅 0.02
    "deepseek-v4-pro": {"input": 3.0, "output": 6.0},     # 输入缓存命中价仅 0.025
    "deepseek-chat": {"input": 1.0, "output": 2.0},       # = v4-flash
    "deepseek-reasoner": {"input": 1.0, "output": 2.0},   # = v4-flash（思考模式）
}
DEFAULT_PRICE = {"input": 0.0, "output": 0.0}


@dataclass(frozen=True)
class Settings:
    """运行时配置，全部来自环境变量。"""

    api_key: str
    base_url: str
    model: str


def load_settings() -> Settings:
    """从环境变量读取配置；缺失关键项时打印清晰的中文提示并退出。"""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()

    missing = [
        name
        for name, value in (
            ("LLM_API_KEY", api_key),
            ("LLM_BASE_URL", base_url),
            ("LLM_MODEL", model),
        )
        if not value
    ]
    if missing:
        print(
            "❌ 缺少环境变量: " + ", ".join(missing) + "\n"
            "   请在项目根目录的 .env 中填写这些变量；若还没有 .env，先执行 cp .env.example .env。",
            file=sys.stderr,
        )
        sys.exit(1)

    return Settings(api_key=api_key, base_url=base_url, model=model)


def get_client() -> tuple[OpenAI, Settings]:
    """创建 OpenAI 兼容客户端，返回 (client, settings)。"""
    settings = load_settings()
    client = OpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return client, settings


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """按 PRICE_PER_1M_TOKENS 估算单次调用成本；未登记的模型返回 0。"""
    price = PRICE_PER_1M_TOKENS.get(model, DEFAULT_PRICE)
    return (
        prompt_tokens / 1_000_000 * price["input"]
        + completion_tokens / 1_000_000 * price["output"]
    )
