#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Continue page_zh translations for pages 57–72."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "page_zh"
OUT.mkdir(exist_ok=True)

pages = {}

pages[57] = r"""积逆 ctx.dispose，故子效应的逆本身是父上的效应，这正是 𝜕2Γ 的递归结构。组件层（第 5.1.3 节）以测试 fiber.target 稳定性而非 armed 的守卫复用同一 execute。
5.1.2.  余效应操作
本节实现反应式余效应（第 3.2 节）。所有余效应操作作用于每个上下文所携带的三个符号键槽位：
• @@store：值存储 𝜎: (𝑟: 𝑅) ⇀𝒱︀𝑟，从领域符号到类型化值；
• @@isolate：领域表 𝜌: Map(𝐾, 𝑅)，从余效应键到领域符号；
• @@intercept：拦截表 𝜄: (𝑘: 𝐾) →ℳ︀𝑘，为每个键赋予其元数据。
前二者组成两层解析 𝑘→𝜌(𝑘) →𝜎(𝜌(𝑘))：ctx.get(key)
（算法 2）从 @@isolate 读取领域符号 𝜌(𝑘)，再从 @@store 读取绑定值 𝜎(𝜌(𝑘))。𝜌 间接层使隔离可将键重定向到独立绑定，而 @@intercept 仅在访问绑定时被咨询，调整其使用方式而非解析到什么。我们分两部分实现这些操作：(1) 提供与通知，安装或撤回绑定并将变更传播到依赖方；(2) 隔离与拦截，重塑键的解析方式。
提供与通知。因 set(𝑘, 𝑣) 具有类型 𝔈Σ（第 3.1 节），余效应提供是一次 ctx.effect 调用，并继承其自动跟踪与恢复。算法 2 实现 ctx.set(key, value)，即具体的 set(𝑘, 𝑣)：回调在领域符号 𝜌(𝑘) 下将值绑定进存储，返回的 dispose 函数将其移除。安装与移除都调用 notify，以将变更传播到依赖组件。
算法 2 余效应操作
1
function get(ctx, key)
2
realm ← ctx[@@isolate][key] ▷ 𝜌(𝑘)
3
return ctx[@@store][realm] ▷ 𝜎(𝜌(𝑘))
4
function set(ctx, key, value)
5
function callback()
6
realm ← ctx[@@isolate][key] ▷ 𝜌(𝑘)
7
ctx[@@store][realm] ← value ▷ 𝜎[𝜌(𝑘) ↦𝑣]
8
notify(ctx, [key])
9
return function()
10
delete ctx[@@store][realm] ▷ 𝜎∖𝜌(𝑘)
11
notify(ctx, [key])
12
return ctx.effect(callback)
算法 3 通过如下方式将每次绑定变更传播到依赖方：对每个存活纤程，测试变更键是否出现在其 fiber.inject 中且解析到同一领域；若是，则调用 refresh（第 5.1.3 节）对照新状态重新求值该纤程，并返回它所重新求值的纤程，以便调用方可等待它们。这正是定义 26 的反应式分类：翻转满足性的变更激活或停用纤程，而 refresh 的幂等性使中性变更无害。这种重新求值与多样控制流的交互在第 5.1.3 节展开。
57"""

pages[58] = r"""算法 3 反应式通知
1
function notify(ctx, keys)
2
affected ← ⌀
3
for fiber in all_fibers do
4
for key in keys do
5
if key ∈ fiber.inject and fiber.ctx[@@isolate][key] = ctx[@@isolate][key] then
6
refresh(fiber)
7
affected ← affected ∪ {fiber}
8
break
9
return affected
绑定仅当安装它的纤程为 ACTIVE 时才对依赖方可用，因此 refresh 对照活动提供方而非仅对照存储来解析每个声明的键。这正是定义 46 的“由……提供”关系，也使撤回在实际发生前一步对依赖方可见：已进入 UNLOADING 的提供方停止提供，故其依赖方重算得到不满足的目标视图，并在其绑定仍全部就位时开始各自的拆除。
隔离与拦截。两个操作在结构上做同一件事：各自派生一个子上下文，为 key 调整一张继承表，而不触动父，故恢复是隐式的——丢弃子上下文即足，无需运行显式逆。ctx.isolate(key, realm) 用 realm（默认新鲜生成的符号）覆盖领域映射 𝜌（实现 isolate，定义 29），故为同一键赋予不同符号的两个上下文解析到独立绑定。ctx.intercept(key, metadata) 将 metadata 合并进拦截表 𝜄（实现 intercept，定义 31）：依该定义，新元数据与上下文已为 key 携带者组合，并优先于后者。
5.1.3.  组件生命周期
组件由 ctx.use 实例化为纤程。本节赋予纤程（第 5.1 节引入）作为第 4.3.3 节惯性状态机的操作含义。下述算法由两个字段驱动：fiber.parent，形成组件层次的 fiber.ctx 的父上下文（Γ∞ 的递归结构，第 3.3.1 节）；以及 fiber.inertia，飞行中异步迁移的句柄（空闲则为 null）。
算法 4 展示组件实例化。组件将余效应规约 component.inject（𝑑）与效应函数 component.apply 配对；实例化将组件的 config 绑定进 fiber.apply（第 9 行），即生命周期随后运行的、已应用配置的效应函数（𝑒）。callback 函数（第 2 行）是在父纤程中跟踪的效应：执行时，它通过调用 refresh（算法 5）启动子的生命周期；恢复时，它将子的 target 强制为 ⊥ 并触发 unload。这正是定义 47 的注册原语，callback 为其 O-Insert，callback 返回的闭包为其 O-Retire：实例化是父的普通被跟踪效应，故卸载父会级联到其子。
算法 4 组件实例化
1
function use(ctx, component, config)
58"""

pages[59] = r"""2
function callback()
3
refresh(fiber)
4
return function()
5
fiber.target ← ⊥
6
unload(fiber)
7
fiber ← Fiber(parent: ctx, inject: component.inject)
8
fiber.ctx ← ctx[fiber ↦ fiber]
9
fiber.apply ← () ↦ component.apply(fiber.ctx, config)
10
ctx.effect(callback)
11
return fiber
算法 5 实现第 4.3.3 节的惯性状态机，其中 reload 与 unload 是惯性的：一旦进入，迁移运行至完成，系统才响应目标状态变更。它使用对余效应存储的两个辅助查找：resolve(inject) 返回声明键当前解析到的绑定，provided(fiber) 返回本纤程安装其绑定的那些键。refresh 函数从余效应存储重算 fiber.target，若纤程尚未处于迁移中，则启动 reload 或 unload 任务2。reload 函数记录当前目标并执行组件的效应函数 apply。完成后，它检查目标是否仍匹配：若是，纤程进入 ACTIVE；若否（无论新目标是 ⊥ 还是不同的提供方集合），则链接到 unload。对称地，unload 按 LIFO 顺序恢复所有被跟踪效应，然后要么进入 INACTIVE，要么链接到 reload。这种相互递归实现惯性性质：一旦迁移开始，它在任何新迁移可开始之前完成。
算法 5 组件生命周期
1
function refresh(fiber)
2
target ← target(𝛾, 𝑛)
3
if target = fiber.target then return
4
fiber.target ← target
5
if fiber.inertia then return
6
if target ≠ ⊥ then
7
fiber.state ← LOADING
8
fiber.inertia ← create_task(reload(fiber))
9
else
10
fiber.state ← UNLOADING ▷ 在调度任何逆之前退出服务
11
fiber.inertia ← create_task(unload(fiber))
12
async function reload(fiber)
13
target0 ← fiber.target
14
fiber.committed ← resolve(fiber.inject) ▷ 提交视图
15
recover ← await execute(fiber.apply, () ↦ fiber.target = target0)
16
fiber.dispose ← recover ∘ fiber.dispose
17
if fiber.target = target0 then
18
fiber.state ← ACTIVE
2create_task 调度异步函数并发运行并返回其句柄（存于 fiber.inertia）。我们显式写出以保持语言无关：在急切调度（如 TypeScript promise）下，调用是隐式的，返回的 promise 即句柄；而在惰性调度（如 Python 协程、Rust future）下，宿主必须生成任务才能推进。
59"""

pages[60] = r"""19
notify(fiber.ctx, provided(fiber))
20
fiber.inertia ← null
21
else
22
fiber.state ← UNLOADING
23
fiber.inertia ← create_task(unload(fiber))
24
async function unload(fiber)
25
await all(notify(fiber.ctx, provided(fiber)).map(f ↦ f.await())) ▷ 排空依赖方
26
await fiber.dispose()
27
fiber.dispose ← id
28
fiber.committed ← ⊥
29
if fiber.target = ⊥ then
30
fiber.state ← INACTIVE
31
fiber.inertia ← null
32
else
33
fiber.state ← LOADING
34
fiber.inertia ← create_task(reload(fiber))
fiber.target 通过对当前余效应存储解析每个声明键、并将提供它的纤程的 uid 成组而计算，故它是 target(𝛾, 𝑛)（定义 46）的摘要。用提供方而非值来标识绑定，正是使与已记录目标的单次比较即足的原因：uid 新鲜抽取且从不复用，故被替换的提供方不会被误认为它所替换者，即使二者提供相等的值。
因 notify（第 5.1.2 节）在每次余效应变更时重算目标，纤程恰在其某个声明键改由不同纤程提供时重载。因此，提供方就地覆写其自身绑定不可被观察到；希望其替换得以传播的组件须撤回绑定并重新安装。
算法在两个互补层面运作。在迁移层，reload 与 unload 在完成时检查目标，实现跨迁移的惯性链接。在每次迁移内的迭代层，效应执行（算法 1）在每个迭代边界检查目标，实现单次迁移内的部分回滚。这两种机制对应于第 4.3.3 节的迁移间链接，以及定理 64 所依赖的迁移内陈旧性检查。
三行承载定理 63 的余效应次序，而每一行所处位置正是使该次序成立的原因。reload 在第 14 行提交已解析视图，unload 仅在每个逆都运行之后才丢弃它，故纤程在其已加载期间——包括其自身拆除——都读取相同绑定。refresh 在第 10 行、于创建迁移任务之前将纤程标为 UNLOADING，这正是 L-Leave 步：纤程停止提供，依赖方在调度其任何逆之前对照这一点重算。unload 随后在第 25 行等待每个被通知的依赖方到达 INACTIVE，这正是 L-Unload 上的守卫；notify 仅当依赖方的声明键解析到与提供方相同的领域符号时才接纳它，这是守卫要求依赖方从本纤程看到该键、而非仅仅声明它的运行时形式。等待位于整个恢复之前，而非位于被等待的某个逆之内，因为 fiber.dispose 并发启动纤程的效应，把等待放在其中之一内部会使其余者无序。终止性依循定理 66：纤程只等待已停止可满足的依赖方，而本身也是提供方的依赖方以同样方式等待其自己的依赖方，故提供方图按需遍历而非事先分析。
60"""

pages[61] = r"""5.1.4.  上下文访问
第 5.1.2 节的余效应操作构成反射式 API：用 ctx.set(key, value) 写余效应，用 ctx.get(key) 读，二者皆按名键控。Cordis 在此反射式 API 之上叠放第二种、更原生的扩展与消费上下文的方式：属性访问。组件可将余效应作为属性 ctx[key] 访问，仿佛它是上下文的原生结构，而非通过方法调用。在 TypeScript 中，Cordis 用 Proxy 实现这一点，其 get 陷阱中介每一次属性访问。算法 6 展示上下文如何将对余效应的此种访问解析到第 5.1.2 节的原语 get 之上。
算法 6 代理中介的上下文访问
1
function resolve(ctx, key)
2
fiber ← ctx.fiber
3
repeat
4
if key ∈ fiber.committed then return fiber.committed[key]
5
if key ∈ fiber.inject then throw INACTIVE_ACCESS
6
if fiber = root then throw UNDECLARED_ACCESS
7
fiber ← fiber.parent.fiber
算法 6 从访问上下文沿纤程链向上行走：在第一个其已提交视图绑定 key 的纤程处，访问被授权并返回该绑定；若行走到达声明了 key 但尚未提交它的纤程，则该纤程未加载，访问失败；若到达根且无任何声明，则访问作为未声明而被拒绝。这正是代理与裸 ctx.get 的不同之处：ctx.get(key) 是对照存储的查找，返回绑定值或空且从不失败，而代理对照访问纤程自身的视图解析，并在使用点强制余效应规约 𝑑。读取视图而非存储也是定理 63 所依赖的，因为它使由该依赖消失所触发拆除的组件仍可读到该依赖。
这种拒绝是在访问点执行的运行时检查。因组件的余效应规约 𝑑 静态声明，原则上同一违例可在编译时检测——在执行前对照声明的 𝑑 解析每个 ctx[key]；第 6.4 节讨论宿主语言的类型级依赖声明与编译时元编程如何恰好完成此种中介。
5.2.  组件加载器
核心库为组件开发者配备动态组合的命令式原语，如 ctx.effect、ctx.use 与 ctx.set。对应用编排器则出现另一关切：他们将既有组件装配为运行系统，并在其生命周期中调整组合。组件加载器通过引入声明式配置层来应对这一关切：编排器将期望组合指定为持久数据结构，加载器将该规约的变更翻译为相应的命令式纤程操作。
61"""

pages[62] = r"""5.2.1.  声明式配置
第 4 节将运行系统分解为纤程，每个纤程是一个组件的一次实例化。实例化所需的一切都可声明，故编排器可将整个系统描述为声明式配置：加载器将其实现为纤程并与之保持同步的持久记录。
条目。配置由条目组成。每个条目指定一个纤程并管理它，绑定双向运行：加载器响应条目字段的变更以调整纤程，而修订自身配置或禁用自身的组件则把变更写回其条目。
定义 74. 条目声明单个纤程，记录：
• id — 稳定标识符，在其组的子列表变更时用作调和键；
• url — 待实例化组件模块的 URL；
• isolate — 应用于条目上下文的隔离注解；
• intercept — 应用于条目上下文的拦截注解；
• config — 绑定进组件以形成其效应函数 apply 的配置；
• disabled — 条目是否被管理性地关闭。
条目可作为忠实规约，因为支撑纤程的恰是条目所记录者。定义 67 的支持集读 𝜏、𝜋、𝑑 与 𝑝 且别无其他，而条目给出全部四者：disabled 给出 𝜏，条目在树中的父给出 𝜋，url 选定声明 𝑑 与 𝑝 的组件。支持集未读的字段是纤程的运行时状态，实例化也不需要它们；引理 70 在每个组件安装其所声明每个键（定义 69）的范围内，将支持集与静默状态（定义 49）的 𝖠𝖼𝗍𝗂𝗏𝖾 纤程等同。
这些条目形成配置树，是系统加载内容的权威记录。条目可以是映射到单个纤程的叶，或其组件又可加载更多组件，使条目成为分支节点。Cordis 为这种分组与嵌套加载提供组件：@cordisjs/group 以子条目列表为其配置并将它们作为子组加载，@cordisjs/include 加载外部配置文件（YAML 或 JSON）并将其条目嫁接为嵌套子树。二者都是建立在定义 47 注册原语（算法 4）上的普通组件，故嵌套树留在演算之内，下文结果对之成立。
调和。当条目的记录变更时，加载器增量调和，而非整体拆除并重建纤程。如此调和之所以可靠，是元理论所供给的理由。
• 定理 73 使静默状态仅为最终配置的函数：无论加载器途中执行何种实例化与退役、以何种次序，系统都静默于从零加载最终配置所会留下之处。最终哪些组件被加载，仅在每个组件安装其所声明每个键（定义 69）的范围内由声明读出；只在某些配置下才安装所声明键的组件，加载器仍可调和，但已加载组件之集于是也回答那些配置。
• 定理 66 证明系统确实静默，故一旦发出其实例化与退役，调和即完成。
• 推论 62 使离去纤程对状态的贡献为零，故重建一个条目撤回其纤程所安装者，并使其周围纤程保持原样。
62"""

pages[63] = r"""• 定理 63 允许条目一并实例化，编排器无需安排加载次序：声明键尚未被提供的纤程在其 L-Begin 处等待，提供方离开者则先于它被停用。因此依赖约束的是纤程何时激活，而非其模块何时被获取与求值，故加载器并发加载模块——大型配置启动所花费的时间正在此处。
在条目所声明的纤程之上，加载器按条目哪些字段变更分派，并对每种应用干扰最小的操作。
• id, url — 重建条目，因其身份或其组件已变；
• isolate — 重新赋值条目的领域（算法 7）；
• intercept — 就地更新，因拦截元数据在读时被咨询，无需重载；
• config — 交给组件，由组件决定如何应用新载荷，通常通过与先前者求差，仅在实质变更时重载。特别地，@cordisjs/group 条目的 config 是其子条目列表，故它将更新应用为按子 id 的键控求差，创建、移除或更新每个子；因更新幸存子会重新进入同一按字段分派，组调和与条目更新沿树一起递归；
• disabled — 置位时卸载纤程，清除时重载它。
托管领域。核心中的隔离派生覆盖某一键处领域表 𝜌 的子上下文（第 5.1.2 节），在上下文树静止时即足。条目可在运行时在组之间移动，故加载器管理其自身的领域，isolate 字段为每个键在两条作用域规则间选择。值为 true 请求局部领域，私有于条目并由其 id 标记，条目无论移到何处都携带它；字符串请求由每个命名该字符串的条目共享的全局领域，故移动这样的条目改变的是它与哪些条目共享绑定，而非它属于哪个领域。一旦无条目命名某领域，该领域即被丢弃。
重新赋值条目的领域取决于哪些键变更了领域、条目本身是否为变更键处的提供方、以及通知哪些依赖方。中间问题最难，因为领域符号可由若干纤程共享，其中只有一个是提供方。加载器用分隔符回答：每个键一个符号 𝛿𝑘，其下每个上下文存储自己的标签。分隔符写在上下文上并由其后代继承，故条目的标签与提供方的标签恰在二者在同一 isolate 作用域内为 𝑘 派生时一致，而这正是 𝑘 处绑定为条目自身、须随其移动的情形。
算法 7 隔离领域重新赋值
1
function patch_isolation(entry, 𝜌′)
2
𝜌 ← entry.ctx[@@isolate]
3
store ← entry.ctx[@@store]
4
Δ ← {𝑘| 𝜌(𝑘) ≠𝜌′(𝑘)} ▷ 领域变更的键
5
for 𝑘 in Δ do
6
entry.ctx[𝛿𝑘] ← fresh tag
7
diff[𝑘] ← (𝜌(𝑘), 𝜌′(𝑘), entry.ctx[𝛿𝑘], store[𝜌(𝑘)].fiber.ctx[𝛿𝑘])
8
entry.ctx[@@isolate] ← 𝜌′
9
reload(entry.fiber)
10
for 𝑘 in Δ do
63"""

pages[64] = r"""11
(𝑠1, 𝑠2, 𝑑1, 𝑑2) ← diff[𝑘]
12
if 𝑑1 = 𝑑2 and store[𝑠1] and not store[𝑠2] then ▷ 绑定为条目自身的
13
store[𝑠2] ← store[𝑠1]
14
delete store[𝑠1]
15
function affected(fiber, 𝑘)
16
(𝑠1, 𝑠2, 𝑑1, 𝑑2) ← diff[𝑘]
17
return fiber.ctx[@@isolate][𝑘] ∈ {𝑠1, 𝑠2} and (fiber.ctx[𝛿𝑘] = 𝑑1) ≠ (𝑑2 = 𝑑1)
18
notify(entry.ctx, Δ, affected) ▷ 取代算法 3 的领域测试
该测试取决于分隔符的一个性质。𝛿𝑘 下的标签写在条目的上下文上，并由从它派生的每个上下文继承，且在每次重新赋值时新鲜抽取，故对上下文 𝛾′
𝛾′[𝛿𝑘] = 𝑑1
⟺
𝛾′ 由条目的上下文派生
(65)
记 own(𝛾′) 为该条件，其中 𝑑2 = 𝑑1 是提供方处的实例。重新赋值将满足 own 的上下文从 𝑠1 移到 𝑠2，并将其余留在原处；由上循环，恰当提供方满足 own 时把绑定移到 𝑠2。依赖方在其于 𝑘 处的领域等于绑定所在领域时看到绑定。在 own 于依赖方与提供方上一致处，二者同移或同留，故依赖方在之后看到绑定恰当它在之前看到。在 own 将二者分开处，一方移动另一方留下，故依赖方获得或失去绑定。不等式即该分离，而成员测试丢掉在两个领域都不解析 𝑘 的依赖方——移动的任何部分都到不了它们。
5.2.2.  热模块替换
热模块替换（HMR）在模块层应用可逆效应模式：当源文件变更时（通常在开发期间），系统就地替换受影响模块而不重启进程。因纤程已界定其组件的全部效应与余效应，本身即为组件的模块可仅通过纤程操作替换：处置旧纤程恢复组件所安装的一切，从重载模块实例化的新纤程重新安装之。因此 HMR 无需开发者注解的接受边界，这与 Webpack [46] 或 Vite [47] 的 HMR 相对。
@cordisjs/hmr 组件提供 HMR 引擎，分三阶段运作。
阶段 1：模块分类。引擎接受两个输入：暂存集（自上次重载以来内容已变的文件 URL）与外部集（不能热替换、反而触发完全重启的模块）。记 get_imports(url) 为 url 直接导入的模块，引擎对变更的依赖子图分类，将每个模块标为 accepted 或 declined：
算法 8 模块分类
1
function classify(stashed, externals)
2
accepted ← stashed
3
declined ← externals
4
pending ← ⌀
5
for url in stashed do
64"""

for n in range(57, 65):
    path = OUT / f"page-{n:03d}.json"
    path.write_text(json.dumps({"page": n, "zh": pages[n]}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {path.name}")

print("batch07 partial ok")
