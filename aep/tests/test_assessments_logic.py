"""Pure logic in assessments/models.py -- no database.

These are the NRS cut scores and form-rotation rules that drive state reporting,
so the tests are deliberately table-driven and pin every boundary. Everything
here operates on unsaved instances, which also sidesteps the save() -> Celery
cascade entirely.
"""
import datetime

import pytest

from assessments.models import Clas_E, Tabe


class TestTabeGetLevel:
    """Tabe.get_level is the NRS cut-score table.

    Boundaries per subject (score < cut -> level):
        read (501, 536, 576, 800)
        math (496, 537, 596, 800)
        lang (511, 547, 584, 800)
    Below the first cut is 'E', then 'M', 'D', 'A', and at/above the last '*'.
    """

    @pytest.mark.parametrize('subject,cuts', [
        ('read', (501, 536, 576, 800)),
        ('math', (496, 537, 596, 800)),
        ('lang', (511, 547, 584, 800)),
    ])
    def test_boundaries(self, subject, cuts):
        first, second, third, fourth = cuts
        # One below each cut and exactly at each cut -- the off-by-one guard.
        assert Tabe.get_level(first - 1, None, subject) == 'E'
        assert Tabe.get_level(first, None, subject) == 'M'
        assert Tabe.get_level(second - 1, None, subject) == 'M'
        assert Tabe.get_level(second, None, subject) == 'D'
        assert Tabe.get_level(third - 1, None, subject) == 'D'
        assert Tabe.get_level(third, None, subject) == 'A'
        assert Tabe.get_level(fourth - 1, None, subject) == 'A'
        assert Tabe.get_level(fourth, None, subject) == '*'

    @pytest.mark.parametrize('subject', ['read', 'math', 'lang'])
    def test_none_score_returns_dash(self, subject):
        assert Tabe.get_level(None, None, subject) == '-'

    @pytest.mark.parametrize('subject', ['read', 'math', 'lang'])
    def test_zero_scores_as_lowest_level(self, subject):
        assert Tabe.get_level(0, None, subject) == 'E'

    def test_level_argument_is_ignored(self):
        """The `level` parameter is overwritten before use -- it is dead.

        Pinned so that removing the argument is a deliberate signature change
        rather than something that silently alters behaviour.
        """
        assert Tabe.get_level(520, 'IGNORED', 'read') == 'M'
        assert Tabe.get_level(None, 'IGNORED', 'read') == '-'


class TestTabeAssign:
    """Form rotation plus the three level lookups."""

    @pytest.mark.parametrize('current,expected', [
        ('11', '12'),
        ('12', '11'),
        ('13', '14'),
        # Anything that is not 11/12/13 falls through to '13'.
        ('14', '13'),
        ('', '13'),
    ])
    def test_form_rotation(self, current, expected):
        tabe = Tabe(form=current, read_ss=520, total_math_ss=520, lang_ss=520)
        assert tabe.assign().split()[0] == expected

    def test_uses_total_math_ss_not_math_comp_ss(self):
        """assign() reads total_math_ss; math_comp_ss must not affect it."""
        tabe = Tabe(
            form='11',
            read_ss=520,
            total_math_ss=490,   # below the math 'E' cut of 496
            math_comp_ss=700,    # would be 'A' if this were the field used
            lang_ss=520,
        )
        assert tabe.assign() == '12 M E M'

    def test_missing_scores_render_as_dash(self):
        tabe = Tabe(form='11')
        assert tabe.assign() == '12 - - -'


class TestTabeCheckGain:
    """check_gain compares this test against a pretest."""

    def test_clas_e_pretest_only_gains_on_read_level_4_to_m(self):
        pretest = Clas_E(read_level='4')
        assert Tabe(read_level='M').check_gain(pretest) is True

    @pytest.mark.parametrize('pre_level,post_level', [
        ('4', 'D'),   # right pretest level, wrong post level
        ('3', 'M'),   # wrong pretest level, right post level
        ('3', 'D'),
    ])
    def test_clas_e_pretest_no_gain_otherwise(self, pre_level, post_level):
        pretest = Clas_E(read_level=pre_level)
        assert Tabe(read_level=post_level).check_gain(pretest) is False

    def test_clas_e_branch_ignores_nrs_entirely(self):
        """A big NRS jump does not count when the pretest was a CLAS-E."""
        pretest = Clas_E(read_level='2', read_nrs='1')
        post = Tabe(read_level='A', read_nrs='6', math_nrs='6', lang_nrs='6')
        assert post.check_gain(pretest) is False

    @pytest.mark.parametrize('field', ['read_nrs', 'math_nrs', 'lang_nrs'])
    def test_any_single_subject_gain_counts(self, field):
        pretest = Tabe(read_nrs='2', math_nrs='2', lang_nrs='2')
        post = Tabe(read_nrs='2', math_nrs='2', lang_nrs='2')
        setattr(post, field, '3')
        assert post.check_gain(pretest) is True

    def test_no_gain_when_all_equal(self):
        pretest = Tabe(read_nrs='2', math_nrs='2', lang_nrs='2')
        post = Tabe(read_nrs='2', math_nrs='2', lang_nrs='2')
        assert post.check_gain(pretest) is False

    def test_no_gain_when_scores_drop(self):
        pretest = Tabe(read_nrs='4', math_nrs='4', lang_nrs='4')
        post = Tabe(read_nrs='2', math_nrs='2', lang_nrs='2')
        assert post.check_gain(pretest) is False

    def test_none_nrs_is_swallowed_not_raised(self):
        """TypeError from a None comparison is caught and treated as no gain."""
        pretest = Tabe(read_nrs=None, math_nrs=None, lang_nrs=None)
        post = Tabe(read_nrs='3', math_nrs=None, lang_nrs=None)
        assert post.check_gain(pretest) is False

    def test_nrs_comparison_is_lexicographic_not_numeric(self):
        """NRS fields are CharField(max_length=1), so '>' compares strings.

        Characterising current behaviour, not endorsing it. Within 1-6 the
        string and numeric orderings agree, which is why this has never bitten.
        """
        pretest = Tabe(read_nrs='1', math_nrs='1', lang_nrs='1')
        assert Tabe(read_nrs='2', math_nrs='1', lang_nrs='1').check_gain(
            pretest
        ) is True
        # '-' sorts below '1' in ASCII, so a dash never reads as a gain.
        assert Tabe(read_nrs='-', math_nrs='1', lang_nrs='1').check_gain(
            pretest
        ) is False


class TestTabeNrsFormatting:

    def test_nrs_joins_three_subjects(self):
        tabe = Tabe(read_nrs='2', math_nrs='3', lang_nrs='4')
        assert tabe.nrs() == '2 3 4'

    def test_nrs_substitutes_dash_for_missing(self):
        assert Tabe(read_nrs='2').nrs() == '2 - -'
        assert Tabe().nrs() == '- - -'

    def test_nrs_level_format_includes_date(self):
        tabe = Tabe(
            read_nrs='2', read_level='M',
            math_nrs='3', math_level='D',
            lang_nrs='4', lang_level='A',
            test_date=datetime.date(2026, 3, 9),
        )
        assert tabe.nrs_level_format() == '2/M 3/D 4/A 03/09/2026'
