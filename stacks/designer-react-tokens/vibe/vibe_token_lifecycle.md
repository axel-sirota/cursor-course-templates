# Vibe: Token Lifecycle

A token goes through five steps. Skipping a step is how hardcoded values creep in.

```
Need → Name → Add → Build → Use → (Retire)
```

## 1. Need
A screen spec or component spec asks for a value. Example: the over-budget state needs a warning color for the status text.

Check the semantic layer first. If `color.status.danger` exists, use it and stop here.

## 2. Name
No match? Name the job, not the look.

| Good | Bad |
|---|---|
| `color.status.warning` | `color.orange` |
| `space.stack.lg` | `space.24` |
| `font.size.caption` | `font.size.small2` |

Ask the user before adding a new semantic name. Write the proposal in the session notes.

## 3. Add
Add the semantic leaf in `tokens/tokens.json`, pointing at an existing primitive:

```json
"warning": { "$value": "{primitive.color.amber.600}", "$type": "color" }
```

Add a primitive only when the palette really lacks the value. A new primitive is a brand decision, so flag it in the transition doc.

## 4. Build
```bash
npm run check:tokens   # valid shape, every reference resolves
npm run build:tokens   # regenerate src/styles/tokens.css
```
The check fails if a semantic token holds a raw value or points at a path that does not exist.

## 5. Use
```css
.budget-card[data-status='near-limit'] .budget-card__status { color: var(--color-status-warning); }
```
Then run `npm test`. The style guard test fails if the CSS used `--primitive-color-amber-600` directly.

## Retire
1. Search components for the CSS variable. Replace every use.
2. Remove the token from `tokens.json`.
3. Run check, build and test.
4. Note the removal in the transition doc.

## Lifecycle per session
| Session step | Token work |
|---|---|
| `/start-session` | read `tokens/tokens.json` and open questions |
| During work | add tokens only through steps 1 to 4 |
| `/next-session` | list token changes and any `MISSING` entries from screen specs |
