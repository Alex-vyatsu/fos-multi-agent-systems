# Проверка доступности внешних URL — 2026-08-06

Проверка выполнена `RESOURCE_OWNER` (команда № 53) методом HTTP HEAD/GET с
таймаутом 15–20 с. Локальные ресурсы из
[`resource-manifest.csv`](../data/resource-manifest.csv) считаются подтверждёнными
наличием файлов в репозитории.

## Итог

| Категория | Результат |
|---|---|
| Проверено внешних URL | 42 |
| Доступны (HTTP 200 / устойчивый ответ) | 40 |
| Исправлены в карточках | 2 |
| Остаются недоступными | 0 |

## Исправления по итогам проверки

| Было | Стало | Причина |
|---|---|---|
| `http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/` | `https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/` | HTTP-эндпоинт нестабилен; HTTPS отвечает 200 |
| `https://pettingzoo.farama.org/environments/mpe/` | `https://pettingzoo.farama.org/` + путь пакета в GitHub `Farama-Foundation/PettingZoo` (MPE) | страница `/environments/mpe/` возвращает 404 |

## Подтверждённые группы ссылок

- Учебники открытого доступа: marl-book.com, masfoundations.org, incompleteideas.net.
- arXiv-статьи модуля 5–6 (MADDPG, QMIX, VDN, PettingZoo, LLM-MAS survey, AutoGen, ReAct, Plan-and-Solve).
- Документация библиотек: NumPy, NetworkX, Matplotlib, Mesa, SPADE, Nashpy, Axelrod, PySwarms, Gymnasium, PettingZoo, Ray RLlib, AutoGen, LangGraph, MCP, OpenTelemetry.
- Спецификации A2A и MCP; Yandex AI Studio; Creative Commons legalcode/deed.
- Вспомогательные среды и курсы: NetLogo, Complexity Explorer, Hugging Face Deep RL Course, OpenAI Spinning Up.
- Репозитории бенчмарков: SMAC, Melting Pot.

## Регламент

Повторная проверка — перед каждым семестром по
[регламенту ресурсов](../resources/README.md#регламент-обновления). Отчёт
сохраняется рядом с предыдущими (`docs/link-check-ГГГГ-ММ-ДД.md`).
