import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

INPUT_FILE = "input_theme.txt"
OUTPUT_FILE = "output_outline.md"

def generate_outline(theme):
    print("Generating SEO-optimized article outline ...")
    prompt = f"""
あなたは凄腕のWebマーケターであり、noteのアルゴリズムやSEOに精通したプロの編集者です。
クライアントは元ランカー（夜職）で、自身の経験を元に記事を執筆します。

以下の「テーマ・悩み」をベースに、noteで読まれやすく、検索流入（SEO）も狙える「記事の設計図（プロット）」を作成してください。

【最適化の条件】
- タイトル案：クリック率が高まるパワーワードを含め、30文字前後で3つ提案してください。
- 構成：読者の離脱を防ぐため、導入（共感）→ 問題提起 → 解決策（経験談）→ まとめ・行動喚起（有料noteへの誘導など）の王道パターンとすること。
- クライアントへの指示：各見出しの中で「具体的にどんな経験談やエピソードを書けばいいか」をわかりやすく指南してください。

【テーマ・市場の悩み】
{theme}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional SEO marketer and editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def main():
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            f.write("ここにXや市場でリサーチした「記事のテーマ」や「読者の悩み」を記載してください。")
        print(f"Created {INPUT_FILE}. Please write the theme there and run again.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        theme = f.read().strip()

    if not theme or theme.startswith("ここにXや市場で"):
        print(f"Please edit {INPUT_FILE} with an actual theme or pain points.")
        return

    try:
        outline_text = generate_outline(theme)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(outline_text)
        print(f"Successfully generated outline. Saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
