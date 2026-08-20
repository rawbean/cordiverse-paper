#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write Live-SWE-agent per-page zh + plain JSON (page-aligned)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "papers" / "self-evolve" / "live-swe-agent" / "artifacts"

PAGES: list[tuple[str, str]] = [
    (
        """LIVE-SWE-AGENT：软件工程智能体能否在运行中自演化？
Chunqiu Steven Xia  Zhe Wang  Yan Yang†  Yuxiang Wei  Lingming Zhang
University of Illinois Urbana-Champaign
{chunqiu2, zhe36, ywei40, lingming}@illinois.edu  †yanyang826@outlook.com
摘要
大语言模型（LLM）正在重塑几乎所有行业，包括软件工程。近年来，已有若干 LLM 智能体被提出以解决真实软件问题。这类软件智能体通常配备一套编码工具，并能自主决定下一步动作，形成完整轨迹以端到端完成软件任务。尽管前景可观，它们通常需要专门设计，且仍可能次优——因为穷尽整个智能体脚手架设计空间极度困难且昂贵。
认识到软件智能体本质上也是软件、因而可以被进一步精炼 / 修改，研究者近期提出若干自改进软件智能体，包括达尔文–哥德尔机（DGM）。同时，这类自改进智能体需要在特定基准上做昂贵的离线训练，并且在不同 LLM 或基准之间未必泛化良好。
本文提出 LIVE-SWE-AGENT，第一个能够在解决真实软件问题的运行时自主、持续地当场自演化的 live 软件智能体。更具体地，LIVE-SWE-AGENT 从最基本的、仅能访问 bash 工具的脚手架（如 mini-SWE-agent）出发，在解决真实软件问题的同时自主演化自己的脚手架实现。
我们在广泛研究的 SWE-bench Verified 基准上的评估表明，LIVE-SWE-AGENT 在无测试时缩放的情况下可达到 77.4% 的可观解决率，超过所有现有软件智能体，包括最佳专有方案。此外，在较新的 SWE-Bench Pro 上，它也超过最先进的人工打造软件智能体，达到当时已知最佳的 45.8% 解决率。更多细节见 https://github.com/OpenAutoCoder/live-swe-agent
图 1：SWE-bench Verified 与 SWE-Bench Pro 结果（单次尝试、无测试时缩放）
†作为伊利诺伊大学厄巴纳–香槟分校研究实习生完成。
arXiv:2511.13646v3 [cs.SE] 24 Nov 2025
""",
        "封面：问题写在标题里——软件智能体能不能「边修 bug 边改自己」。作者的答案是能，而且不必先花离线训练把脚手架炼成固定成品。从只会 bash 的 mini-SWE-agent 起步，Verified 单次 77.4%、Pro 45.8%。图 1 把开源脚手架和公司内部架子放在同一张棒图上，强调「没有测试时缩放」。像学徒不先换全套工具箱，而是修这台机器时现场焊一把更顺手的扳手。",
    ),
    (
        """引言
大语言模型已从简单的代码自动补全 [7, 12, 22, 38] 迅速进展到能浏览仓库、跑测试并端到端提交补丁的交互式智能体 [42, 34, 47, 37, 10, 23]。早期对话式修复系统利用环境反馈迭代精炼候选修复 [40]；随后的智能体框架（如 SWE-agent [42] 与 OpenHands [34]）为 LLM 配上终端、编辑器与搜索，使其能在复杂仓库上多步使用工具。与此同时，互补的「少一点智能体」流水线（如 Moatless [49] 与 Agentless [37]）主张：脚手架设计中许多被感知的复杂度，其实可以被专门的提示与工作流设计取代。
尽管有这些进展，大多数现有智能体设计固定，并受限于静态行动空间：即便某任务本可从更多定制中受益，脚手架实现（含工具）仍被预先设定。此外，由于设计空间无穷，人工设计最优软件智能体脚手架极度困难且昂贵。因此，社区最近开始探索自演化软件智能体 [45, 30, 33]，它们迭代修改自己的脚手架实现，并用编码基准上的离线评估信号实证验证每次改动。然而这些方法增加显著额外成本。例如据原文，DGM 在 SWE-bench 上跑一轮大约 22,000 美元 [45]。并且它们严重依赖离线演化：改进通常在某些基准上学会，再烘焙进一个静态智能体。如此，学成的智能体可能专门化到给定基准与底层 LLM，之外泛化不良。
为弥合这一差距，我们提出 LIVE-SWE-AGENT，第一个 live、运行时自演化的软件工程智能体，它在处理真实世界 issue 时当场扩展并修订自己的能力。关键洞察是：软件智能体本身就是软件系统，而基于现代 LLM 的软件智能体已经具备在运行时扩展或修改自身实现的内在能力。虽然「当场自演化」的想法适用于脚手架实现的所有部分，作为第一步，我们主要聚焦工具创造，因为它是软件智能体最核心的部分之一。LIVE-SWE-AGENT 从仅有 bash 工具访问的简单智能体（如 mini-SWE-agent [42]）出发。在常规的 issue 求解循环中，智能体可以合成、修改并执行自定义工具，例如编辑器、代码搜索工具与领域特定分析器。一条轻量的步反思提示反复询问：创造或修订一个工具是否会加速进展，从而把工具化变成与「跑测试」等普通动作并列的一等决策。该机制不改底层脚手架、不需要离线训练、且与底层 LLM 无关。通过把工具创造提升为显式、迭代的决策点，我们解锁了这一隐藏的当场自改进能力。
LIVE-SWE-AGENT 针对现有研究的局限。首先，有了工具创造，智能体行动空间适配当前问题，产出精确抓住完成本任务所需的任务相关工具。此外，通过把改进从离线训练挪到在线演化，它缓解了繁琐的脚手架工程，因为新能力从遇到的 issue 本身涌现。重要的是，工具合成不是一次性预处理，而是与解题交错的持续迭代。智能体可以随着对失败模式理解的演化而精炼工具。尽管设计最小、简单，LIVE-SWE-AGENT 可泛化到不同脚手架与 LLM，并在软件 issue 求解上取得先进的开源结果。
我们在广泛使用的 SWE-bench Verified [26] 与更具挑战的 SWE-Bench Pro [4] 上评估。在无任何测试时缩放的情况下，LIVE-SWE-AGENT 在 Verified 上达到 77.4% 解决率，在 Pro 上达到 45.8%，超过最先进的开源基线甚至最佳商业智能体系统。消融与工具分析表明：（1）自定义工具创造以极小开销实质提升有效性（更高解决率）；（2）收益在不同先进 LLM 后端上持续存在，更强模型上更好，显示随着 LLM 能力迅速演化其前景可观；（3）合成的工具既包括通用工具，也包括有利于 issue 特化求解的任务对齐特化。
总之，我们做出以下贡献：
""",
        "引言把对手摆清楚：固定工具集太死；离线自演化（DGM）太贵、还容易过拟合基准。作者的刀很快：智能体已经会改软件，缺的只是把「要不要造个工具」写成和跑测试一样的一等动作。反思提示像工头每做完一步就问「要不要先做把专用钳子」。先记住：不改主循环、不离线训练、先只演化工具。",
    ),
    (
        """Issue 描述　项目代码库　$ cat file.c　$ python tool.py　$ grep -r x
工具　智能体　自定义工具　反馈　THOUGHT　REFLECT　环境　已提交补丁
图 2：LIVE-SWE-AGENT 总览
• 第一个 live 软件智能体。我们提出 LIVE-SWE-AGENT，第一个能在解决真实 issue 时当场自主自演化自身脚手架实现、且无需离线训练或额外流水线的 live 软件智能体。
• 最小且通用的实现。当前实现采用最小、通用的设计：智能体从仅 bash 的最小脚手架（如 mini-SWE-agent）出发，通过创造通用或定制工具当场自改进。该设计兼容任何现有软件智能体循环或 LLM，开销可忽略，已公开于 https://github.com/OpenAutoCoder/live-swe-agent。
• 先进性能。在 SWE-bench Verified 与 SWE-Bench Pro 上，LIVE-SWE-AGENT 分别达到 77.4% 与 45.8% 解决率（无任何测试时缩放），超过撰文时所有现有开源智能体与商业系统。据我们所知，SWE-Bench Pro 结果也是当时报道的最佳。
• 全面分析。我们详细研究当场造工具何时、为何有帮助，如何提升效率，以及与固定工具智能体、基于工作流的系统、离线自改进方法相比如何。值得注意的是，相对现有自改进智能体，我们在 SWE-bench Verified-60 子集上达到 65.0% 解决率（DGM 为 53.3%），同时成本显著更低（无离线成本）。
• 统一榜单。对软件任务，近期 LLM 常用人工工程化的专有智能体脚手架评测，使公平的模型比较变得困难。LIVE-SWE-AGENT 提供开放、统一且强大的脚手架，使未来模型发布能真正公平、对等地比较。我们维护用 LIVE-SWE-AGENT 在真实软件任务上评估近期模型的榜单：http://live-swe-agent.github.io
方法
LIVE-SWE-AGENT 是一个 live、自演化的智能体，在解决 issue 时当场改进并扩展自己的能力。关键洞察是：智能体本身可以像它们被设计去解决的软件 issue 一样被迭代改进。智能体可以演化的空间不仅包括所用工具，也包括底层脚手架本身。本文从简单脚手架出发，主要聚焦工具创造与使用上的自演化，因为工具是智能体最关键的组件之一。下面说明 LIVE-SWE-AGENT 如何为 LLM 提供当场开发并使用自己工具的框架。
图 2 给出总览。首先，① 我们同时接收项目代码库与待解决 issue 的描述，把这些信息提供给智能体，并用一组工具初始化它。一开始，智能体可能只拥有有限工具（如 bash 命令），而 LIVE-SWE-AGENT 的目标是让智能体在解题过程中当场生成并使用自己的工具。随着智能体解题，每一步它可以选择 ② 输出一条命令（例如使用某工具），或 ③ 创造一个能帮助
""",
        "贡献五条加图 2。循环很瘦：读 issue → 要么跑命令要么写脚本 → 环境反馈后再被问一句「要不要造工具」。作者还想用它当「公平比模型」的开源架子，避免各家用私有脚手架刷榜。读到这里先建立画面：左边是仓库，右边多了一个 tools/ 文件夹，是智能体自己长出来的。",
    ),
    (
        """它解决问题的自定义工具。在 LIVE-SWE-AGENT 中，我们把自定义工具定义为可在环境中执行的脚本。这为智能体提供直观、直接的工具使用接口，使它能输出一条命令来使用任何自定义工具。接下来，与现有方法 ④ 直接把环境反馈输出提供给智能体不同，⑤ 我们特别要求智能体反思过去步骤，并在反馈消息中决定是否应创造工具。该循环重复，直到智能体提交对初始问题的解 ⑥。与先前智能体设定中工具集与可能动作固定不同，LIVE-SWE-AGENT 允许智能体通过当场创造并使用自定义工具来进行 live 自演化。
2.1 当场自演化
LIVE-SWE-AGENT 的关键想法是让智能体通过修改自己的脚手架（例如基于问题与既往轨迹创造自定义工具）来自改进。为支持造工具，我们对智能体的初始提示做若干简单修改。具体地，我们提供说明与示例，展示工具应如何被创造与使用。更重要的是，我们向智能体表明：（1）它创造的任何工具，目标都应是更好地完成任务；（2）所造工具可以用于任何目的，不必通用。
除了通过初始提示引入造工具能力，我们还在每一步之后显式要求智能体反思既往轨迹，以决定是否应创造任何工具。做法是在每条环境反馈之后追加一条简单的反思消息。实验中我们发现，这一反思过程对于提醒智能体设计对该 issue 有用且具体的工具是必要的。
必须指出，LIVE-SWE-AGENT 对常规智能体框架所做的修改极其简单（初始提示与反思消息均见附录 D）。它不改变智能体循环、不强加特定工作流、也不要求任何昂贵离线训练。重点在于允许并扩展智能体在运行时创造自己的自定义工具，以提升性能并减少人工造工具的工作量。这使 LIVE-SWE-AGENT 极为通用，适用于广泛的不同任务、LLM 与脚手架。我们还指出：软件智能体本质上也是软件。因此，它们可以由软件智能体（它们自己）当场修改与更新，与任何其它软件仓库无异。在 LIVE-SWE-AGENT 中，我们利用这一洞察，通过让智能体按当前问题创造自己的自定义工具来实现当场自改进。下面更详细描述智能体创造的自定义工具。
2.2 自定义工具合成
在 LIVE-SWE-AGENT 中，我们把自定义工具定义为可在环境中执行的脚本。这让智能体既能轻松创造工具（创建脚本文件），也能使用已造工具（带参数运行脚本）。我们相信这是适合广泛任务的通用、直观接口。
示例编辑工具。图 3a 展示智能体创造的一个自定义工具。这是一个编辑工具，允许智能体通过替换、插入或删除代码来编辑文件。可以看到它包含必要的工具逻辑，以及如何使用该工具的清晰说明。相比可能用许多不同参数与开关淹没智能体的 bash 命令，智能体自己创造的工具目的直接、易于使用。此外，在该例中，编辑工具还提供相关反馈消息，例如指出替换编辑是否成功。这类反馈对告知智能体下一步动作可能至关重要。另一方面，像 sed 这样的 bash 编辑命令并不指示编辑结果：若待替换字符串不存在，替换操作不会产生警告，但仍返回成功码。因此，智能体可能被误导，以为编辑成功，而文件实际上没有任何改动。
LIVE-SWE-AGENT 也鼓励智能体创造能提高工作流效率的工具。例如，解决 issue 的常见一步是定位相关代码片段以理解根因。此时，自定义搜索工具可用于在特定目录内搜索代码并显示周围上下文。虽然用不同 bash 命令的组合也可能达到自定义搜索工具的同样结果
""",
        "机制页。改动只有两处：开场说「你可以造工具，不必通用」；每步反馈后再贴一句反思。自定义工具 = 可执行脚本，创建就是写文件。编辑器例子很狠：sed 替换失败仍返回 0，智能体会以为改成功了；自写编辑器会打印 “not found”。像用不会说话的锤子对会报错的扭力扳手。",
    ),
    (
        """（例如 grep、find、cat），智能体往往需要多步才能完成实际搜索，导致上下文变长、解题耗时增加。通过创造能处理复杂、多步任务的自定义工具，LIVE-SWE-AGENT 可以同时提升智能体的有效性与效率。
图 3：自定义工具示例　(a) 编辑工具　(b) MARC 文件分析工具
示例 issue 特化工具。除通用工具外，LIVE-SWE-AGENT 的另一好处是能创造 issue 特化工具。图 3b 展示一个专门针对特定 issue 定制的工具。该例中，工具分析 MARC 文件（一种出版或文本记录的文件格式）并以人类可读格式打印。智能体可以创造并使用该工具，显示作为测试用例的相关 MARC 文件内容（包括二进制文件），从而更好理解 issue 并评估潜在补丁。这类功能很难用简单 bash 命令甚至通用工具轻易实现。通过让智能体当场创造任意自定义工具，LIVE-SWE-AGENT 能为个别问题生成特化工具，从而更有效地解决 issue。
一个公平的问题是：为何不在一开始就直接生成这些工具？原因是：造工具与人工解题一样，也是迭代过程。我们需要理解当前问题，并在求解过程中识别问题，才能在不同情形下想出有帮助的工具。例如在 MARC 文件例子中，并非一开始就显然需要专门分析 MARC 的自定义工具。若在开始时造齐所有工具并在全程套用这一固定集合，就会失去在独特情形下设计有用自定义工具的机会。此外，拥有一切可能工具并不一定更好，因为它们可能淹没并误导智能体。再者，智能体常常会迭代或修改已造工具，这需要固定工具设定下并不具备的运行时修改能力。LIVE-SWE-AGENT 让智能体自动当场合成自定义工具，而无需沉重的脚手架修改或昂贵的离线训练更新。
实验设置
实现。尽管 LIVE-SWE-AGENT 可通用于不同软件智能体脚手架，我们在流行的 mini-SWE-agent [42] 框架之上实现它。因此我们默认保留 mini-SWE-agent 的超参数（即每 issue 最大 250 步、最大成本 3 美元）。选择它作为底座，是因为它不仅简单（约 100 行代码、只访问 bash 命令），而且被广泛使用。除非另有说明，实验使用 Claude 4.5 Sonnet（claude-sonnet-4-5-20250929）[6]，每个 issue 采样一个补丁。
数据集。我们在流行的 SWE-bench Verified [26] 上评估，该基准含 500 个软件开发问题，目标是根据问题描述成功修改仓库。SWE-bench Verified 经人类开发者验证，确保每条问题描述含有足够信息以解决问题。此外，我们也在较新的 SWE-Bench Pro [4] 上评估，该基准含 731 个公开问题，旨在捕捉真实、复杂、企业级问题。与 SWE-bench Verified 相比，SWE-Bench Pro 包含跨多个仓库与编程语言的更难问题。
""",
        "本页回答「为何不开始就造齐」。MARC 分析器是现场长出来的：一开始你根本不知道这题要读一种图书编目二进制格式。工具太多还会吵。实验底座故意选最瘦的 mini-SWE-agent（约 100 行、每题 3 美元封顶），好证明涨点来自「能造工具」，不是来自另一套 7000 行架子。",
    ),
    (
        """表 1：SWE-bench Verified 结果
工具　LLM　解决率　平均美元成本
mini-SWE-agent [42]　GPT-5-Mini 59.8% / $0.04；GPT-5 65.0% / $0.28；Claude 4.5 Sonnet 70.6% / $0.56；Gemini 3 Pro 74.2% / $0.46
LIVE-SWE-AGENT　GPT-5-Mini 63.0% / $0.05；GPT-5 68.4% / $0.27；Claude 4.5 Sonnet 75.4% / $0.68；Gemini 3 Pro 77.4% / $0.48
表 2：SWE-bench Verified-60 结果
工具　LLM　解决率　离线成本（小时）
离线自改进智能体　SICA [30] GPT-5-Mini 50.0% / 无限循环；DGM [45] 53.3% / 1231；HGM [33] 56.7%
LIVE-SWE-AGENT　GPT-5-Mini　65.0%　（无离线）
基线。我们将 LIVE-SWE-AGENT 与有代表性的先进智能体方法比较。对 SWE-bench Verified，我们与 mini-SWE-agent 比较，因为它是 SWE-bench 任务上使用最广泛、榜单靠前的开源智能体方案之一。此外这也是直接比较，因为我们直接建在该框架之上。我们还在 SWE-bench Verified 的一个子集上与先前自演化智能体比较：Self-Improving Coding Agent（SICA）[30]、达尔文–哥德尔机（DGM）[45]、Huxley-Gödel Machine（HGM）[33]。这 60 题子集已被先前工作 [33] 专门用来评估上述三个自改进基线。对 SWE-Bench Pro，我们与该榜上表现最好的 SWE-agent [42] 比较。对各基线，我们直接复用其实验结果，并在可能时报告性能、成本与所用后端 LLM。
评估
4.1 主要结果
SWE-bench Verified。表 1 给出 LIVE-SWE-AGENT 与先前智能体方法在 SWE-bench Verified 上的结果。我们首先观察到：相对 mini-SWE-agent，在四种不同 LLM 后端上，LIVE-SWE-AGENT 均持续取得更高解决率。这展示了允许智能体当场创造并使用自己的自定义工具所带来的性能改进。此外，相对基础 mini-SWE-agent，它仅以极小的成本增加实现这一点。在某些情形（如 GPT-5）我们甚至观察到轻微节省：智能体用实现相同功能的自定义工具替换复杂、多轮命令，从而提高求解效率。
我们还展示 LIVE-SWE-AGENT 与表现最佳的智能体工具（包括最先进开源方案与专有商业脚手架）在 SWE-bench Verified 上的比较（图 1）。图 1 只报告单次尝试结果、无任何测试时缩放，以确保公平比较。我们观察到：使用 Gemini 3 Pro 的 LIVE-SWE-AGENT 在无测试时缩放时达到 77.4% 解决率，超过 SWE-bench Verified 榜单¹上撰文时包括最先进商业方案在内的所有现有智能体。
¹https://www.swebench.com
""",
        "数字页。同一底座上换四套模型，live 版都比纯 bash 高几个点，成本几乎持平，GPT-5 甚至更便宜——因为少打了几轮绕口令式 grep。表 2 更刺：离线自演化烧一千多小时，还打不过「当场造工具」的 65%。DGM 的 2.2 万美元在这里变成一张「无离线」空格。",
    ),
    (
        """表 3：SWE-Bench Pro 结果
工具　LLM　解决率　平均美元成本
SWE-agent [42]　Claude 4.5 Sonnet　43.6%　—
LIVE-SWE-AGENT　Claude 4.5 Sonnet　45.8%　$0.73
我们还在先前评估 [33] 选用的 60 道 SWE-bench Verified 子集上，与三个先前自演化智能体做详细比较。表 2 给出 SICA、DGM、HGM 与 LIVE-SWE-AGENT 在该子集上的解决率与离线成本。我们观察到 LIVE-SWE-AGENT 取得最佳性能，相对此前最佳方法提升 8.3 个百分点。我们也看到，先前自演化智能体都需要大量离线训练来演化基础智能体，耗时超过 500 小时。并且先前自演化技术产出一个用于所有问题的静态智能体。相反，LIVE-SWE-AGENT 为每个任务创造自定义工具，使其能根据问题与所用特定 LLM 当场适配。与先前自演化智能体所需的昂贵离线更新不同，它采用在线演化：提示智能体当场生成自定义工具以提升性能，开销很小。
SWE-Bench Pro。我们也在 SWE-Bench Pro 的公开集上评估，含跨 11 个仓库、四种编程语言（Python、Go、TypeScript、JavaScript）的 731 道题。表 3 给出相对 SWE-agent 这一先进基线的表现。与只访问基本 bash 的 mini-SWE-agent 不同，SWE-agent 提供人工打造的文件查看与编辑工具，并且是 SWE-Bench Pro 上表现最好的方法。我们为 SWE-agent 选择 Claude 4.5 Sonnet，因为它在 SWE-Bench Pro 榜²上排名最高；因此我们也用它作为 LIVE-SWE-AGENT 的基础 LLM 以公平比较。我们观察到 LIVE-SWE-AGENT 能取得比 SWE-agent 更好的表现——而后者是一个接近 7,000 行代码的专门设计智能体。我们还在图 1 中与所有其它顶尖智能体与 LLM 比较，观察到它在 SWE-Bench Pro 上达到 45.8% 解决率的新先进水平。这进一步说明 live 脚手架设计相对与固定、人工打造工具集交互的现有智能体的优越性。
4.2 工具分析
图 4：Claude 4.5 Sonnet 在 SWE-bench Verified 与 SWE-Bench Pro 上生成工具的二维 t-SNE 可视化。我们按工具类型（图 4a）、仓库名（图 4b）以及仓库所用编程语言（图 4c）标注嵌入。注意图 4b 因版面只在图例中标了三个仓库；选择它们是因为具有代表性的独立簇。
自定义工具的类别与变体。我们考察 LIVE-SWE-AGENT 创造的自定义工具。图 4 用 t-SNE [17] 展示嵌入可视化。我们基于工具体（即工具脚本内容）用文本嵌入模型（OpenAI text-embedding-3-small）计算每个工具的嵌入。
""",
        "Pro 上 45.8% 对上近 7000 行的 SWE-agent 的 43.6%：更瘦的「现场焊工具」压过了人手打磨的查看/编辑套件。图 4 预告工具并不长成一个点——同叫 edit，彼此仍散开。像厨房里大家都有刀，但切生鱼片的和砍骨头的不是同一把。",
    ),
    (
        """首先，我们通过把工具归入常见功能（如 edit、view、search 等）来看 LIVE-SWE-AGENT 创造的工具类型。归类用基于工具脚本文件名的简单字符串匹配。图 4a 展示为 SWE-bench Verified 生成的工具可视化。可以看到，虽然确有 edit、view、search 等常见工具的明显簇，它们内部仍有变体。例如 edit 工具簇（蓝色圆圈）不是紧密的一点，而是铺开的，说明 LIVE-SWE-AGENT 能按问题生成不同的编辑工具。此外，它也允许智能体生成额外工具（others，红色三角）。这些是更独特的 issue 特化工具，例如把非常细致的补丁打到多个文件的脚本，或显示两文件差异的 diff 检查工具。我们对所有研究数据集做了类似分析，见附录 B。
除创造的工具类型外，我们也考察工具如何随不同仓库与语言变化。图 4b 按仓库展示 SWE-Bench Pro 中创造的工具。Pro 有 11 个仓库，并不奇怪，不同仓库之间也有共同工具（图中重叠簇）。另一方面，某些仓库也有特定工具，例如我们看到 openlibrary（一个文献编目代码库）有一个独立簇（橙色菱形）。由于 openlibrary 处理大量特殊格式的原始数据，LIVE-SWE-AGENT 生成的自定义工具专门为此定制。当我们按仓库编程语言分解工具时（图 4c），也观察到类似结果。不同问题、环境与语言可能需要完全不同的特化工具，再次说明对所有问题使用同一套工具是次优的。
图 5：自定义工具示例　(a) 搜索工具　(b) Go 文件分析工具
有效且有趣的自定义工具。我们更仔细看几个 LIVE-SWE-AGENT 创造的有效且有趣的工具。图 5a 展示一个自定义搜索工具。该例乍看可能简单直接。但它实现了若干重要特性：（1）支持目录内聚焦搜索与基于模式的匹配；（2）搜索时忽略无关文件夹（__pycache__ 与 node_modules）以及隐藏文件夹（.git）；（3）显示找到代码前后的相关上下文；（4）把结果限制在前 20 条以减小上下文。通过在搜索工具中内置排除无关文件夹，智能体不必在搜索时再单独加这些开关。显示周围上下文也有帮助，因为我们常常想知道感兴趣的代码片段如何被使用。此外，只显示前 20 条匹配对避免急剧膨胀上下文窗口可能至关重要，使智能体能轻松收紧搜索。图 5a 顶部给出模拟该自定义工具功能的示例 bash 命令。
""",
        "工具不是「再实现一遍 grep」。好的搜索脚本默认跳过 .git 和 node_modules、带上下文、只吐前 20 条——这些是人用 bash 时最容易忘、也最容易把上下文撑爆的细节。openlibrary 簇说明：编目仓库会逼出 MARC 一类别人用不上的刀。固定工具箱对所有仓库发同一套扳手，这里被点名批评。",
    ),
    (
        """可以看到这条长命令在选项、参数与开关上的高度复杂。另一方面，我们只需调用 “python search_code.py ‘code’ src/” 即可通过自定义工具执行搜索。若只使用基本 bash 命令，智能体必须用复杂开关把多条命令链在一起，并可能引入错误（例如较旧的 grep 版本不支持 --exclude-dir 一类特性）或显著变慢。事实上，在我们的实验结果中，我们发现没有自定义工具时，智能体常常要走多步才能完成搜索相关代码这类基本任务。当像搜索这样的步骤在一个任务中需要做多次时，该问题会被进一步放大，从而急剧限制解题效率与有效性。通过创造并引入由智能体自己设计的高效、易用自定义工具，LIVE-SWE-AGENT 可以提升智能体在复杂软件工程任务上的表现。
图 5b 展示 LIVE-SWE-AGENT 创造的另一个自定义工具 go_analyzer.py。该工具可用于分析 Go 文件，查找任意 struct 与函数定义、标识符引用，并获取文件中使用的 import。此例展示了智能体强大的生成能力：自定义工具可被用作面向 Go 的简单静态分析器，以搜索并提供关于文件的关键信息。与前一个理论上尚可用 bash 命令（尽管是非常复杂的链式命令）模仿行为的搜索工具不同，这里的工具逻辑更复杂。自定义工具基于 Go 语法做策略性模式匹配，并提供支持多种不同用法的接口。此外，通过把该自定义工具存成可执行脚本，智能体可以多次复用该功能。通过创造并使用该自定义工具以更好理解文件结构与内容，LIVE-SWE-AGENT 解决了先前最佳基线未能解决的这一 issue³。
4.3 消融
为评估 LIVE-SWE-AGENT 不同设定的效果，我们使用 SWE-bench Verified 中随机 50 题的子集（问题列表见附录 C.1）。除非另有说明，消融实验使用 Claude 4.5 Sonnet。
造工具步骤的有效性。表 4 展示 LIVE-SWE-AGENT 不同组件对性能的影响。可以看到，去掉当场造工具能力（即使用基础 mini-SWE-agent）时解决率最低。当我们在初始提示中向智能体表明应创造自定义工具时（行「LIVE-SWE-AGENT w/o reflection」），性能有所提升。然而，一旦我们显式要求智能体在每一步之后反思既往轨迹以决定是否应创造任何工具，才达到最高解决率。实验中我们发现，这一反思过程为智能体提供了良好提醒，使其创造专门为该 issue 设计的工具。此外，虽然工具数量不必与解题性能相关，我们也看到相对只在初始提示中表明造工具，这一反思过程平均会创造更多工具。LIVE-SWE-AGENT 通过反思当前问题与既往轨迹来当场创造自定义工具，从而提升性能。
不同 LLM 后端。我们接着考察为 LIVE-SWE-AGENT 使用不同 LLM 后端的效果。表 5 在与上一消融相同的 50 题上，比较基础 mini-SWE-agent 与 LIVE-SWE-AGENT 随所用 LLM 变化的性能。
³navidrome__navidrome-10108c63c9b5bdf2966ffb3239bbfd89683e37b7，SWE-Bench Pro
""",
        "bash 等价命令又长又脆；Go 分析器已经不像「封装 grep」，更像现场写了个迷你语言服务器。消融预告：只在开场提一句，远不如步步提醒。下一页表 4、表 5 会把「反思」和「模型不够强会负优化」写成数。",
    ),
    (
        """表 4：SWE-bench Verified 子集上不同 LIVE-SWE-AGENT 设定的消融
方法　解决率　创造的工具数
LIVE-SWE-AGENT 无造工具　62.0%　0.00
LIVE-SWE-AGENT 无反思　64.0%　2.92
LIVE-SWE-AGENT　76.0%　3.28
表 5：同一子集上不同 LLM 后端的消融
LLM　mini-SWE-agent　LIVE-SWE-AGENT
GPT-5-Nano　44.0%　14.0%（↓-68.2%）
GPT-5-Mini　60.0%　58.0%（↓-3.3%）
GPT-5　60.0%　68.0%（↑13.3%）
Claude 3.7 Sonnet　46.0%　50.0%（↑8.7%）
Claude 4 Sonnet　58.0%　64.0%（↑10.3%）
Claude 4.5 Sonnet　62.0%　76.0%（↑22.6%）
我们首先观察到，对某些较弱的 LLM，用 LIVE-SWE-AGENT 当场造自定义工具甚至会降低性能。特别是 GPT-5-Nano，使用 LIVE-SWE-AGENT 的结果显著差于基础 mini-SWE-agent。检查轨迹后发现，GPT-5-Nano 未能理解创造自定义工具的目标，并常常卡在循环中，从而导致性能下降。这表明较弱 LLM 可能缺乏当场合成有用工具所需的高层推理能力。然而我们看到，随着使用更强模型，LIVE-SWE-AGENT 相对基础 mini-SWE-agent 的提升更大。具体地，Claude 4 Sonnet 与 GPT-5 等先进 LLM 在使用 LIVE-SWE-AGENT 相对 mini-SWE-agent 时取得最高的相对解决率提升。这展示了 LIVE-SWE-AGENT 在高性能 LLM 上的可泛化性，以及随着我们继续构建越来越强的 LLM，它进一步提升性能的潜力。
SWE-bench Multilingual。除在 SWE-bench Verified 与 SWE-Bench Pro 上评估外，我们也在其它基准上测试 LIVE-SWE-AGENT 的可泛化性。我们在 SWE-bench Multilingual [19] 的 50 题子集（列表见附录 C.2）上做了初步实验，该基准覆盖 9 种编程语言（JavaScript、TypeScript、Rust、Ruby、Go、C/C++、PHP 与 Java）的软件工程任务。表 6 给出相对 mini-SWE-agent 的表现。
""",
        "表 4：不造工具 62%，只开场提一句 64%，步步反思 76%。反思几乎不增加工具个数（2.92→3.28），却大幅涨点——关键不是「造得更多」，而是「造得更对症」。表 5 是冷水：GPT-5-Nano 从 44% 掉到 14%，会在造工具的循环里转圈。live 不是免费午餐，它假设模型已经会做一层元决策。",
    ),
    (
        """表 6：SWE-bench Multilingual 子集结果
工具　LLM　解决率　平均美元成本
mini-SWE-agent [42]　Claude 4.5 Sonnet　40.0%　$0.59
LIVE-SWE-AGENT　Claude 4.5 Sonnet　46.0%　$0.66
我们观察到 LIVE-SWE-AGENT 以 46.0% 的解决率取得更好表现，而 mini-SWE-agent 仅为 40.0%。这展示了它在额外挑战性问题上的可泛化性。
4.4 讨论与未来工作
走向通用的当场自演化。本文中，LIVE-SWE-AGENT 主要聚焦通过自定义工具的创造与使用使智能体自演化。如前所述，其关键想法——当场改进并修改智能体自身——不仅包括创造新工具，也包括修改整个智能体实现。这包括智能体的总体系统提示、它如何与环境交互，甚至它尝试解决问题时的具体工作流。我们相信，整个智能体循环可以像任何其它软件一样被修改与改进，尤其是基于解题过程中获得的反馈与洞察当场进行。此外，我们希望把自演化循环扩展到不同任务之间。不是在任务完成后丢弃每个已演化的智能体，我们可以保存并序列化有用的工具与洞察（通过 Skills [5] 一类概念）供未来任务使用。智能体随后可以当场加载这些在先前任务中获得的有用工具与洞察，以进一步提升性能并支持跨任务的持续自演化。
对 LLM 评测的影响。我们在多个基准、多个 LLM 上的实验结果表明，LIVE-SWE-AGENT 可以达到先进性能。这说明它可以作为在软件开发 issue 求解上统一评估 LLM 性能的有效脚手架。不必使用复杂或专有的智能体脚手架，它提供简单、轻量的做法，可轻易叠在任何智能体设计之上以评估 LLM。而且它不仅评估 issue 求解能力，还可以测试 LLM 与智能体的造工具能力。工具是智能体最重要的方面之一，并直接影响 issue 求解性能。LLM 创造自定义工具、尤其是为解决复杂软件开发 issue 而创造的能力，尚未被广泛评估。为此，我们已在评估中看到一些有趣结果：较弱 LLM 缺乏当场创造有用工具的高层推理（见第 4.3 节）。LIVE-SWE-AGENT 提供了一个独特框架，可联合评估 LLM 的造工具与 issue 解决能力。
""",
        "多语言子集再涨 6 个点，说明不单吃 Python。§4.4 把野心写大：下一步要改提示、改工作流、还要把有用工具存成 Skills 跨任务加载。评测上作者想一箭双雕——既比谁会修 issue，也比谁会现场造工具。弱模型会被双重惩罚，读表 5 时要记得这把双刃剑。",
    ),
    (
        """超出软件 issue 求解任务的应用。除软件 issue 求解外，LIVE-SWE-AGENT 可轻易应用于其它有挑战的软件工程任务，如生成测试 [16]、检测并修补漏洞 [21]、以及从零合成可投产软件 [48]。相对 issue 求解，其它软件问题域将需要更加任务特定、多样的工具与智能体脚手架。例如，要在商业成品二进制中检测恶意漏洞，我们需要二进制分析工具与反编译器。要优化大型复杂系统，我们需要应用 profiler 与追踪工具。不必使用无法适配不同问题域的固定脚手架加基本工具，也不必为每个任务辛苦设计专门智能体，LIVE-SWE-AGENT 可以通过基于当前任务当场自动修改自身，轻易泛化到不同域的任务求解。
LLM 训练期间的自演化。本文中，LIVE-SWE-AGENT 实现为对现有智能体的轻量修改，不需要离线训练或更新。然而，当场自演化的想法也可以轻易扩展到 LLM 训练：不是从固定工作流与静态工具集学习，LLM 在训练中也学习创造新工具并修改脚手架本身。在这种方法中，得到的 LLM 将拥有更强的推理能力，因为自演化训练提供额外学习信号，使 LLM 能解决更复杂的任务。通过自演化训练，LLM 可以学会更好地创造有用、任务特定的工具，并根据当前问题动态修改高级脚手架。而且，最终训练出的 LLM 将与更多运行时智能体框架兼容，因为它能从自己创造的工具与修改过的脚手架中学习，而不是依赖预定义脚手架。这种适应性使其更稳健，并能有效泛化到新的脚手架设定甚至不同任务。
相关工作
5.1 软件工程智能体
受人类调试过程启发——开发者与环境反馈（如测试失败）交互并从先前尝试中学习——ChatRepair [39, 40] 提出了第一个基于 LLM 的交互式修 bug 方案。自 ChatRepair 以来，大量关于修 bug 与一般编码任务的研究工作旨在通过多轮对话自动为 LLM 提供更多上下文信息 [13, 20, 43]。最近，基础 LLM 在工具使用与推理能力上取得实质进展，将反馈驱动方案进一步装备这些涌现的 LLM 能力变得非常自然。2024 年 3 月，Devin AI 发布了第一个 AI 软件工程师，可以完全自主完成端到端软件任务，例如 GitHub issue 解决 [15]。Devin 的初始发布在含数千真实 GitHub issue 的 SWE-bench [18] 上展示了 13.86% 的可观解决率。此后，大量专门的软件智能体脚手架被提出，包括 SWE-agent [41]、OpenHands [34]、AutoCodeRover [47] 与 Trae Agent [24]。这类软件智能体通常为 LLM 配备一套编码工具，并鼓励 LLM 自主决定完成真实软件任务的下一步动作。与主流软件智能体不同，研究者也提出了基于预定义工作流的各种 AI 软件工程师方案，以挑战复杂智能体设计的必要性，例如 Agentless [37] 与 Moatless [49]。
此外，近期 LLM 越来越多地在海量真实软件数据上做后训练，以更好解决软件工程 issue，包括 SWE-RL [36]、DeepSWE [25]、DeepSeek V3.1 [3]、MiniMax M1/M2 [11]、Kimi K2 [31]、SWE-1.5 [14] 以及 Code World Model（CWM）[10]。
由于软件智能体的巨大设计空间，构建最优智能体脚手架可能极度困难且昂贵。因此，最近提出了若干自改进软件智能体，包括 Self-Improving Coding Agent（SICA）[30]、达尔文–哥德尔机（DGM）[45] 与 Huxley-Gödel Machine（HGM）[33]。然而，这类自改进智能体需要在已知基准上做昂贵离线训练，并且在不同 LLM、基准与 issue 类型之间未必泛化良好。在软件工程域之外，先前工作 [9, 32, 28, 27, 35] 探索用 LLM 为一般推理或具身任务创造工具，但它们不以真实软件工程问题为目标。相比之下，本文提出 LIVE-SWE-AGENT，第一个能够在解决真实 issue 的运行时进行实用当场自演化的 live 软件智能体。这样，它完全不需要离线训练
""",
        "展望加相关工作。作者认为测漏洞、写测试、从零写库更需要特化工具，live 架子反而更合适。训练期自演化还只是设想。文献谱系：ChatRepair → Devin 13.86% → SWE-agent / OpenHands 对 Agentless；自改进一支是 DGM；造工具一支点名 LATM [9]。这篇给自己的位置是：不离线、对着真实仓库。",
    ),
    (
        """并且可以轻易泛化到不同 LLM 与 issue 域。而且，它也展示了相对所有现有自改进软件智能体的优越性能。
5.2 软件工程智能体基准
为评估并展示软件工程智能体的性能，已提出大量数据集。SWE-bench [18] 是最早、使用最广泛的软件智能体基准数据集之一。除包含数千真实 GitHub issue 的初始 SWE-bench 外，研究者也构建了高质量、有代表性的精选子集以支持更快、更可靠的评估，包括 SWE-bench Lite [18] 与 SWE-bench Verified [26]。由于 SWE-bench 大多聚焦 Python 项目，研究者提出若干 SWE-bench 风格的多语言项目基准以更全面地评估智能体，包括 SWE-PolyBench [29]、SWE-bench Multilingual [19] 与 Multi-SWE-bench [44]。此外，SWE-bench 严重依赖人工收集实例与搭建可执行环境，难以扩展；因此研究者也利用软件智能体来理顺 issue 收集与环境搭建，以构建 live、可扩展的基准，包括 SWE-bench-Live [46] 与 SWE-rebench [8]。最近，Scale AI 还构建了 SWE-Bench Pro [4]，旨在捕捉比 SWE-bench 更真实、复杂、企业级的 issue。为对 LIVE-SWE-AGENT 做严格评估，我们的研究涉及多个广泛使用的基准，包括 SWE-bench Verified、SWE-bench Multilingual、SWE-bench Pro。
结论
本文提出 LIVE-SWE-AGENT，第一个能够在解决真实软件问题的运行时自主、持续地当场自演化的 live 软件智能体。更具体地，它从最基本的、仅能访问 bash 工具的智能体脚手架出发，在解决真实软件问题的同时自主演化自己的脚手架实现。我们在广泛研究的基准（如 SWE-bench Verified 与 SWE-bench Pro）上的评估表明，LIVE-SWE-AGENT 超过最先进的人工设计软件智能体，为 live、自演化的软件智能体展示了可观前景。
参考文献
[1] GPT-5.1. https://openai.com/index/gpt-5-1-for-developers/.
[2] kimi-k2-thinking. https://moonshotai.github.io/Kimi-K2/thinking.html.
[3] DeepSeek AI. DeepSeek V3.1. https://api-docs.deepseek.com/news/news250821.
[4] Scale AI. Swe-bench pro: Can ai agents solve long-horizon software engineering tasks? arXiv preprint arXiv:2509.16941, 2025.
[5] Anthropic. Introducing Agent Skills. https://www.claude.com/blog/skills.
[6] Anthropic. Claude Sonnet 4.5, 2025. https://www.anthropic.com/news/claude-sonnet-4-5.
[7] Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le, and Charles Sutton. Program synthesis with large language models. arXiv preprint arXiv:2108.07732, 2021.
[8] Ibragim Badertdinov et al. Swe-rebench: An automated pipeline for task collection and decontaminated evaluation of software engineering agents. arXiv preprint arXiv:2505.20411, 2025.
[9] Tianle Cai, Xuezhi Wang, Tengyu Ma, Xinyun Chen, and Denny Zhou. Large language models as tool makers. In International Conference on Representation Learning, volume 2024, pages 54067–54089, 2024.
""",
        "基准谱系一页说清：Lite / Verified 是精选，Multilingual / Poly / Multi 是跨语言，Live / rebench 想自动扩，Pro 想更企业。结论收束主张：从 bash-only 起步，当场改自己。文献 [9] 正是馆藏里的 LATM——两篇对照读，一个摊成本造通用函数，一个对着仓库造一次性脚本。",
    ),
    (
        """[10] Quentin Carbonneaux et al. Cwm: An open-weights llm for research on code generation with world models. arXiv preprint arXiv:2510.02387, 2025.
[11] Aili Chen et al. Minimax-m1: Scaling test-time compute efficiently with lightning attention. arXiv preprint arXiv:2506.13585, 2025.
[12] Mark Chen et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021.
[13] Xinyun Chen, Maxwell Lin, Nathanael Schärli, and Denny Zhou. Teaching large language models to self-debug. arXiv preprint arXiv:2304.05128, 2023.
[14] Cognition. SWE-1.5. https://cognition.ai/blog/swe-1-5.
[15] Cognition. Devin AI, 2024. https://cognition.ai/blog/introducing-devin.
[16] Yinlin Deng, Chunqiu Steven Xia, Haoran Peng, Chenyuan Yang, and Lingming Zhang. Large language models are zero-shot fuzzers: Fuzzing deep-learning libraries via large language models. In ISSTA, 2023.
[17] Geoffrey E Hinton and Sam Roweis. Stochastic neighbor embedding. Advances in neural information processing systems, 15, 2002.
[18] Carlos E Jimenez et al. Swe-bench: Can language models resolve real-world github issues? arXiv preprint arXiv:2310.06770, 2023.
[19] Kabir Khandpur et al. Swe-bench multilingual, 2025. https://www.swebench.com/multilingual.html.
[20] Jiaolong Kong et al. Contrastrepair: Enhancing conversation-based automated program repair via contrastive test case pairs. ACM TOSEM, 2025.
[21] Hwiwon Lee, Ziqi Zhang, Hanxiao Lu, and Lingming Zhang. SEC-bench: Automated Benchmarking of LLM Agents on Real-World Software Security Tasks. NeurIPS, 2025.
[22] Yujia Li et al. Competition-level code generation with alphacode. arXiv preprint arXiv:2203.07814, 2022.
[23] Junwei Liu et al. Large language model-based agents for software engineering: A survey. arXiv preprint arXiv:2409.02977, 2024.
[24] Yizhou Liu et al. Marscode agent: Ai-native automated bug fixing. arXiv preprint arXiv:2409.00899, 2024.
""",
        "参考文献续：SWE-bench 原文、Devin、Codex 论文、自调试、t-SNE。书目保留英文。需要对照「智能体脚手架史」时，[15] Devin 与 [18] SWE-bench 是两条主线的起点。",
    ),
    (
        """[25] Michael Luo et al. Deepswe: Training a fully open-sourced, state-of-the-art coding agent by scaling rl.
[26] OpenAI. SWE-bench Verified, 2025. https://openai.com/index/introducing-swe-bench-verified/.
[27] Cheng Qian et al. Creator: Tool creation for disentangling abstract and concrete reasoning of large language models, 2024.
[28] Jiahao Qiu et al. Alita: Generalist agent enabling scalable agentic reasoning with minimal predefinition and maximal self-evolution, 2025.
[29] Muhammad Shihab Rashid et al. Swe-polybench: A multi-language benchmark for repository level evaluation of coding agents. arXiv preprint arXiv:2504.08703, 2025.
[30] Maxime Robeyns, Martin Szummer, and Laurence Aitchison. SICA a self-improving coding agent. ICLR 2025 Workshop, 2025.
[31] Kimi Team. Kimi k1.5: Scaling reinforcement learning with llms. arXiv preprint arXiv:2501.12599, 2025.
[32] Guanzhi Wang et al. Voyager: An open-ended embodied agent with large language models. TMLR, 2024.
[33] Wenyi Wang et al. Huxley-gödel machine: Human-level coding agent development by an approximation of the optimal self-improving machine, 2025.
[34] Xingyao Wang et al. Openhands: An open platform for ai software developers as generalist agents. arXiv preprint arXiv:2407.16741, 2024.
[35] Zhiruo Wang, Daniel Fried, and Graham Neubig. Trove: Inducing verifiable and efficient toolboxes for solving programmatic tasks, 2024.
[36] Yuxiang Wei et al. Swe-rl: Advancing llm reasoning via reinforcement learning on open software evolution. arXiv preprint arXiv:2502.18449, 2025.
[37] Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, and Lingming Zhang. Agentless: Demystifying llm-based software engineering agents. arXiv preprint arXiv:2407.01489, 2024.
[38] Chunqiu Steven Xia and Lingming Zhang. Less training, more repairing please: revisiting automated program repair via zero-shot learning. ESEC/FSE, 2022.
[39] Chunqiu Steven Xia and Lingming Zhang. Conversational automated program repair. arXiv preprint arXiv:2301.13246, 2023.
[40] Chunqiu Steven Xia and Lingming Zhang. Automated program repair via conversation: Fixing 162 out of 337 bugs for $0.42 each using chatgpt. ISSTA, 2024.
""",
        "参考文献续：SICA、HGM、OpenHands、Agentless、ChatRepair、CREATOR、Voyager。自演化对照读 [30][33][45]；「少一点智能体」对照读 [37]。书目保留英文。",
    ),
    (
        """[41] John Yang et al. Swe-agent: Agent-computer interfaces enable automated software engineering. NeurIPS, 2024.
[42] John Yang et al. SWE-agent: Agent-computer interfaces enable automated software engineering. NeurIPS, 2024.
[43] Zhiqiang Yuan et al. Evaluating and improving chatgpt for unit test generation. Proc. ACM Softw. Eng., 2024.
[44] Daoguang Zan et al. Multi-swe-bench: A multilingual benchmark for issue resolving. arXiv preprint arXiv:2504.02605, 2025.
[45] Jenny Zhang, Shengran Hu, Cong Lu, Robert Lange, and Jeff Clune. Darwin godel machine: Open-ended evolution of self-improving agents. arXiv preprint arXiv:2505.22954, 2025.
[46] Linghao Zhang et al. Swe-bench goes live! arXiv preprint arXiv:2505.23419, 2025.
[47] Yuntong Zhang, Haifeng Ruan, Zhiyu Fan, and Abhik Roychoudhury. Autocoderover: Autonomous program improvement. ISSTA, 2024.
[48] Wenting Zhao et al. Commit0: Library generation from scratch. arXiv preprint arXiv:2412.01769, 2024.
[49] Albert Örwall. Moatless, 2024. https://github.com/aorwall/moatless-tools.
A 额外实验设置
我们现在描述 LIVE-SWE-AGENT 评估所用的额外实验设置。如第 3 节所述，我们在 mini-SWE-agent 框架上实现它。撰文时我们使用与 mini-SWE-agent 相同的默认超参数（每 issue 最大步数 250、最大成本 3 美元）。
对 Gemini 3 Pro，我们使用温度 1，因为这是开发者所推荐的⁴。对实验中的任何 Anthropic 模型，我们遵循 mini-SWE-agent，使用温度 0.0。对任何 OpenAI 模型（如 GPT-5、GPT-5-Mini、GPT-5-Nano），由于不支持温度 0.0 采样，我们使用温度 1。据我们所知，mini-SWE-agent 在使用 OpenAI 模型时也是如此。
B 额外工具分析
图 6：Claude 4.5 Sonnet 在 SWE-bench Verified 与 SWE-Bench Pro 上生成工具的额外二维 t-SNE 可视化。我们按仓库名（图 6a）与工具名（图 6b）标注嵌入。
我们做了与第 4.2 节类似的额外工具分析，补上 Verified 按仓库、Pro 按工具名的可视化。Verified 全是 Python 仓库，故未按语言分解。观察模式与主评估类似。分析使用 sklearn 的 PCA（n_components=50）再接 t-SNE（max_iter=1000）。
C 消融所用问题
C.1 SWE-bench Verified 消融子集
以下是消融评估中随机选取的 50 道 SWE-bench Verified 问题（sympy、django、scikit-learn、matplotlib、sphinx 等实例 id）。
⁴https://ai.google.dev/gemini-api/docs/gemini-3
""",
        "文献收束到 DGM [45]、SWE-agent、Moatless。附录 A 交代温度：Gemini / GPT-5 系列用 1（后者还不支持 0），Claude 用 0。附录 C 开始列出 50 道消融题 id，便于复现，不必精读每一条。",
    ),
    (
        """（续）SWE-bench Verified 消融 50 题实例 id 列表，以及 C.2 SWE-bench Multilingual 消融子集的 instance_id 列表（apache/druid、ruff、axios、caddy、ripgrep、three.js、redis、rubocop、axum 等，覆盖多语言）。
""",
        "附录 C 的实例名单续页：Verified 50 题 + Multilingual 50 题。正文表 4–6 的分母就在这里。除非你要复现消融，否则扫一眼语言覆盖面即可。",
    ),
    (
        """（续）Multilingual 子集剩余 id（tokio、coreutils、valkey、vuejs 等）。
D 所用提示
我们给出 LIVE-SWE-AGENT 使用的详细提示。注意提示的主体由 mini-SWE-agent 构造，我们只做最小改动以启用当场造工具。此外有一处轻微修改：在所有 SWE-Bench Pro 评估的初始提示中，把测试床主目录指示从 testbed 改为 app。因为 Pro 的 docker 环境用 app 作为含仓库代码的主源目录，与 SWE-bench 环境不同。除此之外，所有评估使用同一提示。
D.1 初始提示
Initial prompt for LIVE-SWE-AGENT
（提示原文保留英文：含 PR 描述、一次只发一条 bash、THOUGHT + 单个代码块、不要改测试文件、推荐工作流等。主体来自 mini-SWE-agent。）
""",
        "附录 D 开始：作者强调自己几乎没改循环，只在 mini-SWE-agent 的长提示上打补丁。Pro 环境根目录叫 app 不叫 testbed，所以换了一个词。提示要求每次只回一条 bash，并带 THOUGHT——这是后面「造工具 = 再写一个 cat <<EOF」能接上的前提。",
    ),
    (
        """**CRITICAL REQUIREMENTS:** 响应必须恰好包含一个 bash 代码块、其中恰好一条命令（或用 && / || 连接的一组）。零个或多个块都会失败。目录与环境变量更改不持久。
后接正确 / 错误响应示例、环境细节、用 heredoc 创建文件、用 nl/sed 查看行号等（原文保留英文）。
**IMPORTANT TOOL CREATION INSTRUCTIONS**
## Creating your own tools
- 你也可以用 Python 创造自己的工具来帮助工作流
- 相对基本 bash，所造工具应能更好帮助完成本任务
- 每个工具应为 Python、含有信息量的输出或报错、并可从命令行运行
- 你至少应创造一个简单的编辑工具，以有效编辑任意文件，而不是使用 bash 命令
- 工具可以用于任何目的，不必通用；思考它如何具体帮助当前任务
随后是用 cat <<'EOF' 写 /path/to/tool_name.py 的示例（原文保留英文）。
""",
        "本页才是「最小改动」的实体：在原有「一次一条 bash」军规下面，加了造工具专章——至少做一把编辑器，工具不必通用，用 heredoc 写出 Python。和 LATM 的三阶段流水线不同，这里没有独立的验证模型，质检就是环境跑起来看。",
    ),
    (
        """（初始提示中造工具示例的剩余部分，以及 D.2 每步追加的反思消息，原文保留英文。反思大意：回顾过去步骤，思考是否有任何工具可以创造以帮助当前任务。）
""",
        "提示最后一页：示例工具写完，再给出步步追加的 REFLECT 句。表 4 里 64% 变 76% 的那个开关，物理形态就是环境反馈后面多贴的这一句。全文到此结束。对照阅读时，把附录 D 和 §2.1 对着看，会发现方法章节几乎没有藏额外算法。",
    ),
]


def main() -> None:
    assert len(PAGES) == 20, len(PAGES)
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
