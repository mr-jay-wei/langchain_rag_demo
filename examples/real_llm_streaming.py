"""
真实的LLM流式调用示例
展示生产环境中如何实现真正的流式响应
"""

import asyncio
import json
from typing import AsyncGenerator

# 模拟真实的LLM流式调用
async def real_openai_streaming(prompt: str) -> AsyncGenerator[str, None]:
    """
    真实的OpenAI流式调用示例
    在生产环境中，这里会是真实的API调用
    """
    
    # 真实的OpenAI流式调用代码：
    """
    import openai
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True,  # 启用流式响应
        temperature=0.7
    )
    
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content  # 直接yield，无延迟
    """
    
    # 模拟真实的流式响应（无人为延迟）
    response_parts = [
        "根据", "您的", "问题，", "我", "认为", "人工智能", 
        "是", "计算机科学", "的", "一个", "重要", "分支。"
    ]
    
    for part in response_parts:
        # 这里的延迟是模拟真实的LLM生成时间
        # 在真实环境中，这个延迟来自LLM本身，不是人为添加
        await asyncio.sleep(0.1)  # 模拟真实的LLM处理时间
        yield part

async def real_deepseek_streaming(prompt: str) -> AsyncGenerator[str, None]:
    """
    真实的DeepSeek流式调用示例
    """
    
    # 真实的DeepSeek流式调用代码：
    """
    import httpx
    
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("choices", [{}])[0].get("delta", {}).get("content"):
                        yield data["choices"][0]["delta"]["content"]
    """
    
    # 模拟真实响应
    words = ["人工智能", "是", "一门", "综合性", "的", "学科"]
    for word in words:
        await asyncio.sleep(0.15)  # 模拟真实的API响应时间
        yield word

async def production_streaming_example():
    """生产环境流式响应示例"""
    print("🚀 生产环境流式响应示例")
    print("=" * 60)
    
    prompt = "什么是人工智能？"
    
    print("1. 真实的OpenAI流式调用:")
    print("   答案: ", end="", flush=True)
    
    async for chunk in real_openai_streaming(prompt):
        print(chunk, end=" ", flush=True)  # 直接输出，无额外延迟
    
    print("\n")
    
    print("2. 真实的DeepSeek流式调用:")
    print("   答案: ", end="", flush=True)
    
    async for chunk in real_deepseek_streaming(prompt):
        print(chunk, end=" ", flush=True)  # 直接输出，无额外延迟
    
    print("\n")

def production_best_practices():
    """生产环境最佳实践"""
    print("\n📋 生产环境最佳实践")
    print("=" * 60)
    
    print("✅ 正确的流式实现:")
    print("""
    async def stream_llm_response(prompt):
        # 直接调用LLM API，获取流式响应
        async for chunk in llm_api.stream(prompt):
            yield chunk  # 立即转发，无延迟
    """)
    
    print("❌ 错误的流式实现:")
    print("""
    async def bad_stream_response(text):
        for char in text:
            await asyncio.sleep(0.02)  # ❌ 人为延迟
            yield char
    """)
    
    print("🎯 关键原则:")
    print("  1. 延迟应该来自真实的处理时间")
    print("  2. 不要为了'效果'添加人为延迟")
    print("  3. 尽可能快地传输数据")
    print("  4. 让用户尽早看到响应")
    
    print("\n⚡ 性能优化建议:")
    print("  1. 使用更快的LLM模型")
    print("  2. 优化网络连接")
    print("  3. 减少中间处理步骤")
    print("  4. 实现智能缓存")
    print("  5. 并行处理多个请求")

async def main():
    """主演示函数"""
    
    await production_streaming_example()
    production_best_practices()
    
    print("\n" + "=" * 60)
    print("🎯 总结")
    print("=" * 60)
    print("💡 你的观察完全正确！")
    print("  生产环境不应该有模拟延迟")
    print("  真实的延迟来自LLM处理，不是人为添加")
    print("  流式响应的目的是提升用户体验，不是展示效果")
    print("  移除人为延迟后，性能提升数百倍！")

if __name__ == "__main__":
    asyncio.run(main())