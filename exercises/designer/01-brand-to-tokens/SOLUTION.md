# Solution Key: Exercise 1, Brand to Tokens (instructor only)

## The traps in the brief

Ratios below come from `checks/check_contrast.mjs` (WCAG 2.x relative luminance).

| Trap | Ratio | Why it fails | Passing choice |
|---|---|---|---|
| Marketing wants Harbor Teal (`#0F8B8D`) primary buttons with white text | 4.12:1 | Below 4.5:1 for normal text | teal 700 `#0A6466` fill: 6.94:1. Keeps the brand family. Navy 700 (11.63:1) also passes |
| Harbor Teal as link text on white | 4.12:1 | Below 4.5:1 | teal 700 for `color.text.link` |
| gray 500 `#7B8794` as muted text | 3.66:1 on white, 3.41:1 on gray 100 | Below 4.5:1 | gray 600 `#52606D`: 6.46:1 / 6.02:1 |
| gray 400 `#9AA5B1` as focus ring or control border | 2.50:1 on white | Below 3:1 non-text | Ring: teal 500 (4.12:1 on white, 3.84:1 on gray 100). Border: gray 500 (3.66:1) |
| 500 shades as badge text on their 100 tints | green 3.01, blue 3.55, red 3.73, teal 3.58, amber 2.07 | Mid shades fail on the 100 tints | Use the 700 (or amber 800) shade on the 100 tint |
| Muted text checked only on white | 6.46 vs 6.02 | Students forget the page is gray 100, not white | `pairs.json` checks both surfaces |
| Brand teal "fails", so drop it | n/a | Over-correction | Teal still works as the focus ring (3:1 rule) and as the Paid badge family |

## Expected decisions in the transition doc

1. Primary button fill is teal 700, not Harbor Teal, because white on teal 500 is 4.12:1. Hover goes to navy 700 (11.63:1).
2. Link text is teal 700 for the same reason.
3. Muted text is gray 600. Gray 500 is reserved for control borders (3:1 rule), gray 400 is decorative only.
4. Focus ring is Harbor Teal 500. It is non-text, so 3:1 applies, and it passes on both surfaces.
5. Status badges pair each family's 700 shade (amber 800) with its 100 tint.

## Reference run

```
$ node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs --tokens <reference tokens.json>
...
5  | color.text.inverse (#ffffff)   | color.action.primary.bg (#0a6466) | 6.94:1 | 4.5:1 | PASS | primary button label
...
17 | color.focus.ring (#0f8b8d)     | color.surface.card (#ffffff)      | 4.12:1 | 3:1   | PASS | focus ring on cards and rows
18 | color.focus.ring (#0f8b8d)     | color.surface.page (#f5f7fa)      | 3.84:1 | 3:1   | PASS | focus ring on app background

[contrast] OK: 18 pair(s) meet WCAG AA

$ node scripts/build-tokens.mjs --check
[tokens] OK: 52 primitive, 56 semantic
```

A typical first attempt (Harbor Teal button, gray 500 muted text, green 500 approved text, gray 400 ring, no flag tokens) exits 1 with 8 problems:

```
[contrast] 8 problem(s):
  - #3 color.text.muted on color.surface.page: 3.41:1 is below 4.5:1
  - #4 color.text.muted on color.surface.card: 3.66:1 is below 4.5:1
  - #5 color.text.inverse on color.action.primary.bg: 4.12:1 is below 4.5:1
  - #12 color.status.approved.text on color.status.approved.bg: 3.01:1 is below 4.5:1
  - #15 color.flag.text: token not found
  - #15 color.flag.bg: token not found
  - #17 color.focus.ring on color.surface.card: 2.50:1 is below 3:1
  - #18 color.focus.ring on color.surface.page: 2.33:1 is below 3:1
```

## Grading notes

| Look for | Pass | Fail |
|---|---|---|
| Primitive values | Every hex is in the brief | Invented hex such as `#0B7A7C` "a bit darker teal" |
| Semantic values | All `{primitive...}` references | Raw hex in `semantic` (build-tokens `--check` catches this) |
| Names | Intent: `color.text.muted`, `space.inset.md` | Appearance: `color.teal`, `space.16` |
| Gaming the check | `pairs.json` untouched | Pairs deleted or `min` lowered |
| Decisions | Each override written down with a ratio | Silent changes |

Common question: "Can the semantic layer reference another semantic token?" Not in this stack. `build-tokens.mjs` requires a single reference to a primitive. `check_contrast.mjs` would follow a chain, but the build check rejects it.

## Reference tokens.json

One passing answer. Others are valid (navy primary button, for example).

```json
{
  "primitive": {
    "color": {
      "white": { "$value": "#ffffff", "$type": "color" },
      "navy": {
        "100": { "$value": "#e3ecf5", "$type": "color" },
        "500": { "$value": "#2f5f8f", "$type": "color" },
        "700": { "$value": "#1b3a5c", "$type": "color" },
        "900": { "$value": "#0e2236", "$type": "color" }
      },
      "teal": {
        "100": { "$value": "#dff3f3", "$type": "color" },
        "300": { "$value": "#5cc5c7", "$type": "color" },
        "500": { "$value": "#0f8b8d", "$type": "color" },
        "700": { "$value": "#0a6466", "$type": "color" }
      },
      "gray": {
        "100": { "$value": "#f5f7fa", "$type": "color" },
        "200": { "$value": "#e4e7eb", "$type": "color" },
        "400": { "$value": "#9aa5b1", "$type": "color" },
        "500": { "$value": "#7b8794", "$type": "color" },
        "600": { "$value": "#52606d", "$type": "color" },
        "700": { "$value": "#3e4c59", "$type": "color" },
        "900": { "$value": "#1f2933", "$type": "color" }
      },
      "blue": {
        "100": { "$value": "#e6efff", "$type": "color" },
        "500": { "$value": "#3d7be0", "$type": "color" },
        "700": { "$value": "#1f4fa3", "$type": "color" }
      },
      "green": {
        "100": { "$value": "#e3f5ea", "$type": "color" },
        "500": { "$value": "#2f9e58", "$type": "color" },
        "700": { "$value": "#1e6b3a", "$type": "color" }
      },
      "red": {
        "100": { "$value": "#fde8e8", "$type": "color" },
        "500": { "$value": "#d64545", "$type": "color" },
        "700": { "$value": "#a61b1b", "$type": "color" }
      },
      "amber": {
        "100": { "$value": "#fff4d6", "$type": "color" },
        "500": { "$value": "#e0a100", "$type": "color" },
        "800": { "$value": "#7a4b00", "$type": "color" }
      }
    },
    "space": {
      "1": { "$value": "4px", "$type": "dimension" },
      "2": { "$value": "8px", "$type": "dimension" },
      "3": { "$value": "12px", "$type": "dimension" },
      "4": { "$value": "16px", "$type": "dimension" },
      "6": { "$value": "24px", "$type": "dimension" },
      "8": { "$value": "32px", "$type": "dimension" },
      "12": { "$value": "48px", "$type": "dimension" }
    },
    "border": {
      "1": { "$value": "1px", "$type": "dimension" },
      "2": { "$value": "2px", "$type": "dimension" }
    },
    "radius": {
      "1": { "$value": "4px", "$type": "dimension" },
      "2": { "$value": "8px", "$type": "dimension" },
      "full": { "$value": "9999px", "$type": "dimension" }
    },
    "font": {
      "family": {
        "sans": { "$value": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif", "$type": "fontFamily" }
      },
      "size": {
        "100": { "$value": "12px", "$type": "dimension" },
        "200": { "$value": "14px", "$type": "dimension" },
        "300": { "$value": "16px", "$type": "dimension" },
        "400": { "$value": "20px", "$type": "dimension" },
        "500": { "$value": "24px", "$type": "dimension" },
        "600": { "$value": "32px", "$type": "dimension" }
      },
      "weight": {
        "400": { "$value": 400, "$type": "fontWeight" },
        "600": { "$value": 600, "$type": "fontWeight" },
        "700": { "$value": 700, "$type": "fontWeight" }
      },
      "lineHeight": {
        "tight": { "$value": 1.25, "$type": "number" },
        "normal": { "$value": 1.5, "$type": "number" }
      }
    }
  },
  "semantic": {
    "color": {
      "surface": {
        "page": { "$value": "{primitive.color.gray.100}", "$type": "color" },
        "card": { "$value": "{primitive.color.white}", "$type": "color" }
      },
      "text": {
        "default": { "$value": "{primitive.color.gray.900}", "$type": "color" },
        "muted": { "$value": "{primitive.color.gray.600}", "$type": "color" },
        "inverse": { "$value": "{primitive.color.white}", "$type": "color" },
        "link": { "$value": "{primitive.color.teal.700}", "$type": "color" },
        "danger": { "$value": "{primitive.color.red.700}", "$type": "color" },
        "success": { "$value": "{primitive.color.green.700}", "$type": "color" }
      },
      "action": {
        "primary": {
          "bg": { "$value": "{primitive.color.teal.700}", "$type": "color" },
          "bgHover": { "$value": "{primitive.color.navy.700}", "$type": "color" }
        }
      },
      "status": {
        "draft": {
          "text": { "$value": "{primitive.color.gray.700}", "$type": "color" },
          "bg": { "$value": "{primitive.color.gray.100}", "$type": "color" }
        },
        "submitted": {
          "text": { "$value": "{primitive.color.blue.700}", "$type": "color" },
          "bg": { "$value": "{primitive.color.blue.100}", "$type": "color" }
        },
        "approved": {
          "text": { "$value": "{primitive.color.green.700}", "$type": "color" },
          "bg": { "$value": "{primitive.color.green.100}", "$type": "color" }
        },
        "rejected": {
          "text": { "$value": "{primitive.color.red.700}", "$type": "color" },
          "bg": { "$value": "{primitive.color.red.100}", "$type": "color" }
        },
        "paid": {
          "text": { "$value": "{primitive.color.teal.700}", "$type": "color" },
          "bg": { "$value": "{primitive.color.teal.100}", "$type": "color" }
        }
      },
      "flag": {
        "text": { "$value": "{primitive.color.amber.800}", "$type": "color" },
        "bg": { "$value": "{primitive.color.amber.100}", "$type": "color" }
      },
      "border": {
        "subtle": { "$value": "{primitive.color.gray.200}", "$type": "color" },
        "control": { "$value": "{primitive.color.gray.500}", "$type": "color" }
      },
      "focus": {
        "ring": { "$value": "{primitive.color.teal.500}", "$type": "color" }
      }
    },
    "space": {
      "inset": {
        "xs": { "$value": "{primitive.space.1}", "$type": "dimension" },
        "sm": { "$value": "{primitive.space.2}", "$type": "dimension" },
        "md": { "$value": "{primitive.space.4}", "$type": "dimension" },
        "lg": { "$value": "{primitive.space.6}", "$type": "dimension" }
      },
      "stack": {
        "xs": { "$value": "{primitive.space.1}", "$type": "dimension" },
        "sm": { "$value": "{primitive.space.2}", "$type": "dimension" },
        "md": { "$value": "{primitive.space.3}", "$type": "dimension" },
        "lg": { "$value": "{primitive.space.6}", "$type": "dimension" },
        "xl": { "$value": "{primitive.space.8}", "$type": "dimension" },
        "xxl": { "$value": "{primitive.space.12}", "$type": "dimension" }
      },
      "inline": {
        "xs": { "$value": "{primitive.space.1}", "$type": "dimension" },
        "sm": { "$value": "{primitive.space.2}", "$type": "dimension" },
        "md": { "$value": "{primitive.space.4}", "$type": "dimension" }
      }
    },
    "border": {
      "width": {
        "default": { "$value": "{primitive.border.1}", "$type": "dimension" },
        "focus": { "$value": "{primitive.border.2}", "$type": "dimension" }
      }
    },
    "radius": {
      "control": { "$value": "{primitive.radius.1}", "$type": "dimension" },
      "card": { "$value": "{primitive.radius.2}", "$type": "dimension" },
      "badge": { "$value": "{primitive.radius.full}", "$type": "dimension" }
    },
    "font": {
      "family": {
        "base": { "$value": "{primitive.font.family.sans}", "$type": "fontFamily" }
      },
      "size": {
        "caption": { "$value": "{primitive.font.size.100}", "$type": "dimension" },
        "label": { "$value": "{primitive.font.size.200}", "$type": "dimension" },
        "body": { "$value": "{primitive.font.size.300}", "$type": "dimension" },
        "title": { "$value": "{primitive.font.size.400}", "$type": "dimension" },
        "heading": { "$value": "{primitive.font.size.500}", "$type": "dimension" },
        "amount": { "$value": "{primitive.font.size.500}", "$type": "dimension" },
        "page": { "$value": "{primitive.font.size.600}", "$type": "dimension" }
      },
      "weight": {
        "regular": { "$value": "{primitive.font.weight.400}", "$type": "fontWeight" },
        "semibold": { "$value": "{primitive.font.weight.600}", "$type": "fontWeight" },
        "bold": { "$value": "{primitive.font.weight.700}", "$type": "fontWeight" }
      },
      "lineHeight": {
        "tight": { "$value": "{primitive.font.lineHeight.tight}", "$type": "number" },
        "normal": { "$value": "{primitive.font.lineHeight.normal}", "$type": "number" }
      }
    }
  }
}
```
