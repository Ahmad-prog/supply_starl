import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

# Page config
st.set_page_config(
    page_title="🚨 Supply Chain Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .critical-alert {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
        animation: pulse 2s infinite;
        border-left: 5px solid #fff;
    }
    .high-alert {
        background: linear-gradient(135deg, #ff8800, #e67300);
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        font-weight: bold;
        border-left: 4px solid #fff;
    }
    .medium-alert {
        background: linear-gradient(135deg, #ffaa00, #cc8800);
        color: white;
        padding: 10px;
        border-radius: 6px;
        margin: 6px 0;
        border-left: 3px solid #fff;
    }
    .success-box {
        background: linear-gradient(135deg, #00cc44, #009933);
        color: white;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        border-left: 3px solid #fff;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
        100% { opacity: 1; transform: scale(1); }
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)


def parse_supply_chain_data():
    """Parse the supply chain data from the structured format"""

    # Production data (hardcoded based on your structure)
    production_data = [
        {'Date': '10-Jun-2025', 'Planned_Qty': 800, 'Actual_Qty': 936, 'Variance': 136, 'Reason': '2 Lines loading'},
        {'Date': '11-Jun-2025', 'Planned_Qty': 800, 'Actual_Qty': 1180, 'Variance': 380,
         'Reason': '2 Lines loading/material issue'},
        {'Date': '12-Jun-2025', 'Planned_Qty': 800, 'Actual_Qty': 650, 'Variance': -150,
         'Reason': 'Loading end/feeding issue'},
        {'Date': '13-Jun-2025', 'Planned_Qty': 2000, 'Actual_Qty': 0, 'Variance': -2000,
         'Reason': 'FEEDING ISSUE FROM CUTTING'},
        {'Date': '14-Jun-2025', 'Planned_Qty': 2000, 'Actual_Qty': 0, 'Variance': -2000,
         'Reason': 'FEEDING ISSUE FROM CUTTING'},
        {'Date': '16-Jun-2025', 'Planned_Qty': 2000, 'Actual_Qty': 393, 'Variance': -1607,
         'Reason': 'FEEDING ISSUE FROM CUTTING'}
    ]

    # Capacity data
    capacity_data = [
        {'Department': 'Cutting', 'Capacity': 3000, 'Planned_Load': 1823, 'Actual_Prod': 1800, 'Utilization': 60,
         'MTD': 8763},
        {'Department': 'Stitching', 'Capacity': 2788, 'Planned_Load': 0, 'Actual_Prod': 393, 'Utilization': 14,
         'MTD': 7974},
        {'Department': 'Lasting', 'Capacity': 3462, 'Planned_Load': 0, 'Actual_Prod': 0, 'Utilization': 0, 'MTD': 12100}
    ]

    # MRP data
    mrp_data = [
        {'Order': '673', 'Ordered': 'Yes', 'Available': 'Yes', 'Status': 'Complete'},
        {'Order': '675', 'Ordered': 'Yes', 'Available': 'Yes', 'Status': 'Complete'},
        {'Order': '677', 'Ordered': 'Yes', 'Available': 'Yes', 'Status': 'Complete'},
        {'Order': '679', 'Ordered': 'No', 'Available': 'No', 'Status': 'Critical'},
        {'Order': '680', 'Ordered': 'Yes', 'Available': 'No', 'Status': 'Pending'},
        {'Order': '681', 'Ordered': 'No', 'Available': 'No', 'Status': 'Critical'}
    ]

    # Procurement data
    procurement_data = {
        'PO_Issued': {'Count': 92, 'Amount': 114.77},
        'PO_Received': {'Count': 56, 'Amount': 96.84},
        'PO_Pending': {'Count': 36, 'Amount': 17.93}
    }

    # Import status
    import_data = {
        'PI': {'Total': 12, 'Received': 12, 'Approved': 12, 'Pending': 0},
        'Payment': {'Done': 3, 'Pending': 4, 'Total': 7},
        'Shipment': {'May': 1, 'June': 8, 'July': 1}
    }

    # Warehouse data
    warehouse_data = {
        'FG_Stock': {'Elten': 1090, 'Bata': 0, 'S-Step': 1500, 'Total': 2590},
        'GRN': {'Total': 4, 'Done': 4, 'Pending': 0}
    }

    return {
        'production': pd.DataFrame(production_data),
        'capacity': pd.DataFrame(capacity_data),
        'mrp': pd.DataFrame(mrp_data),
        'procurement': procurement_data,
        'imports': import_data,
        'warehouse': warehouse_data
    }


def analyze_critical_issues(data):
    """Analyze data and identify critical issues"""
    critical_issues = []
    high_issues = []
    medium_issues = []

    # Production analysis
    prod_df = data['production']
    total_variance = prod_df['Variance'].sum()
    if total_variance < -3000:
        critical_issues.append(f"🚨 CRITICAL: Production shortfall of {abs(total_variance):,} units")

    # Feeding issues
    feeding_issues = prod_df[prod_df['Reason'].str.contains('FEEDING ISSUE', na=False)]
    if len(feeding_issues) >= 3:
        critical_issues.append(f"🔥 CRITICAL: {len(feeding_issues)} days of feeding issues from cutting")

    # Capacity utilization
    cap_df = data['capacity']
    for _, row in cap_df.iterrows():
        if row['Utilization'] < 20:
            critical_issues.append(f"⚠️ CRITICAL: {row['Department']} capacity at {row['Utilization']}%")
        elif row['Utilization'] < 40:
            high_issues.append(f"🔶 HIGH: {row['Department']} underutilized at {row['Utilization']}%")

    # MRP issues
    mrp_df = data['mrp']
    critical_orders = mrp_df[mrp_df['Status'] == 'Critical']
    if len(critical_orders) > 0:
        high_issues.append(f"📋 HIGH: {len(critical_orders)} orders with material unavailability")

    # Procurement issues
    proc = data['procurement']
    pending_ratio = proc['PO_Pending']['Count'] / proc['PO_Issued']['Count']
    if pending_ratio > 0.3:
        medium_issues.append(f"📦 MEDIUM: {pending_ratio:.1%} of POs pending")

    return critical_issues, high_issues, medium_issues


def create_production_chart(prod_df):
    """Create production performance chart"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=prod_df['Date'],
        y=prod_df['Planned_Qty'],
        name='Planned',
        marker_color='lightblue',
        opacity=0.7
    ))

    fig.add_trace(go.Bar(
        x=prod_df['Date'],
        y=prod_df['Actual_Qty'],
        name='Actual',
        marker_color=['red' if v < 0 else 'green' for v in prod_df['Variance']]
    ))

    fig.update_layout(
        title="📊 Production Plan vs Actual",
        height=300,
        template='plotly_dark'
    )
    return fig


def create_capacity_chart(cap_df):
    """Create capacity utilization chart"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=cap_df['Department'],
        y=cap_df['Utilization'],
        name='Utilization %',
        marker_color=['red' if x < 30 else 'orange' if x < 60 else 'green' for x in cap_df['Utilization']],
        text=[f"{x}%" for x in cap_df['Utilization']],
        textposition='auto'
    ))

    fig.update_layout(
        title="⚡ Capacity Utilization by Department",
        yaxis_title="Utilization %",
        height=300,
        template='plotly_dark'
    )
    return fig


def create_summary_report(data, critical_issues, high_issues, medium_issues):
    """Create executive summary report"""
    report = f"""
# 📊 SUPPLY CHAIN EXECUTIVE SUMMARY
**Report Date:** {datetime.now().strftime('%d-%b-%Y %H:%M')}

## 🚨 CRITICAL ALERTS ({len(critical_issues)})
"""
    for issue in critical_issues:
        report += f"- {issue}\n"

    report += f"""
## ⚠️ HIGH PRIORITY ({len(high_issues)})
"""
    for issue in high_issues:
        report += f"- {issue}\n"

    report += f"""
## 📋 KEY METRICS
- **Production Efficiency:** {(data['production']['Actual_Qty'].sum() / data['production']['Planned_Qty'].sum() * 100):.1f}%
- **Total Production Variance:** {data['production']['Variance'].sum():,} units
- **Average Capacity Utilization:** {data['capacity']['Utilization'].mean():.1f}%
- **PO Completion Rate:** {(data['procurement']['PO_Received']['Count'] / data['procurement']['PO_Issued']['Count'] * 100):.1f}%
- **Total FG Inventory:** {data['warehouse']['FG_Stock']['Total']:,} pairs

## 🔄 RECOMMENDATIONS
1. **URGENT:** Address feeding issues from cutting department
2. **HIGH:** Increase stitching and lasting capacity utilization
3. **MEDIUM:** Expedite pending material orders (679, 681)
4. **MEDIUM:** Follow up on {data['procurement']['PO_Pending']['Count']} pending POs worth pkr{data['procurement']['PO_Pending']['Amount']}M
"""
    return report


def export_report_to_excel(data, summary_report):
    """Export dashboard data to Excel"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame({'Executive Summary': [summary_report]})
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)

        # Data sheets
        data['production'].to_excel(writer, sheet_name='Production', index=False)
        data['capacity'].to_excel(writer, sheet_name='Capacity', index=False)
        data['mrp'].to_excel(writer, sheet_name='MRP', index=False)

        # Procurement sheet
        proc_df = pd.DataFrame([
            ['PO Issued', data['procurement']['PO_Issued']['Count'], data['procurement']['PO_Issued']['Amount']],
            ['PO Received', data['procurement']['PO_Received']['Count'], data['procurement']['PO_Received']['Amount']],
            ['PO Pending', data['procurement']['PO_Pending']['Count'], data['procurement']['PO_Pending']['Amount']]
        ], columns=['Status', 'Count', 'Amount (M)'])
        proc_df.to_excel(writer, sheet_name='Procurement', index=False)

        # Warehouse sheet
        wh_df = pd.DataFrame([
            ['Elten', data['warehouse']['FG_Stock']['Elten']],
            ['Bata', data['warehouse']['FG_Stock']['Bata']],
            ['S-Step', data['warehouse']['FG_Stock']['S-Step']],
            ['Total', data['warehouse']['FG_Stock']['Total']]
        ], columns=['Brand', 'Stock (Pairs)'])
        wh_df.to_excel(writer, sheet_name='Warehouse', index=False)

    return output.getvalue()


# Main Dashboard
def main():
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("# 🚨 Supply Chain Command Center")
        st.markdown("### Real-Time Dashboard & Analytics")

    with col3:
        st.markdown(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")

    # Load and analyze data
    data = parse_supply_chain_data()
    critical_issues, high_issues, medium_issues = analyze_critical_issues(data)

    # CRITICAL ALERTS SECTION (TOP PRIORITY)
    st.markdown("## 🚨 CRITICAL ALERTS & SUMMARY")

    if critical_issues:
        for issue in critical_issues:
            st.markdown(f'<div class="critical-alert">{issue}</div>', unsafe_allow_html=True)

    if high_issues:
        for issue in high_issues:
            st.markdown(f'<div class="high-alert">{issue}</div>', unsafe_allow_html=True)

    if medium_issues:
        for issue in medium_issues:
            st.markdown(f'<div class="medium-alert">{issue}</div>', unsafe_allow_html=True)

    if not any([critical_issues, high_issues, medium_issues]):
        st.markdown('<div class="success-box">✅ All Systems Operating Normally</div>', unsafe_allow_html=True)

    # KEY METRICS ROW
    st.markdown("## 📊 KEY PERFORMANCE METRICS")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        efficiency = (data['production']['Actual_Qty'].sum() / data['production']['Planned_Qty'].sum() * 100)
        st.metric("Production Efficiency", f"{efficiency:.1f}%",
                  delta=f"{efficiency - 100:.1f}%", delta_color="inverse" if efficiency < 100 else "normal")

    with col2:
        variance = data['production']['Variance'].sum()
        st.metric("Production Variance", f"{variance:,}",
                  delta=f"{variance:,}", delta_color="inverse" if variance < 0 else "normal")

    with col3:
        avg_util = data['capacity']['Utilization'].mean()
        st.metric("Avg Capacity Util.", f"{avg_util:.1f}%",
                  delta=f"{avg_util - 50:.1f}%", delta_color="normal" if avg_util > 50 else "inverse")

    with col4:
        po_rate = (data['procurement']['PO_Received']['Count'] / data['procurement']['PO_Issued']['Count'] * 100)
        st.metric("PO Completion", f"{po_rate:.1f}%")

    with col5:
        total_inventory = data['warehouse']['FG_Stock']['Total']
        st.metric("FG Inventory", f"{total_inventory:,}")

    # VISUALIZATIONS
    st.markdown("## 📈 ANALYTICS DASHBOARD")

    # Row 1: Production & Capacity
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_production_chart(data['production']), use_container_width=True)
    with col2:
        st.plotly_chart(create_capacity_chart(data['capacity']), use_container_width=True)

    # Row 2: Detailed Tables
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Production", "⚡ Capacity", "📋 MRP Status", "🏭 Warehouse"])

    with tab1:
        st.dataframe(data['production'], use_container_width=True)

    with tab2:
        st.dataframe(data['capacity'], use_container_width=True)

    with tab3:
        mrp_styled = data['mrp'].style.applymap(
            lambda x: 'background-color: #ffcccc' if x == 'Critical' else
            'background-color: #fff3cd' if x == 'Pending' else '',
            subset=['Status']
        )
        st.dataframe(mrp_styled, use_container_width=True)

    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Finished Goods Stock**")
            fg_df = pd.DataFrame([
                ['Elten', data['warehouse']['FG_Stock']['Elten']],
                ['Bata', data['warehouse']['FG_Stock']['Bata']],
                ['S-Step', data['warehouse']['FG_Stock']['S-Step']],
                ['**Total**', data['warehouse']['FG_Stock']['Total']]
            ], columns=['Brand', 'Stock (Pairs)'])
            st.dataframe(fg_df, use_container_width=True)

        with col2:
            st.markdown("**Procurement Summary**")
            proc_df = pd.DataFrame([
                ['PO Issued', data['procurement']['PO_Issued']['Count'],
                 f"pkr{data['procurement']['PO_Issued']['Amount']}M"],
                ['PO Received', data['procurement']['PO_Received']['Count'],
                 f"pkr{data['procurement']['PO_Received']['Amount']}M"],
                ['PO Pending', data['procurement']['PO_Pending']['Count'],
                 f"pkr{data['procurement']['PO_Pending']['Amount']}M"]
            ], columns=['Status', 'Count', 'Amount'])
            st.dataframe(proc_df, use_container_width=True)

    # EXPORT SECTION
    st.markdown("## 📤 EXPORT REPORTS")
    col1, col2 = st.columns(2)

    with col1:
        # Generate summary report
        summary_report = create_summary_report(data, critical_issues, high_issues, medium_issues)
        st.download_button(
            label="📄 Download Executive Summary",
            data=summary_report,
            file_name=f"Supply_Chain_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()