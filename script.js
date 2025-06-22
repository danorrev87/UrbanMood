// JavaScript code will go here
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    const formStatus = document.getElementById('form-status');

    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            const data = new FormData(event.target);

            // Show sending message
            formStatus.textContent = 'Enviando...';
            formStatus.style.color = '#333';
            formStatus.style.opacity = '1';

            try {
                const response = await fetch(event.target.action, {
                    method: 'POST',
                    body: data,
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                if (response.ok) {
                    formStatus.textContent = "¡Gracias por tu mensaje! Nos pondremos en contacto con vos pronto.";
                    formStatus.style.color = '#a8b720'; // Use brand green
                    form.reset();
                } else {
                    const responseData = await response.json();
                    if (Object.hasOwn(responseData, 'errors')) {
                        formStatus.textContent = responseData.errors.map(error => error.message).join(', ');
                    } else {
                        formStatus.textContent = "Oops! Hubo un problema al enviar tu formulario.";
                    }
                    formStatus.style.color = 'red';
                }
            } catch (error) {
                formStatus.textContent = "Oops! Hubo un problema al enviar tu formulario.";
                formStatus.style.color = 'red';
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
        'images/carousel1.jpg',
        'images/carousel2.jpg',
        'images/carousel3.jpg',
        'images/carousel4.jpg',
        'images/carousel5.jpg',
        'images/carousel6.jpg'
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

    // New Mobile menu functionality
    const hamburgerIcon = document.querySelector('.hamburger-icon');
    const sideMenu = document.querySelector('.side-menu');
    const sideMenuLinks = document.querySelectorAll('.side-menu nav a');

    if (hamburgerIcon && sideMenu) {
        hamburgerIcon.addEventListener('click', () => {
            hamburgerIcon.classList.toggle('active');
            sideMenu.classList.toggle('active');
        });

        sideMenuLinks.forEach(link => {
            link.addEventListener('click', () => {
                hamburgerIcon.classList.remove('active');
                sideMenu.classList.remove('active');
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
});
