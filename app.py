from flask import Flask, render_template, url_for , request
from openai import OpenAI
import re

# FlaskとOpenAIのモジュールを利用しています。
# 以下のコマンドでモジュールをインストールして利用してください。
# $ pip install Flask
# $ pip install OpenAI


# 過去処理の記録 面倒なのでglobal変数を利用。セッション変数にホントはすべき
previous_response = '' 

# Webページからのアクセス時の動作を制御 ----------------------------------------------------------------
app = Flask(__name__)

# "/"にアクセスした際に実行される処理
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# ボタンを押した際に実行される処理
@app.route('/', methods=['POST'])
def form():
    project = request.form['field']
    # debug_modeをFalseにするとChatGPTに問い合わせます。料金がかかるので必要ないときはTrueにしておいてください。
    wbslist = getWBS(project,debug_mode=True)
    return render_template('index.html' \
                           , data=wbslist)

# "/description"にアクセスした際に実行される処理
@app.route('/description', methods=['GET'])
def description():
    return render_template('description.html')
#---------------------------------------------------------------------------------------------------- 


def getWBS(project, debug_mode=True ):
    global previous_response #面倒なのでglobal変数を利用。セッション変数にホントはすべき

   # テスト用のデータ
    response = '''
[WBS]"taskname":"キャンペーン計画作成","hierarchy":1,"dateRequired":4
[WBS]"taskname":"市場調査","hierarchy":2,"dateRequired":3
[WBS]"taskname":"競合分析","hierarchy":3,"dateRequired":1
[WBS]"taskname":"顧客ニーズ調査","hierarchy":3,"dateRequired":1
[WBS]"taskname":"市場トレンド調査","hierarchy":3,"dateRequired":1
[WBS]"taskname":"ターゲットオーディエンス設定","hierarchy":2,"dateRequired":3
[WBS]"taskname":"デモグラフィック分析","hierarchy":3,"dateRequired":1
[WBS]"taskname":"ペルソナ作成","hierarchy":3,"dateRequired":2
[WBS]"taskname":"予算策定","hierarchy":2,"dateRequired":2
[WBS]"taskname":"コスト見積もり","hierarchy":3,"dateRequired":1
[WBS]"taskname":"予算配分計画","hierarchy":3,"dateRequired":1
[WBS]"taskname":"キャンペーンコンテンツ作成","hierarchy":2,"dateRequired":5
[WBS]"taskname":"スローガン作成","hierarchy":3,"dateRequired":2
[WBS]"taskname":"ビジュアルデザイン作成","hierarchy":3,"dateRequired":3
[WBS]"taskname":"メディアプランニング","hierarchy":2,"dateRequired":4
[WBS]"taskname":"メディア選定","hierarchy":3,"dateRequired":2
[WBS]"taskname":"スケジュール作成","hierarchy":3,"dateRequired":2
[WBS]"taskname":"広告素材作成","hierarchy":2,"dateRequired":7
[WBS]"taskname":"グラフィックデザイン作成","hierarchy":3,"dateRequired":4
[WBS]"taskname":"コピーライティング","hierarchy":3,"dateRequired":3
[WBS]"taskname":"メディアバイイング","hierarchy":2,"dateRequired":3
[WBS]"taskname":"交渉と契約","hierarchy":3,"dateRequired":2
[WBS]"taskname":"メディア掲載","hierarchy":3,"dateRequired":1
[WBS]"taskname":"キャンペーン実行","hierarchy":2,"dateRequired":10
[WBS]"taskname":"キャンペーンローンチ","hierarchy":3,"dateRequired":1
[WBS]"taskname":"進捗管理","hierarchy":3,"dateRequired":7
[WBS]"taskname":"効果測定","hierarchy":3,"dateRequired":2
[WBS]"taskname":"結果分析とレポート作成","hierarchy":2,"dateRequired":3
[WBS]"taskname":"データ集計","hierarchy":3,"dateRequired":1
[WBS]"taskname":"効果分析","hierarchy":3,"dateRequired":1
[WBS]"taskname":"最終レポート作成","hierarchy":3,"dateRequired":1
'''

    # プロンプト
    prompt = project 

    # どのような事をしたいのかの説明 ★特にここをチューニングすること
    system_context = '''
- 指定されたプロジェクトのWBSを出力してください
- project managementのプロフェッショナルとして詳細なWBSを洗い出して下さい
- ビジネスの文脈で利用するものです。
- 以下のフォーマットに従い、リストとして表示してください。
- "" や [] で囲まれたところは固定値です。変更しないように注意してください。

#format 
[WBS]"taskname":"テスト","hierarchy":1,"dateRequired":4
[WBS]"taskname":"テスト","hierarchy":2,"dateRequired":4
'''
    # 前回のプロンプトの結果など。文脈情報を提供
    user_context = '前回の問い合わせ結果です。参考にしてください' + previous_response

    if debug_mode == False:
        response = get_chatgpt_response(prompt,system_context,user_context)
        previous_response = response
        print(response)

    wbslist = []
    # 正規表現パターンを作成
    pattern = r'\[WBS\]"taskname":"(?P<taskname>.*?)","hierarchy":(?P<hierarchy>\d+),"dateRequired":(?P<dateRequired>\d+)'
    for line in response.strip().split('\n'):
        match = re.match(pattern, line)
        if match:
            wbs_dict = match.groupdict()  # マッチした部分を辞書に変換
            wbs_dict['hierarchy'] = int(wbs_dict['hierarchy'])  # hierarchyを整数に変換
            wbs_dict['dateRequired'] = int(wbs_dict['dateRequired'])  # dateRequiredを整数に変換
            wbslist.append(wbs_dict)  # リストに追加
        for wbs in wbslist:
            print(wbs)
    return wbslist


def get_chatgpt_response(prompt,system_context,user_context):
    client = OpenAI()
    response =  client.chat.completions.create(
        model="gpt-4o",  
        messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_context},
                {"role": "user", "content": prompt}
                  ]
    )
    return response.choices[0].message.content.strip()


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')