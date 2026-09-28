/* Awesome Indian Exams: free study tools (planner, flashcards, marks calculator).
 * No login, no tracking, no network calls except this site's own data files. Progress is saved only in the
 * student's own browser (localStorage), so it works offline and never leaves the device.
 * Data: window.AIE_DATA from data/data.js (works from a downloaded copy too), else data/exams.json. */
(function () {
  "use strict";

  var SCRIPT = document.currentScript && document.currentScript.src;
  var ROOT = SCRIPT ? new URL("..", SCRIPT) : new URL("/", location.href);
  var DIRECTORY_URLS = !/\.html?$/.test(location.pathname);
  var dataPromise = null;

  // ---------- helpers ----------
  function load(key, fallback) {
    try {
      var v = JSON.parse(localStorage.getItem(key));
      return v === null || v === undefined ? fallback : v;
    } catch (e) { return fallback; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* private mode: work without saving */ }
  }
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "on") Object.keys(attrs.on).forEach(function (ev) { n.addEventListener(ev, attrs.on[ev]); });
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function today() { return isoDate(new Date()); }
  function isoDate(d) {
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function addDays(iso, n) { var d = new Date(iso + "T00:00:00"); d.setDate(d.getDate() + n); return isoDate(d); }
  function daysBetween(a, b) { return Math.round((new Date(b + "T00:00:00") - new Date(a + "T00:00:00")) / 86400000); }
  function pageUrl(mdPath) {   // "modules/quant-aptitude.md" -> link that works online and in the offline copy
    var p = mdPath.replace(/\.md$/, "");
    return new URL(DIRECTORY_URLS ? p + "/" : p + ".html", ROOT).href;
  }
  function getData() {
    if (!dataPromise) {
      dataPromise = window.AIE_DATA ? Promise.resolve(window.AIE_DATA)
        : fetch(new URL("data/exams.json", ROOT)).then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        }).then(function (exams) { return { exams: exams, decks: {} }; });
    }
    return dataPromise;
  }
  function fail(root, msg) {
    root.innerHTML = "";
    root.appendChild(el("p", { class: "aie-note", text: msg }));
  }

  // ---------- study planner ----------
  var PKEY = "aie.planner.v1";

  function planner(root) {
    var state = load(PKEY, { exam: "", target: "", done: {}, streak: { last: "", count: 0 }, focus: {} });
    root.innerHTML = "";
    root.appendChild(el("p", { class: "aie-note", text: "Loading the exam list…" }));
    getData().then(function (data) {
      var exams = data.exams.exams, fams = {};
      data.exams.families.forEach(function (f) { fams[f.id] = f.title; });
      var mods = {};
      data.exams.modules.forEach(function (m) { mods[m.id] = m; });
      root.innerHTML = "";

      var select = el("select", { id: "aie-exam", "aria-label": "Your exam" }, [el("option", { value: "", text: "Choose your exam…" })]);
      var groups = {};
      exams.forEach(function (ex) {
        var g = groups[ex.family];
        if (!g) { g = groups[ex.family] = el("optgroup", { label: fams[ex.family] || ex.family }); select.appendChild(g); }
        g.appendChild(el("option", { value: ex.id, text: ex.name }));
      });
      select.value = state.exam || "";
      var target = el("input", { type: "date", id: "aie-target", "aria-label": "Exam date", value: state.target || "" });
      var out = el("div", { class: "aie-plan" });
      root.appendChild(el("div", { class: "aie-row" }, [
        el("label", {}, ["Exam ", select]), el("label", {}, ["Exam date ", target])
      ]));
      root.appendChild(out);
      root.appendChild(focusTimer(state));

      function render() {
        out.innerHTML = "";
        var ex = exams.filter(function (e) { return e.id === state.exam; })[0];
        if (!ex) { out.appendChild(el("p", { class: "aie-note", text: "Choose an exam to see every shared module it needs." })); return; }
        var links = el("p", {}, []);
        if (ex.page) links.appendChild(el("a", { href: pageUrl(ex.page.path), text: "Exam page" }));
        if (ex.official_site) { links.appendChild(document.createTextNode(" · ")); links.appendChild(el("a", { href: ex.official_site, rel: "noopener", text: "Official website" })); }
        out.appendChild(links);

        var done = state.done[ex.id] || {};
        var list = el("ul", { class: "aie-checklist" });
        ex.modules.forEach(function (mid) {
          var m = mods[mid] || { title: mid };
          var box = el("input", { type: "checkbox", id: "aie-m-" + mid });
          box.checked = !!done[mid];
          box.addEventListener("change", function () {
            done[mid] = box.checked; state.done[ex.id] = done; bumpStreak(state); save(PKEY, state); render();
          });
          var label = m.page ? el("a", { href: pageUrl(m.page), text: m.title }) : el("span", { text: m.title });
          list.appendChild(el("li", {}, [box, " ", label, el("span", { class: "aie-muted", text: " · counts for " + (m.exams ? m.exams.length : 1) + " exams" })]));
        });
        var n = ex.modules.length, k = ex.modules.filter(function (m) { return done[m]; }).length;
        out.appendChild(el("p", {}, [el("strong", { text: k + " of " + n + " modules done" })]));
        out.appendChild(el("progress", { max: String(n || 1), value: String(k) }));
        out.appendChild(list);

        var left = ex.modules.filter(function (m) { return !done[m]; });
        if (state.target && left.length) {
          var days = daysBetween(today(), state.target);
          if (days <= 0) { out.appendChild(el("p", { class: "aie-note", text: "The exam date has passed. Set your next attempt's date." })); }
          else {
            // Leave the last sixth of the time (at least a week) for full mocks and revision.
            var revise = Math.max(7, Math.round(days / 6)), study = Math.max(1, days - revise), per = study / left.length;
            var table = el("table", {}, [el("thead", {}, [el("tr", {}, [el("th", { text: "From" }), el("th", { text: "To" }), el("th", { text: "Module" })])])]);
            var body = el("tbody");
            left.forEach(function (mid, i) {
              var a = addDays(today(), Math.floor(i * per)), b = addDays(today(), Math.max(Math.floor(i * per), Math.floor((i + 1) * per) - 1));
              body.appendChild(el("tr", {}, [el("td", { text: a }), el("td", { text: b }), el("td", { text: (mods[mid] || { title: mid }).title })]));
            });
            body.appendChild(el("tr", {}, [el("td", { text: addDays(today(), study) }), el("td", { text: addDays(state.target, -1) }), el("td", { text: "Full mocks, previous papers and revision" })]));
            table.appendChild(body);
            out.appendChild(el("h3", { text: days + " days left: your plan" }));
            out.appendChild(table);
            out.appendChild(el("p", { class: "aie-muted", text: "Start each module with its previous-year questions, then the free resources on its page. Tick it off when you can solve its PYQs." }));
          }
        } else if (!state.target) {
          out.appendChild(el("p", { class: "aie-note", text: "Set your exam date (from the official notification) to get a week-by-week plan." }));
        }
      }
      select.addEventListener("change", function () { state.exam = select.value; save(PKEY, state); render(); });
      target.addEventListener("change", function () { state.target = target.value; save(PKEY, state); render(); });
      render();
    }).catch(function () { fail(root, "The exam list could not be loaded. Open this page on the website or in the downloaded offline copy."); });
  }

  function bumpStreak(state) {
    var t = today(), s = state.streak || { last: "", count: 0 };
    if (s.last === t) return;
    s.count = s.last === addDays(t, -1) ? s.count + 1 : 1;
    s.last = t; state.streak = s;
  }

  function focusTimer(state) {
    var box = el("div", { class: "aie-focus" });
    var display = el("span", { class: "aie-clock", text: "25:00" });
    var info = el("span", { class: "aie-muted" });
    var timer = null, left = 25 * 60, mode = "focus";
    function paint() {
      display.textContent = String(Math.floor(left / 60)).padStart(2, "0") + ":" + String(left % 60).padStart(2, "0");
      var s = state.streak || { count: 0, last: "" };
      var live = s.last === today() || s.last === addDays(today(), -1) ? s.count : 0;
      info.textContent = " · focus sessions today: " + ((state.focus || {})[today()] || 0) + " · streak: " + live + " day" + (live === 1 ? "" : "s");
    }
    function stop() { if (timer) clearInterval(timer); timer = null; start.textContent = "Start"; }
    var start = el("button", { class: "md-button", type: "button", text: "Start", on: { click: function () {
      if (timer) { stop(); return; }
      start.textContent = "Pause";
      timer = setInterval(function () {
        left -= 1;
        if (left <= 0) {
          stop();
          if (mode === "focus") {
            state.focus = state.focus || {}; state.focus[today()] = (state.focus[today()] || 0) + 1;
            bumpStreak(state); save(PKEY, state); mode = "break"; left = 5 * 60;
          } else { mode = "focus"; left = 25 * 60; }
        }
        paint();
      }, 1000);
    } } });
    var reset = el("button", { class: "md-button", type: "button", text: "Reset", on: { click: function () { stop(); mode = "focus"; left = 25 * 60; paint(); } } });
    box.appendChild(el("h3", { text: "Focus timer" }));
    box.appendChild(el("p", {}, [display, info]));
    box.appendChild(el("p", {}, [start, " ", reset]));
    box.appendChild(el("p", { class: "aie-muted", text: "25 minutes of focus, then a 5-minute break. Each finished session counts towards your daily streak." }));
    paint();
    return box;
  }

  // ---------- flashcards (Leitner boxes: a simple, robust spaced repetition) ----------
  var FKEY = "aie.flashcards.v1";
  var INTERVALS = [0, 1, 3, 7, 16, 35];   // days until the next review, by box

  function flashcards(root) {
    root.innerHTML = "";
    root.appendChild(el("p", { class: "aie-note", text: "Loading decks…" }));
    getData().then(function (data) {
      var decks = data.decks || {}, ids = Object.keys(decks);
      if (!ids.length) { fail(root, "No decks found. Open this page on the website or in the downloaded offline copy."); return; }
      var progress = load(FKEY, {});
      root.innerHTML = "";
      var select = el("select", { "aria-label": "Deck" }, ids.map(function (id) { return el("option", { value: id, text: decks[id].title }); }));
      var stage = el("div", { class: "aie-card-stage" });
      root.appendChild(el("div", { class: "aie-row" }, [el("label", {}, ["Deck ", select])]));
      root.appendChild(stage);

      function next() {
        var deck = decks[select.value], p = progress[deck.id] = progress[deck.id] || {};
        var t = today();
        var due = deck.cards.filter(function (c) { return !p[c.id] || p[c.id].due <= t; });
        var learnt = deck.cards.filter(function (c) { return p[c.id] && p[c.id].box >= 4; }).length;
        stage.innerHTML = "";
        stage.appendChild(el("p", { class: "aie-muted", text: due.length + " due today · " + learnt + " of " + deck.cards.length + " learnt" }));
        if (!due.length) {
          stage.appendChild(el("p", { class: "aie-note", text: "All done for today. Come back tomorrow: reviewing on the right day is what makes it stick." }));
          return;
        }
        // Newest-first would overwhelm; take the most overdue (or new) card first.
        due.sort(function (a, b) { return ((p[a.id] || {}).due || "") < ((p[b.id] || {}).due || "") ? -1 : 1; });
        var card = due[0];
        var back = el("div", { class: "aie-back", hidden: "hidden" }, [
          el("p", { text: card.back }),
          deck.source ? el("p", { class: "aie-muted" }, ["Source: ", el("a", { href: deck.source.url, rel: "noopener", text: deck.source.title })]) : null
        ]);
        function grade(ok) {
          var s = p[card.id] || { box: 0, due: t };
          s.box = ok ? Math.min(s.box + 1, INTERVALS.length - 1) : 0;
          s.due = addDays(t, ok ? INTERVALS[s.box] : 1);   // missed cards come back tomorrow
          p[card.id] = s; save(FKEY, progress); next();
        }
        var buttons = el("p", { hidden: "hidden" }, [
          el("button", { class: "md-button", type: "button", text: "Missed it", on: { click: function () { grade(false); } } }), " ",
          el("button", { class: "md-button md-button--primary", type: "button", text: "Got it", on: { click: function () { grade(true); } } })
        ]);
        var show = el("button", { class: "md-button md-button--primary", type: "button", text: "Show answer", on: { click: function () {
          back.removeAttribute("hidden"); buttons.removeAttribute("hidden"); show.setAttribute("hidden", "hidden");
        } } });
        stage.appendChild(el("div", { class: "aie-card" }, [el("p", { class: "aie-front", text: card.front }), back]));
        stage.appendChild(el("p", {}, [show]));
        stage.appendChild(buttons);
      }
      select.addEventListener("change", next);
      next();
    }).catch(function () { fail(root, "Decks could not be loaded. Open this page on the website or in the downloaded offline copy."); });
  }

  // ---------- marks calculator ----------
  var PRESETS = [
    { label: "Custom", plus: 1, minus: 0 },
    { label: "+4 / −1 (NTA MCQs, e.g. JEE Main, NEET UG)", plus: 4, minus: 1 },
    { label: "+2 / −0.5 (SSC CGL Tier 1)", plus: 2, minus: 0.5 },
    { label: "+1 / −0.25 (IBPS and SBI prelims)", plus: 1, minus: 0.25 },
    { label: "+2 / −0.66 (UPSC Prelims GS)", plus: 2, minus: 0.66 }
  ];

  function calculator(root) {
    root.innerHTML = "";
    function num(label, value, step) {
      var i = el("input", { type: "number", min: "0", step: step || "1", value: String(value) });
      return { input: i, label: el("label", {}, [label + " ", i]) };
    }
    var preset = el("select", { "aria-label": "Marking scheme" }, PRESETS.map(function (p, i) { return el("option", { value: String(i), text: p.label }); }));
    var total = num("Questions", 100), right = num("Correct", 0), wrong = num("Wrong", 0);
    var plus = num("Marks per correct", 1, "0.01"), minus = num("Marks lost per wrong", 0, "0.01");
    var out = el("div", { class: "aie-result", "aria-live": "polite" });
    function calc() {
      var n = +total.input.value || 0, r = +right.input.value || 0, w = +wrong.input.value || 0;
      var a = +plus.input.value || 0, b = +minus.input.value || 0;
      out.innerHTML = "";
      if (r + w > n) { out.appendChild(el("p", { class: "aie-note", text: "Correct + wrong is more than the number of questions." })); return; }
      var score = r * a - w * b, max = n * a, attempted = r + w;
      out.appendChild(el("p", {}, [el("strong", { text: "Score: " + (Math.round(score * 100) / 100) + " / " + max })]));
      out.appendChild(el("p", { text: "Attempted " + attempted + " · accuracy " + (attempted ? Math.round(100 * r / attempted) : 0) + "% · marks lost to negative marking " + (Math.round(w * b * 100) / 100) }));
      if (b > 0 && a > 0) {
        out.appendChild(el("p", { class: "aie-muted", text: "A guess pays off on average only if you can rule out enough options: with 4 options and these marks, a blind guess is worth " + (Math.round((a / 4 - b * 3 / 4) * 100) / 100) + " marks." }));
      }
    }
    preset.addEventListener("change", function () {
      var p = PRESETS[+preset.value]; plus.input.value = p.plus; minus.input.value = p.minus; calc();
    });
    [total, right, wrong, plus, minus].forEach(function (f) { f.input.addEventListener("input", calc); });
    root.appendChild(el("div", { class: "aie-row" }, [el("label", {}, ["Marking scheme ", preset])]));
    root.appendChild(el("div", { class: "aie-row" }, [total.label, right.label, wrong.label]));
    root.appendChild(el("div", { class: "aie-row" }, [plus.label, minus.label]));
    root.appendChild(out);
    calc();
  }

  // ---------- share bar (WhatsApp first: it is how most Indian students pass links on) ----------
  var SITE = "https://lakhidas168-ship-it.github.io/awesome-indian-exams/";

  function publicUrl() {   // the page's address on the website, even when read from the offline copy
    if (/^https?:$/.test(location.protocol)) return location.href.split("#")[0];
    var rel = location.href.slice(ROOT.href.length).split("#")[0].replace(/(^|\/)index\.html$/, "$1").replace(/\.html$/, "/");
    return SITE + rel;
  }

  function shareBar() {
    var h1 = document.querySelector(".md-content__inner h1, article h1");
    if (!h1 || document.querySelector(".aie-share")) return;
    var url = publicUrl(), title = document.title.replace(/ - Awesome Indian Exams$/, "");
    var text = title + " — free on Awesome Indian Exams: " + url;
    var bar = el("div", { class: "aie-share", role: "group", "aria-label": "Share this page" }, [
      el("a", { class: "md-button aie-wa", href: "https://wa.me/?text=" + encodeURIComponent(text), target: "_blank", rel: "noopener", text: "WhatsApp" }),
      el("a", { class: "md-button", href: "https://t.me/share/url?url=" + encodeURIComponent(url) + "&text=" + encodeURIComponent(title), target: "_blank", rel: "noopener", text: "Telegram" }),
      el("button", { class: "md-button", type: "button", text: "Copy link", on: { click: function (e) {
        var b = e.currentTarget;
        function done() { b.textContent = "Copied ✓"; setTimeout(function () { b.textContent = "Copy link"; }, 2000); }
        if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, function () { prompt("Copy this link:", url); });
        else prompt("Copy this link:", url);
      } } })
    ]);
    if (navigator.share) {
      bar.appendChild(el("button", { class: "md-button", type: "button", text: "Share…", on: { click: function () {
        navigator.share({ title: title, text: title + " — free on Awesome Indian Exams", url: url }).catch(function () {});
      } } }));
    }
    h1.insertAdjacentElement("afterend", bar);
  }

  // ---------- daily question (one question a day for everyone, like Wordle; share the result, not the answer) ----------
  var DKEY = "aie.daily.v1";
  var EPOCH = "2026-10-01";   // question #1

  function rng(seed) {   // small deterministic generator, so everyone gets the same options in the same order
    return function () { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  }

  function dailyPool(data) {
    var pool = [];
    (data.questions || []).forEach(function (q) {
      pool.push({ id: "q:" + q.id, question: q.question, options: q.options.slice(), answer: q.answer,
                  explain: q.solution, source: "Original question by " + q.author + " (" + q.license + ")" });
    });
    Object.keys(data.decks || {}).sort().forEach(function (did) {
      var deck = data.decks[did];
      deck.cards.forEach(function (c) { pool.push({ id: "c:" + did + ":" + c.id, card: c, deck: deck }); });
    });
    pool.sort(function (a, b) { return a.id < b.id ? -1 : 1; });
    return pool;
  }

  function dailyItem(data, day) {
    var pool = dailyPool(data);
    if (!pool.length) return null;
    // A fixed shuffle, walked one step a day: no repeats until every question has had its day.
    var mix = rng(20261001);
    for (var k = pool.length - 1; k > 0; k--) { var x = Math.floor(mix() * (k + 1)); var y = pool[k]; pool[k] = pool[x]; pool[x] = y; }
    var r = rng(day * 7919 + 17), item = pool[(day - 1) % pool.length];
    if (item.card) {   // turn a flashcard into a question with three wrong options from the same deck
      var others = item.deck.cards.filter(function (c) { return c.id !== item.card.id; }).map(function (c) { return c.back; });
      var opts = [item.card.back];
      while (opts.length < 4 && others.length) opts.push(others.splice(Math.floor(r() * others.length), 1)[0]);
      item = { id: item.id, question: item.card.front, options: opts, answer: item.card.back, explain: item.card.back,
               source: item.deck.source ? item.deck.source.title : item.deck.title, sourceUrl: item.deck.source && item.deck.source.url };
    } else {
      item = JSON.parse(JSON.stringify(item));
      var m = /^[A-Z]$/.exec(item.answer || "");
      if (m) item.answer = item.options[item.answer.charCodeAt(0) - 65];
    }
    for (var i = item.options.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)); var t = item.options[i]; item.options[i] = item.options[j]; item.options[j] = t; }
    return item;
  }

  function daily(root) {
    root.innerHTML = "";
    getData().then(function (data) {
      var t = today(), day = daysBetween(EPOCH, t) + 1;
      if (day < 1) day = 1;
      var item = dailyItem(data, day);
      if (!item) { fail(root, "No questions yet. Open this page on the website or in the offline copy."); return; }
      var st = load(DKEY, { last: "", streak: 0, results: {} });
      var mine = st.results[t];
      root.innerHTML = "";
      root.appendChild(el("p", { class: "aie-muted", text: "आज का सवाल · Question of the day #" + day + " · " + t }));
      root.appendChild(el("div", { class: "aie-card" }, [el("p", { class: "aie-front", text: item.question })]));
      var list = el("div", { class: "aie-options" });
      var out = el("div", { class: "aie-result", "aria-live": "polite" });
      function finish(choice) {
        var ok = choice === item.answer;
        if (!st.results[t]) {
          st.streak = ok ? (st.last === addDays(t, -1) ? st.streak + 1 : 1) : 0;
          st.last = t; st.results[t] = { choice: choice, ok: ok }; save(DKEY, st);
        }
        render();
      }
      function render() {
        list.innerHTML = ""; out.innerHTML = "";
        var res = st.results[t];
        item.options.forEach(function (o, i) {
          var b = el("button", { class: "md-button aie-option", type: "button", text: String.fromCharCode(65 + i) + ". " + o });
          if (res) {
            b.disabled = true;
            if (o === item.answer) b.classList.add("aie-right");
            else if (o === res.choice) b.classList.add("aie-wrong");
          } else b.addEventListener("click", function () { finish(o); });
          list.appendChild(b);
        });
        if (!res) return;
        out.appendChild(el("p", {}, [el("strong", { text: res.ok ? "सही! Correct." : "Not this time. Answer: " + item.answer })]));
        out.appendChild(el("p", { text: item.explain }));
        out.appendChild(el("p", { class: "aie-muted" }, ["Source: ", item.sourceUrl ? el("a", { href: item.sourceUrl, rel: "noopener", text: item.source }) : item.source]));
        var msg = "Awesome Indian Exams · आज का सवाल #" + day + "\n" + (res.ok ? "✅ सही" : "❌ गलत") +
                  (st.streak > 1 ? " · 🔥 " + st.streak + " दिन" : "") + "\nFree daily question for every exam aspirant: " + SITE + "tools/daily/";
        out.appendChild(el("p", {}, [
          el("a", { class: "md-button md-button--primary aie-wa", href: "https://wa.me/?text=" + encodeURIComponent(msg), target: "_blank", rel: "noopener", text: "Share result on WhatsApp" }),
          " ", el("span", { class: "aie-muted", text: "(the answer stays hidden)" })
        ]));
        out.appendChild(el("p", { class: "aie-muted", text: "Come back tomorrow for #" + (day + 1) + ". Streak: " + (st.streak || 0) + " day" + (st.streak === 1 ? "" : "s") + "." }));
      }
      root.appendChild(list); root.appendChild(out); render();
    }).catch(function () { fail(root, "The question could not be loaded. Open this page on the website or in the downloaded offline copy."); });
  }

  // ---------- installable app and offline reading (service worker; the website only, not the file:// copy) ----------
  function registerWorker() {
    if (!("serviceWorker" in navigator) || !/^https?:$/.test(location.protocol)) return;
    navigator.serviceWorker.register(new URL("sw.js", ROOT).href).catch(function () { /* optional */ });
  }

  // ---------- boot (works with Material's instant navigation and with plain page loads) ----------
  function boot() {
    var p = document.getElementById("aie-planner"); if (p) planner(p);
    var f = document.getElementById("aie-flashcards"); if (f) flashcards(f);
    var c = document.getElementById("aie-calculator"); if (c) calculator(c);
    var d = document.getElementById("aie-daily"); if (d) daily(d);
    shareBar();
  }
  registerWorker();
  if (window.document$ && typeof window.document$.subscribe === "function") window.document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  // For tests.
  window.AIE_TOOLS = { addDays: addDays, daysBetween: daysBetween, INTERVALS: INTERVALS, PRESETS: PRESETS, dailyItem: dailyItem };
})();
