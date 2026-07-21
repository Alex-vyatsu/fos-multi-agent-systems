# Научные статьи

Публикации обеспечивают модули 4–6 и исследовательские записки (индикатор **FC-3.3**): обучающийся воспроизводит и анализирует результаты актуальных исследований МАС. Список ниже — опорный минимум; для [исследовательских записок](../../M5-marl/kim-03-research-note.md) обучающийся самостоятельно подбирает публикации в журналах 1 уровня Белого списка и на конференциях уровня A*/A (см. требования в РПД §5, СРС 4–6).

## Классические работы (основания методов)

| Название | Аннотация | Связанные КИМ | Доступ | Лицензия / условия | Дата проверки |
|---|---|---|---|---|---|
| Smith R. G. **The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver** // IEEE Transactions on Computers. — 1980. — Vol. C-29, № 12 | Первоисточник протокола Contract Net: анонс задачи, торги, назначение подрядчика. Читается при подготовке ЛР 2.1 и вопросов рубежного контроля 1 | [КИМ-2.1](../../M2-coordination/kim-01-practical-work.md), [КИМ-РК1.1](../../Midterm-1/kim-01-control-work.md) | DOI: 10.1109/TC.1980.1675516 (ЭБС / IEEE Xplore) | По условиям издателя | 2026-07-21 |
| Kennedy J., Eberhart R. **Particle Swarm Optimization** // Proceedings of ICNN'95. — 1995 | Первоисточник метода роя частиц: социальная модель поиска, параметры инерции и притяжения | [КИМ-4.1](../../M4-swarm-intelligence/kim-01-practical-work.md) | DOI: 10.1109/ICNN.1995.488968 | По условиям издателя | 2026-07-21 |
| Dorigo M., Maniezzo V., Colorni A. **Ant System: Optimization by a Colony of Cooperating Agents** // IEEE Transactions on Systems, Man, and Cybernetics, Part B. — 1996. — Vol. 26, № 1 | Первоисточник муравьиных алгоритмов: феромонные следы, испарение, применение к задачам на графах | [КИМ-4.1](../../M4-swarm-intelligence/kim-01-practical-work.md), [КИМ-4.3](../../M4-swarm-intelligence/kim-03-research-note.md) | DOI: 10.1109/3477.484436 | По условиям издателя | 2026-07-21 |

## Алгоритмы MARL

| Название | Аннотация | Связанные КИМ | Доступ | Лицензия / условия | Дата проверки |
|---|---|---|---|---|---|
| Lowe R. et al. **Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments (MADDPG)** // NeurIPS 2017 | Централизованный критик и децентрализованные акторы для смешанных сценариев; опорная статья по CTDE | [КИМ-5.1](../../M5-marl/kim-01-practical-work.md), [КИМ-5.3](../../M5-marl/kim-03-research-note.md), [КИМ-РК2.1](../../Midterm-2/kim-01-control-work.md) | <https://arxiv.org/abs/1706.02275> | arXiv, открытый доступ | 2026-07-21 |
| Rashid T. et al. **QMIX: Monotonic Value Function Factorisation for Deep Multi-Agent Reinforcement Learning** // ICML 2018 | Монотонная декомпозиция функции ценности для кооперативных задач; сравнивается с VDN и IQL в ЛР 5.1 | [КИМ-5.1](../../M5-marl/kim-01-practical-work.md), [КИМ-РК2.1](../../Midterm-2/kim-01-control-work.md) | <https://arxiv.org/abs/1803.11485> | arXiv, открытый доступ | 2026-07-21 |
| Sunehag P. et al. **Value-Decomposition Networks For Cooperative Multi-Agent Learning (VDN)** // 2017 | Аддитивная декомпозиция командной функции ценности; базовая точка сравнения для QMIX | [КИМ-5.1](../../M5-marl/kim-01-practical-work.md), [КИМ-5.2](../../M5-marl/kim-02-test.md) | <https://arxiv.org/abs/1706.05296> | arXiv, открытый доступ | 2026-07-21 |
| Terry J. K. et al. **PettingZoo: Gym for Multi-Agent Reinforcement Learning** // NeurIPS 2021 | Описание API и сред PettingZoo, используемых в ЛР 5.1 и в экзаменационном практическом задании | [КИМ-5.1](../../M5-marl/kim-01-practical-work.md), [КИМ-Э.2](../../Exam/kim-02-practical-task.md) | <https://arxiv.org/abs/2009.14471> | arXiv, открытый доступ | 2026-07-21 |

## Мультиагентные LLM-системы

| Название | Аннотация | Связанные КИМ | Доступ | Лицензия / условия | Дата проверки |
|---|---|---|---|---|---|
| Guo T. et al. **Large Language Model based Multi-Agents: A Survey of Progress and Challenges** // IJCAI 2024 | Обзор архитектур, паттернов взаимодействия и открытых проблем LLM-МАС; основа обзорной записки модуля 6 | [КИМ-6.3](../../M6-llm-mas/kim-03-research-note.md), [КИМ-6.2](../../M6-llm-mas/kim-02-test.md) | <https://arxiv.org/abs/2402.01680> | arXiv, открытый доступ | 2026-07-21 |
| Wu Q. et al. **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation** // 2023 | Фреймворк мультиагентных диалогов «оркестратор + специализированные агенты»; используется как образец архитектуры в ЛР 6.1 | [КИМ-6.1](../../M6-llm-mas/kim-01-practical-work.md) | <https://arxiv.org/abs/2308.08155> | arXiv, открытый доступ | 2026-07-21 |
| Yao S. et al. **ReAct: Synergizing Reasoning and Acting in Language Models** // ICLR 2023 | Паттерн рассуждения с чередованием шагов размышления и действий; проверяется в ЛР 6.1 и на экзамене | [КИМ-6.1](../../M6-llm-mas/kim-01-practical-work.md), [КИМ-Э.1](../../Exam/kim-01-theory.md) | <https://arxiv.org/abs/2210.03629> | arXiv, открытый доступ | 2026-07-21 |
| Wang L. et al. **Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models** // ACL 2023 | Паттерн «сначала план, затем исполнение»; сопоставляется с ReAct при выборе паттерна агента | [КИМ-6.1](../../M6-llm-mas/kim-01-practical-work.md), [КИМ-6.2](../../M6-llm-mas/kim-02-test.md) | <https://arxiv.org/abs/2305.04091> | arXiv, открытый доступ | 2026-07-21 |

## Требования к добавлению

- Приводите DOI или устойчивую ссылку (arXiv, издательство), полное описание и пояснение, для какого результата обучения используется публикация.
- Для исследовательских записок засчитываются публикации журналов 1 уровня Белого списка и конференций уровня A*/A; препринт без рецензирования допускается как дополнительный источник, но не как единственный.
- Предпочтительны работы с доступным кодом и данными — это делает возможным воспроизведение результата, требуемое рубрикой записки.
- При добавлении статьи, вокруг которой строится задание, отдельно фиксируйте, какой её результат подлежит воспроизведению и в каком упрощённом масштабе.
