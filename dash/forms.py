from django import forms
from .models import CityView, ChannelView, ContentView


YEARS = [
    ('2019', '2019'),
    ('2020', '2020'),
    ('2021', '2021'),
    ('2022', '2022'),
    ('2023', '2023'),
]

MONTHS = (
    (1, 'Январь'),
    (2, 'Февраль'),
    (3, 'Март'),
    (4, 'Апрель'),
    (5, 'Май'),
    (6, 'Июнь'),
    (7, 'Июль'),
    (8, 'Август'),
    (9, 'Сентябрь'),
    (10, 'Октябрь'),
    (11, 'Ноябрь'),
    (12, 'Декабрь'),
)


class FilterForm(forms.Form):
    channel_id = forms.MultipleChoiceField(label="Название канала", widget=forms.SelectMultiple(attrs={'id': 'select-channels'}), choices=ChannelView.objects.values_list('id', 'name')
                                           )
    city_id = forms.ChoiceField(label="Название города",
                                choices=reversed(CityView.objects.values_list('id', 'name')), widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(
        label="Год", widget=forms.Select(attrs={'class': 'form-select'}), choices=YEARS)


class FilterFormTvshows(FilterForm):
    pass


class FilterFormProgram(FilterForm):
    channel_id = forms.MultipleChoiceField(label="Название канала", widget=forms.SelectMultiple(
        attrs={'id': 'select-channels'}), choices=ChannelView.objects.values_list('id', 'name'), required=False)
    titles = forms.MultipleChoiceField(
        label="Программы для отчета", widget=forms.SelectMultiple(attrs={'id': 'select-programs'}))


class FilterFormGeneral(FilterForm):
    month = forms.ChoiceField(label="Месяц", widget=forms.Select(
        attrs={'class': 'form-select'}), choices=MONTHS)
