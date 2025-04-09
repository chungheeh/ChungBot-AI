from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# 아래 부분은 로컬 테스트용이므로 그대로 둡니다.
# if __name__ == '__main__':
#     app.run(debug=True) 