# Exercise 3: RICE and the MVP Cut

**Time:** 45 to 60 minutes
**Needs:** Exercise 1 done (the workspace has `research/usage_metrics.csv` and `research/interview_notes.md`)
**You produce:** `research/rice-q1-2027.md` (scored table and the MVP cut) and `docs/stakeholder-update-q1-2027-mvp.md` (one page for leadership).

## Scenario

Planning for Q1 2027 starts on Monday. There are 8 candidate features for Northwind Expense and room for about a third of them. The head of Finance wants multi-currency, sales leadership wants receipt capture, and the support team wants anything that cuts tickets.

Your job: score all 8 with RICE using the team's agreed rules, cut the MVP to the squad's capacity, and write the one-page update that tells leadership what is in, what is out, and why.

## Inputs

| File | What it is |
|---|---|
| `../../_data/northwind/usage_metrics.csv` | the 8 candidate features: `feature`, `area`, `monthly_active_users`, `support_tickets_per_month`, `avg_minutes_to_submit_claim` |
| `inputs/effort-estimates.md` | the RICE rules (Reach, Impact, Confidence), effort in person-months, capacity (10 person-months) and the cut rule |
| `../../_data/northwind/interview_notes.md` | P1 to P6, used for Confidence |
| `../../_data/northwind/support_tickets.csv` | ticket sample, for quotes in the update |

## Setup

```bash
cp exercises/pm/03-rice-and-mvp-cut/inputs/effort-estimates.md workspaces/pm/research/
cp exercises/_data/northwind/usage_metrics.csv workspaces/pm/research/   # skip if done in exercise 1
```

## Task

1. **Score (20 minutes).** In `research/rice-q1-2027.md`, build one table with these columns: `Rank | Feature | Reach | Tickets per 1,000 users | Minutes to submit | Impact | Confidence | Effort | RICE`. Follow `inputs/effort-estimates.md` exactly. Ask Cursor to compute it, then check two rows by hand, including one that sits close to a tier boundary.
2. **Cut (10 minutes).** Apply the cut rule with 10 person-months. Under the table, list the MVP features, the effort used, and the features left out.
3. **Challenge your own cut (10 minutes).** Write a short "What the score does not see" section: risks in the effort notes, dependencies, and whether a different set of features would deliver more total RICE in the same 10 person-months. Say whether you keep the rule's cut or recommend a change, and why.
4. **Write the stakeholder update (15 minutes).** `docs/stakeholder-update-q1-2027-mvp.md`, one page, these sections:
   - **Decision:** the MVP in one sentence.
   - **Why these:** the top of the RICE table (3 to 5 rows), with the evidence in plain words: users, tickets, interview quotes.
   - **What is out and when we look again:** each cut feature with one reason.
   - **Risks:** at least 2, each with an owner.
   - **Ask:** what you need from leadership, with a date.

   Use the same section shape `/pm-report` uses for status (executive summary first, then detail, then risks), so leadership reads every PM update the same way.
5. **Hand off.** Run `/next-session`. Record the ranking and the cut in the transition doc.

## Commands to use

```
/start-session pm
# score, cut and write with Cursor chat in research/ and docs/
/next-session
```

Optional, for the stretch: `/architect pm exercises/pm/03-rice-and-mvp-cut/README.md` to plan a PRD for the MVP, then `/pm-validate`.

## How it is checked

1. **Instructor key.** Your RICE table, ranking and cut are compared with the key. Scores must match to the decimal when the rules were followed.
2. **Self-check before you hand in.** Re-run the numbers: the efforts of your MVP features add up to 10 or less, and nothing left out would still fit in the remaining capacity.
3. **Peer read.** Swap stakeholder updates with a neighbor. They must be able to say, in one sentence, what ships and what does not.

## Done when

- [ ] `research/rice-q1-2027.md` scores all 8 features with every input column shown
- [ ] Ranking and scores match the key (one decimal place)
- [ ] The MVP cut follows the rule and uses 10 person-months or less
- [ ] "What the score does not see" names at least 2 risks from the effort notes and compares at least one alternative cut by total RICE
- [ ] The stakeholder update fits on one page, starts with the decision, and every claim has a number or a source
- [ ] Every cut feature has a reason and a "look again" point
- [ ] No policy or data number in the update contradicts the input files

## Stretch

- **Sensitivity.** Which single input change would move Mobile offline drafts into the MVP? Try Confidence 100% (a second interview) and Effort 3. Which is more believable?
- **The loudest voice.** Finance wants multi-currency. Show where it ranks and what you would need to believe for it to make the cut. Put that in the update as a sentence, not a debate.
- **From cut to PRD.** Run `/architect pm` for the MVP, draft the PRD skeleton, and run `/pm-validate` on it.
