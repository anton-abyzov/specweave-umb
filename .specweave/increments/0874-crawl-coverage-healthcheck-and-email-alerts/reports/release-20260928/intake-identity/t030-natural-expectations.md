# Natural postrelease acceptance — T030

Baseline `t030-natural-baseline.json` at23:03:27Z: same sweep026ba568, shard1/page4, accepted399/discovered400, exact target hash e3b3310b… unresolved1. Historical totalLost694, totalErrors152 and recovered/source errorCount45 must never decrease. The original diagnostic counters were earlier snapshots, not a proposed reset target.

After parent supplies the new Worker UUID and its deployment-readback receipt, collect ONE snapshot with:

```
ssh -oBatchMode=yes -oConnectTimeout=10 root@5.161.56.136 'python3 -' < /tmp/cc-work-release-20260928/0874/t030-natural-snapshot.py > <new-owned-snapshot.json>
```

Use cwd `/Users/antonabyzov/Projects/sw-easychamp`. The remote script refuses changed crawler/scanner IDs and reads only Docker metadata, the existing private checkpoint, and localhost status GET. It never calls discovery/intake or prints raw identities.

Compare with `t030-verify-natural.py --snapshot <file> --worker-version <UUID> --deployment-receipt <root-readback.json> --output <new-verdict.json>`. Exit0 requires the latest deployment version at100%, a postdeployment natural run, unchanged process/container/sweep identity, retained cumulative failures/loss, and accepted399→400 in the original leaf or genuine cursor advancement with the original batch drained. A new later batch may have unresolved entries; that does not undo proof that this original batch drained. Whole-sweep coverage is not claimed. Nine offline positive/negative cases pass.

An optional `node t030-natural-db-read.cjs > <new-db-readback.json>` checks only the previously confirmed canonical tuple through hashes and a15-second READ ONLY transaction on the exact configured production DB. It confirms the same original row and public tenantless Skill; it makes no claim about scheduler acceptance or immutable lifecycle state.

If the original target remains pending, retain the failed verdict, wait for the normal retry cadence, and diagnose only a new concrete error. No manual replay, repair, backfill, reset, restart, cache flush, synthetic payload, or schema operation. The baseline and every snapshot/verdict remain separate immutable receipt files.
