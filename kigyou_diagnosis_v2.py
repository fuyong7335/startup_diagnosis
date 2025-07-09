import streamlit as st
import plotly.graph_objects as go
from openai import OpenAI

# --- OpenAI API キー設定（Secretsから取得） ---
client = OpenAI(api_key=st.secrets["openai_api_key"])

# --- ページ設定 ---
st.set_page_config(page_title="起業タイプ診断", layout="centered")
st.title("起業タイプ診断")
st.write("以下の質問に、スライダーであなたの気持ちの度合いを選んでください。スライダー上の位置に 1〜5 の数字が表示されます。")

# --- 質問セット ---
question_set = {
    "性格傾向": [
        "新しいことを自分で調べて試すことが多い",
        "初対面の人と自然に会話を楽しめる方だ",
        "計画を立ててから行動したいと思う",
        "自分の直感を頼りに決断することがある",
        "何か失敗したとき、自分の責任だと考えやすい"
    ],
    "価値観": [
        "自由な働き方を重視したいと感じる",
        "人に感謝されることでやりがいを感じる",
        "ルールが多いとストレスを感じる",
        "お金よりも、自分が納得できる仕事を優先したい",
        "仕事は成長の場だと考えている"
    ],
    "本気度": [
        "起業について以前から考え続けている",
        "今が行動を起こすタイミングだと思う",
        "不安があってもチャレンジしたい気持ちがある",
        "すでに何らかの準備や調査を始めている",
        "環境が整えばすぐにでも始めたいと感じる"
    ],
    "仕事スタイル": [
        "一人で計画を実行することに抵抗が少ない",
        "マイペースに仕事を進めるのが心地よい",
        "困ったときは自分で解決策を考えることが多い",
        "集中して自分の世界に没頭する時間が好きだ",
        "チームより個人での裁量を重視したい"
    ],
    "思考の癖": [
        "どうせ私には無理だと思うことがある",
        "うまくいかないとき、自分を責めることが多い",
        "他人と比べて落ち込むことがよくある",
        "失敗を恐れて行動できないことがある",
        "本当はやりたいのに一歩が踏みだせないことがある"
    ]
}

# --- 回答フォーム ---
responses = {}
with st.form("diagnosis_form"):
    q_num = 1
    for category, questions in question_set.items():
        st.markdown(f"### {category}")
        for question in questions:
            reverse = (category == "思考の癖")
            responses[q_num] = 6 - st.slider(
                label=f"No.{q_num} {question}",
                min_value=1,
                max_value=5,
                step=1,
                format="%d",
                key=f"Q{q_num}"
            ) if reverse else st.slider(
                label=f"No.{q_num} {question}",
                min_value=1,
                max_value=5,
                step=1,
                format="%d",
                key=f"Q{q_num}"
            )
            q_num += 1
    submitted = st.form_submit_button("診断する")

# --- 結果処理 ---
if submitted:
    # スコア計算
    scores = {}
    idx = 1
    for category in question_set:
        total = 0
        for _ in range(5):
            total += responses[idx]
            idx += 1
        avg = total / 5
        scores[category] = int((avg - 1) * 25)

    # レーダーチャート
    cats = list(scores.keys())
    vals = list(scores.values())
    cats.append(cats[0])
    vals.append(vals[0])
    fig = go.Figure(data=[go.Scatterpolar(r=vals, theta=cats, fill='toself')],
                    layout=go.Layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False))
    st.subheader("あなたの起業傾向レーダーチャート")
    st.plotly_chart(fig)

    # --- AIによるコメント生成 ---
    prompt = """
あなたはキャリアコーチです。
以下はクライアントの起業傾向スコアです。
各カテゴリに対して、1）共感や受容を示すひとこと、2）次の一歩を後押しするアドバイス、をセットで日本語で返してください。
"""
    for cat, score in scores.items():
        prompt += f"\n{cat}: {score}/100"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは、クライアントの回答傾向から性格や価値観、思考のパターンを的確に分析し、起業に必要な視点や可能性を見出して具体的な行動提案を行うビジネス視点を持ったキャリアコンサルタントです。診断結果に基づき、率直かつ建設的にアドバイスを伝えてください。"},
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content
    st.markdown("---")
    st.subheader("AIからのフィードバック")
    st.write(reply)

    st.markdown("---")
    st.write("必要に応じてサポートをご案内することもできます。あなたの強みと課題が見えてきた今、次の一歩をご一緒に考えていきましょうね")
