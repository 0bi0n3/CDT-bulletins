(() => {
  const $ = (id) => document.getElementById(id);
  const fmt = new Intl.DateTimeFormat("en-GB", { dateStyle: "long" });
  const fmtTime = new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short" });
  let all = [], section = "All";

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  // Only allow http(s)/relative links so a bad entry can't inject javascript: URLs.
  const safeUrl = (u) => {
    try { const x = new URL(u, location.href); return /^https?:$/.test(x.protocol) ? x.href : null; }
    catch { return null; }
  };

  function story(b, lead) {
    const a = el(lead ? "article" : "article", lead ? "" : "story");
    const tag = el("div", "tag");
    if (b.breaking) tag.append(el("span", "flash", "Breaking"));
    tag.append(document.createTextNode(b.category || "News"));
    const h = el(lead ? "h2" : "h3");
    if (b.slug) { const l = el("a", "", b.title); l.href = "story/" + b.slug + ".html"; l.style.textDecoration = "none"; h.append(l); }
    else h.textContent = b.title;
    a.append(tag, h);
    if (b.summary) a.append(el("p", lead ? "summary" : "", b.summary));
    if (b.body) b.body.split(/\n{2,}/).forEach((p) => a.append(el("p", "", p)));
    const meta = el("div", "meta", ["The Editors", fmtTime.format(new Date(b.date))].filter(Boolean).join(" · "));
    a.append(meta);
    const href = b.link && safeUrl(b.link);
    if (href) {
      const l = el("a", "read", "Read more →");
      l.href = href; l.rel = "noopener";
      a.append(l);
    }
    return a;
  }

  function render() {
    const q = $("q").value.trim().toLowerCase();
    const list = all.filter((b) =>
      (section === "All" || b.category === section) &&
      (!q || [b.title, b.summary, b.body, b.category].join(" ").toLowerCase().includes(q)));
    const lead = $("lead"), grid = $("grid");
    lead.replaceChildren(); grid.replaceChildren();
    $("empty").hidden = list.length > 0;
    list.forEach((b, i) => (i === 0 ? lead : grid).append(story(b, i === 0)));
  }

  function renderSections() {
    const cats = ["All", ...new Set(all.map((b) => b.category).filter(Boolean))];
    const nav = $("sections");
    nav.replaceChildren(...cats.map((c) => {
      const btn = el("button", "", c);
      btn.type = "button";
      btn.setAttribute("aria-pressed", String(c === section));
      btn.onclick = () => { section = c; renderSections(); render(); };
      return btn;
    }));
  }

  function renderTicker() {
    const items = all.filter((b) => b.breaking);
    $("breaking").hidden = items.length === 0;
    if (!items.length) return;
    const track = $("ticker");
    track.replaceChildren(...items.map((b) => el("span", "", b.title)));
    track.style.setProperty("--dur", Math.max(20, items.reduce((n, b) => n + b.title.length, 0) * 0.25) + "s");
  }

  $("today").textContent = fmt.format(new Date());
  $("q").addEventListener("input", render);

  fetch("bulletins.json", { cache: "no-cache" })
    .then((r) => r.json())
    .then((d) => {
      if (d.edition) $("edition").textContent = d.edition;
      all = (d.bulletins || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date));
      renderTicker(); renderSections(); render();
    })
    .catch(() => { $("lead").append(el("p", "empty", "Could not load bulletins.json.")); });
})();
