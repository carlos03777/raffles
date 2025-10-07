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
     NAVBAR: user dropdown
     ========================= */
  (function initUserDropdown() {
    const btn = document.getElementById("userMenuBtn");
    const menu = document.getElementById("userDropdown");
    if (!btn || !menu) return;

    // Toggle dropdown
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      menu.style.display = menu.style.display === "block" ? "none" : "block";
    });

    // Click fuera → cerrar
    document.addEventListener("click", (e) => {
      if (!btn.contains(e.target) && !menu.contains(e.target)) {
        menu.style.display = "none";
      }
    });

    // Escape → cerrar
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        menu.style.display = "none";
      }
    });
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
(function initWinnersCard() {
  const card = document.querySelector("#winners .winners-card");
  if (!card) return;

  const glare = card.querySelector(".winners-glare");
  const flipBtn = card.querySelector(".winners-flip-btn");
  const minimap = document.querySelector("#winners .winners-minimap");
  const spans = minimap ? minimap.querySelectorAll("span") : [];
  const logos = card.querySelectorAll(".winners-logo");

  let isFlipped = false;
  let bounds = card.getBoundingClientRect();

  function updateMinimap(x, y) {
    if (!spans.length) return;
    spans[0].textContent = `x: ${x}`;
    spans[1].textContent = `y: ${y}`;
  }

  function handleMove(e) {
    const { clientX, clientY } = e;
    bounds = card.getBoundingClientRect();
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
      logo.classList.add("prism");
    });
  }

  function handleLeave() {
    card.style.transform = "rotateY(0deg) rotateX(0deg)";
    if (glare)
      glare.style.background = `radial-gradient(circle, rgba(255,255,255,0.2), transparent 60%)`;

    logos.forEach((logo) => {
      logo.style.opacity = 0.15;
      logo.classList.remove("prism");
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


  /* =========================
   RAFFLE-CAROUSEL (scoped)
   Pegar dentro de tu DOMContentLoaded
   ========================= */
(function initRaffleCarousel() {
  const carousel = document.querySelector('.raffle-carousel');
  if (!carousel) return;

  const track = carousel.querySelector('.raffle-carousel-track');
  const slides = Array.from(carousel.querySelectorAll('.raffle-carousel-slide'));
  const prevBtn = carousel.querySelector('.raffle-carousel-prev');
  const nextBtn = carousel.querySelector('.raffle-carousel-next');

  if (!track || slides.length === 0) return;

  let index = 0;
  let autoplayTimer = null;

  function update() {
    // mover el track
    track.style.transform = `translateX(-${index * 100}%)`;

    // accesibilidad: marcar aria-hidden para las slides inactivas
    slides.forEach((s, i) => s.setAttribute('aria-hidden', i !== index ? 'true' : 'false'));
  }

  function next() {
    index = (index + 1) % slides.length;
    update();
  }

  function prev() {
    index = (index - 1 + slides.length) % slides.length;
    update();
  }

  // listeners controles
  if (nextBtn) nextBtn.addEventListener('click', next);
  if (prevBtn) prevBtn.addEventListener('click', prev);

  // keyboard (cuando el carousel tiene foco)
  carousel.setAttribute('tabindex', '0'); // hace focusable
  carousel.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') prev();
  });

  // autoplay (opcional) y pausa al hover/focus
  if (slides.length > 1) {
    const startAutoplay = () => {
      clearInterval(autoplayTimer);
      autoplayTimer = setInterval(next, 5000);
    };
    const stopAutoplay = () => clearInterval(autoplayTimer);

    startAutoplay();
    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);
    carousel.addEventListener('focusin', stopAutoplay);
    carousel.addEventListener('focusout', startAutoplay);
  }

  // init
  update();

  // DEBUG helpers (descomenta si necesitas ver en consola)
  // console.log('raffle carousel inited, slides:', slides.length);
})();
(function() {
  const section = document.querySelector(".ticket-purchase");
  if (!section) return;

  const inputs = section.querySelectorAll(".ticket-code input");
  const btnAleatorio = section.querySelector(".ticket-btn-alt");
  const btnVaciar = section.querySelector(".ticket-btn-secondary");
  const form = section.querySelector("#ticketForm");
  const hiddenInput = section.querySelector("#ticketNumber");

  // Elementos del card resumen
  const summaryCard = section.querySelector(".ticket-summary-card");
  const summaryNumber = summaryCard?.querySelector(".ticket-summary-number");

  // 👉 Aquí leemos el máximo permitido desde el atributo data
  const maxTickets = parseInt(section.dataset.maxTickets, 10) || 9999;

  if (!inputs.length) return;

  // Helpers
  const getTicketCode = () => Array.from(inputs).map((i) => i.value).join("");
  const setTicketCode = (code) => {
    inputs.forEach((i, idx) => (i.value = code[idx] || ""));
  };
  const focusFirstEmpty = () => {
    const firstEmpty = Array.from(inputs).find((i) => !i.value);
    (firstEmpty || inputs[0]).focus();
  };

  // 👉 Rellenar casillas si hiddenInput tiene valor (caso EDITAR)
  if (hiddenInput && hiddenInput.value) {
    const code = hiddenInput.value.toString().padStart(inputs.length, "0");
    setTicketCode(code);
  }

  // Navegación entre inputs
  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/\D/g, "");
      if (e.target.value && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !input.value && index > 0) {
        inputs[index - 1].focus();
      }
    });
  });

  // Aleatorio
  btnAleatorio?.addEventListener("click", () => {
    // número aleatorio entre 1 y maxTickets
    const randomNum = Math.floor(Math.random() * maxTickets) + 1;

    // Convertimos a string con ceros a la izquierda según inputs
    const code = randomNum.toString().padStart(inputs.length, "0");

    setTicketCode(code);
    hiddenInput.value = randomNum; // guardamos el número como entero
    inputs[inputs.length - 1].focus();

    if (summaryNumber) {
      summaryNumber.textContent = `Ticket #${code}`;
    }
  });

  // Vaciar
  btnVaciar?.addEventListener("click", () => {
    setTicketCode("");
    hiddenInput.value = "";
    inputs[0].focus();
    if (summaryNumber) {
      summaryNumber.textContent = "Ticket: --";
    }
  });

  // Submit
  form?.addEventListener("submit", (e) => {
    const code = getTicketCode();
    if (code.length !== inputs.length) {
      e.preventDefault();
      alert("Debes ingresar un número de ticket completo.");
      return;
    }
    hiddenInput.value = parseInt(code, 10); // guardamos como número
    if (summaryNumber) {
      summaryNumber.textContent = `Ticket #${code}`;
    }
  });
})();




}); // end DOMContentLoaded
