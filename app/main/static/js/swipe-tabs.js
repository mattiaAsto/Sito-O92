/* Small-screen tabs: pill selector on top + horizontal swipe between panes.
   Markup: [data-swipe-tabs] > .activity-tabs-nav (Bootstrap pills) + .tab-content > .tab-pane.
   On wide screens the CSS shows every pane and hides the selector. */
(() => {
  const roots = document.querySelectorAll("[data-swipe-tabs]");
  if (!roots.length || typeof bootstrap === "undefined") return;

  const phone = window.matchMedia("(max-width: 767.98px)");
  const noSwipe = "input, textarea, select, iframe, .carousel, .calendar-grid, [data-no-swipe]";

  roots.forEach((root) => {
    const nav = root.querySelector('[role="tablist"]');
    const buttons = Array.from(root.querySelectorAll('[data-bs-toggle="pill"]'));
    let start = null;

    buttons.forEach((button) => {
      button.addEventListener("shown.bs.tab", () => {
        if (!nav) return;
        const left = button.offsetLeft - (nav.clientWidth - button.offsetWidth) / 2;
        nav.scrollTo({ left, behavior: "smooth" });
      });
    });

    root.addEventListener("touchstart", (event) => {
      if (!phone.matches || event.target.closest(noSwipe)) {
        start = null;
        return;
      }
      const touch = event.touches[0];
      start = { x: touch.clientX, y: touch.clientY };
    }, { passive: true });

    root.addEventListener("touchend", (event) => {
      if (!start) return;
      const touch = event.changedTouches[0];
      const dx = touch.clientX - start.x;
      const dy = touch.clientY - start.y;
      start = null;
      if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy) * 1.5) return;
      const current = buttons.findIndex((button) => button.classList.contains("active"));
      const next = buttons[current + (dx < 0 ? 1 : -1)];
      if (next) bootstrap.Tab.getOrCreateInstance(next).show();
    }, { passive: true });
  });

  // In-page links and #anchors that point inside a hidden pane must open that pane first.
  const showPaneFor = (hash) => {
    if (!phone.matches || !hash || hash.length < 2) return false;
    let target = null;
    try {
      target = document.querySelector(hash);
    } catch (error) {
      return false;
    }
    const pane = target && target.closest("[data-swipe-tabs] .tab-pane");
    const button = pane && document.querySelector(`[data-bs-target="#${pane.id}"]`);
    if (!button) return false;
    if (button.classList.contains("active")) {
      target.scrollIntoView();
    } else {
      button.addEventListener("shown.bs.tab", () => target.scrollIntoView(), { once: true });
      bootstrap.Tab.getOrCreateInstance(button).show();
    }
    return true;
  };

  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (link && showPaneFor(link.getAttribute("href"))) event.preventDefault();
  });
  window.addEventListener("hashchange", () => showPaneFor(window.location.hash));
  showPaneFor(window.location.hash);
})();
