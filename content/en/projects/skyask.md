---
title: SkyAsk
description: A civil-aviation theory exam practice platform — a React + Vite + TypeScript front end and a Node / Express / SQLite back end, with "Cloud", a Socratic AI study assistant. The web app is the product today (mobile ships as a phone-shell layout you can preview right in the browser); a native Flutter app is planned to follow once the web build is signed off.
date: 2026-07-31
tags: [Projects, web, app]
thumbnail: /images/projects/skyask-hero.jpg
tech: [React 18, TypeScript, Vite, Tailwind CSS, Radix UI, Node.js, Express, SQLite, Flutter]
type: web
---

# SkyAsk

## What it is

A practice and exam platform for civil-aviation theory tests, covering question banks for the PPL, CPL and instrument rating. It is not just "pick an answer, next question" — practice, mistake review, mock exams, community and Q&A are wired into one continuous study loop. Living inside it is a study assistant called **Cloud**, an AI partner that guides instead of handing over answers.

Along the way you grow a cloud of your own: you start out as a **Little Cloud**, level up through **Cumulus** and **Cirrus**, and finally reach **Rainbow Cloud**. Every question you answer and every contribution you make to the community takes shape as its growth.

## Key features

- **Practice**: single-choice, multiple-choice, true/false and fill-in questions; option rows can be shuffled and answers are graded per question type (multiple-choice ignores order, fill-in ignores case and whitespace)
- **Mistake book & favourites**: wrong answers are collected automatically and favourite state syncs per user in real time
- **Filtering & search**: filter by question type and difficulty, plus keyword search across questions
- **Mock exams**: a 30-minute countdown that turns red in the final five minutes and auto-submits on timeout
- **Study stats & growth**: questions answered today, streak, a 7-day accuracy trend and a "weak knowledge points" view; four cloud stages unlock as you progress (Little Cloud → Cumulus → Cirrus → Rainbow Cloud)
- **AI Q&A**: ask about a specific question or start a general conversation; chat history is restored on return; Cloud guides rather than handing over the answer
- **Community**: a feed with posts, likes and comments, split into Recommended / Help / Notes / Experience; posting and earning likes both add growth points — turning one person's exam prep into a group effort

## Stack

| Layer | Choice |
|---|---|
| Front end | React 18 + Vite + TypeScript (strict) + Tailwind CSS + Radix UI |
| Forms & validation | react-hook-form + Zod |
| Back end | Node.js + Express + SQLite (proxied at `/api` by Vite) |
| Mobile | Flutter, sharing the same question bank and grading rules — port planned |
| Tooling | ESLint + Prettier, with `pnpm check` (type-check + lint) as the single quality gate |

## Development notes

**"One authoritative grading rule" was the real lesson.** The same question gets graded on both the front end and the back end. If the normalisation rule drifts in even one place, you get bugs like "correct on the page, wrong from the API" — the kind that are almost impossible to reproduce. In the end I collapsed grading into one identical rule, and made "change grading = change both sides" a hard rule.

**Hunting down silent failures.** Early on, a lot of `catch` blocks were empty: a dead endpoint or a failed token refresh produced nothing at all on screen, and users just felt like "nothing happened when I tapped". Adding toast feedback, session-expiry notices and a route-level ErrorBoundary turned invisible errors into visible ones. None of that added features, but it changed the experience enormously.

**An AI assistant shouldn't answer the question for the student.** Cloud's context used to include the correct answer, so its replies simply restated it. Rewriting the prompt into a Socratic one — hint at the approach, ask about the key condition — is what finally made it a study partner rather than an answer machine. That trade-off was more interesting than wiring up the model itself.

**Every rough edge started as something that felt awkward.** A hover menu that never opened on touch, a subject name lost on refresh, stats that lagged five minutes, a native dialog that interrupted the exam flow — that chain of small issues is exactly the distance between "it runs" and "it's pleasant to use".

## TODO

- Importing questions is still a manual process; I want a smoother authoring / bulk-import flow
- The mistake book covers "weak knowledge points" now, but a batch review view grouped by knowledge point is still being refined
- I'd like Cloud to go beyond text and explain diagrams too
- The web app currently ships as a phone-shell layout; a desktop layout of its own is still to come
- The native Flutter app will follow once the web build is signed off

## Join the project

SkyAsk is an open-source study project that is still moving fast, and we want to make it the practice-and-Q&A tool civil-aviation candidates actually reach for. If that sounds interesting, come join us.

### What we're building

- Wiring practice, mistake review, mock exams, community and AI Q&A into one continuous study loop
- Polishing Cloud — a Socratic study partner that guides you instead of doing the questions for you
- Growing and calibrating the question banks for the PPL, CPL and instrument rating

### Where we need help

- Front end (React / Vite / TypeScript / Tailwind): web features and the desktop layout
- Mobile (Flutter): porting and maintaining the app
- Back end (Node / Express / SQLite): community, points and AI integration
- AI / algorithms: improving Cloud's guidance strategy, a purpose-built Q&A agent, diagram explanations
- Question bank / content: sourcing, checking and entering civil-aviation theory questions
- Design / product: Cloud's character and the interaction experience around it

### What we're looking for

- An interest in civil-aviation theory exams or educational tools (exam experience is a plus, not a requirement)
- One stack you can work in — or the willingness to learn as you go
- Steady availability and a taste for small, fast iterations

### How to join

- Contact: PmrALQ@Outlook.com
