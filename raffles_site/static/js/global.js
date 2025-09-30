document.addEventListener("DOMContentLoaded", () => {
  /* =========================
     NAVBAR: toggle + scroll
     ========================= */
  (function initNavbar() {
    const toggleMenu = document.querySelector(".navbar__toggle");
    const menu = document.getElementById("navbarMenu");
    const navbar = document.querySelector(".navbar");

    if (toggleMenu && menu) {
      const closeMenuOnResize = () => {
        if (window.innerWidth > 768) {
          menu.classList.remove("active");
          toggleMenu.classList.remove("open");
          toggleMenu.setAttribute("aria-expanded", "false");
        }
      };

      toggleMenu.addEventListener("click", () => {
        const isActive = menu.classList.toggle("active");
        toggleMenu.classList.toggle("open");
        toggleMenu.setAttribute("aria-expanded", String(isActive));
      });

      window.addEventListener("resize", closeMenuOnResize);
    }

    if (navbar) {
      // scroll listener independiente — no depende de toggleMenu/menu
      window.addEventListener("scroll", () => {
        if (window.scrollY > 50) navbar.classList.add("scrolled");
        else navbar.classList.remove("scrolled");
      });
    }
  })();

  /* =========================
     HERO: carousel / slides
     ========================= */
  (function initHeroCarousel() {
    const slides = Array.from(document.querySelectorAll(".carousel-slide"));
    if (!slides.length) return;

    const nextBtn = document.querySelector(".next");
    const prevBtn = document.querySelector(".prev");
    let current = 0;
    let autoplayTimer = null;

    function showSlide(index) {
      slides.forEach((s, i) => s.classList.toggle("active", i === index));
    }

    if (nextBtn) nextBtn.addEventListener("click", () => {
      current = (current + 1) % slides.length;
      showSlide(current);
    });

    if (prevBtn) prevBtn.addEventListener("click", () => {
      current = (current - 1 + slides.length) % slides.length;
      showSlide(current);
    });

    // Keyboard arrows
    document.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") {
        current = (current + 1) % slides.length;
        showSlide(current);
      } else if (e.key === "ArrowLeft") {
        current = (current - 1 + slides.length) % slides.length;
        showSlide(current);
      }
    });

    // Autoplay if more than one slide
    if (slides.length > 1) {
      const startAutoplay = () => {
        if (autoplayTimer) clearInterval(autoplayTimer);
        autoplayTimer = setInterval(() => {
          current = (current + 1) % slides.length;
          showSlide(current);
        }, 5000);
      };
      startAutoplay();

      // Pause autoplay on hover/focus
      const carouselWrap = document.querySelector(".carousel") || slides[0].parentElement;
      if (carouselWrap) {
        carouselWrap.addEventListener("mouseenter", () => clearInterval(autoplayTimer));
        carouselWrap.addEventListener("mouseleave", startAutoplay);
        carouselWrap.addEventListener("focusin", () => clearInterval(autoplayTimer));
        carouselWrap.addEventListener("focusout", startAutoplay);
      }
    }

    // init first
    showSlide(current);
  })();

 
  /* =========================
   WINNERS CARD: holográfica
   ========================= */
(function initWinnersCard3D() {
  const card = document.querySelector("#winners .winners-card3d");
  if (!card) return;

  const glare = card.querySelector(".winners-card-glare");
  const flipBtn = card.querySelector(".winners-card-flip-btn");
  const minimap = document.querySelector("#winners .winners-card-minimap");
  const spans = minimap ? minimap.querySelectorAll("span") : [];
  const logos = card.querySelectorAll(".winners-card-logo");

  let isFlipped = false;
  let bounds = card.getBoundingClientRect();

  function updateMinimap(x, y) {
    if (!spans.length) return;
    spans[0].textContent = `x: ${x}`;
    spans[1].textContent = `y: ${y}`;
  }

  function handleMove(e) {
    const { clientX, clientY } = e;
    bounds = bounds || card.getBoundingClientRect();
    const x = clientX - bounds.left;
    const y = clientY - bounds.top;
    const centerX = bounds.width / 2;
    const centerY = bounds.height / 2;

    const rotateX = ((y - centerY) / centerY) * 15;
    const rotateY = ((x - centerX) / centerX) * 15;

    card.style.transform = `rotateY(${rotateY}deg) rotateX(${-rotateX}deg)`;
    updateMinimap(Math.round(rotateX), Math.round(rotateY));

    if (glare) {
      glare.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.4), transparent 60%)`;
    }

    logos.forEach((logo) => {
      const rect = logo.getBoundingClientRect();
      const logoX = rect.left + rect.width / 2;
      const logoY = rect.top + rect.height / 2;
      const dx = clientX - logoX;
      const dy = clientY - logoY;
      const hue = ((Math.atan2(dy, dx) + Math.PI) / (2 * Math.PI)) * 360;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const intensity = Math.max(0.6, 1.2 - distance / 250);
      const rotation = (Date.now() / 10) % 360;

      logo.style.setProperty("--hue", `${hue}deg`);
      logo.style.setProperty("--angle", `${rotation}deg`);
      logo.style.opacity = intensity;
      logo.classList.add("winners-card-prism");

      const icon = logo.querySelector(".winners-card-logo-icon");
      if (icon) {
        icon.style.filter = `hue-rotate(${hue}deg) brightness(${1.6 + intensity}) saturate(2)`;
      }
    });
  }

  function handleLeave() {
    card.style.transform = "rotateY(0deg) rotateX(0deg)";
    if (glare)
      glare.style.background = `radial-gradient(circle, rgba(255,255,255,0.2), transparent 60%)`;

    logos.forEach((logo) => {
      logo.style.setProperty("--hue", "0deg");
      logo.style.setProperty("--angle", "0deg");
      logo.style.opacity = 0.15;
      logo.classList.remove("winners-card-prism");
      const icon = logo.querySelector(".winners-card-logo-icon");
      if (icon) icon.style.filter = "brightness(1.2)";
    });
  }

  if (flipBtn) {
    flipBtn.addEventListener("click", () => {
      isFlipped = !isFlipped;
      card.setAttribute("data-active", isFlipped);
      flipBtn.setAttribute("aria-pressed", isFlipped);
      card.style.transform = isFlipped ? "rotateY(180deg)" : "rotateY(0deg)";
    });
  }

  card.addEventListener("mousemove", handleMove);
  card.addEventListener("mouseleave", handleLeave);
  window.addEventListener("resize", () => (bounds = card.getBoundingClientRect()));
})();


}); // end DOMContentLoaded
