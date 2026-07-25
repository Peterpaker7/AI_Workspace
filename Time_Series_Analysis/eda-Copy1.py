import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class EDA:

    @staticmethod
    def separate_columns(df):
        """
        Returns numerical and categorical columns.
        """
        numerical = df.select_dtypes(include=np.number).columns.tolist()
        categorical = df.select_dtypes(exclude=np.number).columns.tolist()
        return numerical, categorical

    @staticmethod
    def descriptive_analysis(df):
        """
        Returns descriptive statistics as a single DataFrame.
        """
        numerical, categorical = EDA.separate_columns(df)
        num_desc = df[numerical].describe().T
        if len(categorical) > 0:
            cat_desc = df[categorical].describe().T
        else:
            cat_desc = pd.DataFrame()
        desc = pd.concat([num_desc, cat_desc], axis=0)
        return desc

    @staticmethod
    def outlier_columns(df):
        """
        Returns columns containing outliers.
        """
        numerical, _ = EDA.separate_columns(df)

        cols = []

        for col in numerical:

            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            if ((df[col] < lower) | (df[col] > upper)).any():
                cols.append(col)

        return cols

    @staticmethod
    def outlier_summary(df):

        numerical, _ = EDA.separate_columns(df)

        result = []

        for col in numerical:

            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            count = ((df[col] < lower) | (df[col] > upper)).sum()

            result.append({
                "Column": col,
                "Outlier Count": count
            })

        return pd.DataFrame(result)

    @staticmethod
    def replace_outliers(df):
        """
        Caps outliers using IQR.
        """
        df = df.copy()

        numerical, _ = EDA.separate_columns(df)

        for col in numerical:

            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            df[col] = np.where(df[col] < lower, lower, df[col])
            df[col] = np.where(df[col] > upper, upper, df[col])

        return df

        
    @staticmethod
    def probability_distribution(df, columns=None, bins=30, figsize=(8, 5)):
        
        """
        Plot Probability Distribution for numerical columns.

        Parameters
        ----------
        df : pandas.DataFrame
            Input dataframe.

        columns : list, default=None
            List of numerical columns to visualize.
            If None, all numerical columns are used.

        bins : int, default=30
            Number of histogram bins.

        figsize : tuple, default=(8,5)
            Figure size.

        Returns
        -------
        pandas.DataFrame
            Summary statistics of plotted columns.
        """

        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()

        summary = []

        for col in columns:

            plt.figure(figsize=figsize)

            sns.histplot(
                data=df,
                x=col,
                bins=bins,
                kde=True,
                stat="probability",
                color="skyblue",
                edgecolor="black"
            )

            mean = df[col].mean()
            median = df[col].median()
            std = df[col].std()
            skew = df[col].skew()
            kurt = df[col].kurt()

            plt.axvline(mean, color='red', linestyle='--',
                        linewidth=2, label=f"Mean = {mean:.2f}")

            plt.axvline(median, color='green', linestyle='-',
                        linewidth=2, label=f"Median = {median:.2f}")

            plt.title(f"Probability Distribution - {col}")
            plt.xlabel(col)
            plt.ylabel("Probability")
            plt.legend()
            plt.tight_layout()
            plt.show()

            summary.append({
                "Column": col,
                "Mean": round(mean, 3),
                "Median": round(median, 3),
                "Std": round(std, 3),
                "Skewness": round(skew, 3),
                "Kurtosis": round(kurt, 3)
            })

        return pd.DataFrame(summary)