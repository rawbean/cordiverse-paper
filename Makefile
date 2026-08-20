REGISTRY      ?= docker.gw.sury.cn/library
IMAGE_NAME    ?= cordiverse-paper
CHART_NAME    ?= cordiverse-paper
CHART_DIR     := deploy/helm/$(CHART_NAME)
# 未指定 VERSION 时读 Chart.yaml；release 会再按 BUMP 自增
VERSION       ?= $(shell awk '/^version:/{print $$2; exit}' $(CHART_DIR)/Chart.yaml)
BUMP          ?= patch
IMAGE         := $(REGISTRY)/$(IMAGE_NAME)
# 集群节点是 amd64；在 Apple Silicon 上不指定平台会打出 arm64，Pod 报 exec format error
PLATFORM      ?= linux/amd64
# chart 必须与镜像不同路径，否则 helm push 会覆盖 docker 镜像（CreateContainerError: no command specified）
CHART_OCI     := oci://$(REGISTRY)/charts
DIST          := dist
PORT          ?= 18080

.PHONY: help build push package helm-push release login run dev lint clean

help:
	@echo "REGISTRY=$(REGISTRY)  当前 Chart 版本=$(VERSION)  BUMP=$(BUMP)"
	@echo ""
	@echo "  make release     先升版本，再构建并推送镜像 + OCI chart"
	@echo "                   默认 patch：0.1.0 -> 0.1.1"
	@echo "                   make release BUMP=minor|major"
	@echo "                   make release VERSION=1.2.3   （必须与当前不同）"
	@echo "  make build       构建镜像 $(IMAGE):$(VERSION)"
	@echo "  make push        推送镜像（不升版本）"
	@echo "  make package     打包 Helm chart 到 $(DIST)/"
	@echo "  make helm-push   以 OCI 推送 chart 到 $(CHART_OCI)/$(CHART_NAME)"
	@echo "  make login       docker / helm 登录 $(firstword $(subst /, ,$(REGISTRY)))"
	@echo "  make run         本地跑镜像快照 :8080（不跟磁盘同步）"
	@echo "  make dev         挂载 ./site，默认 :$(PORT)，改文件后刷新即可"
	@echo "                   make dev PORT=8765"
	@echo "  make lint        helm lint"
	@echo "  make clean       删除 $(DIST)/"

login:
	docker login $(firstword $(subst /, ,$(REGISTRY)))
	helm registry login $(firstword $(subst /, ,$(REGISTRY)))

build:
	docker build --platform $(PLATFORM) -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

push: build
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

package:
	mkdir -p $(DIST)
	helm package $(CHART_DIR) -d $(DIST)

helm-push: package
	helm push $(DIST)/$(CHART_NAME)-$(VERSION).tgz $(CHART_OCI)

# 每次 release 必须换版本：未传 VERSION 则按 BUMP 自增并写回 Chart.yaml / values.yaml
# 推送失败时用 make push helm-push 重试，不要再跑 release（否则会再升一档）
release:
	@if [ "$(origin VERSION)" = "command line" ] || [ "$(origin VERSION)" = "environment" ]; then \
		new=$$(python3 tools/bump_version.py "$(VERSION)"); \
	else \
		new=$$(python3 tools/bump_version.py "$(BUMP)"); \
	fi; \
	echo "已升至 $$new（写入 Chart.yaml / values.yaml）"; \
	$(MAKE) push helm-push VERSION=$$new; \
	echo "镜像: $(IMAGE):$$new"; \
	echo "Chart: $(CHART_OCI)/$(CHART_NAME):$$new"

run: build
	docker run --rm -p 8080:8080 $(IMAGE):$(VERSION)

# 挂载仓库里的 site/，改 HTML/图/词典后刷新浏览器即可（nginx 不 livereload）
dev: build
	@echo "http://127.0.0.1:$(PORT)  （./site → 容器，Ctrl+C 结束）"
	docker run --rm --name cordiverse-paper-dev \
		-p $(PORT):8080 \
		-v "$(CURDIR)/site:/usr/share/nginx/html:ro" \
		-v "$(CURDIR)/deploy/nginx/dev.conf:/etc/nginx/conf.d/default.conf:ro" \
		$(IMAGE):$(VERSION)

lint:
	helm lint $(CHART_DIR)

clean:
	rm -rf $(DIST)
