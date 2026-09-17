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
# ツール3: X(Twitter)用ポスト生成 (Grok)
# ----------------------------------------
with tab3:
    st.markdown("### 🐦 X (Twitter) 用ポスト作成")
    st.write("Xのアルゴリズムとトレンドに強い「**xAI Grok**」を使って、ファンを獲得するためのポスト（ツイート）文案を作成します。")
    
    if not xai_client:
        st.warning("`XAI_API_KEY` が設定されていないため、Grokは利用できません。")
    else:
        x_input = st.text_area("ポストで伝えたい内容や、募集したい悩み", height=150, placeholder="例：新しくnoteを始めたことの告知。現役の子たちの悩みを聞いてみたい、など...", key="x_input")
        
        if st.button("Grokでポストを作成する", key="btn_grok"):
            if x_input:
                with st.spinner("GrokがX向けのバズるポストを考案しています..."):
                    prompt = f"""
あなたはX（旧Twitter）のアルゴリズム、トレンド、バズる構文に精通した凄腕のSNSマーケターです。
クライアントは元ランカー（夜職）で、今後は自身の経験を情報商材（note等）として発信し、ファンを獲得していきます。

以下の「伝えたい内容」を元に、夜職の現役層の共感を引き出し、エンゲージメント（いいね・リプライ・リポスト）を獲得しやすいポスト（ツイート）の文案を3パターン作成してください。

【条件】
- 140文字以内に収める短文パターンと、ツリー形式（スレッド）で長めに語るパターンの両方を含めること。
- 夜職界隈でウケやすい、リアルで刺さる言葉選びをすること。
- Grok特有の、少しウィットに富んだエッジの効いた表現も歓迎します。

【伝えたい内容】
{x_input}
"""
                    try:
                        response = xai_client.chat.completions.create(
                            model="grok-beta",
                            messages=[
                                {"role": "system", "content": "You are a professional X (Twitter) marketer expert in viral posts and engagement."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.8
                        )
                        st.success("Grokによるポスト文案の生成が完了しました！")
                        st.markdown("### 生成結果 (Powered by Grok)")
                        st.markdown(response.choices[0].message.content)
                        
                        st.text_area("コピー用", value=response.choices[0].message.content, height=300, key="copy_x_post")
                    except Exception as e:
                        st.error(f"Grok APIエラーが発生しました: {e}")
            else:
                st.warning("内容を入力してください。")
