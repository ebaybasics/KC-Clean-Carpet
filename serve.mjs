import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = 3000;

const MIME = {
  '.html': 'text/html',
  '.css':  'text/css',
  '.js':   'application/javascript',
  '.mjs':  'application/javascript',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
  '.mp4':  'video/mp4',
  '.webm': 'video/webm',
  '.webp': 'image/webp',
};

const server = http.createServer((req, res) => {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);

  // Redirect .html URLs to clean versions
  if (urlPath.endsWith('.html')) {
    const clean = urlPath === '/index.html' ? '/home' : urlPath.slice(0, -5);
    res.writeHead(301, { 'Location': clean });
    res.end();
    return;
  }

  // Route clean URLs to HTML files
  if (urlPath === '/') {
    res.writeHead(301, { 'Location': '/home' });
    res.end();
    return;
  }

  // Aliases
  if (urlPath === '/book-now' || urlPath === '/contact-us') {
    res.writeHead(301, { 'Location': '/schedule' });
    res.end();
    return;
  }

  let filePath;
  if (urlPath === '/home') {
    filePath = path.join(__dirname, 'index.html');
  } else if (path.extname(urlPath) === '') {
    // No extension — try .html file
    filePath = path.join(__dirname, urlPath + '.html');
  } else {
    // Static file with extension (images, fonts, etc.)
    filePath = path.join(__dirname, urlPath);
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('404 Not Found: ' + urlPath);
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const mime = MIME[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': mime });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
