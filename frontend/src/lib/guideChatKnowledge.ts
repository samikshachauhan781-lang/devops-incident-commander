/**
 * Documentation-based knowledge for the homepage guide assistant.
 * Grounded in implemented product behavior only.
 */
import type { GuideCategory } from './guideChatTypes';

export type GuideTopicEntry = {
  id: string;
  title: string;
  category: GuideCategory;
  keywords: string[];
  phrases?: string[];
  answer: string;
  followUpSuggestions?: string[];
  relatedTopicIds?: string[];
};

export const GUIDE_WELCOME =
  'Hi! I\'m the **DevOps Incident Commander guide** — a documentation-based assistant (not a live generative AI). I explain this app, incidents, investigations, timelines, analytics, and demo mode. Pick a suggestion or type a question.';

export const GUIDE_SUGGESTED_QUESTIONS = [
  'What does this project do?',
  'Explain this website to me',
  'How do I investigate a server failure?',
  'Can this monitor my production servers automatically?',
  'What is the difference between High and Critical severity?',
];

export const GUIDE_FOLLOWUP_PROMPTS = [
  'What is DevOps Incident Commander?',
  'How does AI investigation work?',
  'What happens when I click Investigate?',
  'Is this a demo or real monitoring?',
  'What are the platform limitations?',
];

export const GUIDE_EMPTY_PROMPT =
  'Please type a question about the platform — for example incidents, severity, investigation, timeline, or demo mode.';

export const GUIDE_CAPABILITIES = `I can help you understand **what this app does** and **how to use it**:

- Project overview and navigation
- Incidents, severity, and status
- AI investigation workflow and results
- Timeline, analytics, and filters
- Demo mode vs a private deployment
- Troubleshooting load/API errors

I **cannot** access your servers, change incidents, or reveal secrets. I'm not a trained LLM — answers come from curated documentation.`;

export const GUIDE_SECURITY_REFUSAL = `I can't help with **secrets, credentials, bypassing security, or destructive actions**.

This guide is **read-only** and does not run commands or modify incidents. For deployment secrets, use your host's environment settings (see README / Render docs) — never paste keys into chat.

Ask me about **using the UI**, **demo mode**, or **investigation workflow** instead.`;

export const GUIDE_AMBIGUOUS_CLARIFY = `Your question could match a few topics. Which did you mean? Reply with one of the suggestions below, or rephrase with a bit more detail.`;

export const GUIDE_FALLBACK_ANSWER =
  'I don\'t have a specific documented answer for that. I\'m a **documentation-based guide**, not a live AI model. Try a suggested question, or ask about incidents, severity, investigation, timeline, analytics, demo mode, or limitations.';

/** Short social replies — not incident actions; session keeps the prior technical topic. */
export const GUIDE_GREETING_DEFAULT =
  'Hello! 👋 I\'m the **DevOps Incident Commander guide** — here to explain incidents, investigations, the timeline, analytics, and demo mode. What would you like to explore first?';

export const GUIDE_GREETING_TIME = {
  morning: 'Good morning! ☀️ Ready to walk through incidents, investigations, or demo mode — what can I help with?',
  afternoon: 'Good afternoon! I can help you navigate incidents, severity, and AI investigations. What\'s on your mind?',
  evening: 'Good evening! 🌙 Ask me about the dashboard, timeline, or how investigation works in this app.',
} as const;

export const GUIDE_GREETING_RETURN =
  'Welcome back — still on the same topic if you want to go deeper, or ask something new about incidents or the platform.';

export const GUIDE_GREETING_REPEAT =
  'I\'m still here. Try a specific question (for example demo mode, severity, or **Start Investigation**), or tap a suggestion below.';

export const GUIDE_INTRO_WHO =
  'I\'m the **documentation-based guide** for DevOps Incident Commander — not a live generative AI. I explain how to use this incident-management app (read-only in public demo). I don\'t create, edit, or delete incidents from chat.';

export const GUIDE_THANKS =
  'You\'re welcome! 🙂 If anything else comes up — investigations, timeline filters, or demo vs production — just ask.';

export const GUIDE_THANKS_HELPFUL =
  'Glad that helped. Want to go deeper on the same topic, or switch to analytics, timeline, or troubleshooting?';

export const GUIDE_ACK =
  'Sounds good. When you\'re ready, ask a follow-up like **tell me more** or pick a suggestion — I\'ll stay on context.';

export const GUIDE_ACK_NO_CONTEXT =
  'Got it. Ask about incidents, severity, investigation, demo mode, or pick a starter question below.';

export const GUIDE_CLOSING =
  'Goodbye for now! 👋 Reopen **Guide** anytime you need help with incidents or investigations. Take care.';

export const GUIDE_CLOSING_SOFT =
  'All set for now — I\'ll be here when you need the incident workflow or demo mode explained again.';

export const GUIDE_FOLLOWUP_NO_CONTEXT =
  'Happy to continue — what topic should we pick up? Incidents, investigation, timeline, analytics, or demo mode?';

export const GUIDE_TOPICS: GuideTopicEntry[] = [
  {
    id: 'what-is',
    title: 'Project overview',
    category: 'overview',
    keywords: ['what is', 'devops incident commander', 'about', 'project', 'platform', 'this website', 'this app', 'what does this project do'],
    phrases: ['explain this website', 'explain this app to me', 'what does this do', 'tell me about this tool'],
    answer: `**DevOps Incident Commander** is a web app for tracking production-style **incidents** and running **AI-assisted investigations**.

It helps teams:
1. **Record** incidents (title, service, severity, status, description)
2. **Review** history on a **timeline** of events
3. **See trends** on the **dashboard** and **analytics** pages
4. **Run investigations** that suggest hypotheses and next steps

The React UI talks to a **FastAPI** backend with SQLite. Public demos usually run in **read-only demo mode** with sample data — not a live feed from your production servers.`,
    followUpSuggestions: ['How does the platform work step by step?', 'Is this real production monitoring?'],
    relatedTopicIds: ['how-works', 'demo'],
  },
  {
    id: 'purpose',
    title: 'Purpose of the platform',
    category: 'overview',
    keywords: ['purpose', 'why', 'goal', 'use case', 'who is this for', 'help me understand'],
    phrases: ['why was this built', 'who should use this', 'purpose of this website', 'purpose of this platform'],
    answer: `The purpose is a **single place to understand and work through incidents** during an outage or drill.

You can see open vs resolved work, filter incidents, open details, start **AI investigation**, and browse a **global timeline**.

It is an **MVP / demo-friendly** product for learning incident workflows — not a full observability replacement.`,
    followUpSuggestions: ['What can this platform do?', 'What are its limitations?'],
    relatedTopicIds: ['capabilities', 'limitations'],
  },
  {
    id: 'capabilities',
    title: 'What the guide can do',
    category: 'faq',
    keywords: ['what can you do', 'what can this do', 'capabilities', 'features list', 'help topics', 'what can you help', 'what can this platform'],
    phrases: ['what can you help me with', 'what can this platform do'],
    answer: GUIDE_CAPABILITIES,
    followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS.slice(0, 3),
  },
  {
    id: 'how-works',
    title: 'How the platform works',
    category: 'navigation',
    keywords: ['how does', 'how it works', 'architecture', 'flow', 'steps', 'overview', 'step by step'],
    phrases: ['walk me through the site', 'how do i use this website'],
    answer: `Step by step:

1. **Dashboard (/)** — Metrics, recent incidents, platform health (including **demo mode**).
2. **Incidents** — List with filters, search, pagination; open a row for **details**.
3. **Incident detail** — Description, badges, **Start Investigation** when allowed.
4. **Timeline** — Events across incidents with filters.
5. **Analytics** — Severity and status charts.
6. **Settings** — Theme/accent (stored in your browser).

Data loads via **REST API**. This chatbot is **guide-only** — it does not create or change incidents.`,
    followUpSuggestions: ['How do I navigate the dashboard?', 'What happens when I click Investigate?'],
    relatedTopicIds: ['navigation', 'investigate-button'],
  },
  {
    id: 'navigation',
    title: 'Dashboard and navigation',
    category: 'navigation',
    keywords: ['dashboard', 'filter', 'sidebar', 'navigation', 'menu', 'home page', 'recent incidents', 'timeline page'],
    phrases: ['how do i use the dashboard', 'where is analytics', 'how do i get to incidents', 'where is the timeline page', 'where is timeline'],
    answer: `**Dashboard** — Open **/** for metric cards, recent incidents, and health (demo mode indicator).

**Incidents** — Service, severity, status filters + search. Click a row for details.

**Timeline** — Cross-incident events; filter by type and search.

**Analytics** — Visual breakdowns.

**Settings** — Light/dark theme and accent color.

Use the **sidebar** (desktop) or **mobile menu** to switch sections.`,
    followUpSuggestions: ['How do filters work on analytics?', 'What appears on the timeline?'],
    relatedTopicIds: ['analytics', 'timeline'],
  },
  {
    id: 'incidents',
    title: 'Incident management',
    category: 'incidents',
    keywords: ['create', 'manage', 'incident', 'new incident', 'edit', 'delete', 'resolve', 'crud', 'lifecycle'],
    phrases: ['how do i create an incident', 'manage incidents', 'incident lifecycle'],
    answer: `**Non–read-only deployment:** create, update, delete, list, filter, and search incidents via the API/UI.

**Demo / read-only mode:** view **sample incidents** only; create/edit/delete return **403 Forbidden** — expected on public demos.

Workflow: **Incidents** → open one → read details or **Start Investigation** when enabled.`,
    followUpSuggestions: ['What do incident statuses mean?', 'What is demo mode?'],
    relatedTopicIds: ['status-lifecycle', 'demo'],
  },
  {
    id: 'status-lifecycle',
    title: 'Incident status lifecycle',
    category: 'status',
    keywords: ['status', 'open', 'investigating', 'resolved', 'closed', 'lifecycle', 'state'],
    phrases: ['what does investigating mean', 'incident states', 'when is an incident resolved'],
    answer: `Statuses describe **where work stands**:

- **Open** — Reported, not yet actively owned
- **Investigating** — Team is actively diagnosing
- **Resolved** — Mitigation applied; monitoring for stability
- **Closed** — Fully done; post-incident notes may be complete

Status appears on badges in lists, detail pages, timeline cards, and analytics. Changing status (when not in demo mode) is done via API/UI updates — **Start Investigation** adds analysis but does not automatically change status.`,
    followUpSuggestions: ['How does AI investigation work?', 'Severity vs status?'],
    relatedTopicIds: ['ai-investigation', 'severity'],
  },
  {
    id: 'severity',
    title: 'Severity levels',
    category: 'severity',
    keywords: ['severity', 'critical', 'high', 'medium', 'low', 'priority', 'urgent', 'triage'],
    phrases: ['what do severity levels mean', 'how serious is an incident'],
    answer: `Severity is **impact / urgency** (four levels):

- **Critical** — Major outage or serious risk; respond immediately
- **High** — Significant impact; urgent response
- **Medium** — Limited blast radius
- **Low** — Minor or early signal

Shown on badges and analytics. It helps **triage** — it does not auto-remediate.`,
    followUpSuggestions: ['Difference between High and Critical?', 'How do I filter by severity?'],
    relatedTopicIds: ['severity-compare', 'analytics'],
  },
  {
    id: 'severity-compare',
    title: 'High vs Critical severity',
    category: 'severity',
    keywords: ['difference', 'high', 'critical', 'compare', 'versus', 'vs'],
    phrases: [
      'what is the difference between high and critical',
      'high vs critical',
      'critical versus high severity',
    ],
    answer: `**Critical** is the highest tier: widespread outage, major data/security risk, or SLA-threatening impact — all-hands response.

**High** is serious but usually **narrower** than Critical — important service degraded, significant users affected, still urgent but may not be company-wide catastrophe.

Both need fast response; **Critical** wins when you must drop everything. Use analytics and the dashboard to see how many of each you have in the current database.`,
    followUpSuggestions: ['What do status levels mean?', 'How does investigation help?'],
    relatedTopicIds: ['status-lifecycle', 'ai-investigation'],
  },
  {
    id: 'ai-investigation',
    title: 'AI investigation workflow',
    category: 'investigation',
    keywords: ['ai', 'investigation', 'investigate', 'ollama', 'mock', 'template', 'hypothesis', 'server failure'],
    phrases: [
      'how can i investigate a server failure',
      'how does ai investigation work',
      'run an investigation',
    ],
    answer: `**AI investigation** helps analyze an incident after you open it.

1. Open **Incidents** → select an incident → **Incident detail**.
2. Click **Start Investigation** (or call the investigate API).
3. Backend gathers context; **templates** (API failure, database, network) may apply when relevant.
4. An **AI provider** returns structured analysis. In **demo mode**, a **mock** result is returned — no paid external API required.

Investigation **does not** auto-change incident status; it adds **analysis** for humans to verify.`,
    followUpSuggestions: ['What happens when I click Investigate?', 'How do I read investigation results?'],
    relatedTopicIds: ['investigate-button', 'investigation-results'],
  },
  {
    id: 'investigate-button',
    title: 'Start Investigation button',
    category: 'investigation',
    keywords: ['click investigate', 'start investigation', 'button', 'what happens when'],
    phrases: ['what happens when i click investigate', 'when i press start investigation'],
    answer: `When you click **Start Investigation** on the incident detail page:

1. The frontend sends a **POST** to \`/incidents/{id}/investigate\`.
2. In **demo mode**, the API returns a **mock investigation JSON** (no external AI call).
3. You should see a success toast (**Investigation started**) when the request succeeds.
4. Results include hypotheses, recommendations, and diagnostic steps to read on the response / UI.

If the API blocks the request (network/CORS/demo limits), you'll see an error toast instead — the incident itself is not modified by the chatbot.`,
    followUpSuggestions: ['How do I interpret investigation results?', 'Demo mode restrictions?'],
    relatedTopicIds: ['investigation-results', 'demo'],
  },
  {
    id: 'investigation-results',
    title: 'Understanding investigation results',
    category: 'results',
    keywords: ['results', 'recommendations', 'findings', 'hypotheses', 'confidence', 'root cause', 'evidence', 'interpret'],
    phrases: ['how do i interpret investigation results', 'read the investigation output', 'read investigation output'],
    answer: `Look for:

- **Summary / findings** — Plain-language explanation
- **Root cause hypotheses** — Ranked ideas with **confidence** where provided
- **Recommendations** — Next steps (logs, rollback, scaling, etc.)
- **Diagnostic steps** — Ordered checks for your team
- **Template metadata** — Which playbook applied, if any

Treat output as **human-in-the-loop assistance**. In **demo mode**, responses are **illustrative**. Verify against real logs and systems.`,
    followUpSuggestions: ['What investigation templates exist?', 'Can AI fix production automatically?'],
    relatedTopicIds: ['limitations', 'ai-investigation'],
  },
  {
    id: 'timeline',
    title: 'Timeline and events',
    category: 'timeline',
    keywords: ['timeline', 'events', 'chronological', 'history', 'audit', 'incident created'],
    phrases: ['what shows on the timeline', 'incident events'],
    answer: `The **Timeline** page lists **events** across incidents (newest first), such as:

- Incident created / updated / resolved
- Investigation started / completed
- Alerts (when present in data)

Filter by **event type** and **search** text. Cards link back to the incident. Events come from the API per incident — not from this chatbot.`,
    followUpSuggestions: ['How do filters work?', 'Dashboard vs timeline?'],
    relatedTopicIds: ['navigation', 'analytics'],
  },
  {
    id: 'analytics',
    title: 'Analytics and filtering',
    category: 'analytics',
    keywords: ['analytics', 'chart', 'breakdown', 'metrics', 'statistics', 'filtering', 'graphs'],
    phrases: ['how do analytics work', 'severity breakdown chart'],
    answer: `**Analytics** shows database-driven **severity** and **status** breakdowns (counts and percentages from your SQLite data).

**Incidents** and **Timeline** pages add **filters** (service, severity, status, search). Analytics is read-only visualization — it does not auto-alert or monitor live infrastructure.`,
    followUpSuggestions: ['Is this live monitoring?', 'What is demo mode?'],
    relatedTopicIds: ['demo', 'severity'],
  },
  {
    id: 'demo',
    title: 'Demo mode and monitoring',
    category: 'demo',
    keywords: ['demo', 'production', 'real', 'monitoring', 'live', 'sample', 'read-only', 'render', 'automatically'],
    phrases: [
      'is this a demo or real production monitoring',
      'can this monitor my production servers automatically',
      'does it watch my servers',
    ],
    answer: `**This public demo is not automatic production monitoring.**

- It does **not** ingest live metrics/alerts from your servers by itself.
- It uses **sample incidents** in a demo database (\`incidents_demo.db\`).
- **Demo mode** blocks writes (create/update/delete) and hides public API docs.
- Dashboard health may show **Read-only demo**.

A private deployment with a full DB and writable API is a separate configuration.`,
    followUpSuggestions: ['What can I still do in demo mode?', 'Why did create incident fail?'],
    relatedTopicIds: ['limitations', 'troubleshooting'],
  },
  {
    id: 'troubleshooting',
    title: 'Errors and troubleshooting',
    category: 'troubleshooting',
    keywords: ['not work', 'broken', 'error', 'network', 'loading', 'failed', 'stuck', 'blank', 'why am i getting an error'],
    phrases: ['why am i getting an error', 'page wont load', 'api down'],
    answer: `Try:

1. **Refresh** the page (deep links like \`/incidents/:id\` should recover).
2. Check **platform health** on the dashboard — API down shows load errors.
3. **Local/preview**: run API + frontend; production builds need \`VITE_API_BASE_URL\`.
4. **Demo limits**: forbidden on create/edit = **read-only demo** (expected).
5. **CORS/network**: investigation POST needs demo CORS allowing POST from your frontend origin.

See **README** and \`project_memory/RENDER_DEPLOY.md\` for deployment details.`,
    followUpSuggestions: ['What is demo mode?', 'How does investigation POST work?'],
    relatedTopicIds: ['demo', 'investigate-button'],
  },
  {
    id: 'limitations',
    title: 'Platform limitations',
    category: 'limitations',
    keywords: ['limitation', 'cannot', 'does not', 'not support', 'missing', 'wont', "can't"],
    phrases: ['what can this platform not do', 'what are the limitations', 'will ai fix production'],
    answer: `Documented limitations:

- **Not** a full observability stack (no always-on prod monitoring in the demo).
- **Not** autonomous remediation — humans verify investigations.
- **Demo mode** blocks mutating API calls except allowed paths like **investigate** mock POST.
- **Guide chatbot** is documentation-based — not a trained generative model.
- Some API constraint fields are not exposed on HTTP investigate (see README).

Do not treat demo investigation output as ground truth for real outages.`,
    followUpSuggestions: ['What is demo mode?', 'How does investigation work?'],
    relatedTopicIds: ['demo', 'ai-investigation'],
  },
  {
    id: 'faq-monitoring',
    title: 'FAQ — monitoring',
    category: 'faq',
    keywords: ['monitor', 'alert', 'pager', 'datadog', 'prometheus', 'grafana', 'automatic'],
    phrases: ['connect to my monitoring', 'pull alerts from'],
    answer: `This MVP **does not ship** a built-in connector to Datadog, Prometheus, PagerDuty, etc. You **manually** create or import incidents via the API in a full deployment.

The demo shows **sample data** only. Integrations would be custom work outside this guide's scope.`,
    followUpSuggestions: ['What does this project do?', 'Demo vs production?'],
    relatedTopicIds: ['what-is', 'demo'],
  },
];
