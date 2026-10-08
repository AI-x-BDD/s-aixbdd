---
name: review-article-stepwise
description: Review and edit an article or prose document unit by unit against local and document-wide context, completing the whole document automatically by default. Use for paragraph-by-paragraph review, 逐段檢查, 全文自動審稿, title-by-title editing, contextual line editing, or an explicitly approval-gated writing pass paired with a style skill such as shuorenhua.
---

# Review an Article Stepwise

Review every unit in sequence and finish the whole document in one run. Apply useful revisions directly by default; use approval-gated mode only when the user explicitly asks to confirm each change.

## Pair with the style skill

Load and follow the available skill named `shuorenhua` before making style judgments. Let that skill own tone, protected spans, rewrite severity, and fidelity checks. Let this skill own unit boundaries, context selection, sequencing, file edits, and completion.

If `shuorenhua` is unavailable, state that limitation and continue with a general clarity review unless style fidelity is essential to the request.

## Choose the mode

- **Automatic mode (default):** review every unit, apply warranted edits, run the final consistency pass, and report once after the document is complete.
- **Approval-gated mode:** use only when the user asks for逐項確認, 一段一段等確認, approval before edits, or an equivalent interaction. Present one unit and wait after each decision.
- **Read-only mode:** use when the user asks for comments, diagnosis, or suggestions without changing the file. Review the whole document and report the findings without editing.

A bare skill invocation, a file path, `proceed`, `continue`, `自動審完`, or `一路審完` selects automatic mode. Continue to completion without requesting routine confirmation.

## Establish the review

1. Resolve the target document. If the user names one file, use it without asking again.
2. Read the whole document once to establish its purpose, audience, structure, terminology, and existing voice.
3. Build an ordered internal queue of reviewable units. Keep the queue internal unless the user asks to see it.
4. Process the queue from the first unit, or from the user's stated starting point, until every unit has a recorded keep-or-revise decision.

Treat these as separate reviewable units:

- each document title and heading at every level;
- each prose or blockquote paragraph;
- each list item;
- a table header and each table row.

Treat fenced code, commands, paths, parameters, error text, and other protected spans according to `shuorenhua`. Skip code-only units unless the user asks to review code comments or technical correctness.

## Review each unit

For every current unit:

1. Refresh it from the current file.
2. Read its enclosing heading, section purpose, neighboring units, prior edits that affect it, and document-wide terminology.
3. For a heading, compare its covered content and sibling headings.
4. Keep natural wording as-is. Revise only when the change materially improves clarity, accuracy of expression, flow, consistency, or naturalness.
5. Preserve meaning and responsibility. Add no unsupported facts, examples, claims, sources, capabilities, or conclusions.
6. In automatic mode, apply the revision directly and advance. In read-only mode, record the recommendation and advance.

Use the updated file as the source of truth after every edit. Revisit an earlier unit only when a later edit creates a direct inconsistency.

## Approval-gated mode

Present exactly one unit in this compact shape:

```text
Location: [line or heading path]
Type: [title / heading / paragraph / list item / table]
Decision: [keep / revise]

Original:
> [current unit]
```

For `revise`, append one recommendation and a concrete reason. Then wait for the user's accept, keep, replacement, retry, explanation, stop, or switch-to-automatic instruction. When the user says `proceed`, `continue automatically`, `一路審完`, or an equivalent phrase, switch to automatic mode and finish the remaining queue in the same run.

## Finish the document

After the queue is exhausted, reread the complete current document and check:

- heading hierarchy and naming patterns;
- terminology and responsibility;
- transitions affected by edits;
- conspicuous repetition, fragments, or formulaic endings;
- Markdown structure and protected technical spans.

In automatic mode, apply any consistency fixes that satisfy the same fidelity rules. Finish only when every queued unit has a decision, all selected edits are present in the file, and the final consistency pass finds no unresolved in-scope issue.

Report once with a concise summary of the material changes, notable passages intentionally kept, validation performed, and any issue that requires information or authority outside the document. Do not print a unit-by-unit transcript unless the user requests it.
