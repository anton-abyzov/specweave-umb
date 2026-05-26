// Shape vocabulary — JSDoc only, no runtime types needed.
// Mirrors src/verify/core/types.ts in cwc-workshops/phase-3-verify.

/**
 * @typedef {"PASS"|"FAIL"|"BLOCKED"|"SKIP"} Verdict
 *
 * @typedef {Object} Check
 * @property {string} id
 * @property {"ok"|"fail"|"warn"|"probe"} status
 * @property {string} [message]
 * @property {unknown} [actual]
 * @property {unknown} [expected]
 *
 * @typedef {Object} Invariant
 * @property {string} id
 * @property {string} description
 * @property {(surface: any) => boolean | Promise<boolean>} predicate
 *
 * @typedef {Object} FixtureCtx
 * @property {string} workdir          - tmp workdir created per fixture
 * @property {Record<string,string>} env - extra env vars for child processes
 *
 * @typedef {Object} Fixture
 * @property {string} id
 * @property {string} description
 * @property {boolean} [probe]
 * @property {(ctx: FixtureCtx) => Promise<any>} act - returns the surface object
 *
 * @typedef {Object} VerifiableUnit
 * @property {string} id
 * @property {string} command           - human description ("vskill install <source>")
 * @property {any}    surfaceSchema     - Zod schema for surface
 * @property {Invariant[]} invariants
 * @property {Fixture[]} fixtures
 *
 * @typedef {Object} FixtureResult
 * @property {string} unitId
 * @property {string} fixtureId
 * @property {boolean} probe
 * @property {Verdict} verdict
 * @property {Check[]} checks
 * @property {any} [surface]
 * @property {number} durationMs
 * @property {string} [blockedReason]
 *
 * @typedef {Object} UnitResult
 * @property {string} unitId
 * @property {string} command
 * @property {Verdict} verdict
 * @property {FixtureResult[]} fixtures
 *
 * @typedef {Object} RunAllResult
 * @property {string} version
 * @property {string} runAt
 * @property {Verdict} verdict
 * @property {UnitResult[]} units
 */

export {};
