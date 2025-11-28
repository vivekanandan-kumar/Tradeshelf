# trading/management/commands/run_whole_number.py
import os
import sys
import django
from django.core.management.base import BaseCommand
from trading.models import ScriptRunLog, WholeNumberStock
from django.utils import timezone
from datetime import date, datetime
import importlib.util

# Add the path to your existing script
SCRIPT_PATH = '/Users/vivekanandan/PycharmProjects/DjangoProject/Tradeshelf/scripts/Whole_Number/st_whole_num_v2.py'


class Command(BaseCommand):
    help = 'Detect whole number stocks using existing script and save to database'

    def handle(self, *args, **options):
        # Create log entry
        log_entry = ScriptRunLog.objects.create(
            script_name='WHOLE_NUMBER',
            status='RUNNING',
            start_time=timezone.now()
        )

        records_processed = 0
        records_success = 0

        try:
            self.stdout.write('Starting Whole Number detection using existing script...')

            # Run the existing script
            whole_number_data = self.run_existing_whole_number_script()

            if not whole_number_data:
                self.stdout.write(self.style.WARNING('No data returned from Whole Number script'))
                # Update log for empty result but mark as success
                log_entry.status = 'SUCCESS'
                log_entry.records_processed = 0
                log_entry.records_success = 0
                log_entry.end_time = timezone.now()
                log_entry.calculate_duration()
                log_entry.save()
                self.stdout.write(self.style.SUCCESS('Script completed (no data found)'))
                return

            # Process each stock
            for stock_data in whole_number_data:
                try:
                    symbol = stock_data['symbol']
                    trade_date = stock_data.get('trade_date', date.today())

                    # Skip if already exists for today
                    if WholeNumberStock.objects.filter(
                            symbol=symbol,
                            trade_date=trade_date
                    ).exists():
                        self.stdout.write(f'Skipping {symbol} - already exists for {trade_date}')
                        records_processed += 1
                        records_success += 1
                        continue

                    # Create WholeNumberStock entry
                    whole_number_stock = WholeNumberStock.objects.create(
                        symbol=symbol,
                        trade_date=trade_date,
                        high=stock_data['high'],
                        low=stock_data['low'],
                        open_price=stock_data.get('open'),
                        close_price=stock_data.get('close'),
                        volume=stock_data.get('volume'),
                        high_is_round=stock_data['high_is_round'],
                        low_is_round=stock_data['low_is_round']
                    )

                    records_success += 1
                    records_processed += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Processed {symbol} - High: {stock_data["high"]} (Round: {stock_data["high_is_round"]}), Low: {stock_data["low"]} (Round: {stock_data["low_is_round"]})')
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {stock_data.get("symbol", "unknown")}: {str(e)}')
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
                    f'Successfully processed {records_success}/{records_processed} stocks'
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

    def run_existing_whole_number_script(self):
        """Run the existing Whole Number script and return structured data"""
        try:
            # Add the script directory to Python path
            script_dir = os.path.dirname(SCRIPT_PATH)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)

            # Import the module
            spec = importlib.util.spec_from_file_location("whole_number_script", SCRIPT_PATH)
            whole_number_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(whole_number_module)

            # Use the Django integration function
            result_data = whole_number_module.get_whole_number_data_for_django()

            return result_data

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running existing script: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
            return []