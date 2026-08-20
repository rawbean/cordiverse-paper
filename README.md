# A Programming Paradigm for Spatiotemporal Composability

**[对照阅读](site/papers/featured/cordiverse/)** · **[馆藏](site/index.html)** · **[Read the paper (PDF)](papers/featured/cordiverse/paper.pdf)** · Draft of August 13, 2026

> This is a preprint under active revision. The content may change substantially; please cite the latest version and check back before relying on specific results.

Modern software---from plugin systems to self-evolving agent harnesses---increasingly requires _dynamic composition_, yet its formal foundations remain underdeveloped. We identify two orthogonal dimensions of the problem: _temporal composability_, the ability to completely revert a component's side effects upon removal, and _spatial composability_, the ability to declare and reactively manage inter-component dependencies.
We address the two dimensions by lifting classical effect and coeffect concepts to runtime mechanisms.
In particular, we formalize _revertible effects_, in which every context transformation carries an inverse that the runtime tracks.
We formalize _reactive coeffects_, in which each change of the context notifies a component against its coeffect specification.
We unify the effect context and the coeffect context into a single _context type_, which constitutes a programming paradigm.
After that, we combine these mechanisms into the notion of a _component_ and give a calculus of dynamic composition, whose metatheory carries spatiotemporal composability from a single component to a whole system of interleaved components.
We implement these ideas in _Cordis_, a meta-framework of spatiotemporal composability that provides a core library with effect tracking and coeffect resolution, as well as a declarative component loader with configuration reconciliation and hot module replacement.

## 仓库结构

| 路径 | 内容 |
|------|------|
| `site/` | 对外站点。馆藏：`site/index.html`；阅读页：`site/papers/<category>/<id>/` |
| `papers/<category>/<id>/paper.pdf` | 该篇原始 PDF |
| `papers/<category>/<id>/artifacts/` | 该篇抽取/翻译中间产物（不进 Git / 镜像） |
| `papers/_shared/` | 跨篇共享资源（如 ECDICT），不进 Git |
| `deploy/` | Nginx + Helm（Rancher） |
| `tools/` | 排版等脚本 |

部署见 [deploy/README.md](deploy/README.md)。发布：`make login && make release`（每次自动升版本；镜像进 `docker.gw.sury.cn/library/cordiverse-paper`，chart 进 `docker.gw.sury.cn/library/charts/cordiverse-paper`）。
