import streamlit as st
import pandas as pd

st.set_page_config(page_title="Customer 360 Dashboard", layout="wide")

crm = pd.read_csv("crm.csv")
support = pd.read_csv("support.csv")
emails = pd.read_csv("emails.csv")

st.title("📊 Customer 360 AI Dashboard")

customer = st.selectbox(
    "Select Customer",
    crm["CustomerName"]
)

crm_row = crm[crm["CustomerName"] == customer].iloc[0]
support_row = support[support["CustomerID"] == crm_row["CustomerID"]].iloc[0]
email_row = emails[emails["CustomerID"] == crm_row["CustomerID"]].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.subheader("CRM Details")
    st.write(f"**Company:** {crm_row['Company']}")
    st.write(f"**Industry:** {crm_row['Industry']}")
    st.write(f"**Plan:** {crm_row['Plan']}")
    st.write(f"**MRR:** ₹{crm_row['MRR']}")
    st.write(f"**Owner:** {crm_row['Owner']}")
    st.write(f"**Stage:** {crm_row['Stage']}")

with col2:
    st.subheader("Support")
    st.write(f"Open Tickets: {support_row['OpenTickets']}")
    st.write(f"Last Issue: {support_row['LastIssue']}")
    st.write(f"Priority: {support_row['Priority']}")

st.subheader("Email Activity")


st.write(f"Last Email: {email_row['LastEmail']}")
st.write(f"Status: {email_row['ResponseStatus']}")

st.subheader("AI Summary")

risk = "Low"
if support_row["OpenTickets"] >= 2:
    risk = "High"
elif support_row["OpenTickets"] == 1:
    risk = "Medium"

if email_row["ResponseStatus"] == "Negative":
    action = "Escalate to Customer Success and schedule a call."
elif support_row["OpenTickets"] > 1:
    action = "Resolve support issues before sales follow-up."
else:
    action = "Schedule product demo and discuss upgrade."

summary = f"""
Customer {crm_row['CustomerName']} from {crm_row['Company']} is currently in the
{crm_row['Stage']} stage.

They have {support_row['OpenTickets']} open support ticket(s).

Email sentiment is **{email_row['ResponseStatus']}**.

Overall Risk: **{risk}**

Recommended Next Best Action:

{action}
"""

st.success(summary)