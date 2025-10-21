from enum import Enum

class ImportProfileMappingDestinationColumns(Enum):
    # name = value
    # The value is used both for displaying and for what should be saved in the database.
    NAME = "Name"
    DESCRIPTION = "Description"
    TRANSACTION_DATE = "Transaction Date"
    REFERENCE = "Reference"
    BUSINESS_ENTITY_NAME = "Business Entity Name"
    AMOUNT = "Amount"
    CURRENCY = "Currency"
    CATEGORY = "Category"

def text_to_enum_destination_column(text_value: str):
    """Convert text like 'NAME' to enum member"""
    try:
        return ImportProfileMappingDestinationColumns[text_value]  # Uses the name (NAME)
    except KeyError:
        # Fallback: try to find by value if needed
        for member in ImportProfileMappingDestinationColumns:
            if member.value == text_value:
                return member
        raise ValueError(f"Unknown option: {text_value}")