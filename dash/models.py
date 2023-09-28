from django.db import models
from django.utils import timezone


# Create your models here.
class Report(models.Model):
    id = models.BigIntegerField(primary_key=True)
    dt = models.DateTimeField()
    channel_id = models.IntegerField()
    city_id = models.IntegerField()
    start = models.DateTimeField()
    finish = models.DateTimeField()
    title = models.CharField(max_length=255)
    audience_hm = models.FloatField()
    reach_hm = models.FloatField()
    reach = models.FloatField()
    share = models.FloatField()
    tvr = models.FloatField()
    efir_year = models.IntegerField()
    efir_month = models.IntegerField()
    efir_week = models.IntegerField()
    efir_dayofweek = models.IntegerField()
    efir_day = models.IntegerField()
    efir_slot = models.IntegerField()

    class Meta:
        managed = False
        abstract = True


class Report2023(Report):
    class Meta:
        db_table = '[mediahills].[report_tvshows_2023_view]'


class Report2022(Report):
    class Meta:
        db_table = '[mediahills].[report_tvshows_2022_view]'


class Report2021(Report):
    class Meta:
        db_table = '[mediahills].[report_tvshows_2021_view]'


class Report2020(Report):
    class Meta:
        db_table = '[mediahills].[report_tvshows_2020_view]'


class Report2019(Report):
    class Meta:
        db_table = '[mediahills].[report_tvshows_2019_view]'


class ChannelView(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = '[mediahills].[channel_view]'


class CityView(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = '[mediahills].[city_view]'


class ContentView(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    class Meta:
        managed = False
        db_table = '[mediahills].[content_view]'


class ReportGeneral(models.Model):
    id = models.BigIntegerField(primary_key=True)
    dt = models.DateTimeField()
    channel_id = models.IntegerField()
    city_id = models.IntegerField()
    audience_hm = models.FloatField()
    reach_hm = models.FloatField()
    reach = models.FloatField()
    share = models.FloatField()
    tvr = models.FloatField()
    efir_year = models.IntegerField()
    efir_month = models.IntegerField()
    efir_week = models.IntegerField()
    efir_dayofweek = models.IntegerField()
    efir_day = models.IntegerField()

    class Meta:
        managed = False
        abstract = True


class ReportGeneral2023View(ReportGeneral):
    class Meta:
        db_table = '[mediahills].[report_general_2023_view]'


class ReportGeneral2022View(ReportGeneral):
    class Meta:
        db_table = '[mediahills].[report_general_2022_view]'


class ReportGeneral2021View(ReportGeneral):
    class Meta:
        db_table = '[mediahills].[report_general_2021_view]'


class ReportGeneral2020View(ReportGeneral):
    class Meta:
        db_table = '[mediahills].[report_general_2020_view]'


class ReportGeneral2019View(ReportGeneral):
    class Meta:
        db_table = '[mediahills].[report_general_2019_view]'
