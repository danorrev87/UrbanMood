// JavaScript code will go here
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    const formStatus = document.getElementById('form-status');

    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Show sending message
            formStatus.textContent = 'Enviando...';
            formStatus.style.color = '#333';
            formStatus.style.opacity = '1';

            try {
                const response = await fetch('https://mailer-app-5ebl.onrender.com/send-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const responseData = await response.json();

                if (response.ok && responseData.success) {
                    formStatus.textContent = '¡Gracias por tu mensaje! Te contactaremos pronto.';
                    formStatus.style.color = '#a8b720'; // Use project's light green for success
                    formStatus.className = 'success';
                    form.reset();
                } else {
                    formStatus.textContent = responseData.message || 'Oops! Hubo un problema al enviar tu formulario.';
                    formStatus.className = 'error';
                }
            } catch (error) {
                console.error('Error:', error);
                formStatus.textContent = 'Oops! Hubo un problema al enviar tu formulario.';
                formStatus.className = 'error';
            }

            // Fade out the status message after 5 seconds
            setTimeout(() => {
                formStatus.style.opacity = '0';
            }, 5000);
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
        '/static/images/carousel6.jpg'
    ];

    if (slides.length > 0) {
        slides.forEach((slide, index) => {
            if (images[index]) {
                slide.style.backgroundImage = `url('${images[index]}')`;
            }
        });

        let currentSlide = 0;
        slides[currentSlide].classList.add('active'); // Show the first slide initially

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
    console.log('floatingWhatsApp:', floatingWhatsApp);
    console.log('heroSection:', heroSection);
    if (floatingWhatsApp) floatingWhatsApp.classList.add('visible'); // TEMP: always show for debug

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
});
