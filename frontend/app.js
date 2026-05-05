/* CrisisGrid Frontend — app.js */

const API = 'http://localhost:8000/api/v1';
let state = {
  simId: null, simName: '', running: false, intervalId: null,
  speed: 1000, timestep: 0, totalTimesteps: 100,
  powerCap: 1000, waterCap: 500,
  historyPower: [], historyWater: [], historyDemand: [],
  historySupply: [], historyStability: [], historyRisk: [],
  historyLabels: [], maxHistory: 40,
  lastEvent: null,
};

// ── SCENARIO PRESETS ──────────────────────────────────────────────────────────
const SCENARIOS = {
  default: {
    name: 'Default Crisis', timesteps: 60,
    agents: [
      { type: 'hospital',  name: 'Hospitals',           demand: 180, max: 200, min: 100, priority: 2.0 },
      { type: 'power',     name: 'Power Grid',          demand: 350, max: 500, min: 200, priority: 1.8 },
      { type: 'water',     name: 'Water Authority',     demand: 250, max: 350, min: 150, priority: 1.7 },
      { type: 'emergency', name: 'Emergency Services',  demand: 120, max: 150, min: 80,  priority: 1.9 },
    ]
  },
  flood: {
    name: 'Flood Response', timesteps: 80,
    agents: [
      { type: 'hospital',  name: 'Riverside Hospital',  demand: 195, max: 250, min: 150, priority: 2.5 },
      { type: 'water',     name: 'Flood Control',       demand: 480, max: 600, min: 250, priority: 2.2 },
      { type: 'emergency', name: 'Rescue Operations',   demand: 175, max: 200, min: 120, priority: 2.4 },
      { type: 'power',     name: 'Backup Generators',   demand: 280, max: 400, min: 180, priority: 1.6 },
    ]
  },
  earthquake: {
    name: 'Earthquake Recovery', timesteps: 100,
    agents: [
      { type: 'hospital',  name: 'Trauma Center A',     demand: 198, max: 250, min: 150, priority: 2.8 },
      { type: 'hospital',  name: 'Trauma Center B',     demand: 190, max: 250, min: 150, priority: 2.6 },
      { type: 'emergency', name: 'Search & Rescue',     demand: 178, max: 200, min: 120, priority: 2.5 },
      { type: 'power',     name: 'City Power Grid',     demand: 550, max: 700, min: 300, priority: 1.5 },
      { type: 'water',     name: 'Water Treatment',     demand: 300, max: 400, min: 200, priority: 1.7 },
    ]
  },
  hurricane: {
    name: 'Hurricane Strike', timesteps: 70,
    agents: [
      { type: 'emergency', name: 'Evacuation Center',   demand: 179, max: 200, min: 120, priority: 2.6 },
      { type: 'hospital',  name: 'Storm Shelter Med',   demand: 188, max: 250, min: 150, priority: 2.4 },
      { type: 'power',     name: 'Emergency Grid',      demand: 600, max: 800, min: 350, priority: 1.4 },
      { type: 'water',     name: 'Storm Water Mgmt',    demand: 360, max: 500, min: 200, priority: 1.8 },
    ]
  },
  blackout: {
    name: 'Cascading Blackout', timesteps: 50,
    agents: [
      { type: 'power',     name: 'Grid Station East',   demand: 680, max: 800, min: 400, priority: 2.2 },
      { type: 'power',     name: 'Grid Station West',   demand: 650, max: 800, min: 400, priority: 2.1 },
      { type: 'hospital',  name: 'City Hospital',       demand: 192, max: 250, min: 150, priority: 2.9 },
      { type: 'emergency', name: 'Emergency Dispatch',  demand: 170, max: 200, min: 120, priority: 2.3 },
    ]
  },
};

// ── CHART SETUP ───────────────────────────────────────────────────────────────
Chart.defaults.color = '#9c9484';
Chart.defaults.borderColor = 'rgba(180,170,150,0.15)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;

function makeChart(id, datasets, yMax) {
  const ctx = document.getElementById(id).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets },
    options: {
      responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 10 } } },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { maxTicksLimit: 8 } },
        y: { grid: { color: 'rgba(0,0,0,0.04)' }, min: 0, max: yMax || undefined,
             ticks: { maxTicksLimit: 5 } },
      },
      elements: { point: { radius: 0, hitRadius: 8 }, line: { tension: 0.3 } },
    }
  });
}

let charts = {};
function initCharts() {
  charts.resources = makeChart('chartResources', [
    { label: 'Power', data: [], borderColor: '#c4955a', backgroundColor: 'rgba(196,149,90,0.08)', fill: true, borderWidth: 2 },
    { label: 'Water', data: [], borderColor: '#2c7a7b', backgroundColor: 'rgba(44,122,123,0.06)', fill: true, borderWidth: 2 },
  ]);
  charts.demand = makeChart('chartDemand', [
    { label: 'Total Demand', data: [], borderColor: '#c0392b', backgroundColor: 'rgba(192,57,43,0.08)', fill: true, borderWidth: 2 },
    { label: 'Total Supply', data: [], borderColor: '#3d8b5e', backgroundColor: 'rgba(61,139,94,0.08)', fill: true, borderWidth: 2 },
  ]);
  charts.stability = makeChart('chartStability', [
    { label: 'Stability', data: [], borderColor: '#3d8b5e', borderWidth: 2, backgroundColor: 'rgba(61,139,94,0.06)', fill: true },
    { label: 'Risk', data: [], borderColor: '#c0392b', borderWidth: 2, backgroundColor: 'rgba(192,57,43,0.06)', fill: true },
  ], 1.0);
}

function pushChartData(power, water, demand, supply, stability, risk, label) {
  const lim = state.maxHistory;
  const push = (arr, v) => { arr.push(v); if (arr.length > lim) arr.shift(); };
  push(state.historyPower, power);     push(state.historyWater, water);
  push(state.historyDemand, demand);   push(state.historySupply, supply);
  push(state.historyStability, stability); push(state.historyRisk, risk);
  push(state.historyLabels, label);

  [charts.resources, charts.demand, charts.stability].forEach(c => {
    c.data.labels = [...state.historyLabels];
  });
  charts.resources.data.datasets[0].data = [...state.historyPower];
  charts.resources.data.datasets[1].data = [...state.historyWater];
  charts.demand.data.datasets[0].data   = [...state.historyDemand];
  charts.demand.data.datasets[1].data   = [...state.historySupply];
  charts.stability.data.datasets[0].data = [...state.historyStability];
  charts.stability.data.datasets[1].data = [...state.historyRisk];
  charts.resources.update('none');
  charts.demand.update('none');
  charts.stability.update('none');
}

// ── API HELPERS ───────────────────────────────────────────────────────────────
async function apiFetch(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── SIMULATION LIFECYCLE ──────────────────────────────────────────────────────
async function createSimulation() {
  const scenario = document.getElementById('scenarioSelect').value;
  const preset   = SCENARIOS[scenario] || SCENARIOS.default;

  setBtnLoading('btnCreate', true);
  try {
    const sim = await apiFetch('/simulations/', 'POST', {
      name: preset.name,
      description: `Scenario: ${preset.name}`,
      total_timesteps: preset.timesteps,
    });
    state.simId           = sim._id;
    state.simName         = sim.name;
    state.totalTimesteps  = sim.total_timesteps;
    state.timestep        = 0;
    state.powerCap        = sim.power_available || 1000;
    state.waterCap        = sim.water_available || 500;
    resetHistory();

    addEvent('info', '⚡', `Simulation "${preset.name}" created`, `ID: ${sim._id}`);

    for (const ag of preset.agents) {
      await apiFetch(
        `/simulations/${state.simId}/agents?agent_type=${ag.type}&name=${encodeURIComponent(ag.name)}&current_demand=${ag.demand}&max_demand=${ag.max}&min_demand=${ag.min}&priority_level=${ag.priority}`,
        'POST'
      );
    }

    const agents = await apiFetch(`/simulations/${state.simId}/agents`);
    renderAgents(agents);
    enableControls(true);
    addEvent('stable', '✅', `${agents.length} agents configured`, `Ready to simulate`);
  } catch (e) {
    addEvent('critical', '❌', 'Failed to create simulation', e.message);
  }
  setBtnLoading('btnCreate', false);
}

function startAuto() {
  if (!state.simId || state.running) return;
  state.running = true;
  document.getElementById('btnStart').disabled = true;
  document.getElementById('btnStop').disabled  = false;
  document.getElementById('btnStep').disabled  = true;
  autoStepLoop();
}

async function autoStepLoop() {
  if (!state.running) return;
  const t0 = Date.now();
  await doStep();
  if (state.running) {
    const elapsed = Date.now() - t0;
    const delay = Math.max(0, state.speed - elapsed);
    state.intervalId = setTimeout(autoStepLoop, delay);
  }
}

function stopAuto() {
  state.running = false;
  clearTimeout(state.intervalId);
  document.getElementById('btnStart').disabled = false;
  document.getElementById('btnStop').disabled  = true;
  document.getElementById('btnStep').disabled  = false;
}

async function doStep() {
  if (!state.simId) return;
  try {
    const res = await apiFetch(`/simulations/${state.simId}/step`, 'POST');
    processStepResult(res);
    if (res.state?.is_completed) {
      stopAuto();
      addEvent('stable', '🏁', 'Simulation completed!', `${res.state.current_timestep} steps finished`);
      enableControls(false);
    }
  } catch (e) {
    stopAuto();
    addEvent('critical', '❌', 'Step failed', e.message);
  }
}

function processStepResult(res) {
  const s     = res.state   || {};
  const m     = res.metrics || {};
  const agents = res.agents  || [];
  const event  = res.event;
  const expls  = res.explanations || [];

  state.timestep = s.current_timestep || 0;
  const power = s.power_available ?? state.powerCap;
  const water = s.water_available ?? state.waterCap;

  // Resources
  updateGauge('powerBar', 'powerCurrent', power, state.powerCap, 'power');
  updateGauge('waterBar', 'waterCurrent', water, state.waterCap, 'water');

  // Metrics
  setMetric('metricStability', m.stability_score, true);
  setMetric('metricRisk',      m.risk_level, false, true);
  setMetric('metricEfficiency',m.allocation_efficiency, true);
  setMetric('metricFairness',  m.fairness_score, true);
  document.getElementById('metricUnmet').textContent = (m.unmet_demand || 0).toFixed(1);

  // Header tick
  document.getElementById('headerTimestep').textContent = state.timestep;

  // Stability badge
  updateStabilityBadge(m.stability_score);

  // Agents
  renderAgents(agents);

  // Demand / supply totals
  const totalDemand  = agents.reduce((s, a) => s + (a.current_demand || 0), 0);
  const totalSupply  = agents.reduce((s, a) => s + (a.allocated_resources || 0), 0);

  pushChartData(power, water, totalDemand, totalSupply,
    m.stability_score || 0, m.risk_level || 0, `T${state.timestep}`);

  // Alert banner
  updateAlertBanner(m);

  // Event
  if (event) {
    state.lastEvent = event;
    const sev = event.severity || 0;
    const cls = sev > 0.7 ? 'critical' : sev > 0.4 ? 'warning' : 'info';
    const icons = {
      power_outage: '⚡', water_shortage: '💧', demand_spike: '📈',
      infrastructure_failure: '🏗️', recovery: '🔄'
    };
    const eventName = event.event_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    addEvent(cls, icons[event.event_type] || '🚨', eventName,
      `Severity ${(sev*100).toFixed(0)}% — ${event.affected_agent_type || 'system'}`);
    updateActiveEvent(eventName, sev, event.description || `${event.affected_agent_type || 'System'} affected.`);
  }

  // Explanations
  updateExplanations(expls);
}

// ── RENDERING ─────────────────────────────────────────────────────────────────
const TYPE_ICON = { hospital:'🏥', water:'💧', power:'⚡', emergency:'🚨' };

function renderAgents(agents) {
  const grid = document.getElementById('agentGrid');
  if (!agents.length) {
    grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🤖</div><p>No agents</p></div>';
    return;
  }

  grid.innerHTML = agents.map(a => {
    const demand = a.current_demand || 0;
    const alloc  = a.allocated_resources || 0;
    const pct    = demand > 0 ? Math.min(100, (alloc / demand) * 100) : 100;
    const trust  = a.trust_score ?? 0.5;
    const behav  = a.behavior_profile || 'adaptive';
    const priority = a.priority_level || 1;
    const cardCls = pct < 50 ? 'critical' : pct < 80 ? 'warning' : '';

    // Compute a mock utility score (demand * priority * trust)
    const utility = (demand * priority * trust).toFixed(1);

    const pip10 = Array.from({length:10}, (_,i) => {
      const filled = i < Math.round(trust * 10);
      const cls = trust > 0.7 ? 'high' : trust > 0.4 ? 'mid' : 'low';
      return `<div class="trust-pip ${filled ? `filled ${cls}` : ''}"></div>`;
    }).join('');

    // Resource bar fill percentages (simulated breakdown)
    const powerPct = Math.min(100, (alloc / Math.max(demand, 1)) * 100 * 0.7);
    const waterPct = Math.min(100, (alloc / Math.max(demand, 1)) * 100 * 0.3);
    const medPct = a.agent_type === 'hospital' ? Math.min(100, pct * 0.9) : 0;

    return `<div class="agent-card ${cardCls}">
      <div class="agent-header">
        <div>
          <div class="agent-name">${TYPE_ICON[a.agent_type]||'🤖'} ${a.name}</div>
          <div class="agent-meta">priority ${priority.toFixed(0)} | trust ${trust.toFixed(2)}</div>
        </div>
        <div class="agent-utility">
          <span class="agent-utility-label">utility</span> ${utility}
        </div>
      </div>
      <div class="agent-stats">
        <div><div class="agent-stat-label">Demand</div><div class="agent-stat-value">${demand.toFixed(0)}</div></div>
        <div><div class="agent-stat-label">Allocated</div><div class="agent-stat-value">${alloc.toFixed(0)}</div></div>
        <div><div class="agent-stat-label">Behavior</div><div class="agent-stat-value" style="text-transform:capitalize;font-size:11px">${behav}</div></div>
      </div>
      <div class="agent-resources">
        <div class="agent-res-item">
          <div class="agent-res-label">Power</div>
          <div class="agent-res-bar"><div class="agent-res-fill power" style="width:${powerPct}%"></div></div>
        </div>
        <div class="agent-res-item">
          <div class="agent-res-label">Water</div>
          <div class="agent-res-bar"><div class="agent-res-fill water" style="width:${waterPct}%"></div></div>
        </div>
        <div class="agent-res-item">
          <div class="agent-res-label">Medical</div>
          <div class="agent-res-bar"><div class="agent-res-fill medical" style="width:${medPct}%"></div></div>
        </div>
      </div>
      <div class="trust-row">
        <span class="trust-label">Trust</span>
        <div class="trust-pips">${pip10}</div>
        <span style="font-family:var(--mono);font-size:10px;color:var(--text-secondary);margin-left:4px">${(trust*100).toFixed(0)}%</span>
      </div>
    </div>`;
  }).join('');
}

function updateGauge(barId, curId, current, capacity, type) {
  const pct = capacity > 0 ? (current / capacity) * 100 : 0;
  const bar = document.getElementById(barId);
  bar.style.width = pct + '%';
  bar.className = `gauge-bar-fill ${pct < 30 ? 'crit' : pct < 60 ? 'warn' : type}`;
  document.getElementById(curId).textContent = current.toFixed(0);
}

function setMetric(id, val, higherBetter = true, isRisk = false) {
  const el = document.getElementById(id);
  if (val === undefined || val === null) { el.textContent = '—'; return; }
  const pct = (val * 100).toFixed(0) + '%';
  el.textContent = pct;
  el.className = 'metric-mini-value';
  if (isRisk) {
    el.classList.add(val > 0.6 ? 'crit' : val > 0.3 ? 'warn' : 'good');
  } else {
    el.classList.add(val > 0.75 ? 'good' : val > 0.5 ? 'warn' : 'crit');
  }
}

function updateStabilityBadge(score) {
  const el = document.getElementById('stabilityBadge');
  if (score === undefined || score === null) return;
  const pct = (score * 100).toFixed(0);
  el.textContent = `STABILITY ${pct}%`;
  el.className = 'stability-badge';
  if (score > 0.7) el.classList.add('good');
  else if (score > 0.4) el.classList.add('warn');
  else el.classList.add('crit');
}

function updateActiveEvent(name, severity, desc) {
  document.getElementById('activeEventTitle').textContent = `${name} | severity ${severity.toFixed(2)}`;
  document.getElementById('activeEventDesc').textContent = desc;
}

function updateAlertBanner(m) {
  const el = document.getElementById('alertBanner');
  const risk = m.risk_level || 0;
  const stab = m.stability_score || 1;
  if (risk > 0.6 || stab < 0.4) {
    el.style.display = 'flex';
    el.className = 'alert-banner crit';
    el.innerHTML = '⚠️ CRITICAL — Cascading failure risk is high! Resource shortages detected.';
  } else if (risk > 0.3 || stab < 0.7) {
    el.style.display = 'flex';
    el.className = 'alert-banner warn';
    el.innerHTML = '⚠️ WARNING — System under stress. Monitor resource allocation closely.';
  } else {
    el.style.display = 'flex';
    el.className = 'alert-banner ok';
    el.innerHTML = '✅ STABLE — All systems operating within normal parameters.';
  }
}

function updateExplanations(expls) {
  const el = document.getElementById('explanationList');
  if (!expls.length) return;
  el.innerHTML = expls.slice(0, 6).map(e =>
    `<div class="explanation-item">${e}</div>`
  ).join('');
}

function addEvent(type, icon, title, detail) {
  const feed = document.getElementById('eventsFeed');
  const noEv = feed.querySelector('.no-events');
  if (noEv) noEv.remove();
  const item = document.createElement('div');
  item.className = `event-item ${type}`;
  const now = new Date().toLocaleTimeString();
  item.innerHTML = `<div class="event-icon">${icon}</div>
    <div class="event-body">
      <div class="event-title">${title}</div>
      <div style="font-size:11px;color:var(--text-secondary);margin-top:1px">${detail}</div>
      <div class="event-time">${now} · T${state.timestep}</div>
    </div>`;
  feed.insertBefore(item, feed.firstChild);
  while (feed.children.length > 20) feed.removeChild(feed.lastChild);
}

// ── SPEED ──────────────────────────────────────────────────────────────────────
function setSpeed(ms) {
  state.speed = ms;
  document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
  const labels = { 2000:'0.5×', 1000:'1×', 500:'2×', 200:'5×' };
  document.querySelectorAll('.speed-btn').forEach(b => {
    if (b.textContent === labels[ms]) b.classList.add('active');
  });
  if (state.running) {
    clearTimeout(state.intervalId);
    state.intervalId = setTimeout(autoStepLoop, ms);
  }
}

// ── RESET ──────────────────────────────────────────────────────────────────────
async function resetSim() {
  if (!state.simId) return;
  stopAuto();
  try {
    await apiFetch(`/simulations/${state.simId}`, 'DELETE');
    addEvent('info', '🗑', 'Simulation deleted', state.simId);
  } catch (e) {
    addEvent('critical', '❌', 'Delete failed', e.message);
  }
  state.simId = null; state.simName = ''; state.lastEvent = null;
  resetHistory();
  renderAgents([]);
  document.getElementById('alertBanner').style.display = 'none';
  document.getElementById('explanationList').innerHTML = '<div class="empty-state"><div class="empty-icon">🧠</div><p>Reasoning will appear<br>after each step</p></div>';
  ['powerCurrent','waterCurrent'].forEach(id => document.getElementById(id).textContent = '—');
  ['powerBar','waterBar'].forEach(id => document.getElementById(id).style.width = '0%');
  ['metricStability','metricRisk','metricEfficiency','metricFairness'].forEach(id => {
    const el = document.getElementById(id);
    el.textContent = '—'; el.className = 'metric-mini-value';
  });
  document.getElementById('metricUnmet').textContent = '—';
  document.getElementById('headerTimestep').textContent = '0';
  document.getElementById('stabilityBadge').textContent = 'STABILITY —';
  document.getElementById('stabilityBadge').className = 'stability-badge good';
  document.getElementById('activeEventTitle').textContent = 'No active event';
  document.getElementById('activeEventDesc').textContent = 'Start a simulation to see events.';
  enableControls(false);
  [charts.resources, charts.demand, charts.stability].forEach(c => {
    c.data.labels = [];
    c.data.datasets.forEach(d => d.data = []);
    c.update();
  });
}

// ── HELPERS ─────────────────────────────────────────────────────────────────────
function resetHistory() {
  state.historyPower = []; state.historyWater = [];
  state.historyDemand = []; state.historySupply = [];
  state.historyStability = []; state.historyRisk = [];
  state.historyLabels = []; state.timestep = 0;
}

function enableControls(on) {
  document.getElementById('btnStart').disabled = !on;
  document.getElementById('btnStop').disabled  = true;
  document.getElementById('btnStep').disabled  = !on;
  document.getElementById('btnReset').disabled = !on;
}

function setBtnLoading(id, loading) {
  const btn = document.getElementById(id);
  btn.disabled = loading;
  btn.innerHTML = loading ? '<span class="spinner"></span> Working…' : '⚡ New';
}

// ── NAV ────────────────────────────────────────────────────────────────────────
function switchNav(el) {
  const sectionId = el.getAttribute('data-section') + '-view';
  const targetView = document.getElementById(sectionId);
  if (!targetView) return; // Ignore if view doesn't exist

  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  el.classList.add('active');

  document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
  targetView.classList.add('active');
}

// ── INIT ────────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initCharts();
  enableControls(false);
});
