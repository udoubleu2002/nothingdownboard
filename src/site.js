(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var today = new Date().toISOString().slice(0, 10);

  // ---------- small storage helpers (storage can be blocked; never let it break the page)
  function load(key, fallback) { try { var v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; } }
  function store(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} }

  // ---------- toast
  var toastTimer;
  function toast(msg) {
    var t = $("toast"); if (!t) return;
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.hidden = true; }, 2400);
  }

  // ---------- saved offers
  var saved = load("ndb-saved", []);
  if (!Array.isArray(saved)) saved = [];
  function isSaved(id) { return saved.indexOf(id) > -1; }
  function paintSaved() {
    $$(".save").forEach(function (b) {
      var on = isSaved(b.dataset.id);
      b.setAttribute("aria-pressed", on ? "true" : "false");
      var l = b.querySelector(".act-l"); if (l) l.textContent = on ? "Saved" : "Save";
    });
    $$("[data-saved-count]").forEach(function (el) { el.textContent = saved.length; el.hidden = saved.length === 0; });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".save"); if (!b) return;
    var id = b.dataset.id;
    if (isSaved(id)) { saved = saved.filter(function (x) { return x !== id; }); toast("Removed from Saved"); }
    else { saved.push(id); toast("Saved. Find it under Saved."); }
    store("ndb-saved", saved); paintSaved();
    if (typeof apply === "function" && state && state.saved) apply();
  });

  // ---------- share
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".share"); if (!b) return;
    var url = location.origin + b.dataset.url;
    var data = { title: b.dataset.title, text: b.dataset.title + " — found on nothingdown.com", url: url };
    if (navigator.share) {
      navigator.share(data).catch(function () {});
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { toast("Link copied"); }, function () { toast(url); });
    } else { toast(url); }
  });

  // ---------- bottom bar: mark the current tab
  (function () {
    var p = location.pathname, q = location.search;
    var tab = /saved=1/.test(q) ? "saved" : p.indexOf("/guides/") === 0 ? "guides" : (p === "/" || /^\/(car-|home-|phones|deals|offer)/.test(p)) ? "deals" : "";
    $$(".bottombar [data-tab]").forEach(function (a) { if (a.dataset.tab === tab) a.setAttribute("aria-current", "page"); });
  })();

  // ---------- listing pages
  var list = $("list");
  var state = null, apply = null;
  if (list) {
    var items = $$(".offer", list);
    var newestAdded = items.reduce(function (m, el) { var a = el.dataset.added || ""; return a > m ? a : m; }, "");
    var filterIds = ["provider", "onlyZeroDas", "noTrade", "noNewLine", "noSpecial", "minMo", "maxMo", "onlyNew", "hasExpiry"];
    state = { saved: false, since: false, cats: [], nomil: false };

    // New since last visit: compare with offers seen before.
    var seen = load("ndb-seen", null);
    var sinceIds = [];
    if (seen && Array.isArray(seen.ids)) {
      items.forEach(function (el) {
        if (seen.ids.indexOf(el.dataset.id) === -1 && el.dataset.added > (seen.at || "")) {
          sinceIds.push(el.dataset.id);
          var tags = el.querySelector(".tags");
          if (tags) { var s = document.createElement("span"); s.className = "tag since"; s.textContent = "New since your last visit"; tags.insertBefore(s, tags.firstChild); }
        }
      });
    }
    var allSeen = (seen && Array.isArray(seen.ids) ? seen.ids : []).concat(items.map(function (el) { return el.dataset.id; }));
    var uniq = allSeen.filter(function (v, i) { return allSeen.indexOf(v) === i; }).slice(-2000);
    store("ndb-seen", { ids: uniq, at: today });
    var sincePill = document.querySelector('[data-pill="since"]');
    if (sincePill && sinceIds.length) { sincePill.hidden = false; sincePill.textContent = sinceIds.length + " new since your last visit"; }
    if (sinceIds.length && $("sinceMWrap")) { $("sinceMWrap").hidden = false; $("sinceMLabel").textContent = sinceIds.length + " new since my last visit"; }

    function val(id) { var el = $(id); return el.type === "checkbox" ? el.checked : el.value; }
    function setVal(id, v) { var el = $(id); if (el.type === "checkbox") el.checked = !!v; else el.value = v == null ? "" : v; }

    // Read filters from the page link (?zero=1&max=350 …) so filtered views can be shared.
    var P = {};
    try { new URLSearchParams(location.search).forEach(function (v, k) { P[k] = v; }); } catch (e) {}
    if (P.q) $("q").value = P.q;
    if (P.provider) setVal("provider", P.provider);
    if (P.zero) setVal("onlyZeroDas", true);
    if (P.notrade) setVal("noTrade", true);
    if (P.nonewline) setVal("noNewLine", true);
    if (P.nospecial) setVal("noSpecial", true);
    if (P.min) setVal("minMo", P.min);
    if (P.max) setVal("maxMo", P.max);
    if (P["new"]) setVal("onlyNew", true);
    if (P.expiry) setVal("hasExpiry", true);
    if (P.sort && $("sort").querySelector('option[value="' + P.sort + '"]')) $("sort").value = P.sort;
    if (P.saved) state.saved = true;
    if (P.nomil) state.nomil = true;
    if (P.cat) state.cats = P.cat.split(",");

    function activeCount() {
      var n = filterIds.reduce(function (c, id) { var v = val(id); return c + (v === true || (typeof v === "string" && v !== "") ? 1 : 0); }, 0);
      return n + (state.saved ? 1 : 0) + (state.since ? 1 : 0) + (state.nomil ? 1 : 0) + (state.cats.length ? 1 : 0);
    }

    function syncUrl() {
      var p = new URLSearchParams();
      var qv = $("q").value.trim(); if (qv) p.set("q", qv);
      if (val("provider")) p.set("provider", val("provider"));
      if (val("onlyZeroDas")) p.set("zero", "1");
      if (val("noTrade")) p.set("notrade", "1");
      if (val("noNewLine")) p.set("nonewline", "1");
      if (val("noSpecial")) p.set("nospecial", "1");
      if (val("minMo")) p.set("min", val("minMo"));
      if (val("maxMo")) p.set("max", val("maxMo"));
      if (val("onlyNew")) p.set("new", "1");
      if (val("hasExpiry")) p.set("expiry", "1");
      if (state.saved) p.set("saved", "1");
      if (state.nomil) p.set("nomil", "1");
      if (state.cats.length) p.set("cat", state.cats.join(","));
      if ($("sort").value !== "monthly") p.set("sort", $("sort").value);
      var qs = p.toString();
      try { history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash); } catch (e) {}
    }

    function paintPills() {
      var map = { zero: val("onlyZeroDas"), notrade: val("noTrade"), nonewline: val("noNewLine"), u350: val("maxMo") === "350",
                  "new": val("onlyNew"), saved: state.saved, since: state.since };
      $$(".pill").forEach(function (b) { b.setAttribute("aria-pressed", map[b.dataset.pill] ? "true" : "false"); });
    }

    apply = function () {
      var terms = $("q").value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      var prov = val("provider");
      var min = parseFloat(val("minMo")), max = parseFloat(val("maxMo"));
      var shown = 0;
      items.forEach(function (el) {
        var d = el.dataset, flags = (d.flags || "").split(" ");
        var m = d.monthly === "" ? NaN : parseFloat(d.monthly);
        var ok = !(d.expires && d.expires < today);
        if (ok && state.cats.length && state.cats.indexOf(d.cat) === -1) ok = false;
        if (ok && prov && d.provider !== prov) ok = false;
        if (ok && val("onlyZeroDas") && d.zero !== "1") ok = false;
        if (ok && val("noTrade") && flags.indexOf("trade") > -1) ok = false;
        if (ok && val("noNewLine") && flags.indexOf("newline") > -1) ok = false;
        if (ok && val("noSpecial") && flags.indexOf("special") > -1) ok = false;
        if (ok && state.nomil && flags.indexOf("military") > -1) ok = false;
        if (ok && !isNaN(min) && !(m >= min)) ok = false;
        if (ok && !isNaN(max) && !(m <= max)) ok = false;
        if (ok && val("onlyNew") && d.added !== newestAdded) ok = false;
        if (ok && val("hasExpiry") && !d.expires) ok = false;
        if (ok && state.saved && !isSaved(d.id)) ok = false;
        if (ok && state.since && sinceIds.indexOf(d.id) === -1) ok = false;
        if (ok && terms.length) { for (var i = 0; i < terms.length; i++) { if (d.text.indexOf(terms[i]) === -1) { ok = false; break; } } }
        el.hidden = !ok;
        if (ok) shown++;
      });
      sortItems();
      var label = shown === 1 ? "1 offer" : shown + " offers";
      $("count").textContent = (state.saved ? "Saved: " : "") + (shown === items.length ? label : label + " of " + items.length);
      $("applyCount").textContent = "Show " + label;
      var empty = $("empty");
      empty.hidden = shown !== 0;
      empty.querySelector("strong").textContent = state.saved && !saved.length ? "Nothing saved yet" : "No offers match these filters";
      empty.querySelector(".empty-msg").textContent = state.saved && !saved.length
        ? "Tap the heart on any offer to keep it here." : "Loosen a filter or clear them to see every offer.";
      var c = activeCount();
      $("filterBadge").hidden = c === 0; $("filterBadge").textContent = c;
      paintPills(); syncUrl();
      if ($("sortM")) $("sortM").value = $("sort").value;
      if ($("savedM")) $("savedM").checked = state.saved;
      if ($("sinceM")) $("sinceM").checked = state.since;
    };

    function sortItems() {
      var s = $("sort").value;
      var num = function (el, key) { var v = parseFloat(el.dataset[key]); return isNaN(v) || v === 0 ? Infinity : v; };
      var sorted = items.slice().sort(function (a, b) {
        var ta = a.dataset.title, tb = b.dataset.title;
        if (s === "monthly") return (num(a, "monthly") - num(b, "monthly")) || ta.localeCompare(tb);
        if (s === "total") return (num(a, "total") - num(b, "total")) || (num(a, "monthly") - num(b, "monthly")) || ta.localeCompare(tb);
        if (s === "newest") return (b.dataset.added || "").localeCompare(a.dataset.added || "") || ta.localeCompare(tb);
        if (s === "ending") return (a.dataset.expires || "9999").localeCompare(b.dataset.expires || "9999") || ta.localeCompare(tb);
        return ta.localeCompare(tb);
      });
      var empty = $("empty");
      sorted.forEach(function (el) { list.insertBefore(el, empty); });
    }

    var t;
    $("q").addEventListener("input", function () { clearTimeout(t); t = setTimeout(apply, 120); });
    $("q").addEventListener("search", apply);
    $("sort").addEventListener("change", apply);
    if ($("sortM")) $("sortM").addEventListener("change", function () { $("sort").value = $("sortM").value; apply(); });
    if ($("savedM")) $("savedM").addEventListener("change", function () { state.saved = $("savedM").checked; apply(); });
    if ($("sinceM")) $("sinceM").addEventListener("change", function () { state.since = $("sinceM").checked; apply(); });
    filterIds.forEach(function (id) { $(id).addEventListener(id === "minMo" || id === "maxMo" ? "input" : "change", apply); });

    $$(".pill").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.dataset.pill;
        if (k === "zero") setVal("onlyZeroDas", !val("onlyZeroDas"));
        else if (k === "notrade") setVal("noTrade", !val("noTrade"));
        else if (k === "nonewline") setVal("noNewLine", !val("noNewLine"));
        else if (k === "u350") setVal("maxMo", val("maxMo") === "350" ? "" : "350");
        else if (k === "new") setVal("onlyNew", !val("onlyNew"));
        else if (k === "saved") state.saved = !state.saved;
        else if (k === "since") state.since = !state.since;
        apply();
      });
    });

    function reset() {
      filterIds.forEach(function (id) { setVal(id, ""); });
      $("q").value = ""; state.saved = false; state.since = false; state.nomil = false; state.cats = [];
      apply();
    }
    $("reset").addEventListener("click", reset);
    $("emptyReset").addEventListener("click", reset);

    // Phone filter drawer
    var opener = $("openFilters"), scrim = $("scrim"), rail = $("filters");
    function openF() { document.body.classList.add("filters-open"); scrim.hidden = false; opener.setAttribute("aria-expanded", "true"); rail.focus(); }
    function closeF() { document.body.classList.remove("filters-open"); scrim.hidden = true; opener.setAttribute("aria-expanded", "false"); opener.focus(); }
    opener.addEventListener("click", openF);
    $("closeFilters").addEventListener("click", closeF);
    $("applyFilters").addEventListener("click", function () { closeF(); $("offers").scrollIntoView({ block: "start" }); });
    scrim.addEventListener("click", closeF);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && document.body.classList.contains("filters-open")) closeF(); });

    var tw = document.querySelector(".toolbar-wrap");
    if (tw && "IntersectionObserver" in window) {
      var sentinel = document.createElement("div");
      tw.parentNode.insertBefore(sentinel, tw);
      new IntersectionObserver(function (e) { tw.classList.toggle("stuck", !e[0].isIntersecting); }).observe(sentinel);
    }
    apply();
  }
  paintSaved();

  // ---------- "What can I get?" quiz
  var sheet = $("match");
  if (sheet) {
    var offersData = null, answers = {}, step = 0, lastFocus = null;
    var NEEDS = [
      { v: "car", label: "A car", sub: "Lease or loan", cats: ["Car lease", "Car financing"], page: "/" },
      { v: "home", label: "A home", sub: "Mortgage with 0% down", cats: ["Home loan"], page: "/home-loans/" },
      { v: "phone", label: "A phone", sub: "Free or $0 down", cats: ["Phone"], page: "/phones/" },
      { v: "solar", label: "Solar or home upgrades", sub: "$0 at installation", cats: ["Home improvement"], page: "/home-improvement/" },
      { v: "all", label: "Show me everything", sub: "All zero-down deals", cats: [], page: "/" }
    ];
    function need() { return NEEDS.filter(function (n) { return n.v === answers.need; })[0] || NEEDS[4]; }
    function questions() {
      var qs = [{ k: "need", q: "What are you shopping for?", opts: NEEDS.map(function (n) { return { v: n.v, label: n.label, sub: n.sub }; }) }];
      var n = answers.need;
      if (n === "car" || n === "home" || n === "all") {
        qs.push({ k: "mil", q: "Have you served in the military, or are you a military spouse?", opts: [{ v: "yes", label: "Yes" }, { v: "no", label: "No" }] });
        qs.push({ k: "credit", q: "How would you describe your credit?", opts: [
          { v: "excellent", label: "Excellent", sub: "About 720 or higher" }, { v: "good", label: "Good", sub: "About 670 to 719" },
          { v: "fair", label: "Fair or building", sub: "Below about 670" }, { v: "unsure", label: "Not sure" }] });
      }
      if (n === "phone") {
        qs.push({ k: "switch", q: "Would you switch carriers or add a new line?", opts: [{ v: "yes", label: "Yes, I’m open to it" }, { v: "no", label: "No, I want to stay put" }] });
        qs.push({ k: "trade", q: "Do you have a phone you could trade in?", opts: [{ v: "yes", label: "Yes" }, { v: "no", label: "No" }] });
      }
      if (n === "solar") {
        qs.push({ k: "own", q: "Do you own your home?", opts: [{ v: "yes", label: "Yes" }, { v: "no", label: "No, I rent" }] });
      }
      return qs;
    }
    function matches(o) {
      var nd = need();
      var reqs = (o.requirements || []).join(" ").toLowerCase();
      if (o.expires && o.expires < today) return false;
      if (nd.cats.length && nd.cats.indexOf(o.category) === -1) return false;
      if (answers.mil === "no" && /military|veteran/.test(reqs)) return false;
      if (answers["switch"] === "no" && /new line|switch/.test(reqs)) return false;
      if (answers.trade === "no" && /trade-in/.test(reqs) && !/or trade-in|trade-in or/.test(reqs)) return false;
      return true;
    }
    function resultUrl() {
      var nd = need(), p = new URLSearchParams();
      if (nd.v === "car") p.set("cat", nd.cats.join(","));
      if (answers.mil === "no") p.set("nomil", "1");
      if (answers["switch"] === "no") p.set("nonewline", "1");
      if (answers.trade === "no") p.set("notrade", "1");
      var qs = p.toString();
      return nd.page + (qs ? "?" + qs : "") + "#offers";
    }
    function notes() {
      var out = [];
      if (answers.mil === "yes" && (answers.need === "home" || answers.need === "all")) out.push("You may qualify for a VA loan, the strongest zero-down mortgage: no down payment and no monthly mortgage insurance.");
      if (answers.credit === "fair") out.push(answers.need === "home"
        ? "VA and USDA loans have no official minimum score, but most lenders want about 580 to 640. A housing counselor can help you get ready."
        : "Advertised $0-down leases usually need top-tier credit. A credit-union loan or a cosigner may be your best route for now.");
      if (answers.credit === "good" && answers.need === "car") out.push("Many $0-due-at-signing leases still work at good credit, but the lowest advertised payments assume excellent credit.");
      if (answers.own === "no") out.push("Solar financing needs a homeowner. Renters can look at community solar programs from their utility instead.");
      if (answers.need === "phone") out.push("Free phones are paid through 36 months of bill credits. Leaving early ends the credits.");
      return out;
    }
    function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
    function render() {
      var qs = questions(), box = $("quiz");
      $("qbar").style.width = Math.min(100, Math.round((step / qs.length) * 100)) + "%";
      if (step < qs.length) {
        var q = qs[step];
        box.innerHTML = '<p class="q-step">Question ' + (step + 1) + " of " + qs.length + '</p><h3 class="q-q">' + esc(q.q) + '</h3><div class="q-opts">' +
          q.opts.map(function (o) {
            return '<button type="button" class="q-opt" data-v="' + o.v + '"' + (answers[q.k] === o.v ? ' aria-pressed="true"' : "") + '><span>' + esc(o.label) + "</span>" + (o.sub ? '<small>' + esc(o.sub) + "</small>" : "") + "</button>";
          }).join("") + "</div>" + (step > 0 ? '<button type="button" class="q-back">← Back</button>' : "");
        $$(".q-opt", box).forEach(function (b) {
          b.addEventListener("click", function () {
            answers[q.k] = b.dataset.v;
            if (q.k === "need") { answers = { need: b.dataset.v }; }
            step++; render();
          });
        });
        var back = box.querySelector(".q-back"); if (back) back.addEventListener("click", function () { step--; render(); });
        var first = box.querySelector(".q-opt"); if (first) first.focus();
        return;
      }
      box.innerHTML = '<p class="q-step">Your matches</p><h3 class="q-q">Finding offers…</h3>';
      getOffers(function (data) {
        var n = data ? data.filter(matches).length : null;
        var ns = notes();
        box.innerHTML = '<p class="q-step">Your matches</p><h3 class="q-q">' +
          (n === null ? "Your matching offers are ready" : n === 0 ? "No exact matches today" : "We found " + n + (n === 1 ? " offer" : " offers") + " for you") + "</h3>" +
          (ns.length ? '<ul class="q-notes">' + ns.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : "") +
          (n === 0 ? '<p class="q-sub">New offers arrive every morning. Get an alert when one matches.</p>' : "") +
          '<div class="q-actions">' + (n === 0 ? '<a class="btn-primary" href="#alerts" data-close-match>Get deal alerts</a>' : '<a class="btn-primary" href="' + resultUrl() + '">Show my offers</a>') +
          '<button type="button" class="btn-ghost q-restart">Start over</button></div>';
        $("qbar").style.width = "100%";
        box.querySelector(".q-restart").addEventListener("click", function () { answers = {}; step = 0; render(); });
        var go = box.querySelector(".q-actions .btn-primary"); if (go) go.focus();
      });
    }
    function getOffers(cb) {
      if (offersData) return cb(offersData);
      fetch("/offers.json", { cache: "no-store" }).then(function (r) { return r.json(); })
        .then(function (d) { offersData = d.offers || []; cb(offersData); }, function () { cb(null); });
    }
    function openM() {
      lastFocus = document.activeElement; answers = {}; step = 0;
      sheet.hidden = false; document.body.classList.add("sheet-open");
      requestAnimationFrame(function () { sheet.classList.add("open"); });
      render(); getOffers(function () {});
    }
    function closeM() {
      sheet.classList.remove("open"); document.body.classList.remove("sheet-open");
      setTimeout(function () { sheet.hidden = true; }, 200);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    document.addEventListener("click", function (e) {
      if (e.target.closest("[data-open-match]")) { e.preventDefault(); openM(); return; }
      if (e.target.closest("[data-close-match]")) { closeM(); return; }
      if (e.target === sheet) closeM();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !sheet.hidden) closeM(); });
    if (location.hash === "#match") openM();
  }
})();
