FROM debian:trixie-slim AS base

RUN apt-get update

FROM base AS deps

ARG TARGETARCH

RUN apt-get install -y --no-install-recommends \
    libcrypt1 libz1

RUN if [ "$TARGETARCH" = "arm64" ]; then MULTIARCH="aarch64-linux-gnu"; else MULTIARCH="x86_64-linux-gnu"; fi \
    && mkdir -p /rootfs/usr/lib/${MULTIARCH} \
    && cp /usr/lib/${MULTIARCH}/libcrypt.so.1 /rootfs/usr/lib/${MULTIARCH}/ \
    && cp /usr/lib/${MULTIARCH}/libz.so.1 /rootfs/usr/lib/${MULTIARCH}/

RUN mkdir -p /rootfs/etc \
    && echo 'yogurt:x:1000:1000::/nonexistent:/sbin/nologin' > /rootfs/etc/passwd \
    && echo 'yogurt:x:1000:' > /rootfs/etc/group \
    && mkdir -p /rootfs/data \
    && chown -R 1000:1000 /rootfs/data

FROM base AS binary

ARG TARGETARCH
ARG VERSION=v0.1.0-dev.220

RUN apt-get install -y --no-install-recommends \
    curl unzip ca-certificates

RUN if [ "$TARGETARCH" = "arm64" ]; then ARCH="arm64"; else ARCH="x64"; fi \
    && curl -fsSL "https://github.com/SaltifyDev/yogurt-releases/releases/download/${VERSION}/yogurt-linux-${ARCH}.zip" -o "/tmp/yogurt.zip" \
    && unzip -j "/tmp/yogurt.zip" "yogurt.kexe" -d / \
    && mv /yogurt.kexe /yogurt \
    && chmod +x /yogurt

FROM base AS launcher

RUN apt-get install -y --no-install-recommends \
    gcc libc6-dev

RUN --mount=type=bind,source=./launcher.c,target=/launcher.c \
    gcc -O2 -s /launcher.c -o /launcher && chmod +x /launcher

FROM gcr.io/distroless/cc-debian13 AS rootfs

COPY --from=deps /rootfs/ /

FROM scratch AS runtime

COPY --from=rootfs / /
COPY --from=launcher /launcher /
COPY --from=binary /yogurt /

USER yogurt

WORKDIR /data
EXPOSE 3000
VOLUME ["/data"]
ENTRYPOINT ["/launcher"]
CMD ["/yogurt"]
