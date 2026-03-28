import unittest
from pathlib import Path

import pandas as pd

from utils.cleaner import filter_by_date
from utils.data_loader import load_data_bundle
from utils.ml_forecasting import build_time_series, forecast_revenue
from utils.ml_segmentation import compute_rfm


class DataIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_data_bundle()
        cls.orders = cls.bundle["orders"]
        cls.order_items = cls.bundle["order_items"]
        cls.payments = cls.bundle["payments"]
        cls.project_root = Path(__file__).resolve().parents[1]

    def test_filter_by_date_includes_full_end_day(self):
        start = str(self.orders["order_purchase_timestamp"].min().date())
        end = str(self.orders["order_purchase_timestamp"].max().date())

        filtered = filter_by_date(self.orders, start, end)
        expected = self.orders[
            (self.orders["order_purchase_timestamp"] >= pd.Timestamp(start))
            & (
                self.orders["order_purchase_timestamp"]
                < pd.Timestamp(end) + pd.Timedelta(days=1)
            )
        ]

        self.assertEqual(len(filtered), len(expected))
        self.assertEqual(filtered["order_id"].nunique(), expected["order_id"].nunique())

    def test_order_items_preserve_multi_product_orders(self):
        raw_items = pd.read_csv(self.project_root / "data" / "olist_order_items_dataset.csv")
        raw_multi_product = raw_items.groupby("order_id")["product_id"].nunique()
        sample_order_id = raw_multi_product[raw_multi_product > 1].index[0]

        raw_count = int(raw_multi_product.loc[sample_order_id])
        bundle_count = int(
            self.order_items.loc[
                self.order_items["order_id"] == sample_order_id, "product_id"
            ].nunique()
        )

        self.assertEqual(bundle_count, raw_count)

    def test_payment_distribution_matches_raw_payment_rows(self):
        raw_payments = pd.read_csv(
            self.project_root / "data" / "olist_order_payments_dataset.csv"
        )
        raw_payments = raw_payments[raw_payments["order_id"].isin(self.orders["order_id"])]

        expected = (
            raw_payments.groupby("payment_type")["payment_value"].sum().sort_index()
        )
        actual = self.payments.groupby("payment_type")["payment_value"].sum().sort_index()

        pd.testing.assert_series_equal(
            actual,
            expected,
            check_names=False,
            check_exact=False,
            rtol=1e-9,
            atol=1e-9,
        )

    def test_segmentation_excludes_non_delivered_only_customers(self):
        rfm = compute_rfm(self.orders)
        delivered_customers = set(
            self.orders.loc[
                self.orders["order_status"] == "delivered", "customer_unique_id"
            ].dropna()
        )

        self.assertTrue(set(rfm["customer_unique_id"]).issubset(delivered_customers))

    def test_forecast_returns_holdout_metrics(self):
        ts = build_time_series(self.orders)
        _, _, metrics, _ = forecast_revenue(ts, horizon_days=30)

        self.assertGreater(metrics["backtest_days"], 0)
        self.assertTrue(pd.notna(metrics["r2_score"]))
        self.assertTrue(pd.notna(metrics["mape"]))


if __name__ == "__main__":
    unittest.main()
