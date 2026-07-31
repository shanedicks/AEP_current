"""Pure helpers in core/utils.py -- no database."""
import csv
import datetime
import io

import pytest
from django.utils import timezone

from core.utils import (
    get_fiscal_year_end_date,
    get_fiscal_year_start_date,
    plivo_num,
    render_to_csv,
    time_string_to_hours,
)


class TestFiscalYear:
    """Fiscal year runs 1 July -- 30 June."""

    @pytest.mark.parametrize('today,start,end', [
        # Just after the boundary.
        ((2026, 7, 1), (2026, 7, 1), (2027, 6, 30)),
        ((2026, 12, 31), (2026, 7, 1), (2027, 6, 30)),
        # Just before it: still the previous fiscal year.
        ((2026, 6, 30), (2025, 7, 1), (2026, 6, 30)),
        ((2026, 1, 1), (2025, 7, 1), (2026, 6, 30)),
    ])
    def test_boundaries(self, monkeypatch, today, start, end):
        frozen = timezone.make_aware(datetime.datetime(*today, 12, 0))
        monkeypatch.setattr(timezone, 'now', lambda: frozen)
        assert get_fiscal_year_start_date() == datetime.date(*start)
        assert get_fiscal_year_end_date() == datetime.date(*end)

    def test_start_always_precedes_end(self, monkeypatch):
        for month in range(1, 13):
            frozen = timezone.make_aware(datetime.datetime(2026, month, 15))
            monkeypatch.setattr(timezone, 'now', lambda f=frozen: f)
            assert get_fiscal_year_start_date() < get_fiscal_year_end_date()


class TestTimeStringToHours:

    @pytest.mark.parametrize('value,expected', [
        ('01:00:00', 1.0),
        ('00:30:00', 0.5),
        ('02:15:00', 2.25),
        ('00:00:00', 0.0),
        ('10:20:00', 10.33),
    ])
    def test_essential_ed_format(self, value, expected):
        assert time_string_to_hours(value, 'Essential Ed') == expected

    @pytest.mark.parametrize('value,expected', [
        ('1h 0m', 1.0),
        ('0h 30m', 0.5),
        ('2h 15m', 2.25),
        ('10h 20m', 10.33),
    ])
    def test_duolingo_format(self, value, expected):
        assert time_string_to_hours(value, 'Duolingo') == expected

    def test_unknown_source_raises_unbound_local(self):
        """Neither branch runs, so hours_float is never assigned.

        Characterising current behaviour: an unrecognised source fails with
        UnboundLocalError rather than a clear error.
        """
        with pytest.raises(UnboundLocalError):
            time_string_to_hours('01:00:00', 'Some Other Source')


class TestRenderToCsv:

    def read_back(self, response):
        return list(csv.reader(io.StringIO(response.content.decode())))

    def test_sets_csv_content_type_and_filename(self):
        response = render_to_csv([['a']], 'report.csv')
        assert response['Content-Type'] == 'text/csv'
        assert response['Content-Disposition'] == (
            'attachment; filename="report.csv"'
        )

    def test_writes_every_row_in_order(self):
        data = [['Last', 'First'], ['Doe', 'Jane'], ['Roe', 'Ann']]
        assert self.read_back(render_to_csv(data, 'r.csv')) == data

    def test_empty_data_yields_empty_body(self):
        assert render_to_csv([], 'r.csv').content == b''

    def test_commas_and_quotes_are_escaped(self):
        data = [['Doe, Jane', 'say "hi"']]
        assert self.read_back(render_to_csv(data, 'r.csv')) == data


def test_plivo_num_prefixes_country_code():
    assert plivo_num('5045551234') == '15045551234'
