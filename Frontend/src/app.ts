type ScreenId = 'screen-login' | 'screen-register' | 'screen-map' | 'screen-offers';

function qs<T extends Element>(selector: string): T {
    const el = document.querySelector(selector);
    if (!el) throw new Error(`Selector not found: ${selector}`);
    return el as T;
}

function setActive(screenId: ScreenId): void {
    document.querySelectorAll<HTMLElement>('.screen').forEach((el) => {
        el.classList.toggle('active', el.id === screenId);
    });
}

function setupNav(): void {
    qs<HTMLAnchorElement>('#go-register').addEventListener('click', (e) => {
        e.preventDefault();
        setActive('screen-register');
    });

    qs<HTMLAnchorElement>('#go-login').addEventListener('click', (e) => {
        e.preventDefault();
        setActive('screen-login');
    });

    qs<HTMLButtonElement>('#btn-login').addEventListener('click', () => {
        setActive('screen-map');
    });

    qs<HTMLButtonElement>('#btn-register').addEventListener('click', () => {
        setActive('screen-map');
    });

    qs<HTMLButtonElement>('#to-offers').addEventListener('click', () => setActive('screen-offers'));
    qs<HTMLButtonElement>('#to-map').addEventListener('click', () => setActive('screen-map'));
    qs<HTMLButtonElement>('#open-login').addEventListener('click', () => setActive('screen-login'));
}

type Offer = {
    id: number;
    title: string;
    image: string;
};

function generateOffers(count: number): Offer[] {
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

function renderOffers(): void {
    const container = qs<HTMLDivElement>('#offers');
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

function main(): void {
    setupNav();
    renderOffers();
    setActive('screen-map');
}

document.addEventListener('DOMContentLoaded', main);


