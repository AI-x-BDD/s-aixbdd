---
name: course-transcript-notes
description: Turn a course subtitle or transcript into accurate, learner-friendly class notes through a fixed Teach → shuorenhua → no-ai-slop pipeline. Use when the user supplies course captions, an SRT/VTT/transcript, or asks to turn a lesson recording into natural course notes.
---

# Course Transcript Notes

Create one source-faithful Markdown course note, then refine its language in this exact order: `teach`, `shuorenhua`, `no-ai-slop`.

## Resolve the source and delivery

1. Read the complete subtitle or transcript before writing. Accept pasted text and common caption formats such as `.srt`, `.vtt`, and `.txt`.
2. Remove caption sequence numbers, timestamps, and repeated subtitle fragments from the prose input. Retain timestamps only when the user asks for them or they identify an important demo step.
3. Preserve code, commands, file paths, API names, error messages, version numbers, speaker-attributed claims, and stated uncertainty as source facts.
4. Write to the explicitly requested destination. Otherwise, return the note in chat; when the user supplies a source file and asks to save it, use `notes/<source-stem>-notes.md`.

## Phase 1 — Teach: build the class note

Load and apply `teach` first. Use its teaching judgment to organize the material for a learner, but produce a Markdown class note rather than a standalone HTML lesson unless the user explicitly requests a lesson.

Build this shape when the transcript supports it:

```markdown
# [Course or lesson title]

## 這堂課在講什麼

## 學完要會什麼

## 重點整理

### [Concept or step]

## 範例與操作

## 常見誤解／注意事項

## 重點速記
```

Adapt headings to the source. Explain the instructor's reasoning, prerequisites, ordered procedure, and worked examples in learner-facing language. Keep the original teaching order when it aids understanding; merge repetitions and obvious spoken detours. Do not invent definitions, commands, examples, links, prerequisites, or conclusions that are absent from the transcript.

Resolve routine transcript slips before writing the note. When the exercise goal, repeated surrounding explanation, and established technical behavior identify one clear executable interpretation, write that interpretation directly. Do not turn a likely spoken slip into research or verification work for the learner. Mark an ambiguity only when two or more plausible readings remain and choosing between them would materially change the learner's code, result, or next action. Preserve unclear audio and unfinished demonstrations as unresolved when they meet that threshold.

Treat this phase as complete only when every substantive topic, demonstrated action, caveat, and final takeaway in the source is represented or deliberately omitted as repetition.

If the client cannot load `teach` as a nested skill, follow the `teach` learning-oriented workflow directly and state that fallback in the final handoff. Do not skip this phase.

## Phase 2 — shuorenhua: normalize the note's voice

Load and apply `shuorenhua` to the Phase 1 draft. Treat the output as `docs`: favor its conservative, information-preserving mode. Keep Markdown hierarchy, technical terms, code blocks, commands, paths, quotes, and all source-backed relationships protected.

Remove translation-like phrasing, template transitions, inflated summaries, and unnatural shifts between spoken and formal language. Keep a clear teaching voice; do not turn precise notes into casual chat or flatten useful technical distinctions.

## Phase 3 — no-ai-slop: make the final prose human

Load and apply `no-ai-slop` to the Phase 2 draft in edit mode. Make the minimum effective edit. Preserve the instructional structure and the instructor's substance while removing generic openings, filler, performative emphasis, mechanical contrast patterns, repetitive rhythm, and decorative formatting.

Do not add a separate `What changed` section to the course note. Keep any short edit summary for the final handoff only.

## Final fidelity pass

Read the final note against the source and verify all of the following:

- The note distinguishes facts taught in the course from your organizational wording.
- Steps remain executable and in their correct order.
- Code and technical identifiers remain exact.
- No source claim, limitation, uncertainty, or warning became stronger, weaker, or more specific.
- Headings and lists help later review without merely copying the subtitle stream.
- The prose sounds like a capable person explaining the class naturally, without claiming knowledge the transcript did not provide.

Finish only after all three phases have run and this pass finds no unhandled material ambiguity. In the handoff, name the output location or provide the note, state that the three phases completed, and list only material ambiguities that affect what the learner should do.
