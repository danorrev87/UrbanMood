// JavaScript code will go here
function setVH() {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// Set initial viewport height
setVH();

// Update on window resize
window.addEventListener('resize', setVH);

// Update on orientation change (important for mobile)
window.addEventListener('orientationchange', function() {
    setTimeout(setVH, 100); // Small delay to ensure orientation change is complete
});

// Also set on DOMContentLoaded to ensure it's available early
document.addEventListener('DOMContentLoaded', function() {
    setVH();
    
    // Loading overlay logic
    const loadingOverlay = document.getElementById('loading-overlay');
    const heroVideo = document.querySelector('#background-video'); // Fixed: use the actual video ID
    let videoLoaded = false;
    let minimumTimeElapsed = false;
    
    function hideLoadingOverlay() {
        if (loadingOverlay && videoLoaded && minimumTimeElapsed) {
            loadingOverlay.classList.add('fade-out');
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 500);
        }
    }
    
    function checkVideoLoaded() {
        videoLoaded = true;
        hideLoadingOverlay();
    }
    
    function checkMinimumTime() {
        minimumTimeElapsed = true;
        hideLoadingOverlay();
    }
    
    // Set minimum display time
    setTimeout(checkMinimumTime, 2500);
    
    // Wait for hero video to load
    if (heroVideo) {
        // Use multiple events to ensure video is ready
        heroVideo.addEventListener('canplaythrough', checkVideoLoaded);
        heroVideo.addEventListener('loadeddata', checkVideoLoaded);
        
        // Also check if video is already loaded
        if (heroVideo.readyState >= 3) { // HAVE_FUTURE_DATA or higher
            checkVideoLoaded();
        }
        
        // Fallback: hide loading after 10 seconds even if video doesn't load
        setTimeout(() => {
            if (loadingOverlay && !loadingOverlay.classList.contains('fade-out')) {
                loadingOverlay.classList.add('fade-out');
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                }, 500);
            }
        }, 10000);
    } else {
        // If no video found, hide loading after minimum time
        setTimeout(() => {
            if (loadingOverlay && !loadingOverlay.classList.contains('fade-out')) {
                loadingOverlay.classList.add('fade-out');
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                }, 500);
            }
        }, 3000);
    }

    // Form handling with AJAX (no page reload)
    const form = document.getElementById('contact-form');
    const formStatus = document.getElementById('form-status');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent page reload
            
            // Show sending message
            formStatus.textContent = 'Enviando...';
            formStatus.style.color = '#333';
            formStatus.style.opacity = '1';
            
            // Prepare form data
            const formData = new FormData(form);
            
            // Submit via fetch API
            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    // Success
                    formStatus.textContent = '¡Gracias por tu mensaje! Te contactaremos pronto.';
                    formStatus.style.color = '#a8b720';
                    formStatus.className = 'success';
                    
                    // Reset form
                    form.reset();
                    
                    // Scroll to contact section to ensure message is visible
                    const contactSection = document.querySelector('#contact');
                    if (contactSection) {
                        contactSection.scrollIntoView({ behavior: 'smooth' });
                    }
                    
                    // Fade out after 5 seconds
                    setTimeout(() => {
                        formStatus.style.opacity = '0';
                    }, 5000);
                } else {
                    throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                // Error
                formStatus.textContent = 'Hubo un error al enviar el mensaje. Por favor intenta nuevamente.';
                formStatus.style.color = '#e74c3c';
                formStatus.className = 'error';
                
                console.error('Form submission error:', error);
            });
        });
    }

    // Smooth scroll for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');

            if (targetId === '#home') {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            } else {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Image carousel functionality
    const slides = document.querySelectorAll('.carousel-slide');
    const images = [
        '/static/images/carousel1.jpg',
        '/static/images/carousel2.jpg',
        '/static/images/carousel3.jpg',
        '/static/images/carousel4.jpg',
        '/static/images/carousel5.jpg',
        '/static/images/carousel6.jpg',
        '/static/images/carousel7.jpg',
        '/static/images/carousel8.jpg'
    ];

        // Schedule tabs logic
        function initScheduleTabs(root=document) {
            const containers = root.querySelectorAll('.schedule-tabs');
            containers.forEach(container => {
                const buttons = container.querySelectorAll('.tab-btn');
                const panels = container.querySelectorAll('.tab-panel');
                buttons.forEach(btn => {
                    btn.addEventListener('click', () => {
                        if (btn.classList.contains('active')) return;
                        buttons.forEach(b => b.classList.remove('active'));
                        panels.forEach(p => p.classList.remove('active'));
                        btn.classList.add('active');
                        const target = container.querySelector(btn.dataset.target);
                        if (target) target.classList.add('active');
                    });
                });
            });
        }
        initScheduleTabs();

        // Fallback for missing schedule images
        const scheduleImgs = document.querySelectorAll('.schedule-tabs img.dropdown-image');
        scheduleImgs.forEach(img => {
            img.addEventListener('error', () => {
                if (img.dataset.fallbackApplied) return;
                img.dataset.fallbackApplied = '1';
                const loc = img.alt.includes('Palermo') ? 'Palermo' : 'Cordón';
                    img.replaceWith(Object.assign(document.createElement('div'), {
                        className: 'dropdown-image schedule-fallback',
                        innerHTML: `<div style="padding:1.5em;text-align:center;font-size:0.85rem;background:#2a2f33;border:1px dashed #555;border-radius:10px;">Horario de ${loc} próximamente.<br>Cargá la imagen clases-${loc.toLowerCase()}.png</div>`
                }));
            });
        });

    if (slides.length > 0) {
        slides.forEach((slide, index) => {
            if (images[index]) {
                slide.style.backgroundImage = `url('${images[index]}')`;
                
                // Preload images for better performance
                const img = new Image();
                img.src = images[index];
                img.onerror = function() {
                    console.error('Failed to load carousel image:', images[index]);
                };
            }
        });

        let currentSlide = 0;
        
        // Ensure first slide is visible immediately
        if (slides[0]) {
            slides[0].classList.add('active');
        }

        setInterval(() => {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }, 5000); // Change slide every 5 seconds
    }

    // Adjust hero height on mobile to account for viewport inconsistencies
    function setHeroHeight() {
        const hero = document.querySelector('.hero');
        const header = document.querySelector('.top-header');
        if (hero && header) {
            const headerHeight = header.offsetHeight;
            hero.style.height = `${window.innerHeight - headerHeight}px`;
        }
    }

    // Set height on initial load and on resize, specifically for mobile
    if (window.innerWidth <= 768) {
        setHeroHeight();
        window.addEventListener('resize', setHeroHeight);
    }

    // Floating WhatsApp Icon Visibility
    const floatingWhatsApp = document.querySelector('.floating-whatsapp');
    const heroSection = document.querySelector('.hero');

    function updateWhatsAppVisibility() {
        if (floatingWhatsApp && heroSection) {
            const heroRect = heroSection.getBoundingClientRect();
            if (heroRect.bottom < 0 || window.scrollY > 100) {
                floatingWhatsApp.classList.add('visible');
            } else {
                floatingWhatsApp.classList.remove('visible');
            }
        }
    }

    window.addEventListener('scroll', updateWhatsAppVisibility);
    window.addEventListener('resize', updateWhatsAppVisibility);
    updateWhatsAppVisibility(); // Initial check

    // New Mobile menu functionality
    const hamburger = document.querySelector('.hamburger-icon');
    const sideMenu = document.querySelector('.side-menu');
    const sideMenuLinks = document.querySelectorAll('.side-menu nav a');

    if (hamburger && sideMenu) {
        hamburger.addEventListener('click', () => {
            const isActive = hamburger.classList.toggle('active');
            sideMenu.classList.toggle('active');
            document.documentElement.classList.toggle('no-scroll', isActive);
            document.body.classList.toggle('body-no-scroll', isActive);
        });

        sideMenuLinks.forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                sideMenu.classList.remove('active');
                document.documentElement.classList.remove('no-scroll');
                document.body.classList.remove('body-no-scroll');
            });
        });
    }

    // Accordion for Actividades
    const activityItems = document.querySelectorAll('.activity-item');
    if (activityItems.length > 0) {
        activityItems.forEach(item => {
            const header = item.querySelector('.activity-header');
            header.addEventListener('click', () => {
                item.classList.toggle('active');
            });
        });
    }

    // Video background source update based on screen size and orientation
    const video = document.getElementById('background-video');
    const videoSource = document.getElementById('video-source');

    const updateVideoSource = () => {
        const isMobile = window.innerWidth <= 768;
        const isLandscape = window.innerWidth > window.innerHeight;
        
        if (isMobile) {
            // Use mobile video for mobile devices regardless of orientation
            videoSource.src = '/static/videos/web.mp4';
        } else {
            // Use landscape video for desktop/larger screens in landscape mode
            videoSource.src = isLandscape ? '/static/videos/web-landscape.mp4' : '/static/videos/web.mp4';
        }
        video.load();
    };

    updateVideoSource();
    window.addEventListener('resize', updateVideoSource);

    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe all elements with animation classes
    const animatedElements = document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right, .scale-in, .slide-up');
    animatedElements.forEach(element => {
        observer.observe(element);
    });

    // Add pulse animation to CTA buttons after they become visible
    const ctaButtons = document.querySelectorAll('.cta-button');
    ctaButtons.forEach(button => {
        button.classList.add('fade-in');
        observer.observe(button);
        
        // Add pulse animation after the button becomes visible
        button.addEventListener('transitionend', () => {
            if (button.classList.contains('visible')) {
                setTimeout(() => {
                    button.classList.add('pulse-animation');
                }, 500);
            }
        });
    });

    // Add floating animation to specific elements
    const floatingElements = document.querySelectorAll('.floating-whatsapp');
    floatingElements.forEach(element => {
        element.classList.add('float-animation');
    });

    // Header hide/show on scroll functionality
    let lastScrollTop = 0;
    let scrollTimeout = null;
    const header = document.querySelector('.top-header');
    const scrollThreshold = 5; // Minimum scroll distance to trigger hide/show

    function handleScroll() {
        const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        
        // Clear any existing timeout
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        // Don't hide header when at the very top of the page
        if (currentScroll <= 0) {
            header.classList.remove('hidden');
            lastScrollTop = currentScroll;
            return;
        }
        
        // Only act if scroll distance is significant enough
        if (Math.abs(currentScroll - lastScrollTop) > scrollThreshold) {
            if (currentScroll > lastScrollTop) {
                // Scrolling down - hide header
                header.classList.add('hidden');
            } else {
                // Scrolling up - show header
                header.classList.remove('hidden');
            }
            lastScrollTop = currentScroll;
        }
        
        // Set a timeout to show header after scrolling stops
        scrollTimeout = setTimeout(() => {
            header.classList.remove('hidden');
        }, 1000); // Show header 1 second after scrolling stops
    }

    window.addEventListener('scroll', handleScroll, { passive: true });

    // Add error handling for images
    const allImages = document.querySelectorAll('img');
    allImages.forEach(img => {
        img.onerror = function() {
            console.error('Failed to load image:', this.src);
            this.style.backgroundColor = '#f5f5f5';
            this.style.display = 'block';
        };
    });
});
