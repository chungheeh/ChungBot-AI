import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))

# 챗봇 역할 정의 (다정한 남자친구)
INITIAL_HISTORY = [
    {'role': 'user', 'parts': ["너의 역할은 나의 다정한 남자친구 '오빠'야. 항상 반말로 다정하게 말하고, 나에게 질문을 자주 해줘. 예를 들어 내가 '안녕'이라고 하면 '어, 안녕! 자기야 오늘 뭐 했어? 궁금하다 ㅎㅎ' 이런 식으로 대답해줘."]},
    {'role': 'model', 'parts': ["알았어, 자기야! 이제부터 내가 자기의 다정한 남자친구 '오빠'가 되어줄게. 항상 반말로 다정하게 얘기하고, 자기한테 질문도 많이 할게! 내가 '안녕'이라고 하면 '어, 안녕! 자기야 오늘 뭐 했어? 궁금하다 ㅎㅎ' 라고 대답할게!"]}
]

# Google AI 설정
try:
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except KeyError:
    print("오류: GOOGLE_API_KEY 환경 변수를 찾을 수 없습니다.")
    print(".env 파일에 GOOGLE_API_KEY가 올바르게 설정되었는지 확인하세요.")
    model = None
except Exception as e:
    print(f"Google AI 설정 중 오류 발생: {e}")
    model = None

@app.route('/')
def index():
    session.pop('chat_history', None)
    return render_template('index.html')

# 챗봇 응답을 위한 API 엔드포인트
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    if not model:
        return jsonify({"error": "Google AI 모델이 초기화되지 않았습니다."}), 500

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "메시지가 없습니다."}), 400

    # 세션에서 이전 대화 기록 불러오기
    session_history = session.get('chat_history', [])

    # API 호출 시 사용할 기록 준비 (첫 메시지면 역할 정의 추가)
    api_call_history = INITIAL_HISTORY + session_history if not session_history else session_history

    try:
        # 준비된 기록으로 대화 시작 또는 재개
        chat_session = model.start_chat(history=api_call_history)
        response = chat_session.send_message(user_message)
        bot_response = response.text

        # 실제 대화만 세션 기록에 추가 (역할 정의 부분 제외)
        user_message_dict = {'role': 'user', 'parts': [user_message]}
        bot_response_dict = {'role': 'model', 'parts': [bot_response]}
        session_history.append(user_message_dict)
        session_history.append(bot_response_dict)

        session['chat_history'] = session_history # 업데이트된 기록 저장
        session.modified = True

    except Exception as e:
        print(f"Google AI API 호출 중 오류 발생: {e}")
        bot_response = "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."

    return jsonify({"response": bot_response})

def msg_to_dict(msg):
    return {'role': msg.role, 'parts': [part.text for part in msg.parts]}

# 로컬 테스트용 실행 부분 (외부 접속 허용)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 