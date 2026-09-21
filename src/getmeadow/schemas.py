from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, Field


class AWSDocumentRequest(BaseModel):
    type: str
    file_name: str = Field(..., alias="fileName")
    file_type: str = Field(..., alias="fileType")


class MeadowNewDocument(BaseModel):
    document_type_id: int = Field(..., alias="documentTypeId")
    path: str
    mime: str


class NewUser(BaseModel):
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: Optional[str]
    phone: str


class Payment(BaseModel):
    payment_type_id: int = Field(..., alias="paymentTypeId")
    remaining: bool = True


class LineItem(BaseModel):
    product_id: int = Field(..., alias="productId")
    product_option_id: int = Field(..., alias="productOptionId")
    quantity: Optional[int] = None
    remove_discount_ids: List[Any] = Field(default_factory=list, alias="removeDiscountIds")
    add_discount_ids: List[int] = Field(default_factory=list, alias="addDiscountIds")
    custom_discounts: List[Any] = Field(default_factory=list, alias="customDiscounts")


class Address(BaseModel):
    street1: str
    street2: Optional[str] = None
    city: str
    state: str
    postal_code: str = Field(..., alias="postalCode")
    county: Optional[str] = None

class LatLng(BaseModel):
    lat: float
    lng: float


class Order(BaseModel):
    type: Literal["delivery", "in-store"]
    payments: List[Payment]
    adjustments: List[Any] = []
    add_discount_ids: List[Any] = Field(default_factory=list, alias="addDiscountIds")
    discount_codes: List[Any] = Field(default_factory=list, alias="discountCodes")
    discount_limits: Dict[Any, Any] = Field(default_factory=dict, alias="discountLimits")
    remove_discount_ids: List[Any] = Field(default_factory=list, alias="removeDiscountIds")
    remove_discount_instances: Dict[Any, Any] = Field(default_factory=dict, alias="removeDiscountInstances")
    admin_notes: Optional[str] = Field(None, alias="adminNotes")

    #discounts: List[Any] = []
    delivery_zone_id: Optional[int] = Field(None, alias="deliveryZoneId")
    line_items: List[LineItem] = Field(..., alias="lineItems")
    patient_hash: str = Field(..., alias="patientHash")
    status: Optional[str]
    source: str = 'web-admin'
    is_admin: bool = Field(True, alias="isAdmin")
    tax_exempt: bool = Field(False, alias="taxExempt")
    inventory_location_id: Any = Field(None, alias="inventoryLocationId")
    address: Optional[Address] = None

class Option(BaseModel):
    amount: int | float = 1
    content: Optional[str] = None
    name: str = ''
    weedmaps_v2_verified_variant: Optional[Any] = Field(None, alias="weedmapsV2VerifiedVariant")
    price: int | float
    sales_price: Optional[Any] = Field(..., alias="salesPrice")
    id: Optional[Any] = None

class Product(BaseModel):
    name: str
    strain_type: str = Field(..., alias="strainType")
    category: str
    weedmaps_category_id: Optional[int] = Field(default=None, alias='weedmapsCategoryId')
    sub_categories: List[Any] = Field(default_factory=list, alias="subCategories")
    tags: List[Any] = Field(default_factory=list, alias="tags")
    compounds: Optional[Dict[Any, Any]] = Field(default_factory=dict, alias="compounds")
    unit: str
    brand_id: Optional[int] = Field(None, alias="brandId")
    sales_price_unit: Optional[Any] = Field(None, alias='salesPriceUnit')
    description: str = ''
    is_active: bool = Field(..., alias="isActive")
    is_featured: bool = Field(..., alias="isFeatured")
    options: Optional[List[Option]] = Field(default_factory=list, alias="options")
    pricing_tier_id: Optional[Any] = Field(None, alias='pricingTierId')
    pricing_type: Optional[str] = Field(None, alias="pricingType")
    photos: Optional[List[Any]] = Field(default_factory=list, alias="photos")
    auto_import_compounds: Optional[Any] = Field(None, alias="autoImportCompounds")


class ReconciliationLineItem(BaseModel):
    amount: int
    operation: str
    package_id: Optional[Any] = Field(None, alias="packageId")
    product_id: int = Field(..., alias="productId")
    product_option_id: int = Field(..., alias="productOptionId")

class Reconciliation(BaseModel):
    inventory_location_id: int = Field(..., alias="inventoryLocationId")
    line_items: List[ReconciliationLineItem] = Field(default_factory=list, alias="lineItems")
    notes: str
    compliance_notes: str = Field(..., alias="complianceNotes")
    compliance_reason: str = Field(..., alias="complianceReason")

class PurchaseOrder(BaseModel):
    id: Optional[int]
    organization_id: int
    user_id: int = Field(..., alias="userId")
    total_amount: str = Field(..., alias="totalAmount")
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    inventory_vendor_id: int = Field(..., alias="inventoryVendorId")
    notes: Optional[Any] = None
    subtotal: int
    expected_at: str = Field(..., alias="expectedAt")
    status: str
    payment_status: str = Field(..., alias="paymentStatus")
    payment_terms: Optional[Any] = Field(None, alias="paymentTerms")
    payment_terms_due_date: Optional[Any] = Field(None, alias="paymentTermsDueDate")
    total_amount_received: str = Field(..., alias="totalAmountReceived")
    final_total: int = Field(..., alias="finalTotal")
    ca_excise_total: int = Field(..., alias="caExciseTotal")
    amount_paid: int = Field(..., alias="amountPaid")
    amount_outstanding: int = Field(..., alias="amountOutstanding")
    external_invoice_number: str = Field(..., alias="externalInvoiceNumber")
    external_invoice_file_path: Optional[str] = Field(None, alias="externalInvoiceFilePath")
    shipping_handling_fee: int = Field(..., alias="shippingHandlingFee")
    shipping_handling_fee_excise: int = Field(..., alias="shippingHandlingFeeExcise")
    api_consumer_id: Optional[Any] = Field(None, alias="apiConsumerId")
    is_overdue: bool = Field(..., alias="isOverdue")
    inventory_vendor: Optional[Any] = Field(None, alias="inventoryVendor")
    line_items: List[LineItem] = Field(default_factory=list, alias="lineItems")


class ReceiveLineItem(BaseModel):
    amount: int
    purchase_order_line_item_id: int = Field(..., alias="purchaseOrderLineItemId")
    package_id: Optional[int] = Field(..., alias="packageId")
    expirationDate: Optional[str] = Field(..., alias="expirationDate")
    multiplier: Optional[str] = Field(..., alias="multiplier")
    thcPercent: Optional[str] = Field(..., alias="thcPercent")
    thcMg: Optional[str] = Field(None, alias="thcMg")
    cbdPercent: Optional[str] = Field(None, alias="cbdPercent")
    cbdMg: Optional[str] = Field(None, alias="cbdMg")
    producerName: str = Field(..., alias="producerName")
    producerLicense: str = Field(..., alias="producerLicense")
    harvestDate: Optional[str] = Field(None, alias="harvestDate")
    harvestFacilityName: Optional[str] = Field(None, alias="harvestFacilityName")
    itemStrain: Optional[str] = Field(..., alias="itemStrain")
    labName: Optional[str] = Field(None, alias="labName")
    labDate: Optional[str] = Field(None, alias="labDate")




class CreatePurchaseOrderLineItem(BaseModel):
    product_id: int = Field(..., alias="productId")
    product_option_id: int = Field(..., alias="productOptionId")
    amount: int
    cost_per_unit: str = Field(..., alias="costPerUnit")
    ca_excise_per_unit: int = Field(0, alias="caExcisePerUnit")
    ca_excise_override: Optional[bool] = Field(False, alias="caExciseOverride")
    tmp_id: Optional[str] = Field(None, alias="tmpId")
    compliance_item_name: Optional[str] = Field(None, alias="complianceItemName")


class UpdatePurchaseOrderLineItem(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    product_id: int = Field(..., alias="productId")
    product_option_id: int = Field(..., alias="productOptionId")
    amount: int
    cost_per_unit: str = Field(..., alias="costPerUnit")
    ca_excise_per_unit: int = Field(0, alias="caExcisePerUnit")
    ca_excise_override: Optional[bool] = Field(False, alias="caExciseOverride")
    tmp_id: Optional[str] = Field(None, alias="tmpId")
    compliance_item_name: Optional[str] = Field(None, alias="complianceItemName")


class Insight(BaseModel):
    labels: list[str]
    datasets: list[dict]
    query_totals: dict = Field(..., alias="queryTotals")
