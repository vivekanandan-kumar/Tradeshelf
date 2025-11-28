# admin.py
from django.contrib import admin
from .models import TradingSymbol, SymbolExpiry, CamarillaLevel, WholeNumberStock, ScriptRunLog, HistoricalData

@admin.register(TradingSymbol)
class TradingSymbolAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'instrument_type', 'is_active', 'created_at']
    list_filter = ['instrument_type', 'is_active']
    search_fields = ['symbol', 'name']

@admin.register(SymbolExpiry)
class SymbolExpiryAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'expiry_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'expiry_date']
    search_fields = ['symbol__symbol']

@admin.register(CamarillaLevel)
class CamarillaLevelAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'trade_date', 'expiry_date', 'prev_high', 'prev_low', 'prev_close']
    list_filter = ['trade_date', 'symbol']
    search_fields = ['symbol__symbol']

@admin.register(WholeNumberStock)
class WholeNumberStockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'trade_date', 'high', 'low', 'email_sent']
    list_filter = ['trade_date', 'email_sent']
    search_fields = ['symbol']
    date_hierarchy = 'trade_date'

@admin.register(ScriptRunLog)
class ScriptRunLogAdmin(admin.ModelAdmin):
    list_display = ['script_name', 'run_date', 'status', 'records_processed', 'duration_seconds']
    list_filter = ['script_name', 'status', 'run_date']
    date_hierarchy = 'run_date'

@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'trade_date', 'close_price', 'volume']
    list_filter = ['trade_date']
    search_fields = ['symbol__symbol']
    date_hierarchy = 'trade_date'