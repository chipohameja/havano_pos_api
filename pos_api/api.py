import frappe
import json

@frappe.whitelist()
def add_currency(currency_name, fraction="", fraction_units=100, smallest_currency_fraction_value=0, symbol="", number_format="#,###.##"):
    new_currency = frappe.get_doc({
        "doctype": "Currency",
		"currency_name": currency_name,
		"fraction": fraction,
		"fraction_units": fraction_units,
		"smallest_currency_fraction_value": smallest_currency_fraction_value,
		"symbol": symbol,
		"number_format": number_format
	})
    
    new_currency.insert()
    
    return new_currency

@frappe.whitelist()
def get_items(
    fields=[
        "name",
        "item_name",
        "item_code",
        "item_group",
        "stock_uom",
        "disabled",
        "valuation_rate",
        "standard_rate",
        "description",
	], 
    filters=None):
    
    return frappe.get_all("Item", fields=fields, filters=filters)

@frappe.whitelist()
def make_payment(
	posting_date,
	company,
	mode_of_payment,
	party_type,
	party,
	paid_from,
	paid_from_account_currency,
	paid_to,
	paid_to_account_type,
	paid_to_account_currency,
	received_amount,
	reference_name,
	payment_type="Receive",
	paid_from_account_type="Receivable",
	target_exchange_rate=1.00
):
	paid_amount = received_amount * target_exchange_rate
	
	references = [
		{
			"allocated_amount": paid_amount,
			"doctype": "Payment Entry Reference",
			"reference_doctype": "Sales Invoice",
			"reference_name": reference_name
		}
	]

	# default_currency = frappe.db.get_single_value("Global Defaults", "default_currency")
	# exchange_rate = None
	
	# if paid_from_account_currency != paid_to_account_currency:
	# 	exchange_rate_exists = frappe.db.exists("Currency Exchange", {"from_currency": paid_from_account_currency, "to_currency": paid_to_account_currency})
		
	# 	if exchange_rate_exists:
	# 		exchange_rate = frappe.get_last_doc("Currency Exchange", filters={"from_currency": paid_from_account_currency, "to_currency": paid_to_account_currency})
			
	# 		source_exchange_rate = exchange_rate.exchange_rate
			
	new_payment_entry = frappe.get_doc({
		"doctype": "Payment Entry",
		"payment_type": payment_type,
		"posting_date": posting_date,
		"company": company,
		"mode_of_payment": mode_of_payment,
		"party_type": party_type,
		"party": party,
		"paid_from": paid_from,
		"paid_from_account_type": paid_from_account_type,
		"paid_from_account_currency": paid_from_account_currency,
		"paid_to": paid_to,
		"paid_to_account_type": paid_to_account_type,
		"paid_to_account_currency": paid_to_account_currency,
		"paid_amount": paid_amount,
		"received_amount": received_amount,
		"total_allocated_amount": paid_amount,
		"references": references,
		"base_total_allocated_amount": paid_amount,
		"target_exchange_rate": target_exchange_rate
	})

	new_payment_entry.insert()
	new_payment_entry.submit()

	return new_payment_entry

@frappe.whitelist()
def make_sales_invoice(
	selling_price_list,
	price_list_currency,
	plc_conversion_rate,
	items,
	customer, 
	company, 
	currency,
	posting_date,
	set_warehouse,
	due_date,
	conversion_rate=1.00, 
	update_stock=1,
	is_return=0,
	return_against=None,
	):
		
	new_sales_invoice = frappe.get_doc({
		"doctype": "Sales Invoice",
		"selling_price_list": selling_price_list,
		"price_list_currency": price_list_currency,
  		"plc_conversion_rate": plc_conversion_rate,
		"set_warehouse": set_warehouse,
  		"customer": customer,
		"company": company,
		"currency": currency,
		"posting_date": posting_date,
		"conversion_rate": conversion_rate,
		"items": items,
		"update_stock": update_stock,
		"is_return": is_return,
		"due_date": due_date
	})

	if is_return and return_against:
		setattr(new_sales_invoice, "return_against", return_against)

	new_sales_invoice.insert()
	new_sales_invoice.submit()

	return new_sales_invoice
