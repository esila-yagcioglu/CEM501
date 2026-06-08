# REFLECTION.md

**CEM501 Communication Skills for CEM — Spring 2026**
Hilal Esila Yağcıoğlu | 2025722042

---

## What I Built

I built an AI-powered email communication agent for construction project managers. The agent connects to a dedicated Gmail folder, reads incoming emails, classifies them as URGENT, ACTION, FYI, or ARCHIVE, and generates professional draft replies using Claude AI. Approved drafts can be sent directly from a web dashboard or via Telegram with no terminal interaction needed. The system also sends Telegram alerts for urgent emails, allowing approval on mobile without being at a desk. The system addresses a real problem that we observed in CEM practice: project engineers spend hours each day managing email across subcontractors, clients, and consultants. This agent reduces that to minutes.

---

## Communication Lessons

Developing an automated communication tool made me clarify the guidelines I had always followed without realizing it. Before I had to define "urgent" as a list of terms, I had never considered what constitutes an urgent email. I came to see that professional tone involves more than simply word choice; it also involves time, structure, and the implied connection between the sender and the recipient. I realized that context influences communication just as much as content when my agent sent a response to a stop-work order in the same tone as a weekly report. Additionally, I discovered that closing statements, greeting customs, and CC choices all had significance that I had previously overlooked.

---

## AI-Assisted Development Lessons

Working with Claude changed the way I think about giving instructions. At first, I thought Claude had a greater capacity for understanding, especially compared to other AIs. But over time, I realized that the most important thing is to explain everything in detail and tell it exactly what you want it to do; otherwise, you can't get the desired result. For example, when I asked Claude to write the IMAP reader without specifying the folder name or fetch limit, it made assumptions that did not match my setup and I had to debug the output carefully. Another crucial point was to always monitor its actions — Claude could produce confident-sounding code that had subtle logic errors I only caught during testing.

---

## What I'd Do Differently

I would design the database schema before writing any other code. I added memory.py halfway through the project and had to refactor several modules to log messages correctly. I would also start with the classifier earlier and test it against real emails before building the drafter — I lost time generating drafts for emails that were misclassified. Finally, I underestimated how long SMTP and IMAP configuration would take; I would allocate a full session to email infrastructure at the start.

---

## Connection to Professional Practice

My approach to reading professional emails was altered by this project. Like the classifier, I now automatically recognize category, tone, and structure. I have been a more cautious communicator since realizing that email is a tool for managing relationships, recording decisions, and safeguarding legal interests in addition to being a means of transmitting information. In a real project with 30+ subcontractors, this kind of systematic triage could prevent missed deadlines and miscommunication that lead to disputes. The practice of approaching communication methodically will lead to productivity even if the agent itself does not go into production.

---

