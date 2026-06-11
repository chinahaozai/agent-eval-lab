"""Day 1 · 第一个 LLM API 调用。

目标：跑通一次对话，并打印本次消耗的 token 数与估算成本 ——
建立"每次调用都在花钱"的体感，这是后面做 Eval 成本指标的起点。

运行（在项目根目录、已激活虚拟环境的前提下）:
    python -m src.hello_llm
"""
from __future__ import annotations

from src.config import estimate_cost, get_client

# 故意问一个和项目主题相关的问题。
PROMPT = "用一句话解释什么是 AI Agent。"


def main() -> None:
    client, settings = get_client()

    print(f"→ 模型: {settings.model}")
    print(f"→ 提问: {PROMPT}\n")

    response = client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": PROMPT}],
    )

    reply = response.choices[0].message.content
    print("← 回复:")
    print(reply)
    print()

    # usage 在极个别兼容实现里可能为 None，做个防御。
    usage = response.usage
    if usage is None:
        print("⚠️  本次响应未返回 usage 信息，无法统计 token。")
        return

    cost = estimate_cost(settings.model, usage.prompt_tokens, usage.completion_tokens)
    print("📊 本次调用消耗:")
    print(f"   输入 token : {usage.prompt_tokens}")
    print(f"   输出 token : {usage.completion_tokens}")
    print(f"   合计 token : {usage.total_tokens}")
    print(f"   估算成本   : {cost:.6f}  (单位同你 provider 的计价；为 0 表示该模型未在 config 登记价格)")


if __name__ == "__main__":
    main()
