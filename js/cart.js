const cartBody = document.querySelector(".cart__table_tr");
const cartTotalPrice = document.querySelector(".cart__total-price");
const navQuantity = document.querySelector(".nav__quantity");
const navTotal = document.querySelector(".nav__total");
const basketInfo = document.querySelector(".basket");
const basketMessage = document.querySelector(".basket__message");

let cart = (JSON.parse(localStorage.getItem("CART")) || [])
	.map((saved) => {
		const product = modalProduct.find((item) => item.id === saved.id);
		return product && { ...product, numberOfUnits: saved.numberOfUnits };
	})
	.filter(Boolean);
updateCart();

function addToCart(id) {
	if (cart.some((item) => item.id === id)) {
		basketInfo.classList.add("basket__active");
		basketMessage.textContent = "Item already exists in cart";
		setTimeout(() => {
			basketInfo.classList.remove("basket__active");
		}, 2000);
	} else {
		basketInfo.classList.add("basket__active");
		basketMessage.textContent = "Product successfully added to your cart";
		const item = modalProduct.find((product) => product.id === id);
		cart.push({
			...item,
			numberOfUnits: 1,
		});
		setTimeout(() => {
			basketInfo.classList.remove("basket__active");
		}, 2000);
	}
	updateCart();
}

function updateCart() {
	renderList();
	renderTotal();

	localStorage.setItem("CART", JSON.stringify(cart));
}

function renderTotal() {
	let totalPrice = 0;
	let totalItems = 0;

	cart.forEach((item) => {
		totalPrice += item.price * item.numberOfUnits;
		totalItems += item.numberOfUnits;
	});

	cartTotalPrice.innerHTML = `Total: $${totalPrice.toFixed(2)}`;
	navTotal.innerHTML = `$${totalPrice.toFixed(2)}`;
	navQuantity.innerHTML = totalItems;
}

function renderList() {
	cartBody.innerHTML = "";

	cart.forEach((item) => {
		cartBody.innerHTML += `
		<tr class="cart__table-content">
		<td class="cart__table-img">
				<img src="${item.img.replace(/\.webp$/, "-540.webp")}" alt="${item.alt}" loading="lazy">
		</td>
		<td>${item.title}</td>
		<td class="cart__quantity">
		<button class="cart__minus fa-solid fa-minus" type="button" aria-label="Decrease quantity of ${item.title}" onclick='changeNumberOfUnits("minus", ${
			item.id
		})' ></button>
		<span class="cart__total">${item.numberOfUnits}</span>
		<button class="cart__plus fa-solid fa-plus" type="button" aria-label="Increase quantity of ${item.title}" onclick='changeNumberOfUnits("plus", ${
			item.id
		})' ></button>
		</td>
		<td>$${(item.price * item.numberOfUnits).toFixed(2)}</td>
</tr>
    `;
	});
}

const changeNumberOfUnits = (action, id) => {
	cart = cart.map((item) => {
		let numberOfUnits = item.numberOfUnits;

		if (item.id === id) {
			if (action === "plus" && numberOfUnits < item.instock) {
				numberOfUnits++;
			} else if (action === "minus" && numberOfUnits > 0) {
				numberOfUnits--;
			}
		}
		return {
			...item,
			numberOfUnits,
		};
	});
	cart = cart.filter((item) => item.numberOfUnits > 0);
	updateCart();
};

const paymentButton = document.querySelector(".payment__button");
const payment = document.querySelector(".payment");
const cartPaymentBtn = document.querySelector(".cart__payment");
const paymentInputs = document.querySelectorAll(".payment__input");
const paymentMessage = document.querySelector(".payment__message");

function areAllInputsFilled() {
	let allInputsFilled = true;
	paymentInputs.forEach((input) => {
		if (input.value.trim() === "") {
			allInputsFilled = false;
		}
	});
	return allInputsFilled;
}

paymentButton.addEventListener("click", () => {
	if (cart.length === 0) {
		paymentMessage.textContent = "Your cart is empty";
		setTimeout(() => {
			paymentMessage.textContent = "";
		}, 2000);
	} else if (areAllInputsFilled()) {
		paymentMessage.textContent = "The order has been accepted!";
		setTimeout(() => {
			paymentInputs.forEach((input) => {
				input.value = "";
			});
			paymentMessage.style.display = "none";
		}, 2000);
		cart = [];
		updateCart();
	} else {
		paymentMessage.textContent = "Please fill in all required fields";
		setTimeout(() => {
			paymentMessage.textContent = "";
		}, 2000);
	}
});
