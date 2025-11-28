# models.py - Make sure this is your current structure
from django.db import models
from django.utils import timezone


class TradingSymbol(models.Model):
    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    instrument_type = models.CharField(max_length=50, choices=[
        ('STOCK', 'Stock'),
        ('FUTURE', 'Future'),
        ('OPTION', 'Option'),
        ('FUTIDX', 'Future Index'),
        ('FUTSTK', 'Future Stock'),
    ], default='FUTIDX')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trading_symbols'
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}" if self.name else f"{self.symbol}"


class SymbolExpiry(models.Model):
    symbol = models.ForeignKey(TradingSymbol, on_delete=models.CASCADE, related_name='expiries')
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['symbol', 'expiry_date']
        verbose_name_plural = "Symbol expiries"

    def __str__(self):
        return f"{self.symbol.symbol} - {self.expiry_date}"


class CamarillaLevel(models.Model):
    """Daily Camarilla levels for each symbol"""
    symbol = models.ForeignKey(TradingSymbol, on_delete=models.CASCADE, related_name='camarilla_levels')

    # Use expiry_date as ForeignKey to SymbolExpiry
    expiry_date = models.ForeignKey(SymbolExpiry, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='camarilla_levels')

    trade_date = models.DateField(db_index=True)

    # Previous day OHLC
    prev_open = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    prev_high = models.DecimalField(max_digits=12, decimal_places=2)
    prev_low = models.DecimalField(max_digits=12, decimal_places=2)
    prev_close = models.DecimalField(max_digits=12, decimal_places=2)

    # H4 - Long Breakout
    h4_level = models.DecimalField(max_digits=12, decimal_places=2)
    h4_sl = models.DecimalField(max_digits=12, decimal_places=2)
    h4_target1 = models.DecimalField(max_digits=12, decimal_places=2)
    h4_target2 = models.DecimalField(max_digits=12, decimal_places=2)
    h4_target3 = models.DecimalField(max_digits=12, decimal_places=2)

    # H3 - Reversal Sell
    h3_level = models.DecimalField(max_digits=12, decimal_places=2)
    h3_sl = models.DecimalField(max_digits=12, decimal_places=2)
    h3_target1 = models.DecimalField(max_digits=12, decimal_places=2)
    h3_target2 = models.DecimalField(max_digits=12, decimal_places=2)
    h3_target3 = models.DecimalField(max_digits=12, decimal_places=2)

    # L3 - Reversal Buy
    l3_level = models.DecimalField(max_digits=12, decimal_places=2)
    l3_sl = models.DecimalField(max_digits=12, decimal_places=2)
    l3_target1 = models.DecimalField(max_digits=12, decimal_places=2)
    l3_target2 = models.DecimalField(max_digits=12, decimal_places=2)
    l3_target3 = models.DecimalField(max_digits=12, decimal_places=2)

    # L4 - Short Breakout
    l4_level = models.DecimalField(max_digits=12, decimal_places=2)
    l4_sl = models.DecimalField(max_digits=12, decimal_places=2)
    l4_target1 = models.DecimalField(max_digits=12, decimal_places=2)
    l4_target2 = models.DecimalField(max_digits=12, decimal_places=2)
    l4_target3 = models.DecimalField(max_digits=12, decimal_places=2)

    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'camarilla_levels'
        unique_together = ['symbol', 'trade_date', 'expiry_date']
        ordering = ['-trade_date', 'symbol']

    def __str__(self):
        return f"{self.symbol.symbol} - {self.trade_date}"


class WholeNumberStock(models.Model):
    """Stocks with whole number highs and lows"""
    symbol = models.CharField(max_length=50, db_index=True)
    trade_date = models.DateField(db_index=True)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)

    high_is_round = models.BooleanField(default=False)
    low_is_round = models.BooleanField(default=False)

    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'whole_number_stocks'
        unique_together = ['symbol', 'trade_date']
        ordering = ['-trade_date', 'symbol']
        indexes = [
            models.Index(fields=['-trade_date']),
            models.Index(fields=['symbol', '-trade_date']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.trade_date}"


class ScriptRunLog(models.Model):
    """Log of script executions"""
    SCRIPT_CHOICES = [
        ('CAMARILLA', 'Camarilla Levels'),
        ('WHOLE_NUMBER', 'Whole Number Detection'),
    ]

    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    script_name = models.CharField(max_length=20, choices=SCRIPT_CHOICES)
    run_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    records_processed = models.IntegerField(default=0)
    records_success = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)

    error_message = models.TextField(null=True, blank=True)
    log_details = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'script_run_logs'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['-run_date', 'script_name']),
        ]

    def __str__(self):
        return f"{self.script_name} - {self.run_date} - {self.status}"

    def calculate_duration(self):
        """Calculate and save duration"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
            self.save(update_fields=['duration_seconds'])


class HistoricalData(models.Model):
    """Store historical OHLC data"""
    symbol = models.ForeignKey(TradingSymbol, on_delete=models.CASCADE, related_name='historical_data')
    trade_date = models.DateField(db_index=True)

    open_price = models.DecimalField(max_digits=12, decimal_places=2)
    high_price = models.DecimalField(max_digits=12, decimal_places=2)
    low_price = models.DecimalField(max_digits=12, decimal_places=2)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)

    volume = models.BigIntegerField(null=True, blank=True)
    open_interest = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historical_data'
        unique_together = ['symbol', 'trade_date']
        ordering = ['-trade_date']
        indexes = [
            models.Index(fields=['symbol', '-trade_date']),
        ]

    def __str__(self):
        return f"{self.symbol.symbol} - {self.trade_date}"