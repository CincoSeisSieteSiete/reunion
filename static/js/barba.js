document.addEventListener("DOMContentLoaded", () => {

    barba.init({
        transitions: [{
            name: "fade-transition",

            leave(data) {
                return new Promise(resolve => {
                    const block = data.current.container.querySelector('.main-container');
                    block.classList.add('fade-leave');

                    setTimeout(resolve, 100); // duración del fade
                });
            },

            enter(data) {
                    const block = data.next.container.querySelector('.main-container');
                    block.classList.add('fade-enter');

                    // permitir que la animación se vea correctamente
                    setTimeout(() => {
                        block.classList.remove('fade-enter');
                    }, 100);
            }
        }]
    });

});
