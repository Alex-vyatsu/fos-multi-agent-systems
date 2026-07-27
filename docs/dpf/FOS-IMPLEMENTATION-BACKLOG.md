# Backlog доработки ФОС «Мультиагентные системы»

**Редакция:** `0.2.0`  
**Источник:** замечания команды 53  
**Статус:** план; задачи не считаются выполненными

## Правила

- Приоритет задается риском для запуска и измерения, а не простотой правки.
- `Done` допустим только со ссылкой на приемочное доказательство.
- Роль — не назначенный человек; до назначения владельца соответствующий
  release-gate остается заблокированным.

## Волна 1 — воспроизводимый минимум

| ID | Задача | Роль | Зависимость | Приемка |
|---|---|---|---|---|
| `BL-101` | Добавить lock/environment и Docker recipe | `REPRODUCIBILITY_OWNER` | Решение по поддерживаемым Python/OS | `CP01-ENV`, `CP04-CLEAN` |
| `BL-102` | Baseline и smoke test модуля 1 | `M1_OWNER` | `BL-101` | `FOS-CP-01` |
| `BL-103` | Baseline и generator потока заявок модуля 2 | `M2_OWNER` | `BL-101` | `FOS-CP-01` |
| `BL-104` | Baseline модуля 4 | `M4_OWNER` | `BL-101` | `FOS-CP-01` |
| `BL-105` | PettingZoo/MARL baseline модуля 5 | `M5_OWNER` | `BL-101`, resource profile | `FOS-CP-01`, `FOS-CP-04` |
| `BL-106` | A2A/MCP baseline и negative tests модуля 6 | `M6_OWNER` | `BL-101`, technical source pins | `FOS-CP-05` |
| `BL-107` | Малый synthetic dataset | `DATA_OWNER` | Схема двух выбранных КИМ | `CP01-DATA`, license record |
| `BL-108` | Experiment log template | `MEASUREMENT_OWNER` | Evidence requirements | Direct template + filled example |
| `BL-109` | Student repository и report templates | `FOS_MAINTAINER` | КИМ format | Direct templates + README route |
| `BL-110` | Удалить ложные ссылки на пустые attachments или заполнить их | `FOS_MAINTAINER` | Inventory | `CP03-NO-GHOST` |
| `BL-111` | Назначить сопровождающего и заместителя | Организация | Management decision | `CP06-OWNER` |
| `BL-112` | Ввести проверку внешних URL и версий | `RESOURCE_OWNER` | Resource manifest | Dated link/version report |

## Волна 2 — атомарная модель измерения

| ID | Задача | Роль | Зависимость | Приемка |
|---|---|---|---|---|
| `BL-201` | Собрать atomic measurement matrix | `MEASUREMENT_OWNER` | КРМ, РПД, все КИМ | `FOS-CP-02` |
| `BL-202` | Исправить уровень O-2.3 | `MEASUREMENT_OWNER` | `BL-201` | Exact KRM level |
| `BL-203` | Исправить представление FC-3.3 | `MEASUREMENT_OWNER` | `BL-201` | Separate atomic row |
| `BL-204` | Разделить KRM wording и subject descriptor | `MEASUREMENT_OWNER` | `BL-201` | `CP02-KRM`, `CP02-DESC` |
| `BL-205` | Заменить общие resource links прямыми | `RESOURCE_OWNER` | Resource manifest | `FOS-CP-03` |
| `BL-206` | Явно показать существующее решение по контролю LLM-4 | `RPD_OWNER` | Measurement gap review | Текущий контроль + экзамен; изменение только через пересмотр РПД |
| `BL-207` | Вывести существующие НИРС/практику/ВКР из РПД в корневую навигацию | `RPD_OWNER` | Existing RPD rows | Direct links; вне 100-балльной системы |

## Волна 3 — публикация

| ID | Задача | Роль | Зависимость | Приемка |
|---|---|---|---|---|
| `BL-301` | Проверить owner record перед выпуском | `FOS_MAINTAINER` | `BL-111` | Owner, channel, cadence, deputy |
| `BL-302` | Генерировать inventory КИМ/rubric | `FOS_MAINTAINER` | Repository rules | Actual counts; old claim removed |
| `BL-303` | Включить external URL/version check в release gate | `RESOURCE_OWNER` | `BL-112` | Repeated link/version report |
| `BL-304` | Добавить ToC в длинные документы | Document owners | Length threshold | Navigation check |
| `BL-305` | Добавить ведомости и протоколы | `FOS_MAINTAINER` | Local university forms | Direct templates |
| `BL-306` | Проверить license text | `LEGAL_APPROVER` | Organizational authority | Approved/pending record |

## Волна 4 — пилот

| ID | Задача | Роль | Зависимость | Приемка |
|---|---|---|---|---|
| `BL-401` | Clean run лабораторной модуля 2 | `REPRODUCIBILITY_OWNER` | Волна 1 | `FOS-CP-04` relevant rows |
| `BL-402` | Clean run лабораторной модуля 5 | `REPRODUCIBILITY_OWNER` | `BL-105` | `FOS-CP-04` |
| `BL-403` | Clean run экзаменационного задания | `REPRODUCIBILITY_OWNER` | Templates + baselines | `CP04-EXAM` |
| `BL-404` | Измерить hardware/time/quota profiles | `RESOURCE_OWNER` | `BL-401..403` | Three profiles with measured limits |
| `BL-405` | Зафиксировать метрики и предел переноса | `MEASUREMENT_OWNER` | Run reports | Non-aggregated evaluation record |
| `BL-406` | Выпустить pilot refresh report | `FOS_MAINTAINER` | `BL-401..405` | Refresh report form |

## Вне полномочий этой рамки

- назначение конкретных сотрудников;
- утверждение РПД или изменение КРМ;
- юридическое заключение;
- предоставление GPU/LLM квот;
- публикация закрытых банков заданий.

Эти пункты должны иметь внешнее решение, а не автоматически считаться
выполненными текстом backlog.
