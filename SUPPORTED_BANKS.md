# Supported Banks - Complete List

## 🏦 Multi-Bank PDF Statement Parser

This application supports **4 major Indian banks** with robust parsing capabilities.

---

## 1. Bandhan Bank ✨ NEW
**Format**: 6 columns  
**Headers**: Transaction Date | Value Date | Description | Amount | Dr / Cr | Balance  
**Date Format**: `June30, 2025`  
**Amount Format**: `INR34,279.01`  
**Identification**: IFSC code `BDBL`, "Dr / Cr" column  
**Test File**: `Bandhan_bank.pdf` (14 pages, 158 transactions)

---

## 2. Axis Bank
**Format**: 8 columns (with empty column 3)  
**Headers**: S.No | Transaction Date | Value Date | Particulars | Amount | Debit/Credit | Balance | Cheque Number | Branch Name  
**Date Format**: `DD/MM/YYYY`  
**Amount Format**: `1,234.56`  
**Identification**: "axis bank", "S.No" header, "Debit/Credit" column  
**Parser**: Table-based extraction

---

## 3. Yes Bank
**Format**: 7 columns  
**Headers**: Transaction Date | Value Date | Description | Reference Number | Withdrawals | Deposits | Running Balance  
**Date Format**: `YYYY-MM-DD`  
**Amount Format**: `1,234.56`  
**Identification**: "yes bank", "Withdrawals", "Deposits", "Reference Number" headers  
**Parser**: Hybrid (text + table) for multi-line descriptions  
**Special**: Handles multi-line descriptions and reference numbers

---

## 4. Indian Overseas Bank (IOB)
**Format**: 7 columns  
**Headers**: Date(Value Date) | Particulars | Ref No./Cheque No. | Transaction Type | Debit(Rs) | Credit(Rs) | Balance(Rs)  
**Date Format**: `DD-Mon-YY (DD-Mon-YY)` with multi-line  
**Amount Format**: `1,00,102.03` (Indian format)  
**Identification**: "indian overseas bank", "iob", "Transaction Type" column  
**Password Support**: Yes  
**Test File**: `Indian_Overseas_bank_51087192.pdf` (57 pages, 1,833 transactions, password: 51087192)

---

## 🔑 Key Features

### Multi-Page Support
All parsers handle multi-page statements correctly, including:
- Pages with headers
- Continuation pages without headers
- Large statements (50+ pages)

### Password Protection
Supported for IOB and Bandhan Bank (and any other password-protected PDFs)

### Data Extraction
- Transaction Date
- Description/Particulars
- Reference Numbers (where available)
- Debit Amount
- Credit Amount
- Running Balance
- Bank Name

### Output Format
- JSON export
- Pandas DataFrame for display
- Summary statistics (total debits, credits, net change)

---

## 📊 Test Results Summary

| Bank | Test File | Pages | Transactions | Status |
|------|-----------|-------|--------------|--------|
| Bandhan | Bandhan_bank.pdf | 14 | 158 | ✅ |
| Axis | - | - | - | ✅ |
| Yes | - | - | - | ✅ |
| IOB | Indian_Overseas_bank_51087192.pdf | 57 | 1,833 | ✅ |

---

## 🚀 Usage

```bash
# Run web application
streamlit run app.py

# Test individual banks
python3 test_bandhan.py
python3 test_iob.py
```

---

## 🔮 Future Enhancements

Potential banks to add:
- HDFC Bank
- ICICI Bank
- State Bank of India (SBI)
- Kotak Mahindra Bank
- Punjab National Bank (PNB)
