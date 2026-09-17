import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# 環境変数の読み込み
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
xai_api_key = os.environ.get("XAI_API_KEY")

st.set_page_config(page_title="AI Editor Suite", page_icon="📝", layout="wide")

# --- Streamlitの不要なロゴ等を非表示にするためのCSS ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QSob {visibility: hidden;}
            a[href*="streamlit"] { display: none !important; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- カスタムCSS (過去プロジェクトの共通デザインを適用) ---
custom_css = """
<style>
    /* 全体フォント */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    }
    
    /* 検索・実行ボタンのカスタム */
    div.stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-size: 15px;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.5);
    }
    
    /* ページヘッダー装飾 */
    .page-header {
        text-align: center;
        padding: 20px 0 20px 0;
        margin-bottom: 20px;
    }
    .page-header h1 {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .page-header p {
        font-size: 14px;
        color: #718096;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

if not api_key or api_key == "your_openai_api_key_here":
    st.error("OpenAIのAPIキーが設定されていません。`.env` または Secrets を設定してください。")
    st.stop()

# OpenAI クライアント初期化
client = OpenAI(api_key=api_key)

# xAI (Grok) クライアント初期化 (キーがあれば)
xai_client = None
if xai_api_key:
    xai_client = OpenAI(
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1",
    )

# --- ページヘッダー ---
st.markdown("""
<div class="page-header">
    <h1>📝 AI Editor Suite</h1>
    <p>夜職経験の情報商材化サポート / 構成案の自動生成・原稿のブラッシュアップ・X向けポスト作成</p>
</div>
""", unsafe_allow_html=True)

# タブでツールを切り替え
tab1, tab2, tab3 = st.tabs([
    "1. SEO・構成最適化ツール", 
    "2. 記事校閲・ブラッシュアップツール",
    "3. X(Twitter)用ポスト生成 (Grok)"
])

# ----------------------------------------
# ツール1: 構成・タイトル生成 (OpenAI)
# ----------------------------------------
with tab1:
    st.markdown("### 📌 構成・タイトル生成")
    st.write("Xや市場でリサーチした「記事のテーマ」や「読者の悩み」を入力してください。")
    theme_input = st.text_area("テーマ・市場の悩み", height=150, placeholder="例：お客さんとの連絡（営業）がしんどい、売り上げが伸びない焦り...", key="theme_input")
    
    if st.button("構成案を生成する", key="btn_outline"):
        if theme_input:
            with st.spinner("AIが構成案を作成しています..."):
                prompt = f"""
あなたは凄腕のWebマーケターであり、noteのアルゴリズムやSEOに精通したプロの編集者です。
クライアントは元ランカー（夜職）で、自身の経験を元に記事を執筆します。

以下の「テーマ・悩み」をベースに、noteで読まれやすく、検索流入（SEO）も狙える「記事の設計図（プロット）」を作成してください。

【最適化の条件】
- タイトル案：クリック率が高まるパワーワードを含め、30文字前後で3つ提案してください。
- 構成：読者の離脱を防ぐため、導入（共感）→ 問題提起 → 解決策（経験談）→ まとめ・行動喚起（有料noteへの誘導など）の王道パターンとすること。
- クライアントへの指示：各見出しの中で「具体的にどんな経験談やエピソードを書けばいいか」をわかりやすく指南してください。

【テーマ・市場の悩み】
{theme_input}
"""
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a professional SEO marketer and editor."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    st.success("構成案の生成が完了しました！")
                    st.markdown("### 生成結果")
                    st.markdown(response.choices[0].message.content)
                    
                    st.text_area("コピー用", value=response.choices[0].message.content, height=300, key="copy_outline")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("テーマを入力してください。")

# ----------------------------------------
# ツール2: 記事校閲・ブラッシュアップ (OpenAI)
# ----------------------------------------
with tab2:
    st.markdown("### ✨ 記事校閲・ブラッシュアップ")
    st.write("ご友人が執筆したnote原稿（下書き）を貼り付けてください。")
    draft_input = st.text_area("原稿（下書き）", height=300, placeholder="ここに原稿を貼り付け...", key="draft_input")
    
    if st.button("校閲・ブラッシュアップを実行", key="btn_proofread"):
        if draft_input:
            with st.spinner("AIが原稿をブラッシュアップしています...（数秒〜十数秒かかります）"):
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
{draft_input}
"""
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a professional editor and proofreader."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    st.success("ブラッシュアップが完了しました！")
                    st.markdown("### 完成版の原稿")
                    st.markdown(response.choices[0].message.content)
                    
                    st.text_area("コピー用", value=response.choices[0].message.content, height=400, key="copy_proofread")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("原稿を入力してください。")

# ----------------------------------------
# ツール3: X(Twitter) 市場リサーチ＆悩み分析 (Grok)
# ----------------------------------------
with tab3:
    st.markdown("### 🐦 X (Twitter) 市場リサーチ・悩み分析")
    st.write("Xのトレンドやユーザー心理の解析に強い「**xAI Grok**」を利用し、市場のリアルな声を分析します。")
    st.write("リサーチしたいキーワードや、実際に気になったポスト（ツイート）のテキストを貼り付けてください。")
    
    if not xai_client:
        st.warning("`XAI_API_KEY` が設定されていないため、Grokは利用できません。")
    else:
        x_input = st.text_area("リサーチキーワード、または実際のポスト内容", height=150, placeholder="例：『最近お客さんとのLINEがしんどい』というポストがバズっていた。ここからどんな悩みが抽出できる？\n\n例：検索キーワード「夜職 辞めたい」「売上 焦り」", key="x_input")
        
        if st.button("Grokで市場の悩みを分析する", key="btn_grok"):
            if x_input:
                with st.spinner("GrokがXの文脈を元に市場をリサーチ・分析しています..."):
                    prompt = f"""
あなたはX（旧Twitter）のアルゴリズム、最新トレンド、そしてユーザー心理の深い解析に精通した凄腕のSNSマーケターです。
クライアントは元ランカー（夜職）で、今後は自身の経験を情報商材（note等）として発信し、ファンを獲得していきます。

以下の「キーワード」や「実際のポスト内容」を元に、夜職の現役層が**今、具体的にどんなことに悩み、どんな言葉（インサイト）に反応するのか**を深くリサーチ・分析してください。

【分析・出力の条件】
1. **悩みの深堀り:** 表面的な悩みだけでなく、その裏にある本音や恐怖（例：将来への不安、承認欲求など）を言語化してください。
2. **需要の高いトピック案:** 分析結果を踏まえ、次にnoteで書くべき「需要の高い記事トピック案」を3つ提案してください。
3. **Grokの強みを活かす:** X界隈特有のリアルな空気感や言葉選び（文脈）を踏まえた、生々しく実用的な分析結果にしてください。

【リサーチ対象（キーワード・実際のポスト等）】
{x_input}
"""
                    try:
                        response = xai_client.chat.completions.create(
                            model="grok-beta",
                            messages=[
                                {"role": "system", "content": "You are a professional X (Twitter) market researcher and data analyst."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        st.success("Grokによるリサーチ・分析が完了しました！")
                        st.markdown("### リサーチ結果 (Powered by Grok)")
                        st.markdown(response.choices[0].message.content)
                        
                        st.text_area("コピー用", value=response.choices[0].message.content, height=300, key="copy_x_post")
                    except Exception as e:
                        st.error(f"Grok APIエラーが発生しました: {e}")
            else:
                st.warning("リサーチ対象を入力してください。")
