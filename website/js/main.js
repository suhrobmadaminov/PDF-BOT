/* ═══════════════════════════════════════════════════════════════════════════
   IMAGE TO PDF PRO BOT — Landing Page JavaScript
   Features: Scroll reveal, counter animation, FAQ accordion, mobile menu
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ── Sticky Header ────────────────────────────────────────────────────────

    const header = document.getElementById('header');
    let lastScrollY = 0;

    function handleHeaderScroll() {
        const scrollY = window.scrollY;
        if (scrollY > 50) {
            header.classList.add('header--scrolled');
        } else {
            header.classList.remove('header--scrolled');
        }
        lastScrollY = scrollY;
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

        // Close mobile menu on link click
        const mobileLinks = mobileMenu.querySelectorAll('.mobile-menu__link');
        mobileLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                burger.classList.remove('active');
                mobileMenu.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ── Scroll Reveal (IntersectionObserver) ─────────────────────────────────

    function initScrollReveal() {
        const reveals = document.querySelectorAll('.reveal');

        if (!reveals.length) return;

        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        // Stagger children within same parent for grid items
                        const parent = entry.target.parentElement;
                        if (parent) {
                            const siblings = parent.querySelectorAll('.reveal');
                            let index = 0;
                            siblings.forEach(function (sib) {
                                if (sib === entry.target) {
                                    entry.target.style.transitionDelay = (index * 0.1) + 's';
                                }
                                index++;
                            });
                        }

                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.15,
                rootMargin: '0px 0px -40px 0px',
            }
        );

        reveals.forEach(function (el) {
            observer.observe(el);
        });
    }

    // ── Animated Counters ────────────────────────────────────────────────────

    function animateCounter(element, target, duration) {
        const startTime = performance.now();
        const startValue = 0;

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease out quad
            const eased = 1 - (1 - progress) * (1 - progress);
            const currentValue = Math.floor(startValue + (target - startValue) * eased);

            element.textContent = currentValue.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }

    function initCounters() {
        const counters = document.querySelectorAll('.stats__number[data-target]');

        if (!counters.length) return;

        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        const el = entry.target;
                        const target = parseInt(el.getAttribute('data-target'), 10);
                        const duration = target > 100 ? 2000 : 1200;
                        animateCounter(el, target, duration);
                        observer.unobserve(el);
                    }
                });
            },
            {
                threshold: 0.5,
            }
        );

        counters.forEach(function (counter) {
            observer.observe(counter);
        });
    }

    // ── FAQ Accordion ────────────────────────────────────────────────────────

    function initFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(function (item) {
            const questionBtn = item.querySelector('.faq-item__question');

            if (!questionBtn) return;

            questionBtn.addEventListener('click', function () {
                const isActive = item.classList.contains('active');

                // Close all other FAQ items
                faqItems.forEach(function (other) {
                    other.classList.remove('active');
                    var otherBtn = other.querySelector('.faq-item__question');
                    if (otherBtn) {
                        otherBtn.setAttribute('aria-expanded', 'false');
                    }
                });

                // Toggle current
                if (!isActive) {
                    item.classList.add('active');
                    questionBtn.setAttribute('aria-expanded', 'true');
                }
            });
        });
    }

    // ── Smooth Scroll for anchor links ───────────────────────────────────────

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (e) {
                const targetId = this.getAttribute('href');
                if (!targetId || targetId === '#') return;

                const target = document.querySelector(targetId);
                if (!target) return;

                e.preventDefault();

                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start',
                });
            });
        });
    }

    // ── Active navigation highlight ──────────────────────────────────────────

    function initActiveNav() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.header__link');

        if (!sections.length || !navLinks.length) return;

        function updateActiveLink() {
            const scrollY = window.scrollY + 120;

            sections.forEach(function (section) {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                const sectionId = section.getAttribute('id');

                if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                    navLinks.forEach(function (link) {
                        link.style.color = '';
                        if (link.getAttribute('href') === '#' + sectionId) {
                            link.style.color = 'var(--primary-light)';
                        }
                    });
                }
            });
        }

        window.addEventListener('scroll', updateActiveLink, { passive: true });
    }

    // ── Parallax subtle effect on hero shapes ────────────────────────────────

    function initParallax() {
        const shapes = document.querySelectorAll('.hero__shape');

        if (!shapes.length || window.innerWidth < 768) return;

        window.addEventListener('mousemove', function (e) {
            const x = (e.clientX / window.innerWidth - 0.5) * 2;
            const y = (e.clientY / window.innerHeight - 0.5) * 2;

            shapes.forEach(function (shape, index) {
                const speed = (index + 1) * 10;
                shape.style.transform =
                    'translate(' + (x * speed) + 'px, ' + (y * speed) + 'px)';
            });
        });
    }

    // ── Web Converter Logic ──────────────────────────────────────────────────

    function initConverter() {
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const convertBtn = document.getElementById('convertBtn');
        const btnText = document.getElementById('btnText');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const resultCard = document.getElementById('resultCard');
        const resultMeta = document.getElementById('resultMeta');
        const downloadBtn = document.getElementById('downloadBtn');

        const modeSelect = document.getElementById('modeSelect');
        const converterOptions = document.querySelector('.converter__options');
        const converterAction = document.querySelector('.converter__action');

        const qualityGroup = document.getElementById('qualityGroup');
        const pageSizeGroup = document.getElementById('pageSizeGroup');
        const ocrLangGroup = document.getElementById('ocrLangGroup');
        const editActionGroup = document.getElementById('editActionGroup');

        if (!dropzone || !fileInput || !convertBtn) return;

        let selectedFiles = [];

        // Global Select Tool Function
        window.selectTool = function (mode) {
            modeSelect.value = mode;
            modeSelect.dispatchEvent(new Event('change'));

            // Scroll to converter
            const converterSection = document.getElementById('converter');
            if (converterSection) {
                converterSection.scrollIntoView({ behavior: 'smooth' });
            }

            // Update Titles
            const titles = {
                'convert': 'JPG в PDF',
                'ocr': 'OCR PDF',
                'compress': 'Сжать PDF',
                'edit': 'Редактировать изображение'
            };
            const descs = {
                'convert': 'Преобразуйте ваши изображения в PDF документы высокой четкости.',
                'ocr': 'Распознавание текста и создание доступных для поиска PDF.',
                'compress': 'Уменьшите размер PDF файла без потери качества.',
                'edit': 'Примените фильтры и изменения к вашим изображениям.'
            };

            document.querySelector('.dropzone__title').textContent = titles[mode] || 'Выберите файлы';
            document.querySelector('.dropzone__desc').textContent = descs[mode] || 'или перетащите их сюда';
        };

        // Mode Change Handler
        modeSelect.addEventListener('change', (e) => {
            const mode = e.target.value;
            // Reset UI Groups
            qualityGroup.style.display = 'none';
            pageSizeGroup.style.display = 'none';
            ocrLangGroup.style.display = 'none';
            editActionGroup.style.display = 'none';

            if (mode === 'convert') {
                qualityGroup.style.display = 'block';
                pageSizeGroup.style.display = 'block';
                fileInput.accept = 'image/*';
            } else if (mode === 'ocr') {
                ocrLangGroup.style.display = 'block';
                fileInput.accept = 'image/*';
            } else if (mode === 'compress') {
                qualityGroup.style.display = 'block';
                fileInput.accept = '.pdf';
            } else if (mode === 'edit') {
                editActionGroup.style.display = 'block';
                fileInput.accept = 'image/*';
            }

            selectedFiles = [];
            updateFileList();
            resultCard.style.display = 'none';

            // Hide options until files selected
            converterOptions.style.display = 'none';
            converterAction.style.display = 'none';
        });

        // Trigger convert mode view by default
        modeSelect.dispatchEvent(new Event('change'));

        // Handle clicks
        dropzone.addEventListener('click', (e) => {
            if (e.target.id === 'fileInputLabel' || e.target.closest('#fileInputLabel')) {
                // Label click will trigger input naturally
                return;
            }
            // Optional: clicking anywhere in dropzone triggers it too
            // fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        // Handle Drag & Drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.add('dropzone--active'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('dropzone--active'), false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            handleFiles(dt.files);
        });

        function handleFiles(files) {
            if (files.length === 0) return;
            selectedFiles = [...files];
            updateFileList();
            resultCard.style.display = 'none';

            // Show options and action button when files selected (iLovePDF Style)
            converterOptions.style.display = 'grid';
            converterAction.style.display = 'block';

            // Hide the initial upload UI to focus on options
            document.getElementById('fileInputLabel').style.display = 'none';
        }

        function updateFileList() {
            fileList.innerHTML = '';
            if (selectedFiles.length === 0) {
                document.getElementById('fileInputLabel').style.display = 'inline-block';
                return;
            }

            selectedFiles.forEach(file => {
                const badge = document.createElement('div');
                badge.className = 'file-badge';
                const name = file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name;
                badge.textContent = name;
                fileList.appendChild(badge);
            });
        }

        // Convert Button Click
        convertBtn.addEventListener('click', async () => {
            if (selectedFiles.length === 0) {
                alert('Пожалуйста, выберите файлы!');
                return;
            }

            const mode = modeSelect.value;
            const formData = new FormData();
            let endpoint = '/api/convert';

            if (mode === 'convert') {
                selectedFiles.forEach(file => formData.append('files', file));
                formData.append('quality', document.getElementById('qualitySelect').value);
                formData.append('pagesize', document.getElementById('pageSizeSelect').value);
                formData.append('orientation', 'portrait');
                formData.append('margin', 'small');
            } else if (mode === 'ocr') {
                endpoint = '/api/ocr';
                formData.append('file', selectedFiles[0]);
                formData.append('lang', document.getElementById('ocrSelect').value);
            } else if (mode === 'compress') {
                endpoint = '/api/compress';
                formData.append('file', selectedFiles[0]);
                formData.append('quality', document.getElementById('qualitySelect').value);
            } else if (mode === 'edit') {
                endpoint = '/api/edit';
                formData.append('file', selectedFiles[0]);
                formData.append('action', document.getElementById('editActionSelect').value);
            }

            // UI State: Loading
            convertBtn.disabled = true;
            btnText.textContent = 'Обработка...';
            progressBar.style.display = 'block';
            progressFill.style.width = '0%';
            resultCard.style.display = 'none';

            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 95) progress = 95;
                progressFill.style.width = progress + '%';
            }, 400);

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });

                clearInterval(interval);
                progressFill.style.width = '100%';

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Oшибка сервера');
                }

                const result = await response.json();

                setTimeout(() => {
                    progressBar.style.display = 'none';
                    resultCard.style.display = 'flex';
                    resultMeta.textContent = `Файл: ${result.filename}`;
                    if (result.compressed_size) {
                        resultMeta.textContent += ` (${(result.compressed_size / 1024 / 1024).toFixed(2)} MB)`;
                    }
                    downloadBtn.href = result.download_url;
                    btnText.textContent = 'Готово';
                    convertBtn.disabled = false;

                    // Hide options
                    converterOptions.style.display = 'none';
                    converterAction.style.display = 'none';
                }, 600);

            } catch (err) {
                clearInterval(interval);
                alert('Ошибка: ' + err.message);
                btnText.textContent = 'Повторить';
                convertBtn.disabled = false;
                progressBar.style.display = 'none';
            }
        });
    }

    // ── Initialize everything on DOM ready ───────────────────────────────────

    document.addEventListener('DOMContentLoaded', function () {
        initScrollReveal();
        initCounters();
        initFAQ();
        initSmoothScroll();
        initActiveNav();
        initParallax();
        initConverter();
    });

})();
