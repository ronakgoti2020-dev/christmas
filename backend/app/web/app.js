const app = document.getElementById("app");
const tokenKey = "ss_token";
const api = "";

const state = { user: null, error: "", notice: "" };

function token() { return localStorage.getItem(tokenKey); }
function authHeaders() {
  const t = token();
  return t ? { Authorization: `Bearer ${t}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
}
function path() {
  return location.pathname + location.search;
}
function go(href) {
  history.pushState({}, "", href);
  render();
}
async function req(url, opts = {}) {
  const res = await fetch(api + url, { ...opts, headers: { ...authHeaders(), ...(opts.headers || {}) } });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = { detail: text }; }
  if (!res.ok) {
    const detail = data && data.detail;
    throw new Error(typeof detail === "string" ? detail : (detail && detail.message) || res.statusText);
  }
  return data;
}
function nav() {
  const signed = Boolean(token());
  return `
    <header class="top">
      <a class="brand" href="/">🎅 SecretSanta</a>
      <nav>
        <a href="/how-it-works">How it works</a>
        <a href="/gift-ideas">Gift ideas</a>
        ${signed ? `<a href="/dashboard">Dashboard</a><button class="link" id="logout">Log out</button>` : `<a href="/login">Sign in</a><a class="btn" href="/register">Create account</a>`}
      </nav>
    </header>`;
}
function footer() {
  return `<footer class="footer"><a href="/about">About</a> · <a href="/privacy-policy">Privacy</a> · <a href="/terms">Terms</a> · <a href="/contact">Contact</a></footer>`;
}
function flash() {
  return `${state.error ? `<p class="error">${state.error}</p>` : ""}${state.notice ? `<p class="ok">${state.notice}</p>` : ""}`;
}
function layout(html) {
  app.innerHTML = nav() + `<main class="wrap">${flash()}${html}</main>` + footer();
  document.querySelectorAll("a[href^='/']").forEach((a) => {
    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey) return;
      e.preventDefault();
      go(a.getAttribute("href"));
    });
  });
  const out = document.getElementById("logout");
  if (out) out.onclick = () => { localStorage.removeItem(tokenKey); go("/"); };
}

async function home() {
  layout(`
    <section class="hero">
      <p class="chip">Christmas 2026 · year-round exchanges</p>
      <h1>Run a Secret Santa without the spreadsheet.</h1>
      <p class="muted">Create a group, share one invite link, collect wishlists, then draw names so everyone gives one gift and nobody draws themselves.</p>
      <div class="row">
        <a class="btn" href="${token() ? "/create-group" : "/register"}">Create a gift exchange</a>
        <a class="btn secondary" href="/how-it-works">See how it works</a>
      </div>
    </section>
    <div class="grid" style="margin-top:32px">
      <div class="card"><h3>Private by default</h3><p>Only the giver sees the recipient. The organizer cannot open the full mapping unless the group chooses that.</p></div>
      <div class="card"><h3>Fair draws</h3><p>The server assigns names in one transaction. No self-gifts, no duplicates, exclusions supported.</p></div>
      <div class="card"><h3>Wishlists that stay quiet</h3><p>Your ideas are visible to you and to your Secret Santa after the draw.</p></div>
    </div>
    <div class="ad-slot">Public pages may show ads later. Assignment and confirmation screens stay ad-free.</div>
  `);
}

const HOW_IT_WORKS = {
  title: "How Secret Santa works",
  steps: [
    { title: "Create a group", body: "Name the exchange, set a budget, date and privacy mode." },
    { title: "Invite people", body: "Share a unique join link over WhatsApp, email or messages." },
    { title: "Collect wishlists", body: "Everyone adds gift ideas. Only their Secret Santa can see them." },
    { title: "Draw names", body: "The organizer starts a fair random draw. Nobody gets themselves." },
    { title: "Give the gift", body: "Track shopping, shipping and delivery until the reveal." }
  ]
};

const GIFT_IDEAS = {
  title: "Secret Santa gift ideas",
  collections: [
    { title: "Office Secret Santa", ideas: ["Desk plant", "Good notebook", "Coffee sampler", "Noise-cancelling earplugs"] },
    { title: "Family gift exchange", ideas: ["Photo book", "Board game", "Hot chocolate kit", "Cozy socks"] },
    { title: "Christmas 2026", ideas: ["Fairy lights", "Recipe journal", "Reusable wrap kit", "Local artisan chocolate"] }
  ]
};

async function how() {
  let data = HOW_IT_WORKS;
  try { data = await req("/api/public/how-it-works"); } catch { /* keep local copy */ }
  const steps = data.steps || HOW_IT_WORKS.steps;
  layout(`<h1>${data.title || HOW_IT_WORKS.title}</h1>` + steps.map((s, i) => `<div class="card" style="margin:12px 0"><span class="chip">Step ${i + 1}</span><h3>${s.title}</h3><p>${s.body}</p></div>`).join("") + `<p><a class="btn" href="/create-group">Create a gift exchange</a></p>`);
}

async function ideas() {
  let data = GIFT_IDEAS;
  try { data = await req("/api/public/gift-ideas"); } catch { /* keep local copy */ }
  const collections = data.collections || GIFT_IDEAS.collections;
  layout(`<h1>${data.title || GIFT_IDEAS.title}</h1>` + collections.map((c) => `<div class="card" style="margin:12px 0"><h3>${c.title}</h3><ul>${c.ideas.map((i) => `<li>${i}</li>`).join("")}</ul></div>`).join("") + `<p><a class="btn" href="/create-group">Create a gift exchange</a></p>`);
}

function legal(title, body) {
  layout(`<h1>${title}</h1><div class="card"><p>${body}</p></div>`);
}

async function login() {
  layout(`
    <h1>Sign in</h1>
    <form id="f" class="card">
      <label>Email</label><input name="email" type="email" required>
      <label>Password</label><input name="password" type="password" required>
      <div class="row"><button class="btn" type="submit">Sign in</button><a href="/register">Create an account</a></div>
    </form>`);
  document.getElementById("f").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const data = await req("/api/auth/login", { method: "POST", body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }) });
      localStorage.setItem(tokenKey, data.access_token);
      go("/dashboard");
    } catch (err) { state.error = err.message; render(); }
  };
}

async function register() {
  layout(`
    <h1>Create your account</h1>
    <form id="f" class="card">
      <label>Full name</label><input name="full_name" required>
      <label>Email</label><input name="email" type="email" required>
      <label>Password</label><input name="password" type="password" required minlength="8">
      <label>Country</label><input name="country">
      <div class="row"><button class="btn" type="submit">Join SecretSanta</button></div>
    </form>`);
  document.getElementById("f").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const data = await req("/api/auth/register", { method: "POST", body: JSON.stringify(Object.fromEntries(fd)) });
      localStorage.setItem(tokenKey, data.access_token);
      go("/dashboard");
    } catch (err) { state.error = err.message; render(); }
  };
}

async function dashboard() {
  const data = await req("/api/dashboard");
  const groups = data.active_groups.map((g) => `
    <a class="card" href="/groups/${g.id}" style="text-decoration:none;color:inherit">
      <span class="chip">${g.event_type}</span>
      <h3>${g.name}</h3>
      <p>${g.currency} ${g.minimum_budget}–${g.maximum_budget} · ${g.participant_count} people</p>
      <p class="muted">Exchange ${g.event_date} · assignment ${g.assignment_status}</p>
    </a>`).join("");
  layout(`
    <h1>Hello ${data.user.full_name}</h1>
    <div class="row"><a class="btn" href="/create-group">Create a Gift Exchange</a></div>
    <div class="list" style="margin-top:20px">${groups || "<div class='card'>No groups yet. Create one and share the invite link.</div>"}</div>
  `);
}

async function createGroup() {
  layout(`
    <h1>Create a gift exchange</h1>
    <form id="f" class="card">
      <label>Group name</label><input name="name" required>
      <label>Description</label><textarea name="description"></textarea>
      <label>Occasion</label>
      <select name="event_type">
        <option value="christmas">Christmas</option>
        <option value="birthday">Birthday</option>
        <option value="office">Office</option>
        <option value="family">Family</option>
        <option value="friends">Friends</option>
        <option value="new_year">New Year</option>
        <option value="custom">Custom</option>
      </select>
      <label>Exchange date</label><input name="event_date" type="date" value="2026-12-25" required>
      <label>Registration closes</label><input name="registration_deadline" type="date" value="2026-12-15" required>
      <label>Minimum budget</label><input name="minimum_budget" type="number" value="20" required>
      <label>Maximum budget</label><input name="maximum_budget" type="number" value="50" required>
      <label>Currency</label><input name="currency" value="USD">
      <label>Country</label><input name="country" value="India">
      <label>Exchange type</label>
      <select name="exchange_type"><option value="physical">Physical</option><option value="digital">Digital</option><option value="both">Both</option></select>
      <label>Privacy</label>
      <select name="privacy_mode">
        <option value="secret">Secret Santa (organizer cannot see the mapping)</option>
        <option value="organizer">Organizer can see assignments</option>
        <option value="public">Public inside the group</option>
      </select>
      <div class="row"><button class="btn" type="submit">Create group</button></div>
    </form>`);
  document.getElementById("f").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    body.minimum_budget = Number(body.minimum_budget);
    body.maximum_budget = Number(body.maximum_budget);
    try {
      const group = await req("/api/groups", { method: "POST", body: JSON.stringify(body) });
      go(`/groups/${group.id}`);
    } catch (err) { state.error = err.message; render(); }
  };
}

async function groupPage(id) {
  const [group, people] = await Promise.all([req(`/api/groups/${id}`), req(`/api/groups/${id}/participants`)]);
  const isOrg = group.organizer_id === (await meSafe())?.id;
  const link = `${location.origin}/join/${group.invite_code}`;
  layout(`
    <span class="chip">${group.event_type}</span>
    <h1>${group.name}</h1>
    <p class="muted">${group.description || ""}</p>
    <div class="card">
      <p>Budget ${group.currency} ${group.minimum_budget}–${group.maximum_budget}</p>
      <p>Exchange ${group.event_date} · ${people.length} participants</p>
      <p>Privacy: ${group.privacy_mode} · draw: ${group.assignment_status}</p>
      ${isOrg ? `<p><strong>Invite link</strong><br><input value="${link}" readonly><div class="row">
        <a class="btn secondary" href="https://wa.me/?text=${encodeURIComponent("Join my Secret Santa: " + link)}" target="_blank">Share on WhatsApp</a>
        <button class="btn ghost" id="copy">Copy link</button></div></p>` : ""}
    </div>
    <div class="row">
      <a class="btn" href="/groups/${id}/wishlist">Wishlist</a>
      <a class="btn secondary" href="/groups/${id}/assignment">My assignment</a>
      <a class="btn ghost" href="/groups/${id}/gift-tracking">Gift tracking</a>
      <a class="btn ghost" href="/groups/${id}/reveal">Reveal</a>
    </div>
    ${isOrg && group.assignment_status !== "completed" ? `<div class="row"><button class="btn" id="draw">Start the draw</button></div>` : ""}
    <h2>People</h2>
    <div class="list">${people.map((p) => `<div class="card"><strong>${p.full_name}</strong> · ${p.role}<br><span class="chip">${p.wishlist_completed ? "wishlist ready" : "needs wishlist"}</span></div>`).join("")}</div>
  `);
  const copy = document.getElementById("copy");
  if (copy) copy.onclick = () => navigator.clipboard.writeText(link);
  const draw = document.getElementById("draw");
  if (draw) draw.onclick = async () => {
    try { await req(`/api/groups/${id}/assignments/draw`, { method: "POST" }); state.notice = "Assignments created. Check your assignment page."; go(`/groups/${id}`); }
    catch (err) { state.error = err.message; render(); }
  };
}

async function meSafe() {
  if (!token()) return null;
  if (state.user) return state.user;
  try { state.user = await req("/api/auth/me"); return state.user; } catch { return null; }
}

async function join(code) {
  const preview = await req(`/api/invitations/${code}`);
  const signed = Boolean(token());
  layout(`
    <h1>Join ${preview.name}</h1>
    <div class="card">
      <p>Hosted by ${preview.organizer_name}</p>
      <p>Budget ${preview.currency} ${preview.minimum_budget}–${preview.maximum_budget}</p>
      <p>Exchange ${preview.event_date}</p>
      ${preview.closed ? "<p class='error'>Registration has closed.</p>" : ""}
      ${preview.already_joined ? "<p class='ok'>You are already in this group.</p>" : ""}
    </div>
    <form id="f" class="card">
      ${signed ? "" : `
        <label>Full name</label><input name="full_name" required>
        <label>Email</label><input name="email" type="email" required>
        <label>Password</label><input name="password" type="password" required>
      `}
      <label>Gift preferences</label><textarea name="gift_preferences"></textarea>
      <label>Interests</label><input name="interests">
      <label><input type="checkbox" name="budget_acknowledged" checked> I accept the gift budget</label>
      <button class="btn" type="submit">Join group</button>
    </form>`);
  document.getElementById("f").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    body.budget_acknowledged = true;
    try {
      const result = await req(`/api/invitations/${code}/join`, { method: "POST", body: JSON.stringify(body) });
      if (result.access_token) localStorage.setItem(tokenKey, result.access_token);
      go("/dashboard");
    } catch (err) { state.error = err.message; render(); }
  };
}

async function wishlist(id) {
  const items = await req(`/api/groups/${id}/wishlist`);
  layout(`
    <h1>Your wishlist</h1>
    <p class="muted">Only you and your Secret Santa can see these ideas after the draw.</p>
    <form id="f" class="card">
      <label>Gift name</label><input name="title" required>
      <label>Description</label><textarea name="description"></textarea>
      <label>Product URL</label><input name="product_url">
      <label>Estimated price</label><input name="estimated_price" type="number">
      <label>Category</label>
      <select name="category"><option>technology</option><option>books</option><option>fashion</option><option>home</option><option>games</option><option>beauty</option><option>food</option><option>other</option></select>
      <button class="btn" type="submit">Add idea</button>
    </form>
    <div class="list">${items.map((i) => `<div class="card"><span class="chip">${i.category}</span><h3>${i.title}</h3><p>${i.description || ""}</p></div>`).join("")}</div>
  `);
  document.getElementById("f").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    if (body.estimated_price) body.estimated_price = Number(body.estimated_price);
    body.priority = "medium";
    try { await req(`/api/groups/${id}/wishlist`, { method: "POST", body: JSON.stringify(body) }); go(`/groups/${id}/wishlist`); }
    catch (err) { state.error = err.message; render(); }
  };
}

async function assignment(id) {
  try {
    const a = await req(`/api/groups/${id}/assignments/me`);
    layout(`
      <h1>You are Secret Santa for ${a.receiver_name}</h1>
      <div class="card">
        <p>Keep this private until the reveal.</p>
        <p>Budget ${a.currency} ${a.budget_min}–${a.budget_max}</p>
        <p>Exchange ${a.event_date}</p>
        <p>${a.receiver_preferences || ""}</p>
      </div>
      <h2>Their wishlist</h2>
      <div class="list">${a.wishlist.map((i) => `<div class="card"><h3>${i.title}</h3><p>${i.description || ""}</p><p>${i.product_url || ""}</p></div>`).join("") || "<p>No ideas yet.</p>"}</div>
      <form id="f" class="card">
        <label>Gift status</label>
        <select name="gift_status">
          ${["not_started","selected","purchased","packed","shipped","delivered","exchanged"].map((s) => `<option ${s === a.gift_status ? "selected" : ""}>${s}</option>`).join("")}
        </select>
        <button class="btn" type="submit">Update status</button>
      </form>`);
    document.getElementById("f").onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      try { await req(`/api/groups/${id}/gift-status`, { method: "PATCH", body: JSON.stringify(Object.fromEntries(fd)) }); state.notice = "Saved"; go(`/groups/${id}/assignment`); }
      catch (err) { state.error = err.message; render(); }
    };
  } catch (err) {
    layout(`<h1>Assignment</h1><p>${err.message}</p>`);
  }
}

async function gifts(id) {
  const rows = await req(`/api/groups/${id}/gift-tracking`);
  layout(`<h1>Gift tracking</h1><p class="muted">Progress only. Private gift notes stay with the giver.</p><div class="list">${rows.map((r) => `<div class="card"><strong>${r.full_name}</strong><br><span class="chip">${r.gift_status}</span></div>`).join("")}</div>`);
}

async function reveal(id) {
  const data = await req(`/api/groups/${id}/reveal`);
  layout(`
    <h1>Reveal</h1>
    <div class="card">
      ${data.unlocked ? "<p>It's time to open the gifts.</p>" : `<p>Countdown to ${data.event_date}.</p>`}
      ${(data.identities || []).map((i) => `<p>${i.giver} → ${i.receiver}</p>`).join("")}
    </div>
  `);
}

async function render() {
  state.error = "";
  const p = location.pathname.replace(/\/$/, "") || "/";
  try {
    if (p === "/") return home();
    if (p === "/how-it-works") return how();
    if (p === "/gift-ideas") return ideas();
    if (p === "/about") return legal("About SecretSanta", "SecretSanta is a gift-exchange platform. Assignments are created on the server and stay hidden according to each group's privacy mode.");
    if (p === "/privacy-policy") return legal("Privacy policy", "We store account details, membership, wishlists and assignments. Wishlists are visible only to you, your assigned giver, or the organizer if you allow it. We do not send private assignments to analytics. Email privacy@secretsanta.app to request deletion.");
    if (p === "/terms") return legal("Terms", "You are responsible for gifts you send. Do not harass anyone. Organizers control draws and resets.");
    if (p === "/contact") return legal("Contact", "hello@secretsanta.app for product questions. privacy@secretsanta.app for data requests.");
    if (p === "/login") return login();
    if (p === "/register") return register();
    if (p === "/dashboard") return dashboard();
    if (p === "/create-group") return createGroup();
    const joinMatch = p.match(/^\/join\/([^/]+)$/);
    if (joinMatch) return join(joinMatch[1]);
    const g = p.match(/^\/groups\/([^/]+)(?:\/([^/]+))?$/);
    if (g) {
      const id = g[1];
      const sub = g[2];
      if (!sub) return groupPage(id);
      if (sub === "wishlist") return wishlist(id);
      if (sub === "assignment") return assignment(id);
      if (sub === "gift-tracking") return gifts(id);
      if (sub === "reveal") return reveal(id);
    }
    layout("<h1>Not found</h1>");
  } catch (err) {
    layout(`<h1>Something went wrong</h1><p class="error">${err.message}</p><p><a href="/login">Sign in</a></p>`);
  }
}

window.addEventListener("popstate", render);
render();
