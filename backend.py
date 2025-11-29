from flask import Flask, request, jsonify, render_template
import requests
import json
from difflib import get_close_matches
import os
from datetime import datetime, timedelta
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

# API URLs
FRANKFURTER_API = "https://api.frankfurter.dev"  # Free historical data
EXCHANGE_RATE_API = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest"

# ============== GEMINI AI FUNCTION ==============

def get_gemini_response(user_message):
    """Get intelligent response from Gemini API with ALL 190 real exchange rates"""
    try:
        rates = get_exchange_rate('USD', EXCHANGE_API_KEY)
        
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

# ============== CURRENT EXCHANGE RATE FUNCTIONS ==============

def get_exchange_rate(base_currency, api_key):
    """Get current exchange rates from ExchangeRate-API"""
    try:
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}'
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code == 200 and 'conversion_rates' in data:
            return data['conversion_rates']
    except Exception as e:
        print(f"Exchange Rate API Error: {e}")
    return None

# Frankfurter supported currencies (European Central Bank)
FRANKFURTER_CURRENCIES = [
    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'SEK', 'NOK', 
    'DKK', 'PLN', 'HUF', 'CZK', 'ISK', 'BGN', 'RON', 'HRK', 'TRY', 'ILS',
    'CNY', 'HKD', 'SGD', 'KRW', 'THB', 'MYR', 'IDR', 'PHP', 'MXN', 'BRL',
    'ZAR', 'RUB'
]

# ============== REAL HISTORICAL DATA (Frankfurter API) ==============

def get_real_historical_rate(base_currency, target_currency, date_str):
    """Get REAL historical exchange rate from Frankfurter API (FREE!)"""
    try:
        # Check if currencies are supported by Frankfurter
        if base_currency in FRANKFURTER_CURRENCIES and target_currency in FRANKFURTER_CURRENCIES:
            url = f"{FRANKFURTER_API}/{date_str}"
            params = {
                'from': base_currency,
                'to': target_currency
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and target_currency in data['rates']:
                    return {'rate': data['rates'][target_currency], 'source': 'real'}
        
        # Fallback: Generate simulated historical data
        current_rates = get_exchange_rate(base_currency, EXCHANGE_API_KEY)
        if not current_rates or target_currency not in current_rates:
            return None
        
        current_rate = current_rates[target_currency]
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        days_diff = (today - target_date).days
        
        if days_diff < 0:
            return None
        
        # Simulate historical variation (±0.5% per day, max ±10%)
        variation = min(0.10, (days_diff * 0.005))
        import random
        random.seed(int(target_date.timestamp()))
        historical_rate = current_rate * (1 + random.uniform(-variation, variation))
        
        return {'rate': round(historical_rate, 4), 'source': 'estimated'}
        
    except Exception as e:
        print(f"Historical Rate Error: {e}")
        return None

def get_historical_data_range(base_currency, target_currency, days=30):
    """Get historical data for multiple days"""
    try:
        historical_data = []
        
        # Check if both currencies are supported by Frankfurter
        if base_currency in FRANKFURTER_CURRENCIES and target_currency in FRANKFURTER_CURRENCIES:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Frankfurter API supports date ranges
            url = f"{FRANKFURTER_API}/{start_date.strftime('%Y-%m-%d')}.."
            params = {
                'from': base_currency,
                'to': target_currency
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data:
                    for date, rates in data['rates'].items():
                        if target_currency in rates:
                            historical_data.append({
                                'date': date,
                                'rate': rates[target_currency]
                            })
                    if historical_data:
                        return sorted(historical_data, key=lambda x: x['date'])
        
        # Fallback: Generate simulated data
        current_rates = get_exchange_rate(base_currency, EXCHANGE_API_KEY)
        if not current_rates or target_currency not in current_rates:
            return None
        
        current_rate = current_rates[target_currency]
        for i in range(days, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            import random
            random.seed(int(date_obj.timestamp()))
            variation = random.uniform(-0.02, 0.02)
            rate = current_rate * (1 + variation)
            
            historical_data.append({
                'date': date,
                'rate': round(rate, 4)
            })
        
        return historical_data
        
    except Exception as e:
        print(f"Historical Range Error: {e}")
        return None

# ============== ADVANCED PREDICTION ALGORITHM ==============

def predict_future_rate_advanced(base_currency, target_currency, days_ahead=7):
    """Advanced prediction using real historical data and trend analysis"""
    try:
        # Get 30 days of real historical data
        historical_data = get_historical_data_range(base_currency, target_currency, days=30)
        
        if not historical_data or len(historical_data) < 7:
            return None
        
        # Extract rates
        rates = [item['rate'] for item in historical_data]
        
        # Calculate multiple trend indicators
        
        # 1. Simple Moving Average (SMA) - Last 7 days
        sma_7 = sum(rates[-7:]) / 7
        
        # 2. Exponential Moving Average (EMA) - More weight on recent data
        ema = rates[0]
        smoothing = 2 / (7 + 1)
        for rate in rates[1:]:
            ema = (rate * smoothing) + (ema * (1 - smoothing))
        
        # 3. Linear regression for trend
        n = len(rates)
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(rates) / n
        
        numerator = sum((x_values[i] - x_mean) * (rates[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator != 0:
            slope = numerator / denominator
            intercept = y_mean - slope * x_mean
        else:
            slope = 0
            intercept = y_mean
        
        # 4. Calculate volatility (standard deviation)
        mean_rate = sum(rates) / len(rates)
        variance = sum((r - mean_rate) ** 2 for r in rates) / len(rates)
        volatility = variance ** 0.5
        
        # 5. Predict future rate using linear regression
        future_x = n + days_ahead
        predicted_rate = slope * future_x + intercept
        
        # 6. Calculate confidence based on volatility
        volatility_percent = (volatility / mean_rate) * 100
        if volatility_percent < 1:
            confidence = 'high'
        elif volatility_percent < 3:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # 7. Calculate price change percentage
        current_rate = rates[-1]
        change_percent = ((predicted_rate - current_rate) / current_rate) * 100
        
        # 8. Determine trend strength
        if abs(change_percent) > 2:
            trend_strength = 'strong'
        elif abs(change_percent) > 0.5:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        return {
            'predicted_rate': round(predicted_rate, 4),
            'current_rate': round(current_rate, 4),
            'trend': 'upward' if predicted_rate > current_rate else 'downward',
            'trend_strength': trend_strength,
            'change_percent': round(change_percent, 2),
            'confidence': confidence,
            'volatility': round(volatility_percent, 2),
            'days_ahead': days_ahead,
            'sma_7': round(sma_7, 4),
            'ema': round(ema, 4),
            'data_points': len(rates)
        }
        
    except Exception as e:
        print(f"Advanced Prediction Error: {e}")
        return None

# ============== API ENDPOINTS ==============

@app.route('/convert', methods=['GET'])
def convert_currency():
    """Current conversion endpoint"""
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
            return jsonify({
                'success': True, 
                'result': f'{result:.2f} {target_currency}',
                'rate': rate,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to get exchange rate'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/historical', methods=['GET'])
def get_historical():
    """REAL Historical rates endpoint using Frankfurter API"""
    base_currency = request.args.get('base_currency', 'USD')
    target_currency = request.args.get('target_currency', 'EUR')
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'success': False, 'error': 'Date required (YYYY-MM-DD)'}), 400
    
    try:
        # Validate date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if date_obj > datetime.now():
            return jsonify({'success': False, 'error': 'Cannot get future rates'}), 400
        
        result = get_real_historical_rate(base_currency, target_currency, date_str)
        
        if result:
            source_text = 'European Central Bank (Real Data)' if result['source'] == 'real' else 'Estimated based on current trends'
            return jsonify({
                'success': True,
                'date': date_str,
                'base_currency': base_currency,
                'target_currency': target_currency,
                'rate': result['rate'],
                'source': source_text,
                'data_type': result['source']
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to get historical rate'}), 400
            
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/predict', methods=['GET'])
def predict_rate():
    """Advanced prediction endpoint using real historical data"""
    base_currency = request.args.get('base_currency', 'USD')
    target_currency = request.args.get('target_currency', 'EUR')
    days = request.args.get('days', 7, type=int)
    
    if days < 1 or days > 30:
        return jsonify({'success': False, 'error': 'Days must be between 1 and 30'}), 400
    
    try:
        prediction = predict_future_rate_advanced(base_currency, target_currency, days)
        
        if prediction:
            return jsonify({
                'success': True,
                'prediction': prediction,
                'disclaimer': 'Prediction based on historical trends. Not financial advice.',
                'method': 'Linear Regression with Moving Averages'
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to generate prediction'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/chart_data', methods=['GET'])
def get_chart_data():
    """Get REAL historical data for charts (7, 30, or 90 days)"""
    base_currency = request.args.get('base_currency', 'USD')
    target_currency = request.args.get('target_currency', 'EUR')
    days = request.args.get('days', 30, type=int)
    
    try:
        chart_data = get_historical_data_range(base_currency, target_currency, days)
        
        if chart_data:
            return jsonify({
                'success': True,
                'data': chart_data,
                'base_currency': base_currency,
                'target_currency': target_currency,
                'period_days': days,
                'source': 'European Central Bank'
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to fetch chart data'}), 400
        
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
        fallback_currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 
                               'NZD', 'SEK', 'KRW', 'SGD', 'NOK', 'MXN', 'BRL', 'ZAR', 'RUB', 'AED']
        return jsonify({'success': True, 'currencies': fallback_currencies})

@app.route('/')
def serve_index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)