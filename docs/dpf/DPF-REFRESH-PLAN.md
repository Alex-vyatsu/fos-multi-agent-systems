# План обновления рамок

**Идентификатор:** `MAS-DPF-REFRESH-001`  
**Редакция:** `0.2.0`  
**Дата:** 2026-07-27  
**Статус:** план; выполнение и результаты еще не заявлены

## 1. Объекты текущести

| ID | Объект | Вид текущести | Основание версии | Минимальная область изменения |
|---|---|---|---|---|
| `CUR-01` | Технический source pack | Стандарты и спецификации | Дата среза + версии источников | Одна source row, связанные claims и паттерны |
| `CUR-02` | Техническая рамка | Архитектурные решения | Edition `0.1.0` | Один паттерн и его отношения |
| `CUR-03` | Source pack ФОС | Состояние репозитория и рецензии | Git snapshot + review snapshot | Одно утверждение и связанный ремонт |
| `CUR-04` | Прикладная рамка ФОС | Учебная практика | Edition `0.2.0` | Один паттерн, КИМ или профиль |
| `CUR-05` | Словарь | Смысл терминов | Edition `0.2.0` | Одна строка и использующие ее документы |
| `CUR-06` | Оценка пакета | Доказательная база | Qualification window | Координаты, затронутые новым evidence |

## 2. Очередь триггеров

| Приоритет | Триггер | Затронуто | Планируемое действие | Требуемый результат |
|---:|---|---|---|---|
| 1 | Финальный MCP после `2025-11-25` | `CUR-01`, `CUR-02`, КИМ модуля 6 | Сравнить изменения, обновить contract profile, выполнить replay | Migration report и решение о новой edition |
| 1 | Security/safety incident или ложная приемка | Связанный паттерн и КИМ | Root-cause, новый negative case, regression test | Incident-linked refresh report |
| 1 | Изменение КРМ или РПД | `CUR-03`, `CUR-04` | Повторить атомарную трассировку индикаторов | Новая measurement matrix и migration note |
| 2 | Изменение `main` исходного ФОС | `CUR-03`, `CUR-04`, `CUR-06` | Повторить инвентаризацию файлов, ссылок, ресурсов и закрытых замечаний | Repository delta report |
| 2 | Первый clean run | `CUR-04`, `CUR-06` | Зафиксировать environment, duration, hardware и failures | Pilot report и regression assets |
| 2 | Новая стабильная A2A | `CUR-01`, `CUR-02`, модуль 6 | Contract diff, Agent Card/auth/task replay | Compatibility decision |
| 3 | Новая утвержденная IEEE agent standard | Watchlist и связанный паттерн | Перевести из watchlist после анализа | Source-use decision |
| 3 | Повторяющаяся ошибка читателя/студента | Один паттерн/КИМ | Уточнить первый шаг, пример или blocked reading | Локальная новая редакция |
| 3 | Broken external URL или недоступный ресурс | Resource row и КИМ | Исправить URL или включить fallback | Link/resource availability report |
| 3 | Изменение лицензии или владельца | Публикационный контур | Юридическая/организационная проверка | Updated notice и owner record |

## 3. Роли

До назначения конкретных лиц используются роли:

- `FRAMEWORK_STEWARD` — принимает edition и локализует пересмотр;
- `TECHNICAL_STANDARDS_OWNER` — проверяет A2A/MCP/FIPA/IEEE/NIST/ISO;
- `FOS_MAINTAINER` — отвечает за структуру ФОС, КИМ и публикацию;
- `MEASUREMENT_OWNER` — сверяет КРМ, РПД, индикаторы и рубрики;
- `REPRODUCIBILITY_OWNER` — выполняет clean run и хранит отчет;
- `SECURITY_GOVERNANCE_OWNER` — полномочия, риск, лицензия и incident route.

Отсутствие назначенного `FOS_MAINTAINER` блокирует заявление о готовности ФОС к
тиражированию, но не блокирует локальную разработку материалов.

## 4. Протокол выполнения

1. Записать точный trigger и affected object.
2. Определить минимальную зависимую область; глобальный пересмотр допускается
   только с объяснением полной зависимости.
3. Выполнить действие у прямого владельца: source review, contract diff,
   measurement rebuild, clean run или publication repair.
4. Запустить соответствующие regression checks.
5. Выпустить отчет: выполненные действия, наблюдаемые изменения, затронутые
   версии, нерешенные ограничения, deprecation/migration.
6. Обновить оценку только по фактическим доказательствам.

## 5. Форма отчета

```text
Refresh report:
  id:
  trigger:
  affected objects:
  previous editions:
  executed actions:
  evidence:
  regression results:
  changed claims/patterns/resources:
  unchanged dependent objects and reason:
  deprecations or migrations:
  remaining limits:
  new qualification window:
```

План не считается отчетом, а запланированный тест — пройденным тестом.
