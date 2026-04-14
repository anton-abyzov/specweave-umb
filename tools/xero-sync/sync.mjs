import { config } from "dotenv";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";

config();

const CLIENT_ID = process.env.XERO_CLIENT_ID;
const CLIENT_SECRET = process.env.XERO_CLIENT_SECRET;
const TENANT_ID = process.env.XERO_TENANT_ID || "";
const TOKEN_URL = "https://identity.xero.com/connect/token";
const API_BASE = "https://api.xero.com/api.xro/2.0";
const CONNECTIONS_URL = "https://api.xero.com/connections";

const DATA_DIR = join(import.meta.dirname, "data");
const TEST_ONLY = process.argv.includes("--test");

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error("Missing XERO_CLIENT_ID or XERO_CLIENT_SECRET in .env");
  process.exit(1);
}

async function getAccessToken() {
  const credentials = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString("base64");
  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: {
      "Authorization": `Basic ${credentials}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Token request failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  return data.access_token;
}

async function getTenantId(token) {
  const res = await fetch(CONNECTIONS_URL, {
    headers: { "Authorization": `Bearer ${token}` },
  });

  if (!res.ok) throw new Error(`Connections request failed (${res.status})`);
  const connections = await res.json();

  if (connections.length === 0) throw new Error("No connected Xero organisations found");

  console.log(`Connected org: ${connections[0].tenantName} (${connections[0].tenantId})`);
  return connections[0].tenantId;
}

async function apiGet(token, tenantId, endpoint, params = {}) {
  const url = new URL(`${API_BASE}/${endpoint}`);
  for (const [k, v] of Object.entries(params)) {
    url.searchParams.set(k, v);
  }

  const res = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Xero-Tenant-Id": tenantId,
      "Accept": "application/json",
    },
  });

  if (res.status === 429) {
    const retryAfter = parseInt(res.headers.get("Retry-After") || "5", 10);
    console.log(`  Rate limited, waiting ${retryAfter}s...`);
    await sleep(retryAfter * 1000);
    return apiGet(token, tenantId, endpoint, params);
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${endpoint} failed (${res.status}): ${text}`);
  }

  return res.json();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchAllPages(token, tenantId, endpoint, resultKey, options = {}) {
  const { orderBy = "UpdatedDateUTC DESC", where } = options;
  const allItems = [];
  let page = 1;

  while (true) {
    const params = { page: String(page), order: orderBy };
    if (where) params.where = where;

    console.log(`  Fetching ${endpoint} page ${page}...`);
    const data = await apiGet(token, tenantId, endpoint, params);
    const items = data[resultKey] || [];
    allItems.push(...items);

    if (items.length < 100) break;
    page++;
    await sleep(1100); // respect 60 calls/min rate limit
  }

  return allItems;
}

async function fetchJournals(token, tenantId) {
  const allJournals = [];
  let offset = 0;

  while (true) {
    console.log(`  Fetching Journals offset ${offset}...`);
    const data = await apiGet(token, tenantId, "Journals", { offset: String(offset) });
    const journals = data.Journals || [];
    allJournals.push(...journals);

    if (journals.length < 100) break;
    offset = journals[journals.length - 1].JournalNumber;
    await sleep(1100);
  }

  return allJournals;
}

function saveData(name, data) {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });

  const filePath = join(DATA_DIR, `${name}.json`);
  writeFileSync(filePath, JSON.stringify(data, null, 2));
  console.log(`  Saved ${Array.isArray(data) ? data.length : "1"} items to ${filePath}`);
}

function splitByYear(items, dateField) {
  const byYear = {};
  for (const item of items) {
    const raw = item[dateField];
    if (!raw) continue;
    const match = raw.match(/\d{4}/);
    const year = match ? match[0] : "unknown";
    if (!byYear[year]) byYear[year] = [];
    byYear[year].push(item);
  }
  return byYear;
}

async function main() {
  console.log("Authenticating with Xero...");
  const token = await getAccessToken();
  console.log("Token acquired.\n");

  const tenantId = TENANT_ID || await getTenantId(token);
  console.log();

  if (TEST_ONLY) {
    console.log("Connection test successful!");
    const orgData = await apiGet(token, tenantId, "Organisation");
    const org = orgData.Organisations?.[0];
    if (org) {
      console.log(`  Name: ${org.Name}`);
      console.log(`  Legal Name: ${org.LegalName}`);
      console.log(`  Country: ${org.CountryCode}`);
      console.log(`  Timezone: ${org.Timezone}`);
      console.log(`  Financial Year End: ${org.FinancialYearEndDay}/${org.FinancialYearEndMonth}`);
    }
    return;
  }

  console.log("=== Pulling Organisation Info ===");
  const orgData = await apiGet(token, tenantId, "Organisation");
  saveData("organisation", orgData.Organisations?.[0] || orgData);

  console.log("\n=== Pulling Chart of Accounts ===");
  const accounts = await apiGet(token, tenantId, "Accounts");
  saveData("accounts", accounts.Accounts || []);

  console.log("\n=== Pulling Contacts ===");
  const contacts = await fetchAllPages(token, tenantId, "Contacts", "Contacts");
  saveData("contacts", contacts);

  console.log("\n=== Pulling Bank Transactions (newest first) ===");
  const bankTxns = await fetchAllPages(token, tenantId, "BankTransactions", "BankTransactions", {
    orderBy: "Date DESC",
  });
  saveData("bank-transactions-all", bankTxns);

  const txnsByYear = splitByYear(bankTxns, "Date");
  for (const [year, items] of Object.entries(txnsByYear).sort((a, b) => b[0].localeCompare(a[0]))) {
    saveData(`bank-transactions-${year}`, items);
  }

  console.log("\n=== Pulling Invoices (newest first) ===");
  const invoices = await fetchAllPages(token, tenantId, "Invoices", "Invoices", {
    orderBy: "Date DESC",
  });
  saveData("invoices-all", invoices);

  const invByYear = splitByYear(invoices, "Date");
  for (const [year, items] of Object.entries(invByYear).sort((a, b) => b[0].localeCompare(a[0]))) {
    saveData(`invoices-${year}`, items);
  }

  console.log("\n=== Pulling Bank Statements (Statement Lines) ===");
  try {
    const statements = await apiGet(token, tenantId, "BankStatements");
    saveData("bank-statements", statements.BankStatements || statements);
  } catch (e) {
    console.log(`  Bank Statements endpoint not available: ${e.message}`);
  }

  console.log("\n=== Pulling Payments ===");
  const payments = await fetchAllPages(token, tenantId, "Payments", "Payments", {
    orderBy: "Date DESC",
  });
  saveData("payments-all", payments);

  console.log("\n=== Pulling Credit Notes ===");
  const creditNotes = await fetchAllPages(token, tenantId, "CreditNotes", "CreditNotes");
  saveData("credit-notes", creditNotes);

  console.log("\n=== Pulling Manual Journals ===");
  const manualJournals = await fetchAllPages(token, tenantId, "ManualJournals", "ManualJournals");
  saveData("manual-journals", manualJournals);

  console.log("\n=== Pulling Journals (Full Audit Trail) ===");
  const journals = await fetchJournals(token, tenantId);
  saveData("journals-all", journals);

  const journalsByYear = splitByYear(journals, "CreatedDateUTC");
  for (const [year, items] of Object.entries(journalsByYear).sort((a, b) => b[0].localeCompare(a[0]))) {
    saveData(`journals-${year}`, items);
  }

  console.log("\n=== Summary ===");
  console.log(`  Contacts:          ${contacts.length}`);
  console.log(`  Bank Transactions: ${bankTxns.length}`);
  console.log(`  Invoices:          ${invoices.length}`);
  console.log(`  Payments:          ${payments.length}`);
  console.log(`  Credit Notes:      ${creditNotes.length}`);
  console.log(`  Manual Journals:   ${manualJournals.length}`);
  console.log(`  Journals:          ${journals.length}`);
  console.log(`\nAll data saved to: ${DATA_DIR}`);

  const reconciledTxns = bankTxns.filter((t) => t.IsReconciled);
  const unreconciledTxns = bankTxns.filter((t) => !t.IsReconciled);
  console.log(`\n=== Reconciliation Status ===`);
  console.log(`  Reconciled:   ${reconciledTxns.length}`);
  console.log(`  Unreconciled: ${unreconciledTxns.length}`);
  saveData("bank-transactions-unreconciled", unreconciledTxns);
}

main().catch((err) => {
  console.error("Fatal error:", err.message);
  process.exit(1);
});
