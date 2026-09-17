import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

INPUT_FILE = "input_draft.txt"
OUTPUT_FILE = "output_proofread.md"

def proofread_article(draft):
    print("Proofreading and optimizing the draft ...")
    prompt = f"""
あなたは凄腕のWebマーケターであり、プロの編集者（校閲・ブラッシュアップ担当）です。
以下のテキストは、元ランカー（夜職）のクライアントが書いたnote記事の原稿（下書き）です。

この原稿を以下の条件に従ってブラッシュアップしてください。

【校閲・最適化の条件】
1. 熱量と個性の保持：筆者独自の筆致、言葉遣い、感情（熱量）は絶対に殺さず、そのまま活かしてください。
2. 読みやすさの向上：スマホで読まれることを前提とし、適度な改行、箇条書き、太字装飾を加えて、視覚的な離脱を防いでください。
3. SEOとアルゴリズム最適化：自然な形で関連キーワード（夜職、悩み、売上アップなど文脈に合うもの）を見出しや本文に散りばめてください。
4. 誤字脱字の修正：明らかな誤字や文法エラーのみ修正してください。

【出力フォーマット】
ブラッシュアップ後の「完成版の記事本文（Markdown形式）」のみを出力してください。（挨拶や解説は不要です）

【クライアントの原稿】
{draft}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional editor and proofreader."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def main():
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            f.write("ここにご友人が執筆したnote原稿（下書き）を貼り付けてください。")
        print(f"Created {INPUT_FILE}. Please paste the draft there and run again.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        draft = f.read().strip()

    if not draft or draft.startswith("ここにご友人が"):
        print(f"Please edit {INPUT_FILE} with the actual draft.")
        return

    try:
        proofread_text = proofread_article(draft)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(proofread_text)
        print(f"Successfully proofread the draft. Saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
