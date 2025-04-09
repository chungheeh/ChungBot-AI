import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))

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

    chat_history = session.get('chat_history', [])

    try:
        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message(user_message)
        bot_response = response.text

        session['chat_history'] = [msg_to_dict(m) for m in chat_session.history]
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