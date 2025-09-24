// ===============================
//  GLOBAL JS - MotoRaffles
// ===============================

// Espera a que cargue el DOM
document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------
  // Animación del header al cargar
  // -------------------------------

  // Logo
  gsap.from(".logo", {
    x: -60,
    opacity: 0,
    duration: 0.8,
    ease: "power3.out"
  });

  // Menú (cada li entra uno por uno)
  gsap.from(".nav-links li", {
    y: -30,
    opacity: 0,
    duration: 0.6,
    ease: "back.out(1.7)",
    stagger: 0.15
  });

  // Iconos de login/carrito
  gsap.from(".nav-icons a", {
    x: 50,
    opacity: 0,
    duration: 0.6,
    ease: "power3.out",
    stagger: 0.2
  });

  // -------------------------------
  // Hover animado en los links
  // -------------------------------
  document.querySelectorAll(".nav-links a").forEach(link => {
    let scaleUp = gsap.quickTo(link, "scale", { duration: 0.3, ease: "power2.out" });
    let scaleDown = gsap.quickTo(link, "scale", { duration: 0.3, ease: "power2.in" });

    link.addEventListener("mouseenter", () => scaleUp(1.15)); // crece un poco
    link.addEventListener("mouseleave", () => scaleDown(1));  // vuelve al normal
  });

  // -------------------------------
  // Hover animado en los iconos
  // -------------------------------
  document.querySelectorAll(".nav-icons a").forEach(icon => {
    let bounce = gsap.timeline({ paused: true });
    bounce.to(icon, { scale: 1.2, duration: 0.2, ease: "power1.out" })
          .to(icon, { scale: 1, duration: 0.2, ease: "bounce.out" });

    icon.addEventListener("mouseenter", () => bounce.play(0));
  });
});
