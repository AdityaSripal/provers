#!/usr/bin/env python3
"""Check normal/build dependency closures from cargo metadata on stdin."""
import json
import sys

metadata = json.load(sys.stdin)
packages = {p['id']: p for p in metadata['packages']}
nodes = {n['id']: n for n in metadata['resolve']['nodes']}


def closure(name):
    start = [p['id'] for p in packages.values() if p['name'] == name]
    assert len(start) == 1, f'expected one {name}, got {start}'
    seen, pending = set(), start
    while pending:
        package = pending.pop()
        if package in seen:
            continue
        seen.add(package)
        pending.extend(d['pkg'] for d in nodes[package]['deps']
                       if any(k['kind'] != 'dev' for k in d['dep_kinds']))
    return [packages[p] for p in seen]


for backend in ('eez-prover-stateful', 'eez-prover-stateless'):
    graph = closure(backend)
    names = {p['name'] for p in graph}
    assert {'eez-prover-evm', 'eez-proof-signer', 'revm'} <= names
    assert not names & {'eez-evm', 'eez-node', 'eez-composer'}, names
    assert not any(n.startswith('evm2') for n in names), names
    assert {p['version'].split('.')[0] for p in graph if p['name'] == 'revm'} == {'43'}
    reth = {p['source'] for p in graph
            if p['name'].startswith('reth-') and (p['source'] or '').startswith('git+')}
    assert len(reth) == 1 and 'fa9e76ab4fd69d8323c3bbbbe43470f64aa47cb7' in next(iter(reth)), reth
    if backend == 'eez-prover-stateful':
        assert 'eez-follower' in names
    print(f'{backend}: prover EVM, revm 43, one reth pin; no node EVM or composer dependency')

follower = {p['name'] for p in closure('eez-follower')}
assert not follower & {'eez-prover-stateful', 'eez-prover-stateless', 'eez-proof-signer'}
