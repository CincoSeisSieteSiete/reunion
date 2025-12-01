# 🎨 Documentación del Frontend - Proyecto Betania

## Stack Tecnológico

- **HTML5**: Estructura semántica
- **CSS3**: Estilos con sistema de temas (claro/oscuro)
- **JavaScript (Vanilla)**: Interactividad sin frameworks
- **Anime.js**: Librería de animaciones
- **Barba.js**: Transiciones entre páginas

## Estructura de Archivos

```
static/
├── css/
│   ├── style.css          # Estilos globales
│   ├── base/base.css      # Variables CSS
│   ├── light/light.css    # Tema claro
│   ├── dark/dark.css      # Tema oscuro
│   └── toast/             # Notificaciones
├── js/
│   ├── menu.js            # Navegación
│   ├── toast.js           # Sistema de notificaciones
│   └── barba.js           # Transiciones
├── iconos/                # SVG icons
└── logos/                 # Imágenes de marca

templates/
├── base.html              # Plantilla base
├── 404.html               # Página de error
├── inicio/                # Login y registro
├── user_view/             # Vistas de usuario
├── creador/               # Crear grupos
├── gestionar/             # Admin
└── config/                # Configuración
```

## Sistema de Temas

### Variables CSS (base.css)

```css
:root {
    --text-primary: #222222;
    --text-secondary: #555555;
    --bg-main: #ffffff;
    --accent-color: #ffc107;
}
```

### Cambio Dinámico

El tema se carga según `session.get('tema')`:
- `0` = Tema claro
- `1` = Tema oscuro

```html
{% if session.get('tema', 0) == 0 %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/light/light.css') }}">
{% else %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dark/dark.css') }}">
{% endif %}
```

## JavaScript

### menu.js - Navegación Responsiva

```javascript
function toggleMenu() {
    const menu = document.getElementById('navbarMenu');
    menu.classList.toggle('active');
}

// Animaciones con Anime.js
anime({
    targets: '.navbar',
    translateY: [-100, 0],
    opacity: [0, 1],
    duration: 800,
    easing: 'easeOutExpo'
});
```

### toast.js - Notificaciones

```javascript
function showToast(message, category = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${category}`;
    toast.innerHTML = `
        <div class="toast-content">
            <p>${message}</p>
        </div>
    `;
    document.getElementById('toast-container').appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => toast.remove(), 5000);
}
```

## Plantilla Base (base.html)

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Betania - {% block title %}Home{% endblock %}</title>
  
  <!-- CSS Base + Tema -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/base/base.css') }}">
  {% if session.get('tema', 0) == 0 %}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/light/light.css') }}">
  {% else %}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/dark/dark.css') }}">
  {% endif %}
</head>

<body>
  <div id="toast-container"></div>
  
  <nav class="navbar">
    <!-- Navegación -->
  </nav>

  <div class="main-content">
    {% block content %}{% endblock %}
  </div>

  <footer class="footer">
    <!-- Footer -->
  </footer>

  <script src="{{ url_for('static', filename='js/menu.js')}}"></script>
  <script src="{{ url_for('static', filename='js/toast.js')}}"></script>
</body>
</html>
```

## Características

1. **Responsive Design**: Breakpoint en 768px
2. **Animaciones suaves**: Anime.js
3. **Sistema de temas**: Claro/Oscuro
4. **Notificaciones Toast**: Feedback visual
5. **Navegación sticky**: Barra fija al scroll
6. **Grid Layout**: Footer responsive

---

**Desarrollado por**: Niozex Studio
