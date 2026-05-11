/* FitControl Pro 2.0 — Auth interactions */
(function () {
  "use strict";
  const togglers = document.querySelectorAll("[data-password-toggle]");
  togglers.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.passwordToggle;
      const input = document.getElementById(targetId);
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
      btn.classList.toggle("is-on");
    });
  });
})();
