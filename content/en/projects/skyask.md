---
title: SkyAsk
description: A civil-aviation theory exam practice platform — a React front end, a Node/SQLite back end and a Flutter app sharing one question bank, with "Cloud", a Socratic AI study assistant.
date: 2026-07-31
tags: [Projects, web, app]
thumbnail: /images/projects/skyask-hero.jpg
tech: [React 18, TypeScript, Vite, Tailwind CSS, Radix UI, Node.js, Express, SQLite, Flutter]
type: web
---

# SkyAsk

## What it is

A practice and exam platform for civil-aviation theory tests, covering question banks for the PPL, CPL and instrument rating. It is not just "pick an answer, next question" — practice, mistake review, mock exams and Q&A are wired into one continuous study loop. Living inside it is a study assistant called **Cloud**, an AI partner that guides instead of handing over answers.

## Key features

- **Practice**: single-choice, multiple-choice, true/false and fill-in questions; option rows can be shuffled and answers are graded per question type (multiple-choice ignores order, fill-in ignores case and whitespace)
- **Mistake book & favourites**: wrong answers are collected automatically and favourite state syncs per user in real time
- **Filtering & search**: filter by question type and difficulty, plus keyword search across questions
- **Mock exams**: a 30-minute countdown that turns red in the final five minutes and auto-submits on timeout
- **Study stats**: questions answered today, streak, and a 7-day accuracy trend
- **AI Q&A**: ask about a specific question or start a general conversation; chat history is restored on return

## Stack

| Layer | Choice |
|---|---|
| Front end | React 18 + Vite + TypeScript (strict) + Tailwind CSS + Radix UI |
| Forms & validation | react-hook-form + Zod |
| Back end | Node.js + Express + SQLite (proxied at `/api` by Vite) |
| Mobile | Flutter, sharing the same question bank and grading rules |
| Tooling | ESLint + Biome, with `pnpm check` (type-check + lint) as the single quality gate |

## Development notes

**Keeping three clients consistent was the real lesson.** The same question is graded by the web app, the Flutter app *and* the server. If the normalisation rule drifts in even one place, you get bugs like "correct on the web, wrong on the phone" — the kind that are almost impossible to reproduce. In the end I wrote the grading logic as one identical rule across all three, and made "change grading = change all three" a hard rule.

**Hunting down silent failures.** Early on, a lot of `catch` blocks were empty: a dead endpoint or a failed token refresh produced nothing at all on screen, and users just felt like "nothing happened when I tapped". Adding toast feedback, session-expiry notices and a route-level ErrorBoundary turned invisible errors into visible ones. None of that added features, but it changed the experience enormously.

**An AI assistant shouldn't answer the question for the student.** Cloud's context used to include the correct answer, so its replies simply restated it. Rewriting the prompt into a Socratic one — hint at the approach, ask about the key condition — is what finally made it a study partner rather than an answer machine. That trade-off was more interesting than wiring up the model itself.

**Every rough edge started as something that felt awkward.** A hover menu that never opened on touch, a subject name lost on refresh, stats that lagged five minutes, a native dialog that interrupted the exam flow — that chain of small issues is exactly the distance between "it runs" and "it's pleasant to use".

## TODO

- Importing questions is still a manual process; I want a smoother authoring flow
- Mistake review still lacks a "grouped by knowledge point" view
- I'd like Cloud to go beyond text and explain diagrams too
