---
title: Electric Circuits — formula sheet
subject: electric-circuits
exams: gate-ee, upsc-ese-ee, ssc-je-ee, rrb-je-ee, state-ae-je, psu-ee
---

# Electric Circuits — formula sheet

Standard results for DC, transient and sinusoidal circuit analysis, written from scratch for this list.
This sheet is a study aid, not a source of exam facts: marks, dates and syllabus claims live on the exam
pages, for example [GATE Electrical Engineering (EE)](../exams/engineering/gate-ee.md). The broader
[courses and syllabus map](../resources/ee-subject-map.md) lists where the subject fits.

## DC basics

$$ V = IR, \qquad P = VI = I^2 R = \frac{V^2}{R}, \qquad G = \frac{1}{R} $$

$$ R_{series} = \sum_k R_k, \qquad \frac{1}{R_{parallel}} = \sum_k \frac{1}{R_k} $$

$$ V_k = V \frac{R_k}{R_{series}}, \qquad I_1 = I \frac{R_2}{R_1 + R_2} \quad \text{(two parallel resistors)} $$

$$ W_C = \frac{1}{2} C V^2, \qquad W_L = \frac{1}{2} L I^2 $$

## Network theorems

$$ \sum_k i_k = 0 \ \text{(KCL at a node)}, \qquad \sum_k v_k = 0 \ \text{(KVL around a loop)} $$

$$ V_{Th} = v_{oc}, \qquad R_{Th} = \frac{v_{oc}}{i_{sc}}, \qquad I_N = \frac{V_{Th}}{R_{Th}} $$

$$ R_L = R_{Th} \ \Rightarrow \ P_{max} = \frac{V_{Th}^2}{4 R_{Th}} $$

## First-order transients

$$ \tau = RC \ \text{(RC circuit)} \quad \text{or} \quad \tau = \frac{L}{R} \ \text{(RL circuit)} $$

$$ x(t) = x(\infty) + \left[x(0^+) - x(\infty)\right] e^{-t/\tau} $$

## Second-order RLC circuits

$$ s^2 + 2\alpha s + \omega_0^2 = 0, \qquad \alpha = \frac{R}{2L}, \qquad \omega_0 = \frac{1}{\sqrt{LC}} $$

$$ \zeta = \frac{\alpha}{\omega_0}, \qquad \omega_d = \sqrt{\omega_0^2 - \alpha^2} \quad (\alpha < \omega_0) $$

Overdamped means $\alpha > \omega_0$, critically damped means $\alpha = \omega_0$, and underdamped means
$\alpha < \omega_0$, with damped frequency $\omega_d$.

## Sinusoidal steady state

$$ Z_R = R, \qquad Z_L = j\omega L, \qquad Z_C = \frac{1}{j\omega C} $$

$$ Z = R + j\left(\omega L - \frac{1}{\omega C}\right), \qquad |Z| = \sqrt{R^2 + \left(\omega L - \frac{1}{\omega C}\right)^2} $$

$$ V_{rms} = \frac{V_m}{\sqrt{2}} \quad \text{(sinusoid)}, \qquad S = V_{rms} I_{rms}^{*} = P + jQ $$

$$ P = V_{rms} I_{rms} \cos\varphi, \qquad Q = V_{rms} I_{rms} \sin\varphi, \qquad \text{power factor} = \cos\varphi $$

## Resonance

$$ \omega_0 = \frac{1}{\sqrt{LC}}, \qquad Q = \frac{\omega_0 L}{R} = \frac{1}{R}\sqrt{\frac{L}{C}}, \qquad \Delta\omega = \frac{\omega_0}{Q} = \frac{R}{L} \quad \text{(series RLC)} $$

$$ Q = R\sqrt{\frac{C}{L}}, \qquad \Delta\omega = \frac{1}{RC} \quad \text{(parallel RLC)} $$

## Three-phase systems

$$ \text{star: } V_L = \sqrt{3}\, V_{ph}, \quad I_L = I_{ph}; \qquad \text{delta: } V_L = V_{ph}, \quad I_L = \sqrt{3}\, I_{ph} $$

$$ P_{3\phi} = \sqrt{3}\, V_L I_L \cos\varphi = 3 V_{ph} I_{ph} \cos\varphi $$

## Coupled inductors

$$ v_1 = L_1 \frac{di_1}{dt} + M \frac{di_2}{dt}, \qquad v_2 = M \frac{di_1}{dt} + L_2 \frac{di_2}{dt}, \qquad M = k\sqrt{L_1 L_2} $$

## Two-port networks

$$ \begin{aligned} V_1 &= z_{11} I_1 + z_{12} I_2 \\ V_2 &= z_{21} I_1 + z_{22} I_2 \end{aligned} $$

$$ \begin{aligned} V_1 &= A V_2 - B I_2 \\ I_1 &= C V_2 - D I_2 \end{aligned}, \qquad AD - BC = 1 \ \text{(reciprocal two-port)} $$

## How to use this sheet

- Revise a block, then attempt the matching practice questions in [`questions/`](../questions/README.md).
- Re-derive, never memorise alone: every line above follows from KCL, KVL and the element laws.
