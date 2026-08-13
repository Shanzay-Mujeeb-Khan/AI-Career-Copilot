import requests


GROQ_API_KEY = "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"

def ask_ai(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional career copilot. Provide customized, detailed career analysis based strictly on the user query or resume."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        res_json = response.json()
        if response.status_code == 200:
            return res_json['choices'][0]['message']['content']
        else:
            return f"API Error ({response.status_code}): {res_json.get('error', {}).get('message', 'Failed to process request')}"
    except Exception as e:
        return f"Connection Error: {str(e)}"