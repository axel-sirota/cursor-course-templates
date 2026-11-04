# Exercise 1: expected findings

Open this after you have written `docs/eda/data-quality-findings.md`. Source: `exercises/_data/northwind/answer_key.json` (seed 2026). Every count below was recomputed from the CSVs with the definitions in the exercise README.

## Profile facts

| Fact | Value |
|---|---|
| `expense_lines.csv` shape | 9,176 rows x 12 columns |
| `expense_claims.csv` shape | 4,000 rows x 10 columns |
| Claim status | paid 3,415, approved 174, submitted 161, rejected 140, draft 110 |
| Claim currency | USD 3,668, EUR 126, GBP 120, CAD 86 |
| Line category | Ground transport 2,065, Meals 1,674, Lodging 1,396, Software 989, Office supplies 958, Airfare 873, Client entertainment 814, Training 399, blank 8 |
| `expense_date` range | 2026-05-18 to 2026-10-30 (claims are submitted Aug to Oct; some expenses are older) |
| Blank cells, lines | `category` 8, `gl_account_hint` 8, `attendees_count` 6,687 (expected: only Meals and Client entertainment carry it) |
| Blank cells, claims | `submitted_at` 110 (drafts), `approver_id` 271, `approved_at` 411, `paid_at` 585, `fx_rate` 3 |

## Issue counts

| # | Issue | Count | Unit |
|---|---|---|---|
| 1 | Exact duplicates | 90 | pairs (90 duplicate lines on 90 different claims) |
| 2 | Near-duplicates | 45 | pairs: 23 `amount_1_cent`, 22 `date_1_day` |
| 3 | Split under receipt threshold | 6 | groups (15 lines, each group spans 2 claims) |
| 4 | Weekend expenses | 30 | lines |
| 5 | Missing category | 8 | lines |
| 6 | Mixed currency without fx | 3 | lines, on 3 claims with blank `fx_rate` |
| 7 | Outlier | 1 | line (USD 9,800.00 Office supplies) |
| 8 | Alcohol | 25 | lines, all Meals, 6 at Copper Kettle Taproom |
| 9 | Over policy limit | 10 | lines: Meals 5, Lodging 4, Office supplies 1 |
| 10 | Missing receipt over $75 | 10 | lines |
| 11 | Older than 60 days | 4 | lines |
| 12 | Leakage column | 1 | `gl_account_hint` |

## Ids

### 1. Exact duplicates (original > duplicate)

L-000112>L-000327, L-000121>L-002976, L-000174>L-004340, L-000354>L-001489, L-000360>L-002605, L-000373>L-001018, L-000413>L-001313, L-000742>L-004234, L-000818>L-002251, L-000943>L-000965, L-001035>L-003877, L-001049>L-003100, L-001086>L-005323, L-001101>L-001804, L-001102>L-002243, L-001318>L-005181, L-001400>L-001604, L-001428>L-004223, L-001750>L-004443, L-001897>L-002961, L-002036>L-006310, L-002047>L-002953, L-002086>L-003190, L-002200>L-002674, L-002226>L-002897, L-002382>L-007251, L-002436>L-005367, L-002650>L-004325, L-002671>L-005255, L-002701>L-004028, L-002751>L-006614, L-002844>L-006551, L-002986>L-003272, L-003035>L-004284, L-003158>L-004421, L-003262>L-006084, L-003263>L-006838, L-003414>L-007324, L-003518>L-007100, L-003595>L-004088, L-003632>L-004723, L-003677>L-007210, L-003706>L-006694, L-003746>L-006630, L-003751>L-008911, L-003769>L-005523, L-004180>L-004863, L-004193>L-004344, L-004196>L-006170, L-004631>L-009083, L-004646>L-007151, L-004739>L-006733, L-004740>L-005946, L-004743>L-006439, L-004793>L-008958, L-004817>L-007810, L-005034>L-007083, L-005193>L-007045, L-005232>L-006749, L-005234>L-006899, L-005384>L-007914, L-005459>L-007379, L-005493>L-008872, L-005694>L-005763, L-005716>L-007830, L-005799>L-006193, L-005865>L-007939, L-005896>L-007647, L-005935>L-008988, L-006000>L-007539, L-006104>L-006618, L-006128>L-008827, L-006145>L-006701, L-006187>L-007705, L-006540>L-007338, L-006545>L-007752, L-006611>L-009003, L-006670>L-008121, L-006715>L-007886, L-006782>L-006916, L-007013>L-008377, L-007036>L-007040, L-007054>L-008927, L-008058>L-008464, L-008140>L-008870, L-008267>L-008931, L-008417>L-008834, L-008493>L-008567, L-008531>L-008618, L-008854>L-009016

The 90 duplicate lines add up to 2,548,410 cents in claim currency.

### 2. Near-duplicates

`amount_1_cent` (23): L-000138/L-001535, L-000465/L-004067, L-000722/L-001596, L-000783/L-004572, L-000888/L-001869, L-000937/L-001181, L-001115/L-005156, L-001603/L-005879, L-001854/L-003863, L-003679/L-005983, L-004150/L-007270, L-004200/L-006732, L-004320/L-008844, L-004562/L-007033, L-004927/L-008935, L-005436/L-007912, L-006447/L-008540, L-006950/L-008969, L-007023/L-007050, L-007174/L-008079, L-007256/L-008833, L-007691/L-007915, L-008382/L-008727

`date_1_day` (22): L-000107/L-002374, L-000297/L-000954, L-000809/L-003536, L-001829/L-002768, L-001837/L-003742, L-001886/L-003348, L-002630/L-003826, L-002665/L-006251, L-002699/L-004319, L-002801/L-005775, L-003261/L-003352, L-003578/L-004292, L-004179/L-007842, L-004328/L-005754, L-004776/L-005248, L-005610/L-005890, L-005758/L-006490, L-005981/L-008932, L-006259/L-007057, L-006707/L-009135, L-008208/L-008246, L-008978/L-009160

### 3. Split under receipt threshold

| line_ids | employee | merchant | date | claims | USD cents | total |
|---|---|---|---|---|---|---|
| L-000213, L-000553, L-000554 | E0013 | Paper & Pine Supply | 2026-07-31 | C-00091, C-00241 | 7033, 7314, 7215 | 21562 |
| L-000222, L-000512 | E0003 | Pixelforge | 2026-07-31 | C-00096, C-00224 | 7479, 7240 | 14719 |
| L-000580, L-002258 | E0088 | Paper & Pine Supply | 2026-08-04 | C-00251, C-00964 | 7318, 7083 | 14401 |
| L-000694, L-001099, L-001100 | E0052 | Riverside Grill | 2026-08-06 | C-00298, C-00466 | 7467, 7142, 7070 | 21679 |
| L-000914, L-001272 | E0062 | Riverside Grill | 2026-08-07 | C-00385, C-00546 | 7403, 7025 | 14428 |
| L-001748, L-003696, L-003697 | E0095 | Pixelforge | 2026-08-17 | C-00764, C-01599 | 7186, 7314, 7078 | 21578 |

### 4. Weekend expenses (30)

L-000022, L-000408, L-000696, L-001008, L-001203, L-001360, L-001542, L-002064, L-002238, L-002252, L-003214, L-003346, L-003438, L-003666, L-003759, L-003944, L-004620, L-004737, L-005254, L-005858, L-006468, L-006829, L-007038, L-007184, L-007419, L-007592, L-007782, L-008157, L-008533, L-008909

### 5. Missing category (8)

| line_id | claim_id | merchant | description | amount_cents |
|---|---|---|---|---|
| L-000092 | C-00037 | Boxmart Marketplace | Screen recorder license | 2184 |
| L-000542 | C-00238 | Swift Cab Co | Taxi to customer site | 5156 |
| L-002881 | C-01233 | Deskworks | Printer paper and toner | 18348 |
| L-004343 | C-01894 | Deskworks | Whiteboard markers | 15097 |
| L-005471 | C-02397 | Skyline Steakhouse | Client dinner | 48300 |
| L-005932 | C-02586 | Rideo | Ride to airport | 4410 |
| L-006886 | C-03002 | Roadrunner Car Rental | Rental car | 11506 |
| L-007780 | C-03394 | Rideo | Ride to customer site | 3536 |

`gl_account_hint` is blank on exactly these 8 lines too.

### 6. Mixed currency without fx

| line_id | claim_id | claim currency | line currency | amount_cents | claim status |
|---|---|---|---|---|---|
| L-008749 | C-03817 | USD | GBP | 921 | submitted |
| L-009143 | C-03986 | USD | CAD | 1840 | submitted |
| L-009164 | C-03996 | USD | EUR | 402 | submitted |

Claims with blank `fx_rate`: C-03817, C-03986, C-03996. Their `total_cents` adds two currencies together.

### 7. Outlier

L-007001, claim C-03048, E0088, Deskworks, Office supplies, 980000 cents on 2026-09-24. The next largest Office supplies line is 23995 cents. IQR per category on USD flags only this line in Office supplies.

### 8. Alcohol (25)

L-000334, L-000400, L-000750, L-000964, L-001506, L-001896, L-001937, L-002831, L-003043, L-004195, L-004294, L-004557, L-004752, L-005189, L-005539, L-006401, L-006640, L-006863, L-006993, L-007180, L-007650, L-007741, L-007791, L-007885, L-008253

Copper Kettle Taproom: L-000750, L-001937, L-005189, L-005539, L-007650, L-008253.

### 9. Over policy limit (10)

| line_id | claim_id | employee | rule | USD cents |
|---|---|---|---|---|
| L-002106 | C-00904 | E0075 | Lodging | 36234 |
| L-004252 | C-01855 | E0089 | Lodging | 40225 |
| L-005412 | C-02365 | E0007 | Meals | 9157 |
| L-005737 | C-02508 | E0029 | Meals | 12939 |
| L-005866 | C-02561 | E0004 | Lodging | 36649 |
| L-006708 | C-02913 | E0102 | Lodging | 34282 |
| L-007001 | C-03048 | E0088 | Office supplies | 980000 |
| L-007409 | C-03224 | E0005 | Meals | 13916 |
| L-007822 | C-03405 | E0031 | Meals | 12293 |
| L-007838 | C-03412 | E0059 | Meals | 12820 |

No Airfare, Ground transport, Software or Training line breaks its limit.

### 10. Missing receipt over $75 (10)

L-000135, L-000355, L-000538, L-001631, L-003713, L-004046, L-005302, L-005692, L-007242, L-008680

### 11. Older than 60 days (4)

| line_id | claim_id | expense_date | category |
|---|---|---|---|
| L-000225 | C-00098 | 2026-05-18 | Ground transport |
| L-003177 | C-01353 | 2026-06-24 | Software |
| L-005700 | C-02491 | 2026-07-13 | Ground transport |
| L-006388 | C-02788 | 2026-07-31 | Software |

### 12. Leakage column

`gl_account_hint` maps 1:1 to `category`: Meals 6100, Lodging 6110, Airfare 6120, Ground transport 6130, Software 6140, Office supplies 6150, Training 6160, Client entertainment 6170, blank when category is blank. A crosstab has exactly one non-zero cell per row and per column.

## Stretch answers

| Question | Answer |
|---|---|
| Claims holding the later line of an exact duplicate | 90 |
| Claims holding the later line of an exact or near-duplicate pair | 132 |
| Self-approved claims | C-01045, C-01201, C-01904, C-02145, C-02468 |
| Approved above approver limit | C-01395, C-02645, C-03040, C-03115, C-03439 |
