from flask import Flask, request, jsonify, Response, stream_with_context, render_template
import requests
import json
import os
import threading

OLLAMA_HOST = "http://host.docker.internal:11434"
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"

MEMORY_FILE = "user_memory.txt"

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/2")
def index2():
    return render_template("index2.html")

def get_memory():
    """저장된 사용자 기억을 불러옵니다."""
    if not os.path.exists(MEMORY_FILE):
        return ""
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

def update_memory_task(model, user_input):
    """
    [백그라운드 작업]
    사용자 입력에서 '중요한 정보'가 발견될 때만 기억을 업데이트합니다.
    모든 프롬프트는 한국어로 작성되어, 기억도 한국어로 저장됩니다.
    """
    
    extraction_prompt = f"""
    역할: 당신은 사용자의 대화 내용을 분석하여 중요한 정보를 추출하는 '기억 관리자'입니다.
    
    사용자 입력: "{user_input}"
    
    지시사항:
    1. 위 '사용자 입력'을 분석하여 사용자에 대한 구체적인 사실(이름, 취미, 선호도, 일정, 특징 등)이 포함되어 있는지 판단하세요.
    2. 기억할 만한 가치가 있는 정보라면, 그 사실을 간결한 '한국어 문장'으로 출력하세요. (예: "사용자는 매운 음식을 좋아한다.")
    3. 만약 단순한 인사("안녕"), 감탄사("그래요?")) 등 기억할 가치가 없는 내용이라면, 오직 "없음" 이라고만 출력하세요.
    4. 설명이나 다른 말은 덧붙이지 말고, 오직 결과만 출력하세요.
    """
    
    try:
        check_response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": extraction_prompt,
                "stream": False,
                "options": {"temperature": 2}
            },
            timeout=30
        )
        
        if check_response.status_code != 200:
            return

        extracted_info = check_response.json().get("response", "").strip()
        
        if "없음" in extracted_info or len(extracted_info) < 2:
            # print(f"무시됨 (정보 없음): {user_input}")
            return

        print(f"💡 중요 정보 감지됨: {extracted_info}")

        current_memory = get_memory()
        
        merge_prompt = f"""
        역할: 당신은 사용자의 장기 기억을 관리하는 비서입니다.
        
        [기존 기억]:
        {current_memory if current_memory else "(아직 기억 없음)"}
        
        [새로운 정보]:
        {extracted_info}
        
        지시사항:
        1. [새로운 정보]를 [기존 기억]에 추가하여 하나로 정리된 기억 목록을 만드세요.
        2. 만약 [새로운 정보]가 [기존 기억]과 충돌한다면, 최신 정보인 [새로운 정보]를 기준으로 내용을 수정하세요.
        3. 내용은 반드시 '한국어'로 작성하고, 읽기 쉽게 개조식(bullet points)으로 요약하세요.
        4. 오직 정리된 기억 내용만 출력하세요.
        """
        
        merge_response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": merge_prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        
        if merge_response.status_code == 200:
            new_memory = merge_response.json().get("response", "").strip()
            if new_memory:
                with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                    f.write(new_memory)
                print("기억 파일 업데이트 완료.")

    except Exception as e:
        print(f"기억 업데이트 중 오류 발생: {e}")

@app.post("/api/chat")
def chat_stream():
    body = request.get_json(force=True, silent=True) or {}
    model = body.get("model", "gemma3:4b")
    messages = body.get("messages", [])
    options = body.get("options")

    user_memory = get_memory()

    system_content = "당신은 유능하고 친절한 AI 비서입니다. 한국어로 자연스럽게 대화하세요."
    
    if user_memory:
        system_content += f"\n\n[사용자에 대해 기억된 정보]:\n{user_memory}\n\n위 정보를 참고하여 사용자와 대화하세요. (단, '메모를 읽었다'는 티를 내지 말고 자연스럽게 아는 척하세요.)"

    if messages and messages[0].get('role') == 'system':
        messages[0]['content'] = system_content + " " + messages[0]['content']
    else:
        messages.insert(0, {"role": "system", "content": system_content})

    try:
        upstream = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": model,
                "messages": messages,
                "stream": True,
                **({"options": options} if options else {}),
            },
            stream=True,
            timeout=600,
        )
        upstream.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    last_user_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
    
    if last_user_msg:
        threading.Thread(target=update_memory_task, args=(model, last_user_msg)).start()

    def generate():
        for line in upstream.iter_lines():
            if not line:
                continue
            yield line + b"\n"

    return Response(stream_with_context(generate()), mimetype="application/x-ndjson")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)