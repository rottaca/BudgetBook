from typing import List
import numpy as np
import pandas as pd
import Levenshtein
from sklearn.cluster import dbscan
from sklearn.neighbors import LocalOutlierFactor
from BudgetBook.category_parser import CategoryParser

from BudgetBook.config_parser import ConfigParser, DataColumns
from BudgetBook.dated_transaction import DatedTransaction
from BudgetBook.regular_event import RegularEvent
from BudgetBook.regular_transaction import RegularTransaction
from BudgetBook.transaction_interval import TransactionInterval


class RegularTransactionPredictor:
    def __init__(self, config: ConfigParser) -> None:
        self._config = config
        self._category_parser = CategoryParser(self._config)

    def to_regular_transactions(self, dated_transactions_list: List[DatedTransaction]):

        dataset = pd.DataFrame.from_records(
            [d.to_dict() for d in dated_transactions_list]
        )

        payment_partys = dataset[DataColumns.PAYMENT_PARTY].unique()
        same_party_label = RegularTransactionPredictor.group_by_similarity(
            payment_partys, eps=3
        )

        grouped_payment_parties = [
            payment_partys[same_party_label == l].tolist()
            for l in np.unique(same_party_label)
            if l >= 0
        ]
        grouped_payment_parties.extend(
            [p] for p in payment_partys[same_party_label == -1]
        )

        potentially_regular_transactions = []
        irregular_transactions = []

        for curr_payment_partys in grouped_payment_parties:
            df_same_group = dataset[
                dataset[DataColumns.PAYMENT_PARTY].isin(curr_payment_partys)
            ]

            desc = df_same_group[DataColumns.DESCRIPTION]
            avg_desc_length = max(desc.apply(len).mean(), 10)

            labels = RegularTransactionPredictor.group_by_similarity(
                [d[:150] for d in desc], eps=0.1 * avg_desc_length
            )

            for l in pd.Series(labels).unique():
                data_per_group = df_same_group[labels == l]

                if l == -1:
                    irregular_transactions.extend(
                        d for _, d in data_per_group.iterrows()
                    )
                else:
                    potentially_regular_transactions.append(data_per_group)

        transactions = []
        for transaction_group in potentially_regular_transactions:

            transaction_group = transaction_group.sort_values(DataColumns.DATE)

            dates = transaction_group[DataColumns.DATE]
            amounts = transaction_group[DataColumns.AMOUNT]

            transaction_intervals = dates.diff()

            # identify outliers in the dataset
            lof = LocalOutlierFactor(n_neighbors=min(5, len(transaction_intervals)))
            yhat = lof.fit_predict(transaction_intervals.values.reshape(-1, 1))
            # select all rows that are not outliers
            filter_mask = yhat != -1

            filtered_interval_std = transaction_intervals[filter_mask].std()
            transaction_interval_median = transaction_intervals[filter_mask].median()

            amount_difference = amounts.diff()
            amount_standard_deviation = amount_difference.std()
            amount_difference_median = amounts.median()

            if (
                filtered_interval_std > pd.Timedelta(value=4, unit="days")
                or transaction_interval_median.days == 0
            ):
                continue
            else:
                if transaction_interval_median.days < 25:
                    interval = TransactionInterval(
                        days=transaction_interval_median.days
                    )
                else:
                    interval = TransactionInterval(
                        months=round(transaction_interval_median.days / 30)
                    )

                freqency = RegularEvent(
                    transaction_group[DataColumns.DATE].min(), interval
                )
                desc = ""
                desc += (
                    f"Stddev of interval is +/- {filtered_interval_std.days} days.\n"
                )
                desc += f"Based on {len(transaction_group)} samples with {sum(~filter_mask)} outliers.\n"
                desc += "Last transaction description:\n"
                desc += transaction_group[DataColumns.DESCRIPTION].iloc[-1][:100]
                desc += "[...]"
                transactions.append(
                    RegularTransaction(
                        transaction_group[DataColumns.PAYMENT_PARTY].iloc[0],
                        freqency,
                        amount_difference_median,
                        desc,
                        self._category_parser.get_category_for_record(
                            transaction_group.iloc[0]
                        ),
                    )
                )
        return transactions

    @staticmethod
    def gen_lev_distance_for(series: pd.Series):
        def lev_metric(x, y):
            i, j = int(x[0]), int(y[0])  # extract indices
            if isinstance(series, pd.Series):
                return Levenshtein.distance(series.iloc[i], series.iloc[j])
            else:
                return Levenshtein.distance(series[i], series[j])

        return lev_metric

    @staticmethod
    def group_by_similarity(data_series, eps):
        X = np.arange(len(data_series)).reshape(-1, 1)
        _, labels = dbscan(
            X,
            metric=RegularTransactionPredictor.gen_lev_distance_for(data_series),
            eps=eps,
            min_samples=3,
        )

        return labels
