function toggleMenu() {
      const menu = document.getElementById('navbarMenu');
      menu.classList.toggle('active');
    }

    function toggleDropdown(event) {
      event.stopPropagation();
      const dropdown = event.target.closest('.dropdown');
      dropdown.classList.toggle('open');

      // Cierra otros dropdowns
      document.querySelectorAll('.dropdown').forEach(d => {
        if (d !== dropdown) d.classList.remove('open');
      });
    }

    document.addEventListener('click', () => {
      document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
    });

    // Animaciones
    anime({
      targets: '.navbar',
      translateY: [-100, 0],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutExpo'
    });

    // Animación inicial con Anime.js
    anime({
      targets: '.navbar',
      translateY: [-100, 0],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutExpo'
    });



    anime({
      targets: '.main-content',
      opacity: [0, 1],
      translateY: [30, 0],
      duration: 1000,
      delay: 200,
      easing: 'easeOutExpo'
    });