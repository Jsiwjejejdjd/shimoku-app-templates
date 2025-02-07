import shimoku_api_python
from board import Board
from utils.components import create_title_name_head
from utils.utils import get_status, get_column_name_by_value
import pandas as pd


class CustomerSatisfactionPerformance(Board):
    """
    This class represents a Customer Satisfaction Performance dashboard.
    It inherits from the Board class.
    """

    def __init__(self, self_board: Board):
        """
        Initializes the CustomerSatisfactionPerformance instance.

        Args:
            self_board (Board): An instance of the Board class.
        """
        super().__init__(self_board.shimoku)
        self.df_app = self_board.results
        self.order = 0  # Initialize order of plotting elements
        self.menu_path = "Customer Satisfaction Performance"

        if self.shimoku.menu_paths.get_menu_path(name=self.menu_path):
            self.shimoku.menu_paths.delete_menu_path(name=self.menu_path)

        self.shimoku.set_menu_path(name=self.menu_path)

    def plot(self):
        """
        Plots the Customer Satisfaction Performance dashboard.
        Each method is responsible for plotting a specific section of the page.
        """
        self.plot_header()
        self.plot_kpi_indicators()
        self.plot_customer_satisfaction()
        self.plot_orders_satisfaction()
        self.plot_revenue_indicators()
        self.plot_orders_returned_orders()
        self.plot_revenue_analysis()

    def plot_header(self):
        """
        Plot the header section of the dashboard.

        Returns: True if the operation is successful.
        """
        self.shimoku.plt.html(
            html=create_title_name_head(
                title="Customer Satisfaction Performance",
                subtitle="",
            ),
            order=self.order,
        )

        # Increment the order
        self.order += 1
        return True

    def plot_kpi_indicators(self):
        """
        Plot the Key Performance Indicators (KPI) section of the dashboard.

        Returns:
            bool: True if the operation is successful.
        """
        # Extract KPI data from the DataFrame
        total_customers = self.df_app["Total Customers"]
        customers_with_returns = self.df_app["Customers with Returns"]
        total_orders = self.df_app["Total Orders"]
        orders_with_returns = self.df_app["Orders with Returns"]

        # Determine the status of customers and orders with returns
        customers_with_returns_status = get_status(customers_with_returns)
        orders_with_returns_status = get_status(orders_with_returns)

        # Prepare data for KPI indicators
        indicator_data = [
            {
                "title": "Customers",
                "align": "center",
                "value": f"{round(total_customers, 0)}",
                "color": "default",
            },
            {
                "title": "Orders",
                "align": "center",
                "value": f"{round(total_orders, 0)}",
                "color": "default",
            },
        ]

        # Plot the first KPI indicator for Customers
        self.shimoku.plt.indicator(
            cols_size=3, data=indicator_data[0], order=self.order, color="color"
        )

        # Increment the order
        self.order += 1

        # Plot the Shimoku gauge for Customers with Returns
        self.shimoku.plt.shimoku_gauge(
            cols_size=3,
            value=customers_with_returns,
            order=self.order,
            rows_size=1,
            name="Customer with Returns",
            is_percentage=True,
            color=customers_with_returns_status,
        )

        # Increment the order
        self.order += 1

        # Plot the KPI indicator for Orders
        self.shimoku.plt.indicator(
            cols_size=3,
            data=indicator_data[1],
            order=self.order,
            color="color",
        )

        # Increment the order
        self.order += 1

        # Plot the Shimoku gauge for Orders with Returns
        self.shimoku.plt.shimoku_gauge(
            cols_size=3,
            value=orders_with_returns,
            order=self.order,
            rows_size=1,
            name="Orders with Returns",
            is_percentage=True,
            color=orders_with_returns_status,
        )

        # Increment the order
        self.order += 1

        return True

    def plot_customer_satisfaction(self):
        """
        Plot the Customer Satisfaction section of the dashboard.

        Returns:
            bool: True if the operation is successful.
        """
        # Extract customer satisfaction data from the Dict
        customer_satisfaction = self.df_app["Customer Satisfaction"]

        # Convert customer satisfaction data to a DataFrame for plotting
        customer_satisfaction = pd.DataFrame(
            list(customer_satisfaction.items()), columns=["status", "value"]
        )

        # Plot a rose chart to visualize customer satisfaction
        self.shimoku.plt.rose(
            data=customer_satisfaction,
            values="value",
            names="status",
            order=self.order,
            rows_size=3,
            cols_size=4,
            title="Customer Satisfaction",
        )

        # Increment the order
        self.order += 1

        return True

    def plot_orders_satisfaction(self):
        """
        Plot the Orders Satisfaction section of the dashboard.

        Returns: True if the operation is successful.
        """

        # Extract the "Order Satisfaction" data from the Dict
        orders_satisfaction = self.df_app["Order Satisfaction"]

        # Create a new DataFrame with two columns: "date" and "Rate"
        orders_satisfaction = pd.DataFrame(
            list(orders_satisfaction.items()), columns=["date", "Rate"]
        )

        # Plot a segmented line chart to visualize orders satisfaction
        self.shimoku.plt.segmented_line(
            data=orders_satisfaction,
            order=self.order,
            cols_size=8,
            rows_size=3,
            x="date",
            y="Rate",
            title="Orders Satisfaction",
            marking_lines=[
                0,
                1,
                2,
                3,
                4,
                5,
            ],
            range_colors=[
                "green",
                "yellow",
                "orange",
                "red",
                "purple",
                "maroon",
            ],
            x_axis_name="Date",
            y_axis_name="Rate",
        )

        # Increment the order
        self.order += 1

        return True

    def plot_revenue_indicators(self):
        """
        Plot the Revenue Indicators section of the dashboard.

        Returns: True if the operation is successful.
        """

        # Extract relevant data columns from the Dict
        total_revenue = self.df_app["Total Revenue"]
        revenue_lost = self.df_app["Revenue Lost"]
        real_revenue = self.df_app["Real Revenue"]

        # Create a list of dictionaries to represent the indicator data
        indicator_data = [
            {
                "title": "Revenue",
                "align": "center",
                "value": f"{round(total_revenue, 0)}€",
                "color": "default",
            },
            {
                "title": get_column_name_by_value(self.df_app, revenue_lost),
                "align": "center",
                "value": f"-{round(revenue_lost, 0)}€",
                "color": "error",
            },
            {
                "title": get_column_name_by_value(self.df_app, real_revenue),
                "align": "center",
                "value": f"{round(real_revenue, 0)}€",
                "color": "success",
            },
        ]

        # Plot the indicator data
        self.shimoku.plt.indicator(
            cols_size=6, data=indicator_data, order=self.order, color="color"
        )

        # Increment the order
        self.order += len(indicator_data)

        return True

    def plot_orders_returned_orders(self):
        """
        Plot the Orders & Returned Orders section of the dashboard.

        Returns: True if the operation is successful.
        """

        # Extract the "Monthly Metrics" data from the Dict
        monthly_metrics = self.df_app["Monthly Metrics"]

        # Create a new DataFrame from the extracted data
        monthly_metrics_df = pd.DataFrame(monthly_metrics)

        # Reset the index of the DataFrame and rename the columns for clarity
        monthly_metrics_df.reset_index(inplace=True)
        monthly_metrics_df.rename(columns={"index": "Month"}, inplace=True)
        monthly_metrics_df.rename(
            columns={
                "Monthly Orders": "Orders",
                "Monthly Orders with Returns": "Returned Orders",
            },
            inplace=True,
        )

        # Plot a line chart for "Orders" and "Returned Orders" over time
        self.shimoku.plt.line(
            title="Orders & Returned Orders",
            data=monthly_metrics_df[["Orders", "Returned Orders", "Month"]],
            order=self.order,
            x="Month",
            rows_size=4,
            cols_size=6,
        )

        # Increment the order
        self.order += 1

        return True

    def plot_revenue_analysis(self):
        """
        Plot the Revenue Analysis section of the dashboard.

        Returns: True if the operation is successful.
        """

        # Extract the "Monthly Metrics" data from the Dict
        monthly_metrics = self.df_app["Monthly Metrics"]

        # Create a new DataFrame from the extracted data
        monthly_metrics_df = pd.DataFrame(monthly_metrics)

        # Reset the index of the DataFrame and rename the columns for clarity
        monthly_metrics_df.reset_index(inplace=True)
        monthly_metrics_df.rename(columns={"index": "Month"}, inplace=True)

        # Round the "Monthly Real Revenue" and "Monthly Revenue Lost" columns to integers
        monthly_metrics_df["Monthly Real Revenue"] = monthly_metrics_df[
            "Monthly Real Revenue"
        ].round(0)
        monthly_metrics_df["Monthly Revenue Lost"] = monthly_metrics_df[
            "Monthly Revenue Lost"
        ].round(0)

        # Rename the columns for consistency in the plot
        monthly_metrics_df.rename(
            columns={
                "Monthly Real Revenue": "Real Revenue",
                "Monthly Revenue Lost": "Revenue Lost",
            },
            inplace=True,
        )

        # Plot a stacked bar chart for "Real Revenue" and "Revenue Lost" over time
        self.shimoku.plt.stacked_bar(
            cols_size=6,
            rows_size=3,
            data=monthly_metrics_df[["Real Revenue", "Revenue Lost", "Month"]],
            x="Month",
            order=self.order,
            show_values=["Real Revenue"],
            title="Revenue Analysis",
        )

        # Increment the order
        self.order += 1

        return True
