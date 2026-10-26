# GitHub development setup

`main` is the accepted integration branch. Substantial changes use focused feature branches and pull requests. Merge only after the applicable review and exact-head checks, then verify post-merge CI. Do not bypass protection or force-push shared history.

The repository is public; that does not authorize public application deployment. The application retains its private-development safety gate. Project licensing is undecided; dependency notices and development-tool limitations remain documented.

The [required workflow](workflows/repository-integrity.yml) runs repository/design/simulation, backend, frontend/browser and CAD/figure validation. It uses pinned Actions, read-only repository permissions, and disposable test services. Uploaded evidence excludes credentials and private evaluation truth. The [root README](../README.md) describes current implementation and limitations; the [completion register](../docs/testing/PRE_M10_COMPLETION_REGISTER.md) preserves unresolved acceptance cases.

[Original backlog definitions](backlog.json) describe M01–M10 issues and labels. They are historical planning data, not proof that an issue is complete. Use private disclosure for security vulnerabilities; never publish credentials in an issue or pull request.
