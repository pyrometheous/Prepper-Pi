# Contributing to Prepper Pi

Thanks for your interest! This project is primarily a personal/DIY stack. Contributions are welcome for fixes and docs.

## Ground rules
- Respect third-party licenses and trademarks.
- Do not submit proprietary or confidential code.
- Keep PRs small, with a clear problem statement and testing notes.
- Expect best-effort review only; there is no SLA for triage or merging.

## License for contributions (inbound=outbound)
By opening a PR, you agree your contribution is licensed under:
- Code: Prepper Pi Noncommercial License (PP-NC-1.0) as in `LICENSE`.
- Docs/media: CC BY-NC 4.0 as in `LICENSE-DOCS`.

DIY builds are free under PP‑NC‑1.0. Any commercial sale of preconfigured hardware or services that ship/market the Prepper‑Pi stack requires a separate commercial license with revenue share (see `docs/legal/COMMERCIAL-LICENSE.md`).

This mirrors GitHub’s "inbound = outbound" convention. If you can’t accept these terms, please do not contribute.

## DCO sign-off
Include a Signed-off-by line in each commit message:

```
Signed-off-by: Your Name <your-username@users.noreply.github.com>
```

This asserts you have the right to contribute the code under the stated licenses.

## Development quick-start
- Scripts are designed for Linux hosts; some are placeholders pending hardware tests.
- Avoid committing secrets; use `.env` files locally and do not push them.

## Compliance notes
- When adding or enabling a new container or package, update `licenses/THIRD_PARTY_NOTICES.md` and ensure the release manifest captures immutable image digests.
- For GPL/AGPL components, ensure Corresponding Source is linked in the release per `licenses/SOURCE-OFFER.md`.