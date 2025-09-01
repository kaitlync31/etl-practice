ontology = {
    # Fill in fields and relationships for each entity in data
    'customers':{
        'fields': ['customer_id', 'name', 'email', 'signup_date', 'gender'],
        'relationships': {'makes': 'orders'},
    },
    'order_items':{
        'fields': ['order_item_id', 'order_id', 'product_id', 'quantity', 'unit_price'],
        'relationships': {'in_order': 'orders', 'includes': 'products'},
    },
    'orders':{
        'fields': ['order_id', 'customer_id', 'order_date', 'total_amount'],
        'relationships': {'placed_by': 'customers', 'contains': 'order_items'},
    },
    'products':{
        'fields': ['product_id', 'name', 'category', 'price'],
        'relationships': {'in_order_item': 'order_items'}
    },
}