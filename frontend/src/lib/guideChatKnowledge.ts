/**
 * Documentation-based answers for the homepage guide chatbot.
 * Content reflects implemented features only (no live production monitoring claims).
 */

export type GuideTopic = {
  id: string;
  title: string;
  keywords: string[];
  answer: string;
};

export const GUIDE_WELCOME =
  'Hi! I\'m the DevOps Incident Commander guide. I can explain what this app does, how to use incidents, timelines, analytics, and AI investigation—in plain English. Pick a suggestion below or type your own question.';

export const GUIDE_SUGGESTED_QUESTIONS = [
  'What is DevOps Incident Commander?',
  'Is this a demo or real production monitoring?',
  'How do I create and manage an incident?',
  'What do severity levels mean?',
  'How does AI investigation work?',
  'How do I use the dashboard and analytics?',
];

export const GUIDE_TOPICS: GuideTopic[] = [
  {
    id: 'what-is',
    title: 'What is DevOps Incident Commander?',
    keywords: [
      'what is',
      'devops incident commander',
      'about',
      'project',
      'platform',
      'this website',
      'this app',
    ],
    answer: `**DevOps Incident Commander** is a web app for tracking production-style incidents and running **AI-assisted investigations**.

It helps teams:
1. **Record** incidents (title, service, severity, status, description)
2. **Review** history on a **timeline** of events
3. **See trends** on the **dashboard** and **analytics** pages
4. **Run investigations** that suggest hypotheses and next steps

This UI talks to a **FastAPI backend** with a SQLite database. On public demo hosting it runs in **read-only demo mode** with sample data—not a live connection to your real servers.`,
  },
  {
    id: 'purpose',
    title: 'Purpose of this website',
    keywords: ['purpose', 'why', 'goal', 'use case', 'who is this for', 'help me understand'],
    answer: `The purpose is to give you a **single place to understand and work through incidents** during an outage or drill.

You can:
- See **how many** incidents are open, investigating, or resolved
- **Filter and search** incidents by service, severity, and status
- Open an incident for **details** and **start an AI investigation**
- Browse a **global timeline** of events across incidents

It is built as an **MVP / demo-friendly** product: great for learning incident response workflows and trying AI-guided analysis, not for replacing your full observability stack.`,
  },
  {
    id: 'how-works',
    title: 'How the platform works',
    keywords: ['how does', 'how it works', 'architecture', 'flow', 'steps', 'overview'],
    answer: `Here is the flow, step by step:

1. **Dashboard (home)** — Summary metrics, recent incidents, and platform health (including whether **demo mode** is on).
2. **Incidents** — List with filters, search, sorting, and pagination. Click a row to open **incident details**.
3. **Incident detail** — Full description, status, and actions such as **Start Investigation** (when the API allows it).
4. **Timeline** — Chronological **events** (created, updated, investigation started/completed, etc.) with filters.
5. **Analytics** — Charts for severity and status breakdowns.
6. **Settings** — Appearance (theme/accent) and other UI preferences stored locally in your browser.

Data is loaded through **REST API** calls from the React frontend. The chatbot is **guide-only**—it does not create or change incidents for you.`,
  },
  {
    id: 'incidents',
    title: 'Create and manage incidents',
    keywords: [
      'create',
      'manage',
      'incident',
      'new incident',
      'edit',
      'delete',
      'resolve',
      'patch',
      'crud',
    ],
    answer: `**In a full (non–read-only) deployment**, incidents are managed via the API:
- **Create** with title, description, service, severity, and status
- **Update** fields (for example move status from open → investigating → resolved)
- **Delete** when appropriate
- **List** with filters, search, sort, and pagination

**In demo / read-only mode** (common on public demos and Render):
- You can **view** sample incidents and explore the UI
- **Creating, editing, and deleting** incidents is **blocked** (the API returns forbidden)
- Use the sample data to learn the workflows

To work with an incident: go to **Incidents** → open one → read details or start **Investigation** if enabled.`,
  },
  {
    id: 'severity',
    title: 'Severity levels',
    keywords: ['severity', 'critical', 'high', 'medium', 'low', 'priority', 'urgent'],
    answer: `Severity tells people **how serious** an incident is. This app uses four levels:

- **Critical** — Major outage or data risk; many users affected; respond immediately
- **High** — Significant impact; respond urgently
- **Medium** — Limited blast radius; schedule focused work
- **Low** — Minor issue or early warning; handle when convenient

Severity appears on **badges** in lists, the dashboard, timeline cards, and analytics charts. It helps you **triage** what to look at first—it does not auto-fix anything.`,
  },
  {
    id: 'ai-investigation',
    title: 'AI investigation',
    keywords: [
      'ai',
      'investigation',
      'investigate',
      'ollama',
      'mock',
      'template',
      'hypothesis',
    ],
    answer: `**AI investigation** helps you think through an incident after you open it on the **Incident detail** page.

1. Click **Start Investigation** (or use the investigate API).
2. The backend gathers **incident context** and may apply **investigation templates** (for example API failure, database, or network patterns) when they fit.
3. An **AI provider** analyzes the situation. In **demo mode**, a **mock provider** returns structured sample results—no external paid API key required.
4. Optional **evidence** can be sent with the request in non-demo setups; the public UI focuses on the core flow.

Investigation does **not** change incident status by itself; it adds **analysis** you can read and act on.`,
  },
  {
    id: 'investigation-results',
    title: 'Understanding investigation results',
    keywords: [
      'results',
      'recommendations',
      'findings',
      'hypotheses',
      'confidence',
      'root cause',
      'evidence',
    ],
    answer: `When an investigation finishes, look for:

- **Findings / summary** — Plain-language explanation of what might be wrong
- **Root cause hypotheses** — Ranked ideas with **confidence** scores where provided
- **Recommendations** — Suggested next steps (check logs, rollback, scale service, etc.)
- **Diagnostic steps** — Ordered checks your team can run
- **Template info** — If a built-in template applied, it shows which playbook was used

Treat these as **assistance for humans**, not automatic truth. Verify against your real logs and systems. In demo mode, responses are **illustrative** to show the UX.`,
  },
  {
    id: 'navigation',
    title: 'Dashboard, filters, timeline, analytics',
    keywords: [
      'dashboard',
      'filter',
      'timeline',
      'analytics',
      'chart',
      'search',
      'navigation',
      'sidebar',
    ],
    answer: `**Dashboard** — Open **/** for metric cards, recent incidents, activity feed, and platform health (including demo mode).

**Incidents** — Use **Service**, **Severity**, and **Status** filters plus **search**. Change page size and sort as needed. Click a row for details.

**Timeline** — See events across incidents; filter by event type and search text. Cards show severity/status and timestamps.

**Analytics** — Visual breakdowns of incidents by severity and status.

**Settings** — Theme (light/dark) and accent color; preferences save in your browser.

Use the **left sidebar** (or mobile menu) to move between sections.`,
  },
  {
    id: 'demo',
    title: 'Demo vs production',
    keywords: [
      'demo',
      'production',
      'real',
      'monitoring',
      'live',
      'sample',
      'read-only',
      'render',
    ],
    answer: `**This public demo is not real-time production monitoring.**

- It does **not** watch your live servers, metrics, or alerts automatically.
- It uses **sample / synthetic incidents** in a demo database (\`incidents_demo.db\` on the server).
- **Demo mode** blocks writes (create/update/delete) and disables public API docs.
- The dashboard **health** section may show **Read-only demo** when demo mode is on.

A private deployment could use a full database and writable API—that is a separate configuration from the public demo.`,
  },
  {
    id: 'troubleshooting',
    title: 'Something does not work',
    keywords: [
      'not work',
      'broken',
      'error',
      'network',
      'loading',
      'failed',
      'help',
      'stuck',
      'blank',
    ],
    answer: `Try these steps:

1. **Refresh** the page. Deep links like \`/incidents/:id\` should still load after refresh.
2. **Check platform health** on the dashboard—if the API is down, you'll see load errors.
3. **Local preview**: run the **API** and frontend together. Production builds need \`VITE_API_BASE_URL\` pointing at your API (see README / Render docs).
4. **Demo limits**: if create/edit fails with forbidden, you're in **read-only demo**—that's expected.
5. **Theme issues**: toggle appearance under **Settings**; hard refresh if the UI looks stale after an update.

For code and deployment details, see the project **README** and \`project_memory/RENDER_DEPLOY.md\` in the repository.`,
  },
];

export const GUIDE_FALLBACK_ANSWER =
  'I don\'t have a specific answer for that yet. I\'m a documentation-based guide (not a live AI model). Try one of the suggested questions, or ask about incidents, severity, investigation, timeline, analytics, or demo mode. For more detail, check the README in the GitHub repository.';
