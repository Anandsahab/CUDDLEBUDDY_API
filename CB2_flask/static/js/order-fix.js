// Direct checkout fix script
(function() {
    console.log("Order fix script loaded");
    
    // Get cart items from the order summary
    function getCartItems() {
        const items = [];
        const cart = document.querySelector(".order-summary, .cart-summary");
        
        if (cart) {
            // Try to find item rows
            const rows = cart.querySelectorAll(".item-row, tr:not(:first-child)");
            
            rows.forEach(row => {
                try {
                    let productName, price, quantity;
                    
                    // First try with explicit classes
                    const nameEl = row.querySelector(".product-name");
                    const priceEl = row.querySelector(".price");
                    const quantityEl = row.querySelector(".quantity");
                    
                    if (nameEl && priceEl && quantityEl) {
                        productName = nameEl.textContent.trim();
                        price = parseFloat(priceEl.textContent.replace(/[^0-9.]/g, ""));
                        quantity = parseInt(quantityEl.textContent.trim());
                    } else {
                        // Try table cells
                        const cells = row.querySelectorAll("td");
                        if (cells.length >= 3) {
                            productName = cells[0].textContent.trim();
                            price = parseFloat(cells[1].textContent.replace(/[^0-9.]/g, ""));
                            quantity = parseInt(cells[2].textContent.trim());
                        }
                    }
                    
                    if (productName && !isNaN(price) && !isNaN(quantity)) {
                        items.push({
                            product_name: productName,
                            price: price,
                            quantity: quantity
                        });
                        console.log(`Added item: ${productName}, ${price}, ${quantity}`);
                    }
                } catch (err) {
                    console.error("Error parsing cart item:", err);
                }
            });
        }
        
        // Get total price
        let totalPrice = 0;
        const totalEl = document.querySelector(".total, .order-total, .cart-total");
        if (totalEl) {
            totalPrice = parseFloat(totalEl.textContent.replace(/[^0-9.]/g, ""));
        } else {
            // Calculate from items
            totalPrice = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        }
        
        return {
            items: items,
            totalPrice: totalPrice
        };
    }
    
    // Submit order to API
    function submitOrder(formData) {
        const cart = getCartItems();
        
        // Prepare order data
        const orderData = {
            first_name: formData.get("first_name") || "",
            last_name: formData.get("last_name") || "",
            email: formData.get("email") || "",
            address: formData.get("address") || "",
            postal_code: formData.get("postal_code") || "",
            city: formData.get("city") || "",
            total_price: cart.totalPrice,
            payment_method: document.querySelector('input[name="payment_method"]:checked')?.value || "Cash on Delivery",
            items: cart.items
        };
        
        console.log("Submitting order:", orderData);
        
        // Submit to API
        fetch("http://127.0.0.1:5000/api/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(orderData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not OK");
            }
            return response.json();
        })
        .then(data => {
            console.log("Order submitted successfully:", data);
            
            // Create receipt HTML
            const receiptHTML = `
                <div class="container py-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card border-success">
                                <div class="card-body text-center">
                                    <div class="mb-4">
                                        <i class="fas fa-check-circle text-success" style="font-size: 4rem;"></i>
                                    </div>
                                    <h1 class="card-title mb-4 text-success">Thank You for Your Order!</h1>
                                    <p class="lead mb-4">Your order has been successfully placed and is being processed.</p>
                                    
                                    <div class="order-details bg-light p-4 rounded mb-4 text-start">
                                        <h3 class="mb-3">Order Details</h3>
                                        <p><strong>Order Number:</strong> #${data.order_id}</p>
                                        <p><strong>Order Date:</strong> ${new Date().toLocaleString()}</p>
                                        <p><strong>Total Amount:</strong> ₹${cart.totalPrice.toFixed(2)}</p>
                                        
                                        <h4 class="mt-4 mb-3">Shipping Information</h4>
                                        <p><strong>Name:</strong> ${orderData.first_name} ${orderData.last_name}</p>
                                        <p><strong>Address:</strong> ${orderData.address}</p>
                                        <p><strong>City:</strong> ${orderData.city}</p>
                                        <p><strong>Postal Code:</strong> ${orderData.postal_code}</p>
                                    </div>
                                    
                                    <a href="/" class="btn btn-primary">Return to Home</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Replace page content with receipt
            document.body.innerHTML = receiptHTML;
            document.title = "Order Confirmation";
        })
        .catch(error => {
            console.error("Error submitting order:", error);
            alert("There was an error processing your order. Please try again.");
        });
    }
    
    // Fix the checkout form
    const checkoutForm = document.getElementById("checkout-form");
    if (checkoutForm) {
        console.log("Found checkout form, fixing it");
        
        // Remove warning message
        const warning = document.querySelector(".alert-warning");
        if (warning) {
            warning.style.display = "none";
        }
        
        // Enable submit button
        const submitBtn = checkoutForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
        }
        
        // Override form submission
        checkoutForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(checkoutForm);
            
            // Submit order
            submitOrder(formData);
        });
        
        console.log("Checkout form fixed successfully");
    } else {
        console.error("Checkout form not found");
    }
})(); 