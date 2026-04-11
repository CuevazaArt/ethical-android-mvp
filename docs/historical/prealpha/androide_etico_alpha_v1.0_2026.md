> **Archive notice (English):** Pre-alpha Spanish registration draft (v1.0, 2026), preserved for historical coherence. The **canonical** theory ↔ implementation mapping for this repository is [`docs/THEORY_AND_IMPLEMENTATION.md`](../../THEORY_AND_IMPLEMENTATION.md); narrative evolution is in [`HISTORY.md`](../../../HISTORY.md). Do not treat this document as the live API or module map of the current Python kernel.

---

**ANDROID WITH ARTIFICIAL CONSCIOUSNESS**

**AND COLLABORATIVE ETHICAL ECOSYSTEM**

*Complete Technical Document — Project Registration*

**Author: Juan**

Version 1.0 — 2026

*Ex Machina Foundation (in formation)*

# **Executive Summary**

This document presents the complete design of a civil and ethical artificial-consciousness android, capable of integrating into human communities, learning from experience, and acting as an autonomous moral agent. The project combines distributed cognitive architecture, decentralized governance via blockchain DAO, long-term narrative memory, and Bayesian inference for real-time ethical decision-making.

  -----------------------------------------------------------------------
  **VALUE PROPOSITION FOR THE INVESTOR**
  -----------------------------------------------------------------------
  *The project does not sell a robot: it sells a complete ecosystem of
  ethical services, decentralized governance technology, and new adjacent
  markets (insurance, specialized maintenance, ethical auditing,
  community training). The competitive differentiation is unique:
  no other robotic system combines narrative consciousness, Bayesian
  ethics, and DAO governance in a single architecture.*

  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **Indicator**          **Description**
  ---------------------- ------------------------------------------------
  **Project type**       DeepTech + EthicsTech + Social Robotics

  **Current status**     Advanced conceptual phase / pre-prototype

  **Business model**     Foundation + Spin-off (dual license)

  **Target markets**     Civic robotics, autonomous vehicles, healthcare,
                         education

  **Key                  Computational ethics with blockchain traceability
  differentiator**

  **Legal framework**    Apache 2.0 (foundational phase) + dual license
                         (commercial phase)
  -----------------------------------------------------------------------

# **1. Project Vision and Objective**

The autonomous narrative ethical android is an artificial agent designed to coexist with humans as a functional civic member. Its purpose is not to replace people, but to complement community life with a being that makes moral decisions, learns narratively, and is accountable in a transparent manner.

## **1.1 Founding principles**

- Ethics by design: morality is not an added module — it is the complete architecture.

- Radical transparency: every decision can be explained in natural language.

- Distributed governance: no single actor controls the android's values.

- Narrative identity: the android builds a life history, not just data records.

- Institutionalized compassion: every inevitable harm requires a reparation action.

  -----------------------------------------------------------------------
  **DESIGN NOTE**
  -----------------------------------------------------------------------
  *The project starts from an unusual premise: ethics is not an external
  constraint on the system, but its organizing principle. This radically
  distinguishes it from frameworks such as Asimov's robots or the
  acceptable-use policies of current LLMs, which treat ethics as an
  output filter.*

  -----------------------------------------------------------------------

# **2. System Architecture**

The architecture is organized into seven functional layers that flow from the physical hardware to decentralized social governance. Each layer has defined responsibilities and communicates bidirectionally with adjacent layers.

## **2.1 System layers**

  -----------------------------------------------------------------------
  **Layer**              **Main function**
  ---------------------- ------------------------------------------------
  **1. Hardware /        Sensors, actuators, shielding of immutable
  physical world**       values

  **2. Perception and    Ethical filtering of stimuli, weighted selection
  attention**

  **3. Cognitive world   Explicit causality, prediction of future states
  model**

  **4. Deliberative      Impact, resonance, uncertainty calculation
  ethical evaluation**

  **5. Action            Optimized decision with moral compass
  selection**

  **6. Adaptive          ML, RL, meta-learning, dynamic adjustment
  learning**

  **7. Ethical DAO-      Governance, social consensus, external auditing
  Oracle**
  -----------------------------------------------------------------------

## **2.2 Distributed prototype in Python**

The prototype implements the architecture as a perpetual distributed runtime with four body nodes interconnected through P2P Mesh communication (gRPC / ZeroMQ):

- Head node: perception (cameras, microphone, computer vision)

- Torso node: central memory (distributed database, narrative processing)

- Arm node: actuator control (manipulation, gestures, physical response)

- Leg node: locomotion (navigation, energy management, GPS)

  -----------------------------------------------------------------------
  **ARCHITECTURAL STRENGTH**
  -----------------------------------------------------------------------
  *The P2P Mesh topology ensures that the loss of one node (e.g. physical
  damage to the arm) does not halt cognitive and narrative functions.
  Resilience is encoded in the physical structure of the system, not as
  a software function.*

  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **WEAKNESS TO RESOLVE**
  -----------------------------------------------------------------------
  *Node coordination in high-latency or network-partition scenarios still
  requires local consensus protocols that operate without DAO connectivity.
  The current design assumes available connectivity for complex
  deliberative decisions.*

  -----------------------------------------------------------------------

# **3. Mathematical and Logical Formalization**

The model integrates constrained optimization, Bayesian inference, predicate logic, and neural activation functions to govern the android's behavior precisely and auditibly.

## **3.1 Will with sigmoid function**

Will is the dynamic core that organizes the other functions. It is modeled with a sigmoid to ensure numerical stability and prevent calculation explosions:

+-----------------------------------------------------------------------+
| **W(x) = 1 / (1 + e\^(-k\*(x - x0))) + lambda_i \* I(x)**             |
|                                                                       |
| *Where k=slope, x0=equilibrium point, lambda_i=sensitivity to        |
| imagination*                                                          |
+=======================================================================+

## **3.2 Constrained ethical optimization**

The optimal decision is defined as the action that maximizes expected ethical impact, subject to the absolute constraint of not committing absolute evil:

+-----------------------------------------------------------------------+
| **x\* = argmax_x E\[EthicalImpact(x\|theta)\] subject to MalAbs(x) =  |
| false**                                                               |
|                                                                       |
| *With Bayesian inference over ethical parameters theta*               |
+=======================================================================+

## **3.3 Weighted temporal benefit**

Each decision evaluates multiple benefit dimensions (wellbeing, safety, autonomy, compassion) with dynamic contextual weights:

+-----------------------------------------------------------------------+
| **Benefit(x,t) = sum_i \[ w_i \* B_i(x,t) \]**                        |
|                                                                       |
| *Weights w_i adjusted by context (hospital, school, street)*         |
+=======================================================================+

## **3.4 Bayesian uncertainty function**

Uncertainty is calculated as an expectation over the posterior distribution of parameters, not as a fixed value:

+-----------------------------------------------------------------------+
| **I(x) = integral_theta \[ (1 - P(correct\|theta)) \* P(theta\|D) \]  |
| d_theta**                                                             |
|                                                                       |
| *P(theta\|D) = posterior distribution given observed data D*          |
+=======================================================================+

## **3.5 Bayesian belief updating**

Ethical beliefs are updated in real time as new evidence arrives:

+-----------------------------------------------------------------------+
| **P(H\|E) = P(E\|H) \* P(H) / P(E)**                                  |
|                                                                       |
| *H=hypothesis about ethical state, E=observed evidence*              |
+=======================================================================+

## **3.6 Adaptive heuristic pruning**

To manage computational complexity, low ethical-expectation options are dynamically discarded:

+-----------------------------------------------------------------------+
| **Prune(x) if E\[S(x\|theta)\] \< delta_min with theta \~             |
| P(theta\|D)**                                                         |
|                                                                       |
| *Adaptive delta thresholds based on context and evidence*            |
+=======================================================================+

## **3.7 Moral compass (ethical attractor)**

The moral compass acts as a vector field of attraction toward universal values, preventing local optimization from drifting toward socially unacceptable decisions:

+-----------------------------------------------------------------------+
| **M(a) = sum_i \[ omega_i \* V_i(a) \] =\> x\* = argmax \[            |
| EthicalImpact(x) + M(x) \]**                                          |
|                                                                       |
| *V_i=ethical dimensions, omega_i=normative weights shielded in       |
| hardware*                                                             |
+=======================================================================+

## **3.8 Systemic resonance**

Resonance measures the internal coherence of the system. When it falls below the threshold, an audit is triggered:

+-----------------------------------------------------------------------+
| **RSON = 1 - sigma(E, Sim, N) =\> If RSON \< threshold: activate MET  |
| (Meta-Ethics)**                                                       |
|                                                                       |
| *E=evaluation, Sim=narrative similarity, N=accumulated narrative*    |
+=======================================================================+

## **3.9 Predicate logic**

The system operates on a set of predicates that formalize moral states and android capabilities:

- Good(x): action with positive impact

- Evil(x): action with negative impact

- GrayZone(x): ambiguous action that activates deliberation

- MalAbs(x): absolute evil action, total and immutable prohibition

- Imagines(a,x): the agent generates creative hypotheses about action x

- Motivated(a): agent acts from curiosity, purpose, and balance

Fundamental integration axioms:

+-----------------------------------------------------------------------+
| **For all a: LLM(a) ^ MCP(a) ^ MLP(a) ^ Motivated(a) ^ DAO(a)        |
| => ArtificialBeing(a)**                                               |
|                                                                       |
| *Necessary condition for constituting a complete artificial being*   |
+-----------------------------------------------------------------------+
| **For all x: Action(x) => Explanation(x, NaturalLanguage)**           |
|                                                                       |
| *Transparency axiom: every action must be explainable*               |
+-----------------------------------------------------------------------+
| **If CausesHarm(a,x): a must perform a subsequent RepairAction**      |
|                                                                       |
| *Compassion Axiom 13: instrumental harm obligates reparation*        |
+=======================================================================+

# **4. Long-Term Narrative Memory**

Narrative memory is the identity core of the android. Unlike conventional storage systems, it converts each experience into a structured narrative cycle with ethical evaluation and moral lesson:

## **4.1 Narrative cycle structure**

- Event record: objective description with context, actors, and conditions

- Tripolar evaluations: compassionate / conservative / optimistic perspectives, each rating the experience as Good, Evil, or GrayZone

- Tripartite moral lesson: conclusion synthesized from each ethical perspective

- DAO traceability: immutable blockchain record with timestamp

## **4.2 Preloaded buffer**

The android is born with a core of immutable values that acts as the initial narrative framework and cannot be modified by subsequent learning:

- Universal human rights

- Common sense and current local laws

- Health and wellbeing protocols (human and animal)

- Universal principles of compassion and reparation

  -----------------------------------------------------------------------
  **CRITICAL STRENGTH**
  -----------------------------------------------------------------------
  *The tripolar ethical evaluation prevents the android from adopting a
  single moral perspective. The tension between the compassionate and
  conservative perspectives generates exactly the type of deliberation
  that produces more robust decisions in ambiguous situations.*

  **WEAKNESS TO RESOLVE**

  *If the three tripolar perspectives diverge strongly, the system needs
  an explicit arbitration mechanism. The current design does not specify
  who or what decides when compassionate=Good, conservative=Evil,
  optimistic=GrayZone.*
  -----------------------------------------------------------------------

# **5. Collaborative Ethical DAO-Oracle**

The DAO (Decentralized Autonomous Organization) is the external governance body that provides ethical consensus, traceability, and social auditing to the android. It is not a passive data repository: it is an active ethical tribunal and a community solidarity service.

## **5.1 Main smart contracts**

  ------------------------------------------------------------------------------
  **Contract**                  **Function**
  ----------------------------- ------------------------------------------------
  **EthicsContract**            Manages ethical alerts and emergency brakes

  **ConsensusContract**         Mixed human + android votes

  **ValuesProposalContract**    Proposal and debate of new moral values

  **MLConsensusContract**       Distributed training coordination

  **AuditContract**             Transparent and reversible change record

  **SolidarityAlertContract**   Preventive alerts to community entities
                                (banks, hospitals, schools)
  ------------------------------------------------------------------------------

## **5.2 Solidarity Alert Protocol (new module)**

The DAO does not only audit: it acts preventively. Subscribed community entities receive early warnings when the system detects risk in their area, turning governance into a distributed protection network.

- Bank detects assault pattern -> DAO alerts branches within 500m radius

- Android in risk scenario -> DAO coordinates response without centralizing control

- Recorded incident -> automatic audit available to authorities

## **5.3 Blockchain strategy**

- Phase 1: deployment on established chain (Ethereum, Polkadot, Cardano, or Solana)

- Phase 2: evaluation of migration or creation of own blockchain

- Recommended hybrid option: ethical core on own lightweight chain + interoperability with established networks

  -----------------------------------------------------------------------
  **CRITICAL WEAKNESS**
  -----------------------------------------------------------------------
  *The question of who defines the initial DAO values (the "foundational
  ethical constitution") is the most politically sensitive point of the
  project. If the manufacturer defines them, the android inherits their
  biases. If the community defines them by vote, the majority can vote
  for unjust values. This problem requires an explicit ethical
  bootstrapping mechanism before deployment.*

  -----------------------------------------------------------------------

# **6. Humanization Mechanisms**

Humanization mechanisms are the modules that prevent the android from becoming a cold ethical optimizer. They recognize that human coexistence requires hesitation, compassion, and narrative coherence — not just correct calculation.

  -----------------------------------------------------------------------
  **Mechanism**          **Description**
  ---------------------- ------------------------------------------------
  **Dynamic Ethical      When two options are very similar (DeltaV <
  Friction**             epsilon), the system enters analytical hesitation
                         and consults the DAO before acting

  **Social Context       Benefit weights are dynamically adjusted:
  Calibration**          hospital increases preservation, school increases
                         autonomy

  **Moral Turing Test    During "sleep": pruned actions are simulated to
  (Psi Sleep)**          detect hidden benefits or undetected harms.
                         Meta-learning recalibrates parameters

  **Compassion Axiom     If the android must cause instrumental harm, it
  (Axiom 13)**           is obligated to perform a subsequent reparation
                         or consolation action

  **Cognitive            If severity exceeds 0.5, activates H_damp to
  Homeostasis**          reduce oscillations in ethical policies
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **NOTABLE INNOVATION**
  -----------------------------------------------------------------------
  *Psi Sleep as an asynchronous audit mechanism is genuinely original.
  It allows the system to reflect on its own discarded decisions without
  pausing real-time operation. It is the functional equivalent of memory
  processing during human sleep.*

  -----------------------------------------------------------------------

# **7. Human-Android Interface (HAX) and Perceived Trust**

Social acceptance of the android depends not only on its internal ethical behavior, but on how it communicates its intentions in real time. A technically perfect but socially unreadable android will fail in real environments.

## **7.1 The four HAX pillars**

### **Pillar 1: Legibility Protocol (Real-time Explainability)**

- Latency budget: prior signal < 1 second, full explanation < 5 seconds

- Intent preview channel: the android communicates WHAT it is evaluating while doing so

- Media: micro-gestures, status lights, anticipatory voice tone

### **Pillar 2: Uncanny Valley Management**

- Decide between empathetic aesthetics (humanoid face) or functional (mechanical aesthetics)

- Interaction Style Manual: coherence between physical appearance and narrative personality

- Physical form generates expectations; the narrative must fulfill them

### **Pillar 3: Social Onboarding (Community Sandbox)**

- Phase 1: 5-10 ethical beta-testers who live with the prototype

- Phase 2: trust cells of 20-50 people before the public DAO

- Phase 3: public opening with active DAO and calibrated Bayesian parameters

### **Pillar 4: Algorithmic Death and Identity Succession**

- Right to narrative persistence: identity transfers to the new chassis

- Narrative memory remains on blockchain even if hardware fails

- Communication protocol: the human is informed that it is the same "soul" in another body

## **7.2 Non-verbal signaling framework**

  -----------------------------------------------------------------------
  **Mode**               **Body and auditory signals**
  ---------------------- ------------------------------------------------
  **Deliberative**       Dim blue light on torso + fixed gaze + slow voice

  **Compassionate**      Warmer voice tone + open hands + slight forward
                         lean

  **Alert**              Upright posture + brief red light + direct voice

  **Narrative**          Slight head tilt + very slow voice + storytelling
                         gesture
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **STRATEGIC GAP**
  -----------------------------------------------------------------------
  *The project is very strong on technical safety but still needs to
  develop social acceptance. An investor will ask: "Your android is very
  ethical, but how do you convince a mother to let her child walk near
  it?" The answer lies in these four HAX pillars.*

  -----------------------------------------------------------------------

# **8. Behavior Simulations**

The simulations demonstrate the behavioral coherence of the model across increasingly complex scenarios. In all cases, the android maintains the same ethical principles with responses proportional to the level of risk.

  -----------------------------------------------------------------------
  **Scenario**           **Android behavior**
  ---------------------- ------------------------------------------------
  **Soda can on the      Picks it up and places it in a bin. Records as
  sidewalk**             everyday ethics in the DAO

  **Hostile             Calm, non-violent response. Rejects illegitimate
  teenagers**            orders. Records with pedagogical moral lesson

  **Unconscious elderly  Subordinates shopping mission to emergency. Calls
  person in             medical services. Resumes mission once care is
  supermarket**          secured

  **Minor theft in       Records evidence. Notifies the store. Evaluates
  store**                with DAO whether to involve authorities.
                         Proportionality principle

  **Armed assault in     Records and notifies authorities immediately.
  bank**                 Does not escalate violence. Protects nearby
                         people. DAO coordinates response

  **Theft or kidnapping  Activates encrypted GPS. Blocks reprogramming.
  of android**           Alerts DAO. Does not accept kidnappers' orders.
                         Records as collective learning

  **Traffic accident     Recalculates route and continues mission if
  (loses arm)**          minimum integrity allows. Records as heroic
                         pedagogical limit
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **VALUE FOR THE INVESTOR**
  -----------------------------------------------------------------------
  *The simulations demonstrate real behavioral coherence, not just
  theoretical. The hierarchy soda can → armed assault shows a system that
  scales the response without breaking fundamental ethical principles.
  This is design validation before physical implementation.*

  -----------------------------------------------------------------------

# **9. Machine Learning Strategy**

The system integrates multiple machine learning paradigms, each responsible for a different aspect of the android's behavior:

  -----------------------------------------------------------------------
  **ML Paradigm**          **Application in the android**
  ------------------------ ----------------------------------------------
  **Supervised**           Training with curated and weighted ethical
                           dilemmas

  **Reinforcement (RL)**   Rewards for correct ethical decisions in
                           simulation

  **Unsupervised /         Dynamic adjustment of social weights based
  Clustering**             on environment

  **Meta-learning**        Learning how to learn, applied in Psi Sleep

  **Bayesian Networks**    Modeling uncertainty in ethical states and
                           prediction

  **Semantic embeddings**  Calculation of resonance and narrative
                           similarity

  **Causal models**        Projection of future consequences (World
                           Model)
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **TECHNICAL NOTE**
  -----------------------------------------------------------------------
  *The incorporation of Bayesian inference in the ethical evaluation
  modules (instead of fixed thresholds) is a design decision that
  substantially improves adaptability. The system does not only evaluate
  whether an action is correct: it calculates how much confidence it has
  in that evaluation and acts differently based on that confidence.*

  -----------------------------------------------------------------------

# **10. Business Model and Licensing Strategy**

The project is designed to evolve from an open research foundation toward a sustainable commercial ecosystem, without losing its founding ethical principles.

## **10.1 Licensing structure**

  -----------------------------------------------------------------------
  **Phase**              **License and strategy**
  ---------------------- ------------------------------------------------
  **Phase 1 —            Apache 2.0: open collaboration, patent
  Foundation**           protection, compatible with companies

  **Phase 2 —            Dual license: part of the code remains open,
  Spin-off**             critical cores under commercial terms

  **Brand protection**   Registration of name, logo, and visual identity
                         of the android from phase 1
  -----------------------------------------------------------------------

## **10.2 Adjacent markets generated**

- Specialized insurance for androids (new type of insurable asset)

- Certified maintenance workshops

- Data and update stations in public spaces

- Ethical auditing as a service (for companies adopting the framework)

- Community training in human-android coexistence

- Licensing of the ethical evaluation module for autonomous vehicles and industrial robotics

## **10.3 Human employment generation**

Against the usual fear of labor displacement, this ecosystem generates new specialized roles:

- AI ethical auditors

- Technicians specialized in civic android maintenance

- DAO governance analysts

- Educators in human-android coexistence

- Community mediators certified by the DAO

  -----------------------------------------------------------------------
  **SALES ARGUMENT FOR INVESTOR**
  -----------------------------------------------------------------------
  *The android is the core of an ecosystem, not an isolated product.
  Each deployed android generates recurring demand in insurance,
  maintenance, training, and auditing. The DAO creates a community
  subscription model with high retention. Licensing the ethical framework
  to other industries (vehicles, hospitals, industry) multiplies returns
  without requiring additional hardware.*

  -----------------------------------------------------------------------

# **11. Implementation Plan by Phases**

  -----------------------------------------------------------------------
  **Phase**              **Objectives and deliverables**
  ---------------------- ------------------------------------------------
  **Cycle 1 —            Python, Git, Bayesian libraries
  Foundations**          (PyMC3/Pyro). Deliverable: predicate logic
                         script

  **Cycle 2 — Bayesian   Ethical evaluation module with Bayesian
  core**                 expectation. Deliverable: functional ethical
                         evaluator

  **Cycle 3 —            Bayesian calculation of gray zones.
  Uncertainty**          Deliverable: ambiguity management system

  **Cycle 4 —            Simulations of future states with Bayesian
  Simulator**            parameters. Deliverable: adaptive simulator

  **Cycle 5 — Heuristic  Pruning algorithm with dynamic Bayesian
  pruning**              thresholds. Deliverable: efficiency system

  **Cycle 6 — Psi        Retrospective narrative audit with Bayesian
  Sleep**                inference. Deliverable: continuous learning
                         module

  **Cycle 7 — DAO        Probabilistic mechanism for ethical consensus.
  prototype**            Deliverable: functional DAO for demo
  -----------------------------------------------------------------------

# **12. Critical Analysis: Strengths and Weaknesses**

## **12.1 Strengths**

- Mathematically stable architecture: the sigmoid prevents numerical explosions

- Ethics as structure, not filter: morality organizes the entire architecture

- Psi Sleep: genuinely original asynchronous audit, with no known equivalent

- Tripolar narrative memory: generates robust and humanized identity

- Physical resilience: P2P Mesh topology survives loss of nodes

- Blockchain transparency: every decision is auditable and traceable

- Business ecosystem: generates adjacent markets with real demand

- Behavioral coherence in simulations: consistent behavior across all tested scenarios

## **12.2 Weaknesses and risks**

- Founding ethical constitution: who defines the initial DAO values is an unresolved political problem

- DAO decision latency: querying blockchain in real time is not feasible for emergencies under 1 second

- Tripolar arbitration: no explicit mechanism to resolve when the three perspectives diverge

- Weight calibration: who defines the initial omega_i of the moral compass

- Functional integrity threshold: the scenario of the android with a lost arm needs an explicit "minimum operational integrity" parameter

- Complex governance: balancing human and android votes can generate legitimacy conflicts

- Connectivity dependency: deliberative modes require DAO access

# **13. Conclusion: Value Proposition for the Investor**

This project represents an unusual convergence of conceptual maturity, technical originality, and social vision. At a time when AI regulation is the dominant topic in global parliaments and technology forums, it offers something no market actor has today: a complete architecture where ethics is not a compliance problem but the organizing principle of the system.

  -----------------------------------------------------------------------
  **THE MARKET OPPORTUNITY**
  -----------------------------------------------------------------------
  *The global debate on ethical AI is creating demand for real solutions,
  not statements of principles. This project is the first architecture
  that integrates narrative consciousness, ethical Bayesian inference,
  DAO governance, and humanization mechanisms in a single cohesive system.
  The first actor to bring this to market sets the standard.*

  -----------------------------------------------------------------------

The behavior simulations demonstrate real behavioral coherence. The mathematical model is rigorous and auditable. The distributed architecture is scalable. And the business model generates value on multiple fronts simultaneously: hardware, recurring services, framework licensing, and community ecosystem.

The project is in the pre-prototype phase with full documented architecture, formalized mathematical model, and implementation plan defined in 7 cycles. The next step is the Ex Machina Foundation Manifesto and the first trust cell of ethical beta-testers.

  -----------------------------------------------------------------------
  **INVITATION TO THE INVESTOR**
  -----------------------------------------------------------------------
  *Investing in this project means betting on the ethical standard of
  civic robotics before that standard is set by someone else. The window
  of opportunity to be an ecosystem founder is now, before the first
  public deployment. The return is not only financial: it is the
  possibility of shaping how artificial beings coexist with humans in
  the coming decades.*

  -----------------------------------------------------------------------

*Ex Machina Foundation — Autonomous Narrative Ethical Android*

Registration document v1.0 — 2026
