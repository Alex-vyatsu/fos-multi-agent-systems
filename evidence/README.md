# Доказательства предзащитной готовности

Каталог содержит небольшой воспроизводимый комплект для проверки
[КИМ-Э.2](../Exam/kim-02-practical-task.md). Это не готовая студенческая работа
и не решение экзаменатора: обучающийся обязан объяснить архитектуру, повторить
эксперимент и выполнить изменение «на месте».

## Состав

| Артефакт | Назначение |
|---|---|
| [architecture-decision.md](architecture-decision.md) | заполненный пример паспорта архитектурного решения |
| [defense-runbook.md](defense-runbook.md) | последовательность живой демонстрации и ожидаемые признаки прохождения |
| [defense-run-seed42.json](defense-run-seed42.json) | сводка normal path для `reviewed_pipeline` |
| [defense-trace-seed42.jsonl](defense-trace-seed42.jsonl) | коррелированный журнал A2A, MCP, policy decisions и артефактов |
| [pattern-experiment.json](pattern-experiment.json) | IQL/VDN, два LLM-паттерна × три seed, масштаб 4/8/12 и failure/recovery |

## Воспроизведение

```bash
python examples/exam_end_to_end.py \
  --seed 42 \
  --pattern reviewed_pipeline \
  --summary-output evidence/defense-run-seed42.json \
  --trace-output evidence/defense-trace-seed42.jsonl

python examples/defense_experiment.py \
  --output evidence/pattern-experiment.json

python other/tools/check_evidence.py
```

`check_evidence.py` пересоздаёт ожидаемые структуры в памяти и сравнивает их с
опубликованными файлами. Секреты, персональные данные и полные prompts в журнал
не записываются.

## Граница утверждения

Доказательства относятся к минимальному CPU-only semantic contract slice:

- A2A `1.0.0` и MCP `2025-11-25` представлены проверяемыми семантическими
  границами, но не сетевой реализацией;
- `latency_ms` в trace — детерминированный учебный budget, реальное время
  фиксируется отдельным clean run;
- внешняя стоимость равна нулю, потому что LLM API не вызывается;
- качество реальной LLM, wire-conformance и промышленная эксплуатация не
  подтверждаются.
