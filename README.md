# provers

Proof backends for [eez-rollup0](https://github.com/eez-association/eez-rollup0).
Each backend family has its own Cargo workspace, lockfile and execution pins.

| Directory | Backends |
| --- | --- |
| [`ecdsa/`](ecdsa) | Stateless witness replay (`eez-proof-signer`) and a stateful revm follower (`eez-prover-stateful`), sharing settlement validation and ECDSA attestation. |

Composers communicate with both backends through `prove.v1` gRPC. Stateful
proving embeds shared follower code from a pinned eez-rollup0 revision and owns
its local L2 database. Both backends use this repository's `eez-prover-evm`.
The ordinary follower binary remains in eez-rollup0.
