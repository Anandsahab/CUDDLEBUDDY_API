$body = @{
    first_name = 'Test'
    last_name = 'User'
    email = 'test@example.com'
    address = '123 Test St'
    postal_code = '12345'
    city = 'Test City'
    total_price = 100.00
    payment_method = 'Cash on Delivery'
    items = @(
        @{
            product_name = 'Test Product'
            price = 100.0
            quantity = 1
        }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri http://127.0.0.1:5000/api/orders -Method Post -Body $body -ContentType 'application/json' | Select-Object -ExpandProperty Content 