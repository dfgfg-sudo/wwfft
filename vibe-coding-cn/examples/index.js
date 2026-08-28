// Vibe Coding 示例
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello Vibe Coding!');
});

app.listen(port, () => {
  console.log(`Vibe Coding 示例运行在 http://localhost:${port}`);
});