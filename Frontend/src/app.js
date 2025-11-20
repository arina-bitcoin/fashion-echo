function qs(selector) {
    const el = document.querySelector(selector);
    if (!el)
        throw new Error(`Selector not found: ${selector}`);
    return el;
}
function setActive(screenId) {
    document.querySelectorAll('.screen').forEach((el) => {
        el.classList.toggle('active', el.id === screenId);
    });
}
function setupNav() {
    qs('#go-register').addEventListener('click', (e) => {
        e.preventDefault();
        setActive('screen-register');
    });
    qs('#go-login').addEventListener('click', (e) => {
        e.preventDefault();
        setActive('screen-login');
    });
    qs('#btn-login').addEventListener('click', () => {
        setActive('screen-map');
    });
    qs('#btn-register').addEventListener('click', () => {
        setActive('screen-map');
    });
    qs('#to-offers').addEventListener('click', () => setActive('screen-offers'));
    qs('#to-map').addEventListener('click', () => setActive('screen-map'));
    qs('#open-login').addEventListener('click', () => setActive('screen-login'));
}
function generateOffers(count) {
    const images = [
        'https://images.unsplash.com/photo-1520975916090-3105956dac38?q=80&w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1503342217505-b0a15cf70489?q=80&w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1519748768877-3f6f0361d95e?q=80&w=800&auto=format&fit=crop'
    ];
    return Array.from({ length: count }, (_v, i) => ({
        id: i + 1,
        title: 'Тренч, шарф, наушники',
        image: images[i % images.length]
    }));
}
function renderOffers() {
    const container = qs('#offers');
    const items = generateOffers(12);
    container.innerHTML = items
        .map((o) => `
            <div class="offer">
                <img src="${o.image}" alt="offer ${o.id}">
                <div class="cap">${o.title}</div>
            </div>
        `)
        .join('');
}
function main() {
    setupNav();
    renderOffers();
    setActive('screen-map');
}
document.addEventListener('DOMContentLoaded', main);