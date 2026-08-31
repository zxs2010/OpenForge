"use strict";

const state = {
  network: null,
  activities: [],
  currentIntent: null,
  currentMatches: [],
  selectedActivity: null,
  writeToken: null,
};

const byId = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const headers = options.body
    ? {
        "Content-Type": "application/json",
        ...(state.writeToken ? { "X-OpenForge-Token": state.writeToken } : {}),
      }
    : {};
  const response = await fetch(path, {
    ...options,
    headers,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error?.message || `Request failed (${response.status})`);
  }
  return payload;
}

function element(tag, attributes = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attributes).forEach(([name, value]) => {
    if (name === "className") node.className = value;
    else if (name === "text") node.textContent = value;
    else node.setAttribute(name, value);
  });
  children.forEach((child) => node.append(child));
  return node;
}

function capabilityValues(raw) {
  return raw.split(",").map((value) => value.trim()).filter(Boolean);
}

function formatTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(date);
}

function setFormStatus(id, message, kind = "") {
  const status = byId(id);
  status.textContent = message;
  status.className = `form-status ${kind}`.trim();
}

async function loadNetwork() {
  state.network = await api("/api/v1/network");
  renderNetworkCounts();
  renderNodes();
  renderRoutingNodes(state.network.nodes.slice(0, 5));
  byId("network-total").textContent = `${state.network.nodes.length} indexed nodes`;
}

function renderNetworkCounts() {
  const container = byId("network-counts");
  container.replaceChildren();
  Object.entries(state.network.counts)
    .filter(([, count]) => count > 0)
    .forEach(([kind, count]) => {
      const item = element("span");
      item.append(element("strong", { text: String(count) }), ` ${kind}`);
      container.append(item);
    });
}

function renderNodes(kind = "all") {
  const container = byId("node-list");
  container.replaceChildren();
  const nodes = state.network.nodes.filter((node) => kind === "all" || node.kind === kind);
  if (!nodes.length) {
    container.append(element("p", { className: "node-empty", text: "No nodes of this kind are indexed yet. Connect the first one below." }));
    return;
  }
  nodes.forEach((node) => {
    const name = element("div", { className: "node-name", role: "cell" });
    const title = node.origin_url
      ? element("a", { href: node.origin_url, rel: "noreferrer" }, [element("strong", { text: node.name })])
      : element("strong", { text: node.name });
    name.append(title, element("small", { text: node.summary }));

    const capabilities = element("div", { className: "capability-list", role: "cell" });
    node.capabilities.forEach((capability) => capabilities.append(element("code", { text: capability })));
    if (!node.capabilities.length) capabilities.append(element("small", { text: "Capability not declared" }));

    const connection = element("span", { className: "connection-badge", role: "cell" }, [
      element("i", { className: `status-dot ${node.connection_status}`, "aria-hidden": "true" }),
      document.createTextNode(node.connection_status),
    ]);
    container.append(element("div", { className: "node-row", role: "row" }, [
      name,
      element("span", { className: "node-kind", role: "cell", text: node.kind }),
      capabilities,
      connection,
    ]));
  });
}

function routeSlots(count) {
  if (count <= 1) return [2];
  if (count === 2) return [0, 4];
  if (count === 3) return [0, 2, 4];
  if (count === 4) return [0, 1, 3, 4];
  return [0, 1, 2, 3, 4];
}

function renderRoutingNodes(nodes, matches = []) {
  const list = byId("routing-nodes");
  list.replaceChildren();
  const displayed = nodes.slice(0, 5);
  const slots = routeSlots(displayed.length);
  const matchByNodeId = new Map(matches.map((match) => [match.node.id, match]));
  document.querySelectorAll(".route-path").forEach((path, index) => {
    path.classList.toggle("active", matches.length > 0 && slots.includes(index));
  });
  displayed.forEach((node, index) => {
    const match = matchByNodeId.get(node.id);
    const item = element("li", { className: `routing-node slot-${slots[index] + 1}${match ? " matched" : ""}` });
    const reason = match ? `${match.reasons.join(", ")} · ` : "";
    item.append(element("strong", { text: node.name }), element("span", { text: `${reason}${node.kind} · ${node.connection_status}` }));
    list.append(item);
  });
}

async function loadActivities(selectedId = null) {
  const payload = await api("/api/v1/activities");
  state.activities = payload.activities;
  renderActivityList();
  const target = selectedId || state.selectedActivity || state.activities[0]?.id;
  if (target) await openActivity(target);
}

function renderActivityList() {
  const list = byId("activity-list");
  list.replaceChildren();
  if (!state.activities.length) {
    list.append(element("p", { className: "node-empty", text: "No activities yet. Route an intent to open the first one." }));
    return;
  }
  state.activities.forEach((activity) => {
    const button = element("button", { type: "button", "data-activity-id": activity.id });
    if (activity.id === state.selectedActivity) button.setAttribute("aria-current", "true");
    const left = element("span");
    left.append(element("strong", { text: activity.title }), element("small", { text: `${activity.participant_ids.length} participants · ${activity.event_count} events` }));
    button.append(left, element("span", { className: "activity-state", text: activity.state }));
    list.append(button);
  });
}

async function openActivity(activityId) {
  const detail = await api(`/api/v1/activities/${encodeURIComponent(activityId)}`);
  state.selectedActivity = activityId;
  renderActivityList();
  renderActivityRoom(detail);
  if (activityId === "activity:001") renderActivity001(detail);
}

function renderActivity001(detail) {
  byId("activity-001-state").textContent = detail.activity.state;
  byId("activity-001-participants").textContent = detail.participants.length;
  byId("activity-001-events").textContent = detail.events.length;
  const timeline = byId("activity-001-timeline");
  timeline.replaceChildren();
  detail.events.slice(-3).forEach((event) => {
    timeline.append(element("li", {}, [
      document.createTextNode(event.message),
      element("time", { datetime: event.created_at, text: formatTime(event.created_at) }),
    ]));
  });
}

function renderActivityRoom(detail) {
  const room = byId("activity-room");
  room.replaceChildren();
  const head = element("div", { className: "room-head" }, [
    element("h3", { text: detail.activity.title }),
    element("span", { text: detail.activity.state }),
  ]);
  const participants = element("div", { className: "participant-strip", "aria-label": "Activity participants" });
  detail.participants.forEach((participant) => participants.append(element("span", { text: `${participant.name} / ${participant.kind}` })));
  if (!detail.participants.length) participants.append(element("small", { text: "Recruiting the first participant." }));

  const timeline = element("ol", { className: "room-timeline" });
  detail.events.forEach((event) => {
    const content = element("div", {}, [element("p", { text: event.message })]);
    if (event.artifact_url) content.append(element("a", { href: event.artifact_url, rel: "noreferrer", text: "Open artifact" }));
    timeline.append(element("li", {}, [element("time", { datetime: event.created_at, text: formatTime(event.created_at) }), content]));
  });

  const form = element("form", { className: "activity-event-form", "data-activity-id": detail.activity.id });
  form.append(element("h4", { text: "Add meaningful progress" }), element("p", { className: "form-status", text: "Events form the public activity record." }));
  const fields = element("div", { className: "event-fields" });
  const kindWrap = element("div");
  const kindId = `event-kind-${detail.activity.id.replaceAll(":", "-")}`;
  kindWrap.append(element("label", { for: kindId, text: "Event kind" }), element("select", { id: kindId, name: "kind" }, [
    element("option", { value: "progress.recorded", text: "Progress recorded" }),
    element("option", { value: "artifact.published", text: "Artifact published" }),
    element("option", { value: "review.requested", text: "Review requested" }),
  ]));
  const messageWrap = element("div");
  const messageId = `event-message-${detail.activity.id.replaceAll(":", "-")}`;
  messageWrap.append(element("label", { for: messageId, text: "What changed?" }), element("input", { id: messageId, name: "message", required: "", maxlength: "4000", placeholder: "A concrete update with evidence when available." }));
  fields.append(kindWrap, messageWrap);
  form.append(fields, element("button", { type: "submit", text: "Add to activity record" }));
  room.append(head, participants, timeline, form);
}

async function submitIntent(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  const routing = byId("routing-field");
  button.disabled = true;
  button.querySelector("span").textContent = "Routing…";
  delete routing.dataset.matched;
  routing.dataset.routing = "true";
  setFormStatus("intent-status", "Reading the network's declared capabilities…");
  try {
    const result = await api("/api/v1/intents", {
      method: "POST",
      body: JSON.stringify({
        summary: byId("intent-summary").value,
        desired_capabilities: capabilityValues(byId("intent-capabilities").value),
      }),
    });
    state.currentIntent = result.intent;
    state.currentMatches = result.matches;
    const displayNodes = result.matches.length ? result.matches.map((match) => match.node) : state.network.nodes;
    renderRoutingNodes(displayNodes, result.matches);
    routing.dataset.matched = "true";
    const routingEmpty = byId("routing-empty");
    routingEmpty.hidden = result.matches.length > 0;
    routingEmpty.querySelector("strong").textContent = result.matches.length ? "Ready to route" : "No route yet";
    routingEmpty.querySelector("span").textContent = result.matches.length
      ? "Submit an outcome to illuminate compatible nodes."
      : "Try a broader capability or connect the missing node.";
    byId("match-result").hidden = false;
    byId("match-count").textContent = `${result.matches.length} compatible ${result.matches.length === 1 ? "node" : "nodes"}`;
    byId("match-explanation").textContent = result.matches.length
      ? `Top reason: ${result.matches[0].reasons.join(", ")}. Connection evidence breaks ties.${result.matches.length > 5 ? ` Showing the first 5; additional matches remain indexed (${result.matches.length - 5}).` : ""}`
      : "No declared capability matched yet. The intent remains open.";
    byId("activate-intent").disabled = result.matches.length === 0;
    setFormStatus("intent-status", result.matches.length ? "Route ready. Inspect the reasons, then open an activity." : "No match yet. Try adding a capability label or connect the missing node.", result.matches.length ? "success" : "error");
  } catch (error) {
    setFormStatus("intent-status", `${error.message}. Check the fields and try again.`, "error");
  } finally {
    delete routing.dataset.routing;
    button.disabled = false;
    button.querySelector("span").textContent = "Route this intent";
  }
}

async function activateIntent() {
  if (!state.currentIntent) return;
  const button = byId("activate-intent");
  button.disabled = true;
  button.textContent = "Opening…";
  try {
    const detail = await api(`/api/v1/intents/${encodeURIComponent(state.currentIntent.id)}/activate`, { method: "POST", body: "{}" });
    await loadActivities(detail.activity.id);
    byId("activity-room").scrollIntoView({ behavior: "smooth", block: "center" });
  } catch (error) {
    setFormStatus("intent-status", `${error.message}. The intent is saved; try opening it again.`, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Open an activity";
  }
}

async function submitNode(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  button.textContent = "Claiming…";
  try {
    const result = await api("/api/v1/nodes", {
      method: "POST",
      body: JSON.stringify({
        name: byId("node-name").value,
        kind: byId("node-kind").value,
        summary: byId("node-summary").value,
        capabilities: capabilityValues(byId("node-capabilities").value),
        origin_url: byId("node-url").value || null,
      }),
    });
    setFormStatus("node-status", `${result.node.name} is now claimed. Connection and verification remain separate evidence steps.`, "success");
    form.reset();
    byId("node-kind").value = "provider";
    await loadNetwork();
  } catch (error) {
    setFormStatus("node-status", `${error.message}. Correct the record and try again.`, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Claim this node";
  }
}

async function submitEvent(event) {
  const form = event.target.closest(".activity-event-form");
  if (!form) return;
  event.preventDefault();
  const data = new FormData(form);
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await api(`/api/v1/activities/${encodeURIComponent(form.dataset.activityId)}/events`, {
      method: "POST",
      body: JSON.stringify({ kind: data.get("kind"), message: data.get("message") }),
    });
    await loadActivities(form.dataset.activityId);
  } catch (error) {
    const status = form.querySelector(".form-status");
    status.textContent = `${error.message}. Correct the event and try again.`;
    status.classList.add("error");
    button.disabled = false;
  }
}

function bindEvents() {
  byId("intent-form").addEventListener("submit", submitIntent);
  byId("activate-intent").addEventListener("click", activateIntent);
  byId("node-form").addEventListener("submit", submitNode);
  byId("node-filters").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-kind]");
    if (!button) return;
    byId("node-filters").querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
    renderNodes(button.dataset.kind);
  });
  byId("activity-list").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-activity-id]");
    if (button) openActivity(button.dataset.activityId).catch(showPageError);
  });
  document.querySelectorAll("[data-open-activity]").forEach((button) => button.addEventListener("click", () => {
    openActivity(button.dataset.openActivity).then(() => byId("activity-room").scrollIntoView({ behavior: "smooth", block: "center" })).catch(showPageError);
  }));
  byId("activity-room").addEventListener("submit", submitEvent);
}

function showPageError(error) {
  byId("activity-room").replaceChildren(element("p", { className: "room-placeholder", text: `${error.message}. Refresh the page to reconnect to this node.` }));
}

async function start() {
  bindEvents();
  try {
    const meta = await api("/api/v1/meta");
    state.writeToken = meta.write_token;
    await Promise.all([loadNetwork(), loadActivities("activity:001")]);
  } catch (error) {
    showPageError(error);
    setFormStatus("intent-status", "The local reference node is unavailable. Restart it and refresh this page.", "error");
  }
}

start();
