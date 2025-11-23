from flask import Flask, request, jsonify, render_template
import requests
import json
from difflib import get_close_matches
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# Set up your API keys
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
 

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# File path for knowledge base
KNOWLEDGE_BASE_FILE = 'knowledge_base.json'

# ============== GEMINI AI FUNCTION ==============

def get_gemini_response(user_message):
    """Get intelligent response from Gemini API with ALL 190 real exchange rates"""
    try:
        # Fetch ALL current exchange rates
        rates = get_exchange_rate('USD', EXCHANGE_API_KEY)
        
        # Create rate info string for ALL currencies
        rate_info = ""
        if rates:
            rate_info = "Current Exchange Rates (Base: 1 USD):\n"
            for currency, rate in rates.items():
                rate_info += f"{currency}: {rate}\n"
        
        prompt = f"""You are a helpful Currency Converter Chatbot with access to real-time exchange rates for 190 currencies.

{rate_info}

INSTRUCTIONS:
- When asked about ANY currency code (USD, INR, HUF, ZAR, BRL, etc.):
  1. Tell the full form of the currency
  2. Tell which country uses it
  3. Provide the REAL current exchange rate from the data above
- If user asks to convert amounts, calculate using the real rates
- If currency not found, say so politely
- Keep responses concise and friendly

User: {user_message}
Response:"""

        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having trouble right now. Please use the currency converter below!"

# ============== EXCHANGE RATE FUNCTIONS ==============

def get_exchange_rate(base_currency, api_key):
    try:
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}'
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code == 200 and 'conversion_rates' in data:
            return data['conversion_rates']
    except Exception as e:
        print(f"Exchange Rate API Error: {e}")
    return None

@app.route('/convert', methods=['GET'])
def convert_currency():
    amount = request.args.get('amount')
    base_currency = request.args.get('base_currency')
    target_currency = request.args.get('target_currency')

    if not amount or not base_currency or not target_currency:
        return jsonify({'success': False, 'error': 'Invalid parameters'}), 400

    try:
        amount = float(amount)
        rates = get_exchange_rate(base_currency, EXCHANGE_API_KEY)
        rate = rates.get(target_currency) if rates else None

        if rate:
            result = amount * rate
            return jsonify({'success': True, 'result': f'{result:.2f} {target_currency}'})
        else:
            return jsonify({'success': False, 'error': 'Unable to get exchange rate'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============== KNOWLEDGE BASE FUNCTIONS ==============

def load_knowledge_base():
    if os.path.exists(KNOWLEDGE_BASE_FILE):
        with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {"questions": []}

def save_knowledge_base(data):
    with open(KNOWLEDGE_BASE_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def find_best_match(user_question, questions):
    matches = get_close_matches(user_question.lower(), [q.lower() for q in questions], n=1, cutoff=0.6)
    if matches:
        for q in questions:
            if q.lower() == matches[0]:
                return q
    return None

def get_answer_for_question(question, knowledge_base):
    for q in knowledge_base.get("questions", []):
        if q.get("question").lower() == question.lower():
            return q.get("answer")
    return None

# ============== CHAT ENDPOINT ==============

@app.route('/learning_chat', methods=['POST'])
def learn_chatbot():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    
    knowledge_base = load_knowledge_base()

    # Try knowledge base first
    if knowledge_base.get("questions"):
        questions_list = [q["question"] for q in knowledge_base["questions"]]
        best_match = find_best_match(user_message, questions_list)

        if best_match:
            answer = get_answer_for_question(best_match, knowledge_base)
            return jsonify({'success': True, 'response': answer})
    
    # No match - use Gemini
    gemini_response = get_gemini_response(user_message)
    return jsonify({'success': True, 'response': gemini_response})

# ============== CURRENCIES ENDPOINT ==============

@app.route('/currencies', methods=['GET'])
def get_currencies():
    rates = get_exchange_rate('USD', EXCHANGE_API_KEY)
    if rates:
        currencies = list(rates.keys())
        return jsonify({'success': True, 'currencies': currencies})
    else:
        # Fallback: Return common currencies if API fails
        fallback_currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 
                               'NZD', 'SEK', 'KRW', 'SGD', 'NOK', 'MXN', 'BRL', 'ZAR', 'RUB', 'AED']
        return jsonify({'success': True, 'currencies': fallback_currencies})

@app.route('/')
def serve_index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)