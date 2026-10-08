---
name: transcript-deep-learning
description: Analyze a programming-course transcript into a concept-first learning guide with mental models, engineering trade-offs, practice, and answer-gated feedback. Use when a user provides or references a programming lecture transcript and wants to deeply understand it, study it, make learning notes, test their understanding, or practice retrieval rather than receive a chronological summary.
---

# Transcript deep learning

Turn a programming-course transcript into a concept-first learning session. Optimize for transferable understanding and the learner's ability to predict, debug, and apply code.

## Evidence boundary

Treat the transcript as the source of truth.

- Make factual claims about the lesson only when the transcript supports them.
- Do not silently fill gaps with assumed APIs, versions, project conventions, or instructor intent.
- Label useful material that goes beyond the transcript as **延伸知識** and keep it separate from lesson claims.
- If the transcript is incomplete, ambiguous, or contains a likely error, say so plainly and explain the limit of the conclusion.
- Do not produce a chronological recap or an API/syntax inventory unless that is necessary to explain an important concept.

## Workflow

1. Read the entire transcript. Identify its central problem, the concepts needed to solve it, concrete examples, competing approaches, and any stated limitations.
2. Choose only 3–7 concepts. Merge overlapping ideas; omit incidental setup and repeated explanation.
3. Separate language-specific mechanics from portable engineering ideas. Tie every trade-off and expert-review point to material actually covered.
4. Produce the learning guide below in Traditional Chinese unless the learner requests another language.
5. End after asking the code-prediction, bug-hunt, and retrieval questions. Do not reveal their solutions in the first response.
6. When the learner replies with answers, assess each requested answer as **已理解**, **部分理解**, **錯誤理解**, or **尚未理解**. Explain only the gaps, then give the withheld solutions and a small corrective example when helpful.

## Required learning guide

Use these sections in this order. Adapt the depth to the transcript; explicitly state "逐字稿未涵蓋" for an inapplicable section instead of inventing content.

### 1. 這堂課真正要解決的問題

State the core problem, why it matters, and the concrete failure or cost that appears without the concept. Organize by causal logic, not lecture order.

### 2. 核心概念

For each of 3–7 concepts, explain:

- 它是什麼
- 為什麼存在
- 解決什麼問題
- 何時使用
- 何時不適合使用

Discuss concepts, not a flat list of syntax or APIs.

### 3. Mental Model

Explain the model as execution flow, cause and effect, data flow, state changes, references, or object relationships—whichever the transcript supports. Use a compact ASCII flow only when it makes a multi-step relationship clearer.

### 4. 專家視角

Split this into:

- **初學者需要知道，但資深工程師通常不會特別思考的內容**
- **即使是資深工程師仍然會注意的內容**

For each applicable item, explain why it matters. Discuss correctness, design, maintainability, performance, error handling, data modeling, security, or concurrency only when relevant to the lesson.

### 5. 語法 vs 通用知識

Classify the covered material into:

- **語言特有知識**
- **通用程式設計知識**

Name the transferable idea and explain how it carries to other languages.

### 6. Trade-off

For each real alternative in the transcript, compare A vs B: differences, benefits, costs, suitable contexts, and likely consequences of choosing poorly. Omit this section's details when no meaningful alternative was taught.

### 7. 常見誤解

List 3–5 high-impact misunderstandings. Favor misunderstandings that distort runtime behavior, design, data integrity, or debugging—not mere typos.

### 8. Code Prediction — 請先作答

Create three short programs grounded in the lesson. For each, ask the learner to predict:

1. 執行結果
2. 為什麼
3. 程式內部發生什麼事

Do not show answers, hints that give away the outcome, or output comments.

### 9. Bug Hunt — 請先作答

Create two short, plausible flawed snippets grounded in the lesson. Ask the learner to identify the issue, explain its cause, and propose a fix. Do not reveal the flaw or solution.

### 10. Coding Challenge

Design one 10–30 minute challenge in a slightly different context from the instructor's example. Include goal, constraints, completion criteria, and optional stretch goal. Do not provide a solution unless asked after the learner attempts it.

### 11. Retrieval Practice — 請先作答

Ask five answer-free questions covering, respectively: **Why**, **How**, **Trade-off**, **Prediction**, and **Application**. Avoid questions that merely request API syntax.

### 12. 下一步

List 3–5 capabilities the learner should now possess, then at most three next concepts worth learning. For each next concept, state its direct connection to this lesson. Avoid generic advice.

## Follow-up assessment

When assessing the learner's reply, preserve the question numbering and use this structure:

| 題目 | 判斷 | 回饋 |
| --- | --- | --- |
| ... | 已理解／部分理解／錯誤理解／尚未理解 | Concise, evidence-based feedback |

Teach only the weak areas. Then reveal the solutions to the questions the learner attempted, including the internal execution reasoning for prediction questions and a corrected version for bug hunts.
