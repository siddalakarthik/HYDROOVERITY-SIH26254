# GitHub development setup

`main` is the stable branch; future substantial changes use short-lived branches and PRs. No mandatory outside approval, collaborator invitations or Pages publishing are configured by M01. License remains undecided.

Five Markdown issue templates cover features, bugs, engineering investigations, simulation experiments and hardware tasks. The PR template requests scope, issue, files, test evidence, provenance, security and limitations. Use private disclosure rather than an issue for sensitive vulnerabilities.

The [backlog definitions](backlog.json) specify ten practical labels and M01–M10 milestone/issue descriptions, without deadlines or assignees. Remote configuration must be verified separately; this JSON alone is not proof of remote milestones/issues. Avoid duplicates when applying it.

[Repository integrity workflow](workflows/repository-integrity.yml) executes the same standard-library checker as local development, with contents:read, SHA-pinned checkout, no stored checkout credentials and no deployment or secret access. Its success concerns repository structure/documentation only. Actual application/scientific tests are added with implementations.

Security basis: [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use). The checkout pin was resolved from the official actions/checkout v6 ref during M01. Review future pin updates and permissions deliberately.
