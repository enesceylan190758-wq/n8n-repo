#!/usr/bin/env node
/** Screenshot 1080x1080 HTML file to PNG via Puppeteer. */
const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i += 2) {
    const key = argv[i];
    const val = argv[i + 1];
    if (key === '--input') out.input = val;
    if (key === '--output') out.output = val;
    if (key === '--chrome') out.chrome = val;
  }
  return out;
}

(async () => {
  const { input, output, chrome } = parseArgs(process.argv);
  if (!input || !output) {
    console.error('Usage: node render-social-screenshot.js --input file.html --output file.png [--chrome path]');
    process.exit(1);
  }

  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch {
    const local = path.resolve(__dirname, '..', '.tmp', 'sosyal_medya_postlar', 'node_modules', 'puppeteer');
    puppeteer = require(local);
  }

  const browser = await puppeteer.launch({
    executablePath: chrome || process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 1200));
  await page.screenshot({
    path: path.resolve(output),
    type: 'png',
    clip: { x: 0, y: 0, width: 1080, height: 1080 },
  });
  await browser.close();
  console.log('saved', output);
})();
