import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Volopay Customer 360 Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

crm = pd.read_csv("crm.csv")
support = pd.read_csv("support.csv")
emails = pd.read_csv("emails.csv")
usage = pd.read_csv("product_usage.csv")
slack = pd.read_csv("slack.csv")

# ---------------------------------------------------
# MERGE DATA
# ---------------------------------------------------

df = crm.merge(support, on="CustomerID")
df = df.merge(emails, on="CustomerID")
df = df.merge(usage, on="CustomerID")
df = df.merge(slack, on="CustomerID")

# ---------------------------------------------------
# HEALTH SCORE
# ---------------------------------------------------

def calculate_health(row):

    score = 100

    if row["OpenTickets"] == 1:
        score -= 15

    elif row["OpenTickets"] >= 2:
        score -= 35

    if row["ResponseStatus"] == "Negative":
        score -= 20

    elif row["ResponseStatus"] == "Waiting":
        score -= 10

    if row["UsageStatus"] == "Low":
        score -= 20

    elif row["UsageStatus"] == "Medium":
        score -= 8

    if row["FeatureAdoption"] < 50:
        score -= 10

    return max(score, 0)

df["HealthScore"] = df.apply(calculate_health, axis=1)

# ---------------------------------------------------
# RISK
# ---------------------------------------------------

def risk(score):

    if score >= 85:
        return "🟢 Low"

    elif score >= 65:
        return "🟡 Medium"

    return "🔴 High"

df["Risk"] = df["HealthScore"].apply(risk)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("📊 Customer 360 Dashboard")

st.caption("AI Powered Unified Customer Intelligence Platform")

# ---------------------------------------------------
# KPI
# ---------------------------------------------------

customers = len(df)

mrr = int(df["MRR"].sum())

tickets = int(df["OpenTickets"].sum())

health = round(df["HealthScore"].mean(),1)

c1,c2,c3,c4 = st.columns(4)

c1.metric("👥 Customers",customers)

c2.metric("💰 Total MRR",f"₹{mrr:,}")

c3.metric("🎫 Open Tickets",tickets)

c4.metric("❤️ Avg Health",health)

st.divider()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("Customer Filters")

plan = st.sidebar.multiselect(
    "Plan",
    options=sorted(df["Plan"].unique()),
    default=sorted(df["Plan"].unique())
)

stage = st.sidebar.multiselect(
    "Sales Stage",
    options=sorted(df["Stage"].unique()),
    default=sorted(df["Stage"].unique())
)

filtered = df[
    (df["Plan"].isin(plan)) &
    (df["Stage"].isin(stage))
]

customer = st.sidebar.selectbox(
    "Select Customer",
    filtered["CustomerName"]
)

row = filtered[
    filtered["CustomerName"]==customer
].iloc[0]

# ---------------------------------------------------
# CHARTS
# ---------------------------------------------------

left,right = st.columns(2)

with left:

    fig = px.pie(
        filtered,
        names="Plan",
        title="Customers by Subscription Plan"
    )

    st.plotly_chart(fig,use_container_width=True)

with right:

    fig2 = px.bar(
        filtered,
        x="Stage",
        y="MRR",
        color="Stage",
        title="Revenue by Sales Stage"
    )

    st.plotly_chart(fig2,use_container_width=True)

st.divider()

# ---------------------------------------------------
# CUSTOMER OVERVIEW
# ---------------------------------------------------

st.header("👤 Customer Overview")

left,right = st.columns([2,1])

with left:

    st.subheader(row["CustomerName"])

    st.write(f"**🏢 Company:** {row['Company']}")

    st.write(f"**🏭 Industry:** {row['Industry']}")

    st.write(f"**💳 Plan:** {row['Plan']}")

    st.write(f"**💰 MRR:** ₹{row['MRR']:,}")

    st.write(f"**👨‍💼 Owner:** {row['Owner']}")

    st.write(f"**📌 Stage:** {row['Stage']}")

with right:

    st.metric("❤️ Health",row["HealthScore"])

    st.metric("⚠️ Risk",row["Risk"])

    st.metric("🎫 Tickets",row["OpenTickets"])

st.divider()


# ---------------------------------------------------
# SUPPORT + EMAIL
# ---------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("🎫 Support")

    st.write(f"**Open Tickets:** {row['OpenTickets']}")
    st.write(f"**Last Issue:** {row['LastIssue']}")
    st.write(f"**Priority:** {row['Priority']}")

with right:

    st.subheader("📧 Email Activity")

    st.write(f"**Latest Email:** {row['LastEmail']}")
    st.write(f"**Response Status:** {row['ResponseStatus']}")

st.divider()

# ---------------------------------------------------
# PRODUCT USAGE
# ---------------------------------------------------

st.header("📈 Product Usage")

c1, c2, c3 = st.columns(3)

c1.metric("Monthly Logins", row["MonthlyLogins"])
c2.metric("Feature Adoption", f"{row['FeatureAdoption']}%")
c3.metric("Usage Status", row["UsageStatus"])

st.write(f"**Last Login:** {row['LastLoginDays']} day(s) ago")

st.divider()

# ---------------------------------------------------
# INTERNAL NOTES
# ---------------------------------------------------

st.header("💬 Internal Team Notes")

left, right = st.columns(2)

with left:
    st.info(row["SlackNote"])

with right:
    st.success(row["OwnerComment"])

st.divider()

# ---------------------------------------------------
# BUSINESS SIGNALS
# ---------------------------------------------------

st.header("📊 Business Signals")

signals = []

if row["OpenTickets"] >= 2:
    signals.append("🔴 Multiple support tickets require immediate attention.")

if row["ResponseStatus"] == "Negative":
    signals.append("🔴 Customer sentiment is negative.")

if row["UsageStatus"] == "Low":
    signals.append("🟠 Product usage is low.")

if row["FeatureAdoption"] < 60:
    signals.append("🟠 Feature adoption is below expected levels.")

if row["Plan"] == "Enterprise":
    signals.append("⭐ High-value Enterprise customer.")

if row["Stage"] in ["Negotiation", "Proposal Sent"]:
    signals.append("🟢 High probability sales opportunity.")

if len(signals) == 0:
    signals.append("🟢 Customer account looks healthy.")

for signal in signals:
    st.write(signal)

st.divider()

# ---------------------------------------------------
# HEALTH CHART
# ---------------------------------------------------

st.header("❤️ Customer Health")

health_df = pd.DataFrame({
    "Metric": ["Health Score"],
    "Value": [row["HealthScore"]]
})

fig = px.bar(
    health_df,
    x="Metric",
    y="Value",
    text="Value",
    range_y=[0,100],
    color="Value",
    color_continuous_scale="RdYlGn"
)

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------
# AI CUSTOMER SUMMARY
# ---------------------------------------------------

st.header("🤖 AI Customer Summary")

if row["HealthScore"] >= 85:
    health = "Healthy"
elif row["HealthScore"] >= 65:
    health = "Stable"
else:
    health = "At Risk"

summary = f"""
### Customer Snapshot

**Customer:** {row['CustomerName']}

**Company:** {row['Company']}

**Industry:** {row['Industry']}

**Sales Stage:** {row['Stage']}

---

### Health Overview

- Health Score: **{row['HealthScore']}/100**
- Risk Level: **{row['Risk']}**

---

### Support

- Open Tickets: **{row['OpenTickets']}**
- Latest Issue: **{row['LastIssue']}**

---

### Product Usage

- Monthly Logins: **{row['MonthlyLogins']}**
- Feature Adoption: **{row['FeatureAdoption']}%**
- Usage Status: **{row['UsageStatus']}**

---

### Email Engagement

**{row['ResponseStatus']}**

---

### Internal Notes

{row['SlackNote']}

"""

st.success(summary)

st.divider()

# ---------------------------------------------------
# NEXT BEST ACTION
# ---------------------------------------------------

st.header("🎯 Recommended Next Best Actions")

actions = []

if row["OpenTickets"] >= 2:
    actions.append("Resolve all open support tickets within 24 hours.")

if row["ResponseStatus"] == "Negative":
    actions.append("Customer Success Manager should contact the customer immediately.")

if row["UsageStatus"] == "Low":
    actions.append("Schedule a product adoption or training session.")

if row["FeatureAdoption"] < 60:
    actions.append("Recommend advanced features to improve adoption.")

if row["Stage"] == "Negotiation":
    actions.append("Arrange a commercial discussion and finalize pricing.")

if row["Stage"] == "Proposal Sent":
    actions.append("Follow up on the proposal within 48 hours.")

if row["Plan"] == "Enterprise":
    actions.append("Identify upsell and cross-sell opportunities.")

if len(actions) == 0:
    actions.append("Maintain regular engagement with the customer.")

for i, action in enumerate(actions, start=1):
    st.success(f"{i}. {action}")

st.divider()

# ---------------------------------------------------
# DATA TABLE
# ---------------------------------------------------

st.header("📋 Complete Customer Record")

st.dataframe(
    row.to_frame().T,
    use_container_width=True
)

st.divider()

st.caption(
    "Built by Vinod • Volopay Growth Squad Assessment • Customer 360 Dashboard"
)