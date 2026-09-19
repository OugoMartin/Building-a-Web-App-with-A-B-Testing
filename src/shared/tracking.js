(function () {
  const variant = document.body.dataset.variant;
  const key = "lumina_experiment_events";

  function track(eventName) {
    const events = JSON.parse(localStorage.getItem(key) || "[]");
    events.push({
      event_name: eventName,
      variant,
      session_id: sessionStorage.luminaSession || (sessionStorage.luminaSession = crypto.randomUUID()),
      timestamp: new Date().toISOString()
    });
    localStorage.setItem(key, JSON.stringify(events));
  }

  track("product_view");
  document.querySelector("[data-purchase]").addEventListener("click", function () {
    track("purchase_click");
    const toast = document.querySelector(".toast");
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2200);
  });
})();
