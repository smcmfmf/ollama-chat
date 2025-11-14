# 💬 Ollama 챗봇 서비스
로컬 LLM(대규모 언어 모델) 실행 도구인 Ollama와 연동하여, 웹 브라우저에서 실시간으로 AI와 채팅할 수 있는 프로젝트입니다.

# 📋 프로젝트 개요
```
모델: Ollama에서 실행 중인 gemma3:4b
백엔드 : Flask
핵심 기능:
    1. /api/chat [POST]: 웹 프론트엔드로부터 채팅 메시지(model, messages)를 JSON으로 받습니다.
    2. Ollama 프록시: 받은 요청을 Ollama의 /api/chat 엔드포인트(http://host.docker.internal:11434)로 전달합니다.
    3. 스트리밍 응답: Ollama로부터 받은 응답(JSON Lines)을 클라이언트(웹 브라우저)로 즉시 스트리밍하여, 챗봇이 실시간으로 답변을 생성하는 것처럼 보이게 합니다.
    4. 웹 UI 제공: / 및 /2 경로를 통해 채팅 인터페이스 HTML(index2.html, index3.html)을 제공합니다.
```

# 🧰 기술 스택
```
Backend: Python, Flask
API 통신: requests (Ollama 서비스와 통신)
스트리밍: Flask의 stream_with_context, Response 객체
Frontend: HTML (templates/index2.html, templates/index3.html)
의존성: 로컬에서 실행 중인 Ollama model (ex. gemma3:4b, GPT5)
```

# 📁 레포지토리 구조
```
.
├── app.py              # Flask 웹 애플리케이션 실행 파일
├── templates/
│   ├── index2.html     # (경로 '/') 메인 채팅 UI 템플릿
│   └── index3.html     # (경로 '/2') 두 번째 채팅 UI 템플릿
└── README.md           # 프로젝트 요약
```

# 🛠️ 설치 및 사전 준비
## 1. (필수) Ollama 설치 및 모델 다운로드
```
1. Ollama 공식 웹사이트에서 Ollama를 다운로드하고 설치합니다.

2. 터미널을 열고 ollama를 실행하여 Ollama 서비스를 백그라운드에서 실행합니다.

3. app.py의 기본 모델인 gemma3:4b (또는 원하는 다른 모델)를 다운로드합니다.

Bash

ollama pull gemma3:4b
ollama run gemma3:4b
```

## 2. 프로젝트 설치
```

Bash

git clone [https://github.com/smcmfmf/ollama-chat.git]
cd ollama-chat

의존성 패키지 설치: (이 프로젝트의 필수 패키지입니다.)

Bash

pip install flask requests
```
# 🚀 사용 방법
## 1단계: Ollama (gemma3:4b) 실행 여부 확인
```
app.py는 OLLAMA_CHAT_URL = "http://host.docker.internal:11434/api/chat"로 설정되어 있습니다.

  1-1 ollama ps (현재 ollama에서 모델이 실행되고 있는지 확인하는 명령어)

# app.py

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
```

## 2단계: Flask 애플리케이션 실행
```
1. app.py를 실행합니다.

Bash

python app.py
서버가 실행되면 터미널에 다음과 같은 메시지가 나타납니다.

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## 3단계: 채팅하기
```
1. 웹 브라우저를 열고 http://127.0.0.1:5000/ 이나 localhost:5000/ (index2.html 템플릿) 또는 http://127.0.0.1:5000/2 이나 localhost:5000/2 (index3.html 템플릿) 주소로 이동합니다.

2. 웹페이지의 채팅창에 메시지를 입력하고 전송합니다.

Ollama 모델이 생성하는 답변이 실시간 스트리밍으로 화면에 표시되는 것을 확인할 수 있습니다.
```
