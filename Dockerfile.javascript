FROM node:22-alpine
WORKDIR /opt/xverse
RUN npm init -y && npm install --omit=dev --ignore-scripts linkedom@0.18.12
COPY javascript-runner.mjs /opt/xverse/runner.mjs
USER 65534:65534
ENTRYPOINT ["node", "--max-old-space-size=128", "/opt/xverse/runner.mjs"]