from board import Board
import pandas as pd
from shimoku_components_catalog.html_components import beautiful_indicator
import locale
from utils import (
    super_admin_title,
    filter_data_by_week,
    process_revenue_by_day,
    get_last_month_data,
    get_current_month_data,
)
from datetime import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class EcommerceAnalysis(Board):
    """
    This path is responsible for rendering the Ecommerce Analysis path.
    """

    def __init__(self, self_board: Board):
        """
        Initializes the HiddenIndicatorsPage with a shimoku client instance.

        Parameters:
            shimoku: An instance of the Shimoku client.
        """
        super().__init__(self_board.shimoku)

        self.order = 0  # Initialize order of plotting elements
        self.menu_path = "Sales and users"  # Set the menu path for this page

        # Delete existing menu path if it exists
        if self.shimoku.menu_paths.get_menu_path(name=self.menu_path):
            self.shimoku.menu_paths.delete_menu_path(name=self.menu_path)

        self.shimoku.set_menu_path(name=self.menu_path)  # Set the menu path in Shimoku

    def plot(self):
        """
        Plots the user overview page.
        Each method is responsible for plotting a specific section of the page.
        """

        df = pd.read_csv("data/data.csv")

        df["Purchase_Date"] = pd.to_datetime(df["Purchase_Date"], format="%Y-%m-%d")
        df["Month"] = df["Purchase_Date"].dt.month
        df["month_year"] = df["Purchase_Date"].dt.strftime("%Y-%m")
        try:
            price_has_comma = df["Price"].str.contains(",", regex=False).any()
            cost_has_comma = df["Cost"].str.contains(",", regex=False).any()
        except AttributeError:
            price_has_comma, cost_has_comma = False, False
            pass
        if price_has_comma or cost_has_comma:
            df["Price"] = df["Price"].str.replace(",", ".", regex=True).astype(float)
            df["Cost"] = df["Cost"].str.replace(",", ".", regex=True).astype(float)
        else:
            df["Price"] = df["Price"].astype(float)
            df["Cost"] = df["Cost"].astype(float)

        self.df = df

        self.plot_header()
        self.plot_indicators()
        self.plot_sales_by_weekday()
        self.plot_bar_chart_prods()
        self.plot_table_users()
        self.plot_pie_chart()
        self.plot_stacked_bar()

    def plot_header(self):
        indicator = beautiful_indicator(
            title="Analysis of sales and ecommerce users",
            href="https://shimoku.io/9698715a-a9d3-4253-851e-30640dce743e/drag-and-drop",
            background_url="https://images.unsplash.com/photo-1516414447565-b14be0adf13e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1973&q=80",
        )
        self.shimoku.plt.html(
            indicator,
            order=self.order,
            rows_size=3,
            cols_size=12,
        )
        self.order += 1
        return True

    def plot_indicators(self):
        df_copy = self.df.copy()

        last_month, gross_sales_last_month, revenue_last_month = get_last_month_data(df_copy)
        current_month, gross_sales_current_month = get_current_month_data(df_copy)

        data = [
            {
                "description": f"{last_month}",
                "title": "Gross sales last month",
                "value": f"€ {gross_sales_last_month}",
                "color": "default",
                "align": "center",
            },
            {
                "description": f"{last_month}",
                "title": "Net sales last month",
                "value": f"€ {revenue_last_month}",
                "color": "default",
                "align": "center",
            },
            {
                "description": f"{current_month}" if current_month else "N/A",
                "title": "Gross sales current month",
                "value": f"€ {gross_sales_current_month}",
                "color": "default",
                "align": "center",
            },
        ]

        self.shimoku.plt.indicator(
            data=data,
            order=self.order,
            rows_size=1,
            cols_size=12,
            value="value",
            header="title",
            footer="description",
            color="color",
        )
        self.order += len(data)

        return True

    def plot_sales_by_weekday(self):
        # Generate super admin title
        self.shimoku.plt.html(
            html=super_admin_title(title="Accumulated daily revenue"),
            order=self.order,
        )
        self.order += 1

        df_copy = self.df.copy()
        current_date = pd.Timestamp(datetime.now().date())
        df_last_week = filter_data_by_week(df_copy, current_date)
        revenue_by_day_last_week = process_revenue_by_day(df_last_week)
        start_of_week = current_date - pd.DateOffset(days=current_date.dayofweek)
        end_of_week = start_of_week + pd.DateOffset(days=6)

        df_this_week_data = df_copy[
            (df_copy["Purchase_Date"] >= start_of_week)
            & (df_copy["Purchase_Date"] <= end_of_week)
        ]

        revenue_by_day_this_week = process_revenue_by_day(
            df_this_week_data, current_week=True
        )
        revenue_by_day = pd.merge(
            revenue_by_day_last_week,
            revenue_by_day_this_week,
            on="Days of the week",
            how="outer",
        )
        dict_revenue_by_day = revenue_by_day.to_dict(orient="records")

        self.shimoku.plt.line(
            data=dict_revenue_by_day,
            x="Days of the week",
            y=["Last week", "Current week"],
            order=self.order,
            rows_size=3,
            cols_size=12,
        )
        self.order += 1

        return True

    def plot_bar_chart_prods(self):
        df = self.df.copy()
        # get 5 most sold products from last month
        month_year_data = df["month_year"]
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        one_month_before = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m")

        df_last_month = df[month_year_data == one_month_before]
        grouped_df = (
            df_last_month.groupby("Product")
            .agg({"Price": "sum", "Purchase_Date": "count"})
            .sort_values(by="Price", ascending=False)
            .reset_index()
        )
        grouped_df.columns = ["Product", "Total(€)", "Units"]
        grouped_df["Total(€)"] = round(grouped_df["Total(€)"])
        first_five_products = grouped_df.loc[:4]
        first_five_products.sort_values(by="Total(€)", inplace=True)
        
        self.shimoku.plt.html(
            html=super_admin_title(
                title=f"Top 5 best-selling products and most frequent customers of the previous month ({one_month_before})",
            ),
            order=self.order,
        )
        self.order += 1

        self.shimoku.plt.horizontal_bar(
            data=first_five_products,
            x="Product",
            y=["Total(€)"],
            order=self.order,
            rows_size=3,
            cols_size=6,
        )

        self.order += 1
        return True

    def plot_table_users(self):
        df = self.df.copy()
        month_year_data = df["month_year"]
        one_month_before = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m")

        df_last_month = df[month_year_data == one_month_before]
        grouped_df = (
            df_last_month.groupby(["ClientID"])
            .agg({"Email": "first", "Price": "sum", "Product": "count"})
            .sort_values(by="Price", ascending=False)
            .reset_index()
        )
        grouped_df.drop(columns=["ClientID"], inplace=True)
        grouped_df.columns = ["Email", "Total(€)", "Units"]
        grouped_df["Total(€)"] = round(grouped_df["Total(€)"])
        first_five_clients = grouped_df.loc[:4]

        self.shimoku.plt.table(
            data=first_five_clients,
            order=self.order,
            cols_size=5,
            rows_size=3,
            sort_descending=True,
            initial_sort_column="Total(€)",
            columns_options={"Email": {"width": 270}},
        )

        self.order += 1
        return True

    def plot_pie_chart(self):
        self.shimoku.plt.html(
            html=super_admin_title(
                title="Active users in total and in the last semester"
            ),
            order=self.order,
        )
        self.order += 1

        self.order += 1
        df = self.df.copy()
        # Count the occurrences of each gender
        df["Gender"] = df["Gender"].replace("na", "NA")
        gender_counts = df["Gender"].value_counts()
        gender_df = pd.DataFrame(gender_counts.reset_index())
        gender_df.columns = ["Gender", "Count"]
        self.shimoku.plt.doughnut(
            data=gender_df,
            names="Gender",
            values="Count",
            order=self.order,
            rows_size=3,
            cols_size=6,
            padding="0, 0, 0, 0",
        )
        self.order += 1
        return True

    def plot_stacked_bar(self):
        list_for_dict = list()
        for n_month in range(1, 7):
            month_year_data = self.df["month_year"]
            from datetime import datetime
            from dateutil.relativedelta import relativedelta

            # Assuming n_month is already defined as an integer representing the number of months
            n_month_before = (datetime.now() - relativedelta(months=n_month)).strftime(
                "%Y-%m"
            )

            df_mask = self.df[month_year_data == n_month_before]
            new_dict = dict()
            new_dict["Man"] = (df_mask["Gender"] == "Male").sum()
            new_dict["Woman"] = (df_mask["Gender"] == "Female").sum()
            new_dict["NA"] = (df_mask["Gender"] == "na").sum()
            new_dict["Total"] = len(df_mask["ClientID"])
            new_dict["Month"] = n_month_before
            list_for_dict.append(new_dict)

        df_active_users = pd.DataFrame(list_for_dict)
        df_active_users.sort_values("Month", inplace=True)

        self.shimoku.plt.stacked_bar(
            data=df_active_users,
            x="Month",
            y=["Total", "Man", "Woman", "NA"],
            cols_size=5,
            order=self.order,
        )

        self.order += 1
        return True