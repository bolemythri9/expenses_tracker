import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

FILE_NAME = "expenses.json"

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Education",
    "Entertainment",
    "Health",
    "Travel",
    "Other"
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking"
]


# --------------------------------------------------
# JSON FILE FUNCTIONS
# --------------------------------------------------

def initialize_file():
    """Create expenses.json if it does not exist."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as file:
            json.dump([], file, indent=4)


def load_expenses():
    """Read expenses from JSON file."""
    initialize_file()

    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_expenses(expenses):
    """Save expenses to JSON file."""
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_next_id(expenses):
    """Generate a new unique expense ID."""
    if not expenses:
        return 1

    return max(expense["id"] for expense in expenses) + 1


def validate_expense(expense):
    """Validate expense input."""

    if not expense["date"]:
        return "Please select a date."

    if not expense["category"]:
        return "Please select a category."

    if not expense["description"].strip():
        return "Description cannot be empty."

    if expense["amount"] <= 0:
        return "Amount must be greater than 0."

    if not expense["payment_method"]:
        return "Please select a payment method."

    return None


def refresh_data():
    """Reload data from JSON file."""
    st.session_state.expenses = load_expenses()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("💰 Expense Tracker")
st.write("Track, manage and analyze your daily expenses.")

st.divider()


# --------------------------------------------------
# SIDEBAR - ADD EXPENSE
# --------------------------------------------------

with st.sidebar:

    st.header("➕ Add Expense")

    expense_date = st.date_input(
        "Date",
        value=date.today()
    )

    category = st.selectbox(
        "Category",
        CATEGORIES
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch at college"
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=10.0,
        format="%.2f"
    )

    payment_method = st.selectbox(
        "Payment Method",
        PAYMENT_METHODS
    )

    if st.button(
        "Add Expense",
        type="primary",
        use_container_width=True
    ):

        new_expense = {
            "id": get_next_id(st.session_state.expenses),
            "date": expense_date.strftime("%Y-%m-%d"),
            "category": category,
            "description": description.strip(),
            "amount": amount,
            "payment_method": payment_method
        }

        error = validate_expense(new_expense)

        if error:
            st.error(error)

        else:
            st.session_state.expenses.append(new_expense)

            save_expenses(st.session_state.expenses)

            st.success("Expense added successfully!")

            st.rerun()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

expenses = st.session_state.expenses


# --------------------------------------------------
# SUMMARY SECTION
# --------------------------------------------------

st.subheader("📊 Expense Summary")

if expenses:

    total_expenses = sum(
        expense["amount"] for expense in expenses
    )

    number_of_expenses = len(expenses)

    highest_expense = max(
        expense["amount"] for expense in expenses
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Total Expenses",
            f"₹{total_expenses:,.2f}"
        )

    with col2:
        st.metric(
            "🧾 Number of Expenses",
            number_of_expenses
        )

    with col3:
        st.metric(
            "📈 Highest Expense",
            f"₹{highest_expense:,.2f}"
        )

else:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💰 Total Expenses", "₹0.00")

    with col2:
        st.metric("🧾 Number of Expenses", 0)

    with col3:
        st.metric("📈 Highest Expense", "₹0.00")


st.divider()


# --------------------------------------------------
# EXPENSE TABLE
# --------------------------------------------------

st.subheader("📋 All Expenses")

if not expenses:

    st.info(
        "No expenses added yet. Add your first expense using the sidebar."
    )

else:

    # Convert JSON data into DataFrame
    df = pd.DataFrame(expenses)

    # Display columns
    display_df = df[
        [
            "id",
            "date",
            "category",
            "description",
            "amount",
            "payment_method"
        ]
    ].copy()

    display_df.columns = [
        "ID",
        "Date",
        "Category",
        "Description",
        "Amount (₹)",
        "Payment Method"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# UPDATE / DELETE SECTION
# --------------------------------------------------

if expenses:

    st.divider()

    st.subheader("✏️ Manage Expenses")

    expense_ids = [
        expense["id"]
        for expense in expenses
    ]

    selected_id = st.selectbox(
        "Select an expense",
        expense_ids,
        format_func=lambda x: (
            f"ID {x} - "
            f"{next(
                e['description']
                for e in expenses
                if e['id'] == x
            )}"
        )
    )

    selected_expense = next(
        expense
        for expense in expenses
        if expense["id"] == selected_id
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    with col1:

        st.markdown("### ✏️ Update Expense")

        edit_date = st.date_input(
            "Date",
            value=pd.to_datetime(
                selected_expense["date"]
            ).date(),
            key="edit_date"
        )

        edit_category = st.selectbox(
            "Category",
            CATEGORIES,
            index=CATEGORIES.index(
                selected_expense["category"]
            ),
            key="edit_category"
        )

        edit_description = st.text_input(
            "Description",
            value=selected_expense["description"],
            key="edit_description"
        )

        edit_amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=float(selected_expense["amount"]),
            step=10.0,
            format="%.2f",
            key="edit_amount"
        )

        edit_payment = st.selectbox(
            "Payment Method",
            PAYMENT_METHODS,
            index=PAYMENT_METHODS.index(
                selected_expense["payment_method"]
            ),
            key="edit_payment"
        )

        if st.button(
            "💾 Update Expense",
            type="primary",
            use_container_width=True
        ):

            updated_expense = {
                "id": selected_id,
                "date": edit_date.strftime("%Y-%m-%d"),
                "category": edit_category,
                "description": edit_description.strip(),
                "amount": edit_amount,
                "payment_method": edit_payment
            }

            error = validate_expense(updated_expense)

            if error:
                st.error(error)

            else:

                for index, expense in enumerate(
                    st.session_state.expenses
                ):

                    if expense["id"] == selected_id:

                        st.session_state.expenses[index] = (
                            updated_expense
                        )

                        break

                save_expenses(
                    st.session_state.expenses
                )

                st.success(
                    "Expense updated successfully!"
                )

                st.rerun()

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    with col2:

        st.markdown("### 🗑️ Delete Expense")

        st.write(
            f"**Selected:** "
            f"{selected_expense['description']}"
        )

        st.write(
            f"**Amount:** "
            f"₹{selected_expense['amount']:,.2f}"
        )

        st.warning(
            "Deleting an expense cannot be undone."
        )

        if st.button(
            "🗑️ Delete Expense",
            use_container_width=True
        ):

            st.session_state.expenses = [
                expense
                for expense in st.session_state.expenses
                if expense["id"] != selected_id
            ]

            save_expenses(
                st.session_state.expenses
            )

            st.success(
                "Expense deleted successfully!"
            )

            st.rerun()


# --------------------------------------------------
# VISUALIZATIONS
# --------------------------------------------------

if expenses:

    st.divider()

    st.subheader("📈 Expense Analytics")

    chart_df = pd.DataFrame(expenses)

    chart_df["date"] = pd.to_datetime(
        chart_df["date"]
    )

    # --------------------------------------------------
    # CATEGORY CHART
    # --------------------------------------------------

    st.markdown("### 🏷️ Expenses by Category")

    category_data = (
        chart_df
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_data)

    # --------------------------------------------------
    # TIME CHART
    # --------------------------------------------------

    st.markdown("### 📅 Expenses Over Time")

    time_data = (
        chart_df
        .groupby("date")["amount"]
        .sum()
        .sort_index()
    )

    st.line_chart(time_data)

    # --------------------------------------------------
    # PAYMENT METHOD CHART
    # --------------------------------------------------

    st.markdown("### 💳 Payment Method Distribution")

    payment_data = (
        chart_df
        .groupby("payment_method")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(payment_data)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "💰 Expense Tracker | Built with Python, Streamlit and JSON"
)