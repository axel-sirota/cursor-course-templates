---
description: Execute a rigorous TDD-style research process (Hypothesis -> 5x Search -> Refutation -> Refinement)
---

# Deep Research Command

This command forces a rigorous, scientific approach to problem-solving. It prevents "jumping to conclusions" by enforcing a cycle of hypothesis, evidence gathering, and self-correction.

**CRITICAL: Do not modify any code files during this process. Output findings only.**

## The Process (Repeat 3 Times)

You must iterate through 3 complete cycles. Do not summarize or skip steps.

### Cycle 1: Broad Exploration

**Goal**: Establish the landscape and form a solid initial theory.

1. **Hypothesis**: State your initial understanding of how to solve the problem.
   - *Format*: "I believe the best approach is X because Y..."
2. **Evidence Gathering (Mandatory)**:
   - Perform **minimum 5 distinct web searches**.
   - *Constraint*: Look for official docs, GitHub discussions, and contrasting opinions.
   - If relevant, read local files (but do not edit).
3. **Antithesis (Refutation)**:
   - Critically attack your own hypothesis.
   - Ask: "Why might this fail? What are the edge cases? Is there a simpler way?"
4. **Refinement**: Update your mental model based on the evidence.

### Cycle 2: Deep Dive & Validation

**Goal**: Drill down into the specific mechanisms of the refined hypothesis.

1. **Refined Hypothesis**: State the more specific solution you are investigating.
2. **Evidence Gathering (Mandatory)**:
   - Perform **minimum 5 distinct web searches** targeting specific implementation details, error scenarios, or performance benchmarks.
   - Verify version compatibility (e.g., "Does this work with Python 3.11?").
3. **Antithesis (Refutation)**:
   - Look for "gotchas", security vulnerabilities, or scale limitations.
4. **Refinement**: Polish the solution.

### Cycle 3: Edge Cases & Integration

**Goal**: Stress-test the solution against the project constraints.

1. **Final Hypothesis**: The near-complete solution.
2. **Evidence Gathering (Mandatory)**:
   - Search for integration issues, "X vs Y" comparisons, or "common pitfalls".
   - Check the project's `.cursor/context.md` (if it exists) to ensure alignment with the stack.
3. **Antithesis (Refutation)**:
   - Final sanity check: "Is this over-engineered? Is it maintainable?"
4. **Conclusion**: Finalize the findings.

---

## Final Output: Research Findings

After 3 cycles, present a **Research Artifact** (Markdown block):

1. **Executive Summary**: The recommended approach.
2. **Key Findings**: What was learned? What assumptions were wrong?
3. **Trade-offs**: Pros/Cons of the chosen approach vs alternatives.
4. **Proposed Plan**: High-level steps to implement (but do not implement yet).
5. **Sources**: List of key URLs verified.

## Usage
`@research "What is the best way to handle distributed locking in this stack?"`
