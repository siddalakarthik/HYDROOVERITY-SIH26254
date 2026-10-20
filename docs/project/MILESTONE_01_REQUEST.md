# HYDROOVERITY — MILESTONE 01: PROFESSIONAL GITHUB REPOSITORY SETUP

## YOUR ROLE

You are now the Lead Software Engineer, GitHub Repository Architect, DevOps Engineer, and Technical Documentation Engineer for **HYDROOVERITY**, Team TARK's Smart India Hackathon 2026 hardware project.

You have already received our complete authoritative HYDROOVERITY Master Context document.

Use that document as the primary project specification throughout this task.

Do not reinterpret the project, invent a new architecture, or introduce unnecessary technologies.

I want you to take responsibility for establishing a professional, maintainable, scalable, secure GitHub repository that can support the project's entire development lifecycle.

The repository must eventually contain our working website, backend APIs, scientific simulation engines, mechanical CAD, electronic schematics, embedded firmware, reproducible experiments, test automation, technical documentation, and explanation-video assets.

**You are authorized to create the repository, initialize the development workspace, create the required foundational files, make the initial commit, and push it to GitHub if your environment has the necessary authenticated access.**

If authentication or permissions are missing, do not claim success. Explain the precise blocker and provide the minimum steps needed to resolve it.

Do not request my password or access token in chat.

---

# 1. PROJECT IDENTITY

Use the following project identity exactly:

**Project name:** HYDROOVERITY

**Team:** TARK

**Competition:** Smart India Hackathon 2026

**Problem Statement ID:** SIH26254

**Category:** Hardware

**Problem statement:** Development of Indigenous Leak Detection Sensor Systems for Operation & Maintenance of Water Supply Pipelines

**Problem setter:** Ministry of Jal Shakti

**Hardware prototype material budget ceiling:** ₹60,000 INR

**Repository name:**

`HYDROOVERITY-SIH26254`

**Proposed repository description:**

"HYDROOVERITY — Indigenous evidence-qualified pipeline leak detection, localization and water-network maintenance platform for SIH26254, Team TARK."

Do not introduce version labels such as V6, V7, V8, or arbitrary product renaming.

HYDROOVERITY is the project's official name.

---

# 2. VERIFY THE DEVELOPMENT ENVIRONMENT

Before creating the repository:

1. Check the current workspace directory.
2. Check whether Git is installed and functioning.
3. Check whether GitHub authentication is available.
4. Check whether the GitHub CLI (`gh`) is installed and authenticated, or whether a compatible connected GitHub tool can create repositories.
5. Check which GitHub account or organization the repository would belong to.
6. Check whether a repository with the requested name already exists under that owner.
7. Verify whether the current directory contains unrelated files or an existing Git repository.

Never delete or overwrite unrelated files.

If the requested repository already exists, inspect it before proceeding. Do not force-push, overwrite its history, or initialize a conflicting repository.

If the authenticated GitHub owner is clearly available, proceed with that account.

If multiple GitHub accounts or owners are available and ownership is ambiguous, ask me to select the owner before creation.

If GitHub access is unavailable, prepare the local repository only if the current workspace allows it, and clearly report what remains incomplete.

---

# 3. CREATE THE GITHUB REPOSITORY

Create:

`HYDROOVERITY-SIH26254`

Required settings:

- Visibility: **PRIVATE**
- Default branch: `main`
- Git repository initialized
- Repository description configured
- No secrets or credentials committed
- No unrelated starter applications
- No fictional research results
- No fabricated hardware measurements

Do not invite collaborators yet.

Do not enable GitHub Pages or publish the project publicly.

Do not automatically select a software licence. We will make that decision before public release.

Ensure that the local repository is linked to the correct GitHub remote.

---

# 4. CREATE THE COMPLETE MONOREPO STRUCTURE

Create the following organizational structure, adapting only when technically justified:

```text
HYDROOVERITY-SIH26254/
│
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── SECURITY.md
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .env.example
│
├── apps/
│   └── web/
│
├── services/
│   ├── api/
│   ├── ingestion/
│   └── notifications/
│
├── packages/
│   ├── shared-types/
│   └── shared-config/
│
├── simulations/
│   ├── hydraulics/
│   ├── acoustics/
│   ├── guard5/
│   ├── scenarios/
│   ├── evaluation/
│   └── results/
│
├── hardware/
│   ├── guard5-collar/
│   ├── hydro-watch/
│   ├── acoustic-acquisition/
│   ├── mechanical-cad/
│   ├── electronics/
│   ├── firmware/
│   ├── bom/
│   └── calibration/
│
├── data/
│   ├── demo/
│   ├── schemas/
│   └── samples/
│
├── docs/
│   ├── project/
│   ├── requirements/
│   ├── architecture/
│   ├── research/
│   ├── engineering/
│   ├── testing/
│   ├── deployment/
│   ├── decisions/
│   └── presentations/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── security/
│
├── scripts/
│
├── design/
│   ├── ui-ux/
│   ├── wireframes/
│   └── design-system/
│
├── animation/
│   ├── storyboard/
│   ├── scripts/
│   ├── scenes/
│   └── renders/
│
└── .github/
    ├── workflows/
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

Git does not track empty directories, so use appropriate README files or `.gitkeep` placeholders.

Do not generate hundreds of meaningless files.

Establish a clean, useful foundation, not unnecessary boilerplate.

---

# 5. CREATE THE ROOT README

Write a professional `README.md` explaining:

- What HYDROOVERITY is.
- Which government problem it addresses.
- Why pipeline leak detection matters.
- Why rural and intermittent water-supply systems present special difficulties.
- The complete proposed sensing architecture.
- What GUARD-5 does.
- What HYDRO-WATCH does.
- What the acoustic sensing system does.
- How evidence qualification works.
- How work orders and repair verification work.
- The planned website and simulation modules.
- The ₹60,000 hardware materials ceiling.
- The development roadmap.
- Repository navigation.
- Current project status.
- Scientific limitations.
- How future developers can contribute.

Keep the README professional, technically accurate, and understandable to SIH judges and engineers.

Do not claim that our hardware has been physically tested.

Do not invent detection accuracy, sensor range, battery life, cost savings, patentability, or field deployment results.

Clearly distinguish:

**Designed / Implemented in software / Simulated / Physically tested / Field validated.**

Our current physical hardware validation status is unverified and must not be presented as complete.

---

# 6. CREATE THE CODEX INSTRUCTIONS FILE

Create `AGENTS.md` at the repository root.

This file must guide all future Codex work.

It should establish the following permanent rules:

### Project integrity

- Preserve HYDROOVERITY's frozen conceptual architecture.
- Do not arbitrarily add sensing technologies.
- Never fabricate test results.
- Never mix simulated data with measured sensor data.
- Respect the ₹60,000 physical prototype materials ceiling.
- Keep all changes traceable.
- Follow existing architecture documents.
- Record important design decisions.
- Prefer simple, reliable engineering over unnecessary complexity.

### Coding standards

- Use TypeScript for frontend development.
- Use Python for backend and scientific simulation development.
- Prefer strict typing and clearly documented interfaces.
- Write automated tests for important logic.
- Handle errors explicitly.
- Avoid hardcoded secrets.
- Keep frontend, backend, hardware and simulation responsibilities separate.
- Write maintainable, modular code.
- Avoid unnecessary dependencies.

### Scientific standards

- Simulation results must identify assumptions.
- Every scientific experiment should have repeatable input parameters.
- Use deterministic random seeds where applicable.
- Keep ground truth separate from the detection algorithm.
- Report false positives, false negatives, localization errors and unresolved cases.
- Do not label simulated sensor values as physical measurements.
- Never conceal failures or select only favorable trials.

### Security

- No credentials in source code.
- No production secrets in Git history.
- Authorization must be enforced by the backend.
- Citizen accounts must not access internal utility information.
- Never expose device-control endpoints without authorization.
- Do not introduce real infrastructure actuation without explicit approval.
- Never execute destructive commands without reviewing their targets.

### Workflow

For future implementation tasks:

1. Inspect the relevant existing files.
2. State the implementation plan.
3. Make focused changes.
4. Run appropriate tests.
5. Report exactly what changed.
6. Report what passed and failed.
7. Commit only completed and authorized changes.
8. Explain any unresolved blockers.

---

# 7. CREATE THE PROJECT'S AUTHORITATIVE DOCUMENTATION

Inside `docs/`, establish these documents:

**PROJECT_CHARTER.md**

Project identity, purpose, stakeholders, intended users, budget, deliverables and scope boundaries.

**SYSTEM_REQUIREMENTS.md**

Trace the exact SIH26254 requirements to planned HYDROOVERITY capabilities.

**SYSTEM_ARCHITECTURE.md**

Describe HYDRO-WATCH, GUARD-5, acoustic sensing, evidence qualification, backend, website and repair verification.

**HARDWARE_STATUS.md**

Document what has been designed, what has not been built and what needs laboratory validation.

**SIMULATION_PLAN.md**

Define our hydraulic, acoustic and GUARD-5 simulation objectives, assumptions and required outputs.

**WEBSITE_REQUIREMENTS.md**

Describe our complete multi-role water-utility platform.

Include:

- Administrator
- Utility engineer
- Maintenance supervisor
- Field worker
- Citizen/customer

**DATA_DICTIONARY.md**

Define the main future data entities:

- Users
- Organizations
- Roles
- Water zones
- Pipeline segments
- Sensors
- Sensor observations
- Supply states
- Incidents
- Leak-location estimates
- Evidence records
- Work orders
- Repairs
- Verification records
- Citizen complaints
- Feedback
- Simulation runs
- Simulation scenarios
- Hardware configurations

Every sensor observation must support explicit provenance distinguishing simulated, measured laboratory and field data.

**ENGINEERING_LIMITATIONS.md**

Explain the project's real physical limitations, including:

- Very weak plastic-pipe leak acoustics.
- Low-pressure and no-pressure operation.
- Unknown acoustic propagation speed.
- Sparse access to buried pipelines.
- Multiple leaks and branches.
- Rain and environmental moisture.
- False confidence.
- Unproven hardware reliability.

**DECISION_LOG.md**

Record the decisions already frozen, their reasoning and conditions under which they may be revisited.

**ROADMAP.md**

Define staged development milestones from GitHub setup to final SIH presentation.

**EVIDENCE_REGISTER.md**

Document what evidence exists and what remains to be demonstrated.

If the exact historical software-test results are not available in this workspace, do not reproduce them as newly verified results. Attribute earlier results to their original documentation and mark their verification status.

Use the attached Master Context for actual project facts.

Avoid invented specifications.

---

# 8. ESTABLISH WEBSITE DEVELOPMENT REQUIREMENTS

Do not implement the website yet.

However, organize its future development around a real working multi-user application.

Target stack:

- Next.js
- React
- TypeScript
- Tailwind CSS
- Python FastAPI
- PostgreSQL
- PostGIS
- MapLibre
- Recharts or equivalent
- Docker Compose
- Pytest
- Vitest
- Playwright

These are provisional stack selections. Record compatibility, hosting and integration decisions before installing dependencies.

The completed website must eventually include:

1. Real user authentication.
2. Role-based authorization.
3. Pipeline network dashboard.
4. Sensor observations.
5. Live alerts.
6. Geospatial pipe map.
7. Leak investigation.
8. Work-order assignment.
9. Worker mobile workflows.
10. Citizen complaint submission.
11. Repair verification.
12. Maintenance prioritization.
13. Reporting and exports.
14. Sensor diagnostics.
15. Simulated data integration.
16. Feedback and improvement tracking.
17. Offline handling where practical.
18. Persistent database storage.
19. Audit history.
20. Secure APIs.

No fake login, decorative buttons, hardcoded incidents pretending to be live data, or nonfunctional forms in the finished application.

---

# 9. ESTABLISH SIMULATION REQUIREMENTS

Do not implement simulation engines in this milestone.

Document the planned simulation work:

### Hydraulic simulation

Use EPANET/WNTR where appropriate for:

- Pipeline network hydraulic behavior.
- Water demand.
- Pressure changes.
- Leakage scenarios.
- Tank behavior.
- Pump operating states.
- Intermittent-supply operating windows.

Do not misrepresent EPANET as a complete transient, water-hammer or trapped-air simulator.

### Acoustic simulation

Include:

- Actual leak position as hidden ground truth.
- Acoustic signal generation assumptions.
- Pipe length and effective wave speed.
- Attenuation.
- Sensor noise.
- Synchronization effects.
- Correlation algorithms.
- Localization uncertainty.
- False and unresolved locations.
- Multiple leaks.
- Multipath and difficult conditions.

### GUARD-5 simulation

Include:

- Internal joint leakage.
- External rainfall.
- Independent sensing channels.
- Water migration.
- Drainage.
- Collector blockage.
- Bypass witness activation.
- Sensor failure.
- Maintenance self-test.

Do not claim a simple numerical model proves actual fluid transport through a fabricated collar.

Every simulator must eventually produce reproducible experiment records and clearly marked synthetic outputs.

---

# 10. PREPARE HARDWARE DOCUMENTATION

Do not fabricate CAD models or PCB schematics yet.

Create an organized place for:

- GUARD-5 mechanical models.
- Water collection channel design.
- Maintenance test-port design.
- Pipeline rig drawings.
- Pump and pressure specifications.
- Acoustic pickup specifications.
- ESP32 electrical schematics.
- Stereo ADC clocking and analog front end.
- Pressure and flow sensor interfaces.
- Wetness electrode electronics.
- Power distribution.
- PCB layouts.
- Firmware.
- Calibration procedures.
- Component procurement lists.

Add the project's ₹60,000 ceiling.

Treat previous budget figures as estimates, not supplier-verified procurement totals.

---

# 11. CONFIGURE GITHUB WORKFLOW

Set up a professional but lightweight development process.

Use:

- `main` for stable, reviewed code.
- Short-lived feature branches for new work.
- Descriptive commits.
- Pull requests for substantial changes.
- A change log or decision log for important architecture decisions.

Create useful GitHub issue templates for:

- Feature request
- Bug report
- Engineering investigation
- Simulation experiment
- Hardware design task

Create a pull request template with:

- Summary
- Linked issue
- Files changed
- Test evidence
- Simulation/physical-data status
- Security considerations
- Remaining limitations

If GitHub permits, configure practical labels such as:

- `frontend`
- `backend`
- `simulation`
- `hardware`
- `documentation`
- `bug`
- `enhancement`
- `security`
- `testing`
- `blocked`

Do not enforce branch-protection rules that would prevent a single authorized maintainer from working until our collaborator arrangement is known.

---

# 12. ADD BASIC AUTOMATED QUALITY CHECKS

Create a lightweight GitHub Actions workflow appropriate for a repository that does not yet contain a completed application.

Initially, the checks may verify:

- Required documentation files exist.
- Required directories exist.
- Referenced foundational files are present.
- A basic repository-integrity validation script passes.

Use minimal dependencies and explicitly scoped permissions.

Do not make up test-success badges.

Do not create fake frontend or backend unit tests for code that has not been implemented.

Add real application and simulation tests in later milestones.

---

# 13. SECURITY AND REPOSITORY HYGIENE

Configure `.gitignore` for:

- `.env`
- `.env.local`
- `.env.*` except `.env.example`
- Python virtual environments
- Python caches
- Node modules
- Next.js build outputs
- Temporary files
- Local databases
- User-uploaded files containing private information
- Generated simulation outputs where appropriate
- CAD temporary or backup files
- Large video renders
- Local secrets and credentials

Provide a safe `.env.example` containing variable names and clearly marked placeholders only.

Do not store passwords, API keys or private access tokens.

Document how large simulation artifacts, rendered videos and CAD exports will be managed without bloating the Git repository.

---

# 14. CREATE THE INITIAL DEVELOPMENT BACKLOG

Create or document the following major milestones in this order:

**M01 — GitHub Foundation**

Repository, documentation, workflows and issue organization.

**M02 — Website Architecture**

Design system, role definitions, API contracts and database schema.

**M03 — Backend Foundation**

Authentication, organization data, pipeline records and incident management.

**M04 — Frontend Foundation**

Navigation, user-specific dashboards and responsive interface.

**M05 — Scientific Simulations**

Hydraulic, acoustic and GUARD-5 simulation engines.

**M06 — Simulation Integration**

Connect simulation outputs to the actual backend and monitoring interface.

**M07 — Maintenance Operations**

Citizen complaints, work orders, repair verification and reporting.

**M08 — Digital Hardware Engineering**

Mechanical CAD, electronics schematics, firmware and final BOM.

**M09 — Full-System Testing**

Security, correctness, simulation validity, performance and workflow verification.

**M10 — Final Demonstration**

Professional video, engineering visuals, recorded website demonstration and SIH presentation.

Create GitHub milestones and a concise initial issue backlog if the authenticated GitHub tooling supports them. Avoid creating duplicate or excessive issues.

---

# 15. INITIAL COMMIT AND GITHUB PUSH

After completing the foundation:

1. Review the generated repository structure.
2. Confirm that no secrets are staged.
3. Confirm the repository points to the intended private GitHub remote.
4. Run the repository-integrity check.
5. Resolve any failures.
6. Create a meaningful initial commit.
7. Push to the `main` branch.
8. Verify that the repository and files actually exist remotely.
9. Confirm that the repository remains private.

Suggested initial commit message:

`chore: initialize HYDROOVERITY engineering monorepo`

If the push or creation fails, do not report success.

Preserve the local changes and give a precise recovery procedure.

---

# 16. REQUIRED FINAL REPORT TO ME

When you finish, provide:

### A. Repository information

- GitHub repository URL
- Repository owner
- Private/public status
- Default branch
- Latest commit hash
- Remote synchronization status

### B. Files and folders created

Summarize the actual repository structure.

### C. Documentation

List the foundational project documents and explain their purpose.

### D. GitHub development setup

Report whether issue templates, labels, milestones, pull request templates and workflow automation were successfully configured.

### E. Validation

Report every command or check actually executed and whether it passed.

Do not mark tests as passing unless they were run successfully.

### F. Access or permission problems

Identify any incomplete steps, including GitHub authentication or repository permissions.

### G. Next milestone readiness

Confirm whether the repository is ready for:

**M02 — HYDROOVERITY Website Architecture and Database Design.**

### H. Final engineering summary

Explain any contradictions discovered between the Master Context, our intended repository structure and this task.

Do not silently invent decisions to resolve significant contradictions.

---

# IMPORTANT LIMITS

This milestone is **repository infrastructure and project documentation only**.

Do not build:

- Website pages
- Authentication implementations
- Backend application endpoints
- Databases
- Scientific simulation engines
- CAD assemblies
- PCB designs
- Firmware implementations
- Animation scenes

Those will be handled in later milestones.

Do not overengineer this initialization.

Do not create placeholder software whose apparent completeness could mislead reviewers.

Do not copy code or assets from JalNaadi, AquaSense or other repositories without evaluating licences and attribution requirements.

Maintain a professional standard suitable for an engineering project that may be independently reviewed by SIH evaluators.

**Begin Milestone 01 now. Work carefully, verify everything, and finish by reporting exactly what was created and what remains incomplete.**