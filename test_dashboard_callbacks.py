import unittest

import app  # noqa: F401 - ensures Dash app exists before page imports

from pages.cohorts import update_cohorts
from pages.forecasting import _update_forecast
from pages.overview import DATE_MAX as OVERVIEW_MAX
from pages.overview import DATE_MIN as OVERVIEW_MIN
from pages.overview import update_overview
from pages.payments import DATE_MAX as PAYMENTS_MAX
from pages.payments import DATE_MIN as PAYMENTS_MIN
from pages.payments import update_payments
from pages.reviews import CATEGORIES
from pages.reviews import DATE_MAX as REVIEWS_MAX
from pages.reviews import DATE_MIN as REVIEWS_MIN
from pages.reviews import update_reviews
from pages.sellers import DATE_MAX as SELLERS_MAX
from pages.sellers import DATE_MIN as SELLERS_MIN
from pages.sellers import update_sellers
from utils.gemini_analyst import generate_executive_summary
from utils.retention import build_retention_matrix


class DashboardCallbackTests(unittest.TestCase):
    def test_overview_callback_returns_context(self):
        outputs = update_overview(str(OVERVIEW_MIN), str(OVERVIEW_MAX), [])
        self.assertEqual(len(outputs), 12)
        context = outputs[-1]
        self.assertEqual(context["page"], "overview")
        self.assertIn("total_revenue", context["headline_metrics"])

    def test_reviews_boxplot_respects_selected_category(self):
        category = CATEGORIES[1]
        _, _, fig_box, _, context = update_reviews(
            category, str(REVIEWS_MIN), str(REVIEWS_MAX), []
        )
        trace_names = {trace.name for trace in fig_box.data}

        self.assertEqual(trace_names, {category})
        self.assertEqual(context["filters"]["category"], category)

    def test_payments_callback_uses_context_output(self):
        outputs = update_payments(str(PAYMENTS_MIN), str(PAYMENTS_MAX), [])
        self.assertEqual(len(outputs), 10)
        fig_types = outputs[5]
        context = outputs[-1]

        self.assertGreater(len(fig_types.data), 0)
        self.assertEqual(context["page"], "payments")

    def test_sellers_callback_returns_professional_payload(self):
        outputs = update_sellers(str(SELLERS_MIN), str(SELLERS_MAX), [])
        self.assertEqual(len(outputs), 10)
        context = outputs[-1]
        self.assertEqual(context["page"], "sellers")

    def test_cohorts_callback_returns_context(self):
        outputs = update_cohorts(str(OVERVIEW_MIN), str(OVERVIEW_MAX), [])
        self.assertEqual(len(outputs), 8)
        context = outputs[-1]
        self.assertEqual(context["page"], "cohorts")
        self.assertIn("repeat_rate", context["headline_metrics"])

    def test_forecasting_callback_returns_backtest_context(self):
        outputs = _update_forecast(30)
        self.assertEqual(len(outputs), 10)
        context = outputs[-1]
        self.assertEqual(context["page"], "forecasting")
        self.assertEqual(context["filters"]["horizon_days"], 30)

    def test_executive_summary_includes_page_name(self):
        summary = generate_executive_summary(
            "Total Revenue: R$100 | Orders: 5",
            {
                "page": "cohorts",
                "filters": {"start_date": "2017-01-01", "end_date": "2018-08-30"},
                "headline_metrics": {"repeat_rate": "34.5%"},
            },
        )
        self.assertIn("cohorts", summary.lower())
        self.assertIn("repeat", summary.lower())

    def test_retention_matrix_starts_at_full_retention(self):
        pct_matrix, count_matrix = build_retention_matrix(app._data_bundle["orders"])
        self.assertFalse(pct_matrix.empty)
        self.assertIn(0, pct_matrix.columns)
        self.assertTrue((pct_matrix[0] == 100).all())
        self.assertTrue((count_matrix[0] > 0).all())


if __name__ == "__main__":
    unittest.main()
