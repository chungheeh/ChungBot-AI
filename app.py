import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()

app = Flask(__name__)

# Google AI 설정
try:
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    chat = model.start_chat(history=[])
except KeyError:
    print("오류: GOOGLE_API_KEY 환경 변수를 찾을 수 없습니다.")
    print(".env 파일에 GOOGLE_API_KEY가 올바르게 설정되었는지 확인하세요.")
    model = None
    chat = None
except Exception as e:
    print(f"Google AI 설정 중 오류 발생: {e}")
    model = None
    chat = None

@app.route('/')
def index():
    return render_template('index.html')

# 챗봇 응답을 위한 API 엔드포인트
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    if not model or not chat:
        return jsonify({"error": "Google AI 모델이 초기화되지 않았습니다."}), 500

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "메시지가 없습니다."}), 400

    try:
        # Google AI 모델에 메시지 전송 및 응답 받기
        response = chat.send_message(user_message)
        bot_response = response.text
    except Exception as e:
        print(f"Google AI API 호출 중 오류 발생: {e}")
        bot_response = "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."

    return jsonify({"response": bot_response})

# 로컬 테스트용 실행 부분 (외부 접속 허용)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 