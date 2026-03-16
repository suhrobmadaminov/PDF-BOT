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

    // ── Initialize everything on DOM ready ───────────────────────────────────

    document.addEventListener('DOMContentLoaded', function () {
        initScrollReveal();
        initCounters();
        initFAQ();
        initSmoothScroll();
        initActiveNav();
        initParallax();
    });

})();
