# Yogurt Docker

[Yogurt](https://github.com/SaltifyDev/yogurt-releases) 的 Docker 部署方案

## 快速开始

> [!IMPORTANT]
> 挂载数据目录时，若本地目录不存在，Docker daemon 会以 root 权限自动创建，导致容器内非 root 用户无法写入。请提前手动创建并确保权限正确：
> ```bash
> mkdir -p data && chown 1000:1000 data
> ```

### Docker Compose

1. 创建数据目录：

```bash
mkdir -p data && chown 1000:1000 data
```

2. 创建 `docker-compose.yml`：

```yaml
services:
  yogurt:
    image: ghcr.io/wyf7685/yogurt-docker:latest
    container_name: yogurt
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./data:/data
```

3. 启动容器：

```bash
docker compose up -d
```

4. 编辑 `data/config.json`，填写必要信息后重启：

```bash
docker compose restart
```

### Docker Run

1. 创建数据目录：

```bash
mkdir -p data && chown 1000:1000 data
```

2. 启动容器：

```bash
docker run -d \
  --name yogurt \
  --restart unless-stopped \
  -v $(pwd)/data:/data \
  -p 3000:3000 \
  ghcr.io/wyf7685/yogurt-docker:latest
```

3. 编辑 `data/config.json`，填写必要信息后重启：

```bash
docker restart yogurt
```

## 配置说明

请参阅 [Yogurt 配置文档](https://acidify.ntqqrev.org/yogurt/configuration)

## 数据持久化

容器工作目录为 `/data`，挂载该目录即可持久化所有运行时数据：

- `config.json` - 配置文件
- `session-store.json` - PC 协议会话
- `session-store-android.json` - Android 协议会话
- `scripts/` - 自定义脚本目录

## 致谢

workflow 参考了 [shoucandanghehe/yogurt-docker](https://github.com/shoucandanghehe/yogurt-docker)

## 许可证

[MIT](LICENSE)
