import streamlit as st
import requests
import json
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AML AI Analysis & Alert Prioritization Demo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Default API Base URL
DEFAULT_API_BASE_URL = "https://syedkhizarrayaz-bm-ai-analysis-and-alert-priorit-2625d69.hf.space"

# Example data for Prediction API
PREDICTION_EXAMPLE = [
    {
        "AlertID": 1001,
        "FocusColumnValue": "PK-42101-1234567-1",
        "AlertScore": 85.5,
        "CreateDate": "2025-06-15T10:30:00",
        "riskLevel": "Low",
        "MatchDetails": '{"id": "PK-42101-1234567-1", "scenario": "Unusually large installment", "score": 85.5, "riskLevel": "Low"}',
        "MatchInfoJson": '[{"ID": "PK-42101-1234567-1", "TRANSACTIONAMOUNT": 150000, "CURRENCY": "PKR", "INSTALLMENTNUMBER": 1}, {"ID": "PK-42101-1234567-1", "TRANSACTIONAMOUNT": 180000, "CURRENCY": "PKR", "INSTALLMENTNUMBER": 2}, {"ID": "PK-42101-1234567-1", "TRANSACTIONAMOUNT": 200000, "CURRENCY": "PKR", "INSTALLMENTNUMBER": 3}]',
        "ScenarioName": "Unusually large installment",
        "workflow": "Unassigned"
    },
    {
        "AlertID": 1002,
        "FocusColumnValue": "PK-35202-9876543-2",
        "AlertScore": 92.0,
        "CreateDate": "2025-06-20T14:15:00",
        "riskLevel": "High",
        "MatchDetails": '{"id": "PK-35202-9876543-2", "scenario": "Structuring / Smurfing activity", "score": 92.0, "riskLevel": "High"}',
        "MatchInfoJson": '[{"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9500, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}, {"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9800, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}, {"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9200, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}, {"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9600, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}, {"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9400, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}, {"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9900, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}, {"ID": "PK-35202-9876543-2", "TRANSACTIONAMOUNT": 9100, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Cash Deposit"}]',
        "ScenarioName": "Structuring / Smurfing activity",
        "workflow": "Unassigned"
    },
    {
        "AlertID": 1003,
        "FocusColumnValue": "PK-37405-5551234-3",
        "AlertScore": 78.3,
        "CreateDate": "2025-06-25T09:45:00",
        "riskLevel": "Medium",
        "MatchDetails": '{"id": "PK-37405-5551234-3", "scenario": "Rapid movement of funds", "score": 78.3, "riskLevel": "Medium"}',
        "MatchInfoJson": '[{"ID": "PK-37405-5551234-3", "TRANSACTIONAMOUNT": 250000, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Wire Transfer", "COUNTERPARTYACCOUNT": "AE987654321098765432"}, {"ID": "PK-37405-5551234-3", "TRANSACTIONAMOUNT": 300000, "CURRENCY": "PKR", "TRANSACTIONTYPE": "Wire Transfer", "COUNTERPARTYACCOUNT": "GB12ABCD123456789012"}]',
        "ScenarioName": "Rapid movement of funds",
        "workflow": "Unassigned"
    }
]

# Example data for Analysis API
ANALYSIS_EXAMPLE = [
    {
        "AlertID": 1,
        "FilteredTransactions": '[{"CUSTOMERID":"100001","IDENTITYNUMBERS":"42101-1234567-1","LOANID":"LN2024001","ACCOUNTID":"AC100001","CREATEDDATE":"2025-06-01 10:15:00","TRANSACTIONAMOUNT":150000.0,"CURRENCY":"PKR","INSTALLMENTNUMBER":1,"EXCESSAMOUNT":0.0},{"CUSTOMERID":"100001","IDENTITYNUMBERS":"42101-1234567-1","LOANID":"LN2024001","ACCOUNTID":"AC100001","CREATEDDATE":"2025-06-15 14:20:00","TRANSACTIONAMOUNT":180000.0,"CURRENCY":"PKR","INSTALLMENTNUMBER":2,"EXCESSAMOUNT":0.0},{"CUSTOMERID":"100001","IDENTITYNUMBERS":"42101-1234567-1","LOANID":"LN2024001","ACCOUNTID":"AC100001","CREATEDDATE":"2025-06-28 16:45:00","TRANSACTIONAMOUNT":200000.0,"CURRENCY":"PKR","INSTALLMENTNUMBER":3,"EXCESSAMOUNT":0.0}]',
        "FocusColumnValue": "100001",
        "KYCMonthlyIncome": "85,000 PKR",
        "KYCNoOfCredits": "3-5",
        "KYCNoOfDebits": "8-12",
        "KYCRiskCategoryValue": "Low",
        "KYCValueOfCredits": "150,000 - 200,000 PKR",
        "KYCValueOfDebits": "80,000 - 120,000 PKR",
        "OccupationValue": "Private Employee",
        "STRCount": 0,
        "STRScenarioHistory": "",
        "ScenarioName": "Unusually large installment",
        "CustomerName": "Muhammad Bilal Sheikh",
        "CUSTOMERID": "100001",
        "BranchID": "KHI-DHA",
        "Country": "Pakistan",
        "CustomerType": "Retail",
        "CustomerStatus": "Retail Customer",
        "CreatedDate": "2020-01-15",
        "RelationshipStartDate": "2020-01-15",
        "RiskScore": "4.2",
        "PreviousAlerts": [],
        "Counterparties": [],
        "BranchQueries": {
            "Requested": "Verification required for loan installments totaling 530,000 PKR within one month, significantly exceeding declared monthly income of 85,000 PKR. Please confirm source of funds and provide documentation for additional income sources.",
            "Response": "Customer stated installments are from remittances received from brother working in UAE, family savings from wedding expenses, and advance salary from employer for Eid holidays. Customer provided remittance receipts and employer letter."
        }
    },
    {
        "AlertID": 2,
        "FilteredTransactions": '[{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 09:30:00","TRANSACTIONAMOUNT":9500.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 11:30:00","TRANSACTIONAMOUNT":9800.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 13:30:00","TRANSACTIONAMOUNT":9200.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 15:30:00","TRANSACTIONAMOUNT":9600.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 17:30:00","TRANSACTIONAMOUNT":9400.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 19:30:00","TRANSACTIONAMOUNT":9900.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-02 21:30:00","TRANSACTIONAMOUNT":9100.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Cash Deposit","COUNTERPARTYACCOUNT":"","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-03 10:15:00","TRANSACTIONAMOUNT":450000.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Wire Transfer","COUNTERPARTYACCOUNT":"AE123456789012345678","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-03 14:30:00","TRANSACTIONAMOUNT":500000.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Wire Transfer","COUNTERPARTYACCOUNT":"GB29NWBK60161331926819","EXCESSAMOUNT":0.0},{"CUSTOMERID":"100002","IDENTITYNUMBERS":"35202-9876543-2","LOANID":"","ACCOUNTID":"AC100002","CREATEDDATE":"2025-06-03 16:45:00","TRANSACTIONAMOUNT":56525.0,"CURRENCY":"PKR","TRANSACTIONTYPE":"Local Transfer","COUNTERPARTYACCOUNT":"PK36SCBL0000001123456702","EXCESSAMOUNT":0.0}]',
        "FocusColumnValue": "100002",
        "KYCMonthlyIncome": "55,000 PKR",
        "KYCNoOfCredits": "7",
        "KYCNoOfDebits": "6",
        "KYCRiskCategoryValue": "Medium",
        "KYCValueOfCredits": "66,500 PKR",
        "KYCValueOfDebits": "56,525 PKR",
        "OccupationValue": "Textile Trader",
        "STRCount": 2,
        "STRScenarioHistory": "Large Cash Deposits, Rapid Fund Transfers",
        "ScenarioName": "Structuring / Smurfing activity",
        "CustomerName": "Ayesha Malik",
        "CUSTOMERID": "100002",
        "BranchID": "LHR-GUL",
        "Country": "Pakistan",
        "CustomerType": "Retail",
        "CustomerStatus": "Retail Customer",
        "CreatedDate": "2019-03-20",
        "RelationshipStartDate": "2019-03-20",
        "RiskScore": "8.5",
        "PreviousAlerts": [
            {
                "AlertName": "Large Cash Deposits",
                "Description": "1,200,000 PKR deposited in cash across multiple transactions in single day",
                "BranchExplanation": "Proceeds from sale of commercial property in Faisalabad",
                "Documentation": "",
                "RiskEscalation": ""
            },
            {
                "AlertName": "Rapid Fund Transfers",
                "Description": "950,000 PKR transferred to multiple accounts in Dubai and UK within 48 hours of deposit",
                "BranchExplanation": "Payment for textile machinery imports and supplier advance",
                "Documentation": "",
                "RiskEscalation": "Risk score escalated due to rapid fund movement to multiple high-risk jurisdictions without proper trade documentation."
            }
        ],
        "Counterparties": [
            {
                "Name": "Al-Madina Textile Machinery LLC",
                "AccountID": "AE123456789012345678",
                "Country": "United Arab Emirates",
                "Jurisdiction": "Dubai",
                "TransactionAmount": 450000.0,
                "Currency": "PKR",
                "TransactionDate": "2025-06-03 10:15:00",
                "TransactionType": "Wire Transfer",
                "Relationship": "Supplier",
                "RiskLevel": "Medium",
                "ScreeningResult": "No adverse media found"
            },
            {
                "Name": "Manchester Textile Imports Ltd",
                "AccountID": "GB29NWBK60161331926819",
                "Country": "United Kingdom",
                "Jurisdiction": "Manchester",
                "TransactionAmount": 500000.0,
                "Currency": "PKR",
                "TransactionDate": "2025-06-03 14:30:00",
                "TransactionType": "Wire Transfer",
                "Relationship": "Business Partner",
                "RiskLevel": "High",
                "ScreeningResult": "Flagged for enhanced due diligence - multiple transactions with high-risk jurisdictions"
            },
            {
                "Name": "Ahmed Textiles Faisalabad",
                "AccountID": "PK36SCBL0000001123456702",
                "Country": "Pakistan",
                "Jurisdiction": "Faisalabad",
                "TransactionAmount": 56525.0,
                "Currency": "PKR",
                "TransactionDate": "2025-06-03 16:45:00",
                "TransactionType": "Local Transfer",
                "Relationship": "Local Supplier",
                "RiskLevel": "Low",
                "ScreeningResult": "Verified local business entity"
            }
        ],
        "BranchQueries": {
            "Requested": "Multiple cash deposits totaling 66,500 PKR made in same day, each below 10,000 PKR threshold. Pattern suggests potential structuring to avoid CTR reporting. Please verify legitimate business purpose and provide sales invoices or receipts.",
            "Response": "Customer explained these are daily cash collections from retail textile sales at Anarkali Bazaar. Customer provided daily sales register and GST invoices. Stated pattern is normal for cash-based business operations."
        }
    }
]

def call_prediction_api(data: List[Dict[str, Any]], api_base_url: str = DEFAULT_API_BASE_URL) -> Dict[str, Any]:
    """Call the prediction API - handles single alert per request"""
    url = f"{api_base_url}/api/ai-service/predictalertpriority"
    results = []
    errors = []
    
    # Process each alert individually since API expects a single object
    for i, alert_data in enumerate(data):
        try:
            response = requests.post(url, json=alert_data, timeout=120)
            response.raise_for_status()
            try:
                result_data = response.json()
                results.append(result_data)
            except json.JSONDecodeError:
                results.append({"raw_response": response.text, "alert_index": i})
        except requests.exceptions.Timeout:
            errors.append(f"Alert {i+1} (ID: {alert_data.get('AlertID', 'N/A')}): Request timed out.")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"{error_msg}\nDetails: {json.dumps(error_detail, indent=2)}"
                except:
                    error_msg = f"{error_msg}\nResponse: {e.response.text[:500]}"
            errors.append(f"Alert {i+1} (ID: {alert_data.get('AlertID', 'N/A')}): {error_msg}")
    
    if errors and not results:
        return {"success": False, "error": "\n".join(errors)}
    elif errors:
        return {"success": True, "data": results, "errors": errors, "partial": True}
    else:
        # Combine all results into a single response format
        combined_data = []
        for result in results:
            if isinstance(result, dict) and "data" in result:
                combined_data.extend(result["data"] if isinstance(result["data"], list) else [result["data"]])
            else:
                combined_data.append(result)
        
        return {"success": True, "data": {"status": 200, "message": "Success", "data": combined_data}}

def call_analysis_api(data: List[Dict[str, Any]], api_base_url: str = DEFAULT_API_BASE_URL, 
                       cloud: bool = False, llm_on_server: bool = False, 
                       url: str = "", anonymous: bool = False,
                       audit: bool = False, evaluation: bool = False) -> Dict[str, Any]:
    """Call the analysis API with flags"""
    try:
        # Add flags to each alert data object
        data_with_flags = []
        for alert in data:
            alert_copy = alert.copy()
            alert_copy['Cloud'] = cloud
            alert_copy['llm_on_server'] = llm_on_server
            alert_copy['url'] = url
            alert_copy['anonymous'] = anonymous
            alert_copy['audit'] = audit
            alert_copy['evaluation'] = evaluation
            data_with_flags.append(alert_copy)
        
        api_url = f"{api_base_url}/api/ai-service/generateamlanalysis"
        response = requests.post(api_url, json=data_with_flags, timeout=300)
        response.raise_for_status()
        try:
            result_data = response.json()
        except json.JSONDecodeError:
            result_data = {"raw_response": response.text}
        return {"success": True, "data": result_data}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. The analysis may take longer. Please try again."}
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = f"{error_msg}\nDetails: {json.dumps(error_detail, indent=2)}"
            except:
                error_msg = f"{error_msg}\nResponse: {e.response.text[:500]}"
        return {"success": False, "error": error_msg}

def display_prediction_result(result: Dict[str, Any]):
    """Display prediction results in a beautiful format"""
    if result.get("success"):
        data = result.get("data", {})
        
        # Handle partial success
        if result.get("partial") and result.get("errors"):
            st.warning("⚠️ Some alerts processed successfully, but some had errors:")
            for error in result.get("errors", []):
                st.error(error)
        
        # Extract predictions from response
        if isinstance(data, dict) and "data" in data:
            predictions = data["data"] if isinstance(data["data"], list) else [data["data"]]
        elif isinstance(data, list):
            # Handle list of response objects
            all_predictions = []
            for item in data:
                if isinstance(item, dict) and "data" in item:
                    preds = item["data"] if isinstance(item["data"], list) else [item["data"]]
                    all_predictions.extend(preds)
                else:
                    all_predictions.append(item)
            predictions = all_predictions
        else:
            predictions = [data]
        
        st.success("✅ Prediction completed successfully!")
        
        for pred in predictions:
            if isinstance(pred, dict):
                with st.expander(f"Alert ID: {pred.get('AlertID', 'N/A')} - {pred.get('STRScenario', pred.get('ScenarioName', 'Unknown'))}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Alert ID", pred.get('AlertID', 'N/A'))
                        st.metric("Focus Column", pred.get('FocusColumnValue', 'N/A'))
                    with col2:
                        prediction = pred.get('Prediction', 'N/A')
                        risk_color = {
                            'High': '🔴',
                            'Medium': '🟡',
                            'Low': '🟢'
                        }.get(prediction, '⚪')
                        st.metric("Prediction", f"{risk_color} {prediction}")
                        st.metric("Scenario", pred.get('STRScenario', pred.get('ScenarioName', 'N/A')))
                    with col3:
                        if isinstance(data, dict):
                            st.metric("Status", data.get('status', 'N/A'))
                            st.metric("Message", data.get('message', 'Success'))
                        else:
                            st.metric("Status", "Success")
                            st.metric("Message", "Processed")
    else:
        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

def display_analysis_result(result: Dict[str, Any]):
    """Display analysis results - showing only the analysis text"""
    if result.get("success"):
        data = result.get("data", {})
        
        # Handle different response formats
        if isinstance(data, dict):
            if "data" in data:
                analyses = data["data"] if isinstance(data["data"], list) else [data["data"]]
            elif "Analysis" in data:
                analyses = data["Analysis"] if isinstance(data["Analysis"], list) else [data["Analysis"]]
            else:
                analyses = [data]
        elif isinstance(data, list):
            analyses = data
        else:
            analyses = [data]
        
        st.success("✅ Analysis completed successfully!")
        
        for analysis in analyses:
            alert_id = analysis.get('AlertID', analysis.get('Alert ID', 'N/A'))
            customer_name = analysis.get('CustomerName', analysis.get('Customer Name', 'N/A'))
            
            # Show basic info in header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"📊 Analysis Report - Alert ID: {alert_id}")
            with col2:
                if customer_name and customer_name != 'N/A':
                    st.caption(f"Customer: {customer_name}")
            
            # Display thinking separately if present (from audit mode)
            thinking_text = analysis.get('thinking')
            if thinking_text:
                st.markdown("---")
                st.subheader("🧠 Thinking Process (Audit Mode)")
                st.caption("This section shows the model's reasoning process when Audit Mode is enabled.")
                
                # Display thinking in a separate styled text area
                st.text_area(
                    "Model Reasoning",
                    value=str(thinking_text),
                    height=400,
                    disabled=True,
                    label_visibility="visible",
                    key=f"thinking_{alert_id}",
                    help="This is the model's internal reasoning process. Scroll to view the full thinking."
                )
            
            # Display the analysis text
            analysis_text = analysis.get('analysis', analysis.get('Analysis', analysis.get('AnalysisReport', '')))
            
            if analysis_text:
                st.markdown("---")
                st.subheader("📊 Analysis Report")
                
                # Format the text for better display
                import html
                import re
                
                text = str(analysis_text)
                escaped_text = html.escape(text)
                
                # Split into lines and format
                lines = escaped_text.split('\n')
                formatted_lines = []
                in_list = False
                
                for i, line in enumerate(lines):
                    line_stripped = line.strip()
                    
                    # Skip empty lines but add spacing
                    if not line_stripped:
                        if formatted_lines and not formatted_lines[-1].endswith('<br>'):
                            formatted_lines.append('<br>')
                        continue
                    
                    # Detect main headers (like "AML Investigation Report", "Alert Summary", etc.)
                    if (line_stripped.endswith(':') and len(line_stripped) < 60 and 
                        not line_stripped.startswith(' ') and
                        (line_stripped.isupper() or 
                         any(keyword in line_stripped.lower() for keyword in ['report', 'summary', 'analysis', 'conclusion', 'recommendation', 'assessment', 'background', 'pattern', 'flow']))):
                        formatted_lines.append(f'<h3 style="color: #ffffff; margin: 25px 0 15px 0; font-weight: 700; font-size: 20px; border-bottom: 2px solid rgba(102, 126, 234, 0.6); padding-bottom: 8px;">{line_stripped}</h3>')
                    
                    # Detect sub-headers (short lines ending with colon)
                    elif line_stripped.endswith(':') and len(line_stripped) < 50 and not line_stripped.startswith(' '):
                        formatted_lines.append(f'<h4 style="color: #ffffff; margin: 18px 0 10px 0; font-weight: 600; font-size: 16px; color: #a8b5ff;">{line_stripped}</h4>')
                    
                    # Detect bold text markers
                    elif line_stripped.startswith('**') and line_stripped.endswith('**'):
                        bold_text = line_stripped.replace('**', '')
                        formatted_lines.append(f'<p style="color: #ffffff; margin: 12px 0; font-weight: 600; font-size: 16px;">{bold_text}</p>')
                    
                    # Detect list items (lines starting with - or •)
                    elif line_stripped.startswith('-') or line_stripped.startswith('•'):
                        if not in_list:
                            formatted_lines.append('<ul style="color: #ffffff; margin: 10px 0; padding-left: 25px;">')
                            in_list = True
                        list_text = line_stripped.lstrip('-•').strip()
                        formatted_lines.append(f'<li style="margin: 8px 0; line-height: 1.8;">{list_text}</li>')
                    
                    # Regular paragraph text
                    else:
                        if in_list:
                            formatted_lines.append('</ul>')
                            in_list = False
                        # Check if it's a key-value pair (like "Customer Name: ...")
                        if ':' in line_stripped and len(line_stripped.split(':')) == 2:
                            key, value = line_stripped.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            formatted_lines.append(
                                f'<p style="color: #ffffff; margin: 10px 0; line-height: 1.8;">'
                                f'<span style="font-weight: 600; color: #a8b5ff;">{key}:</span> '
                                f'<span>{value}</span></p>'
                            )
                        else:
                            formatted_lines.append(f'<p style="color: #ffffff; margin: 10px 0; line-height: 1.8;">{line_stripped}</p>')
                
                # Close any open list
                if in_list:
                    formatted_lines.append('</ul>')
                
                formatted_html = '\n'.join(formatted_lines)
                
                # Display in a styled container with transparent background and white text
                st.markdown(
                    f"""
                    <div style='
                        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
                        padding: 30px; 
                        border-radius: 12px; 
                        border-left: 4px solid #667eea;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
                        line-height: 1.8; 
                        color: #ffffff; 
                        font-size: 15px;
                        max-height: 800px;
                        overflow-y: auto;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    '>
                    {formatted_html}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.warning("No analysis text found in the response.")
            
            # Show metadata in a collapsible section
            with st.expander("📋 View Metadata", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Response Time", f"{analysis.get('response_time_ms', 0):.2f} ms")
                    st.metric("Method", analysis.get('method', 'N/A'))
                with col2:
                    st.metric("Model", analysis.get('model', 'N/A'))
                    st.metric("Alert ID", alert_id)
                with col3:
                    st.metric("Focus Column", analysis.get('FocusColumnValue', 'N/A'))
    else:
        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 AML AI Analysis & Alert Prioritization Demo</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("This demo showcases the AML AI Analysis and Alert Prioritization system. Use the tabs below to test different APIs.")
        st.markdown("---")
        
        # API Base URL Configuration
        st.markdown("### 🔗 API Configuration")
        api_base_url = st.text_input(
            "API Base URL",
            value=DEFAULT_API_BASE_URL,
            help="Base URL for the API endpoints",
            key="api_base_url"
        )
        st.markdown("---")
        st.markdown("### 📡 API Endpoints")
        st.code(f"{api_base_url}/api/ai-service/predictalertpriority")
        st.code(f"{api_base_url}/api/ai-service/generateamlanalysis")
    
    # Main tabs
    tab1, tab2 = st.tabs(["🎯 Alert Priority Prediction", "📊 AML Analysis Generation"])
    
    # Tab 1: Prediction API
    with tab1:
        st.header("🎯 Alert Priority Prediction API")
        st.markdown("Predict whether an alert should be escalated or closed using the ML model.")
        
        # Preload button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📥 Load Example Data", key="load_pred_example"):
                st.session_state.prediction_data = PREDICTION_EXAMPLE
                st.success("Example data loaded!")
        
        # Data input
        st.subheader("📝 Input Data")
        
        # Number of alerts
        num_alerts = st.number_input("Number of Alerts", min_value=1, max_value=10, value=1, key="num_pred_alerts")
        
        # Initialize session state
        if 'prediction_data' not in st.session_state:
            st.session_state.prediction_data = [{} for _ in range(num_alerts)]
        
        # Form for each alert
        alerts_data = []
        for i in range(num_alerts):
            with st.expander(f"Alert {i+1}", expanded=(i == 0)):
                alert_data = {}
                
                col1, col2 = st.columns(2)
                with col1:
                    alert_data['AlertID'] = st.number_input(f"Alert ID", value=st.session_state.prediction_data[i].get('AlertID', 1001) if i < len(st.session_state.prediction_data) else 1001, key=f"pred_alert_id_{i}")
                    alert_data['FocusColumnValue'] = st.text_input(f"Focus Column Value", value=st.session_state.prediction_data[i].get('FocusColumnValue', 'PK-42101-1234567-1') if i < len(st.session_state.prediction_data) else 'PK-42101-1234567-1', key=f"pred_focus_{i}")
                    alert_data['AlertScore'] = st.number_input(f"Alert Score", value=float(st.session_state.prediction_data[i].get('AlertScore', 85.5)) if i < len(st.session_state.prediction_data) else 85.5, key=f"pred_score_{i}")
                    alert_data['CreateDate'] = st.text_input(f"Create Date (ISO format)", value=st.session_state.prediction_data[i].get('CreateDate', '2025-06-15T10:30:00') if i < len(st.session_state.prediction_data) else '2025-06-15T10:30:00', key=f"pred_date_{i}")
                with col2:
                    alert_data['riskLevel'] = st.selectbox(f"Risk Level", ['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'].index(st.session_state.prediction_data[i].get('riskLevel', 'Low')) if i < len(st.session_state.prediction_data) and st.session_state.prediction_data[i].get('riskLevel') in ['Low', 'Medium', 'High'] else 0, key=f"pred_risk_{i}")
                    alert_data['ScenarioName'] = st.text_input(f"Scenario Name", value=st.session_state.prediction_data[i].get('ScenarioName', 'Unusually large installment') if i < len(st.session_state.prediction_data) else 'Unusually large installment', key=f"pred_scenario_{i}")
                    alert_data['workflow'] = st.text_input(f"Workflow", value=st.session_state.prediction_data[i].get('workflow', 'Unassigned') if i < len(st.session_state.prediction_data) else 'Unassigned', key=f"pred_workflow_{i}")
                
                alert_data['MatchDetails'] = st.text_area(f"Match Details (JSON string)", value=st.session_state.prediction_data[i].get('MatchDetails', '') if i < len(st.session_state.prediction_data) else '', key=f"pred_match_details_{i}", height=100)
                alert_data['MatchInfoJson'] = st.text_area(f"Match Info JSON (JSON array string)", value=st.session_state.prediction_data[i].get('MatchInfoJson', '') if i < len(st.session_state.prediction_data) else '', key=f"pred_match_info_{i}", height=100)
                
                alerts_data.append(alert_data)
        
        # Call API button
        if st.button("🚀 Predict Alert Priority", type="primary", key="call_pred_api"):
            # Get API base URL from sidebar (stored in session state)
            api_url = st.session_state.get('api_base_url', DEFAULT_API_BASE_URL)
            with st.spinner("Calling prediction API..."):
                result = call_prediction_api(alerts_data, api_url)
                st.session_state.prediction_result = result
        
        # Display results
        if 'prediction_result' in st.session_state:
            st.markdown("---")
            st.subheader("📈 Results")
            display_prediction_result(st.session_state.prediction_result)
    
    # Tab 2: Analysis API
    with tab2:
        st.header("📊 AML Analysis Generation API")
        st.markdown("Generate comprehensive AML analysis using Hybrid Template+LLM system.")
        
        # Preload button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📥 Load Example Data", key="load_analysis_example"):
                st.session_state.analysis_data = ANALYSIS_EXAMPLE
                st.success("Example data loaded!")
        
        # Data input
        st.subheader("📝 Input Data")
        
        # Number of alerts
        num_alerts_analysis = st.number_input("Number of Alerts", min_value=1, max_value=10, value=1, key="num_analysis_alerts")
        
        # Initialize session state
        if 'analysis_data' not in st.session_state:
            st.session_state.analysis_data = [{} for _ in range(num_alerts_analysis)]
        
        # Form for each alert
        alerts_analysis_data = []
        for i in range(num_alerts_analysis):
            with st.expander(f"Alert {i+1}", expanded=(i == 0)):
                alert_data = {}
                
                # Basic Information
                st.markdown("#### Basic Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    alert_data['AlertID'] = st.number_input(f"Alert ID", value=st.session_state.analysis_data[i].get('AlertID', 1) if i < len(st.session_state.analysis_data) else 1, key=f"analysis_alert_id_{i}")
                    alert_data['FocusColumnValue'] = st.text_input(f"Focus Column Value", value=st.session_state.analysis_data[i].get('FocusColumnValue', '100001') if i < len(st.session_state.analysis_data) else '100001', key=f"analysis_focus_{i}")
                    alert_data['ScenarioName'] = st.text_input(f"Scenario Name", value=st.session_state.analysis_data[i].get('ScenarioName', 'Unusually large installment') if i < len(st.session_state.analysis_data) else 'Unusually large installment', key=f"analysis_scenario_{i}")
                with col2:
                    alert_data['CustomerName'] = st.text_input(f"Customer Name", value=st.session_state.analysis_data[i].get('CustomerName', '') if i < len(st.session_state.analysis_data) else '', key=f"analysis_customer_name_{i}")
                    alert_data['CUSTOMERID'] = st.text_input(f"Customer ID", value=st.session_state.analysis_data[i].get('CUSTOMERID', '') if i < len(st.session_state.analysis_data) else '', key=f"analysis_customer_id_{i}")
                    alert_data['BranchID'] = st.text_input(f"Branch ID", value=st.session_state.analysis_data[i].get('BranchID', '') if i < len(st.session_state.analysis_data) else '', key=f"analysis_branch_{i}")
                with col3:
                    alert_data['Country'] = st.text_input(f"Country", value=st.session_state.analysis_data[i].get('Country', 'Pakistan') if i < len(st.session_state.analysis_data) else 'Pakistan', key=f"analysis_country_{i}")
                    alert_data['CustomerType'] = st.text_input(f"Customer Type", value=st.session_state.analysis_data[i].get('CustomerType', 'Retail') if i < len(st.session_state.analysis_data) else 'Retail', key=f"analysis_customer_type_{i}")
                    alert_data['RiskScore'] = st.text_input(f"Risk Score", value=st.session_state.analysis_data[i].get('RiskScore', '4.2') if i < len(st.session_state.analysis_data) else '4.2', key=f"analysis_risk_score_{i}")
                
                # KYC Information
                st.markdown("#### KYC Information")
                col1, col2 = st.columns(2)
                with col1:
                    alert_data['KYCMonthlyIncome'] = st.text_input(f"KYC Monthly Income", value=st.session_state.analysis_data[i].get('KYCMonthlyIncome', '85,000 PKR') if i < len(st.session_state.analysis_data) else '85,000 PKR', key=f"analysis_kyc_income_{i}")
                    alert_data['KYCNoOfCredits'] = st.text_input(f"KYC No. of Credits", value=st.session_state.analysis_data[i].get('KYCNoOfCredits', '3-5') if i < len(st.session_state.analysis_data) else '3-5', key=f"analysis_kyc_credits_{i}")
                    alert_data['KYCNoOfDebits'] = st.text_input(f"KYC No. of Debits", value=st.session_state.analysis_data[i].get('KYCNoOfDebits', '8-12') if i < len(st.session_state.analysis_data) else '8-12', key=f"analysis_kyc_debits_{i}")
                    alert_data['KYCRiskCategoryValue'] = st.selectbox(f"KYC Risk Category", ['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'].index(st.session_state.analysis_data[i].get('KYCRiskCategoryValue', 'Low')) if i < len(st.session_state.analysis_data) and st.session_state.analysis_data[i].get('KYCRiskCategoryValue') in ['Low', 'Medium', 'High'] else 0, key=f"analysis_kyc_risk_{i}")
                with col2:
                    alert_data['KYCValueOfCredits'] = st.text_input(f"KYC Value of Credits", value=st.session_state.analysis_data[i].get('KYCValueOfCredits', '150,000 - 200,000 PKR') if i < len(st.session_state.analysis_data) else '150,000 - 200,000 PKR', key=f"analysis_kyc_val_credits_{i}")
                    alert_data['KYCValueOfDebits'] = st.text_input(f"KYC Value of Debits", value=st.session_state.analysis_data[i].get('KYCValueOfDebits', '80,000 - 120,000 PKR') if i < len(st.session_state.analysis_data) else '80,000 - 120,000 PKR', key=f"analysis_kyc_val_debits_{i}")
                    alert_data['OccupationValue'] = st.text_input(f"Occupation", value=st.session_state.analysis_data[i].get('OccupationValue', 'Private Employee') if i < len(st.session_state.analysis_data) else 'Private Employee', key=f"analysis_occupation_{i}")
                    alert_data['STRCount'] = st.number_input(f"STR Count", value=st.session_state.analysis_data[i].get('STRCount', 0) if i < len(st.session_state.analysis_data) else 0, key=f"analysis_str_count_{i}")
                
                # Transactions
                st.markdown("#### Transactions")
                alert_data['FilteredTransactions'] = st.text_area(f"Filtered Transactions (JSON array string)", value=st.session_state.analysis_data[i].get('FilteredTransactions', '[]') if i < len(st.session_state.analysis_data) else '[]', key=f"analysis_transactions_{i}", height=150)
                
                # Additional fields
                st.markdown("#### Additional Information")
                alert_data['STRScenarioHistory'] = st.text_input(f"STR Scenario History", value=st.session_state.analysis_data[i].get('STRScenarioHistory', '') if i < len(st.session_state.analysis_data) else '', key=f"analysis_str_history_{i}")
                alert_data['CreatedDate'] = st.text_input(f"Created Date", value=st.session_state.analysis_data[i].get('CreatedDate', '2020-01-15') if i < len(st.session_state.analysis_data) else '2020-01-15', key=f"analysis_created_date_{i}")
                alert_data['RelationshipStartDate'] = st.text_input(f"Relationship Start Date", value=st.session_state.analysis_data[i].get('RelationshipStartDate', '2020-01-15') if i < len(st.session_state.analysis_data) else '2020-01-15', key=f"analysis_relationship_date_{i}")
                alert_data['CustomerStatus'] = st.text_input(f"Customer Status", value=st.session_state.analysis_data[i].get('CustomerStatus', 'Retail Customer') if i < len(st.session_state.analysis_data) else 'Retail Customer', key=f"analysis_customer_status_{i}")
                
                # Previous Alerts (JSON editor)
                st.markdown("#### Previous Alerts (JSON)")
                prev_alerts_str = st.text_area(f"Previous Alerts (JSON array)", value=json.dumps(st.session_state.analysis_data[i].get('PreviousAlerts', []), indent=2) if i < len(st.session_state.analysis_data) and st.session_state.analysis_data[i].get('PreviousAlerts') else '[]', key=f"analysis_prev_alerts_{i}", height=100)
                try:
                    alert_data['PreviousAlerts'] = json.loads(prev_alerts_str)
                except:
                    alert_data['PreviousAlerts'] = []
                
                # Counterparties (JSON editor)
                st.markdown("#### Counterparties (JSON)")
                counterparties_str = st.text_area(f"Counterparties (JSON array)", value=json.dumps(st.session_state.analysis_data[i].get('Counterparties', []), indent=2) if i < len(st.session_state.analysis_data) and st.session_state.analysis_data[i].get('Counterparties') else '[]', key=f"analysis_counterparties_{i}", height=100)
                try:
                    alert_data['Counterparties'] = json.loads(counterparties_str)
                except:
                    alert_data['Counterparties'] = []
                
                # Branch Queries (JSON editor)
                st.markdown("#### Branch Queries (JSON)")
                branch_queries_str = st.text_area(f"Branch Queries (JSON object)", value=json.dumps(st.session_state.analysis_data[i].get('BranchQueries', {}), indent=2) if i < len(st.session_state.analysis_data) and st.session_state.analysis_data[i].get('BranchQueries') else '{}', key=f"analysis_branch_queries_{i}", height=100)
                try:
                    alert_data['BranchQueries'] = json.loads(branch_queries_str)
                except:
                    alert_data['BranchQueries'] = {}
                
                alerts_analysis_data.append(alert_data)
        
        # LLM Configuration Flags
        st.markdown("---")
        st.subheader("⚙️ LLM Configuration")
        st.info("Configure the LLM options for analysis generation. Only one LLM option should be enabled at a time.")
        
        col1, col2 = st.columns(2)
        with col1:
            use_cloud = st.checkbox(
                "☁️ Use Cloud LLM (OpenRouter)",
                value=True,
                help="Use OpenRouter API for LLM. Requires OPENROUTER_API_KEY to be configured on the server.",
                key="analysis_cloud"
            )
            llm_on_server = st.checkbox(
                "🌐 Use Remote LLM Server",
                value=False,
                help="Use a remote Ollama server instead of Cloud. Requires URL to be provided.",
                key="analysis_llm_on_server"
            )
        with col2:
            remote_url = st.text_input(
                "🔗 Remote LLM Server URL",
                value="",
                help="URL of remote Ollama server (e.g., http://remote-ollama:11434). Required if 'Use Remote LLM Server' is enabled.",
                key="analysis_remote_url",
                disabled=not st.session_state.get('analysis_llm_on_server', False)
            )
            anonymous = st.checkbox(
                "🔒 Mask PII (Anonymous Mode)",
                value=False,
                help="Mask Personally Identifiable Information in the data. PII values will be masked by keeping first 2 and last 2 characters.",
                key="analysis_anonymous"
            )
        
        # Additional Flags
        st.markdown("---")
        st.subheader("🔧 Advanced Options")
        col1, col2 = st.columns(2)
        with col1:
            audit = st.checkbox(
                "🔍 Audit Mode",
                value=False,
                help="Use a thinking model for generation and include 'thinking' reasoning in the response. Cloud: uses OPENROUTER_THINKING_MODEL, Local: uses OLLAMA_THINKING_MODEL.",
                key="analysis_audit"
            )
        with col2:
            evaluation = st.checkbox(
                "✅ Evaluation Mode",
                value=False,
                help="Evaluate the generated analysis and fix mistakes using an evaluator agent. Works with both Cloud and Local/Remote LLM.",
                key="analysis_evaluation"
            )
        
        # Show warning if multiple LLM options are selected
        if use_cloud and llm_on_server:
            st.warning("⚠️ Multiple LLM options selected. Priority: Cloud > Remote Server")
        
        # Show info if neither is selected (defaults to Cloud)
        if not use_cloud and not llm_on_server:
            st.info("ℹ️ Defaulting to Cloud LLM mode (OpenRouter)")
            use_cloud = True
        
        # Call API button
        if st.button("🚀 Generate AML Analysis", type="primary", key="call_analysis_api"):
            # Get API base URL from sidebar (stored in session state)
            api_url = st.session_state.get('api_base_url', DEFAULT_API_BASE_URL)
            with st.spinner("Generating AML analysis... This may take a few moments."):
                result = call_analysis_api(
                    alerts_analysis_data, 
                    api_url,
                    cloud=use_cloud,
                    llm_on_server=llm_on_server,
                    url=remote_url,
                    anonymous=anonymous,
                    audit=audit,
                    evaluation=evaluation
                )
                st.session_state.analysis_result = result
        
        # Display results
        if 'analysis_result' in st.session_state:
            st.markdown("---")
            st.subheader("📈 Results")
            display_analysis_result(st.session_state.analysis_result)

if __name__ == "__main__":
    main()
