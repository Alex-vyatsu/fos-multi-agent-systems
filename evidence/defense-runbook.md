# Сценарий живой защиты минимального профиля

Сценарий рассчитан на 15–20 минут и проверяет репозиторий действием. Он не
задаёт текст ответа: обучающийся должен понимать код, самостоятельно объяснять
решения и выполнить изменение, выбранное экзаменатором.

## 1. Идентификация версии — 1 минута

```bash
git rev-parse --short HEAD
python --version
python other/tools/check_all.py
```

Ожидается: все локальные проверки пройдены, опубликованные evidence-файлы
совпадают с воспроизводимым результатом.

## 2. Обоснование архитектуры — 3 минуты

Открыть [паспорт решения](architecture-decision.md) и объяснить:

- почему фиксированный и централизованный варианты остаются baseline;
- зачем аналитику и рецензенту разные задачи и владельцы;
- почему capability не равна полномочию;
- когда МАС избыточна и требуется откат к более простому решению.

## 3. Два паттерна и наблюдаемость — 4 минуты

```bash
python examples/m6_protocol_slice.py --compare-patterns
```

Показать для `orchestrator` и `reviewed_pipeline` общие метрики:
`event_count`, `latency_budget_ms`, `external_cost_usd`, наличие независимого
review. По trace различить A2A, MCP и policy events; найти `interaction_id`,
`task_id`, `tool_call_id`, `policy_decision_id` и `artifact_id`.

## 4. Повтор ключевого результата — 3 минуты

```bash
python examples/exam_end_to_end.py \
  --seed 42 \
  --pattern reviewed_pipeline \
  --summary-output /tmp/defense-run.json \
  --trace-output /tmp/defense-trace.jsonl
```

Ожидается: `passed = true`, задачи распределены один раз, primary и review
завершены, все acceptance checks истинны, ответственное решение имеет статус
`awaiting_human_decision`.

## 5. Изменение «на месте» — 3 минуты

Экзаменатор выбирает одно изменение.

### Масштаб

```bash
python examples/exam_end_to_end.py --seed 42 --tasks 4
python examples/exam_end_to_end.py --seed 42 --tasks 12
```

Обучающийся объясняет изменение `message_count`, границу локального dataset и
почему этот минимальный пример не доказывает произвольное масштабирование.

### Паттерн

```bash
python examples/exam_end_to_end.py --seed 42 --pattern orchestrator
python examples/exam_end_to_end.py --seed 42 --pattern reviewed_pipeline
```

Обучающийся объясняет цену независимого review и правило выбора по риску.

### Отказ

```bash
python examples/exam_end_to_end.py \
  --seed 42 \
  --pattern reviewed_pipeline \
  --inject-tool-failure
```

Ожидается: исходный path `failed`, отдельный recovery `completed`, двойного
эффекта нет, результат всё ещё ожидает решения человека.

## 6. Эксперимент и границы вывода — 3 минуты

```bash
python examples/defense_experiment.py
```

Показать IQL против VDN-style CTDE, два LLM-паттерна × seeds 7/42/99, масштаб
4/8/12 и local failure/recovery. Объяснить, что latency — учебный
deterministic budget, внешняя стоимость равна нулю, tabular MARL не доказывает
перенос на другую среду, а semantic slice не подтверждает wire-conformance или
качество реальной LLM.

## Финальная самопроверка

- [ ] сценарий выполняется из опубликованных файлов;
- [ ] выбор МАС объяснён относительно более простого варианта;
- [ ] trace восстанавливает путь request → tasks → tool → review → artifact;
- [ ] отказ и восстановление различимы;
- [ ] изменён параметр, указанный экзаменатором;
- [ ] ответственная роль и human gate названы;
- [ ] собственный вклад и границы переноса объяснены.
