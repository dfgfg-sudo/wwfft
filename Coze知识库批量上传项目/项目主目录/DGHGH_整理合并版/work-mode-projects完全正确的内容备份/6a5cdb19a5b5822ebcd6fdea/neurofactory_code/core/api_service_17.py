name: CI/CD
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: { node-version: 18 }
      - run: npm ci
      - run: npm test
      - name: Notify Coze
        run: curl -X POST https://coze.cn/api/plugin/import -H "Authorization: ${{ secrets.COZE_TOKEN }}" -F "file=@weather.yaml"