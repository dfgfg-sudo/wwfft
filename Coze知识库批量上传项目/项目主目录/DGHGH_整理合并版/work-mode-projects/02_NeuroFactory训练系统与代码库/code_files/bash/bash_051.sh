# 使用 act 测试 GitHub Actions
brew install act
act -j build

# 使用 Jenkins Pipeline Linter
curl -X POST -u user:token \
  -F "jenkinsfile=<Jenkinsfile" \
  http://jenkins-url/pipeline-model-converter/validate