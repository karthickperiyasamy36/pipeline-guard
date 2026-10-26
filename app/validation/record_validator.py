
import pandas as pd


def validate_sales_records(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separate valid sales records from records requiring review.

    Returns:
        A tuple containing (accepted_records, quarantined_records).

    Rules:
        - Product must not be missing or blank.
        - Quantity and price must not be missing.
        - Quantity and price must be numeric and finite.
        - Price must not be negative.
        - Negative quantity is allowed because it may represent a return.
    """
    required_columns = ["product", "quantity", "price"]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Work on a copy so the input DataFrame is not modified.
    records = dataframe.copy()

    # Store the reason each record needs review.
    reasons = pd.Series("", index=records.index, dtype="object")

    # Check product names.
    product = records["product"].astype("string").str.strip()

    missing_product = product.isna() | product.eq("").fillna(False)
    reasons.loc[missing_product] += "Product is missing or blank; "

    # Convert numeric columns for validation.
    quantity = pd.to_numeric(records["quantity"], errors="coerce")
    price = pd.to_numeric(records["price"], errors="coerce")

    invalid_quantity = quantity.isna()
    invalid_price = price.isna()

    reasons.loc[invalid_quantity] += "Quantity is missing or non-numeric; "
    reasons.loc[invalid_price] += "Price is missing or non-numeric; "

    # Check infinite numeric values.
    finite_quantity = pd.Series(
        quantity.isna() | quantity.isin([float("inf"), float("-inf")]),
        index=records.index,
    )
    finite_price = pd.Series(
        price.isna() | price.isin([float("inf"), float("-inf")]),
        index=records.index,
    )

    infinite_quantity = quantity.isin([float("inf"), float("-inf")])
    infinite_price = price.isin([float("inf"), float("-inf")])

    reasons.loc[infinite_quantity] += "Quantity is infinite; "
    reasons.loc[infinite_price] += "Price is infinite; "

    # Negative prices need review; negative quantities may be returns.
    negative_price = price.lt(0).fillna(False)
    reasons.loc[negative_price] += "Price is negative; "

    # Put converted values into a working copy.
    records["product"] = product
    records["quantity"] = quantity
    records["price"] = price

    # A blank reason means the record passed all checks.
    accepted_mask = reasons.eq("")
    accepted_records = records.loc[accepted_mask].copy()
    quarantined_records = records.loc[~accepted_mask].copy()

    # Explain why each quarantined record was flagged.
    quarantined_records["rejection_reason"] = (
        reasons.loc[~accepted_mask].str.rstrip("; ")
    )

    return accepted_records, quarantined_records
