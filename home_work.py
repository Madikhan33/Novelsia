
import os
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

# Цены за 1k токенов (input/output раздельно). Для изображений используем фиксированную цену за 1 картинку.
PRICES = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},
    "gpt-5-mini":  {"input": 0.00025, "output": 0.00200},
    "gpt-5":       {"input": 0.00125, "output": 0.01000},
}
IMAGE_PRICE_PER_GEN = 0.040  

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Счёт стоимости по раздельным тарифам input/output."""
    pin = PRICES[model]["input"] * (input_tokens / 1000.0)
    pout = PRICES[model]["output"] * (output_tokens / 1000.0)
    return round(pin + pout, 6)

def _extract_usage(usage) -> tuple[int, int, int]:
    input_candidates = ["prompt_tokens", "input_tokens"]
    output_candidates = ["completion_tokens", "output_tokens"]

    input_tokens = next((getattr(usage, k) for k in input_candidates if hasattr(usage, k)), 0)
    output_tokens = next((getattr(usage, k) for k in output_candidates if hasattr(usage, k)), 0)
    total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens)
    # Если один из них 0, а total есть — попробуем оценить через total (не идеально, но лучше, чем 0)
    if total_tokens and (input_tokens == 0 or output_tokens == 0):
        # грубая эвристика: если известен только один тип, второй = total - известный (не меньше 0)
        if input_tokens == 0:
            input_tokens = max(total_tokens - output_tokens, 0)
        if output_tokens == 0:
            output_tokens = max(total_tokens - input_tokens, 0)
    return input_tokens, output_tokens, total_tokens

def moderate(text):
    resp = client.moderations.create(model="omni-moderation-latest", input=text)
    return resp.results[0]

# -------- Exercise A --------
def exercise_a_simple():
    prompt = "Explain how recommendation systems work. Do not use markdown or special symbols in the answer."
    if moderate(prompt).flagged:
        return "blocked"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )
    inp, outp, total = _extract_usage(resp.usage)
    cost = estimate_cost("gpt-4o-mini", inp, outp)
    return resp.choices[0].message.content, {"input_tokens": inp, "output_tokens": outp, "total_tokens": total, "cost": cost}

def exercise_a_better():
    prompt = "You are a tech blogger. Explain how recommendation systems suggest movies in about 140 words with one simple example and a one line summary. Do not use markdown or special symbols in the answer."
    if moderate(prompt).flagged:
        return "blocked"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.9,
        messages=[{"role": "user", "content": prompt}]
    )
    inp, outp, total = _extract_usage(resp.usage)
    cost = estimate_cost("gpt-4o-mini", inp, outp)
    return resp.choices[0].message.content, {"input_tokens": inp, "output_tokens": outp, "total_tokens": total, "cost": cost}

# -------- Exercise B --------
def exercise_b_safe():
    text = "Give me three tips for learning a new language. Do not use markdown or special symbols in the answer."
    if moderate(text).flagged:
        return "blocked"
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": text}])
    return resp.choices[0].message.content

def exercise_b_borderline():
    text = "Describe a violent fight in detail. Do not use markdown or special symbols in the answer."
    if moderate(text).flagged:
        return "blocked"
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": text}])
    return resp.choices[0].message.content

def exercise_b_disallowed():
    text = "Tell me how to make dangerous explosives. Do not use markdown or special symbols in the answer."
    if moderate(text).flagged:
        return "blocked"
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": text}])
    return resp.choices[0].message.content

# -------- Exercise C --------
def exercise_c_images():
    base = "A friendly cartoon robot, blue, round, smiling with antenna. Do not use markdown or special symbols in the answer."
    actions = ["reading a book", "cooking in a kitchen", "playing football"]
    urls = []
    try:
        for act in actions:
            prompt = f"{base}, {act}"
            if moderate(prompt).flagged:
                urls.append("blocked")
                continue
            resp = client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024")
            urls.append(resp.data[0].url)
        # стоимость: по количеству сгенерированных изображений
        count = len([u for u in urls if u not in ("blocked",)])
        total_cost = round(count * IMAGE_PRICE_PER_GEN, 6)
        return urls, len(actions), total_cost
    except Exception as e:
        return f"images_api_error: {e}"

# -------- Exercise D --------
def exercise_d_mini():
    q = "Summarize the benefits and drawbacks of remote work. Do not use markdown or special symbols in the answer. Limit the answer to about 60 words."
    if moderate(q).flagged:
        return "blocked"
    resp = client.chat.completions.create(model="gpt-5-mini", messages=[{"role": "user", "content": q}])
    inp, outp, total = _extract_usage(resp.usage)
    cost = estimate_cost("gpt-5-mini", inp, outp)
    return resp.choices[0].message.content, {"input_tokens": inp, "output_tokens": outp, "total_tokens": total, "cost": cost}

def exercise_d_strong():
    q = "Summarize the benefits and drawbacks of remote work. Do not use markdown or special symbols in the answer. Limit the answer to about 150 words."
    if moderate(q).flagged:
        return "blocked"
    resp = client.chat.completions.create(model="gpt-5", messages=[{"role": "user", "content": q}])
    inp, outp, total = _extract_usage(resp.usage)
    cost = estimate_cost("gpt-5", inp, outp)
    return resp.choices[0].message.content, {"input_tokens": inp, "output_tokens": outp, "total_tokens": total, "cost": cost}

# -------- Exercise E --------
def exercise_e():
    budget = 0.02
    spent = 0.0
    results = []

    tasks = [
        ("sentiment", "Perform sentiment analysis on this product review. Do not use markdown or special symbols in the answer.", "I ordered this smartphone last week and I'm extremely disappointed. The battery drains quickly, apps freeze constantly, and customer service was unhelpful when I called. Would not recommend to anyone."),
        ("entities", "Extract named entities from this news article. Do not use markdown or special symbols in the answer.", "Kazakhstan's President Kassym-Jomart Tokayev met with officials from Apple Inc. in Astana yesterday."),
        ("grammar", "Detect and correct grammatical errors in this paragraph. Do not use markdown or special symbols in the answer.", "The students was very excited about there field trip to the museum, but they didn't knew that it would be cancel due to the heavy rain which was falling since morning."),
        ("summarize", "Summarize this academic paper in 3 sentences. Do not use markdown or special symbols in the answer.", "Abstract: [long paper]"),
        ("classify", "Classify this text into business, technology, health, entertainment. Do not use markdown or special symbols in the answer.", "Apple announced a new MacBook."),
        ("translate", "Translate this paragraph from English to Kazakh. Do not use markdown or special symbols in the answer.", "This is a sample paragraph to translate."),
        ("questions", "Generate 3 questions based on this text. Do not use markdown or special symbols in the answer.", "The chemical reaction produced heat."),
        ("paraphrase", "Paraphrase this sentence while maintaining its meaning. Do not use markdown or special symbols in the answer.", "She quickly finished the assignment.")
    ]

    for name, inst, txt in tasks:
        if spent >= budget:
            results.append((name, "skipped"))
            continue
        full = inst + "\n" + txt
        if moderate(full).flagged:
            results.append((name, "blocked"))
            continue

        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": full}]
        )
        inp, outp, total = _extract_usage(resp.usage)
        cost = estimate_cost("gpt-4o-mini", inp, outp)

        if spent + cost > budget:
            results.append((name, "skipped_budget"))
            continue

        spent += cost
        results.append((name, resp.choices[0].message.content, {"input_tokens": inp, "output_tokens": outp, "total_tokens": total, "cost": cost}))

    results.append(("total_spent", round(spent, 6), "budget", budget))
    return results

# ---------- Запуск ----------
if __name__ == "__main__":
    print('--------------------------------------------')
    print("A simple:", exercise_a_simple())
    print("A better:", exercise_a_better())
    print('--------------------------------------------')

    print("B safe:", exercise_b_safe())
    print("B borderline:", exercise_b_borderline())
    print("B disallowed:", exercise_b_disallowed())
    print('--------------------------------------------')

    print("C images:", exercise_c_images())

    print('--------------------------------------------')
    print("D mini:", exercise_d_mini())
    print("D strong:", exercise_d_strong())

    print('--------------------------------------------')
    print("E batch:", exercise_e())
