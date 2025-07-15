# tasks/csrf_detector.py

import numpy as np
from .models import Automata, Transition, Alerta, SessionState, Evento
import logging

logger = logging.getLogger(__name__)


class ProbabilisticAutomaton:
    def __init__(self, name="CSRF_Detector"):
        auto = Automata.objects.get(nombre=name)
        self.states = auto.estados
        self.idx = {s: i for i, s in enumerate(self.states)}
        n = len(self.states)
        self.P = np.zeros((n, n))
        for t in auto.transitions.all():
            i, j = self.idx[t.estado], self.idx[t.destino]
            self.P[i, j] += t.prob
        self.dist = np.zeros(n)
        self.dist[self.idx[auto.inicial]] = 1.0
        self.final_idxs = {self.idx[s] for s in auto.finales}

    def step(self, evt):
        new = np.zeros_like(self.dist)
        for i, p in enumerate(self.dist):
            if p:
                new += p * self.P[i]
        if new.sum():
            new /= new.sum()
        self.dist = new
        return new


THRESHOLD = 0.8


def evaluar_evento(evento):
    if evento.tipo_evento == "request_end":
        return

    state, _ = SessionState.objects.get_or_create(
        sesion_id=evento.sesion_id,
        defaults={'distribution': [1.0] + [0.0] * (len(ProbabilisticAutomaton().states) - 1)}
    )
    automaton = ProbabilisticAutomaton()
    automaton.dist = np.array(state.distribution)

    if evento.tipo_evento == "login":
        dist = np.array([1.0] + [0.0] * (len(automaton.states) - 1))
    else:
        dist = automaton.step(evento.tipo_evento)

    state.distribution = dist.tolist()
    state.save()

    prob_ataque = sum(dist[i] for i in automaton.final_idxs)
    if prob_ataque >= 0.8:
        Alerta.objects.create(
            sesion_id=evento.sesion_id,
            evento=evento,
            probabilidades={s: float(dist[idx]) for s, idx in automaton.idx.items()}
        )
