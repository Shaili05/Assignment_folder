// ============================================
// script.js - Product Inventory Dashboard
// Written by: [Your Name]
// ============================================


// ---- DEFAULT PRODUCTS ----
// used only when localStorage has nothing stored yet
const defaultProducts = [
    { id: 1, name: "Smart Mirror Display", price: 18000, stock: 3, category: "electronics" },
    { id: 2, name: "LED Backpack Panel", price: 4200, stock: 6, category: "accessories" },
    { id: 3, name: "Classmate Notebook", price: 250, stock: 4, category: "books" },
    { id: 4, name: "Temperature Control Mug", price: 3200, stock: 2, category: "accessories" },
    { id: 5, name: "Foldable Bluetooth Keyboard", price: 2100, stock: 5, category: "electronics" },
    { id: 6, name: "Hoodie", price: 1800, stock: 7, category: "clothing" },
    { id: 7, name: "Productivity Planner 2.0", price: 899, stock: 10, category: "books" },
    { id: 8, name: "Digital Drawing Tablet Mini", price: 3500, stock: 3, category: "electronics" },
    { id: 9, name: "Portable Monitor 13-inch", price: 12500, stock: 2, category: "electronics" },
    { id: 10, name: "Smart Water Bottle Reminder", price: 1500, stock: 8, category: "accessories" }
];// ---- STATE ----
// these variables hold the current state of the app
let allProducts = [];       // full list (loaded from storage or defaults)
let filteredProducts = [];  // list after filters/search applied
let currentPage = 1;
const ITEMS_PER_PAGE = 6;  // how many cards per page


// ============================================
// SIMULATED API FETCH (Promise + setTimeout)
// mimics how a real backend call would work
// ============================================
function fetchProducts() {
    return new Promise(function(resolve) {
        setTimeout(function() {
            // check if user already has products saved in localStorage
            const saved = localStorage.getItem("inventoryProducts");
            if (saved) {
                resolve(JSON.parse(saved));
            } else {
                resolve(defaultProducts);
            }
        }, 1500); // 1.5 second delay to simulate server response
    });
}


// ============================================
// LOCALSTORAGE HELPER
// ============================================
function saveToStorage() {
    localStorage.setItem("inventoryProducts", JSON.stringify(allProducts));
}


// ============================================
// ANALYTICS UPDATE
// recalculates whenever products change
// ============================================
function updateAnalytics() {
    const total = allProducts.length;

    // add up price * stock for each product to get inventory value
    const totalVal = allProducts.reduce(function(sum, p) {
        return sum + (p.price * p.stock);
    }, 0);

    // count products where stock is exactly 0
    const outOfStockCount = allProducts.filter(function(p) {
        return p.stock === 0;
    }).length;

    document.getElementById("totalProducts").textContent = total;
    document.getElementById("totalValue").textContent = "₹" + totalVal.toLocaleString("en-IN");
    document.getElementById("outOfStock").textContent = outOfStockCount;
}


// ============================================
// FILTERING + SORTING LOGIC
// called every time a filter/search changes
// ============================================
function applyFiltersAndSort() {
    const searchVal = document.getElementById("searchInput").value.toLowerCase().trim();
    const selectedCategory = document.getElementById("categoryFilter").value;
    const sortOption = document.getElementById("sortFilter").value;
    const showLowStock = document.getElementById("lowStockFilter").checked;

    // start with all products, then narrow down
    let result = [...allProducts];

    // search by name (case insensitive)
    if (searchVal !== "") {
        result = result.filter(function(p) {
            return p.name.toLowerCase().includes(searchVal);
        });
    }

    // filter by category
    if (selectedCategory !== "all") {
        result = result.filter(function(p) {
            return p.category === selectedCategory;
        });
    }

    // low stock filter: show only if qty < 5
    if (showLowStock) {
        result = result.filter(function(p) {
            return p.stock < 5;
        });
    }

    // sorting
    if (sortOption === "price-asc") {
        result.sort(function(a, b) { return a.price - b.price; });
    } else if (sortOption === "price-desc") {
        result.sort(function(a, b) { return b.price - a.price; });
    } else if (sortOption === "name-asc") {
        result.sort(function(a, b) { return a.name.localeCompare(b.name); });
    } else if (sortOption === "name-desc") {
        result.sort(function(a, b) { return b.name.localeCompare(a.name); });
    }

    filteredProducts = result;
    currentPage = 1; // reset to page 1 whenever filters change
    renderProducts();
    renderPagination();
}


// ============================================
// RENDER PRODUCT CARDS
// only shows cards for current page
// ============================================
function renderProducts() {
    const grid = document.getElementById("productGrid");
    const noMsg = document.getElementById("noProductsMsg");
    grid.innerHTML = ""; // clear old cards

    if (filteredProducts.length === 0) {
        noMsg.style.display = "block";
        grid.style.display = "none";
        return;
    }

    noMsg.style.display = "none";
    grid.style.display = "grid";

    // figure out which slice to show based on current page
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const pageItems = filteredProducts.slice(startIndex, endIndex);

    pageItems.forEach(function(product) {
        const card = createProductCard(product);
        grid.appendChild(card);
    });
}


// ============================================
// BUILD ONE PRODUCT CARD (DOM element)
// ============================================
function createProductCard(product) {
    const card = document.createElement("div");
    card.classList.add("product-card");

    // add low-stock class for left border highlight
    if (product.stock < 5) {
        card.classList.add("low-stock");
    }

    // stock badge text
    let stockBadgeHTML = "";
    if (product.stock === 0) {
        stockBadgeHTML = '<span class="stock-badge badge-out">Out of Stock</span>';
    } else if (product.stock < 5) {
        stockBadgeHTML = '<span class="stock-badge badge-low">Low Stock</span>';
    }

    card.innerHTML = `
        <span class="prod-category ${product.category}">
    ${capitalizeFirst(product.category)}
</span>
        <p class="prod-name">${product.name}</p>
        <p class="prod-price">₹${product.price.toLocaleString("en-IN")}</p>
        <p class="prod-stock">Qty: ${product.stock} ${stockBadgeHTML}</p>
        <button class="btn-delete" data-id="${product.id}">🗑 Delete</button>
    `;

    // attach delete event directly on this card's button
    card.querySelector(".btn-delete").addEventListener("click", function() {
        deleteProduct(product.id);
    });

    return card;
}


// ============================================
// PAGINATION RENDERING
// ============================================
function renderPagination() {
    const container = document.getElementById("paginationControls");
    container.innerHTML = "";

    const totalPages = Math.ceil(filteredProducts.length / ITEMS_PER_PAGE);
    if (totalPages <= 1) return; // no pagination needed if only one page

    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement("button");
        btn.classList.add("page-btn");
        btn.textContent = i;

        if (i === currentPage) {
            btn.classList.add("active");
        }

        btn.addEventListener("click", function() {
            currentPage = i;
            renderProducts();
            renderPagination();
        });

        container.appendChild(btn);
    }
}


// ============================================
// DELETE PRODUCT
// ============================================
function deleteProduct(id) {
    // remove from the main array
    allProducts = allProducts.filter(function(p) {
        return p.id !== id;
    });
    saveToStorage();
    updateAnalytics();
    applyFiltersAndSort(); // re-run filters so the grid updates
}


// ============================================
// FORM VALIDATION
// returns true only if everything is valid
// ============================================
function validateForm() {
    let isValid = true;

    const name = document.getElementById("productName").value.trim();
    const price = parseFloat(document.getElementById("productPrice").value);
    const stock = parseInt(document.getElementById("productStock").value);
    const category = document.getElementById("productCategory").value;

    // clear previous errors first
    document.getElementById("nameError").textContent = "";
    document.getElementById("priceError").textContent = "";
    document.getElementById("stockError").textContent = "";
    document.getElementById("categoryError").textContent = "";

    if (name === "") {
        document.getElementById("nameError").textContent = "Product name is required.";
        isValid = false;
    }

    if (isNaN(price) || price <= 0) {
        document.getElementById("priceError").textContent = "Price must be greater than 0.";
        isValid = false;
    }

    if (isNaN(stock) || stock < 0) {
        document.getElementById("stockError").textContent = "Stock cannot be negative.";
        isValid = false;
    }

    if (category === "") {
        document.getElementById("categoryError").textContent = "Please select a category.";
        isValid = false;
    }

    return isValid;
}


// ============================================
// ADD PRODUCT (form submit handler)
// ============================================
function handleAddProduct(e) {
    e.preventDefault();

    if (!validateForm()) return; // stop if validation fails

    const name = document.getElementById("productName").value.trim();
    const price = parseFloat(document.getElementById("productPrice").value);
    const stock = parseInt(document.getElementById("productStock").value);
    const category = document.getElementById("productCategory").value;

    // use Date.now() as a simple unique ID
    const newProduct = {
        id: Date.now(),
        name: name,
        price: price,
        stock: stock,
        category: category
    };

    allProducts.push(newProduct);
    saveToStorage();
    updateAnalytics();
    applyFiltersAndSort();

    // clear form after successful add
    document.getElementById("addProductForm").reset();
}


// ============================================
// HELPER: capitalize first letter
// ============================================
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}


// ============================================
// ATTACH EVENT LISTENERS
// all controls wire up here
// ============================================
function attachEventListeners() {
    document.getElementById("searchInput").addEventListener("input", applyFiltersAndSort);
    document.getElementById("categoryFilter").addEventListener("change", applyFiltersAndSort);
    document.getElementById("sortFilter").addEventListener("change", applyFiltersAndSort);
    document.getElementById("lowStockFilter").addEventListener("change", applyFiltersAndSort);
    document.getElementById("addProductForm").addEventListener("submit", handleAddProduct);
}


// ============================================
// APP INITIALIZATION
// runs when the page first loads
// ============================================
async function initApp() {
    const loadingDiv = document.getElementById("loadingMsg");
    const grid = document.getElementById("productGrid");

    // show loading, hide grid
    loadingDiv.style.display = "flex";
    grid.style.display = "none";

    // simulate API call
    allProducts = await fetchProducts();

    // if localStorage was empty before, save the defaults now
    if (!localStorage.getItem("inventoryProducts")) {
        saveToStorage();
    }

    // done loading - show the grid
    loadingDiv.style.display = "none";

    attachEventListeners();
    updateAnalytics();
    applyFiltersAndSort(); // this also calls renderProducts & renderPagination
}
function setupDarkMode() {
    const toggleBtn = document.getElementById("darkModeToggle");

    // load saved theme
    const isDark = localStorage.getItem("darkMode") === "true";
    if (isDark) {
        document.body.classList.add("dark-mode");
        toggleBtn.textContent = "☀️";
    }

    toggleBtn.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");

        const enabled = document.body.classList.contains("dark-mode");
        localStorage.setItem("darkMode", enabled);

        toggleBtn.textContent = enabled ? "☀️" : "🌙";
    });
}

// kick everything off
initApp();
setupDarkMode();