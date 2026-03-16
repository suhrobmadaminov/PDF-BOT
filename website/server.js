/**
 * Image to PDF Pro Bot — Landing Page Server
 * Railway deployment uchun oddiy statik fayl serveri.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

const MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
};

const server = http.createServer((req, res) => {
    // URL ni tozalash
    let urlPath = req.url.split('?')[0].split('#')[0];
    urlPath = decodeURIComponent(urlPath);

    // Root yoki trailing slash uchun index.html
    if (urlPath === '/' || urlPath === '') {
        urlPath = '/index.html';
    }

    // Fayl yo'lini aniqlash
    const filePath = path.join(__dirname, urlPath);

    // Xavfsizlik: directory traversal oldini olish
    const resolvedPath = path.resolve(filePath);
    if (!resolvedPath.startsWith(path.resolve(__dirname))) {
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('403 Forbidden');
        return;
    }

    // Fayl mavjudligini tekshirish
    fs.stat(resolvedPath, (err, stats) => {
        if (err || !stats.isFile()) {
            // 404 — index.html ga redirect (SPA uchun)
            const indexPath = path.join(__dirname, 'index.html');
            fs.readFile(indexPath, (err2, data) => {
                if (err2) {
                    res.writeHead(500, { 'Content-Type': 'text/plain' });
                    res.end('500 Internal Server Error');
                    return;
                }
                res.writeHead(200, {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Cache-Control': 'no-cache',
                });
                res.end(data);
            });
            return;
        }

        // Faylni o'qish va yuborish
        const ext = path.extname(resolvedPath).toLowerCase();
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';

        // Statik fayllar uchun cache
        const isAsset = ext !== '.html';
        const cacheControl = isAsset
            ? 'public, max-age=31536000, immutable'
            : 'no-cache';

        fs.readFile(resolvedPath, (readErr, data) => {
            if (readErr) {
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('500 Internal Server Error');
                return;
            }
            res.writeHead(200, {
                'Content-Type': contentType,
                'Cache-Control': cacheControl,
                'X-Content-Type-Options': 'nosniff',
            });
            res.end(data);
        });
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`🌐 Website server ishga tushdi: http://0.0.0.0:${PORT}`);
});
