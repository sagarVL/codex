# Remote transport validation

This branch contains validation infrastructure and a characterization-test patch only. It makes no production fix and does not claim Avast compatibility.

The workflow fetches upstream commit 67f0994b532b8740f14b5b738af7b7b2a915b1d6 and applies the tests on GitHub-hosted Linux and Windows runners. Dependency identities are checked against its original lockfile. No OpenAI credentials or local laptop builds are required.

The focused jobs exercise transport libraries and custom CA integration. The codex-core fallback integration additions remain outside this focused build and require separate full-workspace validation. Passing this workflow alone does not validate the original OAuth/Web Guard failure.

The preliminary fallback patch remains unapplied. A production PR requires an established failure, a justified fix and actual regression evidence.
