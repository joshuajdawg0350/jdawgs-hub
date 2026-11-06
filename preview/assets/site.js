/* J-Dawgs Industries — flagship site script.
   Three jobs only: the mobile nav toggle, the header's
   solid-on-scroll state, and calm staggered entrances for
   .rise elements. No tracking, no network calls.
   Honors prefers-reduced-motion (elements simply stay visible). */
(function () {
  "use strict";

  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("scrolled", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var items = document.querySelectorAll(".rise");
  if (reduce || !("IntersectionObserver" in window)) {
    items.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  items.forEach(function (el, i) {
    el.style.transitionDelay = (i % 4) * 55 + "ms"; /* 40–60ms stagger family */
    io.observe(el);
  });
  /* Failsafe: motion is a garnish, invisible content is a failure.
     Anything still hidden 2.8s after load simply appears. */
  setTimeout(function () {
    items.forEach(function (el) { el.classList.add("in"); });
  }, 2800);
})();
