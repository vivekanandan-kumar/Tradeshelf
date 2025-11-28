from rest_framework import serializers
from .models import CamarillaLevel, WholeNumberStock, ScriptRunLog, HistoricalData, TradingSymbol


class TradingSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingSymbol
        fields = '__all__'


class CamarillaLevelSerializer(serializers.ModelSerializer):
    symbol_name = serializers.CharField(source='symbol.symbol', read_only=True)

    class Meta:
        model = CamarillaLevel
        fields = '__all__'


class WholeNumberStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = WholeNumberStock
        fields = '__all__'


class ScriptRunLogSerializer(serializers.ModelSerializer):
    duration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = ScriptRunLog
        fields = '__all__'

    def get_duration_formatted(self, obj):
        if obj.duration_seconds:
            mins = obj.duration_seconds // 60
            secs = obj.duration_seconds % 60
            return f"{mins}m {secs}s"
        return None


class HistoricalDataSerializer(serializers.ModelSerializer):
    symbol_name = serializers.CharField(source='symbol.symbol', read_only=True)

    class Meta:
        model = HistoricalData
        fields = '__all__'