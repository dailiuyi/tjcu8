const LOGO_START_DELAY_MS = 1000;
const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)';

export function initializeLogoAnimation({
    root = document,
    view = window,
    startDelayMs = LOGO_START_DELAY_MS
} = {}) {
    const logo = root.querySelector('.logo');
    const logoImage = logo?.querySelector('img');
    if (!logo || !logoImage) {
        return null;
    }

    const reducedMotion = typeof view.matchMedia === 'function'
        ? view.matchMedia(REDUCED_MOTION_QUERY)
        : null;
    let startTimer = null;
    let animationFrame = null;
    let rotationSpeed = 0;
    let isRotating = false;

    function prefersReducedMotion() {
        return reducedMotion?.matches === true;
    }

    function rotateLogo() {
        if (!isRotating) {
            return;
        }

        rotationSpeed += 0.5;
        logoImage.style.transform = `rotate(${rotationSpeed * 10}deg)`;
        animationFrame = view.requestAnimationFrame(rotateLogo);
    }

    function startAnimation() {
        if (prefersReducedMotion() || isRotating || startTimer !== null) {
            return;
        }

        startTimer = view.setTimeout(() => {
            startTimer = null;
            if (prefersReducedMotion()) {
                return;
            }

            isRotating = true;
            rotationSpeed = 2;
            rotateLogo();
        }, startDelayMs);
    }

    function stopAnimation() {
        if (startTimer !== null) {
            view.clearTimeout(startTimer);
            startTimer = null;
        }
        if (animationFrame !== null) {
            view.cancelAnimationFrame(animationFrame);
            animationFrame = null;
        }

        isRotating = false;
        rotationSpeed = 0;
        logoImage.style.transform = 'rotate(0deg)';
    }

    function handleKeydown(event) {
        if (event.key === 'Escape') {
            stopAnimation();
        }
    }

    function handleMotionChange(event) {
        if (event.matches) {
            stopAnimation();
        }
    }

    const eventBindings = [
        ['mouseenter', startAnimation],
        ['mouseleave', stopAnimation],
        ['click', startAnimation],
        ['blur', stopAnimation],
        ['keydown', handleKeydown]
    ];
    eventBindings.forEach(([eventName, listener]) => {
        logo.addEventListener(eventName, listener);
    });

    if (typeof reducedMotion?.addEventListener === 'function') {
        reducedMotion.addEventListener('change', handleMotionChange);
    }

    return {
        start: startAnimation,
        stop: stopAnimation,
        destroy() {
            stopAnimation();
            eventBindings.forEach(([eventName, listener]) => {
                logo.removeEventListener(eventName, listener);
            });
            if (typeof reducedMotion?.removeEventListener === 'function') {
                reducedMotion.removeEventListener('change', handleMotionChange);
            }
        }
    };
}
