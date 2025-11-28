from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db import models
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CamarillaLevel, WholeNumberStock, ScriptRunLog, TradingSymbol, HistoricalData, SymbolExpiry
from .serializers import CamarillaLevelSerializer, WholeNumberStockSerializer, ScriptRunLogSerializer
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.utils import timezone
import subprocess
import threading
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_staff or user.is_superuser


def dashboard_home(request):
    """Main dashboard view - Public facing"""
    # Get counts for stats
    camarilla_count = CamarillaLevel.objects.count()
    whole_num_count = WholeNumberStock.objects.count()

    # Get latest script runs
    latest_camarilla = ScriptRunLog.objects.filter(script_name='CAMARILLA').order_by('-start_time').first()
    latest_whole_num = ScriptRunLog.objects.filter(script_name='WHOLE_NUMBER').order_by('-start_time').first()
    recent_logs = ScriptRunLog.objects.order_by('-start_time')[:5]

    context = {
        'camarilla_count': camarilla_count,
        'whole_num_count': whole_num_count,
        'latest_camarilla': latest_camarilla,
        'latest_whole_num': latest_whole_num,
        'recent_logs': recent_logs,
        'show_admin_features': is_admin(request.user)
    }
    return render(request, 'trading/dashboard.html', context)


def admin_dashboard(request):
    """Admin dashboard view"""
    if not is_admin(request.user):
        return redirect('trading:dashboard')

    # Get counts for stats
    camarilla_count = CamarillaLevel.objects.count()
    whole_num_count = WholeNumberStock.objects.count()

    # Get latest script runs
    latest_camarilla = ScriptRunLog.objects.filter(script_name='CAMARILLA').order_by('-start_time').first()
    latest_whole_num = ScriptRunLog.objects.filter(script_name='WHOLE_NUMBER').order_by('-start_time').first()
    recent_logs = ScriptRunLog.objects.order_by('-start_time')[:5]

    context = {
        'camarilla_count': camarilla_count,
        'whole_num_count': whole_num_count,
        'latest_camarilla': latest_camarilla,
        'latest_whole_num': latest_whole_num,
        'recent_logs': recent_logs,
        'show_admin_features': True,
    }
    return render(request, 'trading/admin_dashboard.html', context)

# views.py - Updated to match model field names
def camarilla_levels_view(request):
    """Camarilla levels list view"""
    symbol_filter = request.GET.get('symbol', '')
    date_filter = request.GET.get('date', '')
    expiry_filter = request.GET.get('expiry', '')

    camarilla_levels = CamarillaLevel.objects.select_related('symbol', 'expiry_date').order_by('-trade_date', 'symbol')

    if symbol_filter:
        camarilla_levels = camarilla_levels.filter(symbol__symbol__icontains=symbol_filter)

    if date_filter:
        camarilla_levels = camarilla_levels.filter(trade_date=date_filter)

    if expiry_filter:
        # Convert string to date object for comparison
        from datetime import datetime
        try:
            expiry_date = datetime.strptime(expiry_filter, '%Y-%m-%d').date()
            camarilla_levels = camarilla_levels.filter(expiry_date__expiry_date=expiry_date)
        except ValueError:
            # Handle invalid date format
            pass

    symbols = TradingSymbol.objects.filter(is_active=True)
    expiries = SymbolExpiry.objects.filter(is_active=True).order_by('-expiry_date')

    context = {
        'camarilla_levels': camarilla_levels,
        'symbols': symbols,
        'expiries': expiries,
        'symbol_filter': symbol_filter,
        'date_filter': date_filter,
        'expiry_filter': expiry_filter,
    }
    return render(request, 'trading/camarilla_list.html', context)

def camarilla_detail_view(request, pk):
    """Camarilla level detail view"""
    camarilla_level = get_object_or_404(CamarillaLevel.objects.select_related('symbol', 'expiry_date'), pk=pk)

    # Get last 2 runs for the same symbol and expiry
    historical = CamarillaLevel.objects.filter(
        symbol=camarilla_level.symbol,
        expiry_date=camarilla_level.expiry_date
    ).exclude(pk=pk).order_by('-trade_date')[:2]

    context = {
        'level': camarilla_level,
        'historical': historical,
    }
    return render(request, 'trading/camarilla_detail.html', context)


@staff_member_required
def symbol_management(request):
    """Symbol and expiry management view"""
    symbols = TradingSymbol.objects.all().order_by('symbol')
    expiries = SymbolExpiry.objects.all().select_related('symbol').order_by('-expiry_date')

    if request.method == 'POST':
        # Handle symbol creation
        if 'add_symbol' in request.POST:
            symbol = request.POST.get('symbol')
            name = request.POST.get('name')
            instrument_type = request.POST.get('instrument_type')

            TradingSymbol.objects.create(
                symbol=symbol,
                name=name,
                instrument_type=instrument_type
            )

        # Handle expiry creation
        elif 'add_expiry' in request.POST:
            symbol_id = request.POST.get('symbol')
            expiry_date = request.POST.get('expiry_date')

            symbol = TradingSymbol.objects.get(id=symbol_id)
            SymbolExpiry.objects.create(
                symbol=symbol,
                expiry_date=expiry_date
            )

    context = {
        'symbols': symbols,
        'expiries': expiries,
    }
    return render(request, 'trading/symbol_management.html', context)


def whole_number_view(request):
    """Whole number stocks list view"""
    symbol_filter = request.GET.get('symbol', '')
    date_filter = request.GET.get('date', '')

    whole_numbers = WholeNumberStock.objects.order_by('-trade_date', 'symbol')

    if symbol_filter:
        whole_numbers = whole_numbers.filter(symbol__icontains=symbol_filter)

    if date_filter:
        whole_numbers = whole_numbers.filter(trade_date=date_filter)

    # Only show stocks where either high or low is round
    whole_numbers = whole_numbers.filter(Q(high_is_round=True) | Q(low_is_round=True))

    context = {
        'whole_numbers': whole_numbers,
        'symbol_filter': symbol_filter,
        'date_filter': date_filter,
    }
    return render(request, 'trading/whole_number_list.html', context)


def script_logs_view(request):
    """Script execution logs view"""
    script_filter = request.GET.get('script', 'ALL')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    logs = ScriptRunLog.objects.order_by('-start_time')

    if script_filter and script_filter != 'ALL':
        logs = logs.filter(script_name=script_filter)

    if status_filter:
        logs = logs.filter(status=status_filter)

    if date_filter:
        logs = logs.filter(start_time__date=date_filter)

    # Calculate statistics
    total_runs = logs.count()
    success_runs = logs.filter(status='SUCCESS').count()
    success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0

    # Fix for avg_duration calculation
    from django.db.models import Avg
    avg_duration_result = logs.aggregate(avg_duration=Avg('duration_seconds'))
    avg_duration = avg_duration_result['avg_duration'] or 0

    context = {
        'logs': logs,
        'script_type': script_filter,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'stats': {
            'total_runs': total_runs,
            'success_rate': success_rate,
            'avg_duration': round(avg_duration, 1),
        }
    }
    return render(request, 'trading/script_logs.html', context)


def analytics_view(request):
    """Analytics dashboard view"""
    from django.db.models import Count
    import json
    from datetime import datetime, timedelta

    # Get period from request or default to 30 days
    period = int(request.GET.get('period', 30))
    start_date = datetime.now().date() - timedelta(days=period)

    # Camarilla data by date
    camarilla_by_date = CamarillaLevel.objects.filter(
        trade_date__gte=start_date
    ).values('trade_date').annotate(
        count=Count('id')
    ).order_by('trade_date')

    # Whole number data by date
    whole_num_by_date = WholeNumberStock.objects.filter(
        trade_date__gte=start_date
    ).values('trade_date').annotate(
        count=Count('id')
    ).order_by('trade_date')

    # Script statistics
    script_stats = ScriptRunLog.objects.filter(
        start_time__date__gte=start_date
    ).values('script_name').annotate(
        count=Count('id')
    )

    # Active symbols
    active_symbols = CamarillaLevel.objects.filter(
        trade_date__gte=start_date
    ).values('symbol__symbol').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    context = {
        'camarilla_by_date': json.dumps(list(camarilla_by_date)),
        'whole_num_by_date': json.dumps(list(whole_num_by_date)),
        'script_stats': json.dumps(list(script_stats)),
        'active_symbols': list(active_symbols),
        'period': period,
    }
    return render(request, 'trading/analytics.html', context)


# API ViewSets
class CamarillaLevelViewSet(viewsets.ModelViewSet):
    """API ViewSet for Camarilla Levels"""
    queryset = CamarillaLevel.objects.select_related('symbol').order_by('-trade_date')
    serializer_class = CamarillaLevelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get('symbol', None)
        date = self.request.query_params.get('date', None)

        if symbol:
            queryset = queryset.filter(symbol__symbol__icontains=symbol)
        if date:
            queryset = queryset.filter(trade_date=date)

        return queryset


class WholeNumberStockViewSet(viewsets.ModelViewSet):
    """API ViewSet for Whole Number Stocks"""
    queryset = WholeNumberStock.objects.order_by('-trade_date')
    serializer_class = WholeNumberStockSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get('symbol', None)
        date = self.request.query_params.get('date', None)

        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol)
        if date:
            queryset = queryset.filter(trade_date=date)

        return queryset


class ScriptRunLogViewSet(viewsets.ModelViewSet):
    """API ViewSet for Script Run Logs"""
    queryset = ScriptRunLog.objects.order_by('-start_time')
    serializer_class = ScriptRunLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        script_name = self.request.query_params.get('script_name', None)
        status = self.request.query_params.get('status', None)

        if script_name:
            queryset = queryset.filter(script_name=script_name)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


# API Endpoints for Script Execution
@csrf_exempt
@require_http_methods(["POST"])
def run_camarilla_script(request):
    """Execute Camarilla script via AJAX"""
    try:
        # Create log entry first
        log_entry = ScriptRunLog.objects.create(
            script_name='CAMARILLA',
            status='RUNNING',
            start_time=timezone.now()
        )

        def run_script():
            try:
                # Update log to RUNNING
                log_entry.status = 'RUNNING'
                log_entry.save()

                # Run the command
                call_command('run_camarilla')

                # Update log to SUCCESS
                log_entry.status = 'SUCCESS'
                log_entry.end_time = timezone.now()
                log_entry.calculate_duration()

                # Get the actual counts from the latest log
                latest_log = ScriptRunLog.objects.filter(
                    script_name='CAMARILLA'
                ).order_by('-start_time').first()

                if latest_log:
                    log_entry.records_processed = latest_log.records_processed
                    log_entry.records_success = latest_log.records_success

                log_entry.save()

            except Exception as e:
                # Update log to FAILED
                log_entry.status = 'FAILED'
                log_entry.error_message = str(e)
                log_entry.end_time = timezone.now()
                log_entry.calculate_duration()
                log_entry.save()

        # Run in background thread
        thread = threading.Thread(target=run_script)
        thread.daemon = True
        thread.start()

        return JsonResponse({
            'status': 'success',
            'message': 'Camarilla script started successfully',
            'log_id': log_entry.id
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error starting script: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_whole_number_script(request):
    """Execute Whole Number script via AJAX"""
    try:
        # Create log entry first
        log_entry = ScriptRunLog.objects.create(
            script_name='WHOLE_NUMBER',
            status='RUNNING',
            start_time=timezone.now()
        )

        def run_script():
            try:
                # Update log to RUNNING
                log_entry.status = 'RUNNING'
                log_entry.save()

                # Run the command
                call_command('run_whole_number')

                # Update log to SUCCESS
                log_entry.status = 'SUCCESS'
                log_entry.end_time = timezone.now()
                log_entry.calculate_duration()

                # Get the actual counts from the latest log
                latest_log = ScriptRunLog.objects.filter(
                    script_name='WHOLE_NUMBER'
                ).order_by('-start_time').first()

                if latest_log:
                    log_entry.records_processed = latest_log.records_processed
                    log_entry.records_success = latest_log.records_success

                log_entry.save()

            except Exception as e:
                # Update log to FAILED
                log_entry.status = 'FAILED'
                log_entry.error_message = str(e)
                log_entry.end_time = timezone.now()
                log_entry.calculate_duration()
                log_entry.save()

        # Run in background thread
        thread = threading.Thread(target=run_script)
        thread.daemon = True
        thread.start()

        return JsonResponse({
            'status': 'success',
            'message': 'Whole Number script started successfully',
            'log_id': log_entry.id
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error starting script: {str(e)}'
        }, status=500)


def get_script_status(request):
    """Get current script execution status"""
    # Check for currently running scripts
    running_camarilla = ScriptRunLog.objects.filter(
        script_name='CAMARILLA',
        status='RUNNING'
    ).order_by('-start_time').first()

    running_whole_number = ScriptRunLog.objects.filter(
        script_name='WHOLE_NUMBER',
        status='RUNNING'
    ).order_by('-start_time').first()

    # Get latest completed scripts
    latest_camarilla = ScriptRunLog.objects.filter(
        script_name='CAMARILLA'
    ).exclude(status='RUNNING').order_by('-start_time').first()

    latest_whole_number = ScriptRunLog.objects.filter(
        script_name='WHOLE_NUMBER'
    ).exclude(status='RUNNING').order_by('-start_time').first()

    response_data = {
        'camarilla': {
            'status': running_camarilla.status if running_camarilla else
                     (latest_camarilla.status if latest_camarilla else 'NOT_RUN'),
            'last_run': (running_camarilla.start_time if running_camarilla else
                        latest_camarilla.start_time if latest_camarilla else None),
            'duration': (running_camarilla.duration_seconds if running_camarilla else
                        latest_camarilla.duration_seconds if latest_camarilla else None),
            'is_running': bool(running_camarilla),
            'records_processed': (running_camarilla.records_processed if running_camarilla else
                                latest_camarilla.records_processed if latest_camarilla else 0),
            'records_success': (running_camarilla.records_success if running_camarilla else
                              latest_camarilla.records_success if latest_camarilla else 0),
        },
        'whole_number': {
            'status': running_whole_number.status if running_whole_number else
                     (latest_whole_number.status if latest_whole_number else 'NOT_RUN'),
            'last_run': (running_whole_number.start_time if running_whole_number else
                        latest_whole_number.start_time if latest_whole_number else None),
            'duration': (running_whole_number.duration_seconds if running_whole_number else
                        latest_whole_number.duration_seconds if latest_whole_number else None),
            'is_running': bool(running_whole_number),
            'records_processed': (running_whole_number.records_processed if running_whole_number else
                                latest_whole_number.records_processed if latest_whole_number else 0),
            'records_success': (running_whole_number.records_success if running_whole_number else
                              latest_whole_number.records_success if latest_whole_number else 0),
        },
    }

    return JsonResponse(response_data)