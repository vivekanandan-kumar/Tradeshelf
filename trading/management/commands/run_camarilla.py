# trading/management/commands/run_camarilla.py
import os
import sys
import django
from django.core.management.base import BaseCommand
from trading.models import ScriptRunLog, CamarillaLevel, TradingSymbol, SymbolExpiry
from django.utils import timezone
from datetime import date, datetime
import importlib.util

# Add the path to your existing script
SCRIPT_PATH = '/home/vivek/Documents/Trading/Tradeshelf/scripts/Camrilla_2025/Camrilla_2025.py'


class Command(BaseCommand):
    help = 'Calculate Camarilla levels using existing script and save to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            help='Process specific symbol only',
        )

    def handle(self, *args, **options):
        # Create log entry
        log_entry = ScriptRunLog.objects.create(
            script_name='CAMARILLA',
            status='RUNNING',
            start_time=timezone.now()
        )

        records_processed = 0
        records_success = 0

        try:
            self.stdout.write('Starting Camarilla calculation using existing script...')

            # Import and run the existing script
            camarilla_data = self.run_existing_camarilla_script()

            if not camarilla_data:
                self.stdout.write(self.style.WARNING('No data returned from Camarilla script'))
                return

            # Process each symbol's data
            for symbol_data in camarilla_data:
                try:
                    symbol = symbol_data['symbol']
                    expiry_date_str = symbol_data.get('expiry_date')

                    # Get or create TradingSymbol
                    trading_symbol, created = TradingSymbol.objects.get_or_create(
                        symbol=symbol,
                        defaults={
                            'instrument_type': symbol_data.get('instrument_type', 'FUTIDX'),
                            'is_active': True
                        }
                    )

                    # Get or create SymbolExpiry
                    if expiry_date_str:
                        try:
                            # Parse the expiry date string to date object
                            if isinstance(expiry_date_str, str):
                                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                            else:
                                expiry_date = expiry_date_str

                            symbol_expiry, created = SymbolExpiry.objects.get_or_create(
                                symbol=trading_symbol,
                                expiry_date=expiry_date,
                                defaults={'is_active': True}
                            )
                        except Exception as e:
                            self.stdout.write(f"Error parsing expiry date {expiry_date_str}: {e}")
                            # Use today's date as fallback
                            symbol_expiry, created = SymbolExpiry.objects.get_or_create(
                                symbol=trading_symbol,
                                expiry_date=date.today(),
                                defaults={'is_active': True}
                            )
                    else:
                        # Use today's date if no expiry date provided
                        symbol_expiry, created = SymbolExpiry.objects.get_or_create(
                            symbol=trading_symbol,
                            expiry_date=date.today(),
                            defaults={'is_active': True}
                        )

                    # Skip if already exists for today
                    if CamarillaLevel.objects.filter(
                            symbol=trading_symbol,
                            trade_date=date.today(),
                            expiry_date=symbol_expiry
                    ).exists():
                        self.stdout.write(f'Skipping {symbol} - already exists')
                        records_processed += 1
                        records_success += 1
                        continue

                    # Create CamarillaLevel entry
                    camarilla_level = CamarillaLevel.objects.create(
                        symbol=trading_symbol,
                        trade_date=date.today(),
                        expiry_date=symbol_expiry,  # Use SymbolExpiry instance

                        # Previous day OHLC
                        prev_open=symbol_data.get('prev_open'),
                        prev_high=symbol_data.get('prev_high'),
                        prev_low=symbol_data.get('prev_low'),
                        prev_close=symbol_data.get('prev_close'),

                        # H4 - Long Breakout
                        h4_level=symbol_data.get('h4_level'),
                        h4_sl=symbol_data.get('h4_sl'),
                        h4_target1=symbol_data.get('h4_target1'),
                        h4_target2=symbol_data.get('h4_target2'),
                        h4_target3=symbol_data.get('h4_target3'),

                        # H3 - Reversal Sell
                        h3_level=symbol_data.get('h3_level'),
                        h3_sl=symbol_data.get('h3_sl'),
                        h3_target1=symbol_data.get('h3_target1'),
                        h3_target2=symbol_data.get('h3_target2'),
                        h3_target3=symbol_data.get('h3_target3'),

                        # L3 - Reversal Buy
                        l3_level=symbol_data.get('l3_level'),
                        l3_sl=symbol_data.get('l3_sl'),
                        l3_target1=symbol_data.get('l3_target1'),
                        l3_target2=symbol_data.get('l3_target2'),
                        l3_target3=symbol_data.get('l3_target3'),

                        # L4 - Short Breakout
                        l4_level=symbol_data.get('l4_level'),
                        l4_sl=symbol_data.get('l4_sl'),
                        l4_target1=symbol_data.get('l4_target1'),
                        l4_target2=symbol_data.get('l4_target2'),
                        l4_target3=symbol_data.get('l4_target3'),
                    )

                    records_success += 1
                    records_processed += 1

                    self.stdout.write(
                        self.style.SUCCESS(f'Processed {symbol}')
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {symbol_data.get("symbol", "unknown")}: {str(e)}')
                    )
                    records_processed += 1

            # Update log entry
            log_entry.status = 'SUCCESS'
            log_entry.records_processed = records_processed
            log_entry.records_success = records_success
            log_entry.end_time = timezone.now()
            log_entry.calculate_duration()
            log_entry.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {records_success}/{records_processed} symbols'
                )
            )

        except Exception as e:
            # Update log entry on failure
            log_entry.status = 'FAILED'
            log_entry.error_message = str(e)
            log_entry.records_processed = records_processed
            log_entry.records_success = records_success
            log_entry.end_time = timezone.now()
            log_entry.calculate_duration()
            log_entry.save()

            self.stdout.write(
                self.style.ERROR(f'Script failed: {str(e)}')
            )
            raise

    def run_existing_camarilla_script(self):
        """Run the existing Camarilla script and return structured data"""
        try:
            # Add the script directory to Python path
            script_dir = os.path.dirname(SCRIPT_PATH)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)

            # Import the module
            spec = importlib.util.spec_from_file_location("camarilla_script", SCRIPT_PATH)
            camarilla_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(camarilla_module)

            # Read stock list from the existing script's input file
            stock_list_file = os.path.join(script_dir, 'input', 'stock_list.dat')
            if not os.path.exists(stock_list_file):
                self.stdout.write(self.style.ERROR(f'Stock list file not found: {stock_list_file}'))
                return []

            with open(stock_list_file) as f:
                lines = f.read().splitlines()

            camarilla_data = []
            self.stdout.write(f'Found {len(lines)} symbols to process')

            for line in lines:
                if not line.strip():
                    continue

                try:
                    val = line.split('|')
                    symbol = val[0]
                    instrument_type = val[1]
                    expiry_date = val[2]
                    option_type = val[3]
                    strike_price = val[4]

                    self.stdout.write(f'Processing {symbol}...')

                    # Use the existing function to get data
                    result = camarilla_module.get_camarilla_data_for_django(
                        symbol, instrument_type, expiry_date, option_type, strike_price
                    )

                    if result:
                        self.stdout.write(f'Successfully processed {symbol}')
                        camarilla_data.append(result)
                    else:
                        self.stdout.write(f'No data returned for {symbol}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing line: {line} - {str(e)}'))
                    continue

            self.stdout.write(f'Total records processed: {len(camarilla_data)}')
            return camarilla_data

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running existing script: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
            return []