// DevHub Workspace Client SPA Application
let authToken = localStorage.getItem("devhub_token");
let currentUser = JSON.parse(localStorage.getItem("devhub_user") || "null");
let activeFilterTab = "all"; // 'all', 'mine', 'bookmarks'

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

function initApp() {
  setupEventListeners();
  if (authToken && currentUser) {
    showAppView();
    loadDashboardStats();
    loadSnippets();
  } else {
    showAuthView();
  }
}

function showAuthView() {
  document.getElementById("view-auth").classList.remove("hidden");
  document.getElementById("view-app").classList.add("hidden");
  document.getElementById("nav-user-area").classList.add("hidden");
}

function showAppView() {
  document.getElementById("view-auth").classList.add("hidden");
  document.getElementById("view-app").classList.remove("hidden");
  document.getElementById("nav-user-area").classList.remove("hidden");
  
  // Populate nav profile
  document.getElementById("user-display-name").textContent = currentUser.full_name;
  document.getElementById("user-display-role").textContent = `${currentUser.role} (@${currentUser.username})`;
  document.getElementById("user-avatar").textContent = currentUser.full_name.charAt(0).toUpperCase();
}

async function apiFetch(url, options = {}) {
  options.headers = options.headers || {};
  if (authToken) {
    options.headers["Authorization"] = `Bearer ${authToken}`;
  }
  options.headers["Content-Type"] = "application/json";

  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    if (response.status === 401 && authToken) {
      // Session expired
      logoutUser();
      showToast("Session expired. Please sign in again.", "error");
    }
    throw new Error(data.detail || data.error || "Request failed");
  }
  return data;
}

function setupEventListeners() {
  // Auth Tab Switch
  document.getElementById("tab-auth-login").addEventListener("click", () => switchAuthTab("login"));
  document.getElementById("tab-auth-register").addEventListener("click", () => switchAuthTab("register"));

  // Login Form
  document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const alert = document.getElementById("auth-error-alert");
    alert.classList.add("hidden");

    try {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });

      authToken = data.access_token;
      currentUser = {
        id: data.user_id,
        username: data.username,
        email: data.email,
        full_name: data.full_name,
        role: data.role
      };

      localStorage.setItem("devhub_token", authToken);
      localStorage.setItem("devhub_user", JSON.stringify(currentUser));

      showAppView();
      loadDashboardStats();
      loadSnippets();
      showToast("Signed in successfully!", "success");
    } catch (err) {
      alert.textContent = err.message;
      alert.classList.remove("hidden");
    }
  });

  // Register Form
  document.getElementById("form-register").addEventListener("submit", async (e) => {
    e.preventDefault();
    const full_name = document.getElementById("reg-fullname").value;
    const username = document.getElementById("reg-username").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const alert = document.getElementById("auth-error-alert");
    alert.classList.add("hidden");

    try {
      const data = await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ full_name, username, email, password })
      });

      authToken = data.access_token;
      currentUser = {
        id: data.user_id,
        username: data.username,
        email: data.email,
        full_name: data.full_name,
        role: data.role
      };

      localStorage.setItem("devhub_token", authToken);
      localStorage.setItem("devhub_user", JSON.stringify(currentUser));

      showAppView();
      loadDashboardStats();
      loadSnippets();
      showToast("Account created successfully!", "success");
    } catch (err) {
      alert.textContent = err.message;
      alert.classList.remove("hidden");
    }
  });

  // Logout
  document.getElementById("btn-logout").addEventListener("click", logoutUser);

  // Filter Tabs
  document.getElementById("tab-filter-all").addEventListener("click", () => setFilterTab("all"));
  document.getElementById("tab-filter-mine").addEventListener("click", () => setFilterTab("mine"));
  document.getElementById("tab-filter-bookmarks").addEventListener("click", () => setFilterTab("bookmarks"));

  // Search & Language Inputs
  document.getElementById("search-input").addEventListener("input", debounce(() => loadSnippets(), 300));
  document.getElementById("language-filter").addEventListener("change", () => loadSnippets());

  // Modal Open / Close Triggers
  document.getElementById("btn-open-create-modal").addEventListener("click", openCreateModal);
  document.getElementById("btn-close-snippet-modal").addEventListener("click", closeSnippetModal);
  document.getElementById("btn-cancel-snippet-modal").addEventListener("click", closeSnippetModal);

  // Snippet Form Submit
  document.getElementById("form-snippet").addEventListener("submit", handleSnippetFormSubmit);
}

function switchAuthTab(type) {
  const loginTab = document.getElementById("tab-auth-login");
  const regTab = document.getElementById("tab-auth-register");
  const loginForm = document.getElementById("form-login");
  const regForm = document.getElementById("form-register");
  document.getElementById("auth-error-alert").classList.add("hidden");

  if (type === "login") {
    loginTab.className = "flex-1 pb-3 text-center text-sm font-semibold text-indigo-400 border-b-2 border-indigo-500 transition-colors";
    regTab.className = "flex-1 pb-3 text-center text-sm font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-colors";
    loginForm.classList.remove("hidden");
    regForm.classList.add("hidden");
  } else {
    regTab.className = "flex-1 pb-3 text-center text-sm font-semibold text-indigo-400 border-b-2 border-indigo-500 transition-colors";
    loginTab.className = "flex-1 pb-3 text-center text-sm font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-colors";
    regForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
  }
}

function logoutUser() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem("devhub_token");
  localStorage.removeItem("devhub_user");
  showAuthView();
  showToast("Logged out.", "info");
}

function setFilterTab(tab) {
  activeFilterTab = tab;
  const btnAll = document.getElementById("tab-filter-all");
  const btnMine = document.getElementById("tab-filter-mine");
  const btnBook = document.getElementById("tab-filter-bookmarks");

  const activeClass = "px-4 py-1.5 rounded-md text-xs font-semibold text-indigo-400 bg-slate-800 transition-all flex-1 md:flex-none";
  const inactiveClass = "px-4 py-1.5 rounded-md text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex-1 md:flex-none";

  btnAll.className = tab === "all" ? activeClass : inactiveClass;
  btnMine.className = tab === "mine" ? activeClass : inactiveClass;
  btnBook.className = tab === "bookmarks" ? activeClass : inactiveClass;

  loadSnippets();
}

async function loadDashboardStats() {
  try {
    const stats = await apiFetch("/api/dashboard/stats");
    document.getElementById("stat-total-snippets").textContent = stats.total_accessible_snippets || 0;
    document.getElementById("stat-my-snippets").textContent = stats.my_snippets_count || 0;
    document.getElementById("stat-my-bookmarks").textContent = stats.my_bookmarks_count || 0;
    document.getElementById("stat-total-views").textContent = stats.total_snippet_views || 0;
  } catch (err) {
    console.error("Dashboard stats error:", err);
  }
}

async function loadSnippets() {
  const container = document.getElementById("snippets-container");
  container.innerHTML = `<div class="col-span-full text-center py-12 text-slate-400 font-medium">Loading snippets...</div>`;

  const searchQuery = document.getElementById("search-input").value.trim();
  const langFilter = document.getElementById("language-filter").value;

  try {
    let url = "/api/snippets";
    if (activeFilterTab === "bookmarks") {
      url = "/api/bookmarks";
    } else {
      const params = new URLSearchParams();
      if (searchQuery) params.append("query", searchQuery);
      if (langFilter) params.append("language", langFilter);
      if (activeFilterTab === "mine") params.append("my_snippets", "true");
      url += `?${params.toString()}`;
    }

    const snippets = await apiFetch(url);
    renderSnippets(snippets);
  } catch (err) {
    container.innerHTML = `<div class="col-span-full text-center py-12 text-red-400 text-sm">Failed to load snippets: ${err.message}</div>`;
  }
}

function renderSnippets(snippets) {
  const container = document.getElementById("snippets-container");
  container.innerHTML = "";

  if (!snippets || snippets.length === 0) {
    container.innerHTML = `
      <div class="col-span-full glass-card rounded-2xl p-12 text-center border border-slate-800">
        <i class="fa-solid fa-code-merge text-4xl text-slate-600 mb-3"></i>
        <h4 class="text-base font-semibold text-slate-300">No Snippets Found</h4>
        <p class="text-xs text-slate-500 mt-1">Try tweaking your search keywords or create a new snippet to build your knowledge base.</p>
      </div>
    `;
    return;
  }

  snippets.forEach(snippet => {
    const isOwner = currentUser && (currentUser.id === snippet.user_id || currentUser.role === "Admin");
    const langLower = (snippet.language || "code").toLowerCase();
    
    // Tag Pills
    const tagsArr = snippet.tags ? snippet.tags.split(",").map(t => t.trim()).filter(Boolean) : [];
    const tagsHtml = tagsArr.map(t => `<span class="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[10px] font-mono border border-slate-700">#${escapeHtml(t)}</span>`).join(" ");

    const card = document.createElement("div");
    card.className = "glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between transition-all hover:shadow-xl hover:shadow-indigo-500/5 space-y-4";

    card.innerHTML = `
      <div>
        <!-- Top Info Line -->
        <div class="flex items-center justify-between gap-2 mb-2">
          <div class="flex items-center space-x-2">
            <span class="lang-${langLower} uppercase text-[10px] font-bold px-2 py-0.5 rounded font-mono">${escapeHtml(snippet.language)}</span>
            ${snippet.is_private ? '<span class="bg-amber-900/50 text-amber-300 text-[10px] font-semibold px-2 py-0.5 rounded border border-amber-700/50"><i class="fa-solid fa-lock"></i> Private</span>' : ''}
          </div>
          <div class="text-[11px] text-slate-400 font-mono flex items-center gap-3">
            <span><i class="fa-regular fa-eye"></i> ${snippet.views_count || 0}</span>
            <span><i class="fa-regular fa-user"></i> ${escapeHtml(snippet.author_name || 'Anonymous')}</span>
          </div>
        </div>

        <!-- Snippet Title & Desc -->
        <h3 class="text-base font-bold text-slate-100 hover:text-indigo-400 cursor-pointer transition-colors" onclick="openSnippetDetail(${snippet.id})">
          ${escapeHtml(snippet.title)}
        </h3>
        ${snippet.description ? `<p class="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-2">${escapeHtml(snippet.description)}</p>` : ''}

        <!-- Code Block Preview -->
        <div class="mt-3 relative bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 group">
          <button onclick="copySnippetCode(this, \`${escapeJsString(snippet.code_content)}\`)" class="absolute top-2 right-2 bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded text-[10px] font-mono transition-colors opacity-80 group-hover:opacity-100 flex items-center gap-1">
            <i class="fa-regular fa-copy"></i> Copy
          </button>
          <pre class="text-xs font-mono text-slate-200 overflow-x-auto max-h-48 pr-12 whitespace-pre">${escapeHtml(snippet.code_content)}</pre>
        </div>

        <!-- Tags -->
        ${tagsArr.length > 0 ? `<div class="flex flex-wrap gap-1.5 mt-3">${tagsHtml}</div>` : ''}
      </div>

      <!-- Action Footer -->
      <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <button onclick="toggleBookmark(${snippet.id})" class="${snippet.is_bookmarked ? 'text-amber-400 font-semibold' : 'text-slate-400 hover:text-amber-400'} transition-colors flex items-center gap-1.5">
          <i class="${snippet.is_bookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
          <span>${snippet.is_bookmarked ? 'Bookmarked' : 'Bookmark'}</span>
        </button>

        <div class="flex items-center space-x-2">
          ${isOwner ? `
            <button onclick="editSnippet(${snippet.id})" class="text-slate-400 hover:text-indigo-400 px-2 py-1 rounded transition-colors" title="Edit Snippet">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
            <button onclick="deleteSnippet(${snippet.id})" class="text-slate-400 hover:text-red-400 px-2 py-1 rounded transition-colors" title="Delete Snippet">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          ` : ''}
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

async function toggleBookmark(snippetId) {
  try {
    const res = await apiFetch(`/api/bookmarks/${snippetId}/toggle`, { method: "POST" });
    showToast(res.message, "success");
    loadDashboardStats();
    loadSnippets();
  } catch (err) {
    showToast(err.message, "error");
  }
}

function copySnippetCode(btn, codeText) {
  navigator.clipboard.writeText(codeText).then(() => {
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Copied!`;
    setTimeout(() => {
      btn.innerHTML = originalText;
    }, 2000);
    showToast("Code copied to clipboard!", "success");
  }).catch(() => {
    showToast("Failed to copy code.", "error");
  });
}

function openCreateModal() {
  document.getElementById("snippet-edit-id").value = "";
  document.getElementById("modal-snippet-title").textContent = "Create New Snippet";
  document.getElementById("form-snippet").reset();
  document.getElementById("modal-error-alert").classList.add("hidden");
  document.getElementById("modal-snippet").classList.remove("hidden");
}

function closeSnippetModal() {
  document.getElementById("modal-snippet").classList.add("hidden");
}

async function editSnippet(snippetId) {
  try {
    const snippet = await apiFetch(`/api/snippets/${snippetId}`);
    document.getElementById("snippet-edit-id").value = snippet.id;
    document.getElementById("modal-snippet-title").textContent = "Edit Snippet";
    document.getElementById("snippet-title-input").value = snippet.title;
    document.getElementById("snippet-language-input").value = snippet.language;
    document.getElementById("snippet-desc-input").value = snippet.description || "";
    document.getElementById("snippet-code-input").value = snippet.code_content;
    document.getElementById("snippet-tags-input").value = snippet.tags || "";
    document.getElementById("snippet-private-input").checked = snippet.is_private;

    document.getElementById("modal-error-alert").classList.add("hidden");
    document.getElementById("modal-snippet").classList.remove("hidden");
  } catch (err) {
    showToast("Failed to fetch snippet details.", "error");
  }
}

async function handleSnippetFormSubmit(e) {
  e.preventDefault();
  const editId = document.getElementById("snippet-edit-id").value;
  const payload = {
    title: document.getElementById("snippet-title-input").value,
    language: document.getElementById("snippet-language-input").value,
    description: document.getElementById("snippet-desc-input").value,
    code_content: document.getElementById("snippet-code-input").value,
    tags: document.getElementById("snippet-tags-input").value,
    is_private: document.getElementById("snippet-private-input").checked
  };

  const alert = document.getElementById("modal-error-alert");
  alert.classList.add("hidden");

  try {
    if (editId) {
      await apiFetch(`/api/snippets/${editId}`, {
        method: "PUT",
        body: JSON.stringify(payload)
      });
      showToast("Snippet updated successfully!", "success");
    } else {
      await apiFetch("/api/snippets", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      showToast("Snippet created successfully!", "success");
    }

    closeSnippetModal();
    loadDashboardStats();
    loadSnippets();
  } catch (err) {
    alert.textContent = err.message;
    alert.classList.remove("hidden");
  }
}

async function deleteSnippet(snippetId) {
  if (!confirm("Are you sure you want to delete this snippet?")) return;
  try {
    await apiFetch(`/api/snippets/${snippetId}`, { method: "DELETE" });
    showToast("Snippet deleted successfully.", "info");
    loadDashboardStats();
    loadSnippets();
  } catch (err) {
    showToast(err.message, "error");
  }
}

function openSnippetDetail(snippetId) {
  // Trigger fetch to increment view count
  apiFetch(`/api/snippets/${snippetId}`).then(() => {
    loadDashboardStats();
  }).catch(() => {});
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");

  let borderBg = "bg-slate-800 text-slate-200 border-slate-700";
  if (type === "success") borderBg = "bg-slate-800 text-emerald-300 border-emerald-500/50";
  if (type === "error") borderBg = "bg-slate-800 text-red-300 border-red-500/50";

  toast.className = `p-3 rounded-lg border shadow-xl text-xs font-medium ${borderBg} transition-all duration-300 transform translate-y-2 opacity-0 pointer-events-auto flex items-center gap-2`;
  toast.innerHTML = `
    <i class="fa-solid ${type === 'success' ? 'fa-circle-check text-emerald-400' : type === 'error' ? 'fa-circle-exclamation text-red-400' : 'fa-circle-info text-sky-400'}"></i>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  }, 10);

  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function escapeJsString(str) {
  if (!str) return "";
  return str.replace(/\\/g, "\\\\").replace(/`/g, "\\`").replace(/\$/g, "\\$");
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
