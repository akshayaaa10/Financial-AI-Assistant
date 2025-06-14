
from flask import Flask, render_template, request, jsonify, session
import os
import logging
from datetime import datetime
import json
import traceback

from config import Config
from financial_data.news_fetcher import NewsFetcher
from financial_data.earnings_fetcher import EarningsFetcher
from financial_data.stock_data import StockDataFetcher
from ai_processor.llm_interface import FinancialQASystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
config = Config()
news_fetcher = NewsFetcher(config.NEWS_API_KEY)
earnings_fetcher = EarningsFetcher(config.ALPHA_VANTAGE_API_KEY)
stock_fetcher = StockDataFetcher()

# Initialize AI system (this may take some time on first run)
try:
    qa_system = FinancialQASystem(config)
    logger.info("AI system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI system: {e}")
    qa_system = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process financial query"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        question = data.get('question', '').strip()
        symbol = data.get('symbol', '').strip().upper()
        company_name = data.get('company_name', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        logger.info(f"Processing query: {question} for {symbol}")
        
        # Collect all financial data
        all_documents = []
        data_sources = {}
        
        # Fetch news articles
        try:
            logger.info("Fetching news articles...")
            news_articles = news_fetcher.fetch_company_news(symbol, company_name, days_back=30)
            all_documents.extend([{**article, 'type': 'news'} for article in news_articles])
            data_sources['news_count'] = len(news_articles)
            logger.info(f"Found {len(news_articles)} news articles")
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            data_sources['news_error'] = str(e)
        
        # Fetch earnings data
        try:
            logger.info("Fetching earnings data...")
            earnings_data = earnings_fetcher.fetch_earnings_data(symbol)
            
            # Convert earnings data to document format
            earnings_docs = []
            
            # Add company info as document
            if earnings_data.get('company_info'):
                info = earnings_data['company_info']
                earnings_docs.append({
                    'title': f"{symbol} Company Information",
                    'content': f"Company: {info.get('longName', symbol)}\n"
                             f"Sector: {info.get('sector', 'N/A')}\n"
                             f"Industry: {info.get('industry', 'N/A')}\n"
                             f"Market Cap: {info.get('marketCap', 'N/A')}\n"
                             f"P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
                             f"Revenue: {info.get('totalRevenue', 'N/A')}\n"
                             f"Profit Margin: {info.get('profitMargins', 'N/A')}\n"
                             f"Description: {info.get('longBusinessSummary', 'N/A')}",
                    'description': f"Company information for {symbol}",
                    'source': 'Yahoo Finance',
                    'symbol': symbol,
                    'type': 'company_info',
                    'published_date': datetime.now(),
                    'url': f"https://finance.yahoo.com/quote/{symbol}"
                })
            
            # Add earnings summary
            if earnings_data.get('summary'):
                summary = earnings_data['summary']
                earnings_docs.append({
                    'title': f"{symbol} Earnings Summary",
                    'content': json.dumps(summary, indent=2, default=str),
                    'description': f"Earnings summary for {symbol}",
                    'source': 'Yahoo Finance',
                    'symbol': symbol,
                    'type': 'earnings_summary',
                    'published_date': datetime.now(),
                    'url': f"https://finance.yahoo.com/quote/{symbol}/financials"
                })
            
            all_documents.extend(earnings_docs)
            data_sources['earnings_data'] = True
            data_sources['earnings_docs_count'] = len(earnings_docs)
            logger.info(f"Generated {len(earnings_docs)} earnings documents")
            
        except Exception as e:
            logger.error(f"Error fetching earnings: {e}")
            data_sources['earnings_error'] = str(e)
        
        # Fetch stock data
        try:
            logger.info("Fetching stock data...")
            stock_data = stock_fetcher.fetch_stock_data(symbol, period='1y')
            
            # Convert stock data to document format
            stock_docs = []
            
            if stock_data.get('summary'):
                summary = stock_data['summary']
                stock_docs.append({
                    'title': f"{symbol} Stock Analysis",
                    'content': json.dumps(summary, indent=2, default=str),
                    'description': f"Technical analysis and stock data for {symbol}",
                    'source': 'Yahoo Finance',
                    'symbol': symbol,
                    'type': 'stock_analysis',
                    'published_date': datetime.now(),
                    'url': f"https://finance.yahoo.com/quote/{symbol}"
                })
            
            # Add technical indicators as separate document
            if stock_data.get('technical_indicators'):
                tech_data = stock_data['technical_indicators']
                stock_docs.append({
                    'title': f"{symbol} Technical Indicators",
                    'content': f"RSI: {tech_data.get('rsi', 'N/A')}\n"
                             f"MACD: {tech_data.get('macd', 'N/A')}\n"
                             f"SMA 20: {tech_data.get('sma_20', 'N/A')}\n"
                             f"SMA 50: {tech_data.get('sma_50', 'N/A')}\n"
                             f"Support: {tech_data.get('support_level', 'N/A')}\n"
                             f"Resistance: {tech_data.get('resistance_level', 'N/A')}\n"
                             f"Bollinger Upper: {tech_data.get('bollinger_upper', 'N/A')}\n"
                             f"Bollinger Lower: {tech_data.get('bollinger_lower', 'N/A')}",
                    'description': f"Technical indicators for {symbol}",
                    'source': 'Technical Analysis',
                    'symbol': symbol,
                    'type': 'technical_analysis',
                    'published_date': datetime.now(),
                    'url': f"https://finance.yahoo.com/quote/{symbol}/chart"
                })
            
            all_documents.extend(stock_docs)
            data_sources['stock_data'] = True
            data_sources['stock_docs_count'] = len(stock_docs)
            logger.info(f"Generated {len(stock_docs)} stock documents")
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            data_sources['stock_error'] = str(e)
        
        # Process query with AI system
        if qa_system and all_documents:
            try:
                logger.info("Processing query with AI system...")
                result = qa_system.process_query(question, symbol, all_documents)
                
                # Add metadata
                result['symbol'] = symbol
                result['company_name'] = company_name
                result['data_sources'] = data_sources
                result['total_documents'] = len(all_documents)
                result['timestamp'] = datetime.now().isoformat()
                
                logger.info("Query processed successfully")
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error processing with AI: {e}")
                logger.error(traceback.format_exc())
                
                # Fallback response
                return jsonify({
                    'answer': f"I found {len(all_documents)} relevant documents for {symbol}, but encountered an error processing your question with the AI system. "
                             f"Error: {str(e)}. Please try rephrasing your question or try again later.",
                    'sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                    'confidence': 0.0,
                    'sources': [doc.get('url', '') for doc in all_documents[:5] if doc.get('url')],
                    'metrics': {},
                    'context_used': len(all_documents),
                    'symbol': symbol,
                    'data_sources': data_sources,
                    'error': str(e)
                })
        
        elif not qa_system:
            return jsonify({
                'answer': "The AI system is not available. Please check the logs and ensure all dependencies are properly installed.",
                'sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                'confidence': 0.0,
                'sources': [],
                'metrics': {},
                'context_used': 0,
                'symbol': symbol,
                'error': "AI system not initialized"
            }), 500
        
        else:
            return jsonify({
                'answer': f"I couldn't find any relevant financial data for {symbol}. Please verify the stock symbol is correct.",
                'sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                'confidence': 0.0,
                'sources': [],
                'metrics': {},
                'context_used': 0,
                'symbol': symbol,
                'data_sources': data_sources
            })
    
    except Exception as e:
        logger.error(f"Unexpected error in process_query: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'news_fetcher': 'ok',
                'earnings_fetcher': 'ok',
                'stock_fetcher': 'ok',
                'ai_system': 'ok' if qa_system else 'error'
            }
        }
        
        return jsonify(status)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/company/<symbol>')
def get_company_info(symbol):
    """Get basic company information"""
    try:
        symbol = symbol.upper()
        earnings_data = earnings_fetcher.fetch_earnings_data(symbol)
        
        company_info = earnings_data.get('company_info', {})
        
        return jsonify({
            'symbol': symbol,
            'name': company_info.get('longName', symbol),
            'sector': company_info.get('sector'),
            'industry': company_info.get('industry'),
            'market_cap': company_info.get('marketCap'),
            'description': company_info.get('longBusinessSummary', '')[:500] + '...' if company_info.get('longBusinessSummary') else None
        })
    
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    
    # Start the application
    print("Starting Financial AI Assistant...")
    print("Note: First startup may take several minutes to download AI models...")
    
    app.run(
        host='0.0.0.0',
        port=8888,
        debug=config.DEBUG,
        threaded=True
    )