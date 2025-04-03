import joblib

# Define features and weights
features = [
    "TotalDebtToIncomeRatio", "BankruptcyHistory", "DebtToIncomeRatio",
    "NetWorth", "MonthlyIncome", "InterestRate", "PreviousLoanDefaults",
    "AnnualIncome", "CreditScore", "LengthOfCreditHistory"
]

weights = {
    "TotalDebtToIncomeRatio": 1.83,
    "BankruptcyHistory": 13.22,
    "DebtToIncomeRatio": 15.54,
    "NetWorth": -0.00002,
    "MonthlyIncome": -0.000849,
    "InterestRate": 33.39,
    "PreviousLoanDefaults": 6.76,
    "AnnualIncome": -0.000014,
    "CreditScore": -0.01187,
    "LengthOfCreditHistory": -0.17
}
intercept = 51.97
threshold = 50

# Save the model
model_data = {"features": features, "weights": weights, "intercept": intercept, "threshold": threshold}
joblib.dump(model_data, "risk_score_model.pkl")
print("Model saved successfully!")
