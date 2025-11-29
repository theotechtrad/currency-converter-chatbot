# Currency Converter Chatbot 💱

A full-stack currency conversion platform with AI-powered chat, real-time exchange rates for 190+ currencies, historical data analysis, and future rate prediction.

## Live Demo

🔗 [Currency Converter Chatbot](https://currencyconverterchatbot.pythonanywhere.com/)

## Features

**Core Currency Conversion:**
- Real-time exchange rates for 190+ global currencies
- Quick conversion between any currency pairs
- Current rates via ExchangeRate-API
- Currency symbols and emoji indicators

**AI-Powered Chatbot:**
- Natural language processing with Gemini AI
- Ask about any currency code (USD, INR, EUR, etc.)
- Get currency full forms and countries
- Conversational currency information
- Learning knowledge base for common queries

**Historical Rate Checker:**
- View past exchange rates for any date
- Real data from European Central Bank (Frankfurter API)
- Covers major currencies (USD, EUR, GBP, JPY, etc.)
- Estimated data for other currencies
- Date picker with validation

**Future Rate Prediction:**
- Predict rates 1-30 days ahead
- Linear regression analysis
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Trend strength indicators
- Confidence levels based on volatility
- Real historical data for accuracy

**User Interface:**
- 3 intuitive tabs (Current, History, Predict)
- Responsive design for mobile and desktop
- Animated currency symbols
- Clean, modern layout
- Real-time conversion results

## Tech Stack

**Backend:**
- Flask 3.1.2
- Google Gemini AI API
- ExchangeRate-API (190+ currencies)
- Frankfurter API (historical data)

**Frontend:**
- HTML5 & CSS3
- Vanilla JavaScript
- Responsive design
- No frameworks

**APIs:**
- ExchangeRate-API for current rates
- Google Generative AI (Gemini)
- Frankfurter (European Central Bank data)

**Deployment:**
- PythonAnywhere hosting
- Python-dotenv for config

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/theotechtrad/currency-converter-chatbot.git
cd currency-converter-chatbot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup environment variables**

Create a `.env` file:
```env
EXCHANGE_API_KEY=your_exchangerate_api_key
GEMINI_API_KEY=your_gemini_api_key
```

Get your API keys:
- ExchangeRate-API: https://www.exchangerate-api.com/
- Gemini API: https://makersuite.google.com/app/apikey

**4. Run the application**
```bash
python backend.py
```

Visit `http://localhost:5000`

## Project Structure

```
currency-converter-chatbot/
├── backend.py              # Flask server & APIs
├── templates/
│   └── index.html         # Frontend interface
├── knowledge_base.json    # Chatbot learning data
├── requirements.txt       # Python dependencies
└── .env                   # API keys (create this)
```

## How It Works

### Current Conversion Tab
1. Enter amount and select currencies
2. Real-time conversion using latest rates
3. Display exchange rate and result
4. Chat with AI about any currency

### Historical Rates Tab
1. Select date from date picker
2. Choose currency pair
3. System fetches real historical data
4. Shows rate from European Central Bank
5. Estimated data for unsupported currencies

### Prediction Tab
1. Select currency pair
2. Choose prediction period (1-30 days)
3. System analyzes 30 days of historical data
4. Applies linear regression and moving averages
5. Shows predicted rate with confidence level
6. Displays trend direction and strength

## Prediction Algorithm

The prediction engine uses:

1. **Linear Regression** - Fits trend line through historical data
2. **Simple Moving Average (SMA)** - 7-day average for smoothing
3. **Exponential Moving Average (EMA)** - Weighted recent data
4. **Volatility Analysis** - Standard deviation for confidence
5. **Trend Strength** - Change percentage classification

**Confidence Levels:**
- High: Volatility < 1%
- Medium: Volatility 1-3%
- Low: Volatility > 3%

**Disclaimer:** Predictions are trend-based estimates, not financial advice.

## API Endpoints

**Chat:**
```
POST /learning_chat
Body: { "message": "What is USD?" }
Response: { "success": true, "response": "..." }
```

**Current Conversion:**
```
GET /convert?amount=100&base_currency=USD&target_currency=EUR
Response: { "success": true, "result": "92.50 EUR", "rate": 0.925 }
```

**Historical Rates:**
```
GET /historical?base_currency=USD&target_currency=EUR&date=2024-01-01
Response: { "success": true, "rate": 0.93, "source": "..." }
```

**Prediction:**
```
GET /predict?base_currency=USD&target_currency=EUR&days=7
Response: { "success": true, "prediction": {...} }
```

**Available Currencies:**
```
GET /currencies
Response: { "success": true, "currencies": ["USD", "EUR", ...] }
```

## Knowledge Base

The chatbot learns from `knowledge_base.json`:
- Common currency questions
- Currency codes and countries
- Conversion queries
- Custom responses

Add your own Q&A pairs to teach the bot!

## Supported Currencies

190+ currencies including:
- USD, EUR, GBP, JPY, CHF
- INR, CNY, AUD, CAD, NZD
- BRL, MXN, ZAR, RUB, TRY
- And 180+ more!

## Features Explained

### Real-time Rates
Fetches latest exchange rates from ExchangeRate-API every request. Covers 190+ official world currencies.

### AI Chatbot
Uses Google's Gemini AI with custom prompts. Trained on all 190 currency codes, full forms, and countries. Falls back to knowledge base for repeated queries.

### Historical Data
Real data from Frankfurter API (European Central Bank) for major currency pairs. Simulated historical data for other currencies based on current rates with realistic variation.

### Trend Prediction
Analyzes 30 days of real historical data using statistical methods. Not a crystal ball - shows trend direction based on past patterns.


## Deployment

Deployed on PythonAnywhere:

1. Upload files to PythonAnywhere
2. Install requirements in virtualenv
3. Configure WSGI file
4. Add environment variables
5. Set Flask app path

## Limitations

- Predictions are trend-based, not financial advice
- Historical data limited for some currency pairs
- Free API has rate limits
- Some currencies may have delayed updates

## Future Improvements

- [ ] Multi-currency converter (compare 3+ currencies)
- [ ] Email rate alerts
- [ ] Currency charts and graphs
- [ ] More prediction models (ARIMA, Prophet)
- [ ] User accounts for saving favorites
- [ ] Mobile app version
- [ ] Cryptocurrency support

## Contributing

Pull requests welcome! For major changes, open an issue first.

## License

MIT License - free to use for personal and commercial projects.

## Contact

Himanshu Yadav  
[GitHub](https://github.com/theotechtrad) | [LinkedIn](https://www.linkedin.com/in/hvhimanshu-yadav)

---

Built with Flask, Gemini AI & ExchangeRate-API | Deployed on PythonAnywhere
