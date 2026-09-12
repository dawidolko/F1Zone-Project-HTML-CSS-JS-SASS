# F1 Zone

> 🏎️ **A poster shop without a framework** — plain HTML, SCSS and vanilla JavaScript, with a cart that persists in the browser

**F1 Zone** sells Formula 1 posters: tracks, cars and drivers. The catalogue lives in a JavaScript data file, a modal opens any poster full size, and the cart keeps its contents in `localStorage`, so closing the tab does not empty it.

There is no framework and no build step beyond compiling SCSS. Every behaviour — the modal, the cart, the totals in the navigation, the "already in your cart" message — is a few dozen lines of vanilla JavaScript, which is the point of the exercise.

![HTML5](https://img.shields.io/badge/HTML5-semantic-E34F26?logo=html5&logoColor=white)
![Sass](https://img.shields.io/badge/Sass-SCSS-CC6699?logo=sass&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?logo=javascript&logoColor=black)
![WebP](https://img.shields.io/badge/Images-WebP%20%2B%20fallback-0A84FF)
![License](https://img.shields.io/badge/License-MIT-green)

**Live:** [f1.dawidolko.pl](https://f1.dawidolko.pl)

---

## 🎯 Key Features

- **A cart that survives the tab** — items are mirrored into `localStorage` on every change, with quantity, unit price and a running total recomputed on load.
- **Duplicate protection with feedback** — adding something already in the basket shows a message instead of silently doing nothing or adding it twice.
- **The catalogue is data** — `js/data.js` holds every poster with its id, price, stock, category, brand, code and alt text. Adding a product means adding an object.
- **A product modal built by hand** — `js/modal.js` renders the detail view from the same data, so the listing and the modal can never disagree.
- **Live totals in the navigation** — quantity and value update in the header as the cart changes, without a page reload.
- **WebP with a fallback** — every photograph ships as both `.webp` and `.jpg`, so modern browsers get the smaller file and older ones still get an image.
- **SCSS split by concern** — colours, sizes, mixins, reset and one partial per breakpoint, compiled into a single stylesheet.
- **Alt text written per product** — it lives in the data file next to the image path, so it cannot be forgotten when a poster is added.

---

## 🛠️ Technology Stack

| Technology      | Role                                                          |
| --------------- | ------------------------------------------------------------- |
| **HTML5**       | Semantic markup across the two pages.                         |
| **SCSS**        | Variables, mixins and per-breakpoint partials.                |
| **JavaScript**  | Cart, modal, totals and rendering — no framework.             |
| **localStorage**| Cart persistence between visits.                              |
| **Font Awesome**| Icon set.                                                     |

---

## 🚀 Getting Started

### Prerequisites

- Any static web server (or just a browser)
- Sass, if you intend to change the styles

### 1. Clone the repository

```bash
git clone https://github.com/dawidolko/F1Zone-Project-HTML-CSS-JS-SASS.git
cd F1Zone-Project-HTML-CSS-JS-SASS
```

### 2. Open it

```bash
open index.html          # or serve the directory
python3 -m http.server   # http://localhost:8000
```

### 3. Work on the styles

```bash
sass --watch sass/main.scss css/style.css
```

---

## 📁 Project Structure

```
F1Zone-Project-HTML-CSS-JS-SASS/
├── index.html          # catalogue
├── cart.html           # basket and totals
├── js/
│   ├── data.js         # every poster: price, stock, category, image, alt
│   ├── main.js         # rendering and filters
│   ├── modal.js        # the product detail view
│   ├── cart.js         # cart state, localStorage, totals
│   └── footer.js
├── sass/
│   ├── main.scss       # entry point
│   ├── _colors.scss  _sizes.scss  _mixins.scss  _reset.scss
│   ├── _medium.scss  _large.scss   # breakpoints
│   └── cart/           # basket-specific styles
├── css/                # compiled stylesheet
├── img/                # posters and backgrounds, WebP + JPG
└── robots.txt
```

---

## 📄 License

MIT © [Dawid Olko](https://dawidolko.pl)
