/* ═══════════════════════════════════════════════════════════════════════════
   IMAGE TO PDF PRO BOT — Per-Tool Page JavaScript
   iLovePDF Style: Each tool has its own dedicated upload page
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ── Sticky Header ────────────────────────────────────────────────────────

    const header = document.getElementById('header');

    function handleHeaderScroll() {
        if (window.scrollY > 10) {
            header.classList.add('header--scrolled');
        } else {
            header.classList.remove('header--scrolled');
        }
    }

    window.addEventListener('scroll', handleHeaderScroll, { passive: true });

    // ── Mobile Menu ──────────────────────────────────────────────────────────

    const burger = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobileMenu');

    if (burger && mobileMenu) {
        burger.addEventListener('click', function () {
            burger.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active')
                ? 'hidden'
                : '';
        });

        const mobileLinks = mobileMenu.querySelectorAll('.mobile-menu__link');
        mobileLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                burger.classList.remove('active');
                mobileMenu.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ── Tool Page Navigation ─────────────────────────────────────────────────

    const toolsGrid = document.getElementById('toolsGrid');
    const siteFooter = document.getElementById('siteFooter');
    const toolPages = ['convert', 'ocr', 'compress', 'edit'];

    // Store selected files per tool
    const toolFiles = {
        convert: [],
        ocr: [],
        compress: [],
        edit: []
    };

    // Show tools grid, hide all tool pages
    window.showToolsGrid = function () {
        toolPages.forEach(function (tool) {
            var page = document.getElementById('toolPage-' + tool);
            if (page) page.style.display = 'none';
        });
        toolsGrid.style.display = '';
        siteFooter.style.display = '';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Open a specific tool page
    window.openToolPage = function (tool) {
        // Close mobile menu if open
        if (burger && mobileMenu) {
            burger.classList.remove('active');
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        }

        // Hide grid and footer
        toolsGrid.style.display = 'none';
        siteFooter.style.display = 'none';

        // Hide all tool pages
        toolPages.forEach(function (t) {
            var page = document.getElementById('toolPage-' + t);
            if (page) page.style.display = 'none';
        });

        // Show selected tool page
        var toolPage = document.getElementById('toolPage-' + tool);
        if (toolPage) {
            toolPage.style.display = '';
            window.scrollTo({ top: 0, behavior: 'instant' });
        }

        // Reset the page state
        resetToolPage(tool);
    };

    function resetToolPage(tool) {
        toolFiles[tool] = [];
        updateFileList(tool);

        // Show upload button, hide options/action/result
        var fileInput = document.getElementById('fileInput-' + tool);
        var labelBtn = document.querySelector('#toolPage-' + tool + ' .tool-page__btn');
        var dropText = document.querySelector('#toolPage-' + tool + ' .tool-page__drop-text');
        var options = document.getElementById('options-' + tool);
        var action = document.getElementById('action-' + tool);
        var result = document.getElementById('result-' + tool);
        var progress = document.getElementById('progress-' + tool);

        if (labelBtn) labelBtn.style.display = '';
        if (dropText) dropText.style.display = '';
        if (options) options.style.display = 'none';
        if (action) action.style.display = 'none';
        if (result) result.style.display = 'none';
        if (progress) progress.style.display = 'none';
        if (fileInput) fileInput.value = '';
    }

    // ── File Handling Per Tool ────────────────────────────────────────────────

    function initToolPage(tool) {
        var dropzone = document.getElementById('dropzone-' + tool);
        var fileInput = document.getElementById('fileInput-' + tool);
        var convertBtn = document.getElementById('convertBtn-' + tool);

        if (!dropzone || !fileInput || !convertBtn) return;

        // File input change
        fileInput.addEventListener('change', function (e) {
            handleToolFiles(tool, e.target.files);
        });

        // Drag & Drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function () {
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function () {
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', function (e) {
            handleToolFiles(tool, e.dataTransfer.files);
        });

        // Convert button click
        convertBtn.addEventListener('click', function () {
            processToolRequest(tool);
        });
    }

    function handleToolFiles(tool, files) {
        if (!files || files.length === 0) return;

        toolFiles[tool] = Array.from(files);
        updateFileList(tool);

        // Hide the upload button, show options and action
        var labelBtn = document.querySelector('#toolPage-' + tool + ' .tool-page__btn');
        var dropText = document.querySelector('#toolPage-' + tool + ' .tool-page__drop-text');
        var options = document.getElementById('options-' + tool);
        var action = document.getElementById('action-' + tool);
        var result = document.getElementById('result-' + tool);

        if (labelBtn) labelBtn.style.display = 'none';
        if (dropText) dropText.style.display = 'none';
        if (options) options.style.display = 'grid';
        if (action) action.style.display = '';
        if (result) result.style.display = 'none';
    }

    function updateFileList(tool) {
        var fileListEl = document.getElementById('fileList-' + tool);
        if (!fileListEl) return;

        fileListEl.innerHTML = '';
        var files = toolFiles[tool];

        if (files.length === 0) return;

        files.forEach(function (file, index) {
            var badge = document.createElement('div');
            badge.className = 'file-badge';

            var icon = document.createElement('span');
            icon.className = 'file-badge__icon';
            icon.textContent = file.type.startsWith('image/') ? '🖼️' : '📄';

            var nameSpan = document.createElement('span');
            var name = file.name.length > 25 ? file.name.substring(0, 22) + '...' : file.name;
            nameSpan.textContent = name;

            var removeBtn = document.createElement('span');
            removeBtn.className = 'file-badge__remove';
            removeBtn.textContent = '×';
            removeBtn.setAttribute('data-tool', tool);
            removeBtn.setAttribute('data-index', index);
            removeBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                var t = this.getAttribute('data-tool');
                var i = parseInt(this.getAttribute('data-index'));
                toolFiles[t].splice(i, 1);
                updateFileList(t);
                if (toolFiles[t].length === 0) {
                    resetToolPage(t);
                }
            });

            badge.appendChild(icon);
            badge.appendChild(nameSpan);
            badge.appendChild(removeBtn);
            fileListEl.appendChild(badge);
        });
    }

    // ── Process Requests ─────────────────────────────────────────────────────

    async function processToolRequest(tool) {
        var files = toolFiles[tool];
        if (!files || files.length === 0) {
            alert('Пожалуйста, выберите файлы!');
            return;
        }

        var formData = new FormData();
        var endpoint = '';

        if (tool === 'convert') {
            endpoint = '/api/convert';
            files.forEach(function (file) {
                formData.append('files', file);
            });
            formData.append('quality', document.getElementById('qualitySelect-convert').value);
            formData.append('pagesize', document.getElementById('pageSizeSelect-convert').value);
            formData.append('orientation', document.getElementById('orientationSelect-convert').value);
            formData.append('margin', 'small');
        } else if (tool === 'ocr') {
            endpoint = '/api/ocr';
            formData.append('file', files[0]);
            formData.append('lang', document.getElementById('ocrLangSelect-ocr').value);
        } else if (tool === 'compress') {
            endpoint = '/api/compress';
            formData.append('file', files[0]);
            formData.append('quality', document.getElementById('qualitySelect-compress').value);
        } else if (tool === 'edit') {
            endpoint = '/api/edit';
            formData.append('file', files[0]);
            formData.append('action', document.getElementById('editActionSelect-edit').value);
        }

        // UI State: Loading
        var convertBtn = document.getElementById('convertBtn-' + tool);
        var progressBar = document.getElementById('progress-' + tool);
        var progressFill = document.getElementById('progressFill-' + tool);
        var resultSection = document.getElementById('result-' + tool);
        var resultMeta = document.getElementById('resultMeta-' + tool);
        var downloadBtn = document.getElementById('downloadBtn-' + tool);
        var optionsPanel = document.getElementById('options-' + tool);

        convertBtn.disabled = true;
        convertBtn.querySelector('span').textContent = 'Обработка...';
        progressBar.style.display = 'block';
        progressFill.style.width = '0%';
        resultSection.style.display = 'none';

        var progress = 0;
        var interval = setInterval(function () {
            progress += Math.random() * 12;
            if (progress > 95) progress = 95;
            progressFill.style.width = progress + '%';
        }, 400);

        try {
            var response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            clearInterval(interval);
            progressFill.style.width = '100%';

            if (!response.ok) {
                var errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка сервера');
            }

            var result = await response.json();

            setTimeout(function () {
                progressBar.style.display = 'none';
                optionsPanel.style.display = 'none';
                document.getElementById('action-' + tool).style.display = 'none';
                resultSection.style.display = '';

                resultMeta.textContent = 'Файл: ' + result.filename;
                if (result.compressed_size) {
                    resultMeta.textContent += ' (' + (result.compressed_size / 1024 / 1024).toFixed(2) + ' MB)';
                }
                downloadBtn.href = result.download_url;

                convertBtn.querySelector('span').textContent = 'Готово ✓';
                convertBtn.disabled = false;
            }, 600);

        } catch (err) {
            clearInterval(interval);
            alert('Ошибка: ' + err.message);
            convertBtn.querySelector('span').textContent = 'Повторить';
            convertBtn.disabled = false;
            progressBar.style.display = 'none';
        }
    }

    // ── Initialize everything on DOM ready ───────────────────────────────────

    document.addEventListener('DOMContentLoaded', function () {
        // Init each tool page
        toolPages.forEach(function (tool) {
            initToolPage(tool);
        });
    });

})();
