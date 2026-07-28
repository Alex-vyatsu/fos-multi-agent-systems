# Минимальные воспроизводимые примеры

Каталог содержит небольшие исходные программы, которые запускаются на Python
3.11+ без сторонних библиотек, облачных сервисов и GPU. Их задача — дать
студенту проверяемую стартовую точку и показать формат эксперимента.

Это **не эталонные решения КИМ**. Примеры намеренно упрощены: студент должен
сам выбрать архитектуру, расширить сценарий, провести серию запусков, добавить
сравнение и обосновать выводы по рубрике.

| Пример | Связанный модуль | Что демонстрируется |
|---|---|---|
| [`m1_reactive_agents.py`](m1_reactive_agents.py) | [М1](../M1-agent-architectures/README.md) | реактивные агенты, события, журнал действий |
| [`m2_contract_net.py`](m2_contract_net.py) | [М2](../M2-coordination/README.md) | объявления задач, заявки и распределение по стоимости |
| [`m3_coordination_game.py`](m3_coordination_game.py) | [М3](../M3-game-theory/README.md) | чистые равновесия, Парето-исходы и повторяющаяся игра |
| [`m4_pso.py`](m4_pso.py) | [М4](../M4-swarm-intelligence/README.md) | упрощённый PSO и сравнение с случайным поиском |
| [`m5_independent_q.py`](m5_independent_q.py) | [М5](../M5-marl/README.md) | независимое Q-обучение в кооперативной игре |
| [`m5_ctde_comparison.py`](m5_ctde_comparison.py) | [М5](../M5-marl/README.md) | IQL против VDN-style CTDE на seeds 7/42/99 |
| [`m6_guarded_orchestrator.py`](m6_guarded_orchestrator.py) | [М6](../M6-llm-mas/README.md) | оркестрация, проверка предложения и передача решения человеку |
| [`m6_protocol_slice.py`](m6_protocol_slice.py) | [М6](../M6-llm-mas/README.md) | разные границы A2A/MCP, task lifecycle, scope и отказ инструмента |
| [`exam_end_to_end.py`](exam_end_to_end.py) | [Экзамен](../Exam/kim-02-practical-task.md) | сквозной smoke: данные, распределение, protocol failure и recovery |
| [`defense_experiment.py`](defense_experiment.py) | [Экзамен](../Exam/kim-02-practical-task.md) | два паттерна × три seed, масштаб 4/8/12 и failure/recovery |

## Быстрый запуск

```bash
python examples/m1_reactive_agents.py --seed 42
python examples/m2_contract_net.py --seed 42
python examples/m3_coordination_game.py --seed 42
python examples/m4_pso.py --seed 42
python examples/m5_independent_q.py --seed 42
python examples/m5_ctde_comparison.py
python examples/m6_guarded_orchestrator.py
python examples/m6_protocol_slice.py --compare-patterns
python examples/exam_end_to_end.py --pattern reviewed_pipeline
python examples/exam_end_to_end.py --pattern reviewed_pipeline --inject-tool-failure
python examples/defense_experiment.py
```

Все программы печатают JSON, поэтому результат можно сохранить и сопоставить
между запусками. Полная локальная проверка:

```bash
python other/tools/check_all.py
```

Контейнерная проверка:

```bash
docker build -t fos-mas .
docker run --rm fos-mas
```

Заполненное архитектурное решение, воспроизводимые JSON/JSONL evidence и
сценарий живой демонстрации находятся в
[`evidence/`](../evidence/README.md). Их соответствие коду проверяет
`python other/tools/check_evidence.py`.

## Границы применения

- Примеры подтверждают только работоспособность минимального учебного контура.
- Они не заменяют PettingZoo, RLlib, PySwarms, LLM API и другие инструменты,
  требуемые расширенными вариантами лабораторных работ.
- `m6_protocol_slice.py` проверяет семантику contract slice, но не заявляет
  сетевое соответствие полной спецификации A2A/MCP; mock не доказывает качество
  реальной LLM.
- `latency_ms` в trace — детерминированный учебный budget; реальное время
  фиксируется в clean run. Внешняя стоимость равна нулю, потому что API не
  вызывается.
- Числа из демонстрационных запусков нельзя переносить в отчёт без собственного
  эксперимента и журнала запусков.

Hardware, версии, стоимость, privacy и недоказанные свойства разделены по
[минимальному, рекомендуемому и расширенному профилям](../docs/resource-profiles.md).
