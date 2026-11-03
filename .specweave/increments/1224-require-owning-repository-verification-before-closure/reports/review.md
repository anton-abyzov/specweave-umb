# Review of increment 1224

Verdict: ship

Fresh reviewer: adoption_review. Reviewed the patch at eba73e6052ea269a0d395dff34390fadeb0e5120 after the strict verification receipt timestamped 2026-11-03T23:37:53.170Z.

The initial proposal used only the SpecWithCode PR gate, which selects server tests from the merge-base diff. On an up-to-date main checkout that selection can contain zero server files. The reviewed configuration now pairs the package, typecheck and fleet stages with the full server sharded command. The server command receives no changed-file filter and rejects an empty full run. The canonical and legacy repository keys both carry these commands.

The published 3.1.21 fixture exercised both owner keys. It confirmed that neither owner gate could be masked by a successful supplemental command, that both ran in the intended directory, and that completion rejected an open task and a missing fresh review. The separate actual umbrella verification reported all three root commands green, 2/2 acceptance criteria met, and zero strict validation errors. Coverage targets retain their existing values.

The fixture uses stub product packages to verify routing and failure handling. It does not certify a SpecWithCode build. The strict CLI requires explicit umbrella-relative task Files to identify a nested repository. Product-relative legacy paths need owner migration before they can select product checks, and CLI versions older than 3.1.21 do not enforce the new policy.
