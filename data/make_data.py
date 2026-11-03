"""Generate demo data for the invoice-chasing agent: Bloomfield Bakery Ltd (fictional).
As-of date: 2 November 2026. Default terms 30 days. All amounts in euro."""
import pandas as pd
from datetime import date, timedelta

AS_OF = date(2026, 11, 2)
D = lambda s: date.fromisoformat(s)

customers = {
    "C01": "The Corner Café, Tullamore",
    "C02": "Riverside Hotel, Birr",
    "C03": "O'Brien's Centra, Portlaoise",
    "C04": "The Daily Grind, Mountmellick",
    "C05": "Kilcormac Community Centre",
    "C06": "Rosie's Deli, Athlone",
    "C07": "Abbeyleix Golf Club",
    "C08": "Bridge House Hotel, Tullamore",
    "C09": "The Tea Room, Clara",
    "C10": "Green Fields Market Stall, Mullingar",
    "C11": "St. Brigid's Nursing Home, Portarlington",
    "C12": "Lakeview Restaurant, Banagher",
    "C13": "Spar Edenderry",
    "C14": "The Bakehouse Café, Rathdowney",
    "C15": "Midlands Events Catering",
}

# (tag, customer, invoice date, amount, payment) ; payment = (date, amount, quote_ref, bank_text) or None
# tags for planted cases start with "T_"
inv = []
def add(tag, cust, d, amt, pays=None):
    inv.append(dict(tag=tag, cust=cust, date=D(d), amount=amt, pays=pays or []))

# --- routine paid history (prompt payers) ---
routine = [
    ("C01","2026-08-04",412.50,9), ("C01","2026-08-28",388.00,11),
    ("C02","2026-08-06",1084.60,26), ("C02","2026-08-27",962.40,28),
    ("C03","2026-08-07",455.80,20),
    ("C05","2026-08-11",236.00,15), ("C05","2026-09-15",198.50,18), ("C05","2026-10-14",244.00,14),
    ("C06","2026-08-12",610.00,24),
    ("C07","2026-08-05",735.00,29),
    ("C09","2026-08-13",318.40,27), ("C09","2026-09-10",296.00,25),
    ("C10","2026-08-20",64.80,6), ("C10","2026-09-17",58.20,5),
    ("C11","2026-08-18",842.00,30), ("C11","2026-09-16",815.50,29),
    ("C12","2026-08-14",588.00,22),
    ("C13","2026-08-19",704.30,17), ("C13","2026-09-18",688.90,19),
    ("C14","2026-08-21",276.00,12), ("C14","2026-09-22",301.50,16),
]
for c, d, a, lag in routine:
    add("paid", c, d, a, [(D(d)+timedelta(days=lag), a, True, None)])

# serial late payer history: paid, but well after due date
for d, a, lag in [("2026-07-03",540.00,52), ("2026-08-07",515.60,49)]:
    add("paid_late", "C04", d, a, [(D(d)+timedelta(days=lag), a, True, None)])

# --- planted cases ---
add("T_loyal_late",   "C01", "2026-09-27", 396.20)                        # 6 days overdue, loyal
add("T_standard",     "C02", "2026-09-13", 1012.80)                       # 20 days overdue, normal
add("T_paid_noref",   "C03", "2026-09-02", 486.20,
    [(D("2026-09-28"), 486.20, False, "OBRIENS CENTRA PTL")])            # paid, no invoice number
add("T_serial_late",  "C04", "2026-09-08", 528.40)                        # 25 days overdue, serial late
add("T_part_paid",    "C06", "2026-09-10", 920.00,
    [(D("2026-10-15"), 500.00, True, None)])                              # €420 balance
add("T_60day_terms",  "C07", "2026-09-05", 768.00)                        # system says 30 days, agreed 60
add("T_plan_1",       "C08", "2026-07-10", 640.00)
add("T_plan_2",       "C08", "2026-07-31", 590.00)
add("T_plan_3",       "C08", "2026-08-21", 510.00)
add("T_dispute",      "C09", "2026-09-15", 342.60)
add("T_small",        "C10", "2026-09-20", 18.40)
add("T_credit_note",  "C12", "2026-09-01", 640.00)
add("T_dup_original", "C15", "2026-09-24", 1150.00,
    [(D("2026-10-21"), 1150.00, True, None)])
add("T_dup_error",    "C15", "2026-09-24", 1150.00)

# --- not yet due (October invoices) ---
for c, d, a in [("C01","2026-10-20",405.00), ("C02","2026-10-12",1046.20), ("C03","2026-10-09",471.30),
                ("C06","2026-10-16",585.00), ("C11","2026-10-14",828.40), ("C12","2026-10-08",602.50),
                ("C13","2026-10-16",715.60), ("C14","2026-10-20",289.00), ("C04","2026-10-13",498.20)]:
    add("not_due", c, d, a)

# number invoices in date order
inv.sort(key=lambda r: (r["date"], r["cust"]))
for i, r in enumerate(inv):
    r["no"] = f"INV-{2001+i}"
    r["due"] = r["date"] + timedelta(days=30)   # what the accounts system says
T = {r["tag"]: r for r in inv if r["tag"].startswith("T_") and not r["tag"].startswith("T_plan")}
plan = [r for r in inv if r["tag"].startswith("T_plan")]

# --- invoices export (as from Sage/Xero) ---
rows = []
for r in inv:
    rows.append(dict(document_no=r["no"], type="Invoice", customer_id=r["cust"],
                     customer_name=customers[r["cust"]], date=r["date"], due_date=r["due"],
                     amount_eur=r["amount"], applies_to=""))
cn = T["T_credit_note"]
rows.append(dict(document_no="CN-0007", type="Credit note", customer_id="C12",
                 customer_name=customers["C12"], date=D("2026-09-08"), due_date="",
                 amount_eur=-85.00, applies_to=cn["no"]))
invoices = pd.DataFrame(rows).sort_values(["date", "document_no"])

# --- bank statement ---
bank = []
for r in inv:
    for (pd_, amt, ref, txt) in r["pays"]:
        if txt is None:
            short = customers[r["cust"]].split(",")[0].upper().replace("'", "")[:18]
            txt = f"{short} {r['no']}" if ref else short
        bank.append(dict(date=pd_, description=txt, money_in_eur=amt, money_out_eur=""))
bank += [
    dict(date=D("2026-10-01"), description="BRIDGE HOUSE HTL PLAN", money_in_eur=300.00, money_out_eur=""),
    dict(date=D("2026-10-31"), description="BRIDGE HOUSE HTL PLAN", money_in_eur=300.00, money_out_eur=""),
]
for d, txt, amt in [("2026-08-05","ODLUMS FLOUR DD",1840.00), ("2026-08-15","ESB NETWORKS DD",612.40),
                    ("2026-08-28","WAGES",6420.00), ("2026-09-05","ODLUMS FLOUR DD",1795.00),
                    ("2026-09-15","ESB NETWORKS DD",598.10), ("2026-09-29","WAGES",6420.00),
                    ("2026-10-05","ODLUMS FLOUR DD",1910.50), ("2026-10-15","ESB NETWORKS DD",641.70),
                    ("2026-10-30","WAGES",6420.00), ("2026-10-12","REVENUE VAT",2318.00),
                    ("2026-09-22","KERRY DAIRY SUPPLIES",1204.30), ("2026-10-22","KERRY DAIRY SUPPLIES",1188.90)]:
    bank.append(dict(date=D(d), description=txt, money_in_eur="", money_out_eur=amt))
bank = pd.DataFrame(bank).sort_values("date")

# --- customer notes (the owner's head, written down) ---
plan_total = sum(r["amount"] for r in plan)
notes = pd.DataFrame([
    ("ALL", "2026-01-10", "House rule: balances under €25 are not chased. Add them to the customer's next invoice."),
    ("ALL", "2026-01-10", "House rule: never send a reminder on an invoice the customer is disputing. Ring them instead."),
    ("C01", "2026-03-02", "Customer for 12 years. Always pays, sometimes a week or so late in quiet months. Keep it friendly."),
    ("C02", "2026-05-14", "Accounts handled by head office in Dublin. Send reminders to accounts@ address on file."),
    ("C03", "2026-04-20", "Pays by bank transfer from their own banking app. Often forgets to put the invoice number."),
    ("C04", "2026-09-30", "Late again. Paid the July and August invoices nearly 7 weeks late. Third time chasing this year. Next one should be firmer."),
    ("C06", "2026-10-15", "Rosie rang, short this month, paid part of the September invoice. Said rest would follow."),
    ("C07", "2026-09-01", f"Agreed 60-day payment terms with the club treasurer from September invoices on. Accounts system not updated yet."),
    ("C08", "2026-09-15", f"Hotel struggling after the refurb. Agreed payment plan: €300 on the 1st of each month until the €{plan_total:,.2f} owed on {plan[0]['no']}, {plan[1]['no']} and {plan[2]['no']} is cleared. Do not send reminders while the plan payments keep coming in."),
    ("C09", "2026-09-17", f"Owner complained crates arrived damaged and half the scones unusable. Disputing {T['T_dispute']['no']}. Need to sort a partial credit."),
    ("C10", "2026-06-01", "Small weekly stall order. Very small amounts."),
    ("C12", "2026-09-08", f"Short delivery on {cn['no']}: credit note CN-0007 for €85 issued."),
    ("C15", "2026-09-26", f"{T['T_dup_error']['no']} was raised in error, a duplicate of {T['T_dup_original']['no']}. To be voided. Customer told."),
], columns=["customer_id", "note_date", "note"])
notes.insert(1, "customer_name", notes["customer_id"].map(lambda c: customers.get(c, "(all customers)")))

# --- answer key ---
def r_(t): return T[t]
key = [
    (r_("T_loyal_late"), "Overdue 6 days", "CHASE: gentle reminder", f"€{r_('T_loyal_late')['amount']:.2f}", "Loyal 12-year customer, only a week late. Friendly nudge."),
    (r_("T_standard"), "Overdue 20 days", "CHASE: standard reminder", f"€{r_('T_standard')['amount']:.2f}", "Control case. Normal overdue invoice, no special notes."),
    (r_("T_serial_late"), "Overdue 25 days", "CHASE: firm reminder", f"€{r_('T_serial_late')['amount']:.2f}", "Serial late payer, notes say next reminder should be firmer."),
    (r_("T_part_paid"), "Looks paid (invoice number on bank line)", "CHASE: balance only", "€420.00", "Part payment of €500 on 15 Oct. Remaining €420 is overdue."),
    (r_("T_credit_note"), "Overdue 32 days", "CHASE: reduced amount", "€555.00", "Credit note CN-0007 (€85) applies. Chase €555, not €640."),
    (r_("T_paid_noref"), "Overdue (no matching reference)", "DO NOT CHASE: already paid", "€0.00", "€486.20 received 28 Sep from O'Brien's Centra with no invoice number. Amount and name match."),
    (r_("T_60day_terms"), "Overdue 28 days per system", "DO NOT CHASE: not yet due", "€0.00", "60-day terms agreed. Really due 4 Nov 2026."),
    (plan[0], "Overdue (3 invoices, oldest 85 days)", "DO NOT CHASE: payment plan on track", "€0.00", f"Plan covers {plan[0]['no']}, {plan[1]['no']}, {plan[2]['no']}. €300 received 1 Oct and 31 Oct."),
    (r_("T_dispute"), "Overdue 18 days", "DO NOT CHASE: phone about dispute", "€0.00", "Customer disputing damaged delivery. House rule: ring, never send a reminder."),
    (r_("T_small"), "Overdue 13 days", "DO NOT CHASE: under €25", "€0.00", "€18.40. House rule: add to next invoice."),
    (r_("T_dup_error"), "Overdue 9 days", "DO NOT CHASE: duplicate raised in error", "€0.00", f"Duplicate of {r_('T_dup_original')['no']}, which is paid. To be voided."),
]
answer = pd.DataFrame([dict(case=i+1, document_no=(r["no"] if r is not plan[0] else f"{plan[0]['no']}, {plan[1]['no']}, {plan[2]['no']}"),
                            customer_name=customers[r["cust"]], what_it_looks_like=look, correct_action=act,
                            amount_to_chase=amt, why=why) for i, (r, look, act, amt, why) in enumerate(key)])

import os; out = os.path.dirname(os.path.abspath(__file__))
import os; os.makedirs(out, exist_ok=True)
invoices.to_csv(f"{out}/invoices.csv", index=False)
bank.to_csv(f"{out}/bank_statement.csv", index=False)
notes.to_csv(f"{out}/customer_notes.csv", index=False)
answer.to_csv(f"{out}/answer_key.csv", index=False)

# --- sanity check: what a naive workflow would flag ---
paid_refs = set()
for d in bank["description"]:
    for w in str(d).split():
        if w.startswith("INV-"): paid_refs.add(w)
inv_only = invoices[invoices.type == "Invoice"]
naive = inv_only[(pd.to_datetime(inv_only.due_date).dt.date < AS_OF) & (~inv_only.document_no.isin(paid_refs))]
print(f"{len(invoices)} documents, {len(bank)} bank lines, {len(notes)} notes")
print("Naive workflow would chase:")
print(naive[["document_no", "customer_name", "due_date", "amount_eur"]].to_string(index=False))
print("\nAnswer key:")
print(answer[["case", "document_no", "correct_action", "amount_to_chase"]].to_string(index=False))
