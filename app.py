import streamlit as st
import pandas as pd
from pyathena import connect

st.set_page_config(
    page_title="GlobalPartners Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("GlobalPartners Analytics Dashboard")
st.success("AWS Athena connection configured")

st.write("AWS Medallion Architecture Analytics Project")
st.write("Gold Database: globalpartners_gold_db")

@st.cache_data(ttl=600)
def load_restaurant_data():
    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
        SELECT restaurant_id, total_orders
        FROM globalpartners_gold_db.restaurant_order_summary
        ORDER BY total_orders DESC
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

try:
    restaurant_df = load_restaurant_data()

    st.subheader("Restaurant Performance")

    st.metric(
        "Restaurants Analyzed",
        len(restaurant_df)
    )

    st.dataframe(
        restaurant_df,
        use_container_width=True
    )

    st.subheader("Top 10 Restaurants by Orders")

    top_restaurants = restaurant_df.head(10)

    st.bar_chart(
        top_restaurants.set_index("restaurant_id")["total_orders"]
    )

except Exception as e:
    st.error(f"Unable to load Athena data: {e}")

# ==========================================
# CUSTOMER SEGMENTATION - RFM ANALYSIS
# ==========================================

st.divider()
st.header("Customer Segmentation (RFM Analysis)")

@st.cache_data(ttl=600)
def load_customer_data():
    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
    SELECT
        user_id,
        last_order_date,
        frequency,
        monetary,
        recency,
        r_score,
        f_score,
        m_score,
        rfm_score,
        customer_segment
    FROM globalpartners_gold_db.customer_rfm
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


try:
    customer_df = load_customer_data()

    customer_df["monetary"] = pd.to_numeric(
        customer_df["monetary"], errors="coerce"
    )

    total_customers = customer_df["user_id"].nunique()
    total_value = customer_df["monetary"].sum()
    avg_value = customer_df["monetary"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Total Customer Value", f"${total_value:,.2f}")
    col3.metric("Average Customer Value", f"${avg_value:,.2f}")

    st.subheader("Customers by RFM Segment")

    segment_df = (
        customer_df.groupby("customer_segment")
        .agg(
            total_customers=("user_id", "nunique"),
            total_monetary=("monetary", "sum"),
            avg_monetary=("monetary", "mean")
        )
        .reset_index()
        .sort_values("total_customers", ascending=False)
    )

    st.bar_chart(
        segment_df.set_index("customer_segment")["total_customers"]
    )

    st.subheader("Average Customer Value by Segment")

    st.bar_chart(
        segment_df.set_index("customer_segment")["avg_monetary"]
    )

    st.subheader("Customer Segment Summary")

    st.dataframe(segment_df, width="stretch")

except Exception as e:
    st.error(f"Unable to load customer data: {e}")


# ==========================================
# CHURN RISK INDICATORS DASHBOARD
# ==========================================

st.divider()
st.header("Churn Risk Indicators")

@st.cache_data(ttl=600)
def load_churn_activity():
    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
        SELECT
            user_id,
            order_date,
            daily_revenue,
            daily_orders
        FROM globalpartners_gold_db.daily_customer_clv
    """

    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


try:
    # Reuse the customer data loaded earlier
    churn_df = load_customer_data().copy()

    churn_df["last_order_date"] = pd.to_datetime(
        churn_df["last_order_date"], errors="coerce"
    )

    churn_df["recency"] = pd.to_numeric(
        churn_df["recency"], errors="coerce"
    )

    # Use the latest order date in the dataset as
    # the reference date for historical analysis.
    reference_date = churn_df["last_order_date"].max()

    churn_df["days_since_last_order"] = (
        reference_date - churn_df["last_order_date"]
    ).dt.days

    # Customer inactivity thresholds
    inactivity_threshold = st.slider(
        "Churn Alert Threshold (Days)",
        min_value=15,
        max_value=180,
        value=45,
        step=5
    )

    churn_df["risk_level"] = "Active"

    churn_df.loc[
        churn_df["days_since_last_order"] > inactivity_threshold,
        "risk_level"
    ] = "At Risk"

    churn_df.loc[
        churn_df["days_since_last_order"] > inactivity_threshold * 2,
        "risk_level"
    ] = "High Risk"

    # Customer activity history
    activity_df = load_churn_activity()

    activity_df["order_date"] = pd.to_datetime(
        activity_df["order_date"], errors="coerce"
    )

    activity_df["daily_revenue"] = pd.to_numeric(
        activity_df["daily_revenue"], errors="coerce"
    )

    activity_df["daily_orders"] = pd.to_numeric(
        activity_df["daily_orders"], errors="coerce"
    )

    activity_df = activity_df.dropna(
        subset=["user_id", "order_date"]
    )

    activity_df = activity_df[
        activity_df["daily_orders"] > 0
    ].copy()

    # Calculate average days between order dates
    order_dates = (
        activity_df[["user_id", "order_date"]]
        .drop_duplicates()
        .sort_values(["user_id", "order_date"])
    )

    order_dates["previous_order_date"] = (
        order_dates.groupby("user_id")["order_date"].shift(1)
    )

    order_dates["days_between_orders"] = (
        order_dates["order_date"] -
        order_dates["previous_order_date"]
    ).dt.days

    interval_df = (
        order_dates.groupby("user_id", as_index=False)
        .agg(
            avg_order_interval=(
                "days_between_orders", "mean"
            )
        )
    )

    churn_df = churn_df.merge(
        interval_df, on="user_id", how="left"
    )

    # Compare the latest 30 days of the dataset
    # against the preceding 30 days
    recent_start = reference_date - pd.Timedelta(days=29)
    previous_start = recent_start - pd.Timedelta(days=30)

    activity_df["period"] = "Outside Window"

    activity_df.loc[
        (activity_df["order_date"] >= previous_start) &
        (activity_df["order_date"] < recent_start),
        "period"
    ] = "Previous 30 Days"

    activity_df.loc[
        (activity_df["order_date"] >= recent_start) &
        (activity_df["order_date"] <= reference_date),
        "period"
    ] = "Recent 30 Days"

    spending_df = (
        activity_df[
            activity_df["period"] != "Outside Window"
        ]
        .pivot_table(
            index="user_id",
            columns="period",
            values="daily_revenue",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    for column in ["Previous 30 Days", "Recent 30 Days"]:
        if column not in spending_df.columns:
            spending_df[column] = 0

    spending_df = spending_df.rename(
        columns={
            "Previous 30 Days": "previous_spend",
            "Recent 30 Days": "recent_spend"
        }
    )

    churn_df = churn_df.merge(
        spending_df, on="user_id", how="left"
    )

    churn_df[["previous_spend", "recent_spend"]] = (
        churn_df[["previous_spend", "recent_spend"]]
        .fillna(0)
    )

    churn_df["spend_change_pct"] = (
        (churn_df["recent_spend"] - churn_df["previous_spend"])
        / churn_df["previous_spend"].replace(0, float("nan"))
        * 100
    )

    # Key metrics
    total_customers = churn_df["user_id"].nunique()
    at_risk = (churn_df["risk_level"] == "At Risk").sum()
    high_risk = (churn_df["risk_level"] == "High Risk").sum()

    risk_pct = (
        (at_risk + high_risk) / total_customers * 100
        if total_customers else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("At Risk Customers", f"{at_risk:,}")
    col3.metric("High Risk Customers", f"{high_risk:,}")
    col4.metric("Total Risk Rate", f"{risk_pct:.1f}%")

    st.caption(
        f"Historical analysis reference date: "
        f"{reference_date:%Y-%m-%d}. "
        "Risk categories are rule-based indicators, "
        "not confirmed customer churn."
    )

    # Risk distribution
    st.subheader("Customers by Churn Risk")

    risk_summary = (
        churn_df["risk_level"]
        .value_counts()
        .rename_axis("risk_level")
        .reset_index(name="customers")
    )

    st.bar_chart(
        risk_summary.set_index("risk_level")["customers"]
    )

    # Average order interval
    st.subheader("Average Order Interval by Risk Level")

    interval_summary = (
        churn_df.groupby("risk_level")["avg_order_interval"]
        .mean()
        .dropna()
    )

    st.bar_chart(interval_summary)

    st.caption(
        "Intervals are calculated between distinct "
        "order dates. Multiple orders on the same day "
        "are not individually timed."
    )

    # Spending trends
    st.subheader("Spending Trends by Risk Level")

    spend_summary = (
        churn_df.groupby("risk_level")[
            ["previous_spend", "recent_spend"]
        ].sum()
    )

    st.bar_chart(spend_summary)

    # Customer re-engagement list
    st.subheader("Customers Requiring Re-engagement")

    risk_customers = churn_df[
        churn_df["risk_level"].isin(["At Risk", "High Risk"])
    ].sort_values(
        "days_since_last_order", ascending=False
    )

    st.dataframe(
        risk_customers[
            [
                "user_id",
                "customer_segment",
                "days_since_last_order",
                "avg_order_interval",
                "previous_spend",
                "recent_spend",
                "spend_change_pct",
                "risk_level"
            ]
        ],
        width="stretch"
    )

    if high_risk > 0:
        st.warning(
            f"{high_risk:,} customers are classified "
            "as High Risk and may need re-engagement."
        )

except Exception as e:
    st.error(f"Unable to load churn indicators: {e}")


# ==========================================
# SALES TRENDS AND SEASONALITY DASHBOARD
# ==========================================

st.divider()
st.header("Sales Trends and Seasonality")

@st.cache_data(ttl=600)
def load_sales_data():
    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
    SELECT
        user_id,
        order_date,
        daily_revenue,
        daily_orders,
        is_weekend,
        is_holiday
    FROM globalpartners_gold_db.daily_customer_clv
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


try:
    sales_df = load_sales_data()

    sales_df["order_date"] = pd.to_datetime(
        sales_df["order_date"], errors="coerce"
    )

    sales_df["daily_revenue"] = pd.to_numeric(
        sales_df["daily_revenue"], errors="coerce"
    ).fillna(0)

    sales_df["daily_orders"] = pd.to_numeric(
        sales_df["daily_orders"], errors="coerce"
    ).fillna(0)

    sales_df = sales_df.dropna(subset=["order_date"])

    # KPI Metrics
    total_revenue = sales_df["daily_revenue"].sum()
    total_orders = sales_df["daily_orders"].sum()

    avg_order_value = (
        total_revenue / total_orders
        if total_orders > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,.0f}")
    col3.metric("Average Order Value", f"${avg_order_value:,.2f}")

    # Monthly Sales
    st.subheader("Monthly Revenue Trends")

    monthly_sales = (
        sales_df.set_index("order_date")
        .resample("MS")["daily_revenue"]
        .sum()
    )

    st.line_chart(monthly_sales)

    # Weekly Sales
    st.subheader("Weekly Sales Trends")

    weekly_sales = (
        sales_df.set_index("order_date")
        .resample("W")["daily_revenue"]
        .sum()
    )

    st.line_chart(weekly_sales)

    # Seasonal Revenue
    st.subheader("Seasonal Revenue by Month")

    seasonal_sales = (
        sales_df.groupby(sales_df["order_date"].dt.month)
        ["daily_revenue"]
        .sum()
        .sort_index()
    )

    seasonal_sales.index = [
        pd.Timestamp(2024, month, 1).strftime("%B")
        for month in seasonal_sales.index
    ]

    st.bar_chart(seasonal_sales)

    # Weekend vs Weekday
    st.subheader("Weekend vs Weekday Sales")

    sales_df["day_type"] = (
        sales_df["order_date"]
        .dt.dayofweek
        .apply(lambda x: "Weekend" if x >= 5 else "Weekday")
    )

    day_sales = (
        sales_df.groupby("day_type")["daily_revenue"]
        .sum()
    )

    st.bar_chart(day_sales)

    st.caption(
        "Sales are aggregated from the "
        "daily_customer_clv Gold table."
    )

except Exception as e:
    st.error(f"Unable to load sales trends: {e}")

# ==========================================
# DASHBOARD 4: LOYALTY PROGRAM IMPACT
# ==========================================

st.divider()
st.header("Loyalty Program Impact")

@st.cache_data(ttl=600)
def load_loyalty_data():
    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
        SELECT *
        FROM globalpartners_gold_db.loyalty_impact
    """

    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


try:
    loyalty_df = load_loyalty_data()

    numeric_columns = [
        "total_customers",
        "total_orders",
        "total_revenue",
        "avg_customer_value",
        "avg_order_value",
        "repeat_purchase_rate"
    ]

    for col in numeric_columns:
        loyalty_df[col] = pd.to_numeric(
            loyalty_df[col], errors="coerce"
        )

    st.subheader("Loyalty vs Non-Loyalty Customers")

    st.dataframe(loyalty_df, width="stretch")

    st.subheader("Average Customer Value")

    st.bar_chart(
        loyalty_df.set_index("loyalty_status")[
            "avg_customer_value"
        ]
    )

    st.subheader("Average Order Value")

    st.bar_chart(
        loyalty_df.set_index("loyalty_status")[
            "avg_order_value"
        ]
    )

    st.subheader("Repeat Purchase Rate (%)")

    st.bar_chart(
        loyalty_df.set_index("loyalty_status")[
            "repeat_purchase_rate"
        ]
    )

    st.caption(
        "Loyalty groups are based on observed "
        "loyalty-flagged transactions, not verified "
        "membership enrollment."
    )

except Exception as e:
    st.error(f"Unable to load loyalty data: {e}")


# ==========================================
# DASHBOARD 5: LOCATION PERFORMANCE
# ==========================================

st.divider()
st.header("Location Performance")

st.subheader("Restaurant Rankings by Order Volume")

@st.cache_data(ttl=600)
def load_location_data():

    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
        SELECT
            restaurant_id,
            total_orders,
            order_rank
        FROM globalpartners_gold_db.location_performance
        ORDER BY order_rank, restaurant_id
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


try:
    location_df = load_location_data()

    location_df["total_orders"] = pd.to_numeric(
        location_df["total_orders"],
        errors="coerce"
    )

    st.metric(
        "Restaurants Analyzed",
        location_df["restaurant_id"].nunique()
    )

    st.subheader("Top 10 Restaurants by Orders")

    top_10 = location_df.nlargest(
        10, "total_orders"
    )

    st.bar_chart(
        top_10.set_index("restaurant_id")["total_orders"]
    )

    st.subheader("Bottom 10 Restaurants by Orders")

    bottom_10 = location_df.nsmallest(
        10, "total_orders"
    )

    st.bar_chart(
        bottom_10.set_index("restaurant_id")["total_orders"]
    )

    st.subheader("Restaurant Performance Details")

    st.dataframe(
        location_df,
        width="stretch"
    )

except Exception as e:
    st.error(
        f"Unable to load location performance: {e}"
    )

# ==========================================
# DASHBOARD 5: RESTAURANT REVENUE ANALYSIS
# ==========================================

@st.cache_data(ttl=600)
def load_restaurant_revenue():

    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
        SELECT
            restaurant_id,
            total_orders,
            total_revenue,
            avg_order_value,
            revenue_rank
        FROM globalpartners_gold_db.restaurant_revenue_performance
        ORDER BY revenue_rank, restaurant_id
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


try:
    revenue_df = load_restaurant_revenue()

    for column in [
        "total_orders",
        "total_revenue",
        "avg_order_value"
    ]:
        revenue_df[column] = pd.to_numeric(
            revenue_df[column],
            errors="coerce"
        )

    st.subheader("Restaurant Revenue Performance")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Restaurant Revenue",
        f"${revenue_df['total_revenue'].sum():,.2f}"
    )

    col2.metric(
        "Restaurants Analyzed",
        revenue_df["restaurant_id"].nunique()
    )

    col3.metric(
        "Overall Average Order Value",
        f"${revenue_df['total_revenue'].sum() / revenue_df['total_orders'].sum():,.2f}"
        if revenue_df["total_orders"].sum() > 0 else "N/A"
    )

    st.subheader("Top 10 Restaurants by Revenue")

    top_revenue = revenue_df.nlargest(
        10, "total_revenue"
    )

    st.bar_chart(
        top_revenue.set_index("restaurant_id")["total_revenue"]
    )

    st.subheader("Bottom 10 Restaurants by Revenue")

    bottom_revenue = revenue_df.nsmallest(
        10, "total_revenue"
    )

    st.bar_chart(
        bottom_revenue.set_index("restaurant_id")["total_revenue"]
    )

    st.subheader("Average Order Value by Restaurant")

    top_aov = revenue_df.nlargest(
        10, "avg_order_value"
    )

    st.bar_chart(
        top_aov.set_index("restaurant_id")["avg_order_value"]
    )

    st.subheader("Restaurant Revenue Summary")

    st.dataframe(
        revenue_df,
        width="stretch"
    )

except Exception as e:
    st.error(f"Unable to load restaurant revenue: {e}")

# ==========================================
# DASHBOARD 6: PRICING EFFECTIVENESS
# ==========================================

st.divider()
st.header("Pricing and Discount Effectiveness")
st.caption(
    "Pricing analysis based on recorded item prices. "
    "Discount effectiveness requires discount data."
)

@st.cache_data(ttl=600)
def load_pricing_data():

    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    query = """
        SELECT
            restaurant_id,
            total_orders,
            total_revenue,
            avg_order_value,
            avg_item_price,
            total_items_sold
        FROM globalpartners_gold_db.pricing_performance
    """

    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


try:
    pricing_df = load_pricing_data()

    numeric_cols = [
        "total_orders",
        "total_revenue",
        "avg_order_value",
        "avg_item_price",
        "total_items_sold"
    ]

    for col in numeric_cols:
        pricing_df[col] = pd.to_numeric(
            pricing_df[col],
            errors="coerce"
        )

    # Key metrics
    st.subheader("Pricing Performance Overview")

    col1, col2, col3 = st.columns(3)

    total_revenue = pricing_df["total_revenue"].sum()
    total_orders = pricing_df["total_orders"].sum()
    total_items = pricing_df["total_items_sold"].sum()

    col1.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}"
    )

    col2.metric(
        "Average Order Value",
        f"${total_revenue / total_orders:,.2f}"
        if total_orders > 0 else "N/A"
    )

    col3.metric(
        "Average Item Price",
        f"${total_revenue / total_items:,.2f}"
        if total_items > 0 else "N/A"
    )

    # Revenue by restaurant
    st.subheader("Top 10 Restaurants by Revenue")

    top_revenue = pricing_df.nlargest(
        10, "total_revenue"
    )

    st.bar_chart(
        top_revenue.set_index("restaurant_id")["total_revenue"]
    )

    # Average order value
    st.subheader("Average Order Value by Restaurant")

    top_aov = pricing_df.nlargest(
        10, "avg_order_value"
    )

    st.bar_chart(
        top_aov.set_index("restaurant_id")["avg_order_value"]
    )

    # Average item price
    st.subheader("Average Item Price by Restaurant")

    top_prices = pricing_df.nlargest(
        10, "avg_item_price"
    )

    st.bar_chart(
        top_prices.set_index("restaurant_id")["avg_item_price"]
    )

    # Detailed table
    st.subheader("Restaurant Pricing Details")

    st.dataframe(
        pricing_df.sort_values(
            "total_revenue",
            ascending=False
        ),
        width="stretch"
    )

except Exception as e:
    st.error(f"Unable to load pricing data: {e}")
