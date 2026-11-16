# ECDSA provers

Both backends share one workspace pinned to reth v2.7.0 (`fa9e76a`) and revm 43,
independent of the root node's EVM. There is no runtime EVM selector.

| Crate | Purpose |
| --- | --- |
| `eez-prover-stateless` | Replays streamed witnesses through the stateless fork and provides the `eez-proof-signer` binary. |
| `eez-prover-stateful` | Runs a revm follower, imports candidate blocks through its engine and signs against its local L2 database. |
| `eez-proof-signer` | Shared gRPC, admission, settlement validation, public-input recomputation and attestation. |
| `eez-prover-evm` | Execution rules used by both backends, including stateful import, payload construction, derivation and checkpoint replay. |

## Shared follower and protocol crates

`eez-follower` and its supporting crates come from a pinned eez-rollup0 Git
revision. Its default `node-evm` feature is disabled. The stateful executable
calls `eez_follower::run_with`, supplies `eez-prover-evm` and its RPC converter, and starts its signer
after the follower has synchronized and established its L1-derived anchor.
The node's task executor coordinates graceful shutdown of the service.

The protocol crates also come from eez-rollup0: `eez-primitives`, `eez-protocol`,
`eez-payload-codec`, `eez-blob`, `eez-control-rpc`, `eez-prover` and
`eez-prover-client`. These contain no git-pinned reth dependencies.

A dependency uses its **owning revision's workspace dependencies**. This lets
root move to evm2 while this workspace retains an evm1-compatible follower
revision. Separate lockfiles alone would not make a path dependency into an
evm2 checkout use evm1. When updating the Git pins, keep the follower revision
compatible with this workspace's reth; port follower fixes to that revision
when root's reth APIs have moved. Update the protocol pins as needed and run
all tests. Do not add a dependency on the root `eez-evm` or a prover dependency
in the root follower library.

In eez-rollup0, `scripts/provers-cargo.sh` redirects protocol crates to the
current checkout while leaving follower dependencies pinned. Its optional
`EEZ_PROVERS_FOLLOWER_SOURCE` override is for developing shared follower code
from a checkout using the compatible reth stack.

## Build and test

```bash
cargo build --locked -p eez-prover-stateless -p eez-prover-stateful --bins
cargo nextest run --locked --workspace
cargo clippy --locked --workspace --all-targets -- -D warnings
docker build --target proof-signer -t eez-proof-signer .
docker build --target stateful-prover -t eez-prover-stateful .
```

See the [stateless](crates/eez-prover-stateless/README.md) and
[stateful](crates/eez-prover-stateful/README.md) configuration guides.
Both EVMs replay `testing/evm-golden/execution.json`; root reads these fixtures
through its `provers/` submodule. Execution-rule changes must update both EVMs.
The stateless streaming test also replays copied `prove.v1` conformance vectors
against the real binary; refresh them when changing the protocol.
