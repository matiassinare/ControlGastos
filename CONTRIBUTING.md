# 🤝 Contribuir a Expense Tracker

Gracias por tu interés en contribuir! Este documento te guiará en el proceso.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Funcionalidades](#sugerir-funcionalidades)
- [Pull Requests](#pull-requests)
- [Guía de Estilo](#guía-de-estilo)
- [Estructura del Proyecto](#estructura-del-proyecto)

## 📜 Código de Conducta

Este proyecto adopta un código de conducta basado en respeto mutuo:

- Ser respetuoso con otros contributors
- Aceptar críticas constructivas
- Enfocarse en lo mejor para la comunidad
- Mostrar empatía hacia otros miembros

## 🚀 Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clonar tu fork
git clone https://github.com/TU_USUARIO/expense-tracker.git
cd expense-tracker
```

### 2. Crear Branch

```bash
git checkout -b feature/mi-nueva-funcionalidad
# o
git checkout -b fix/mi-bug-fix
```

### 3. Hacer Cambios

- Seguir la [Guía de Estilo](#guía-de-estilo)
- Escribir código limpio y documentado
- Probar localmente

### 4. Commit

```bash
git add .
git commit -m "Add: descripción clara del cambio"
```

**Convención de commits**:
- `Add:` nueva funcionalidad
- `Fix:` corrección de bug
- `Update:` mejora de funcionalidad existente
- `Refactor:` cambios de código sin cambiar funcionalidad
- `Docs:` solo cambios en documentación

### 5. Push y PR

```bash
git push origin feature/mi-nueva-funcionalidad
```

Luego abrir Pull Request en GitHub.

## 🐛 Reportar Bugs

1. Verificar que el bug no esté ya reportado en [Issues](https://github.com/TU_USUARIO/expense-tracker/issues)
2. Usar el template de [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
3. Incluir:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots (si aplica)
   - Entorno (OS, Python version, etc.)

## 💡 Sugerir Funcionalidades

1. Verificar que no exista en [Issues](https://github.com/TU_USUARIO/expense-tracker/issues)
2. Usar el template de [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
3. Explicar:
   - Qué problema resuelve
   - Cómo debería funcionar
   - Alternativas consideradas

## 🔄 Pull Requests

### Checklist antes de crear PR

- [ ] El código sigue la guía de estilo
- [ ] He probado los cambios localmente
- [ ] He actualizado la documentación
- [ ] No hay credenciales hardcodeadas
- [ ] El PR tiene un título descriptivo
- [ ] He completado el template de PR

### Proceso de Review

1. Un maintainer revisará tu PR
2. Puede solicitar cambios
3. Una vez aprobado, se hará merge
4. Tu contribución será reconocida!

## 🎨 Guía de Estilo

### Python

- **PEP 8**: Seguir estándar de Python
- **Docstrings**: Documentar funciones con docstrings
- **Type hints**: Usar cuando sea posible
- **Nombres descriptivos**: Variables y funciones claras

Ejemplo:
```python
def get_transactions(user_id: str, start_date: str) -> list:
    """
    Obtener transacciones de un usuario.

    Args:
        user_id: ID del usuario
        start_date: Fecha de inicio (formato YYYY-MM-DD)

    Returns:
        Lista de transacciones
    """
    # Código aquí
    pass
```

### SQL

- **Mayúsculas**: Keywords en mayúsculas (`SELECT`, `WHERE`)
- **Indentación**: 4 espacios
- **Nombres**: snake_case para tablas y columnas
- **Comentarios**: Explicar queries complejas

### Markdown

- **Headers**: Usar `#` apropiadamente
- **Listas**: Consistentes (bullet o numeradas)
- **Code blocks**: Con lenguaje especificado

## 📁 Estructura del Proyecto

```
expense-tracker/
├── database/           # SQL schemas
├── scraper/           # Scraper de tarjetas
│   ├── banks/        # Scrapers específicos por banco
│   ├── run.py        # Entry point
│   └── utils.py      # Helpers
├── dashboard/         # Dashboard Streamlit
│   ├── pages/        # Páginas del dashboard
│   ├── components/   # Componentes reusables
│   └── services/     # Lógica de negocio
└── docs/             # Documentación
```

## 🏆 Áreas de Contribución

### Fácil (Good First Issue)
- Mejorar documentación
- Agregar comentarios al código
- Fix de typos
- Traducción de mensajes

### Intermedio
- Agregar tests
- Mejorar UI del dashboard
- Optimizar queries
- Agregar validaciones

### Avanzado
- Implementar scraper para nuevo banco
- Agregar categorización automática con ML
- Implementar exportación PDF
- GitHub Actions para CI/CD

## 🆘 Necesitas Ayuda?

- Abre un [Discussion](https://github.com/TU_USUARIO/expense-tracker/discussions)
- Pregunta en Issues existentes
- Revisa la [documentación](docs/)

## 📝 Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la [MIT License](LICENSE).

---

**Gracias por contribuir! 🎉**
