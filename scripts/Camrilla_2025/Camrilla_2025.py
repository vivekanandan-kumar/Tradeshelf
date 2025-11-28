import pandas as pd
import datetime as dt
from datetime import date, datetime, timedelta,timezone
import os
from multiprocessing import Process
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pytz

cwd = '/Users/vivekanandan/PycharmProjects/DjangoProject/Tradeshelf/scripts/Camrilla_2025'


def mail_send(symbol, ins_type, text_html):
    mail_details = cwd + '/input/mail_details.dat'
    with open(mail_details) as f:
        lines = f.read().splitlines()
        fromaddr = lines[0].split('|')[0]
        passwd = lines[0].split('|')[1]
        mail_addr = str(lines[0].split('|')[2])
        to_mail = mail_addr.split(",")

    toaddr = ', '.join(to_mail)
    stock = symbol

    # Create enhanced HTML email template
    enhanced_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .trading-table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Arial', sans-serif;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border-radius: 12px;
                overflow: hidden;
                margin: 0 auto;
            }}
            .trading-table th {{
                padding: 16px 8px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
                color: white;
                border: none;
            }}
            .trading-table td {{
                padding: 14px 8px;
                text-align: center;
                border: none;
                font-weight: 500;
            }}
            .header-row {{
                background: linear-gradient(135deg, #1a5276, #1b4f72);
            }}
            /* Column-specific bluish-green gradient backgrounds */
            .h4-column {{
                background: linear-gradient(135deg, #e8f8f5, #d1f2eb);
                border-left: 4px solid #1abc9c;
            }}
            .h3-column {{
                background: linear-gradient(135deg, #fef9e7, #fcf3cf);
                border-left: 4px solid #f1c40f;
            }}
            .l3-column {{
                background: linear-gradient(135deg, #eaf2f8, #d4e6f1);
                border-left: 4px solid #3498db;
            }}
            .l4-column {{
                background: linear-gradient(135deg, #f9ebea, #f2d7d5);
                border-left: 4px solid #e74c3c;
            }}
            /* Level headers with bluish-green gradients */
            .level-header.h4 {{
                background: linear-gradient(135deg, #16a085, #1abc9c) !important;
            }}
            .level-header.h3 {{
                background: linear-gradient(135deg, #f39c12, #f1c40f) !important;
            }}
            .level-header.l3 {{
                background: linear-gradient(135deg, #2980b9, #3498db) !important;
            }}
            .level-header.l4 {{
                background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
            }}
            .level-header {{
                color: white !important;
                font-size: 15px !important;
                padding: 20px 8px !important;
                border-bottom: 2px solid rgba(255,255,255,0.3);
            }}
            .value-cell {{
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 18px 8px;
            }}
            /* Bluish-green psychological color coding */
            .sl-cell {{
                background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
                color: white !important;
                font-weight: bold;
                font-size: 15px;
            }}
            .target-cell-1 {{
                background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
                color: white !important;
                font-weight: bold;
                font-size: 15px;
            }}
            .target-cell-2 {{
                background: linear-gradient(135deg, #229954, #27ae60) !important;
                color: white !important;
                font-weight: bold;
                font-size: 15px;
            }}
            .target-cell-3 {{
                background: linear-gradient(135deg, #1e8449, #229954) !important;
                color: white !important;
                font-weight: bold;
                font-size: 15px;
            }}
            .section-header {{
                background: linear-gradient(135deg, #2c3e50, #34495e) !important;
                color: white !important;
                font-size: 15px;
                font-weight: bold;
                padding: 16px 8px;
                text-align: left;
                padding-left: 20px !important;
            }}
            .symbol-header {{
                background: linear-gradient(135deg, #1a5276, #1b4f72);
                color: white;
                font-size: 22px;
                padding: 24px 8px;
                text-align: center;
                border-bottom: 3px solid rgba(255,255,255,0.2);
            }}
            .footer {{
                background: linear-gradient(135deg, #1a5276, #1b4f72);
                color: white;
                padding: 18px 8px;
                text-align: center;
                font-size: 13px;
                border-top: 3px solid rgba(255,255,255,0.1);
            }}
            /* Row hover effects */
            tr:hover td {{
                filter: brightness(1.05);
                transition: all 0.2s ease;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .symbol {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .date {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .table-container {{
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            

            <div class="table-container">
                {text_html.replace("^", "<br>").replace("%", "<br>")}
            </div>

            <div class="footer">
                TradeShelf © 2025 | Generated on {dt.datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S IST")}
            </div>
        </div>
    </body>
    </html>
    """

    # instance of MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = f"{stock} - {ins_type} :: Camarilla Levels :: {dt.datetime.now().strftime('%b %d, %Y')}"

    # Attach HTML content
    msg.attach(MIMEText(enhanced_html, 'html'))

    # Attach CSV file
    filename = f"{stock}{ins_type}.csv"
    attachment_path = f"{cwd}/hist_data/{stock}{ins_type}_hist.csv"

    if os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename={filename}")
            msg.attach(p)

    # Send email
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, passwd)
        text = msg.as_string()

        for mail in to_mail:
            s.sendmail(fromaddr, mail, text)

        s.quit()
        print(f"Email sent successfully for {stock}")
    except Exception as e:
        print(f"Error sending email: {e}")


def cal_stock_hist(symbol, instrument_type, expiry_date, option_type, strike_price):
    symb = symbol
    ins_type = instrument_type
    end_date = date.today()
    start_date = end_date - timedelta(days=5)

    # Convert from/to dates to 'DD-MM-YYYY' format for NSE API
    end_date_str = end_date.strftime('%d-%m-%Y')
    start_date_str = start_date.strftime('%d-%m-%Y')

    # Use the expiry_date AS-IS (it's already in "30-Dec2025" format)
    # The expiry_date should be passed directly without conversion
    expiry_date_str = expiry_date

    print(f"Start date: {start_date_str}, End date: {end_date_str}, Expiry date: {expiry_date_str}")

    nse_url = "https://www.nseindia.com/api/historicalOR/fo/derivatives?&from=" + start_date_str + "&to=" + end_date_str + "&expiryDate=" + expiry_date_str + "&instrumentType=FUTIDX&symbol=" + symbol

    print(f"Fetching data for {symbol} from URL: {nse_url}")  # Debug log

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.nseindia.com/'
    }

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www.nseindia.com/option-chain", timeout=10)
        response = session.get(nse_url, timeout=15)

        # Check if response is successful
        if response.status_code != 200:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return None

        data = response.json()
        print(f"API Response keys: {data.keys()}")  # Debug log

        # Check if 'data' key exists and has content
        if 'data' not in data or not data['data']:
            print(f"No data found for {symbol} in API response")
            return None

        # Convert the 'data' portion to a DataFrame
        df = pd.DataFrame(data['data'])
        print(f"DataFrame columns: {df.columns.tolist()}")  # Debug log
        print(f"DataFrame shape: {df.shape}")  # Debug log

        if df.empty:
            print(f"Empty DataFrame for {symbol}")
            return None

        df = df.apply(pd.to_numeric, errors='ignore')

        prev_day = df.head(1)

        # Debug: Print available columns to identify the correct column names
        print(f"Available columns in prev_day: {prev_day.columns.tolist()}")

        # Try to find the correct column names with fallbacks
        high_col = None
        low_col = None
        close_col = None
        open_col = None

        # Common column name patterns in NSE data
        possible_high_cols = ['FH_TRADE_HIGH_PRICE', 'highPrice', 'HIGH_PRICE', 'high', 'tradeHigh']
        possible_low_cols = ['FH_TRADE_LOW_PRICE', 'lowPrice', 'LOW_PRICE', 'low', 'tradeLow']
        possible_close_cols = ['FH_CLOSING_PRICE', 'closePrice', 'CLOSE_PRICE', 'close', 'lastPrice']
        possible_open_cols = ['FH_OPENING_PRICE', 'openPrice', 'OPEN_PRICE', 'open']

        for col in possible_high_cols:
            if col in prev_day.columns:
                high_col = col
                break

        for col in possible_low_cols:
            if col in prev_day.columns:
                low_col = col
                break

        for col in possible_close_cols:
            if col in prev_day.columns:
                close_col = col
                break

        for col in possible_open_cols:
            if col in prev_day.columns:
                open_col = col
                break

        print(f"Using columns - High: {high_col}, Low: {low_col}, Close: {close_col}, Open: {open_col}")  # Debug log

        # Check if we found all required columns
        if not all([high_col, low_col, close_col]):
            print(f"Missing required columns for {symbol}. Found: High={high_col}, Low={low_col}, Close={close_col}")
            return None

        # Extract values with the identified column names
        high_price = prev_day[high_col].values[0]
        low_price = prev_day[low_col].values[0]
        close_price = prev_day[close_col].values[0]
        open_price = prev_day[open_col].values[
            0] if open_col else close_price  # Fallback to close if open not available

        print(f"Prices - High: {high_price}, Low: {low_price}, Close: {close_price}, Open: {open_price}")  # Debug log

        # ALL THE CALCULATIONS
        long_breakout = ((high_price - low_price) * (1.1 / 2)) + close_price + 10
        reversal_sell = ((high_price - low_price) * (1.1 / 4)) + close_price - 10
        print("value - long_breakout", long_breakout, "\nvalue - reversal_sell", reversal_sell)

        long_breakout_sl = ((long_breakout + reversal_sell) / 2) - 10
        long_breakout_sl_T1 = (long_breakout * (0.5 / 100)) + long_breakout - 10
        long_breakout_sl_T2 = (long_breakout * (1 / 100)) + long_breakout - 10
        long_breakout_sl_T3 = (long_breakout * (1.5 / 100)) + long_breakout - 10

        reversal_sell_sl = ((long_breakout + reversal_sell) / 2) + 10
        reversal_sell_sl_T1 = close_price - ((high_price - low_price) * (1.1 / 12))
        reversal_sell_sl_T2 = close_price - ((high_price - low_price) * (1.1 / 6))
        reversal_sell_sl_T3 = close_price - ((high_price - low_price) * (1.1 / 4))

        reversal_buy = close_price - ((high_price - low_price) * (1.1 / 4)) + 10
        short_breakout = close_price - ((high_price - low_price) * (1.1 / 2)) - 10

        reversal_buy_sl = ((reversal_buy + short_breakout) / 2) - 10
        reversal_buy_sl_T1 = close_price + ((high_price - low_price) * (1.1 / 12))
        reversal_buy_sl_T2 = close_price + ((high_price - low_price) * (1.1 / 6))
        reversal_buy_sl_T3 = close_price + ((high_price - low_price) * (1.1 / 4))

        short_breakout_sl = ((reversal_buy + short_breakout) / 2) + 10
        short_breakout_sl_T1 = short_breakout - (short_breakout * (0.5 / 100)) + 10
        short_breakout_sl_T2 = short_breakout - (short_breakout * (1 / 100)) + 10
        short_breakout_sl_T3 = short_breakout - (short_breakout * (1.5 / 100)) + 10

        # Add calculated columns to prev_day DataFrame
        prev_day['long_breakout'] = long_breakout
        prev_day['long_breakout_sl'] = long_breakout_sl
        prev_day['long_breakout_sl_T1'] = long_breakout_sl_T1
        prev_day['long_breakout_sl_T2'] = long_breakout_sl_T2
        prev_day['long_breakout_sl_T3'] = long_breakout_sl_T3
        prev_day['reversal_sell'] = reversal_sell
        prev_day['reversal_sell_sl'] = reversal_sell_sl
        prev_day['reversal_sell_sl_T1'] = reversal_sell_sl_T1
        prev_day['reversal_sell_sl_T2'] = reversal_sell_sl_T2
        prev_day['reversal_sell_sl_T3'] = reversal_sell_sl_T3
        prev_day['reversal_buy'] = reversal_buy
        prev_day['reversal_buy_sl'] = reversal_buy_sl
        prev_day['reversal_buy_sl_T1'] = reversal_buy_sl_T1
        prev_day['reversal_buy_sl_T2'] = reversal_buy_sl_T2
        prev_day['reversal_buy_sl_T3'] = reversal_buy_sl_T3
        prev_day['short_breakout'] = short_breakout
        prev_day['short_breakout_sl'] = short_breakout_sl
        prev_day['short_breakout_sl_T1'] = short_breakout_sl_T1
        prev_day['short_breakout_sl_T2'] = short_breakout_sl_T2
        prev_day['short_breakout_sl_T3'] = short_breakout_sl_T3

        # Also store the original price columns for reference
        prev_day['original_high'] = high_price
        prev_day['original_low'] = low_price
        prev_day['original_close'] = close_price
        prev_day['original_open'] = open_price

        # Save files
        file_name = cwd + '/hist_data/' + symbol + ins_type + '.csv'
        prev_day.to_csv(file_name)
        hist_file_name = cwd + '/hist_data/' + symbol + ins_type + '_hist.csv'
        st_hist_5 = df.head(5)
        st_hist_5.to_csv(hist_file_name)

        # Call st_mrng_first
        st_mrng_first(symbol, instrument_type, expiry_date, option_type, strike_price)

        return prev_day

    except Exception as e:
        print(f"Error in cal_stock_hist for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None

def st_mrng_first(symbol, instrument_type, expiry_date, option_type, strike_price):
    symb = symbol
    ins_type = instrument_type
    opt_type = option_type
    strike_price = strike_price

    if 1 == 1:
        stock = symbol
        hist_file_name = cwd + '/hist_data/' + stock + ins_type + '.csv'
        st_hist = pd.read_csv(hist_file_name)
        end_date = date.today()
        DATE = str(end_date)

        # Extract values
        H3 = str(round(st_hist['reversal_sell'].values[0], 2))
        H3_SL = str(round(st_hist['reversal_sell_sl'].values[0], 2))
        H3_SL1 = str(round(st_hist['reversal_sell_sl_T1'].values[0], 2))
        H3_SL2 = str(round(st_hist['reversal_sell_sl_T2'].values[0], 2))
        H3_SL3 = str(round(st_hist['reversal_sell_sl_T3'].values[0], 2))
        H4 = str(round(st_hist['long_breakout'].values[0], 2))
        H4_SL = str(round(st_hist['long_breakout_sl'].values[0], 2))
        H4_SL1 = str(round(st_hist['long_breakout_sl_T1'].values[0], 2))
        H4_SL2 = str(round(st_hist['long_breakout_sl_T2'].values[0], 2))
        H4_SL3 = str(round(st_hist['long_breakout_sl_T3'].values[0], 2))
        L3 = str(round(st_hist['reversal_buy'].values[0], 2))
        L3_SL = str(round(st_hist['reversal_buy_sl'].values[0], 2))
        L3_SL1 = str(round(st_hist['reversal_buy_sl_T1'].values[0], 2))
        L3_SL2 = str(round(st_hist['reversal_buy_sl_T2'].values[0], 2))
        L3_SL3 = str(round(st_hist['reversal_buy_sl_T3'].values[0], 2))
        L4 = str(round(st_hist['short_breakout'].values[0], 2))
        L4_SL = str(round(st_hist['short_breakout_sl'].values[0], 2))
        L4_SL1 = str(round(st_hist['short_breakout_sl_T1'].values[0], 2))
        L4_SL2 = str(round(st_hist['short_breakout_sl_T2'].values[0], 2))
        L4_SL3 = str(round(st_hist['short_breakout_sl_T3'].values[0], 2))

        utc_time = dt.datetime.now(timezone.utc)
        ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
        current_time_ist = ist_time.strftime("%Y-%m-%d %H:%M:%S IST")

        # Enhanced HTML template with proper alignment and psychological color coding
        text = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .trading-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-family: 'Arial', sans-serif;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    border-radius: 12px;
                    overflow: hidden;
                    margin: 0 auto;
                }}
                .trading-table th {{
                    padding: 16px 8px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 14px;
                    color: white;
                    border: none;
                }}
                .trading-table td {{
                    padding: 14px 8px;
                    text-align: center;
                    border: none;
                    font-weight: 500;
                }}
                .header-row {{
                    background: linear-gradient(135deg, #2c3e50, #34495e);
                }}
                /* Column gradient backgrounds matching headers */
                .h4-column {{
                    background: linear-gradient(135deg, #e8f8f5, #d1f2eb, #a3e4d7);
                    border-left: 4px solid #16a085;
                }}
                .h3-column {{
                    background: linear-gradient(135deg, #fef9e7, #fcf3cf, #f7dc6f);
                    border-left: 4px solid #f39c12;
                }}
                .l3-column {{
                    background: linear-gradient(135deg, #eaf2f8, #d4e6f1, #aed6f1);
                    border-left: 4px solid #2980b9;
                }}
                .l4-column {{
                    background: linear-gradient(135deg, #f9ebea, #f2d7d5, #e6b0aa);
                    border-left: 4px solid #c0392b;
                }}
                /* Level headers with stronger gradients */
                .level-header.h4 {{
                    background: linear-gradient(135deg, #16a085, #1abc9c, #48c9b0) !important;
                }}
                .level-header.h3 {{
                    background: linear-gradient(135deg, #f39c12, #f1c40f, #f7dc6f) !important;
                }}
                .level-header.l3 {{
                    background: linear-gradient(135deg, #2980b9, #3498db, #5dade2) !important;
                }}
                .level-header.l4 {{
                    background: linear-gradient(135deg, #c0392b, #e74c3c, #ec7063) !important;
                }}
                .level-header {{
                    color: white !important;
                    font-size: 15px !important;
                    padding: 20px 8px !important;
                    border-bottom: 2px solid rgba(255,255,255,0.3);
                }}
                .value-cell {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 18px 8px;
                }}
                /* Psychological color coding */
                .sl-cell {{
                    background: linear-gradient(135deg, #e74c3c, #c0392b, #a93226) !important;
                    color: white !important;
                    font-weight: bold;
                    font-size: 15px;
                }}
                .target-cell-1 {{
                    background: linear-gradient(135deg, #27ae60, #2ecc71, #58d68d) !important;
                    color: white !important;
                    font-weight: bold;
                    font-size: 15px;
                }}
                .target-cell-2 {{
                    background: linear-gradient(135deg, #229954, #27ae60, #52be80) !important;
                    color: white !important;
                    font-weight: bold;
                    font-size: 15px;
                }}
                .target-cell-3 {{
                    background: linear-gradient(135deg, #1e8449, #229954, #45b39d) !important;
                    color: white !important;
                    font-weight: bold;
                    font-size: 15px;
                }}
                .section-header {{
                    background: linear-gradient(135deg, #495057, #343a40, #212529) !important;
                    color: white !important;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 16px 8px;
                    text-align: left;
                    padding-left: 20px !important;
                }}
                .symbol-header {{
                    background: linear-gradient(135deg, #1a5276, #1b4f72, #154360);
                    color: white;
                    font-size: 22px;
                    padding: 24px 8px;
                    text-align: center;
                    border-bottom: 3px solid rgba(255,255,255,0.2);
                }}
                .footer {{
                    background: linear-gradient(135deg, #2c3e50, #34495e, #1c2833);
                    color: white;
                    padding: 18px 8px;
                    text-align: center;
                    font-size: 13px;
                    border-top: 3px solid rgba(255,255,255,0.1);
                }}
                /* Row hover effects */
                tr:hover td {{
                    filter: brightness(1.05);
                    transition: all 0.2s ease;
                }}
            </style>
        </head>
        <body>
            <table class="trading-table">
                <!-- Symbol Header -->
                <tr>
                    <td colspan="5" class="symbol-header">
                        <strong>{0} - {24}</strong><br>
                        <small style="font-size: 16px; opacity: 0.9;">Trading Levels for {25}</small>
                    </td>
                </tr>

                <!-- Strategy Headers -->
                <tr>
                    <th> </th>
                    <th class="level-header h4">LONG BREAKOUT<br><span style="font-size:12px; opacity: 0.9;">(H4 - Bullish)</span></th>
                    <th class="level-header h3">REVERSAL SELL<br><span style="font-size:12px; opacity: 0.9;">(H3 - Resistance)</span></th>
                    <th class="level-header l3">REVERSAL BUY<br><span style="font-size:12px; opacity: 0.9;">(L3 - Support)</span></th>
                    <th class="level-header l4">SHORT BREAKOUT<br><span style="font-size:12px; opacity: 0.9;">(L4 - Bearish)</span></th>
                </tr>

                <!-- Levels Row -->
                <tr>
                    <td> {23} </td>
                    <td class="h4-column value-cell">{2}</td>
                    <td class="h3-column value-cell">{3}</td>
                    <td class="l3-column value-cell">{4}</td>
                    <td class="l4-column value-cell">{5}</td>
                </tr>

                <!-- Target 1 Row -->
                <tr>
                    <td class="section-header">TARGET 1 🎯 </td>
                    <td class="h4-column target-cell-1">{10}</td>
                    <td class="h3-column target-cell-1">{11}</td>
                    <td class="l3-column target-cell-1">{12}</td>
                    <td class="l4-column target-cell-1">{13}</td>
                </tr>

                <!-- Stop Loss Row -->
                <tr>
                    <td class="section-header">STOP LOSS LEVELS 🛑 </td>
                    <td class="h4-column sl-cell">{6}</td>
                    <td class="h3-column sl-cell">{7}</td>
                    <td class="l3-column sl-cell">{8}</td>
                    <td class="l4-column sl-cell">{9}</td>
                </tr>

                <!-- Target 2 Row -->
                <tr>
                    <td class="section-header">TARGET 2 🎯🎯 </td>
                    <td class="h4-column target-cell-2">{14}</td>
                    <td class="h3-column target-cell-2">{15}</td>
                    <td class="l3-column target-cell-2">{16}</td>
                    <td class="l4-column target-cell-2">{17}</td>
                </tr>

                <!-- Target 3 Row -->
                <tr>
                    <td class="section-header">TARGET 3 🎯🎯🎯 </td>
                    <td class="h4-column target-cell-3">{18}</td>
                    <td class="h3-column target-cell-3">{19}</td>
                    <td class="l3-column target-cell-3">{20}</td>
                    <td class="l4-column target-cell-3">{21}</td>
                </tr>

            </table>
        </body>
        </html>
        """

        html_text = text.format(
            stock, DATE,  # {0}, {1}
            H4, H3, L3, L4,  # {2}, {3}, {4}, {5} - Levels
            H4_SL, H3_SL, L3_SL, L4_SL,  # {6}, {7}, {8}, {9} - Stop Loss
            H4_SL1, H3_SL1, L3_SL1, L4_SL1,  # {10}, {11}, {12}, {13} - Target 1
            H4_SL2, H3_SL2, L3_SL2, L4_SL2,  # {14}, {15}, {16}, {17} - Target 2
            H4_SL3, H3_SL3, L3_SL3, L4_SL3,  # {18}, {19}, {20}, {21} - Target 3
            current_time_ist,  # {22} - Timestamp in IST
            expiry_date,  # {23} - expiry date
            ins_type,  # {24} - instrument type (FUTIDX)
            dt.datetime.now().strftime("%A, %B %d, %Y")  # {25} - formatted date
        )

        #mail_send(stock, ins_type, html_text)

        # Save to DataFrame
        stock_camrilla_df = pd.DataFrame(columns=['SYMBOL', 'DATE', 'H4', 'H3', 'L3', 'L4',
                                                  'H4_SL', 'H4_SL_T1', 'H4_SL_T2', 'H4_SL_T3',
                                                  'H3_SL', 'H3_SL_T1', 'H3_SL_T2', 'H3_SL_T3',
                                                  'L4_SL', 'L4_SL_T1', 'L4_SL_T2', 'L4_SL_T3',
                                                  'L3_SL', 'L3_SL_T1', 'L3_SL_T2', 'L3_SL_T3',
                                                  'PREV_DATE', 'MAIL_TEXT_HTML'])
        stock_camrilla_df.loc[stock] = [stock, DATE,
                                        H4, H3, L3, L4,
                                        H4_SL, H4_SL1, H4_SL2, H4_SL3,
                                        H3_SL, H3_SL1, H3_SL2, H3_SL3,
                                        L4_SL, L4_SL1, L4_SL2, L4_SL3,
                                        L3_SL, L3_SL1, L3_SL2, L3_SL3,
                                        st_hist['FH_TIMESTAMP'].values[0], html_text]
        stock_camrilla_df.to_csv(cwd + "/daily/" + stock + ins_type + ".csv")
        print(f"Table generated for {stock}")

    else:
        print("Outside Market Hours")
    return True

def get_camarilla_data_for_django(symbol, instrument_type, expiry_date, option_type, strike_price):
    """Modified version that returns data for Django integration"""
    try:
        # Run your existing calculation
        result = cal_stock_hist(symbol, instrument_type, expiry_date, option_type, strike_price)

        if result is None or result.empty:
            return None

        # Convert expiry date from "30-Dec2025" to "2025-12-30" format for Django
        try:
            # Parse the original expiry date format
            expiry_parsed = datetime.strptime(expiry_date, '%d-%b%Y')
            django_expiry_date = expiry_parsed.strftime('%Y-%m-%d')
        except ValueError:
            # If parsing fails, use the original date
            django_expiry_date = expiry_date
            print(f"Warning: Could not parse expiry date {expiry_date}, using as-is")

        # Return structured data for Django - access DataFrame columns properly
        return {
            'symbol': symbol,
            'instrument_type': instrument_type,
            'expiry_date': django_expiry_date,  # Use the converted date
            'prev_open': float(result['original_open'].values[0]) if 'original_open' in result.columns else float(result['FH_OPENING_PRICE'].values[0]) if 'FH_OPENING_PRICE' in result.columns else None,
            'prev_high': float(result['original_high'].values[0]),
            'prev_low': float(result['original_low'].values[0]),
            'prev_close': float(result['original_close'].values[0]),
            'h4_level': float(result['long_breakout'].values[0]),
            'h4_sl': float(result['long_breakout_sl'].values[0]),
            'h4_target1': float(result['long_breakout_sl_T1'].values[0]),
            'h4_target2': float(result['long_breakout_sl_T2'].values[0]),
            'h4_target3': float(result['long_breakout_sl_T3'].values[0]),
            'h3_level': float(result['reversal_sell'].values[0]),
            'h3_sl': float(result['reversal_sell_sl'].values[0]),
            'h3_target1': float(result['reversal_sell_sl_T1'].values[0]),
            'h3_target2': float(result['reversal_sell_sl_T2'].values[0]),
            'h3_target3': float(result['reversal_sell_sl_T3'].values[0]),
            'l3_level': float(result['reversal_buy'].values[0]),
            'l3_sl': float(result['reversal_buy_sl'].values[0]),
            'l3_target1': float(result['reversal_buy_sl_T1'].values[0]),
            'l3_target2': float(result['reversal_buy_sl_T2'].values[0]),
            'l3_target3': float(result['reversal_buy_sl_T3'].values[0]),
            'l4_level': float(result['short_breakout'].values[0]),
            'l4_sl': float(result['short_breakout_sl'].values[0]),
            'l4_target1': float(result['short_breakout_sl_T1'].values[0]),
            'l4_target2': float(result['short_breakout_sl_T2'].values[0]),
            'l4_target3': float(result['short_breakout_sl_T3'].values[0]),
        }
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    stock_list = cwd + '/input/stock_list.dat'
    with open(stock_list) as f:
        lines = f.read().splitlines()
        procs = []

    for i in range(len(lines)):
        val = lines[i].split('|')
        proc = Process(target=cal_stock_hist, args=(val[0], val[1], val[2], val[3], val[4],))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

if __name__ == '__main__':
    main()
