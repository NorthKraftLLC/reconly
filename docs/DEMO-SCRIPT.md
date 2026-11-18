# Reconly — Customer Demo Script

*Follow this step-by-step. Each step has what to click, what to say, and what the viewer should see.*

---

## Pre-Flight Checklist

- [ ] Backend running: `http://localhost:8001/health` returns `{"status":"ok"}`
- [ ] Frontend running: `http://localhost:3000` loads
- [ ] Clean browser session (Incognito/Private window)
- [ ] Demo account ready: `demo@reconly.io` / `DemoPass1234`
- [ ] Screen recording software ready (Loom, QuickTime, etc.)

---

## Step 1 — Sign Up (0:00 – 0:30)

**What you see:** Deep indigo login screen with Reconly logo, frosted glass card.

**Say:**

> "Let me show you how fast you can get started. No credit card, no phone call. Just your email and you're in."

**Do:**

1. Open `http://localhost:3000`
2. Click **"Sign up free"** at the bottom
3. Type email: `yourname@yourcompany.com`
4. Type password (12+ characters)
5. Click **"Create account"**
6. Dashboard loads instantly

**Viewer sees:** Smooth transition from login to dashboard. No loading screens. Account created.

---

## Step 2 — First Look at the Dashboard (0:30 – 1:00)

**What you see:** Dashboard with 4 stat cards and 3 quick-action cards.

**Say:**

> "This is your command center. Everything about your inventory — at a glance. Right now everything is zero because we just started. By the end of this demo, you'll see it all populate in real time."

**Point to each card:**

- **Companies** — how many businesses you're tracking
- **Items Reconciled** — total items scanned across all reconciliations
- **Active Reconciliations** — currently running comparisons
- **Open Discrepancies** — items that need your attention (this is the money metric)

**Say:**

> "The three action cards below let you jump straight into anything. Let's start from the beginning."

---

## Step 3 — Add Your First Company (1:00 – 1:45)

**Do:**

1. Click **"Companies"** in the left sidebar
2. Type a company name: `"Acme Retail"`
3. Type industry: `"Retail"`
4. Click **"+ Add Company"**
5. Success message appears, company shows in the table

**Say:**

> "You can manage inventory for as many companies as you need. Each one is completely separate. Your system tracks company name, auto-generates a slug for URLs and APIs, and stores the industry for context."

**Point to:** The clean table showing company name, slug, industry, and creation date.

**Say:**

> "See that slug? That's used in all your API calls and report links. No guessing, no typos."

---

## Step 4 — Stock Your Inventory (1:45 – 3:00)

**Do:**

1. Click **"Inventory"** in the sidebar
2. Select your company from the dropdown
3. Click **"+ Add Item"**
4. Fill in a sample item:
   - SKU: `WIDGET-001`
   - Name: `Premium Widget`
   - Qty on Hand: `500`
   - Unit Cost: `12.50`
   - Category: `Widgets`
5. Click **"Add Item"**
6. Item appears in the table
7. Repeat 2–3 more items with different SKUs and quantities

**Say:**

> "This is your system of record. Every item gets a unique SKU, a name, quantity on hand, unit cost, and category. The system automatically calculates the total value of each line — so you always know what your inventory is worth."

**Point to:** The **Total Value** column — this is system qty × unit cost.

**Say:**

> "You can search by name or SKU at any time. Everything filters instantly."

---

## Step 5 — Run Your First Reconciliation (3:00 – 4:30)

**This is the core feature. Slow down here.**

**Do:**

1. Click **"Reconciliations"** in the sidebar
2. Make sure your company is selected in the dropdown
3. Click **"+ New Reconciliation"** (orange button)
4. Modal slides up
5. Name it: `"Q4 Physical Count"`
6. In the JSON source data area, paste the physical count data

**Say:**

> "Here's where the magic happens. This is the reconciliation engine — the reason you're here.
>
> Here's the scenario: you have inventory recorded in your system. But you just did a physical warehouse count and the numbers don't quite match. This engine compares your system records against your physical count and instantly flags every single discrepancy.
>
> You paste in your source data — this could be from a warehouse count sheet, a supplier delivery, a POS system, whatever. The engine handles the rest."

**Say (while filling out the modal):**

> "The format is simple: two arrays — your system's numbers and the physical count's numbers. Each item needs a SKU, name, quantity, and cost."

7. Click **"Run Reconciliation"**
8. Redirects to the detail page

---

## Step 6 — The Results (4:30 – 6:00)

**This is the "wow" moment.**

**What you see:** Reconciliation detail page with summary stats and discrepancies table.

**Say:**

> "Look at that. The engine just scanned every item and told you exactly what matches and what doesn't.
>
> Up top you've got your summary: total items scanned, how many matched perfectly, and how many discrepancies were found.
>
> And here's the table that matters."

**Point to the Discrepancies table:**

- Each row shows the SKU, item name, system quantity vs source quantity
- The **difference** column is highlighted in red for shortages, orange for overages
- The **severity badge** tells you how critical each one is — critical, high, medium, or low
- The **explanation** column tells you what kind of discrepancy it is

**Say:**

> "Every discrepancy is automatically classified by severity. Critical items get flagged so you can prioritize what to investigate first. You can see at a glance whether something is a small counting error or a real shrinkage problem.
>
> And each discrepancy tracks whether it's been resolved — so you never lose track of an open issue."

---

## Step 7 — Export Reports (6:00 – 6:30)

**Do:**

1. Click the **PDF** button in the top right
2. PDF downloads
3. Open it to show the formatted report

**Say:**

> "Need to share this with your team, your accountant, or your supplier? One click. PDF, CSV, or Excel — whichever format your workflow needs.
>
> The report is professionally formatted, includes all discrepancy details, severity classifications, and timestamps. It's meeting-ready."

---

## Step 8 — Wrap Up (6:30 – 7:00)

**Do:**

1. Navigate back to the **Dashboard**
2. Point out that the stats have updated

**Say:**

> "And that's it. From empty account to full reconciliation in under seven minutes.
>
> Here's what you get with Reconly:
>
> - **Instant setup** — sign up and you're running in seconds
> - **Multi-company support** — manage inventory for any number of businesses
> - **Smart discrepancy detection** — catch shortages, overages, and missing items automatically
> - **Severity classification** — know what to fix first
> - **One-click exports** — PDF, CSV, Excel for any stakeholder
> - **Track resolution** — never lose track of an open issue
>
> Your inventory problems are solved the moment you log in. That's Reconly."

---

**End of Demo — ~7 minutes total**
