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

# セッションステートの初期化
if "writer_profile" not in st.session_state:
    st.session_state.writer_profile = ""
if "adjusted_article" not in st.session_state:
    st.session_state.adjusted_article = ""

# ----------------------------------------
# Step 3: AIによる調整 (校閲 + 文体学習)
# ----------------------------------------
with tab3:
    st.markdown('<div class="step-title">Step 3: AIによる調整 & 文体学習</div>', unsafe_allow_html=True)
    st.write("Step 2 で書き上げた原稿を整えると同時に、**ライター（ご友人）特有の口調や言い回しの癖をAIが分析・学習**します。")
    
    adjust_input = st.text_area("調整する原稿（下書き）", height=300, placeholder="Step 2で書いた原稿を貼り付けてください...", key="adjust_input")
    
    # 蓄積された文体プロファイルを表示
    with st.expander("📝 現在学習済みのライターの癖（ストック）", expanded=True):
        profile_text = st.text_area(
            "このストックは、今後の調整時に「筆者らしさ」を保つための指示書としてAIに引き継がれます。", 
            value=st.session_state.writer_profile, 
            height=150, 
            key="profile_display"
        )
        if st.button("ストックを保存/更新", key="update_profile"):
            st.session_state.writer_profile = st.session_state.profile_display
            st.success("ストックを更新しました。")

    if st.button("AIによる調整 ＆ 癖の分析を実行", key="btn_adjust"):
        if adjust_input:
            with st.spinner("AIが原稿の熱量を保って調整しつつ、文体を分析しています...（数十秒かかります）"):
                # プロンプト1: 原稿のブラッシュアップ (学習済みの癖を反映)
                prompt_adjust = f"""
あなたはプロの編集者（校閲・ブラッシュアップ担当）です。
以下のテキストは、元ランカー（夜職）のクライアントが書いたnote記事の原稿（下書き）です。

【現在までに学習したクライアントの文体・口調の癖】
{st.session_state.writer_profile if st.session_state.writer_profile else "まだ学習データはありません。"}

上記の「癖」を最大限に活かし、筆者独自の筆致や熱量を絶対に殺さずに、以下の条件で原稿をブラッシュアップしてください。
1. スマホで読まれることを前提とし、適度な改行、箇条書き、太字装飾を加えること。
2. 誤字脱字、明らかな文法エラーのみ修正すること。
3. 出力はブラッシュアップ後の「完成版の記事本文」のみとすること。

【クライアントの原稿】
{adjust_input}
"""
                # プロンプト2: 文体と癖の抽出・学習
                prompt_analyze = f"""
あなたは優秀なプロファイラーです。
以下のテキストから、筆者（夜職経験者）特有の「口調」「言い回し」「感情表現の癖」「よく使う語彙」を分析し、箇条書きで抽出してください。
この出力結果は、今後別のAIが文章を代筆・編集する際の「文体再現用プロンプト」として再利用されます。簡潔に、特徴のみをリストアップしてください。

【対象テキスト】
{adjust_input}
"""
                try:
                    # 並行してAPIを叩く
                    import concurrent.futures
                    
                    def call_api(prompt_text):
                        return client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a professional editor and profiler."},
                                {"role": "user", "content": prompt_text}
                            ],
                            temperature=0.7
                        )
                        
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_adjust = executor.submit(call_api, prompt_adjust)
                        future_analyze = executor.submit(call_api, prompt_analyze)
                        
                        resp_adjust = future_adjust.result()
                        resp_analyze = future_analyze.result()
                    
                    adjusted_text = resp_adjust.choices[0].message.content
                    new_profile = resp_analyze.choices[0].message.content
                    
                    # 結果をセッションステートに保存
                    st.session_state.adjusted_article = adjusted_text
                    # 既存のプロファイルに新しく学習した癖を追記
                    if st.session_state.writer_profile:
                        st.session_state.writer_profile += "\n\n【追加学習分】\n" + new_profile
                    else:
                        st.session_state.writer_profile = new_profile
                        
                    st.success("調整と文体分析が完了しました！ (Step 4 で投稿用のフォーマットを出力できます)")
                    
                    st.markdown("### 完成版の原稿")
                    st.text_area("コピー用", value=adjusted_text, height=400, key="copy_adjust")
                    
                    st.markdown("### 🧠 今回抽出された「ライターの癖」")
                    st.info(new_profile)
                    st.write("※抽出された癖は、上部のストックに自動的に蓄積されました。")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("原稿を入力してください。")

# ----------------------------------------
# Step 4: 投稿 (コピペ用出力)
# ----------------------------------------
with tab4:
    st.markdown('<div class="step-title">Step 4: note投稿用データ (コピペ用)</div>', unsafe_allow_html=True)
    st.write("Step 3 で完成した記事をもとに、noteの各入力欄に最低限のコピペで投稿できるよう、データを整形して出力します。")
    
    if st.button("note用コピペデータを生成", key="btn_format"):
        if not st.session_state.adjusted_article:
            st.warning("先に Step 3 で記事の調整を完了させてください。")
        else:
            with st.spinner("note用のタイトル、ハッシュタグ等を生成しています..."):
                prompt = f"""
あなたはnoteのバズアルゴリズムに精通した編集者です。
以下の完成版記事をもとに、noteへ投稿するための「各入力欄のデータ」を生成してください。

【出力フォーマット】
以下の区切り文字を用いて出力してください。
---TITLE---
(30文字前後で、クリックしたくなる魅力的なタイトル案を1つ)
---TAGS---
(カンマ区切りで、noteで検索されやすいハッシュタグを3〜5つ。#は不要)
---BODY---
(以下の完成版記事をそのまま出力、ただし必要なら文末に有料ラインへの自然な誘導を一言添える)

【完成版記事】
{st.session_state.adjusted_article}
"""
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a professional note editor."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    
                    result_text = response.choices[0].message.content
                    
                    # 簡易パース
                    title = ""
                    tags = ""
                    body = ""
                    
                    if "---TITLE---" in result_text:
                        parts = result_text.split("---TITLE---")
                        if "---TAGS---" in parts[1]:
                            sub_parts = parts[1].split("---TAGS---")
                            title = sub_parts[0].strip()
                            if "---BODY---" in sub_parts[1]:
                                tag_body_parts = sub_parts[1].split("---BODY---")
                                tags = tag_body_parts[0].strip()
                                body = tag_body_parts[1].strip()
                            
                    st.success("コピペ用データの生成が完了しました！noteの投稿画面にそのまま貼り付けてください。")
                    
                    st.markdown("#### 🏷️ タイトル (noteの「記事タイトル」欄へ)")
                    st.text_input("タイトル", value=title, key="copy_title", label_visibility="collapsed")
                    
                    st.markdown("#### 📝 本文 (noteの「本文」欄へ)")
                    st.text_area("本文", value=body if body else st.session_state.adjusted_article, height=400, key="copy_final_body", label_visibility="collapsed")
                    
                    st.markdown("#### #️⃣ ハッシュタグ (noteの「ハッシュタグ」欄へ)")
                    st.text_input("ハッシュタグ", value=tags, key="copy_tags", label_visibility="collapsed")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
