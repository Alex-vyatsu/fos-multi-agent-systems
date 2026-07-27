# Профили приемки ФОС «Мультиагентные системы»

**Редакция:** `0.2.0`  
**Назначение:** перевод паттернов в проверяемые условия без заявления, что
проверки уже пройдены.

## 1. Общий формат результата

```yaml
check_result:
  profile_id: ""
  profile_version: "0.2.0"
  object_ref: ""
  object_version: ""
  environment_ref: ""
  evidence_refs: []
  checks:
    - id: ""
      status: pass | fail | blocked | not_applicable
      evidence_ref: ""
      note: ""
  executed_at: ""
  executor_role: ""
  limitations: []
```

Отсутствующее доказательство дает `blocked` или `fail`, но не `pass`.
`not_applicable` требует объяснения границы.

## 2. `FOS-CP-01` — Минимальный исполняемый комплект

| ID | Проверка | Доказательство |
|---|---|---|
| `CP01-ENV` | Окружение создается из закрепленного файла | lock/environment file + build log |
| `CP01-BASE` | Baseline запускается одной опубликованной командой | command + stdout/result artifact |
| `CP01-DATA` | Dataset доступен или generator детерминированно создает малый набор | path/URL/hash или generator seed |
| `CP01-SMOKE` | Smoke test завершается на minimum profile | test report |
| `CP01-OPEN` | Исследовательская переменная не закрыта baseline | КИМ-to-baseline review |
| `CP01-FALLBACK` | Есть путь без платного API/GPU либо явный blocker | fallback run or blocker record |

## 3. `FOS-CP-02` — Атомарная модель измерения

| ID | Проверка | Доказательство |
|---|---|---|
| `CP02-KRM` | Формулировка индикатора совпадает с исходной КРМ | source cell/ref + normalized row |
| `CP02-LEVEL` | Уровень указан на строке индикатора | atomic matrix row |
| `CP02-DESC` | Предметный дескриптор находится в отдельном поле | matrix schema |
| `CP02-KIM` | Есть direct link на конкретный КИМ | resolvable path |
| `CP02-EVID` | Evidence item и rubric row адресуемы | КИМ/rubric anchors |
| `CP02-MIN` | Минимальное условие задано отдельно от общей суммы | acceptance field |
| `CP02-RESOURCE` | Каждый требуемый ресурс указан напрямую | resource record ids |
| `CP02-VIEW` | Модульная сводка воспроизводится из атомарных строк | generation/check result |

Минимальная строка:

```yaml
measurement_row:
  element_id: ""
  indicator_id: ""
  krm_wording_verbatim: ""
  level: ""
  subject_descriptor: ""
  control_form: ""
  kim_ref: ""
  evidence_item_ref: ""
  rubric_row_ref: ""
  minimum_condition: ""
  resource_refs: []
```

## 4. `FOS-CP-03` — Доступность ресурса

| ID | Проверка | Доказательство |
|---|---|---|
| `CP03-DIRECT` | Путь/URL ведет к точному объекту | link check |
| `CP03-VERSION` | Версия, hash или дата среза закреплены | resource manifest |
| `CP03-ACCESS` | Целевая аудитория может получить ресурс на указанных условиях | access probe |
| `CP03-LICENSE` | Статус лицензирования указан | license/status record |
| `CP03-USED` | Перечислены использующие КИМ | reverse references |
| `CP03-FALLBACK` | Критический внешний ресурс имеет fallback или blocker | fallback/blocker evidence |
| `CP03-NO-GHOST` | Пустой/отсутствующий объект не заявлен доступным | inventory report |

## 5. `FOS-CP-04` — Чистый запуск

| ID | Проверка | Доказательство |
|---|---|---|
| `CP04-CLEAN` | Использовано новое окружение | image/build id |
| `CP04-CMD` | Команды взяты из публикации без скрытых шагов | run transcript |
| `CP04-HW` | CPU/GPU/RAM/OS и duration записаны | run metadata |
| `CP04-SEED` | Seeds, повторы и допуски заданы | experiment manifest |
| `CP04-LAB` | Пройдены лабораторные M2 и M5 или обоснованная эквивалентная пара разных типов | result reports |
| `CP04-EXAM` | Пройден экзаменационный end-to-end сценарий | result report |
| `CP04-FAIL` | Проверен хотя бы один отказный сценарий на задание | fault result |
| `CP04-NOMANUAL` | Ручные исправления отсутствуют или возвращены в setup | issue/change ref |

## 6. `FOS-CP-05` — Техническая корректность LLM-МАС

| ID | Проверка | Доказательство |
|---|---|---|
| `CP05-BOUNDARY` | A2A и MCP применяются на разных границах | architecture + contract tests |
| `CP05-DISCOVERY` | Capability проверяется до делегирования | discovery negative test |
| `CP05-TASK` | Task states, cancel, retry и artifact различимы | lifecycle tests |
| `CP05-AUTH` | Identity, delegation и authorization разделены | auth tests/policy records |
| `CP05-RISK` | Высокорисковое действие имеет gate/stop | risk scenario |
| `CP05-PROV` | Task, tool, model/policy и result коррелируются | trace/provenance artifact |
| `CP05-E2E` | Есть malicious/failure end-to-end probe | evaluation result |
| `CP05-VERSION` | Stable/RC/PAR статусы не смешаны | source/version manifest |

## 7. `FOS-CP-06` — Публикационная готовность

| ID | Проверка | Доказательство |
|---|---|---|
| `CP06-OWNER` | Назначен maintainer и escalation route | owner record |
| `CP06-COUNT` | Inventory подтверждает фактическое число КИМ и рубрик | generated inventory |
| `CP06-LINKS` | Внутренние и внешние ссылки проверены | link report |
| `CP06-TOC` | Длинные документы имеют навигацию | document check |
| `CP06-TEMPLATES` | Опубликованы student repo/report, experiment log, ведомости и протоколы | direct paths |
| `CP06-LICENSE` | Юридический статус лицензии подтвержден или явно pending | status + approver |
| `CP06-LIMITS` | Release сообщает известные ограничения | release note |

## 8. Правила агрегирования

- Профиль проходит только при `pass` всех обязательных строк.
- `blocked` не превращается в `pass` через высокий общий балл.
- Результаты разных профилей не усредняются.
- Готовность к пилоту может опираться на `FOS-CP-01`–`04`.
- Готовность модуля 6 дополнительно требует `FOS-CP-05`.
- Готовность к тиражированию дополнительно требует `FOS-CP-06` и назначенных
  владельцев.
