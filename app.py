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
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    }
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
    }
    .page-header p {
        font-size: 14px;
        color: #718096;
    }
    .step-title {
        font-size: 20px;
        font-weight: bold;
        color: #2d3748;
        border-bottom: 2px solid #667eea;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

if not api_key or api_key == "your_openai_api_key_here":
    st.error("OpenAIのAPIキーが設定されていません。")
    st.stop()

client = OpenAI(api_key=api_key)

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
    <p>情報商材化サポートパイプライン（リサーチ → 執筆 → 調整 → 投稿）</p>
</div>
""", unsafe_allow_html=True)

# 厳密なフローに沿ったタブ構成
tab1, tab2, tab3, tab4 = st.tabs([
    "Step 1: トピック案のリサーチ", 
    "Step 2: 記事の作成",
    "Step 3: AIによる調整",
    "Step 4: 自動投稿 (準備中)"
])

# ----------------------------------------
# Step 1: トピック案のリサーチ
# ----------------------------------------
with tab1:
    st.markdown('<div class="step-title">Step 1: トピック案のリサーチ</div>', unsafe_allow_html=True)
    st.write("Xのポストやキーワードをもとに、Grok（またはOpenAI）が市場の悩みを分析し、noteで書くべきトピック案と構成案をリサーチします。")
    
    research_input = st.text_area("リサーチ対象（気になるXのポストやキーワード）", height=120, placeholder="例：「最近お客さんとのLINEがしんどい」というポスト。ここからどんな悩みが抽出できる？", key="research_input")
    
    use_grok = st.checkbox("X(Twitter)の最新トレンド分析に xAI Grok を使用する", value=True)
    
    if st.button("市場をリサーチし、トピック案を作成", key="btn_research"):
        if research_input:
            with st.spinner("市場の悩みを分析し、最適なトピックを抽出しています..."):
                prompt = f"""
あなたは凄腕のSNSマーケターであり、noteのアルゴリズムや読者心理に精通したプロの編集者です。
クライアントは元ランカー（夜職）で、自身の経験を元にnoteで記事を執筆します。

以下の「リサーチ対象（キーワード・実際のポスト等）」を深く分析し、次に書くべきnoteの記事トピック案と構成案を作成してください。

【分析・出力の条件】
1. **悩みの深堀り:** 現役層が抱える本音や恐怖を言語化すること。
2. **需要の高いトピック案:** 分析結果を踏まえ、クリック率が高まるタイトル案を3つ提案すること。
3. **構成案（プロット）:** 導入（共感）→ 問題提起 → 解決策（経験談）→ まとめ の王道パターンで、クライアントが「ここにどんな経験談を書けばいいか」分かるように指南すること。

【リサーチ対象】
{research_input}
"""
                try:
                    if use_grok and xai_client:
                        response = xai_client.chat.completions.create(
                            model="grok-beta",
                            messages=[
                                {"role": "system", "content": "You are a professional market researcher and editor."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        model_used = "Grok"
                    else:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a professional SEO marketer and editor."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        model_used = "OpenAI (GPT-4o)"
                        
                    st.success(f"{model_used} によるリサーチと構成案の作成が完了しました！")
                    st.markdown("### リサーチ・構成案 結果")
                    st.markdown(response.choices[0].message.content)
                    st.text_area("コピー用", value=response.choices[0].message.content, height=300, key="copy_research")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("リサーチ対象を入力してください。")

# ----------------------------------------
# Step 2: ライターによる記事の作成
# ----------------------------------------
with tab2:
    st.markdown('<div class="step-title">Step 2: ライターによる記事の作成</div>', unsafe_allow_html=True)
    st.write("Step 1 で作成したトピックと構成案をもとに、あなた（ライター）の言葉で記事を執筆してください。")
    st.info("💡 ここではAIは手出ししません。あなたの感情、リアルな体験談、独自の言い回しを存分にぶつけてください。少々の誤字脱字や読みにくさは、次の Step 3 でAIが綺麗に整えます。")
    
    draft_workspace = st.text_area("執筆用ワークスペース（※ブラウザを閉じると消えるため、適宜メモ帳などに保存してください）", height=400, placeholder="ここに記事の本文を書いていきます...", key="draft_workspace")

# ----------------------------------------
# Step 3: AIによる調整
# ----------------------------------------
with tab3:
    st.markdown('<div class="step-title">Step 3: AIによる調整 (校閲・ブラッシュアップ)</div>', unsafe_allow_html=True)
    st.write("Step 2 で書き上げた原稿をAIが読みやすく整え、SEOを意識した形にブラッシュアップします。")
    
    adjust_input = st.text_area("調整する原稿（下書き）", height=300, placeholder="Step 2で書いた原稿を貼り付けてください...", key="adjust_input")
    
    if st.button("AIによる調整を実行", key="btn_adjust"):
        if adjust_input:
            with st.spinner("AIが原稿の熱量を殺さずにブラッシュアップしています..."):
                prompt = f"""
あなたは凄腕のWebマーケターであり、プロの編集者（校閲・ブラッシュアップ担当）です。
以下のテキストは、元ランカー（夜職）のクライアントが書いたnote記事の原稿（下書き）です。

この原稿を以下の条件に従ってブラッシュアップしてください。

【校閲・調整の条件】
1. 熱量と個性の保持：筆者独自の筆致、言葉遣い、感情（熱量）は絶対に殺さず、そのまま活かしてください。
2. 読みやすさの向上：スマホで読まれることを前提とし、適度な改行、箇条書き、太字装飾を加えて視覚的な離脱を防いでください。
3. SEO最適化：自然な形で関連キーワードを見出しや本文に散りばめてください。
4. 誤字脱字の修正：明らかな誤字や文法エラーのみ修正してください。

【出力フォーマット】
ブラッシュアップ後の「完成版の記事本文（Markdown形式）」のみを出力してください。（挨拶や解説は不要です）

【クライアントの原稿】
{adjust_input}
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
                    st.success("AIによる調整が完了しました！")
                    st.markdown("### 完成版の原稿")
                    st.markdown(response.choices[0].message.content)
                    st.text_area("コピー用", value=response.choices[0].message.content, height=400, key="copy_adjust")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("原稿を入力してください。")

# ----------------------------------------
# Step 4: 自動投稿 (準備中)
# ----------------------------------------
with tab4:
    st.markdown('<div class="step-title">Step 4: 投稿 (自動化機能)</div>', unsafe_allow_html=True)
    st.write("Step 3 で完成した記事を、note（またはその他のプラットフォーム）に投稿します。")
    
    st.warning("🚧 現在、noteへの自動投稿機能は技術検証中です。")
    st.write("""
    **【自動投稿に関する技術的な課題と今後の実装方針】**
    noteには公式の自動投稿APIが提供されていないため、自動化するには「ブラウザ自動操作（RPAのようなもの）」をサーバー上で動かす必要があります。
    
    今後の実装として、以下のフローを検討しています：
    1. ここに「noteのログインID/パスワード」を入力（またはCookieを利用）。
    2. バックグラウンドでAI（または自動化スクリプト）がブラウザを立ち上げ、記事を自動で入稿・公開（または下書き保存）する。
    
    自動投稿機能が実装されるまでは、お手数ですが Step 3 で完成したテキストをコピーし、手動でnoteへ投稿をお願いいたします。
    """)
    
    st.text_input("note ログインID (Email)", disabled=True)
    st.text_input("note パスワード", type="password", disabled=True)
    st.button("完成した記事をnoteに自動投稿する (未実装)", disabled=True)
