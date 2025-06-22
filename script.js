// JavaScript code will go here
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        // Basic form validation
        const name = form.querySelector('input[name="name"]').value;
        const email = form.querySelector('input[name="email"]').value;
        const message = form.querySelector('textarea[name="message"]').value;

        if (name.trim() === '' || email.trim() === '' || message.trim() === '') {
            alert('Por favor, completá todos los campos obligatorios.');
            return;
        }

        // Simple email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Por favor, ingresá un email válido.');
            return;
        }

        alert('¡Gracias por tu mensaje! Nos pondremos en contacto con vos pronto.');
        form.reset();
    });

    // Smooth scroll for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
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
});
