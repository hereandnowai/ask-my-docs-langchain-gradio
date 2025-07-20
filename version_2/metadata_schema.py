from pydantic import BaseModel, Field
from langchain.chains.query_constructor.base import AttributeInfo

class InvoiceMetadata(BaseModel):
    invoice_date: str = Field(description="The date the invoice was issued, in YYYY-MM-DD format.")
    invoice_number: str = Field(description="The unique identifier for the invoice.")
    total_value: float = Field(description="The total amount of the invoice.")
    vendor_name: str = Field(description="The name of the company that issued the invoice.")

metadata_field_info = [
    AttributeInfo(
        name="invoice_date",
        description="The date the invoice was issued, in YYYY-MM-DD format.",
        type="string",
    ),
    AttributeInfo(
        name="invoice_number",
        description="The unique identifier for the invoice.",
        type="string",
    ),
    AttributeInfo(
        name="total_value",
        description="The total amount of the invoice.",
        type="float",
    ),
    AttributeInfo(
        name="vendor_name",
        description="The name of the company that issued the invoice.",
        type="string",
    ),
]

DOCUMENT_DESCRIPTION = "Scanned invoices and billing statements."
