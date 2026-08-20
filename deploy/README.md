# 部署到 Rancher（Docker + Helm）

静态站点根目录是 `site/`。馆藏 `/`，单篇 `/papers/<category>/<id>/`。容器监听 **8080**。

镜像默认进 **`docker.gw.sury.cn/library/cordiverse-paper`**，Chart 进 **`docker.gw.sury.cn/library/charts/cordiverse-paper`**（不要用同一路径）。

## 发布

```bash
make login          # 首次：docker + helm 登录
make release        # 先升版本，再构建并推送镜像与 OCI Helm chart
```

每次 `make release` **必须换版本**，并写回 `Chart.yaml` 的 `version` / `appVersion` 和 `values.yaml` 的 `image.tag`：

```bash
make release                 # 默认 patch：0.1.0 -> 0.1.1
make release BUMP=minor      # 0.1.1 -> 0.2.0
make release BUMP=major
make release VERSION=1.2.3   # 指定版本，必须与当前不同
```

推送失败时用 `make push helm-push` 重试，不要再跑 `release`（否则会再升一档）。单独步骤：`make build` / `make push` / `make package` / `make helm-push`。

发布结果（路径必须分开，否则后推的 chart 会覆盖镜像，Pod 报 `no command specified`）：

- 镜像：`docker.gw.sury.cn/library/cordiverse-paper:<version>`
- Chart：`oci://docker.gw.sury.cn/library/charts/cordiverse-paper:<version>`

## 安装

```bash
helm upgrade --install cordiverse-paper \
  oci://docker.gw.sury.cn/library/charts/cordiverse-paper \
  --version 0.1.0 \
  --namespace paper --create-namespace \
  --set ingress.hosts[0].host=paper.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

本地 chart：

```bash
helm upgrade --install cordiverse-paper deploy/helm/cordiverse-paper \
  -n paper --create-namespace
```

Rancher：应用商店添加 OCI 仓库 `oci://docker.gw.sury.cn/library/charts`，或用上面的 `helm upgrade`。默认用命名空间里的 `harbor-registry` 密文拉镜像（`imagePullSecrets`）；没有该密文时在 values 里改掉或置空。

## 故障：`exec /docker-entrypoint.sh: exec format error`

本机是 Apple Silicon 时，`docker build` 默认打出 **linux/arm64**，amd64 节点跑不了。`make build` / `make release` 已固定 `--platform linux/amd64`。重新发布后 `helm upgrade` 到新版本；若节点已缓存旧镜像，把 `image.pullPolicy` 临时设为 `Always` 或删掉节点上的旧镜像。

## 故障：`CreateContainerError: no command specified`

kubelet 拉到的不是可运行镜像，而是 Helm chart 的 OCI 包（没有 `Entrypoint`/`Cmd`）。把 chart 改推到 `library/charts/...` 后：

```bash
make login
make release          # 新版本：镜像与 chart 不再互相覆盖
```

集群上再 `helm upgrade` 到新 chart 版本。若节点已缓存坏镜像，把 Deployment 的 `imagePullPolicy` 临时设为 `Always`，或删掉节点上的旧镜像后再滚动重启。

## 本地验证

```bash
make run          # 镜像内快照，http://127.0.0.1:8080
make dev          # 挂载 ./site，默认 http://127.0.0.1:18080
make dev PORT=8765
```

`make run` 不会看到之后改的文件，需停掉再跑。`make dev` 跟磁盘同步，改完刷新浏览器即可。本机 8080 已被占用时用 `make dev`。
