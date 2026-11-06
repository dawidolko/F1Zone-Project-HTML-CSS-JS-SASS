const navMenu = document.querySelector(".nav__menu");
const navOpen = document.querySelector(".nav__open");
const navClose = document.querySelector(".nav__close");
const navLinks = document.querySelector(".nav__links");
const navLink = document.querySelectorAll(".nav__link");

const openNav = () => {
	navOpen.classList.toggle("nav__hide");
	navClose.classList.toggle("nav__hide");
	navLinks.classList.toggle("nav__links-active");
	navMenu.setAttribute("aria-expanded", navLinks.classList.contains("nav__links-active"));
};
navMenu.addEventListener("click", openNav);

navLink.forEach((link) => {
	link.addEventListener("click", () => {
		navLinks.classList.toggle("nav__links-active");
		navOpen.classList.toggle("nav__hide");
		navClose.classList.toggle("nav__hide");
		navMenu.setAttribute("aria-expanded", navLinks.classList.contains("nav__links-active"));
	});
});

const contactLinks = document.querySelectorAll(
	'a[href^="mailto:"], a[href^="tel:"]'
);
const contactMessage = document.querySelector(".contact__message-mail");
const contactMessageTel = document.querySelector(".contact__message-tel");

contactLinks.forEach((link) => {
	link.addEventListener("click", async (event) => {
		event.preventDefault();
		const contactInfo = link.getAttribute("href").replace(/(mailto:|tel:)/, "");

		try {
			if (window.innerWidth >= 768) {
				await navigator.clipboard.writeText(contactInfo);

				if (link.getAttribute("href").startsWith("tel:")) {
					contactMessageTel.textContent = "Phone number has been copied";
					contactMessageTel.style.display = "block";
					setTimeout(() => {
						contactMessageTel.style.display = "none";
					}, 2000);
				} else if (link.getAttribute("href").startsWith("mailto:")) {
					contactMessage.textContent = "Email has been copied";
					contactMessage.style.display = "block";
					setTimeout(() => {
						contactMessage.style.display = "none";
					}, 2000);
				}
			} else {
				if (link.getAttribute("href").startsWith("tel:")) {
					window.location.href = `tel:${contactInfo}`;
				} else if (link.getAttribute("href").startsWith("mailto:")) {
					window.location.href = `mailto:${contactInfo}`;
				}
			}
		} catch (err) {}
	});
});

const renderFooterDate = () => {
	const footerDate = document.querySelector(".footer__date");
	const currentDate = new Date().getFullYear();
	footerDate.innerHTML = currentDate;
};
renderFooterDate();
