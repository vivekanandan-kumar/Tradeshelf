# -*- coding: utf-8 -*-
"""
@author: vivekanandan.kumar
Improved Whole Number Detection Script
"""
import os
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import datetime as dt
from datetime import timezone
import pytz
from datetime import date, timedelta
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configuration
CWD = '/home/vivek/Documents/Trading/Tradeshelf/scripts/Whole_Number'
OUTPUT_DIR = os.path.join(CWD, 'output')
HIST_DATA_DIR = os.path.join(OUTPUT_DIR, 'hist_data')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, 'script_log.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(HIST_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(CWD, 'input'), exist_ok=True)


def load_stock_symbols():
    """Load all stock symbols from input files"""
    symbols = set()
    for i in range(3):
        stock_list_file = os.path.join(CWD, 'input', f'stock_list_{i + 1}.dat')
        if os.path.exists(stock_list_file):
            with open(stock_list_file) as f:
                symbols.update(line.strip() for line in f if line.strip() and line.strip().upper() != "SYMBOL")
    return list(symbols)


def fetch_stock_data(symbol):
    """Fetch historical data for a single stock"""
    try:
        stock_ns = f"{symbol}.NS"
        stock_info = yf.Ticker(stock_ns)
        df = stock_info.history(period="3d")

        if df.empty:
            logger.warning(f"No data found for {symbol}")
            return None

        # Reset index to make Date a column
        df = df.reset_index()
        df['Symbol'] = symbol

        # Get only the latest data point
        latest_data = df.tail(1).copy()

        return latest_data

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None


def fetch_all_stock_data(symbols, max_workers=10):
    """Fetch data for all stocks using thread pool"""
    all_data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(fetch_stock_data, symbol): symbol
            for symbol in symbols
        }

        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                if result is not None and not result.empty:
                    all_data.append(result)
            except Exception as e:
                logger.error(f"Exception processing {symbol}: {str(e)}")

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()


def detect_whole_numbers(df):
    """Detect stocks with whole number highs and lows"""
    if df.empty:
        return df

    # Check if required columns exist
    required_columns = ['High', 'Low']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing columns in DataFrame: {missing_columns}")
        return pd.DataFrame()

    df['High_Round'] = df['High'].apply(lambda x: x.is_integer() if pd.notna(x) else False)
    df['Low_Round'] = df['Low'].apply(lambda x: x.is_integer() if pd.notna(x) else False)

    whole_number_stocks = df[(df['High_Round'] == True) & (df['Low_Round'] == True)]
    logger.info(f"Whole number detection: {len(whole_number_stocks)} stocks found")

    return whole_number_stocks


def create_styled_html_table(df):
    """Create a nicely formatted HTML table with styling"""
    if df.empty:
        return """
        <html>
        <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .no-data { background-color: #fff3cd; padding: 20px; border-radius: 5px; border: 1px solid #ffeaa7; }
            .timestamp { color: #7f8c8d; font-size: 12px; margin-top: 10px; }
        </style>
        </head>
        <body>
            <div class="no-data">
                <h2>🔍 Whole Number Detection Results</h2>
                <p><strong>No stocks found with both High and Low at whole numbers today.</strong></p>
            </div>
            <div class="timestamp">
                Report generated on: {datetime}
            </div>
        </body>
        </html>
        """.format(datetime=datetime.datetime.now().strftime("%Y-%b-%d %H:%M:%S"))

    # Check available columns and create display dataframe
    available_columns = []
    for col in ['Date', 'Symbol', 'High', 'Low']:
        if col in df.columns:
            available_columns.append(col)

    if not available_columns:
        return "<p>No valid data columns available for display.</p>"

    display_df = df[available_columns].copy()

    # Format date column if it exists
    if 'Date' in display_df.columns:
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')

    # Format numeric columns
    if 'High' in display_df.columns:
        display_df['High'] = display_df['High'].round(2)
    if 'Low' in display_df.columns:
        display_df['Low'] = display_df['Low'].round(2)

    # Create styled HTML
    html = """
    <html>
    <head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .stock-table { border-collapse: collapse; width: 100%; font-size: 14px; }
        .stock-table th { background-color: #2c3e50; color: white; padding: 12px; text-align: left; }
        .stock-table td { padding: 10px; border-bottom: 1px solid #ddd; }
        .stock-table tr:nth-child(even) { background-color: #f2f2f2; }
        .stock-table tr:hover { background-color: #e9f7fe; }
        .count-badge { background-color: #3498db; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
        .timestamp { color: #7f8c8d; font-size: 12px; margin-top: 10px; }
    </style>
    </head>
    <body>
    """

    # Add summary section
    html += f"""
    <div class="summary">
        <h2>🔍 Whole Number Detection Results</h2>
        <p>Stocks with both <strong>High</strong> and <strong>Low</strong> at whole numbers</p>
        <p>Stocks Found: <span class="count-badge">{len(display_df)}</span></p>
    </div>
    """

    # Add table
    html += display_df.to_html(
        classes='stock-table',
        index=False,
        escape=False
    )

    # Add timestamp
    html += f"""
    <div class="timestamp">
        Report generated on: {dt.datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S IST")}
    </div>
    </body>
    </html>
    """

    return html


def send_email_with_attachment(df, subject_suffix=""):
    """Send email with results"""
    try:
        # Read email configuration
        mail_details_file = os.path.join(CWD, 'input', 'mail_details.dat')
        if not os.path.exists(mail_details_file):
            logger.error(f"Email configuration file not found: {mail_details_file}")
            return

        with open(mail_details_file) as f:
            lines = f.read().splitlines()
            if not lines:
                logger.error("Email configuration file is empty")
                return

            fromaddr, passwd, mail_addr = lines[0].split('|')
            to_mail = mail_addr.split(",")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = ', '.join(to_mail)

        subject = f"WHOLE NUMBER - EOD SCRIPT LIST {subject_suffix}"
        msg['Subject'] = f"{subject} :: Generated on {dt.datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S IST")}"

        # Create HTML body
        html_content = create_styled_html_table(df)
        msg.attach(MIMEText(html_content, 'html'))

        # Attach CSV file if we have data
        if not df.empty:
            csv_filename = os.path.join(OUTPUT_DIR, 'script_selected_whole_number.csv')

            # Select available columns for CSV
            csv_columns = []
            for col in ['Date', 'Symbol', 'High', 'Low', 'High_Round', 'Low_Round']:
                if col in df.columns:
                    csv_columns.append(col)

            if csv_columns:
                df[csv_columns].to_csv(csv_filename, index=False)

                with open(csv_filename, "rb") as attachment:
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload(attachment.read())
                    encoders.encode_base64(p)
                    p.add_header('Content-Disposition',
                                 f'attachment; filename="whole_number_stocks.csv"')
                    msg.attach(p)

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(fromaddr, passwd)
            text = msg.as_string()
            for mail in to_mail:
                s.sendmail(fromaddr, mail, text)

        logger.info(f"Email sent successfully to {len(to_mail)} recipients")

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise


def debug_dataframe_structure(df, description=""):
    """Debug function to check DataFrame structure"""
    logger.info(f"=== DataFrame Structure {description} ===")
    logger.info(f"Shape: {df.shape}")
    if not df.empty:
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"First few rows:")
        logger.info(df.head(2).to_string())
    else:
        logger.info("DataFrame is empty")
    logger.info("=" * 50)


# Add this to your st_whole_num_v2.py

def fetch_stock_data_improved(symbol):
    """Improved version with better error handling"""
    try:
        stock_ns = f"{symbol}.NS"
        stock_info = yf.Ticker(stock_ns)

        # Try multiple periods
        for period in ["3d", "5d", "1d"]:
            try:
                df = stock_info.history(period=period)
                if not df.empty:
                    break
            except:
                continue
        else:
            logger.warning(f"No data found for {symbol} after trying multiple periods")
            return None

        # Reset index to make Date a column
        df = df.reset_index()
        df['Symbol'] = symbol

        # Get only the latest data point
        latest_data = df.tail(1).copy()

        return latest_data

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def main():
    """Main execution function"""
    ensure_directories()

    logger.info("Starting Whole Number Detection Script")

    # Load stock symbols
    symbols = load_stock_symbols()
    logger.info(f"Loaded {len(symbols)} unique stock symbols")

    if not symbols:
        logger.error("No stock symbols found to process")
        return

    # Fetch stock data
    logger.info("Fetching stock data...")
    stock_data = fetch_all_stock_data(symbols)

    # Debug: Check raw data structure
    debug_dataframe_structure(stock_data, "Raw Stock Data")

    if stock_data.empty:
        logger.error("No stock data retrieved")
        # Send empty report email
        #send_email_with_attachment(pd.DataFrame(), " - No Data Retrieved")
        return

    logger.info(f"Retrieved data for {len(stock_data)} stocks")

    # Detect whole numbers
    logger.info("Analyzing for whole number highs and lows...")
    whole_number_stocks = detect_whole_numbers(stock_data)

    # Debug: Check filtered data structure
    debug_dataframe_structure(whole_number_stocks, "Whole Number Stocks")

    logger.info(f"Found {len(whole_number_stocks)} stocks with whole number highs and lows")

    # Send email report
    logger.info("Sending email report...")
    subject_suffix = f" - Found {len(whole_number_stocks)} Stocks" if not whole_number_stocks.empty else " - No Stocks Found"
    #send_email_with_attachment(whole_number_stocks, subject_suffix)

    logger.info("Script execution completed successfully")


def get_whole_number_data_for_django():
    """Modified version that returns data for Django integration"""
    try:
        symbols = load_stock_symbols()
        stock_data = fetch_all_stock_data(symbols)
        whole_number_stocks = detect_whole_numbers(stock_data)

        # Convert to list of dictionaries for Django
        result_data = []
        for _, row in whole_number_stocks.iterrows():
            result_data.append({
                'symbol': row['Symbol'],
                'trade_date': row['Date'].date() if hasattr(row['Date'], 'date') else datetime.now().date(),
                'high': float(row['High']),
                'low': float(row['Low']),
                'high_is_round': bool(row.get('High_Round', True)),
                'low_is_round': bool(row.get('Low_Round', True)),
            })

        return result_data
    except Exception as e:
        logger.error(f"Error in Django integration: {e}")
        return []

if __name__ == "__main__":
    main()
