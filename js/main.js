const headerItems = [
  {
    img: "img/transparent.png",
    text: "Tracks Collection",
    alt: "tracks collection 2",
  },
  {
    img: "img/teams_top.jpg",
    text: "Teams Collection",
    alt: "teams collection 2",
  },
  {
    img: "img/drivers_top.jpg",
    text: "Drivers Collection",
    alt: "drivers collection 2",
  },
];

const header = document.querySelector(".header");
let currentSlideIndex = 0;

const renderHeader = () => {
  headerItems.forEach((el) => {
    header.innerHTML += `
		<div class="header__slide">
				<div class="header__img">
					<div class="header__content move">
						<p class="header__heading">New Summer</p>
						<h2 class="header__text">${el.text}</h2>
						<a class="header__btn" href="#cars_id">SHOP NOW</a>
					</div>
					<img class="header__cars" src="${el.img}" alt="${el.alt}" />
				</div>
			</div>
	`;
  });
};

const showSlide = (slideIndex) => {
  const slides = document.querySelectorAll(".header__slide");

  slides.forEach((slide, index) => {
    if (index === slideIndex) {
      slide.classList.add("header__active");
    } else {
      slide.classList.remove("header__active");
    }
  });
};
renderHeader();
showSlide(currentSlideIndex);

const slides = document.querySelectorAll(".header__slide");
const leftBtn = document.querySelector(".header__arrow-left");
const rightBtn = document.querySelector(".header__arrow-right");

let activeSlide = 0;

rightBtn.addEventListener("click", () => {
  changeSlide(1);
});

leftBtn.addEventListener("click", () => {
  changeSlide(-1);
});

function changeSlide(direction) {
  activeSlide += direction;

  if (activeSlide > slides.length - 1) {
    activeSlide = 0;
  } else if (activeSlide < 0) {
    activeSlide = slides.length - 1;
  }
  setActiveSlide();
}

function setActiveSlide() {
  slides.forEach((slide) => slide.classList.remove("header__active"));
  slides[activeSlide].classList.add("header__active");
}

const slideContainer = document.querySelector(".slider__gallery");

const BestsellersId = [8, 10, 12, 16, 7, 14, 11];
const Bestsellers = modalProduct.filter((element) =>
  BestsellersId.includes(element.id),
);

const renderSlider = () => {
  Bestsellers.forEach((slider) => {
    slideContainer.innerHTML += `
		<div class="slider__box">
			<div class="slider__content">
				<img
					src="${slider.img}"
					alt="${slider.alt}"
					class="slider__img"
				/>
				<div class="slider__details">
					<h3 class="slider__title">${slider.title}</h3>
					<p class="slider__price">$${slider.price}</p>
					<button class="slider__btn" onclick='addToCart(${slider.id})'>add to cart</button>
				</div>
			</div>
		</div>	
		`;
  });
};
renderSlider();

const productsContainer = document.querySelector(".cars__products");

const renderProducts = () => {
  modalProduct.forEach((product) => {
    productsContainer.innerHTML += `
  <div class="cars__box ${product.visibility}" data-category="${product.category}">
	<div class="cars__img-box">
  <img class="cars__img" src="${product.img}" alt="${product.alt}">
	</div>
  <h3 class="cars__title">${product.title}</h3>
  <p class="cars__price">$${product.price}</p>
	<div class="cars__buttons">
	<button class="cars__btn cars__btn-view">
								quick view <i class="fa-solid fa-eye"></i>
							</button>
  <button class="cars__btn" onclick='addToCart(${product.id})' >add to cart <i class="fa-solid fa-cart-shopping"></i></button>    
  </div>
	</div>
  `;
  });
};
renderProducts();

const sections = document.querySelector(".cars");
const filterButtons = document.querySelectorAll(".cars__filter-btn");
const productsBox = document.querySelectorAll(".cars__box");
const productViewMore = document.querySelector(".product__view-more");
const productsVisible = document.querySelectorAll(".cars__hide");

productViewMore.textContent = "View More";

function ViewMoreBtn() {
  if (productViewMore.textContent === "View Less") {
    window.location.href = "index.html#cars_id";
  }

  if (productViewMore.textContent === "View More") {
    productViewMore.textContent = "View Less";
  } else {
    productViewMore.textContent = "View More";
  }
}

productViewMore.addEventListener("click", () => {
  productsVisible.forEach((el) => {
    setTimeout(() => {
      el.classList.toggle("cars__hide");
    }, 500);
    el.classList.toggle("cars__active_fade");
  });

  ViewMoreBtn();
});

const FilterAll = document.querySelector(".cars__filter-all");

FilterAll.addEventListener("click", () => {
  productViewMore.style.display = "block";
  productsVisible.forEach((el) => {
    el.classList.add("cars__hide");
  });
});

const Filters = document.querySelectorAll(".cars__filter-mwk");
Filters.forEach((el) => {
  el.addEventListener("click", () => {
    productViewMore.textContent = "View More";
    productViewMore.style.display = "none";
    productsVisible.forEach((el) => {
      el.classList.remove("cars__hide");
      el.classList.remove("cars__active_fade");
    });
  });
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((btn) => btn.classList.remove("cars__active"));
    button.classList.add("cars__active");

    const category = button.getAttribute("data-category");

    productsBox.forEach((product) => {
      if (
        category.toLowerCase() === "all" ||
        product.getAttribute("data-category") === category
      ) {
        product.classList.remove("hidden");
        product.classList.add("cars__transition");
        setTimeout(() => {
          product.classList.remove("cars__transition");
        }, 300);
      } else {
        product.classList.add("hidden");
        product.classList.remove("cars__transition");
      }
    });
  });
});

const searchIcon = document.querySelector(".cars__search-icon");
const searchInput = document.querySelector(".cars__search-input");
const products = document.querySelectorAll(".cars__box");

searchIcon.addEventListener("click", () => {
  searchInput.classList.toggle("cars__search-active");

  if (!searchInput.classList.contains("cars__search-active")) {
    searchInput.value = "";
    products.forEach((product) => {
      product.style.display = "flex";
    });
  }
});

function handleSearch(searchInput, products) {
  searchInput.addEventListener("input", () => {
    const searchQuery = searchInput.value.trim().toLowerCase();
    products.forEach((product) => {
      const productName = product
        .querySelector(".cars__title")
        .innerText.toLowerCase();
      if (productName.includes(searchQuery) || searchQuery === "") {
        product.style.display = "flex";
        productViewMore.style.display = "none";
        productsVisible.forEach((el) => {});
      } else {
        product.style.display = "none";
        productViewMore.style.display = "none";
        productsVisible.forEach((el) => {});
      }
    });
  });
}
handleSearch(searchInput, products);

const cookieBox = document.querySelector(".cookie");
const cookieBtn = document.querySelector(".cookie__btn");

const showCookie = () => {
  const cookieEaten = localStorage.getItem("cookie");
  if (cookieEaten) {
    cookieBox.style.display = "none";
  }
};

const handleCookieBox = () => {
  localStorage.setItem("cookie", "true");
  cookieBox.style.display = "none";
};
cookieBtn.addEventListener("click", handleCookieBox);
showCookie();

let scrollContainer = document.querySelector(".slider__gallery");
let sliderLeft = document.querySelector(".slider__left");
let sliderRight = document.querySelector(".slider__right");

scrollContainer.addEventListener("scroll", () => {
  updateButtonColors();
});

function updateButtonColors() {
  const maxScrollLeft =
    scrollContainer.scrollWidth - scrollContainer.clientWidth;

  if (scrollContainer.scrollLeft >= maxScrollLeft) {
    sliderRight.style.color = "grey";
  } else {
    sliderRight.style.color = "";
  }

  if (scrollContainer.scrollLeft <= 0) {
    sliderLeft.style.color = "grey";
  } else {
    sliderLeft.style.color = "";
  }
}

sliderRight.addEventListener("click", () => {
  scrollContainer.style.scrollBehavior = "smooth";
  scrollContainer.scrollLeft += 300;
  updateButtonColors();
});

sliderLeft.addEventListener("click", () => {
  scrollContainer.style.scrollBehavior = "smooth";
  scrollContainer.scrollLeft -= 300;
  updateButtonColors();
});
