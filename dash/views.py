from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.utils import timezone
from .forms import FilterFormTvshows, FilterFormProgram, FilterFormGeneral
from .models import ChannelView, CityView, ContentView
from .models import Report2023, Report2022, Report2021, Report2020, Report2019
from .models import ReportGeneral2019View, ReportGeneral2020View, ReportGeneral2021View, ReportGeneral2022View, ReportGeneral2023View
from django.db import connection
from io import BytesIO
import json
import pandas as pd


REPORTS = {
    '2023': Report2023.objects,
    '2022': Report2022.objects,
    '2021': Report2021.objects,
    '2020': Report2020.objects,
    '2019': Report2019.objects,
}

GENERAL_REPORTS = {
    '2023': ReportGeneral2023View.objects,
    '2022': ReportGeneral2022View.objects,
    '2021': ReportGeneral2021View.objects,
    '2020': ReportGeneral2020View.objects,
    '2019': ReportGeneral2019View.objects,
}

# Добавить виджет фильтра по фильму
# Добавить вкладки с другими отчетами сверху

# Отчеты
# По каналам
# По программе
# По дням
# По слотам

# Фильтр между годами, месяцами, выходными
# Вкладка Программы канала


def tvshows_report(request):

    form = FilterFormTvshows()

    if request.GET:
        form = FilterFormTvshows(request.GET)
        form.fields['channel_id'].choices = ChannelView.objects.values_list('id', 'name')

    if form.is_valid():
        channel_id = form.cleaned_data['channel_id']
        city_id = form.cleaned_data['city_id']
        year = form.cleaned_data['year']

        data = REPORTS[year].filter(
            channel_id__in=channel_id, city_id=city_id)

        if data.exists():
            report = generate_tvshows_report(data)

        if request.GET.get('submit', None) == 'Скачать Excel':
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                report.to_excel(excel_writer=writer)
                writer.close()
                time = timezone.now()
                filename = f'{time.year}_{time.hour}_{time.minute}_report_tvshows'

                return HttpResponse(
                    b.getvalue(),
                    headers={
                        "Content-Type": "application/vnd.ms-excel",
                        "Content-Disposition": 'attachment; filename="%s.xlsx"' % filename,
                    }
                )

    try:
        report = report.to_html(classes="table table-bordered")
    except NameError:
        report = None

    return render(request, 'dash/index.html', {
        'form': form,
        'table': report,
    })


def get_titles(request):
    title = request.GET.get('query', '')

    data = ContentView.objects.all()
    data = list(data.filter(name__icontains=title).values(
        'name')[:100])

    return JsonResponse({'data': data})


def generate_programs_report(request):

    form = FilterFormProgram()

    if request.GET:
        form = FilterFormProgram(request.GET)
        form.fields['titles'].choices = ContentView.objects.values_list('name', 'name')

    if form.is_valid():
        channel_id = form.cleaned_data['channel_id']
        city_id = form.cleaned_data['city_id']
        year = form.cleaned_data['year']
        titles = form.cleaned_data['titles']

        if channel_id: 
            # if channel_id == -1:
            data = REPORTS[year].filter(
                channel_id__in=channel_id, 
                city_id=city_id, 
                title__in=titles
            )
        else:
            data = REPORTS[year].filter(city_id=city_id, title__in=titles)

        if data.exists():
            report = generate_tvshows_report(data)

            if request.GET.get('submit', None) == 'Скачать Excel':
                with BytesIO() as b:
                    writer = pd.ExcelWriter(b, engine='xlsxwriter')
                    report.to_excel(excel_writer=writer)
                    writer.close()
                    time = timezone.now()
                    filename = f'{time.year}_{time.hour}_{time.minute}_report_programs'

                    return HttpResponse(
                        b.getvalue(),
                        headers={
                            "Content-Type": "application/vnd.ms-excel",
                            "Content-Disposition": 'attachment; filename="%s.xlsx"' % filename,
                        }
                    )

    try:
        report = report.to_html(classes="table table-bordered")
    except NameError:
        report = None

    return render(request, 'dash/programs.html', {
        'form': form,
        'table': report,
    })


def general_report(request):
    form = FilterFormGeneral()

    if request.GET:
        form = FilterFormGeneral(request.GET)

    if form.is_valid():
        channel_id = form.cleaned_data['channel_id']
        city_id = form.cleaned_data['city_id']
        year = form.cleaned_data['year']
        month = form.cleaned_data['month']

        data = GENERAL_REPORTS[year].filter(
            channel_id__in=channel_id, city_id=city_id, efir_month=month)

        if data.exists():
            report = pd.DataFrame(data.values())

            channel_ids = pd.DataFrame(ChannelView.objects.filter(
                id__in=data.values('channel_id').distinct()).values('id', 'name'))
            channel_ids = channel_ids.rename(
                columns={"id": "channel_id", "name": "channel_name"})
            report = pd.merge(report, channel_ids, on='channel_id', how='left')

            report['city_name'] = (CityView.objects.get(
                pk=data.first().city_id)).name

            report["date"] = pd.DatetimeIndex(
                report["dt"]).date
            report["year"] = pd.DatetimeIndex(
                report["dt"]).year
            report["month"] = pd.DatetimeIndex(
                report["dt"]).month
            report["day"] = pd.DatetimeIndex(
                report["dt"]).day
            report["time"] = pd.DatetimeIndex(
                report["dt"]).time
            report["hour"] = pd.DatetimeIndex(
                report["dt"]).hour
            report["minute"] = pd.DatetimeIndex(
                report["dt"]).minute
            report["week_number"] = 'w' + (pd.DatetimeIndex(
                report["dt"].dt.isocalendar().week)).astype(str)
            report["week_day_num"] = (
                pd.DatetimeIndex(report["date"])).dayofweek

            report["verify"] = report["year"].astype(str) + "_" + report["month"].astype(
                str) + "_" + report["day"].astype(str) + "_" + report["hour"].astype(str) + "_" + report["minute"].astype(str) + "_"

            weekday = pd.DataFrame({'week_day_num': [0, 1, 2, 3, 4, 5, 6],
                                    'weekday': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']})

            report = pd.merge(report,
                              weekday,
                              on='week_day_num',
                              how='left')

            report = pd.pivot_table(report, index=[
                'channel_name', 'year'], columns=['month'], values='tvr', aggfunc='mean')

    try:
        report = report.to_html(classes="table table-bordered")
    except NameError:
        report = None

    return render(request, 'dash/general.html', {
        'form': form,
        'table': report
    })


def generate_tvshows_report(query):

    report = pd.DataFrame(query.values())

    report['start'] = pd.DatetimeIndex(
        report['start']
    ).time

    report['finish'] = pd.DatetimeIndex(
        report['finish']
    ).time

    channel_ids = pd.DataFrame(ChannelView.objects.filter(
        id__in=query.values('channel_id').distinct()).values('id', 'name'))
    channel_ids = channel_ids.rename(
        columns={"id": "channel_id", "name": "channel_name"})
    report = pd.merge(report, channel_ids, on='channel_id', how='left')

    report['city_name'] = (CityView.objects.get(pk=query.first().city_id)).name

    # Create and convert date tables
    report['date'] = pd.DatetimeIndex(
        report['dt']).date
    report["year"] = pd.DatetimeIndex(
        report["dt"]).year
    report["month"] = pd.DatetimeIndex(
        report["dt"]).month
    report["day"] = pd.DatetimeIndex(report["dt"]).day
    report["time"] = pd.DatetimeIndex(report["dt"]).time
    report["hour"] = pd.DatetimeIndex(report["dt"]).hour
    report["minute"] = pd.DatetimeIndex(report["dt"]).minute
    report["week_number"] = (pd.DatetimeIndex(
        report["dt"].dt.isocalendar().week)).astype(str)
    report["week_day_num"] = (
        pd.DatetimeIndex(report["date"])).dayofweek

    report["verify"] = report["year"].astype(str) + "_" + report["month"].astype(
        str) + "_" + report["day"].astype(str) + "_" + report["hour"].astype(str) + "_" + report["minute"].astype(str) + "_"

    weekday = pd.DataFrame({'week_day_num': [0, 1, 2, 3, 4, 5, 6],
                            'weekday': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']})

    report = pd.merge(report,
                      weekday,
                      on='week_day_num',
                      how='left')

    maximum = report["tvr"].max()
    minimum = report["tvr"].min()
    mean = report["tvr"].mean()
    median = report["tvr"].median()
    std = report["tvr"].std()

    UP = median + 3 * std
    DOWN = median - 3 * std

    ok_data_DOWN = report.loc[(report["tvr"] > DOWN) & (
        report["tvr"] < median)]
    ok_data_UP = report.loc[(report["tvr"] < UP) & (
        report["tvr"] > median)]
    DOWNmedian = (ok_data_DOWN['tvr']).median()
    UPmedian = (ok_data_UP['tvr']).median()

    report.loc[report["tvr"] >= UP, "tier"] = 'A+'
    report.loc[report["tvr"] < DOWN, "tier"] = 'D'
    report.loc[(report["tvr"] >= DOWN) & (
        report["tvr"] < median), "tier"] = 'C'
    report.loc[(report["tvr"] >= median) & (
        report["tvr"] < UPmedian), "tier"] = 'B'
    report.loc[(report["tvr"] >= UPmedian) & (
        report["tvr"] < UP), "tier"] = 'A'

    to_graph = report.drop(columns=['id', 'channel_id', 'city_id', 'efir_dayofweek', 'efir_day',
                                    'efir_slot', 'dt', 'year', 'month', 'day', 'time', 'hour', 'minute', 'week_number', 'week_day_num', 'verify'])

    report = to_graph.sort_values(
        by=['tvr', 'date'], ascending=False)

    return report
