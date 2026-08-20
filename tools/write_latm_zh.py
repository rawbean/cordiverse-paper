#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write LATM per-page zh + plain JSON (page-aligned)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "papers" / "cited-harness" / "latm" / "artifacts"

# (zh, plain) for pages 1..23
PAGES: list[tuple[str, str]] = [
    (
        """发表于 ICLR 2024
大语言模型作为工具制造者
Tianle Cai1,2∗  Xuezhi Wang1  Tengyu Ma1,3†  Xinyun Chen1  Denny Zhou1
1Google Deepmind  2Princeton University  3Stanford University
摘要
近期研究指出，大语言模型（LLM）在合适的外部工具辅助下，解题能力可以显著增强。我们把这一思路再推进一步，提出闭环框架 LATM（LLMs As Tool Makers，大语言模型作为工具制造者）：由 LLM 为自己制造可复用的解题工具。方法分两阶段：1）工具制造：一个 LLM 充当工具制造者，为一类任务写出工具，工具实现为 Python 工具函数；2）工具使用：另一个 LLM 充当工具使用者，调用制造者造好的工具来解题。工具使用者可以与制造者是同一模型，也可以不同。在解题服务端，工具制造使系统能随着新请求不断生成并缓存工具。后续请求可通过对应 API 访问已缓存工具，从而提高解题效率。除了让 LLM 自造工具，该框架还揭示了优化 LLM 服务成本的机会：工具制造需要更强能力，因此交给强大但昂贵的模型；相对简单的工具使用则交给轻量模型。这种分工让一次性的制造成本摊到多次使用上，在保持性能的同时显著降低平均成本。此外，通过缓存并复用工具，我们得到一种功能缓存：它存储的是一类请求的功能，而不是 LLM 的自然语言回答，从而扩展了传统缓存的适用范围。我们在多种复杂推理任务（含 Big-Bench）上评估。以 GPT-4 为工具制造者、GPT-3.5 为工具使用者时，LATM 的表现与两角色都用 GPT-4 相当，但推理成本显著更低。代码见 https://github.com/ctlllll/LLM-ToolMaker。
引言
大语言模型已在广泛的 NLP 任务上展现出色能力 [Brown et al., 2020; Chowdhery et al., 2022; Zhang et al., 2022; Hoffmann et al., 2022; OpenAI, 2023; Google, 2023]，甚至在某些方面呈现出通向通用人工智能的迹象 [Bubeck et al., 2023; Kosinski, 2023]。与人类智能的演化类似，近期研究揭示了用外部工具增强 LLM 的潜力，从而显著提高解题能力与效率 [Yao et al., 2023; Liu et al., 2023; Parisi et al., 2022; Schick et al., 2023]。
然而，这些工具使用方法的适用性很大程度上取决于是否已有合适工具。从人类演化的经验看，一个关键转折是人类获得了为自己制造工具以应对新挑战的能力。受人类工具制造重要性的启发，本文对把这一演化概念用于 LLM 做初步探索。我们提出闭环框架 LATM，使 LLM 能生成自己的可复用工具来应对新任务。方法包含两个关键阶段：1）工具制造：一个 LLM，
∗在 Google Deepmind 任学生研究员期间完成。
†在 Google Deepmind 任访问研究员期间完成。
arXiv:2305.17126v2 [cs.LG] 11 Mar 2024
""",
        "封面页：论文名是「大语言模型作为工具制造者」（LATM）。核心不是再给模型接一个现成计算器，而是让模型自己写出可复用的 Python 函数。贵模型负责一次性造工具，便宜模型负责反复调用，所以平均成本能降下来。缓存的也不是「这句问过、原样再答」，而是「这类题有一个函数」。像工厂里师傅先做模具，学徒用模具量产。",
    ),
    (
        """发表于 ICLR 2024
图 1：LATM 的闭环框架。面对大量解题请求时，直接用强大 LLM 解所有实例成本很高；轻量模型便宜，但复杂任务上往往吃力。LATM 取两者之长：用强大模型当工具制造者，为请求中观察到的任务生成可复用工具（实现为 Python 函数），再把工具交给成本更低的工具使用者模型，去解后续相似实例。这样轻量模型可以达到与强大模型相当的表现，同时更省成本。
称为工具制造者，为给定任务设计工具（实现为 Python 函数）。2）工具使用：另一个称为工具使用者的 LLM（可以与制造者相同）用这些工具处理新请求。两阶段设计使 LATM 能把各阶段任务分配给最合适的 LLM。具体而言，需要高能力的工具制造可交给强大但昂贵的模型（如 GPT-4）；相对简单的工具使用可交给轻量、便宜的模型（如 GPT-3.5 Turbo）。这既增强 LLM 的解题能力，也显著降低处理一系列任务的平均计算成本。
工具制造对给定功能只需执行一次，得到的工具可在不同任务实例间复用。这为处理复杂任务铺出可扩展、省成本的路。例如，用户让 LLM 安排一个所有人都方便的会议（如在邮件对话里）。GPT-3.5 Turbo 这类轻量模型常常在涉及复杂算术推理的任务上挣扎；更强的模型（如 GPT-4）能找到正确解，但推理贵得多。LATM 用昂贵的强模型当制造者，再把工具交给便宜模型当使用者。工具锻造完成后，轻量使用者就能高效、高性能地解题。类似范式也适用于各种工作流中的重复任务：把网页解析成特定数据格式、按多项自定义约束做路径规划，或用来解 24 点、数独等常见游戏。
在降低服务成本方面，LATM 为 LLM 服务器引入了功能缓存的可能。考虑流式设定：服务器持续收到一串请求。传统缓存如 GPTCache [Zilliz, 2023] 存储 LLM 生成的回答，并在文本相似的请求上复用。有了 LATM 的造工具能力，系统可以存储制造者造出的工具，并在功能类似的请求上复用。这一新做法，再加上制造者与使用者的分工，有望在保持高性能的同时，大幅降低服务一串请求的平均成本。
""",
        "本页用图 1 把闭环画清楚：强模型不当「每道题都亲自算」的劳工，而当「做模具的师傅」。约会议、解析网页、24 点这类会反复出现的活，最适合摊模具成本。和 GPTCache 的差别像「存一份标准答案」对「存一把螺丝刀」——数字一变，标准答案废了，螺丝刀还能用。",
    ),
    (
        """发表于 ICLR 2024
实验在一系列复杂推理任务上验证了该方法，包括若干有挑战的 Big-Bench 任务 [Srivastava et al., 2022]。结果表明 LATM 能达到与更昂贵模型相当的性能，同时更省成本。这种模仿人类在创造与使用工具上进化跨越的 LLM 路径，为不断增长的、由 LLM 生成工具的社区打开了新可能。
相关工作
思维链（CoT）。
近期在增强 LLM 解复杂任务能力上进展显著。例如 CoT 提示 [Wei et al., 2022; Wang et al., 2022] 被用来加强推理，在多种推理与 NLP 任务上表现更好。CoT 通常用自然语言表达 [Ling et al., 2017; Cobbe et al., 2021; Suzgun et al., 2022; Shi et al., 2022; Zhou et al., 2022]，也可以有效地用程序语言表示 [Amini et al., 2019; Austin et al., 2021; Nye et al., 2021; Chowdhery et al., 2022; Gao et al., 2023; Chen et al., 2022]。最近 Arora et al. (2023) 提出用 LLM 为文档生成结构化视图，通过集成多个合成函数的抽取结果来平衡质量与成本。我们的方法在管理成本–质量权衡上与之精神相近，但关注更一般的用例。
用工具增强语言模型。
近期工作探索用外部工具补充 LLM 解复杂任务的能力。Yao et al. (2023); Yang et al. (2023) 提出在推理轨迹中加入任务特定动作，使模型能协同推理与行动。多项研究 [Liu et al., 2023; Parisi et al., 2022; Schick et al., 2023; Shen et al., 2023; Lu et al., 2023; Paranjape et al., 2023; Liang et al., 2023] 表明，给 LLM 配上计算器、搜索引擎、翻译、日历、甚至对其它模型的 API 调用，有助于解决单靠 LLM 不易处理的任务。与 LATM 类似，Chameleon [Lu et al., 2023] 等也在流水线中纳入 Python 执行器。但它们的重点是用执行器准确完成涉及算术推理的子步骤，类似于 Gao et al. (2023); Chen et al. (2022)。相比之下，我们用 Python 执行器来创造可复用工具，以应对其它任务实例。此外，制造者与使用者的分离使大多数推理能用轻量模型，从而提高 LATM 的效率与成本效益。
语言模型中的自适应生成。
此外，近期研究提出自适应控制 LLM 解码以提高生成效率 [Leviathan et al., 2022; Chen et al., 2023a; Xia et al., 2023]。投机解码的想法是：生成文本词元（更贵）可以用更快但较弱的模型加速，同时用更大、更贵的模型给已生成词元打分（快得多），以逼近大模型表现。我们把工具从更贵模型传给更小、更快模型，也带有自适应计算的精神。我们不改解码过程，而是在模型间传递新生成的工具，以同时提升解题性能与效率。
语言模型级联。
有证据表明 LLM 能支持反复交互，多个 LLM 组合可进一步扩展能力 [Wu et al., 2022; Zhou et al., 2022; Dohan et al., 2022; Chen et al., 2023c]。Chen et al. (2023b) 还表明，找出最优 LLM 组合有助于降本并提高准确率。我们的动机与这些发现一致；但我们不是仅仅级联 LLM，而是识别出那些用大模型新造的工具能更好处理的任务类别，并把该类别内的每一次推理交给小模型。
造工具的早期尝试。
与我们同期且独立，已有若干用 LLM 造工具的早期尝试。Wang et al. (2023) 在 Minecraft 环境中表明，由 LLM 驱动的智能体可以以程序形式获得新技能。类似地，Qian et al. (2023) 提出把每个实例的解题分解为抽象的工具创造阶段与具体的工具
""",
        "本页把 LATM 放进文献坐标：思维链是「把推理写出来」；工具增强是「接上已有 API」；投机解码是「解码时大小模型配合」。LATM 的差别是：Python 不是用来算一步算术，而是用来留下以后还能用的函数。像不是请人每次口算，而是请人写一个以后谁都能跑的小程序。同期 Voyager、CREATOR 也在造工具，作者强调自己还多了可复用与成本分工。",
    ),
    (
        """发表于 ICLR 2024
应用阶段。我们的工作与 Wang et al. (2023) 及 Qian et al. (2023) 在「让 LLM 自造工具来解题」上精神一致。但我们也强调工具可复用性，以及来自分工的成本效益。造工具的想法在近期综述中也被提及 [Qin et al., 2023]。
大语言模型作为工具制造者（LATM）
图 2：LATM 流水线。可分为两阶段：1）工具制造：强大但更贵的模型当工具制造者，从少量示范生成通用、可复用的工具；2）工具使用：轻量、更便宜的模型当工具使用者，用该工具解该任务的各种实例。工具制造可再分为三个子阶段：（i）工具提出：制造者尝试从少量训练示范生成工具（Python 函数）；若不可执行，报告错误并再生成（修复函数）；（ii）工具验证：制造者在验证样本上跑单元测试；若未通过，报告错误并生成新测试（修复单元测试中的函数调用）；（iii）工具封装：把函数代码以及如何把问句转成函数调用的示范（来自单元测试）包起来，为使用者准备可用工具。
3.1 制造新工具并复用它们
在 LATM 范式中，主过程可分为两阶段：工具制造与工具使用。各阶段使用不同类型的大语言模型，以平衡性能与成本。实验中用到的全部提示见附录 C。
工具制造。
本阶段用强大但更贵的模型（如 GPT-4）充当工具制造者。其职责是从任务的少量示范创造出通用、可复用的工具（实现为 Python 函数）。本阶段可再分为三个子阶段：
• 工具提出：制造者尝试生成一个 Python 函数来解给定任务的示范。该过程遵循「按范例编程」（PbE）
""",
        "方法开篇。图 2 是全文最重要的一张图：造工具不是一次灵感，而是提出 → 验证 → 封装三步。注意验证失败时，作者规定只改单元测试里的「怎么调用」，不改函数本身——有点像质检员核对说明书，而不是回车间改模具。读到这里先记住三步，后面实验会反复用到。",
    ),
    (
        """发表于 ICLR 2024
范式 [Halbert, 1984]：给出若干具体示范，要求模型写出能产生所示行为的程序。实验中本阶段用 3 个示范。若提出的工具不可执行或出错，制造者把报错追加到历史中再试一次。
• 工具验证：制造者利用验证样本生成单元测试，并在提出的工具上执行。实验用 3 个验证样本。若工具未通过任一测试，制造者把错误记入历史，并尝试修正单元测试中的问题（此过程只纠正单元测试部分的函数调用，不纠正函数本身）。LLM 的自调试能力已在近期研究中得到有效展示 [Madaan et al., 2023; Chen et al., 2023c; Lu et al., 2023; Kim et al., 2023]。但在 LATM 流水线里，验证阶段用法略有不同。它承担两个关键角色：1）提供如何把自然语言问句转成函数调用的范例；2）核实工具可靠性，使全流程能完全自动化。
• 工具封装：若执行或验证失败超过预设阈值，则视工具制造失败。否则制造者准备封装好的工具给使用者。这一步把函数代码包起来，并提供如何把任务转成函数调用的示范。这些示范从工具验证步抽出——验证步本就把问句转成了单元测试。最终产品即可供工具使用者使用。封装工具的例子见附录 D。
工具使用。
第二阶段用轻量、便宜的模型（如 GPT-3.5 Turbo）充当工具使用者。其职责是用已验证的工具解该任务的各种实例。本阶段的提示就是封装工具：包含解题函数，以及如何把任务查询转成函数调用的示范。有了示范，使用者即可用上下文学习生成所需调用，再执行这些调用解题。可选地，可做后处理，把输出转成任务要求的格式，例如选择题的选项。
工具制造（含提出、验证、封装）对每一类任务只需做一次。得到的工具可复用于该类任务的全部实例。因此 LATM 比单独使用强大模型显著更高效、更省成本。此外，Python 函数工具是一种更通用的思维链形式，增强了 LLM 的整体效用与灵活性，因为它们可用来解需要算法推理能力的问题 [Veličković and Blundell, 2021]。
LATM 为 LLM 服务培育功能缓存机制
在真实场景中，任务常常以顺序流到达。为此我们引入第三个 LLM——调度器，决定每个到来的任务该启用工具使用者还是工具制造者。这一工具选择功能与已有工作类似 [Lu et al., 2023; Shen et al., 2023; Schick et al., 2023; Paranjape et al., 2023]，但我们的调度器特别贡献在于形成功能缓存——它识别出无法用现有工具解决的新任务，从而触发制造者为这些任务生成合适工具。
调度器以函数 API 的形式维护制造者已造工具的仓库。收到新任务实例时，调度器先尝试在缓存中定位兼容工具。若有，就把实例与对应工具交给使用者求解。若没有合适工具，调度器将其识别为新任务，或用强大模型求解，或必要时请人类标注。这些新实例会被缓存，直到攒够数量以制造新工具，进一步丰富功能缓存。该机制使功能相似的任务能复用这些工具，扩大了经典缓存的覆盖，并降低总体服务成本。由于调度任务本身简单，配备合适提示（见附录 C）的轻量模型就能高效充当调度器，给整条流水线只增加边际成本。
""",
        "本页把三步写严，并引出第三个角色：调度器。可以把它想成图书馆前台：来了一本书，先看架上有没有同类工具；没有就登记「新书目」，攒几本再送去装订成新工具。验证步表面上是「测函数对不对」，作者更看重它顺便产出「人话怎么变成参数」的说明书，好让便宜模型照着抄。",
    ),
    (
        """发表于 ICLR 2024
图 3：LATM 流水线在逻辑演绎任务 [Srivastava et al., 2022] 上的工具提出与工具使用示意。该任务要根据若干给定条件确定五个物体的顺序。在工具提出阶段，工具制造者（如 GPT-4）从该任务提供的 k 个示范（实验中 k=3）出发，写出能解它们的通用 Python 函数。制造者生成一种搜索算法：枚举所有可能排序，并对照给定条件逐一验证。在工具使用阶段，使用者把每道自然语言题翻译成一组条件，生成函数调用，从而对每个任务实例使用该工具。
实验
5.1 实验设置
数据集。
我们在六个来自不同领域的数据集上评估：逻辑演绎、追踪被打乱的物体、Dyck 语言、单词排序、中国剩余定理、安排会议。前五个来自 BigBench [Srivastava et al., 2022]。逻辑演绎与追踪被打乱物体采用五物体版本，文中称为 Logical Deduction (5) 与 Tracking Shuffled Objects (5)。我们还自建了安排会议任务，以展示 LATM 在真实场景中的效果。数据集生成细节见附录 E。每个数据集划分为训练、验证、测试集，分别含 3、3、240 个实例。
模型设置。
工具制造阶段温度设为 0.3，为生成引入随机性，以便必要时重试。本阶段用 GPT-4 与 GPT-3.5 Turbo 的 ChatCompletion API 做实验，始终把回复追加到对话历史以形成交互。工具使用阶段只调用一次 LLM API，我们也对 GPT-3 系列用标准 Completion API 做了消融。使用工具时温度一律 0.0。工具提出与工具验证的最大重试次数设为 3。
5.2 工具制造阶段的有效性
在工具制造阶段，我们用强大但较慢的模型生成针对特定任务的通用 Python 函数。该步对每个任务只做一次，开销摊到该任务的全部实例上。实验中我们用 GPT-4 [OpenAI, 2023] 作为
""",
        "图 3 用「五个东西谁在谁左边」当例子：GPT-4 写的不是一道题的答案，而是「枚举所有排列再检查约束」的搜索函数；GPT-3.5 只需把题面译成约束列表。实验设置很瘦：每类任务 3 条训练、3 条验证、240 条测试。像先用 3 道例题请师傅写通解，再用 3 道验收，然后让学徒考 240 道。",
    ),
    (
        """发表于 ICLR 2024
逻辑演绎 (5)　追踪被打乱物体 (5)　Dyck 语言　单词排序　中国剩余定理　安排会议
搜索　模拟　栈　排序　搜索 / 扩展欧几里得　区间求交
表 1：工具制造者为解题生成的工具函数。
代表性工具制造者，其它模型的造工具能力在第 5.5 节探讨。我们为语言模型提供若干少样本示例，引导它生成通用 Python 程序，如图 3 所示。
我们观察到，当 GPT-4 充当制造者时，模型经常能想出合适的算法。例如表 1 所示，它为逻辑演绎写出枚举所有排列并选出满足约束的那一个。实验中，工具验证阶段主要用于提供「如何把自然语言问句转成函数调用」的范例；在 60 次试验里，我们只观察到 2 次制造者能在报错指引下纠正错误。关于制造者的更多讨论见第 5.5 节。
5.3 LATM 提升轻量 LLM 的性能
表 2 比较思维链提示 [Wei et al., 2022] 与我们的方法 LATM。我们用 GPT-4 为六个任务造工具，并分别评估 GPT-3.5 Turbo 与 GPT-4 作为工具使用者。结果表明：有了工具，像 GPT-3.5 Turbo 这样的轻量模型可以达到与 GPT-4 相当的表现，并显著优于 CoT 提示。此外，用带工具的 GPT-3.5 Turbo 的平均成本远低于用 GPT-4。这凸显了 LATM 在提升轻量模型性能、从而相对使用昂贵模型降低成本上的有效性。有趣的是，在 Dyck 语言任务上，GPT-3.5 Turbo 作为使用者甚至超过了作为使用者的 GPT-4。检查失败案例后发现：把问句转成函数调用时，GPT-4 偶尔会多余地在参数里先补上一些括号，而不是保持参数不变、让函数去解，从而导致函数输出错误。
工具使用者　模型　方法　逻辑演绎 (5)　追踪被打乱物体 (5)　Dyck 语言　单词排序　中国剩余定理　安排会议　n 个样本成本
GPT-3.5 Turbo　CoT　66.4　61.6　20.4　59.2　0.0　18.9　O(nc)
LATM　79.7 (+13.3)　99.6 (+38.0)　92.2 (+71.8)　98.3 (+39.1)　100.0 (+100.0)　100.0 (+81.1)　O(nc + C)
GPT-4　CoT　88.8　100.0　63.6　90.9　0.0　55.6　O(nC)
LATM　86.6　100.0　87.5　99.1　100.0　100.0　O(nC)
表 2：LATM 与思维链的准确率比较。六个任务详见第 5.1 节。LATM 中工具由 GPT-4 制造，由 GPT-3.5 Turbo 与 GPT-4 使用。结果表明 LATM 能显著提升 GPT-3.5 Turbo，在某些情形下超过或匹配 GPT-4 的 CoT。最后一列是处理 n 个样本的总体成本。C 表示一次 GPT-4 调用成本，c 表示一次 GPT-3.5 Turbo 调用成本。撰文时 C 比 c 大约 15 倍以上。前四个任务的少样本 CoT 示范来自 Suzgun et al. (2022)，后两个任务用无 CoT 的直接少样本提示。
5.4 将 LATM 适配到多样任务的动态流
如第 4 节所述，我们可以把 LATM 适配到动态流：来自潜在不同任务的实例实时出现。此时我们引入额外模型——调度器，负责识别每个到来实例所属的任务。我们
""",
        "本页是数字页。表 1 说明制造者真的在选算法：排列搜索、栈、排序、扩展欧几里得、区间求交。表 2 是核心证据：GPT-3.5 加上工具，中国剩余定理从 0% 到 100%，约会议从 19% 到 100%；成本从每题一次贵调用变成「摊一次贵的 + 每题一次便宜的」。有个反直觉细节：Dyck 语言上 GPT-4 当使用者反而更被，因为它爱抢先把括号补完。",
    ),
    (
        """发表于 ICLR 2024
工具制造者模型　逻辑演绎 (5)　追踪被打乱物体 (5)　Dyck 语言　单词排序　中国剩余定理　安排会议
GPT-3.5 Turbo　0/5　0/5　5/5　5/5　5/5　0/5
GPT-4　3/5　4/5　5/5　5/5　5/5　3/5
表 3：工具制造阶段用 GPT-4 与 GPT-3.5 Turbo 生成新工具（通过工具验证的 Python 函数）的成功率。每个模型在每个任务上跑 5 次试验，n/5 表示 5 次中有 n 次成功产出有效工具。对逻辑演绎、追踪被打乱物体等难题，GPT-3.5 Turbo 全部失败，说明有必要用更强模型当制造者。
检测未见过的任务并触发制造者为这些任务创造合适工具。该实验设置有助于评估系统如何在动态、多任务场景中通过复用与扩展功能缓存来降低服务成本。
识别已有工具。
评估的第一部分看调度器能否在功能缓存中认出与给定实例对应的已有工具，类似于传统缓存的读取阶段。为此我们生成 100 个样本的测试集，从第 5.1 节六个任务中随机混合。对每个实例，调度器要在已有工具中判定合适工具，提示里含这些工具关联的任务示例（见附录 C）。成功标准是正确识别工具。在五次随机构造的测试集上，正确判定合适工具的准确率为 95% ± 2%。
请求工具制造。
评估的第二部分测试调度器能否为来自未见任务的实例请求造工具。这类似于缓存未命中时把新实例入队。我们随机指定四个任务为已有工具的现成任务，另选四个任务做测试——其中两个未见，两个仍属已有任务。同样生成 100 个样本的测试集。对测试集中每个实例，调度器判定是需要请求造工具，还是已有工具就能解。多次运行中，正确决策的准确率为 96% ± 3%，表明该方法在高效管理功能缓存上的稳健性。
上述结果说明，调度器能有效识别已有工具，并准确为未见任务请求造工具，同时保持高性能。这些发现凸显 LATM 无缝适配涵盖多样任务的流式环境的潜力。该验证增强了框架在真实应用中的可行性，尤其是在功能缓存的高效管理至关重要之处。
5.5 消融研究
工具制造语言模型所需的能力。
我们考察工具制造阶段所用语言模型的能力要求（见表 3）。总体而言，更强、更贵的模型更胜任，因为该阶段对每个任务只做一次，高准确率对把工具有效交给小模型至关重要。具体地，在逻辑演绎、追踪被打乱物体等难题上，GPT-3.5 Turbo 五次试验全部失败。主要失败原因是工具不够通用，可能只在训练样本上成立。另一方面，对容易任务，制造者也可以是轻量模型。对单词排序这类简单任务，GPT-3.5 Turbo 能轻松生成解题程序。另一个可能导致制造者失败的限制是上下文长度。由于我们在造工具的每一步都使用全部历史以提高可靠性，上下文也会更长。此时具有 8192 上下文长度的 GPT-4 更可取。
工具使用语言模型所需的能力。
本节考察工具使用模型的能力要求。结果见表 4。我们观察到 GPT-3.5
""",
        "调度器在六任务混合流里大约 95% 能选对已有工具，96% 能判断「该不该去造新的」。表 3 说明岗位不能对调：让 GPT-3.5 造难题工具，五局全输，写出来的函数往往只会那三道例题。像只会做课后练习的人偏要编教材——教材会变成「仅适用于这三道」。简单排序则谁都能写。",
    ),
    (
        """发表于 ICLR 2024
GPT-3.5 Turbo　text-davinci-002　davinci　curie　babbage　ada
逻辑演绎 (5)　79.7%　58.2%　11.6%　6.5%　11.6%　3.0%
追踪被打乱物体 (5)　99.6%　100.0%　62.1%　20.7%　16.4%　5.2%
Dyck 语言　92.2%　35.8%　16.4%　18.1%　9.1%　9.9%
单词排序　98.3%　60.8%　26.6%　7.3%　7.3%　0.9%
中国剩余定理　100.0%　100.0%　99.6%　93.1%　75.0%　66.0%
安排会议　100.0%　100.0%　62.9%　59.1%　23.2%　0.0%
成本（美元 / 1K token）　0.002　0.02　0.02　0.002　0.0005　0.0004
表 4：各种工具使用者模型的性能比较，均使用 GPT-4 生成的同一工具。成本按撰文时价格。所有模型中，GPT-3.5 Turbo 在性能与成本之间权衡最好。我们选用指令微调之前的 GPT-3 模型（ada 而非 text-ada-001 等），因为观察到指令微调后的模型在工具使用阶段表现更差。我们推测指令微调损害了上下文学习能力，而这对工具使用阶段至关重要。
Turbo 在所有测试模型中提供了最好的性能–成本平衡。关于更早的 GPT-3 系列（ada、babbage、curie、davinci），我们发现指令微调之前的模型往往优于微调之后的对应版本（text-ada-001 等）。我们推测这些模型的指令微调阶段可能损害上下文学习能力，而这对工具使用阶段至关重要。
把 CoT 当工具并无帮助。
除 LATM 外，我们考察能否像 LATM 流水线那样，把更大模型的思维链复用到更小模型以提升任务性能。具体地，我们在「CoT 制造」阶段用同一更大模型（GPT-4），用零样本提示 “Let's think step by step.” 引出中间思考步骤，再把生成的 CoT 交给同一较小的工具使用模型（GPT-3.5 Turbo）。我们在两个任务上测试，结果见表 5。我们观察到，使用大模型的 CoT 与人类撰写的 CoT 表现相近甚至更差，远不如 LATM。
准确率　GPT-4 CoT　人类撰写 CoT　LATM
逻辑演绎 (5)　36.8　66.4　79.7
追踪被打乱物体 (5)　63.2　61.6　99.6
表 5：使用 GPT-4 生成的 CoT 的准确率。表现与人类撰写 CoT 相近，远不如 LATM。
结论与未来工作
我们提出 LATM，一个使大语言模型能为多样任务创造并使用自己工具的闭环框架。该方法受人类在工具创造上的进化跨越启发，采用两个关键阶段：工具制造与工具使用。这种分工让我们既能利用先进 LLM 的能力，又显著降低计算成本。实验在多种复杂任务上证实了 LATM 的效力：框架表现可与资源密集模型相比，同时更省成本。此外我们表明，再加一个调度器 LLM 能进一步提供灵活性，实现当场造工具与用工具。
在评估过程中，我们发现严重缺少高质量数据集，能真实代表日常人机交互，包括以原始自然语言格式出现的重复任务，如通过邮件或电话安排会议、预订航班。我们预期这项工作将促使研究社区创建此类数据集，它们对培育下一代 AI 系统可能至关重要。这些系统能生成并应用自己的工具，从而更有效地处理复杂任务。一个令人兴奋的未来研究方向是让工具制造者能改进并升级已有工具，以管理新的问题实例，就像软件开发那样。这种适应性可能进一步催化 AI 生态的演化，解锁大量机会。
""",
        "表 4 说明「使用者」也不能太弱：ada 几乎不会把题面填进函数。更刺的是表 5：把 GPT-4 的一步步思考交给 GPT-3.5，还不如人写的思维链，更远不如交出函数。结论把野心说满，也承认缺真实对话数据；下一步想让制造者像改软件一样升级旧工具，而不是每次重写。",
    ),
    (
        """发表于 ICLR 2024
参考文献
Aida Amini, Saadia Gabriel, Peter Lin, Rik Koncel-Kedziorski, Yejin Choi, and Hannaneh Hajishirzi. Mathqa: Towards interpretable math word problem solving with operation-based formalisms. arXiv preprint arXiv:1905.13319, 2019.
Simran Arora, Brandon Yang, Sabri Eyuboglu, Avanika Narayan, Andrew Hojel, Immanuel Trummer, and Christopher Ré. Language models enable simple systems for generating structured views of heterogeneous data lakes, 2023.
Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le, and Charles Sutton. Program synthesis with large language models, 2021.
Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.
Sébastien Bubeck, Varun Chandrasekaran, Ronen Eldan, Johannes Gehrke, Eric Horvitz, Ece Kamar, Peter Lee, Yin Tat Lee, Yuanzhi Li, Scott Lundberg, et al. Sparks of artificial general intelligence: Early experiments with gpt-4. arXiv preprint arXiv:2303.12712, 2023.
Charlie Chen, Sebastian Borgeaud, Geoffrey Irving, Jean-Baptiste Lespiau, Laurent Sifre, and John Jumper. Accelerating large language model decoding with speculative sampling. February 2023a. doi: 10.48550/ARXIV.2302.01318.
Lingjiao Chen, Matei Zaharia, and James Zou. Frugalgpt: How to use large language models while reducing cost and improving performance, 2023b.
Wenhu Chen, Xueguang Ma, Xinyi Wang, and William W. Cohen. Program of thoughts prompting: Disentangling computation from reasoning for numerical reasoning tasks, 2022.
Xinyun Chen, Maxwell Lin, Nathanael Schärli, and Denny Zhou. Teaching large language models to self-debug. ARXIV.ORG, 2023c. doi: 10.48550/arXiv.2304.05128.
Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Paul Barham, Hyung Won Chung, Charles Sutton, Sebastian Gehrmann, et al. Palm: Scaling language modeling with pathways. arXiv preprint arXiv:2204.02311, 2022.
Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.
David Dohan, Winnie Xu, Aitor Lewkowycz, Jacob Austin, David Bieber, Raphael Gontijo Lopes, Yuhuai Wu, Henryk Michalewski, Rif A. Saurous, Jascha Sohl-dickstein, Kevin Murphy, and Charles Sutton. Language model cascades, 2022.
Luyu Gao, Aman Madaan, Shuyan Zhou, Uri Alon, Pengfei Liu, Yiming Yang, Jamie Callan, and Graham Neubig. Pal: Program-aided language models, 2023.
Google. Palm 2 technical report, 2023. URL https://ai.google/static/documents/palm2techreport.pdf.
Daniel Conrad Halbert. Programming by example. University of California, Berkeley, 1984.
Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego de Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, et al. Training compute-optimal large language models. arXiv preprint arXiv:2203.15556, 2022.
Geunwoo Kim, P. Baldi, and S. McAleer. Language models can solve computer tasks. ARXIV.ORG, 2023. doi: 10.48550/arXiv.2303.17491.
Michal Kosinski. Theory of mind may have spontaneously emerged in large language models. arXiv preprint arXiv:2302.02083, 2023.
""",
        "参考文献首页：书目保留英文。可以看到 PAL、Program of Thoughts、自调试、投机采样、模型级联——都是 LATM 用来对照「程序当推理」和「大小模型分工」的邻居。需要细节时按正文编号回查即可。",
    ),
    (
        """发表于 ICLR 2024
Yaniv Leviathan, Matan Kalman, and Yossi Matias. Fast inference from transformers via speculative decoding. November 2022. doi: 10.48550/ARXIV.2211.17192.
Yaobo Liang, Chenfei Wu, Ting Song, Wenshan Wu, Yan Xia, Yu Liu, Yang Ou, Shuai Lu, Lei Ji, Shaoguang Mao, et al. Taskmatrix.ai: Completing tasks by connecting foundation models with millions of apis. arXiv preprint arXiv:2303.16434, 2023.
Wang Ling, Dani Yogatama, Chris Dyer, and Phil Blunsom. Program induction by rationale generation: Learning to solve and explain algebraic word problems. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 158–167, Vancouver, Canada, July 2017.
Ruibo Liu, Jason Wei, Shixiang Shane Gu, Te-Yen Wu, Soroush Vosoughi, Claire Cui, Denny Zhou, and Andrew M. Dai. Mind’s eye: Grounded language model reasoning through simulation. In The Eleventh International Conference on Learning Representations, 2023.
Pan Lu, Baolin Peng, Hao Cheng, Michel Galley, Kai-Wei Chang, Ying Nian Wu, Song-Chun Zhu, and Jianfeng Gao. Chameleon: Plug-and-play compositional reasoning with large language models. arXiv preprint arXiv:2304.09842, 2023.
Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, et al. Self-refine: Iterative refinement with self-feedback. arXiv preprint arXiv:2303.17651, 2023.
Maxwell Nye, Anders Johan Andreassen, Guy Gur-Ari, Henryk Michalewski, Jacob Austin, David Bieber, David Dohan, Aitor Lewkowycz, Maarten Bosma, David Luan, et al. Show your work: Scratchpads for intermediate computation with language models. arXiv preprint arXiv:2112.00114, 2021.
OpenAI. Gpt-4 technical report, 2023.
Bhargavi Paranjape, Scott Lundberg, Sameer Singh, Hannaneh Hajishirzi, Luke Zettlemoyer, and Marco Tulio Ribeiro. Art: Automatic multi-step reasoning and tool-use for large language models. arXiv preprint arXiv:2303.09014, 2023.
Aaron Parisi, Yao Zhao, and Noah Fiedel. Talm: Tool augmented language models, 2022.
Cheng Qian, Chi Han, Yi R Fung, Yujia Qin, Zhiyuan Liu, and Heng Ji. Creator: Disentangling abstract and concrete reasonings of large language models through tool creation. arXiv preprint arXiv:2305.14318, 2023.
Yujia Qin, Shengding Hu, Yankai Lin, Weize Chen, Ning Ding, Ganqu Cui, Zheni Zeng, Yufei Huang, Chaojun Xiao, Chi Han, et al. Tool learning with foundation models. arXiv preprint arXiv:2304.08354, 2023.
Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language models can teach themselves to use tools, 2023.
Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, and Yueting Zhuang. Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface. arXiv preprint arXiv:2303.17580, 2023.
Freda Shi, Mirac Suzgun, Markus Freitag, Xuezhi Wang, Suraj Srivats, Soroush Vosoughi, Hyung Won Chung, Yi Tay, Sebastian Ruder, Denny Zhou, et al. Language models are multilingual chain-of-thought reasoners. arXiv preprint arXiv:2210.03057, 2022.
Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, Abu Awal Md Shoeb, Abubakar Abid, Adam Fisch, Adam R Brown, Adam Santoro, Aditya Gupta, Adrià Garriga-Alonso, et al. Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. arXiv preprint arXiv:2206.04615, 2022.
""",
        "参考文献续页：Toolformer、HuggingGPT、Chameleon、CREATOR、工具学习综述、Big-Bench 都在这里。若要对照「用工具」和「造工具」，先找 Schick et al. 与 Qian et al.；若要对照基准，找 Srivastava et al. 的 Big-Bench。",
    ),
    (
        """发表于 ICLR 2024
Mirac Suzgun, Nathan Scales, Nathanael Schärli, Sebastian Gehrmann, Yi Tay, Hyung Won Chung, Aakanksha Chowdhery, Quoc V Le, Ed H Chi, Denny Zhou, et al. Challenging big-bench tasks and whether chain-of-thought can solve them. arXiv preprint arXiv:2210.09261, 2022.
Petar Veličković and Charles Blundell. Neural algorithmic reasoning. Patterns, 2(7):100273, 2021.
Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, and Anima Anandkumar. Voyager: An open-ended embodied agent with large language models. arXiv preprint arXiv:2305.16291, 2023.
Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, and Denny Zhou. Self-consistency improves chain of thought reasoning in language models. arXiv preprint arXiv:2203.11171, 2022.
Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Ed Chi, Quoc Le, and Denny Zhou. Chain of thought prompting elicits reasoning in large language models. arXiv preprint arXiv:2201.11903, 2022.
Tongshuang Wu, Michael Terry, and Carrie Jun Cai. Ai chains: Transparent and controllable human-ai interaction by chaining large language model prompts. In Proceedings of the 2022 CHI Conference on Human Factors in Computing Systems, pages 1–22, 2022.
Heming Xia, Tao Ge, Si-Qing Chen, Furu Wei, and Zhifang Sui. Speculative decoding: Lossless speedup of autoregressive translation, 2023.
Zhengyuan Yang, Linjie Li, Jianfeng Wang, Kevin Lin, Ehsan Azarnasab, Faisal Ahmed, Zicheng Liu, Ce Liu, Michael Zeng, and Lijuan Wang. Mm-react: Prompting chatgpt for multimodal reasoning and action. arXiv preprint arXiv:2303.11381, 2023.
Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik R Narasimhan, and Yuan Cao. React: Synergizing reasoning and acting in language models. In The Eleventh International Conference on Learning Representations, 2023.
Susan Zhang, Stephen Roller, Naman Goyal, Mikel Artetxe, Moya Chen, Shuohui Chen, Christopher Dewan, Mona Diab, Xian Li, Xi Victoria Lin, et al. Opt: Open pre-trained transformer language models. arXiv preprint arXiv:2205.01068, 2022.
Denny Zhou, Nathanael Schärli, Le Hou, Jason Wei, Nathan Scales, Xuezhi Wang, Dale Schuurmans, Olivier Bousquet, Quoc Le, and Ed Chi. Least-to-most prompting enables complex reasoning in large language models. arXiv preprint arXiv:2205.10625, 2022.
Zilliz. Gptcache. https://github.com/zilliztech/GPTCache, 2023.
""",
        "参考文献末页：含 CoT、ReAct、Voyager、GPTCache。正文里「传统缓存存答句」对应最后一条 Zilliz；「推理再行动」对应 Yao et al. 的 ReAct。全文正文文献到此结束。",
    ),
    (
        """发表于 ICLR 2024
A 调度器示意
图 4：使功能缓存机制成为可能的调度器示意。在任务实例顺序到达的在线设定中，调度器（轻量模型）评估每个到来的实例。若缓存中已有合适工具处理该任务，调度器选择该工具并把任务实例转给工具使用者求解。若找不到合适工具，调度器把实例路由到工具制造者，以创造稍后可供使用者使用的新工具。
B 更广泛的影响与局限
本文探索让大语言模型创造自己的工具，从而在发展其生态上拥有更大自主性的潜力。这一研究方向很有前景，但也带来需要审慎对待的伦理、安全与控制问题。
我们工作最显著的影响之一在于：LLM 有可能自动成长并获得前所未有的能力。这可能显著扩大这些模型能处理的任务范围与复杂度，潜在地变革客服、技术支持乃至研发领域。它可能导致计算资源的更高效使用，并减少对人工干预的依赖，尤其是对常规或重复任务。
然而，LLM 这一新获得的自主性是双刃剑。当我们赋予 LLM 自造工具的能力，也造成一种情形：它们开发的工具质量未必总能达到人类开发者设定的标准或预期。若没有适当保障，这些模型可能生成次优、不正确、甚至潜在有害的解。此外，随着 LLM 更自主，失控的可能增加。若这些模型在缺乏适当监管的情况下被广泛使用，可能出现未预见的后果，甚至导致人类对 AI 系统失去控制的情景。
本研究尚未深入处理这些控制与安全问题，工作也有局限。我们提出的框架 LLM As Tool Maker 在测试场景中有效，但仍处于早期。必须指出，系统的真实表现与安全可能随所应用任务的复杂度与性质而变化。
此外，在真实环境中评估与验证工具制造者所造工具，仍是有待解决的挑战。
""",
        "附录 A 用图 4 把调度器画成分流器：有工具走使用者，没工具走制造者。附录 B 很少见地承认：自造工具等于更大自主性，质量可能差、甚至有害，控制问题本文没做。读论文时别只记住表 2 的 100%，也记住作者把安全写成了「尚未处理」。",
    ),
    (
        """发表于 ICLR 2024
C LATM 提示
工具制造者提示
Please write a generic Python function to solve this type of problems using only standard python libraries. The output of the function can later be converted to the answer (option for multiple choice question). All the function should be wrapped by
```python
```
工具验证者提示
Write unit tests to verify the correctness of the function on the questions above using the following format:
```python
{parse the question into the arguments of the function}
{call the function and save the return value in a variable named "ret"}
{for multiple choice question, parse the options}
{convert the return value "ret" to the answer (if the question is a multiple choice question, convert to an option) and save it in a variable named "ans", otherwise}
{assert ans == the provided answer (if the question is a multiple choice question, assert ans == option)}
```
工具封装者提示
Success! The function is correct. We will need to summarize the function and use cases up for further use. Please extract the information from the history in the following format:
Here is a function to solve a class of problems:
```python
{the function, including necessary imports}
```
Use cases:
Question: {question (including options)}
Solution:
```python
{parse the question into the arguments of the function}
{call the function and save the return value in a variable named "ret"}
{for multiple choice question, parse the options}
{convert the return value "ret" to the answer (if the question is a multiple choice question, convert to an option) and save it in a variable named "ans", otherwise}
```
Do this for all the questions in the verification step.
""",
        "附录 C 给出三份提示原文（此处保留英文）。制造者：只用标准库写通用函数。验证者：按固定模板写单测，返回值先叫 ret 再变成 ans。封装者：成功后把函数和「问句→调用」用例抽成说明书。整套流水线其实就是这三段话在驱动，没有更重的训练。",
    ),
    (
        """发表于 ICLR 2024
调度器提示
Here are several functions that can be used to solve some task:
Task: logical_deduction_five_objects
API: find_order(objects, constraints):
Finds the order of objects that satisfies a given set of constraints.
objects: A list of unique objects (strings) to be ordered.
constraints: A list of lambda functions that represent the constraints on the order of objects. Each constraint should take the order of objects as input and return a boolean value (True if the constraint is satisfied, False otherwise).
return: A tuple representing the order of objects that satisfies all the constraints. If no such order exists, the function returns None.
===
Task: tracking_shuffled_objects_five_objects
API: square_dance(initial_partners, switches):
This function takes an initial list of pairs and a list of switches, and returns a dictionary representing the final state of the pairs after performing the switches.
initial_partners: A list of tuples, where each tuple contains two elements representing a pair. The elements can be any type.
switches: A list of tuples representing pairs of elements from the initial_partners list that will be switched.
return: A dictionary representing the final state of the pairs after performing the switches.
===
Skip other tasks
Here is a question:\\n{question}\\n\\nAccording to the API documents above, you may find some functions that can be used to solve the task, or, sometimes there does not exist proper function to solve the task. Figure out if there is function to solve the task and reply in the format:\\nTask: {{task}} (reply unknown if no function can solve the question)
""",
        "调度器提示：先列出已有工具的 API 说明书（逻辑演绎的 find_order、换位追踪的 square_dance 等），再贴上新问题，要求回答 Task: 某某，或 unknown。功能缓存的「命中 / 未命中」在实现上就是让轻量模型做一次文档问答。像前台对照产品手册决定能不能接单。",
    ),
    (
        """发表于 ICLR 2024
""",
        "本页几乎是空白隔页，只有会议页眉。没有新论点，直接翻到附录 D 的封装工具样例即可。",
    ),
    (
        """发表于 ICLR 2024
D 封装后的工具
逻辑演绎工具
Here is a function to solve a class of problems:
```python
from itertools import permutations
def find_order(objects, constraints):
    for order in permutations(objects):
        valid = True
        for constraint in constraints:
            if not constraint(order):
                valid = False
                break
        if valid:
            return order
```
Use cases:
Question: The following paragraphs each describe a set of five objects arranged in a fixed order. ... On a shelf, there are five books: a white book, a green book, a brown book, a gray book, and an orange book. ...
Options: (A)–(E)
Solution:
```python
objects = ["white", "green", "brown", "gray", "orange"]
constraints = [
    lambda order: order.index("gray") > order.index("orange"),
    lambda order: order.index("green") == len(order) - 2,
    lambda order: order.index("brown") > order.index("white"),
    lambda order: order.index("brown") < order.index("orange"),
]
ret = find_order(objects, constraints)
options = {"A": "white", "B": "green", "C": "brown", "D": "gray", "E": "orange"}
ans = [k for k, v in options.items() if v == ret[2]][0]
```
（其后省略另外两道问句）
""",
        "附录 D 第一件封装工具：暴力枚举排列，用 lambda 写约束。使用者要做的不是「想谁在中间」，而是把题面译成 objects 列表和四条 index 比较。像把侦探推理题改写成「满足这些谓词的排列」。代码保持英文原文。",
    ),
    (
        """发表于 ICLR 2024
追踪被打乱物体的工具
Here is a function to solve a class of problems:
```python
def square_dance(initial_partners, switches):
    current_partners = dict(initial_partners)
    for switch in switches:
        dancer1, dancer2 = switch
        partner1 = current_partners[dancer1]
        partner2 = current_partners[dancer2]
        current_partners[dancer1] = partner2
        current_partners[dancer2] = partner1
    return current_partners
```
Use cases:
Question: Alice, Bob, Claire, Dave, and Eve are on the same team in a soccer match. ... pairs of players occasionally swap positions. ... At the end of the match, Eve is playing
Options: (A) goalkeeper ... (E) center midfielder
Answer: (C)
Solution:
```python
initial_positions = [("Alice", "goalkeeper"), ("Bob", "left midfielder"), ...]
switches = [("Alice", "Claire"), ("Alice", "Bob"), ...]
ret = square_dance(initial_positions, switches)
options = ["goalkeeper", "left midfielder", "right winger", "striker", "center midfielder"]
ans = options.index(ret["Eve"]) + 1
```
（其后省略另外两道问句）
""",
        "第二件工具：用字典模拟两两换位。题面里一长串「Alice 和 Claire 换、再和 Bob 换」被收成 switches 列表，最后查 Eve 的位置。人脑容易数错换了几次；函数不会。这也解释了表 2 里该任务从 62% 飙到 99%——错的不是理解题意，是手工模拟。",
    ),
    (
        """发表于 ICLR 2024
Dyck 语言工具
Here is a function to solve a class of problems:
```python
def complete_sequence(input_str):
    stack = []
    closing_map = {'(': ')', '[': ']', '<': '>', '{': '}'}
    result = []
    for char in input_str:
        if char in closing_map.keys():
            stack.append(char)
        elif char in closing_map.values():
            if stack and closing_map[stack[-1]] == char:
                stack.pop()
            else:
                return "Invalid sequence"
        else:
            return "Invalid character"
    while stack:
        result.append(closing_map[stack[-1]])
        stack.pop()
    return ''.join(result)
```
Use cases:
Question: Complete the rest of the sequence, making sure that the parentheses are closed properly. Input: ([[[{{}}]{<[<[{}]>]>}
Answer: ])
Solution:
```python
input_str = "([[[{{}}]{<[<[{}]>]>}"
ret = complete_sequence(input_str)
ans = ret
```
（其后省略另外两道问句）
""",
        "Dyck 语言工具就是经典括号栈：读完输入后把栈里剩下的开口一次性补上。正文里 GPT-4 当使用者反而会在参数里先补括号，等于还没调用函数就改了题目。本页让你看见：工具对了，调用方仍可能「帮忙过度」。",
    ),
    (
        """发表于 ICLR 2024
单词排序工具
Here is a function to solve a class of problems:
```python
def sort_words_alphabetically(word_list):
    return sorted(word_list)
```
Use cases:
Question: Sort the following words alphabetically: List: conference apparition ignore dutton ...
Answer: apparition conference copra coupe ...
Solution:
```python
words1 = ["conference", "apparition", "ignore", "dutton", ...]
ret1 = sort_words_alphabetically(words1)
ans1 = " ".join(ret1)
```
（其后省略另外两道问句）
""",
        "最简单的一件工具：直接调用 Python 的 sorted。这也对应表 3：GPT-3.5 五次都能造出来。说明 LATM 的「制造者必须是 GPT-4」只对难算法成立；排序这种活，轻量模型自己就会做模具。",
    ),
    (
        """发表于 ICLR 2024
中国剩余定理工具
Here is a function to solve a class of problems:
```python
def find_number(max_limit, divisors, remainders):
    for num in range(max_limit + 1):
        if all((num - remainder) % ...):
            return num
    return None
```
Use cases:
Question: There is a basket of no more than 1188877 durians. If we divide them equally among 41 penguins, we have 17 left; ... How many durians are in the basket?
Solution:
```python
max_limit = 1188877
divisors = [41, 107, 271]
remainders = [17, 42, 260]
ret = find_number(max_limit, divisors, remainders)
ans = ret
```
（其后省略另外两道问句）
""",
        "中国剩余定理在思维链下 GPT-4 也是 0 分，一写成「在上限内枚举满足所有余数」就 100%。抽取文本在取模那一行有折行缺损，对照 PDF 即可。故事很直白：语言模型不擅长大数同余，解释器擅长。这正是「功能缓存」最值的一类题。",
    ),
    (
        """发表于 ICLR 2024
安排会议工具
Here is a function to solve a class of problems:
```python
from datetime import datetime, timedelta
def find_earliest_time_slot(a_availability, b_availability, meeting_duration):
    a_availability = [(datetime.strptime(start, '%...
    b_availability = [(datetime.strptime(start, '%...
    for a_start, a_end in a_availability:
        for b_start, b_end in b_availability:
            latest_start = max(a_start, b_start)
            earliest_end = min(a_end, b_end)
            if earliest_end - latest_start >= timedelta(minutes=meeting_duration):
                return latest_start.strftime('%...
    return None
```
Use cases:
Question: A and B want to schedule a 1-hour meeting together. A's availability: ... B's availability: ... What time slot works best?
Answer: No time slot works.
Solution:
```python
a_availability = [('12:00', '12:30'), ...]
b_availability = [('09:00', '11:00'), ...]
meeting_duration = 60
ret = find_earliest_time_slot(a_availability, b_availability, meeting_duration)
ans = ret if ret else "No time slot works."
```
（其后省略另外两道问句）
E 数据集构造
对「安排会议」任务，我们用如下模板生成数据集：
question_format = \"\"\"A and B want to schedule a {interval}-hour meeting together.
A's availability: {A_availability}
""",
        "约会议工具做区间求交，找最早且够长的重叠。模板题比 Big-Bench 更像真实工作流，也是作者在结论里抱怨「缺真实邮件数据」时拿来凑的替代品。附录 E 从本页下半开始：用字符串模板随机采样时长与空闲段。抽取文本里 strptime 格式串被折行截断，以 PDF 为准。",
    ),
    (
        """发表于 ICLR 2024
B's availability: {B_availability}
What time slot works last? (if multiple, choose the earliest one)\"\"\"
其中 interval 从 {0.5, 1, 1.5} 中随机采样，A 与 B 的空闲时间从 8:00–18:00 以 30 分钟为粒度随机采样。答案通过计算两段空闲集合的交集，再找不短于会议时长的最早时段得到。若无此时段，返回 “No time slot works.”。
""",
        "附录 E 收尾：约会议数据完全程序生成——随机时长、随机空闲格、用区间交集算标准答案。所以表 2 的 100% 测的是「调用对了没有」，不是「模型懂不懂真实秘书工作」。把它当动机例子可以，当真实办公基准则要打折。全文到此结束。",
    ),
]


def main() -> None:
    assert len(PAGES) == 23, len(PAGES)
    zh_dir = ART / "page_zh"
    plain_dir = ART / "page_plain"
    zh_dir.mkdir(parents=True, exist_ok=True)
    plain_dir.mkdir(parents=True, exist_ok=True)
    for i, (zh, plain) in enumerate(PAGES, start=1):
        (zh_dir / f"page-{i:03d}.json").write_text(
            json.dumps({"page": i, "zh": zh.strip() + "\n"}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (plain_dir / f"page-{i:03d}.json").write_text(
            json.dumps({"page": i, "plain": plain.strip() + "\n"}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"wrote {len(PAGES)} zh + {len(PAGES)} plain under {ART}")


if __name__ == "__main__":
    main()
