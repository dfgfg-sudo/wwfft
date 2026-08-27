async function processUrls(urls) {
  let results = [];
  for (let url of urls) {
    let content = await processUrl(url);
    results.push(content);
  }
  return results;
}