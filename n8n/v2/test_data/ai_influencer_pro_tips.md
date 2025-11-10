# Example Scenario / Use Case
I want the pro tips that ai influencers drop every day and their insights into the tools, community and trends

## Test Prompt from Frontend
```
Extract 'Pro Tips' from video transcripts / subtitles. Pro tips can be any insightful or actionable tips around how to use / configure /take advantage of specific tools or technology, how to build profitable companies and products / services, approaches to learning etc. 

For each pro tip i want a field for the protip itself in a short 1-5 sentences max. 
I want the domain which is the broad set of topics, e.g. software development, business, education etc.
I want the topic that the pro tip covers e.g. vibe coding, saas business startup, product launch, backend automation etc. etc.
I want the specific tools or product that the pro tip metions e.g. claude code, python, typescript, chatgpt etc. if there no is technology mentioned then don't make one up. 
I want the level of the pro tip e.g. beginner, intermediate, advanced. if the source doesn't mention any level then put none
I want the tone e.g. Practical / Analytical / Inspirational / Critical
I want the evidence type e.g. Anecdotal / Empirical / Theoretical / Observed
I want the category of pro tip, the pro tip categories are below:
| #     | Category                                   | Definition                                                          | Typical Verbs / Indicators                                       |
| ----- | ------------------------------------------ | ------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **1** | **Actionable / Procedural**                | Direct steps, tactics, or methods to achieve an outcome.            | “Do this”, “Start by”, “Use”, “Apply”, “Implement”               |
| **2** | **Strategic / Analytical Insight**         | Reasoning or principles guiding direction, design, or priorities.   | “Focus on”, “The key is”, “You should consider”, “Because”       |
| **3** | **Conceptual Framework / Heuristic**       | Abstract models or rules that organize thinking or approach.        | “Think of X as”, “Use this framework”, “Follow this principle”   |
| **4** | **Cautionary / Anti-Pattern**              | Warnings, misconceptions, or mistakes to avoid.                     | “Don’t”, “Avoid”, “Never”, “Be careful”                          |
| **5** | **Technical / Implementation Detail**      | Specifics on code, configuration, or architecture.                  | “Use”, “Set”, “Configure”, “Optimize”, “Parameter”               |
| **6** | **Empirical / Evidence-Based Observation** | Results, benchmarks, or measured effects from experiments or cases. | “We found”, “It increased”, “Our data shows”                     |
| **7** | **Mindset / Meta-Skill**                   | Reflections on habits, creativity, learning, or leadership.         | “Adopt”, “Believe”, “Treat”, “Embrace”                           |
| **8** | **Workflow / Productivity Optimization**   | Guidance on process efficiency, time, tools, or collaboration.      | “Batch”, “Automate”, “Streamline”, “Systematize”                 |
| **9** | **Cultural / Ecosystem Commentary**        | Observations about trends, communities, or industry evolution.      | “The trend is”, “People underestimate”, “The market is shifting” |


I want also the sub cateogry of protips examples below:
1. Actionable / Procedural

How-To Step – explicit method (“Fine-tune on 10k samples first”).

Best Practice – standard routine (“Always version control your data”).

Optimization Tip – tuning guidance (“Cache embeddings locally”).

Shortcut / Hack – efficiency trick (“Use cmd+shift+p to re-index prompts”).

Template / Pattern – reusable structure (“Use ABC pattern for onboarding”).

2. Strategic / Analytical Insight

Decision Heuristic – choosing trade-offs (“Prioritize speed over accuracy early”).

Market or Competitive Insight – positioning or moat awareness.

Analytical Model – conceptual explanation (“Retention > acquisition”).

Leverage Principle – how to compound advantage (“Automate what compounds”).

Systemic Observation – macro reasoning (“Innovation cycles compress annually”).

3. Conceptual Framework / Heuristic

Mental Model – analogy or schema (“Data pipelines are assembly lines”).

Rule of Thumb – general ratio or guide (“80/20 rule of debugging”).

Philosophical / Value Statement – worldview (“Code is a form of writing”).

Decision Framework – structured logic (“ICE scoring for prioritization”).

Lifecycle Model – phase-based framing (“Prototype → Test → Scale”).

4. Cautionary / Anti-Pattern

Common Mistake – frequent error.

Myth Busting – refuting misconception.

Limitation / Constraint – known boundary or caveat.

Ethical / Security Warning – risk to privacy, safety, or reputation.

Failure Post-Mortem – reflection on what went wrong.

5. Technical / Implementation Detail

Code-Level Tip – syntax, function, library advice.

Architecture / Design Pattern – component arrangement.

Performance Optimization – latency, throughput, cost, scaling.

Integration / API Handling – connectivity guidance.

Debugging / Testing Tip – troubleshooting or validation.

Deployment / Infra Setup – hosting, CI/CD, or environment detail.

6. Empirical / Evidence-Based Observation

Case Study Result – project outcome (“Switching to Polars halved runtime”).

Benchmark Finding – metric comparison.

Experiment Insight – learned from controlled test.

Survey / Dataset Insight – crowd or data-driven conclusion.

Historical Pattern – data-backed trend over time.

7. Mindset / Meta-Skill

Learning / Growth Habit – study and iteration advice.

Motivational Principle – inspiration through perseverance.

Creative Process – ideation or synthesis guidance.

Team Dynamic – communication, trust, or leadership.

Ethical / Philosophical Reflection – long-term values framing.

8. Workflow / Productivity Optimization

Tooling / Automation Tip – time-saving via software or scripts.

Process Systemization – template, pipeline, or SOP creation.

Prioritization / Focus – managing workload.

Collaboration Flow – async vs sync patterns, documentation habits.

Personal Efficiency – routines, batching, or ergonomics.

9. Cultural / Ecosystem Commentary

Trend Prediction – direction of industry (“Agents replacing APIs”).

Community Norms / Critique – social dynamics (“Developers undervalue docs”).

Policy / Ethical Commentary – regulation or fairness note.

Economic Lens – incentives, funding, or pricing.

Meta-Observation – commentary on discourse itself (“Everyone’s chasing virality”).
```
